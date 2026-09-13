from fastapi import APIRouter, HTTPException

from app.schemas.investigation import InvestigationReport
from app.services import investigation as investigation_service
from app.storage import memory_store


router = APIRouter(
    prefix="/incidents",
    tags=["Investigation"],
)


@router.get(
    "/{incident_id}/investigation",
    response_model=InvestigationReport,
)
def get_investigation(
    incident_id: int,
):

    incident = memory_store.get_incident(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return investigation_service.build_investigation(
        incident
    )
