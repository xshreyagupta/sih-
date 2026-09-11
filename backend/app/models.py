from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON

from datetime import datetime

from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    class_name = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    detected_at = Column(DateTime, nullable=False)
    authority = Column(JSON, nullable=False)


class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(Integer, primary_key=True, index=True)

    location_id = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    expected_infrastructure = Column(String, nullable=False)

    detected_infrastructure = Column(String, nullable=True)
    status = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)


class TrafficObservation(Base):
    __tablename__ = "traffic_observations"

    id = Column(Integer, primary_key=True, index=True)

    frame_id = Column(Integer, nullable=False, index=True)
    timestamp_ms = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    vehicle_count = Column(Integer, nullable=False)
    avg_speed = Column(Float, nullable=False)
    congestion_level = Column(String, nullable=False)


class PriorityResult(Base):
    __tablename__ = "priority_results"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(String, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    priority = Column(String, nullable=False)

    factors = Column(JSON, nullable=False)
    location = Column(JSON, nullable=False)

    timestamp = Column(DateTime, nullable=False)


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(Integer, nullable=True, index=True)
    location_id = Column(String, nullable=True, index=True)

    event_type = Column(String, nullable=False)

    class_name = Column(String, nullable=True)

    expected_infrastructure = Column(String, nullable=True)
    detected_infrastructure = Column(String, nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    verification_result = Column(String, nullable=False)

    confidence = Column(Float, nullable=True)


# -------------------------------------------------------------------
# Existing application models
# -------------------------------------------------------------------


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    priority = Column(String, nullable=False)
    authority = Column(String, nullable=False)
    status = Column(String, default="Open")
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    sla_deadline = Column(DateTime, nullable=True)

    # NEW
    source = Column(String, nullable=True, index=True)
    session_id = Column(String, nullable=True, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False)
    authority = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    message = Column(String, nullable=False)
    sent = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class VerificationQueue(Base):
    __tablename__ = "verification_queue"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    defect_type = Column(String, nullable=False)
    marked_resolved_at = Column(DateTime, nullable=True)
    passes_checked = Column(Integer, default=0)
    passes_needed = Column(Integer, default=2)
    status = Column(String, default="Pending Verification")


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False)
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)