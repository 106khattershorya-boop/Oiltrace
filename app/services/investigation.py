from app.schemas.investigation import InvestigationReport
from app.schemas.spill import SpillIncident
from app.services import evidence as evidence_service
from app.services import priority as priority_service


def build_investigation(
    incident: SpillIncident,
) -> InvestigationReport:

    evidence_list = evidence_service.fuse_evidence(incident)

    ranked_vessels = priority_service.rank_vessels(
        evidence_list
    )

    return InvestigationReport(
        incident=incident,
        candidate_count=len(ranked_vessels),
        ranked_vessels=ranked_vessels,
    )