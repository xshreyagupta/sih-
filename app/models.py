from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime

from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    client_event_id = Column(String, unique=True, index=True)
    event_type = Column(String, nullable=False)

    source_bus = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    confidence = Column(Float, nullable=False)
    severity = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)


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

    # SLA deadline
    sla_deadline = Column(DateTime, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    incident_id = Column(Integer, nullable=False)

    authority = Column(String, nullable=False)
    priority = Column(String, nullable=False)

    message = Column(String, nullable=False)

    sent = Column(Boolean, default=False)

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
    