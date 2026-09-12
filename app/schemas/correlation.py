from pydantic import BaseModel


class VesselCorrelation(BaseModel):
    """A candidate vessel's correlation score against a spill incident."""
    
    mmsi: str
    vessel_name: str
    distance_km: float
    time_diff_minutes: float
    spatial_temporal_score: float