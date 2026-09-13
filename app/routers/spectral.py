from fastapi import APIRouter, HTTPException

from app.schemas.spectral import SpectralResult, SpectralResultCreate
from app.storage import memory_store, spectral_store


router = APIRouter(
    prefix="/incidents",
    tags=["Spectral & Cargo"],
)


@router.post(
    "/{incident_id}/spectral-result",
    response_model=SpectralResult,
    status_code=201,
)
def submit_spectral_result(
    incident_id: str,
    data: SpectralResultCreate,
):
    incident = memory_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return spectral_store.set_spectral_result(
        incident_id,
        data,
    )


@router.get(
    "/{incident_id}/spectral-result",
    response_model=SpectralResult,
)
def get_spectral_result(incident_id: str):
    result = spectral_store.get_spectral_result(incident_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No spectral result submitted for this incident",
        )

    return result