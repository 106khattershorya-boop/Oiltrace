import httpx

from app.core.config import settings
from app.schemas.ml_analysis import (
    MLAnalysisResult,
    MLAnalysisRejected,
    MLVesselTarget,
)


async def call_ml_analyze(
    incident_id: str,
    latitude: float,
    longitude: float,
    event_time: str,
    image_bytes: bytes,
    image_filename: str,
):
    url = f"{settings.ML_API_BASE_URL}/analyze"

    files = {
        "image": (image_filename, image_bytes)
    }

    data = {
        "latitude": str(latitude),
        "longitude": str(longitude),
        "event_time": event_time,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(
            url,
            data=data,
            files=files,
        )

        response.raise_for_status()
        payload = response.json()

    # ML rejected the image
    if payload.get("status") == "rejected":
        return MLAnalysisRejected(
            incident_id=incident_id,
            ml_run_id=payload["run_id"],
            error=payload.get("error", "UNKNOWN_REJECTION"),
            message=payload.get(
                "message",
                "Input rejected by ML API.",
            ),
            recommendation=payload.get("recommendation"),
        )

    # Convert investigation targets
    targets = [
        MLVesselTarget(**target)
        for target in payload.get("investigation_targets", [])
    ]

    # Successful ML analysis
    return MLAnalysisResult(
        incident_id=incident_id,
        ml_run_id=payload["run_id"],
        latitude=payload["incident"]["latitude"],
        longitude=payload["incident"]["longitude"],
        event_time=payload["incident"]["time"],
        spill_detected=payload["spill_detection"]["detected"],
        spill_area_percent=payload["spill_detection"]["spill_area_percent"],
        false_positive_classification=payload["false_positive"]["classification"],
        probable_oil_category=payload["spectral_analysis"]["probable_oil_category"],
        category_confidence_percent=payload["spectral_analysis"]["category_confidence_percent"],
        unique_vessels=payload["ais"]["unique_vessels"],
        investigation_targets=targets,
        disclaimer=payload["disclaimer"],
    )