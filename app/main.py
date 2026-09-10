from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .database import engine, Base, get_db
from . import models
from .schemas import EventCreate, StatusUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Urban Intelligence Backend",
    version="1.0.0"
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Urban Intelligence Backend is running"
    }


# =========================================================
# CREATE EVENT
# =========================================================

@app.post("/api/v1/events")
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):

    # -------------------------
    # 1. Check exact duplicate
    # -------------------------

    existing_event = db.query(models.Event).filter(
        models.Event.client_event_id == event.client_event_id
    ).first()

    if existing_event:

        existing_incident = db.query(models.Incident).filter(
            models.Incident.event_type == existing_event.event_type,
            models.Incident.latitude == existing_event.latitude,
            models.Incident.longitude == existing_event.longitude
        ).first()

        return {
            "message": "Duplicate event detected",
            "event_id": existing_event.id,
            "incident_id": existing_incident.id if existing_incident else None,
            "event_type": existing_event.event_type,
            "duplicate": True
        }

    # -------------------------
    # 2. Create Event
    # -------------------------

    new_event = models.Event(
        client_event_id=event.client_event_id,
        event_type=event.event_type,
        source_bus=event.source_bus,
        latitude=event.latitude,
        longitude=event.longitude,
        confidence=event.confidence,
        severity=event.severity,
        timestamp=event.timestamp
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # -------------------------
    # 3. Calculate Risk
    # -------------------------

    risk_score = event.confidence

    if risk_score >= 0.9:
        priority = "Critical"
    elif risk_score >= 0.75:
        priority = "High"
    elif risk_score >= 0.5:
        priority = "Medium"
    else:
        priority = "Low"

    # -------------------------
    # 4. Decide Authority
    # -------------------------

    authority_map = {
        "pothole": "PWD",
        "waterlogging": "Municipal Corporation",
        "streetlight": "Electrical Department",
        "traffic_signal": "Traffic Police",
        "zebra_crossing": "Traffic Police",
        "divider": "PWD"
    }

    authority = authority_map.get(
        event.event_type,
        "Municipal Corporation"
    )

    # -------------------------
    # 5. Check location duplicate
    # -------------------------

    existing_incidents = db.query(models.Incident).filter(
        models.Incident.event_type == event.event_type
    ).all()

    duplicate_incident = None

    for incident in existing_incidents:

        lat_diff = abs(incident.latitude - event.latitude)
        lon_diff = abs(incident.longitude - event.longitude)

        if lat_diff < 0.0002 and lon_diff < 0.0002:
            duplicate_incident = incident
            break

    # -------------------------
    # 6. If location duplicate
    # -------------------------

    if duplicate_incident:

        return {
            "message": "Duplicate event detected by location",
            "event_id": new_event.id,
            "incident_id": duplicate_incident.id,
            "event_type": duplicate_incident.event_type,
            "priority": duplicate_incident.priority,
            "authority": duplicate_incident.authority,
            "status": duplicate_incident.status,
            "duplicate": True
        }

    # -------------------------
    # 7. SLA
    # -------------------------

    sla_hours = {
        "Critical": 24,
        "High": 72,
        "Medium": 168,
        "Low": 168
    }

    deadline = datetime.utcnow() + timedelta(
        hours=sla_hours[priority]
    )

    # -------------------------
    # 8. Create Incident
    # -------------------------

    incident = models.Incident(
        event_type=event.event_type,
        latitude=event.latitude,
        longitude=event.longitude,
        priority=priority,
        authority=authority,
        status="Open",
        risk_score=risk_score,
        sla_deadline=deadline
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    # -------------------------
    # 9. Create Alert
    # -------------------------

    alert = models.Alert(
        incident_id=incident.id,
        authority=authority,
        priority=priority,
        message=(
            f"{priority} {event.event_type} detected at "
            f"{event.latitude}, {event.longitude}"
        ),
        sent=True
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    # -------------------------
    # 10. Response
    # -------------------------

    return {
        "message": "Event received and incident created",
        "event_id": new_event.id,
        "incident_id": incident.id,
        "event_type": incident.event_type,
        "priority": incident.priority,
        "authority": incident.authority,
        "status": incident.status,
        "risk_score": incident.risk_score,
        "sla_deadline": deadline.isoformat(),
        "alert_id": alert.id,
        "alert": alert.message,
        "duplicate": False
    }


# =========================================================
# SLA CHECK
# =========================================================

@app.post("/api/v1/sla/check")
def check_sla(
    db: Session = Depends(get_db)
):

    now = datetime.utcnow()

    overdue_incidents = db.query(models.Incident).filter(
        models.Incident.sla_deadline != None,
        models.Incident.sla_deadline < now,
        models.Incident.status.notin_([
            "Resolved",
            "Pending Verification",
            "Verified"
        ])
    ).all()

    results = []

    for incident in overdue_incidents:

        # Check if SLA re-alert already exists
        existing_alert = db.query(models.Alert).filter(
            models.Alert.incident_id == incident.id,
            models.Alert.message.like("SLA overdue:%")
        ).first()

        if existing_alert:

            results.append({
                "incident_id": incident.id,
                "event_type": incident.event_type,
                "priority": incident.priority,
                "authority": incident.authority,
                "status": incident.status,
                "sla_deadline": incident.sla_deadline.isoformat(),
                "message": "SLA overdue - re-alert already sent"
            })

            continue

        # Create SLA re-alert
        alert = models.Alert(
            incident_id=incident.id,
            authority=incident.authority,
            priority=incident.priority,
            message=(
                f"SLA overdue: {incident.priority} "
                f"{incident.event_type} at "
                f"{incident.latitude}, {incident.longitude} "
                f"has not been resolved."
            ),
            sent=True
        )

        db.add(alert)

        results.append({
            "incident_id": incident.id,
            "event_type": incident.event_type,
            "priority": incident.priority,
            "authority": incident.authority,
            "status": incident.status,
            "sla_deadline": incident.sla_deadline.isoformat(),
            "message": "SLA overdue - authority re-alerted"
        })

    db.commit()

    return {
        "message": "SLA check completed",
        "overdue_count": len(overdue_incidents),
        "overdue_incidents": results
    }


# =========================================================
# UPDATE INCIDENT STATUS
# =========================================================

@app.patch("/api/v1/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    update: StatusUpdate,
    db: Session = Depends(get_db)
):

    allowed_statuses = [
        "Open",
        "Acknowledged",
        "In Progress",
        "Resolved",
        "Pending Verification",
        "Verified",
        "Disputed"
    ]

    status = update.status

    # Check valid status
    if status not in allowed_statuses:
        return {
            "message": "Invalid status",
            "allowed_statuses": allowed_statuses
        }

    # Find incident
    incident = db.query(models.Incident).filter(
        models.Incident.id == incident_id
    ).first()

    if not incident:
        return {
            "message": "Incident not found"
        }

    # Store previous status
    old_status = incident.status

    # Update status
    incident.status = status

    # If resolved, create verification task
    if status == "Resolved":

        incident.resolved_at = datetime.utcnow()

        verification = models.VerificationQueue(
            incident_id=incident.id,
            latitude=incident.latitude,
            longitude=incident.longitude,
            defect_type=incident.event_type,
            marked_resolved_at=datetime.utcnow(),
            passes_checked=0,
            passes_needed=2,
            status="Pending Verification"
        )

        db.add(verification)

    # Create status history
    history = models.StatusHistory(
        incident_id=incident.id,
        old_status=old_status,
        new_status=status,
        changed_at=datetime.utcnow()
    )

    db.add(history)

    db.commit()

    db.refresh(incident)
    db.refresh(history)

    return {
        "message": "Incident status updated",
        "incident_id": incident.id,
        "old_status": old_status,
        "new_status": incident.status,
        "changed_at": history.changed_at.isoformat()
    }


# =========================================================
# VERIFICATION QUEUE
# =========================================================

@app.get("/api/v1/verification")
def get_verification_queue(
    db: Session = Depends(get_db)
):

    queue = db.query(
        models.VerificationQueue
    ).all()

    return [
        {
            "id": item.id,
            "incident_id": item.incident_id,
            "defect_type": item.defect_type,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "passes_checked": item.passes_checked,
            "passes_needed": item.passes_needed,
            "status": item.status
        }
        for item in queue
    ]


# =========================================================
# VERIFICATION CHECK
# =========================================================

@app.post("/api/v1/verification/check")
def check_verification(
    latitude: float,
    longitude: float,
    event_type: str,
    issue_detected: bool,
    db: Session = Depends(get_db)
):

    verification = db.query(
        models.VerificationQueue
    ).filter(
        models.VerificationQueue.status == "Pending Verification",
        models.VerificationQueue.defect_type == event_type
    ).first()

    if not verification:
        return {
            "message": "No matching verification task found"
        }

    # Approximate location check (~20 meters)
    lat_diff = abs(latitude - verification.latitude)
    lon_diff = abs(longitude - verification.longitude)

    if lat_diff >= 0.0002 or lon_diff >= 0.0002:

        return {
            "message": "Bus detection is too far from verification location",
            "status": verification.status
        }

    # Get related incident
    incident = db.query(
        models.Incident
    ).filter(
        models.Incident.id == verification.incident_id
    ).first()

    # -----------------------------------------------------
    # CASE 1: Defect still present
    # -----------------------------------------------------

    if issue_detected:

        verification.status = "Disputed"

        if incident:

            incident.status = "Disputed"

            alert = models.Alert(
                incident_id=incident.id,
                authority=incident.authority,
                priority=incident.priority,
                message=(
                    f"Resolution disputed: {event_type} "
                    f"still detected at "
                    f"{verification.latitude}, "
                    f"{verification.longitude}"
                ),
                sent=True
            )

            db.add(alert)

        db.commit()
        db.refresh(verification)

        return {
            "message": "Defect still detected. Resolution disputed.",
            "verification_id": verification.id,
            "passes_checked": verification.passes_checked,
            "passes_needed": verification.passes_needed,
            "status": verification.status
        }

    # -----------------------------------------------------
    # CASE 2: Defect NOT present
    # -----------------------------------------------------

    verification.passes_checked += 1

    if verification.passes_checked >= verification.passes_needed:

        verification.status = "Verified"

        if incident:
            incident.status = "Verified"

    db.commit()
    db.refresh(verification)

    return {
        "message": "Verification pass recorded. Defect not detected.",
        "verification_id": verification.id,
        "passes_checked": verification.passes_checked,
        "passes_needed": verification.passes_needed,
        "status": verification.status
    }


# =========================================================
# GET ALL INCIDENTS
# =========================================================

@app.get("/api/v1/incidents")
def get_incidents(
    status: str = None,
    priority: str = None,
    event_type: str = None,
    db: Session = Depends(get_db)
):

    query = db.query(models.Incident)

    # Filter by status
    if status:
        query = query.filter(
            models.Incident.status == status
        )

    # Filter by priority
    if priority:
        query = query.filter(
            models.Incident.priority == priority
        )

    # Filter by event type
    if event_type:
        query = query.filter(
            models.Incident.event_type == event_type
        )

    incidents = query.all()

    return [
        {
            "id": incident.id,
            "event_type": incident.event_type,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "priority": incident.priority,
            "authority": incident.authority,
            "status": incident.status,
            "risk_score": incident.risk_score,
            "created_at": incident.created_at,
            "resolved_at": incident.resolved_at,
            "sla_deadline": incident.sla_deadline
        }
        for incident in incidents
    ]

# =========================================================
# GET ALL ALERTS
# =========================================================

@app.get("/api/v1/alerts")
def get_alerts(
    db: Session = Depends(get_db)
):

    alerts = db.query(
        models.Alert
    ).all()

    return [
        {
            "id": alert.id,
            "incident_id": alert.incident_id,
            "authority": alert.authority,
            "priority": alert.priority,
            "message": alert.message,
            "sent": alert.sent,
            "created_at": alert.created_at
        }
        for alert in alerts
    ]


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@app.get("/api/v1/dashboard")
def dashboard_summary(
    db: Session = Depends(get_db)
):

    # Get all incidents
    incidents = db.query(
        models.Incident
    ).all()

    # -----------------------------------------------------
    # TOTAL INCIDENTS
    # -----------------------------------------------------

    total_incidents = len(incidents)

    # -----------------------------------------------------
    # STATUS COUNTS
    # -----------------------------------------------------

    open_count = sum(
        1 for i in incidents
        if i.status == "Open"
    )

    acknowledged_count = sum(
        1 for i in incidents
        if i.status == "Acknowledged"
    )

    in_progress_count = sum(
        1 for i in incidents
        if i.status == "In Progress"
    )

    resolved_count = sum(
        1 for i in incidents
        if i.status == "Resolved"
    )

    pending_verification_count = sum(
        1 for i in incidents
        if i.status == "Pending Verification"
    )

    verified_count = sum(
        1 for i in incidents
        if i.status == "Verified"
    )

    disputed_count = sum(
        1 for i in incidents
        if i.status == "Disputed"
    )

    # -----------------------------------------------------
    # PRIORITY COUNTS
    # -----------------------------------------------------

    critical_count = sum(
        1 for i in incidents
        if i.priority == "Critical"
    )

    high_count = sum(
        1 for i in incidents
        if i.priority == "High"
    )

    medium_count = sum(
        1 for i in incidents
        if i.priority == "Medium"
    )

    low_count = sum(
        1 for i in incidents
        if i.priority == "Low"
    )

    # -----------------------------------------------------
    # EVENT TYPE COUNTS
    # -----------------------------------------------------

    pothole_count = sum(
        1 for i in incidents
        if i.event_type == "pothole"
    )

    waterlogging_count = sum(
        1 for i in incidents
        if i.event_type == "waterlogging"
    )

    streetlight_count = sum(
        1 for i in incidents
        if i.event_type == "streetlight"
    )

    traffic_signal_count = sum(
        1 for i in incidents
        if i.event_type == "traffic_signal"
    )

    zebra_crossing_count = sum(
        1 for i in incidents
        if i.event_type == "zebra_crossing"
    )

    divider_count = sum(
        1 for i in incidents
        if i.event_type == "divider"
    )

    # -----------------------------------------------------
    # SLA OVERDUE COUNT
    # -----------------------------------------------------

    now = datetime.utcnow()

    overdue_count = sum(
        1 for i in incidents
        if i.sla_deadline is not None
        and i.sla_deadline < now
        and i.status not in [
            "Resolved",
            "Pending Verification",
            "Verified"
        ]
    )

    # -----------------------------------------------------
    # RETURN DASHBOARD DATA
    # -----------------------------------------------------

    return {

        "message": "Dashboard summary",

        "total_incidents": total_incidents,

        "status": {
            "open": open_count,
            "acknowledged": acknowledged_count,
            "in_progress": in_progress_count,
            "resolved": resolved_count,
            "pending_verification": pending_verification_count,
            "verified": verified_count,
            "disputed": disputed_count
        },

        "priority": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },

        "event_types": {
            "pothole": pothole_count,
            "waterlogging": waterlogging_count,
            "streetlight": streetlight_count,
            "traffic_signal": traffic_signal_count,
            "zebra_crossing": zebra_crossing_count,
            "divider": divider_count
        },

        "sla": {
            "overdue": overdue_count
        }
    }