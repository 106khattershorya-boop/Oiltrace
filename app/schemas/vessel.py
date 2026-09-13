from datetime import datetime

from pydantic import BaseModel, Field


class AISReportCreate(BaseModel):
    """A single AIS position report for a vessel."""

    mmsi: str = Field(
        ...,
        min_length=9,
        max_length=9,
        examples=["123456789"]
    )

    vessel_name: str | None = None

    latitude: float = Field(..., ge=-90, le=90)

    longitude: float = Field(..., ge=-180, le=180)

    speed_knots: float | None = Field(default=None, ge=0)

    course_degrees: float | None = Field(
        default=None,
        ge=0,
        lt=360
    )

    timestamp: datetime

    vessel_type: str | None = None


class AISReport(AISReportCreate):
    """Full AIS report record, with a system-assigned ID."""

    report_id: str