# Urban Intelligence Platform — Architecture (Phase 0)

## 1. Final Architecture (pipeline)

```
VIDEO (public dataset, simulated bus feed)
   │
   ▼
[CV MODULE]            Member 1
   frame → YOLO → detections[]
   │  (produces: detections.json / in-proc objects)
   ▼
[TRACKING MODULE]       Member 2
   detections + frame meta → ByteTrack → tracked_objects[]
   also: counting lines, congestion estimate
   │
   ▼
[EVENT + GPS MODULE]    Member 3
   tracked_objects → map to GPS (sim or real) → canonical Event objects
   │  (HTTP POST, canonical Event JSON)
   ▼
[BACKEND — FastAPI]     Member 4
   validates → writes → PostgreSQL/PostGIS
   exposes REST API (events, alerts, verification, analytics)
   │
   ▼
[DATABASE — PostgreSQL + PostGIS]   Member 3 (schema owner) + Member 4 (access layer)
   Event, Incident, Bus, RoadSegment, StatusHistory, Alert, VerificationQueue
   │
   ▼
[DEDUPLICATION]         Member 3 (logic) — runs inside Backend on ingest
   Event → matched to existing Incident or creates new Incident
   │
   ▼
[INTELLIGENCE ENGINE]   Member 5
   Incident + history + traffic + weather → priority_score, priority_level
   writes back to DB via Backend API
   │
   ▼
[ALERTS + ANALYTICS]    Member 5 (logic) + Member 4 (API exposure)
   │
   ▼
[FRONTEND — React + Leaflet]  Member 6
   consumes REST API only — never touches DB directly
   │
   ▼
[REPAIR STATUS → VERIFICATION → RE-DETECTION]
   Status changes via API (manual or future-bus re-detection)
   Re-detection re-enters pipeline as a normal Event, matched to same Incident
```

**Golden rule:** every arrow above is either (a) an in-process function call within one
module, or (b) an HTTP call to FastAPI using the canonical Event JSON. No module talks
directly to another module's internals or database tables. This is what makes 6-way
parallel development possible.

## 2. Repository structure

```
urban-intelligence/
│
├── backend/                # Member 4 — FastAPI app, DB access layer, all APIs
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/        # events.py, alerts.py, verification.py, analytics.py
│   │   ├── models/         # SQLAlchemy / ORM models (mirrors database-schema.md)
│   │   ├── schemas/        # Pydantic models — MUST mirror docs/event-schema.md
│   │   ├── services/       # dedup.py, status.py
│   │   └── db/             # session, migrations (alembic)
│   └── tests/
│
├── cv/                      # Member 1 — YOLO inference, detection classes
│   ├── models/              # weights (gitignored, or via release asset)
│   ├── inference.py
│   ├── classes.py           # MUST mirror docs/detection-classes.md
│   └── tests/
│
├── tracking/                 # Member 2 — ByteTrack, counting, congestion
│   ├── tracker.py
│   ├── counting.py
│   ├── congestion.py
│   └── tests/
│
├── geo_events/                # Member 3 — GPS association, event assembly, dedup logic, PostGIS helpers
│   ├── gps_sim.py
│   ├── event_builder.py       # builds canonical Event JSON (imports contract from data/contracts)
│   ├── dedup.py
│   ├── road_segments.py
│   └── tests/
│
├── intelligence/               # Member 5 — priority/severity scoring, analytics, weather
│   ├── priority_engine.py
│   ├── analytics.py
│   ├── weather.py
│   └── tests/
│
├── frontend/                    # Member 6 — React + Vite + Leaflet
│   ├── src/
│   └── tests/
│
├── data/
│   ├── contracts/                # ★ SHARED — the actual schema files (JSON Schema / OpenAPI)
│   │   ├── event.schema.json     # CONTRACT — do not edit without team sign-off
│   │   ├── openapi.yaml          # CONTRACT — API contract, generated/maintained by Backend owner
│   │   └── detection_classes.json# CONTRACT — canonical class list
│   ├── sample_videos/            # public driving footage used for prototype
│   └── sample_events/            # example Event payloads for testing
│
├── scripts/                      # one-off helper scripts (seed db, run demo pipeline end-to-end)
│
├── tests/                        # cross-module / end-to-end integration tests only
│
├── docs/                         # ★ SHARED — source of truth, see below
│
├── docker/
│   └── postgres/                 # init SQL (PostGIS extension, schema bootstrap)
│
├── .env.example
├── docker-compose.yml            # postgres+postgis (+ optionally backend, frontend)
├── README.md
└── .gitignore
```

### Ownership

| Directory | Owner | Shared? |
|---|---|---|
| `cv/` | Member 1 | No |
| `tracking/` | Member 2 | No |
| `geo_events/` | Member 3 | No (but produces the shared contract's data) |
| `backend/` | Member 4 | No (but schemas/ mirrors the shared contract) |
| `intelligence/` | Member 5 | No |
| `frontend/` | Member 6 | No |
| `data/contracts/` | Member 3 (event schema) + Member 4 (API/OpenAPI) jointly own; **all 6 read** | **YES — highest caution** |
| `docs/` | Lead architect (you) initially, then whoever owns that doc's subject | **YES** |
| `docker-compose.yml`, `.env.example` | Member 4 | **YES** |
| `scripts/` | Whoever needs it, low-risk | Shared, low caution |

**Files that must never be modified casually (require a message in the team channel + quick
sign-off before changing):**
- `data/contracts/event.schema.json`
- `data/contracts/openapi.yaml`
- `data/contracts/detection_classes.json`
- `docker-compose.yml` / `.env.example` (breaks everyone's local env)
- `docs/event-schema.md`, `docs/detection-classes.md`, `docs/api-spec.md`, `docs/state-machine.md`

Everything else is owned by one person and can be changed freely inside that person's module.
