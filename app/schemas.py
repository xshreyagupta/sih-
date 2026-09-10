from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class EventCreate(BaseModel):
    client_event_id: str
    event_type: str
    source_bus: str

    latitude: float
    longitude: float

    confidence: float = Field(ge=0, le=1)
    severity: str

    timestamp: Optional[datetime] = None

class StatusUpdate(BaseModel):
    status: str