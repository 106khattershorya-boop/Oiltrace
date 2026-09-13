from datetime import datetime

from pydantic import BaseModel, Field


class SpillIncidentCreate(BaseModel):
    """Data required to create a new spill incident."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    detection_time: datetime
    estimated_area_km2: float | None = None
    detection_confidence: float | None = None
    satellite_source: str


class SpillIncident(SpillIncidentCreate):
    """Full spill incident record from PostgreSQL."""

    incident_id: int