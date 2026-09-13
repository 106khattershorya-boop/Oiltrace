from enum import Enum
from pydantic import BaseModel


class PriorityLevel(str, Enum):
    high = "HIGH"
    medium_high = "MEDIUM-HIGH"
    medium = "MEDIUM"
    low = "LOW"


class VesselPriority(BaseModel):
    """Final explainable investigation-priority result for one vessel."""

    mmsi: str
    vessel_name: str
    final_priority_score: float
    priority_level: PriorityLevel
    reasons: list[str]

    combined_score: float
    behaviour_score: float
    spectral_score: float | None = None
    cargo_score: float | None = None
    distance_km: float | None = None
    time_difference_minutes: float | None = None
    spatial_score: float | None = None
    temporal_score: float | None = None
    trajectory_score: float | None = None