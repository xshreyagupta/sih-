# API Contract (FastAPI) — definition only, not implemented in Phase 0

Base URL: `/api/v1`

| Method | Path | Purpose |
|---|---|---|
| POST | `/events` | Ingest a raw detection event |
| GET | `/events` | List events (filterable) |
| GET | `/events/{id}` | Get one event |
| GET | `/events/nearby` | Spatial query — events near a point |
| GET | `/events/heatmap` | Aggregated points for heatmap layer |
| PATCH | `/events/{id}/status` | Transition incident status (see state-machine.md) |
| GET | `/incidents` | List deduplicated incidents (frontend's primary map source) |
| GET | `/incidents/{id}` | One incident + its member events |
| GET | `/alerts` | List alerts |
| GET | `/analytics` | Aggregate stats (counts by type/severity/segment/time) |
| POST | `/verification` | Manually trigger/record a verification pass |
| GET | `/verification` | List items in the verification queue |

## POST /events
**Body:** ingestion payload from `event-schema.md` ("Ingestion payload" section).
**Response 201:** full Event object (server-populated fields included).
**Errors:**
- 422 — validation failure (bad enum, bad range, missing required field)
- 409 — `client_event_id` already exists (idempotent — returns the existing event, HTTP 200 not 409, per idempotency convention: **200 OK with existing object** is preferred over an error for this specific case)

## GET /events
**Query params:** `event_type`, `severity`, `status`, `source_bus`, `from` (ISO date),
`to` (ISO date), `limit` (default 100, max 500), `offset`.
**Response 200:** `{ "items": [Event...], "total": int, "limit": int, "offset": int }`

## GET /events/{id}
**Response 200:** single Event. **404** if not found.

## GET /events/nearby
**Query params:** `lat` (required), `lon` (required), `radius_m` (default 20),
`event_type` (optional).
**Response 200:** `{ "items": [Event...], "count": int }`

## GET /events/heatmap
**Query params:** `event_type` (optional), `bbox` (optional, `minLon,minLat,maxLon,maxLat`).
**Response 200:**
```json
{ "points": [{"lat":28.61,"lon":77.20,"weight":0.8,"severity":"high"}] }
```

## PATCH /events/{id}/status
Note: operates on the parent **incident** of the event (path kept as `/events/{id}` for
frontend simplicity, but `{id}` may be either an `event_id` or `incident_id` — backend
resolves to the incident). **Body:**
```json
{ "new_status": "ACKNOWLEDGED", "changed_by": "ops_user_1", "reason": "confirmed on review" }
```
**Response 200:** updated Incident object. **409** on invalid transition (see state-machine.md).

## GET /incidents
**Query params:** `status`, `event_type`, `min_priority`, `bbox`, `limit`, `offset`.
**Response 200:** `{ "items": [Incident...], "total": int }`
Incident object:
```json
{
  "incident_id": "INC_...",
  "event_type": "pothole",
  "latitude": 28.6139, "longitude": 77.2090,
  "status": "OPEN",
  "severity": "high",
  "priority_score": 87,
  "priority_level": "CRITICAL",
  "sighting_count": 3,
  "first_seen_at": "...", "last_seen_at": "...",
  "road_segment_id": "SEG_1042"
}
```

## GET /incidents/{id}
**Response 200:** Incident object + `"events": [Event...]` (all member sightings).

## GET /alerts
**Query params:** `acknowledged` (bool), `limit`, `offset`.
**Response 200:** `{ "items": [Alert...] }`

## GET /analytics
**Query params:** `group_by` (`event_type` | `severity` | `road_segment` | `day`), `from`, `to`.
**Response 200:** `{ "buckets": [{"key": "pothole", "count": 42}] }`

## POST /verification
**Body:** `{ "incident_id": "INC_...", "triggering_event_id": "EVT_..." }`
Used when a new Event on an already-`PENDING_VERIFICATION` incident's segment arrives —
either called automatically by the backend dedup/ingest logic, or manually for testing.
**Response 200:** updated `VerificationQueue` entry + possibly incident status change.

## GET /verification
**Query params:** `status` (`PENDING`/`VERIFIED`/`DISPUTED`).
**Response 200:** `{ "items": [...] }`

## General conventions
- All responses JSON. All timestamps ISO 8601 UTC.
- Errors: `{ "error": "message", "detail": {...optional...} }` with standard HTTP status codes
  (400/404/409/422/500).
- Pagination: `limit`/`offset` everywhere, response always includes `total`.
- The formal machine-readable contract lives in `data/contracts/openapi.yaml`, generated from
  the FastAPI app (`app.openapi()`) — treat that as authoritative once Backend is running;
  this doc is the human-readable version agreed before implementation.
