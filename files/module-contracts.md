# Module Contracts, Communication, Dedup, Priority Engine, Verification

## 1. Module responsibility table

### CV Module (Member 1)
- **Input:** video frame (numpy array / image)
- **Output:** `detections[]` — `[{class_name, confidence, bbox}]`, using canonical class
  names from `detection-classes.md`
- **Responsibilities:** run YOLO inference, filter by confidence threshold, return raw
  detections per frame
- **Dependencies:** none (pure function of a frame)
- **Must NOT handle:** tracking/IDs, GPS, event assembly, DB writes, severity scoring beyond
  raw confidence

### Tracking Module (Member 2)
- **Input:** `detections[]` (per frame) + frame metadata (frame_id, video timestamp)
- **Output:** `tracked_objects[]` — `[{tracking_id, class_name, confidence, bbox, frame_id}]`
  + counting/congestion side outputs (`vehicle_count`, `avg_speed_estimate`,
  `congestion_level`)
- **Responsibilities:** ByteTrack association across frames, virtual-line counting,
  approximate speed, congestion estimation
- **Dependencies:** CV module's detections
- **Must NOT handle:** GPS mapping, event objects, severity, DB/API calls

### Geospatial & Event Module (Member 3)
- **Input:** `tracked_objects[]` (or raw detections for non-tracked classes like potholes),
  video timestamp, bus_id, route info
- **Output:** canonical **Event** objects (per `event-schema.md`), POSTed to Backend.
  Also: dedup logic (Event → Incident matching), road segment matching, PostGIS schema
  ownership.
- **Responsibilities:** GPS simulation/association, building the canonical Event JSON,
  deduplication rules, spatial matching to road segments
- **Dependencies:** Tracking/CV outputs, Backend API (to POST events)
- **Must NOT handle:** YOLO/tracking internals, priority scoring, frontend rendering

### Backend Module (Member 4)
- **Input:** HTTP requests (Event ingestion, queries, status updates)
- **Output:** REST API responses per `api-spec.md`; DB rows
- **Responsibilities:** validation, persistence, exposing all endpoints, calling
  dedup/verification logic (owned as library code by Member 3) and priority logic (owned by
  Member 5) at the right pipeline points, status state machine enforcement
