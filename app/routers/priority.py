from fastapi import APIRouter, HTTPException

from app.schemas.priority import VesselPriority
from app.services import priority as priority_service
from app.storage import memory_store


router = APIRouter(
    prefix="/incidents",
    tags=["Investigation Priority"],
)


@router.get(
    "/{incident_id}/priority",
    response_model=list[VesselPriority],
)
def get_investigation_priority(incident_id: int):

    incident = memory_store.get_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return priority_service.rank_vessels(
        incident.incident_id
    )
