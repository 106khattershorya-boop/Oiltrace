from pydantic import BaseModel, Field


class CargoScoreCreate(BaseModel):
    """Submitted by whoever computes cargo compatibility (teammate or manual entry
    for the MVP, since there's no cargo database yet)."""
    mmsi: str
    vessel_cargo_category: str
    cargo_score: float = Field(..., ge=0, le=1)


class CargoScore(CargoScoreCreate):
    incident_id: str