import httpx

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services import ml_client
from app.storage import memory_store, ml_result_store
from app.schemas.ml_analysis import MLAnalysisRejected, MLAnalysisResult


router = APIRouter(
    prefix="/incidents",
    tags=["ML Analysis"],
)


@router.post("/{incident_id}/run-ml-analysis")
async def run_ml_analysis(
    incident_id: str,
    image: UploadFile = File(...),
):
    # Check that the incident exists
    incident = memory_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    # Read uploaded image
    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )

    try:
        result = await ml_client.call_ml_analyze(
            incident_id=incident_id,
            latitude=incident.latitude,
            longitude=incident.longitude,
            event_time=incident.detection_time.isoformat(),
            image_bytes=image_bytes,
            image_filename=image.filename or "image.png",
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
        status_code=502,
        detail={
            "ml_status": exc.response.status_code,
            "ml_response": exc.response.text,
        },
    )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach ML API: {str(exc)}",
        )

    # ML rejected the image
    if isinstance(result, MLAnalysisRejected):
        raise HTTPException(
            status_code=422,
            detail={
                "error": result.error,
                "message": result.message,
                "recommendation": result.recommendation,
            },
        )

    # Store successful result
    return ml_result_store.save_result(result)


@router.get(
    "/{incident_id}/ml-result",
    response_model=MLAnalysisResult,
)
def get_ml_result(incident_id: str):
    result = ml_result_store.get_result(incident_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No ML analysis found for this incident",
        )

    return result