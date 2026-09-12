
from pathlib import Path
import json
import subprocess
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models


app = FastAPI(
    title="Urban Road Intelligence API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CONFIGURATION
# ============================================================

SEVERITY_SCORES = {
    "low": 25,
    "medium": 50,
    "high": 75,
    "critical": 100,
}


# ============================================================
# M1 CONFIGURATION
# ============================================================

M1_PROJECT_ROOT = Path(
    "/Users/shreyagupta/Desktop/sih/sih-/SmartRoad-M1"
)

M1_VIDEOS_DIR = M1_PROJECT_ROOT / "videos"

M1_OUTPUTS_DIR = M1_PROJECT_ROOT / "outputs"

M1_PYTHON = (
    M1_PROJECT_ROOT /
    "venv" /
    "bin" /
    "python"
)

M1_DETECT_SCRIPT = (
    M1_PROJECT_ROOT /
    "src" /
    "detect.py"
)

M1_VIDEOS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

M1_OUTPUTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Urban Road Intelligence API is running"
    }


@app.get("/api/v1/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# EVENTS
# ============================================================

@app.get("/api/v1/events")
def get_events(
    db: Session = Depends(get_db)
):

    return db.query(models.Event).all()


# ============================================================
# INFRASTRUCTURE
# ============================================================

@app.get("/api/v1/infrastructure")
def get_infrastructure(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Infrastructure
    ).all()


# ============================================================
# TRAFFIC
# ============================================================

@app.get("/api/v1/traffic")
def get_traffic(
    db: Session = Depends(get_db)
):

    return db.query(
        models.TrafficObservation
    ).all()


# ============================================================
# PRIORITY
# ============================================================

@app.get("/api/v1/priority")
def get_priority(
    db: Session = Depends(get_db)
):

    incidents = db.query(
        models.Incident
    ).all()

    result = []

    for incident in incidents:

        result.append({

            "incident_id": incident.id,

            "event_type": incident.event_type,

            "priority": incident.priority,

            "priority_score": SEVERITY_SCORES.get(
                incident.priority.lower()
                if incident.priority
                else "low",
                25
            ),

            "authority": incident.authority,

            "status": incident.status,

            "latitude": incident.latitude,

            "longitude": incident.longitude,

        })

    return result


# ============================================================
# INCIDENTS
# ============================================================

@app.get("/api/v1/incidents")
def get_incidents(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Incident
    ).all()


# ============================================================
# ALERTS
# ============================================================

@app.get("/api/v1/alerts")
def get_alerts(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Alert
    ).all()


# ============================================================
# ACKNOWLEDGE ALERT
# ============================================================

@app.patch("/api/v1/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(models.Alert)
        .filter(models.Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.acknowledged = True

    db.commit()

    db.refresh(alert)

    return {

        "message": "Alert acknowledged",

        "alert_id": alert.id,

        "acknowledged": alert.acknowledged

    }


# ============================================================
# UNACKNOWLEDGE ALERT
# ============================================================

@app.patch("/api/v1/alerts/{alert_id}/unacknowledge")
def unacknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(models.Alert)
        .filter(models.Alert.id == alert_id)
        .first()
    )

    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    alert.acknowledged = False

    db.commit()

    db.refresh(alert)

    return {

        "message": "Alert unacknowledged",

        "alert_id": alert.id,

        "acknowledged": alert.acknowledged

    }


# ============================================================
# GENERATE INITIAL ALERTS
# ============================================================

@app.post("/api/v1/generate-alerts")
def generate_alerts(
    db: Session = Depends(get_db)
):

    incidents = db.query(
        models.Incident
    ).all()

    created_alerts = []

    for incident in incidents:

        existing_alert = (
            db.query(models.Alert)
            .filter(
                models.Alert.incident_id
                == incident.id
            )
            .first()
        )

        if existing_alert:
            continue

        message = (
            f"{incident.event_type} detected at "
            f"({incident.latitude}, {incident.longitude}). "
            f"Priority: {incident.priority}. "
            f"Responsible authority: "
            f"{incident.authority}."
        )

        alert = models.Alert(

            incident_id=incident.id,

            authority=incident.authority,

            priority=incident.priority,

            message=message,

            sent=True

        )

        db.add(alert)

        created_alerts.append(alert)

    db.commit()

    return {

        "message": "Alerts generated successfully",

        "count": len(created_alerts)

    }


# ============================================================
# UPDATE INCIDENT STATUS
# ============================================================

@app.patch("/api/v1/incidents/{incident_id}/status")
def update_incident_status(

    incident_id: int,

    status: str,

    db: Session = Depends(get_db)

):

    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.id
            == incident_id
        )
        .first()
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    old_status = incident.status

    incident.status = status

    db.add(
        models.StatusHistory(

            incident_id=incident.id,

            old_status=old_status,

            new_status=status

        )
    )

    db.commit()

    db.refresh(incident)

    return {

        "message": "Incident status updated",

        "incident_id": incident.id,

        "status": incident.status

    }


# ============================================================
# SLA CHECK
# ============================================================

@app.post("/api/v1/check-sla")
def check_sla(

    simulate: bool = False,

    db: Session = Depends(get_db)

):

    incidents = db.query(
        models.Incident
    ).all()

    breached = []

    already_alerted = []

    for incident in incidents:

        if incident.status in [
            "Verified",
            "Resolved"
        ]:
            continue

        if (
            not simulate
            and not incident.sla_deadline
        ):
            continue

        sla_breached = simulate

        if (
            not simulate
            and incident.sla_deadline
        ):

            try:

                deadline = datetime.fromisoformat(
                    str(incident.sla_deadline)
                )

                sla_breached = (
                    datetime.now()
                    > deadline
                )

            except Exception:

                sla_breached = False

        if not sla_breached:
            continue

        existing_realert = (
            db.query(models.Alert)
            .filter(
                models.Alert.incident_id
                == incident.id,

                models.Alert.message.contains(
                    "SLA BREACHED"
                )
            )
            .first()
        )

        if existing_realert:

            already_alerted.append(
                incident.id
            )

            continue

        message = (

            f"SLA BREACHED: "
            f"{incident.event_type} at "
            f"({incident.latitude}, "
            f"{incident.longitude}) "
            f"remains unresolved. "

            f"Priority: "
            f"{incident.priority}. "

            f"Re-alert sent to the "
            f"responsible authority: "
            f"{incident.authority}."

        )

        alert = models.Alert(

            incident_id=incident.id,

            authority=incident.authority,

            priority=incident.priority,

            message=message,

            sent=True

        )

        db.add(alert)

        breached.append(
            incident.id
        )

    db.commit()

    return {

        "message": "SLA check completed",

        "simulate": simulate,

        "breached_incidents": breached,

        "already_realerted": already_alerted

    }


# ============================================================
# INCIDENT HISTORY
# ============================================================

@app.get("/api/v1/incidents/{incident_id}/history")
def incident_history(

    incident_id: int,

    db: Session = Depends(get_db)

):

    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.id
            == incident_id
        )
        .first()
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    alerts = (
        db.query(models.Alert)
        .filter(
            models.Alert.incident_id
            == incident_id
        )
        .all()
    )

    history = (
        db.query(models.StatusHistory)
        .filter(
            models.StatusHistory.incident_id
            == incident_id
        )
        .order_by(
            models.StatusHistory.changed_at
        )
        .all()
    )

    return {

        "incident": incident,

        "alerts": alerts,

        "history": history

    }


