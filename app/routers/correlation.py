from fastapi import APIRouter, HTTPException

from app.schemas.correlation import VesselCorrelation
from app.services import correlation as correlation_service
from app.storage import memory_store


router = APIRouter(prefix="/incidents", tags=["Correlation"])


@router.get(
    "/{incident_id}/candidates",
    response_model=list[VesselCorrelation],
)
def get_candidate_vessels(incident_id: str):
    incident = memory_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return correlation_service.find_candidate_vessels(incident)