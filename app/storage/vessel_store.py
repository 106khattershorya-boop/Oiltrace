import uuid
from typing import Dict, List

from app.schemas.vessel import AISReport, AISReportCreate

_ais_reports: Dict[str, AISReport] = {}


def add_report(data: AISReportCreate) -> AISReport:
    report_id = uuid.uuid4().hex[:10]
    report = AISReport(report_id=report_id, **data.model_dump())
    _ais_reports[report_id] = report
    return report


def list_reports() -> List[AISReport]:
    return list(_ais_reports.values())


def list_reports_by_mmsi(mmsi: str) -> List[AISReport]:
    return [r for r in _ais_reports.values() if r.mmsi == mmsi]