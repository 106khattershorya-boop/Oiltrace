from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class MLVesselTarget(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    rank: Optional[int] = None
    mmsi: Optional[int] = Field(default=None, alias="MMSI")
    vessel_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None
    time_difference_minutes: Optional[float] = None
    spatial_score: Optional[float] = None
    temporal_score: Optional[float] = None
    vessel_behaviour_score: Optional[float] = None
    combined_behaviour_score: Optional[float] = None
    probable_oil_category: Optional[str] = None
    ais_confidence: Optional[str] = None
    investigation_priority_score: Optional[float] = None
    priority_level: Optional[str] = None
    reasons: List[str] = []


class MLAnalysisResult(BaseModel):
    incident_id: str
    ml_run_id: str
    latitude: float
    longitude: float
    event_time: str
    spill_detected: bool
    spill_area_percent: float
    false_positive_classification: str
    probable_oil_category: str
    category_confidence_percent: float
    unique_vessels: int
    investigation_targets: List[MLVesselTarget]
    disclaimer: str


class MLAnalysisRejected(BaseModel):
    incident_id: str
    ml_run_id: str
    error: str
    message: str
    recommendation: Optional[str] = None