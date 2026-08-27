# Environment & Local Development Setup

## Versions / stack
- Python 3.11
- Node 20 LTS
- PostgreSQL 16 + PostGIS 3.4
- FastAPI (latest stable) + Uvicorn
- React 18 + Vite + Leaflet (`react-leaflet`)
- CV: Ultralytics YOLOv8 (pretrained COCO checkpoint fine-tuned/augmented for pothole/
  waterlogging classes not in COCO — Member 1's call on exact model)
- Tracking: ByteTrack (via `supervision` library's ByteTrack implementation, or the reference
  repo — Member 2's call)

## `.env.example`
```
# Database
POSTGRES_USER=uip
POSTGRES_PASSWORD=uip
POSTGRES_DB=urban_intel
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://uip:uip@localhost:5432/urban_intel

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Verification tuning
DEDUP_RADIUS_M=15
DEDUP_TIME_WINDOW_HOURS=24
VERIFICATION_PASSES_REQUIRED=2

# GPS mode
GPS_MODE=simulated   # simulated | real
```

## Dependency strategy
- Each module directory gets its **own** `requirements.txt` (cv, tracking, geo_events,
  backend, intelligence) so people aren't fighting over one shared file / installing YOLO
  deps to work on FastAPI routes. A root `requirements-dev.txt` covers shared lint/test tools
  only (pytest, black, ruff).
- `frontend/package.json` as usual for Node deps.

## docker-compose.yml (only Postgres+PostGIS is mandatory infra)
```yaml
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
volumes:
  pgdata:
```
Backend and frontend run natively (`uvicorn`, `npm run dev`) during hackathon dev for fast
reload — only the database goes in Docker. Add backend/frontend containers only if the demo
environment specifically needs one-command startup.

## Local dev — quick start
```
docker compose up -d db                  # 1. start Postgres+PostGIS
psql $DATABASE_URL -f docker/postgres/init.sql   # (if not auto-run) create extension + schema
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload   # 2. backend
cd frontend && npm install && npm run dev         # 3. frontend
cd cv && pip install -r requirements.txt && python inference.py --video ../data/sample_videos/x.mp4   # 4. run CV standalone
pytest backend/tests tracking/tests cv/tests geo_events/tests intelligence/tests           # 5. run tests
```

Each module is runnable **standalone** with a small script/CLI (`python inference.py`,
`python tracker.py`, etc.) that prints/saves its output to a local JSON file — this is
critical: no one should be blocked on the full pipeline being wired end-to-end to test their
own piece.
