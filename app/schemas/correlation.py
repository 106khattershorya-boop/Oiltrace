from pydantic import BaseModel


class VesselCorrelation(BaseModel):
    mmsi: str
    vessel_name: str
    distance_km: float
    time_diff_minutes: float
    spatial_score: float
    temporal_score: float
    trajectory_score: float | None = None
    combined_score: float