- **Dependencies:** DB schema, Event schema, dedup/priority as callable functions or modules
- **Must NOT handle:** CV/tracking logic, frontend rendering, scoring formulas themselves
  (calls into Intelligence module's function/API instead)

### Intelligence Module (Member 5)
- **Input:** Incident + historical sightings + traffic/congestion context (from Tracking) +
  weather context (optional external API or static mock)
- **Output:** `{priority_score, priority_level, factors{}}` — written back via Backend
- **Responsibilities:** priority/severity/risk scoring, road health scoring, analytics
  aggregation logic
- **Dependencies:** reads from DB (via Backend's data-access layer or direct read-only query,
  team's call), consumes Tracking's congestion output
- **Must NOT handle:** ingestion, status transitions, API routing (Backend exposes the
  results), frontend rendering

### Frontend Module (Member 6)
- **Input:** REST API only (`api-spec.md`)
- **Output:** React + Leaflet dashboard
- **Responsibilities:** map layers, filters, charts, status update UI, verification view
- **Dependencies:** Backend API contract only — never the DB, never other modules' code
- **Must NOT handle:** any business logic that belongs server-side (scoring, dedup, state
  transition validity) — UI should reflect what the API returns/allows, not reimplement rules

## 2. Communication between modules (data flow)

| Boundary | Producer | Consumer | Format | Protocol |
|---|---|---|---|---|
| CV → Tracking | Member 1 | Member 2 | `detections[]` (Python objects/JSON) | in-process function call (same pipeline script for prototype) |
| Tracking → Event builder | Member 2 | Member 3 | `tracked_objects[]` + counting/congestion | in-process function call |
| Event builder → Backend | Member 3 | Member 4 | canonical Event JSON | HTTP POST `/api/v1/events` |
| Backend → DB | Member 4 | — | SQL/ORM | direct DB connection |
| Backend → Intelligence | Member 4 | Member 5 | Incident + context | in-process function call, OR simple internal HTTP call if Intelligence runs as its own small service — **default: same-process function call** to avoid extra infra |
| Backend → Frontend | Member 4 | Member 6 | JSON | HTTP REST (`api-spec.md`) |

No Kafka, no Redis streams, no microservices, no k8s — a single Python pipeline script calls
CV → Tracking → Event builder in sequence per video, then POSTs to FastAPI. This keeps 6
people productive without needing to stand up infra.

## 3. Deduplication strategy

**Event vs Incident:** yes, kept separate (see `database-schema.md`). Every raw detection is
an Event; Incidents are the deduplicated real-world defects the dashboard shows.

**Prototype rule** (deliberately simple, calibrate later):
```
A new Event joins an existing Incident if ALL of:
  - same event_type
  - within 15 metres (ST_DWithin on geography)
  - within 24 hours of the incident's last_seen_at   (wide window — buses may not repass often in a demo)
Otherwise: create a new Incident.
```
On match: increment `sighting_count`, update `last_seen_at`, recompute `geom` as centroid of
member events' points (or keep the first point — simplest is fine for prototype), set
`severity` = max severity across member events.

These thresholds (15m / 24h) are placeholders for the hackathon prototype and should be
tuned later against real data — call this out explicitly in the demo/readme so it doesn't
read as a finished calibration.

## 4. Priority Engine contract (Member 5)

**Input:**
```json
{
  "incident": { "...Incident fields..." },
  "history": { "past_incidents_on_segment": 4, "days_since_last_repair": 120 },
  "traffic": { "congestion_level": "high", "vehicle_count_recent": 230 },
  "weather": { "condition": "rain", "recent_rainfall_mm": 12 }
}
```
**Output:**
```json
{
  "priority_score": 87,
  "priority_level": "CRITICAL",
  "factors": { "severity": 30, "frequency": 25, "traffic": 20, "recency": 12 }
}
```
**Rules:**
- `priority_score` = simple weighted sum of explainable factors (0–100), levels:
  `LOW <40`, `MEDIUM 40–64`, `HIGH 65–84`, `CRITICAL 85+`.
- No ML model in Phase 0/1 — a transparent formula the team can explain in a 2-minute demo
  beats a black box.
- Called by Backend right after an Incident is created/updated (dedup step), synchronously
  for the hackathon (fine at this scale).

## 5. Verification architecture

```
Incident.status = RESOLVED
        │  (automatic, immediate)
        ▼
Incident.status = PENDING_VERIFICATION
   VerificationQueue row created: passes_required=2, passes_completed=0
        │
        │  future bus passes generate new Events near this incident's location
        ▼
On each new Event of the SAME event_type within the dedup radius of this incident,
while status == PENDING_VERIFICATION:
        │
        ├── event_type NOT detected (i.e. a bus passed the segment and did NOT re-flag it)
        │       → passes_completed += 1
        │       → if passes_completed >= passes_required: status = VERIFIED
        │
        └── event_type IS detected again (defect still there)
                → status = DISPUTED immediately (no need to wait for pass count)
                → ops reviews; if confirmed real → status = RE_ESCALATED → back to OPEN
```

**Note on "a bus passed but didn't detect it":** detecting the *absence* of a defect requires
knowing a bus actually traversed that segment. Simplest prototype approach: whenever any
Event (of any type) from a bus arrives with `road_segment_id` matching the incident's segment,
count that as one "pass" of the segment; check whether a matching-type Event also landed
within the same time window to decide dispute vs. progress-toward-verified. This keeps
verification logic entirely inside `geo_events`/Backend, no new infra needed.

**How many passes:** default 2 (configurable), because a single clean pass could be a bus
that just didn't get a clear camera angle.
