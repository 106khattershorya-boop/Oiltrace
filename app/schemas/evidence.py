from pydantic import BaseModel


class VesselEvidence(BaseModel):
    """All fused evidence for one vessel against one incident, before final scoring."""

    mmsi: str
    vessel_name: str

    combined_score: float
    distance_km: float
    time_diff_minutes: float

    behaviour_score: float
    speed_anomaly: bool
    stop_anomaly: bool
    course_deviation: bool
    ais_gap: bool
    loitering: bool

    spectral_score: float | None = None
    probable_oil_category: str | None = None

    cargo_score: float | None = None