# ============================================================
# VERIFICATION
# ============================================================

@app.get("/api/v1/verification/records")
def verification_records(
    db: Session = Depends(get_db)
):

    return db.query(
        models.VerificationRecord
    ).all()


@app.get("/api/v1/verification")
def verification(
    db: Session = Depends(get_db)
):

    return db.query(
        models.VerificationQueue
    ).all()


# ============================================================
# VERIFY PENDING ISSUE
# ============================================================

@app.post("/api/v1/verification/{queue_id}/verify")
def verify_pending_issue(

    queue_id: int,

    db: Session = Depends(get_db)

):

    queue_item = (
        db.query(models.VerificationQueue)
        .filter(
            models.VerificationQueue.id
            == queue_id
        )
        .first()
    )

    if not queue_item:

        raise HTTPException(
            status_code=404,
            detail="Verification queue item not found"
        )

    if queue_item.status in [
        "Verified",
        "Disputed"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Issue is already "
                f"{queue_item.status}"
            )
        )

    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.id
            == queue_item.incident_id
        )
        .first()
    )

    queue_item.passes_checked = (
        queue_item.passes_checked or 0
    ) + 1

    passes_needed = (
        queue_item.passes_needed or 2
    )

    if (
        queue_item.passes_checked
        >= passes_needed
    ):

        queue_item.status = "Verified"

        if incident:

            old_incident_status = (
                incident.status
            )

            incident.status = "Verified"

            db.add(
                models.StatusHistory(

                    incident_id=incident.id,

                    old_status=old_incident_status,

                    new_status="Verified"

                )
            )

        message = (
            "Issue verified successfully"
        )

    else:

        queue_item.status = (
            "Pending Verification"
        )

        message = (

            f"Verification pass recorded "

            f"({queue_item.passes_checked}/"
            f"{passes_needed})"

        )

    db.commit()

    db.refresh(queue_item)

    return {

        "message": message,

        "queue_id": queue_item.id,

        "incident_id": (
            queue_item.incident_id
        ),

        "passes_checked": (
            queue_item.passes_checked
        ),

        "passes_needed": (
            queue_item.passes_needed
        ),

        "status": queue_item.status

    }


