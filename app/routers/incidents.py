from fastapi import APIRouter, HTTPException

from app.schemas.spill import SpillIncident, SpillIncidentCreate
from app.storage import memory_store

router = APIRouter(prefix="/incidents", tags=["Spill Incidents"])


@router.post("", response_model=SpillIncident, status_code=201)
def create_incident(data: SpillIncidentCreate):
    return memory_store.create_incident(data)


@router.get("", response_model=list[SpillIncident])
def list_incidents():
    return memory_store.list_incidents()


@router.get("/{incident_id}", response_model=SpillIncident)
def get_incident(incident_id: str):
    incident = memory_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident