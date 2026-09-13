from fastapi import APIRouter, HTTPException

from app.schemas.behaviour import BehaviourAnalysis
from app.storage import behaviour_store


router = APIRouter(
    prefix="/vessels",
    tags=["Behaviour Analysis"],
)


@router.get(
    "/{mmsi}/behaviour",
    response_model=BehaviourAnalysis,
)
def get_vessel_behaviour(
    mmsi: str,
):

    result = behaviour_store.get_latest_behaviour(
        mmsi
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Behaviour analysis not found",
        )

    return result
