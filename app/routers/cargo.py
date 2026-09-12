from fastapi import APIRouter, HTTPException

from app.schemas.cargo import CargoScore, CargoScoreCreate
from app.storage import memory_store, cargo_store

router = APIRouter(prefix="/incidents", tags=["Cargo Compatibility"])


@router.post("/{incident_id}/cargo-score", response_model=CargoScore, status_code=201)
def submit_cargo_score(incident_id: str, data: CargoScoreCreate):
    incident = memory_store.get_incident(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return cargo_store.set_cargo_score(incident_id, data)


@router.get("/{incident_id}/cargo-score/{mmsi}", response_model=CargoScore)
def get_cargo_score(incident_id: str, mmsi: str):
    score = cargo_store.get_cargo_score(incident_id, mmsi)
    if score is None:
        raise HTTPException(status_code=404, detail="No cargo score submitted for this vessel/incident")
    return score