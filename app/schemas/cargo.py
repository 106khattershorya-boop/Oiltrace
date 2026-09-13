from pydantic import BaseModel, Field


class CargoScoreCreate(BaseModel):
    """Cargo compatibility score for a vessel involved in an incident."""

    mmsi: str = Field(..., min_length=9, max_length=9)
    vessel_cargo_category: str
    cargo_score: float = Field(..., ge=0, le=1)


class CargoScore(CargoScoreCreate):
    """Full cargo compatibility record."""

    incident_id: int