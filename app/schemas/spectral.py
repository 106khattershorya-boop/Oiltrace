from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OilCategory(str, Enum):
    light_petroleum = "light_petroleum"
    heavy_petroleum = "heavy_petroleum"
    crude_oil_like = "crude_oil_like"
    refined_product_like = "refined_product_like"
    unknown = "unknown"


class SpectralResultCreate(BaseModel):
    """Submitted by the ML team once spectral analysis is run on an incident."""

    spectral_features: dict[str, Any] | str = Field(
        ...,
        description="Extracted spectral features as JSON data or JSON-encoded text",
    )

    probable_oil_category: str = Field(
        ...,
        description="ML-derived probable oil category",
    )

    spectral_score: float = Field(
        ...,
        ge=0,
        description="ML model spectral confidence/score",
    )


class SpectralResult(SpectralResultCreate):
    """Full spectral analysis record from PostgreSQL."""

    incident_id: int


class CargoCompatibilityCheck(BaseModel):
    """Compares vessel cargo against the incident's probable oil category."""

    mmsi: str
    vessel_cargo_category: str
    probable_oil_category: str
    cargo_score: float = Field(..., ge=0, le=1)