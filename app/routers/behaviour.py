from fastapi import APIRouter, HTTPException

from app.schemas.behaviour import BehaviourAnalysis
from app.services import behaviour as behaviour_service
from app.storage import vessel_store


router = APIRouter(
    prefix="/vessels",
    tags=["Behaviour Analysis"],
)


@router.get(
    "/{mmsi}/behaviour",
    response_model=BehaviourAnalysis,
)
def get_vessel_behaviour(mmsi: str):
    reports = vessel_store.list_reports_by_mmsi(mmsi)

    if not reports:
        raise HTTPException(
            status_code=404,
            detail="No AIS reports found for this vessel",
        )

    vessel_name = reports[0].vessel_name

    return behaviour_service.analyze_behaviour(
        mmsi,
        vessel_name,
    )