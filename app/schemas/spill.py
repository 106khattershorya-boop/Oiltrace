from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DetectionConfidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SpillIncidentCreate(BaseModel):
    """Data required to create a new spill incident."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    detection_time: datetime
    estimated_area_km2: float = Field(..., gt=0)
    detection_confidence: DetectionConfidence
    satellite_source: str = Field(..., examples=["Sentinel-1"])


class SpillIncident(SpillIncidentCreate):
    """Full spill incident record."""
    
    incident_id: str
    created_at: datetime