# ============================================================
# DISPUTE PENDING ISSUE
# ============================================================

@app.post("/api/v1/verification/{queue_id}/dispute")
def dispute_pending_issue(

    queue_id: int,

    db: Session = Depends(get_db)

):

    queue_item = (
        db.query(models.VerificationQueue)
        .filter(
            models.VerificationQueue.id
            == queue_id
        )
        .first()
    )

    if not queue_item:

        raise HTTPException(
            status_code=404,
            detail="Verification queue item not found"
        )

    if queue_item.status in [
        "Verified",
        "Disputed"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Issue is already "
                f"{queue_item.status}"
            )
        )

    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.id
            == queue_item.incident_id
        )
        .first()
    )

    old_incident_status = (
        incident.status
        if incident
        else queue_item.status
    )

    queue_item.status = "Disputed"

    if incident:

        incident.status = "Disputed"

        db.add(
            models.StatusHistory(

                incident_id=incident.id,

                old_status=old_incident_status,

                new_status="Disputed"

            )
        )

    db.commit()

    db.refresh(queue_item)

    return {

        "message": "Issue marked as disputed",

        "queue_id": queue_item.id,

        "incident_id": (
            queue_item.incident_id
        ),

        "status": queue_item.status

    }


# ============================================================
# RE-ALERT SPECIFIC INCIDENT
# ============================================================

@app.post("/api/v1/incidents/{incident_id}/re-alert")
def re_alert_incident(

    incident_id: int,

    db: Session = Depends(get_db)

):

    incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.id
            == incident_id
        )
        .first()
    )

    if not incident:

        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    if incident.status == "Verified":

        raise HTTPException(
            status_code=400,
            detail=(
                "Incident is already "
                "verified and resolved"
            )
        )

    if incident.status == "Resolved":

        raise HTTPException(
            status_code=400,
            detail=(
                "Incident is resolved and "
                "waiting for verification"
            )
        )

    existing_realert = (
        db.query(models.Alert)
        .filter(
            models.Alert.incident_id
            == incident.id,

            models.Alert.message.contains(
                "SLA BREACHED"
            )
        )
        .first()
    )

    if existing_realert:

        return {

            "message": (
                "Incident has already "
                "been re-alerted"
            ),

            "incident_id": incident.id,

            "authority": incident.authority,

            "re_alert_created": False

        }

    message = (

        f"SLA BREACHED: "
        f"{incident.event_type} at "
        f"({incident.latitude}, "
        f"{incident.longitude}) "
        f"remains unresolved. "

        f"Priority: "
        f"{incident.priority}. "

        f"Re-alert sent to the "
        f"responsible authority: "
        f"{incident.authority}."

    )

    alert = models.Alert(

        incident_id=incident.id,

        authority=incident.authority,

        priority=incident.priority,

        message=message,

        sent=True

    )

    db.add(alert)

    db.commit()

    db.refresh(alert)

    return {

        "message": "Re-alert sent successfully",

        "incident_id": incident.id,

        "authority": incident.authority,

        "priority": incident.priority,

        "re_alert_created": True,

        "alert_id": alert.id,

        "alert": message

    }


# ============================================================
# VIDEO DETECTION HELPERS
# ============================================================

ISSUE_SOURCES = {
    "road_damage",
    "infrastructure"
}


def _pick(
    det: dict,
    *keys,
    default=None
):

    for key in keys:

        value = det.get(key)

        if value not in (
            None,
            "",
            []
        ):

            return value

    return default


