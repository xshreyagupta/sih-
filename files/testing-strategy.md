# Testing Strategy

Minimum required before integration — keep each fast and independent.

| Module | Minimum tests |
|---|---|
| CV | Given a sample frame/image, detections output has valid `class_name` (in canonical list), `confidence` in [0,1], `bbox` well-formed |
| Tracking | Same object across consecutive frames keeps the same `tracking_id`; counting logic gives correct count on a synthetic sequence with known crossings |
| Geospatial/Event | Event builder output validates against `event.schema.json`; GPS simulation produces coordinates that fall on the intended route; dedup groups two nearby same-type events into one incident and keeps two far-apart events separate |
| Backend | API tests per endpoint: valid POST returns 201 with correct shape; invalid payload returns 422; status transition rules enforced (valid transition 200, invalid 409); idempotent POST with repeated `client_event_id` doesn't duplicate |
| Database | Spatial query correctness: `ST_DWithin` query returns expected rows for known seeded points; GIST index exists (`\d event` in psql) |
| Deduplication | Unit tests with controlled lat/lon/time inputs confirming the 15m/24h rule joins/splits incidents as expected |
| Intelligence | Given fixed input factors, `priority_score`/`priority_level` match expected output (deterministic formula — easy to test) |
| Frontend | Mocked API responses render map markers/charts correctly; a failed API call shows a sane error state, not a blank crash |
| End-to-end (integration, owned jointly, run last) | One sample video → CV → Tracking → Event → POST → DB row exists → GET /incidents returns it → priority populated → dashboard shows a marker. This is the "does the whole thing actually work" smoke test, ideally scripted in `scripts/run_demo_pipeline.py` + `tests/test_e2e_smoke.py` |

**Rule of thumb:** every module ships with tests that run against **saved sample data**
(`data/sample_events/`, a couple of sample frames/videos) — never require the full live
pipeline just to test one module. This is what actually lets 6 people work in parallel and
still trust their own code before integration day.
