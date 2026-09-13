from fastapi import APIRouter

from app.schemas.vessel import AISReport, AISReportCreate
from app.storage import vessel_store

router = APIRouter(prefix="/ais", tags=["AIS Vessel Reports"])


@router.post("", response_model=AISReport, status_code=201)
def add_ais_report(data: AISReportCreate):
    return vessel_store.add_report(data)


@router.get("", response_model=list[AISReport])
def list_ais_reports():
    return vessel_store.list_reports()


@router.get("/{mmsi}", response_model=list[AISReport])
def get_reports_for_vessel(mmsi: str):
    return vessel_store.list_reports_by_mmsi(mmsi)