def _normalize_type(
    raw_type: str
) -> str:

    if not raw_type:

        return "unknown"

    return (
        str(raw_type)
        .strip()
        .lower()
        .replace("_", " ")
    )


def _normalize_source(
    raw_source
) -> str:

    return (
        str(raw_source or "unknown")
        .strip()
        .lower()
    )


def _priority_from_confidence(
    conf
) -> str:

    try:

        c = float(conf)

    except (
        TypeError,
        ValueError
    ):

        return "MEDIUM"

    if c >= 0.75:

        return "CRITICAL"

    if c >= 0.55:

        return "HIGH"

    if c >= 0.35:

        return "MEDIUM"

    return "LOW"


def _authority_from_source(
    source: str
) -> str:

    return {

        "road_damage": "PWD",

        "infrastructure":
            "Municipal Corporation",

        "vehicle":
            "Traffic Police",

    }.get(
        source,
        "PWD"
    )


def _pseudo_coords(
    frame_id
) -> tuple:

    try:

        fid = int(
            frame_id or 0
        )

    except (
        TypeError,
        ValueError
    ):

        fid = 0

    return (

        round(
            28.7041
            + fid * 0.00001,
            6
        ),

        round(
            77.1025
            + fid * 0.00001,
            6
        )

    )


def _load_detection_file(
    detection_json: Path
):

    if not detection_json.exists():

        raise HTTPException(

            status_code=404,

            detail=(
                "Detection JSON not found: "
                f"{detection_json}"
            )

        )

    try:

        with open(
            detection_json,
            "r"
        ) as f:

            return json.load(f)

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Could not read detection JSON: "
                f"{str(e)}"
            )

        )


# ============================================================
# RUN M1
# ============================================================

def _run_m1_detection(
    video_path: Path
):

    if not M1_PYTHON.exists():

        raise HTTPException(

            status_code=500,

            detail=(
                f"M1 Python not found: "
                f"{M1_PYTHON}"
            )

        )

    if not M1_DETECT_SCRIPT.exists():

        raise HTTPException(

            status_code=500,

            detail=(
                f"M1 detect.py not found: "
                f"{M1_DETECT_SCRIPT}"
            )

        )

    try:

        result = subprocess.run(

            [

                str(M1_PYTHON),

                str(M1_DETECT_SCRIPT),

                str(video_path)

            ],

            cwd=str(
                M1_PROJECT_ROOT
            ),

            capture_output=True,

            text=True,

            timeout=1800

        )

    except subprocess.TimeoutExpired:

        raise HTTPException(

            status_code=500,

            detail=(
                "M1 detection timed out "
                "after 30 minutes."
            )

        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Could not start M1 detection: "
                f"{str(e)}"
            )

        )

    if result.returncode != 0:

        raise HTTPException(

            status_code=500,

            detail={

                "message":
                    "M1 detection failed",

                "stdout":
                    result.stdout[-4000:],

                "stderr":
                    result.stderr[-4000:]

            }

        )

    video_name = video_path.stem

    detection_json = (

        M1_OUTPUTS_DIR
        / f"{video_name}_detections.json"

    )

    detection_video = (

        M1_OUTPUTS_DIR
        / f"{video_name}_detection.mp4"

    )

    if not detection_json.exists():

        raise HTTPException(

            status_code=500,

            detail=(

                "M1 finished but detection "
                "JSON was not created: "

                f"{detection_json}"

            )

        )

    return {

        "detection_json":
            detection_json,

        "detection_video":
            detection_video,

        "stdout":
            result.stdout,

        "stderr":
            result.stderr

    }


# ============================================================
# VIDEO DETECTION UPLOAD
# ============================================================

