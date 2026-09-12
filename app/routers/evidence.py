from fastapi import APIRouter, HTTPException

from app.schemas.evidence import VesselEvidence
from app.services import evidence as evidence_service
from app.storage import memory_store


router = APIRouter(
    prefix="/incidents",
    tags=["Evidence Fusion"],
)


@router.get(
    "/{incident_id}/evidence",
    response_model=list[VesselEvidence],
)
def get_fused_evidence(incident_id: str):

    incident = memory_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return evidence_service.fuse_evidence(incident)