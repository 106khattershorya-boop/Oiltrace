from pydantic import BaseModel


class VesselEvidence(BaseModel):
    """All fused evidence for one vessel against one incident."""

    mmsi: str
    vessel_name: str

    combined_score: float
    distance_km: float
    time_diff_minutes: float

    behaviour_score: float

    speed_anomaly: bool | None = None
    stop_anomaly: bool | None = None
    course_deviation: bool | None = None
    ais_gap: bool | None = None
    loitering: bool | None = None

    spectral_score: float | None = None
    probable_oil_category: str | None = None

    cargo_score: float | None = None
