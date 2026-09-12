from enum import Enum
from pydantic import BaseModel, Field


class OilCategory(str, Enum):
    light_petroleum = "light_petroleum"
    heavy_petroleum = "heavy_petroleum"
    crude_oil_like = "crude_oil_like"
    refined_product_like = "refined_product_like"
    unknown = "unknown"


class SpectralResultCreate(BaseModel):
    """Submitted by the ML team once spectral analysis is run on an incident."""

    spectral_features: str = Field(
        ...,
        description="Free-text or JSON-encoded summary of extracted spectral features",
    )
    probable_oil_category: OilCategory
    spectral_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="ML model's confidence in the category",
    )


class SpectralResult(SpectralResultCreate):
    incident_id: str


class CargoCompatibilityCheck(BaseModel):
    """Compares vessel cargo against the incident's probable oil category."""

    mmsi: str
    vessel_cargo_category: str
    probable_oil_category: OilCategory
    cargo_score: float = Field(..., ge=0, le=1)