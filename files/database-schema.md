# Database Schema (PostgreSQL + PostGIS)

## Event vs Incident — separate concepts

- **Event** = one raw sighting: one bus, one detection, one timestamp, one GPS point.
  Immutable once written (except `incident_id`/`road_segment_id` backfill).
- **Incident** = the deduplicated real-world defect. Carries `status`, `priority_score`,
  `sighting_count`. This is what the dashboard and repair workflow operate on.

This split is what makes both dedup and verification clean: dedup = "which Incident does
this new Event belong to"; verification = "does a future Event on this Incident's location
still show the same defect".

## Tables

### BUS
| Column | Type | Notes |
|---|---|---|
| `bus_id` (PK) | text | `BUS_17` |
| `route_id` | text, nullable | FK-ish to route, optional in prototype |
| `label` | text, nullable | human-readable name |

### ROAD_SEGMENT
| Column | Type | Notes |
|---|---|---|
| `segment_id` (PK) | text | `SEG_1042` |
| `geom` | `geometry(LineString, 4326)` | PostGIS, WGS84 |
| `name` | text, nullable | street name if known |
| `road_health_score` | float, nullable | computed by Intelligence module |

Index: `CREATE INDEX idx_segment_geom ON road_segment USING GIST (geom);`

### EVENT
| Column | Type | Notes |
|---|---|---|
| `event_id` (PK) | text | `EVT_<ULID>` |
| `client_event_id` | text, UNIQUE | idempotency key |
| `event_type` | text, CHECK IN (canonical list) | see detection-classes.md |
| `source_bus` | text, FK → bus.bus_id | |
| `route_id` | text, nullable | |
| `timestamp` | timestamptz | detection time |
| `geom` | `geometry(Point, 4326)` | PostGIS point, built from lat/lon |
| `gps_source` | text, CHECK IN ('simulated','real') | |
| `gps_accuracy_m` | float, nullable | |
| `confidence` | float, CHECK 0..1 | |
| `severity` | text, CHECK IN ('low','medium','high','critical') | |
| `tracking_id` | text, nullable | |
| `road_segment_id` | text, nullable, FK → road_segment.segment_id | |
| `frame_ref` | text, nullable | |
| `incident_id` | text, nullable, FK → incident.incident_id | |
| `metadata` | jsonb, nullable | |
| `created_at` | timestamptz, default now() | |

Indexes:
- `CREATE INDEX idx_event_geom ON event USING GIST (geom);`
- `CREATE INDEX idx_event_type_time ON event (event_type, timestamp);`
- `CREATE INDEX idx_event_incident ON event (incident_id);`

### INCIDENT
| Column | Type | Notes |
|---|---|---|
| `incident_id` (PK) | text | `INC_<ULID>` |
| `event_type` | text | same enum as Event |
| `geom` | `geometry(Point, 4326)` | centroid of clustered sightings |
| `road_segment_id` | text, nullable, FK | |
| `status` | text, CHECK IN (state-machine enum) | default `OPEN` |
| `severity` | text | rolled up from member events (max) |
| `priority_score` | float, nullable | set by Intelligence engine |
| `priority_level` | text, nullable | `LOW/MEDIUM/HIGH/CRITICAL` |
| `sighting_count` | int, default 1 | |
| `first_seen_at` | timestamptz | |
| `last_seen_at` | timestamptz | |
| `created_at` | timestamptz, default now() | |
| `updated_at` | timestamptz | |

Indexes:
- `CREATE INDEX idx_incident_geom ON incident USING GIST (geom);`
- `CREATE INDEX idx_incident_status ON incident (status);`
- `CREATE INDEX idx_incident_priority ON incident (priority_score DESC);`

### STATUS_HISTORY
| Column | Type | Notes |
|---|---|---|
| `id` (PK) | serial/bigint | |
| `incident_id` | text, FK → incident.incident_id | |
| `from_status` | text, nullable | |
| `to_status` | text | |
| `changed_by` | text | `"system"` or user id |
| `changed_at` | timestamptz, default now() | |
| `reason` | text, nullable | |
| `triggering_event_id` | text, nullable, FK → event.event_id | |

### VERIFICATION_QUEUE
| Column | Type | Notes |
|---|---|---|
| `id` (PK) | serial/bigint | |
| `incident_id` | text, FK → incident.incident_id | |
| `resolved_at` | timestamptz | when it entered `RESOLVED` |
| `passes_required` | int, default 2 | |
| `passes_completed` | int, default 0 | |
| `status` | text | `PENDING` / `VERIFIED` / `DISPUTED` |

### ALERT
| Column | Type | Notes |
|---|---|---|
| `alert_id` (PK) | text | `ALT_<ULID>` |
| `incident_id` | text, FK → incident.incident_id | |
| `alert_type` | text | e.g. `CRITICAL_PRIORITY`, `RE_ESCALATED` |
| `message` | text | |
| `created_at` | timestamptz, default now() | |
| `acknowledged` | boolean, default false | |

## Relationships

```
BUS 1───* EVENT *───1 INCIDENT 1───* STATUS_HISTORY
                 *
                 │
                 1
          ROAD_SEGMENT

INCIDENT 1───* VERIFICATION_QUEUE  (typically 1:1, modeled as table for history)
INCIDENT 1───* ALERT
```

## Common spatial queries (why the GIST indexes above matter)

```sql
-- events within 20 metres of a point
SELECT * FROM event
WHERE ST_DWithin(geom::geography, ST_MakePoint(:lon,:lat)::geography, 20);

-- incidents near a bus route (buffer around route line)
SELECT i.* FROM incident i, road_segment s
WHERE s.segment_id = :segment_id
AND ST_DWithin(i.geom::geography, s.geom::geography, 50);

-- heatmap data: all incident points + severity/priority for map rendering
SELECT incident_id, ST_X(geom) lon, ST_Y(geom) lat, severity, priority_score
FROM incident WHERE status != 'VERIFIED';
```

Cast to `::geography` for metre-based `ST_DWithin`/`ST_Distance` — this is the simplest
correct way to do distance queries in lat/lon without manual projection math, good enough for
hackathon accuracy.

## Enum/check constraints — keep in sync with docs

`event_type` and `severity`/`status` values must match `detection-classes.md` and
`state-machine.md` exactly. If Postgres `CHECK` constraints feel too rigid for a hackathon,
use plain `text` columns and validate in the Pydantic layer instead (Backend owner's call) —
either way the **allowed values are the same list**, don't let DB and API drift apart.
