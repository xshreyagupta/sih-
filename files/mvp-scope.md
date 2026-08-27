# MVP Scope

## MUST HAVE (the demo doesn't exist without these)
- CV detects at least 2 classes reliably on a sample video (recommend: `pothole` +
  `vehicle_*` — highest visual impact, easiest to source data for)
- Tracking assigns stable IDs (needed for vehicle counting/congestion story, and to avoid
  emitting the same pothole as 50 events per second on a paused frame)
- Simulated GPS mapping video timestamp → coordinates along a predefined route
- Canonical Event object built and POSTed to FastAPI
- PostgreSQL + PostGIS storing events with spatial column
- Basic deduplication (distance+type+time rule) producing Incidents
- `GET /incidents` (or `/events`) API working
- React + Leaflet map showing incident markers with type/severity, from live API (not mock)
- Manual status update (`OPEN → ACKNOWLEDGED → RESOLVED`) via API, reflected on dashboard

**This alone tells the full story:** bus sees defect → backend → map → someone acts on it.

## SHOULD HAVE (significantly strengthens the pitch)
- Full detection class set (traffic sign/light, zebra crossing, road divider, waterlogging,
  pedestrian)
- Priority Engine scoring incidents (explainable factors, not just raw severity)
- Verification loop: RESOLVED → PENDING_VERIFICATION → re-detection triggers DISPUTED/
  RE_ESCALATED — this is the platform's most distinctive feature, worth prioritizing if MUST
  HAVE is done early
- Basic analytics endpoint + a chart on the dashboard (counts by type/severity)
- Multiple simulated buses (shows the "fleet" concept, not just one camera)

## NICE TO HAVE (only if time remains)
- Congestion/traffic estimation via ByteTrack line-counting
- Road health scoring per segment
- Weather-context input to priority scoring
- Alerts feed / notification UI
- Heatmap layer (vs. simple markers)
- Auth/roles for who can transition status

## Explicit non-goals for this hackathon
- Real bus GPS/telemetry integration (simulated only, per Rule 8/9 — always labeled as such)
- Training a custom YOLO model from scratch (use pretrained/fine-tuned/public datasets)
- Production deployment, Kubernetes, autoscaling, multi-tenant auth
- ML-based (non-explainable) priority scoring
