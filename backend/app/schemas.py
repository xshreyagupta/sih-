from pydantic import BaseModel, Field

from datetime import datetime

from typing import Optional


# ============================================================
# EVENTS
# Matches events.json exactly
# ============================================================

class Authority(BaseModel):
    id: int
    name: str


class EventCreate(BaseModel):
    class_name: str
    severity: str
    latitude: float
    longitude: float
    detected_at: datetime
    authority: Authority


# ============================================================
# INFRASTRUCTURE
# Matches infrastructure.json exactly
# ============================================================

class InfrastructureCreate(BaseModel):
    location_id: str
    latitude: float
    longitude: float
    expected_infrastructure: str
    detected_infrastructure: str
    status: str
    confidence: float = Field(ge=0, le=1)


# ============================================================
# TRAFFIC
# Matches traffic JSON exactly
# ============================================================

class TrafficCreate(BaseModel):
    frame_id: int
    timestamp_ms: int
    latitude: float
    longitude: float
    vehicle_count: int
    avg_speed: float
    congestion_level: str


# ============================================================
# M5 PRIORITY ENGINE OUTPUT
# Matches output.json exactly
# ============================================================

class PriorityFactors(BaseModel):
    severity_score: float
    congestion_score: float
    sighting_count: int
    recency_weight: float
    severity_trend_slope: float
    bottleneck: bool
    vehicle_count: float
    traffic_density: float
    average_speed: float


class PriorityLocation(BaseModel):
    latitude: float
    longitude: float


class PriorityResultCreate(BaseModel):
    event_id: str
    risk_score: float
    priority: str
    factors: PriorityFactors
    location: PriorityLocation
    timestamp: datetime


# ============================================================
# VERIFICATION
# Matches both types of records in verification.json
# ============================================================

class VerificationCreate(BaseModel):
    event_id: Optional[int] = None
    location_id: Optional[str] = None
    event_type: str
    class_name: Optional[str] = None
    expected_infrastructure: Optional[str] = None
    detected_infrastructure: Optional[str] = None
    latitude: float
    longitude: float
    verification_result: str
    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1
    )


# ============================================================
# EXISTING INCIDENT STATUS UPDATE
# Kept for your current frontend/backend functionality
# ============================================================

class StatusUpdate(BaseModel):
    status: str