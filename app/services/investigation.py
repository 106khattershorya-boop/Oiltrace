from app.schemas.investigation import InvestigationReport
from app.schemas.spill import SpillIncident
from app.services import priority as priority_service


def build_investigation(
    incident: SpillIncident,
) -> InvestigationReport:

    ranked_vessels = priority_service.rank_vessels(
        incident.incident_id
    )

    return InvestigationReport(
        incident=incident,
        candidate_count=len(ranked_vessels),
        ranked_vessels=ranked_vessels,
    )