@app.post("/api/v1/detection/upload")
async def upload_detection_video(

    file: UploadFile = File(...),

    phase: str = Form("input"),

    db: Session = Depends(get_db),

):

    if not file.filename:

        raise HTTPException(

            status_code=400,

            detail="No video file provided"

        )

    allowed_extensions = {

        ".mp4",

        ".avi",

        ".mov",

        ".mkv"

    }

    original_filename = Path(
        file.filename
    ).name

    extension = Path(
        original_filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(

            status_code=400,

            detail="Only video files are allowed"

        )

    if phase not in {
        "input",
        "output"
    }:

        raise HTTPException(

            status_code=400,

            detail=(
                "phase must be "
                "'input' or 'output', "
                f"got '{phase}'"
            )

        )

    # --------------------------------------------------------
    # UNIQUE VIDEO NAME
    # --------------------------------------------------------

    original_stem = Path(
        original_filename
    ).stem

    video_name = (

        f"{original_stem}_"
        f"{uuid4().hex[:8]}"

    )

    saved_video = (

        M1_VIDEOS_DIR
        / f"{video_name}{extension}"

    )

    # --------------------------------------------------------
    # SAVE UPLOADED VIDEO
    # --------------------------------------------------------

    try:

        with open(
            saved_video,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:

                    break

                buffer.write(chunk)

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Could not save uploaded "
                f"video: {str(e)}"
            )

        )

    # --------------------------------------------------------
    # RUN M1
    # --------------------------------------------------------

    m1_result = _run_m1_detection(
        saved_video
    )

    detection_json = (
        m1_result["detection_json"]
    )

    detection_video = (
        m1_result["detection_video"]
    )

    # --------------------------------------------------------
    # READ M1 JSON
    # --------------------------------------------------------

    detections = _load_detection_file(
        detection_json
    )

    # --------------------------------------------------------
    # CREATE INCIDENTS
    # --------------------------------------------------------

    created_incidents = []

    skipped = 0

    if phase == "input":

        seen_keys = set()

        for det in detections:

            source = _normalize_source(
                det.get("source")
            )

            # Vehicle detections are still
            # returned to React but do not
            # create civic incidents here.

            if source not in ISSUE_SOURCES:

                skipped += 1

                continue

            event_type = _normalize_type(
                det.get("type")
            )

            key = (
                source,
                event_type
            )

            if key in seen_keys:

                continue

            seen_keys.add(key)

            latitude, longitude = (
                _pseudo_coords(
                    det.get("frame_id")
                )
            )

            confidence = det.get(
                "confidence"
            )

            priority = (
                _priority_from_confidence(
                    confidence
                )
            )

            authority = (
                _authority_from_source(
                    source
                )
            )

            risk_score = (
                SEVERITY_SCORES.get(
                    priority.lower(),
                    50
                )
            )

            incident = models.Incident(

                event_type=event_type,

                latitude=latitude,

                longitude=longitude,

                priority=priority,

                authority=authority,

                status="Open",

                risk_score=risk_score,

                source=source,

                session_id=video_name,

                sla_deadline=(
                    datetime.utcnow()
                    + timedelta(days=7)
                ),

            )

            db.add(incident)

            created_incidents.append(
                incident
            )

        db.commit()

        for incident in created_incidents:

            db.refresh(incident)

    # --------------------------------------------------------
    # OUTPUT URL
    # --------------------------------------------------------

    detection_video_url = (

        f"/api/v1/detection/video/"
        f"{detection_video.name}"

    )

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "message":
            "Video processed successfully by M1",

        "phase":
            phase,

        "filename":
            original_filename,

        "session_id":
            video_name,

        "detection_count":
            len(detections),

        "detections":
            detections,

        "detection_json":
            str(detection_json),

        "detection_video":
            str(detection_video),

        "detection_video_url":
            detection_video_url,

        "incidents_created":
            len(created_incidents),

        "incident_ids": [

            incident.id

            for incident
            in created_incidents

        ],

        "incidents_skipped":
            skipped,

        "m1": {

            "status":
                "completed",

            "stdout":
                m1_result[
                    "stdout"
                ][-2000:]

        }

    }


# ============================================================
# RESET INCIDENTS
# ============================================================

@app.post("/api/v1/incidents/reset")
def reset_incidents(
    db: Session = Depends(get_db)
):

    deleted = (
        db.query(
            models.Incident
        ).delete()
    )

    db.query(
        models.Alert
    ).delete()

    db.query(
        models.StatusHistory
    ).delete()

    db.commit()

    return {

        "message":
            "All incidents, alerts and "
            "status history deleted",

        "incidents_deleted":
            deleted

    }


# ============================================================
# SERVE DETECTION VIDEO
# ============================================================

@app.get(
    "/api/v1/detection/video/{video_name}"
)
def get_detection_video(
    video_name: str
):

    safe_video_name = Path(
        video_name
    ).name

    video_path = (
        M1_OUTPUTS_DIR
        / safe_video_name
    )

    if not video_path.exists():

        raise HTTPException(

            status_code=404,

            detail="Detection video not found"

        )

    return FileResponse(

        path=str(video_path),

        media_type="video/mp4",

        filename=safe_video_name

    )

