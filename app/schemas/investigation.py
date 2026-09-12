from pydantic import BaseModel

from app.schemas.spill import SpillIncident
from app.schemas.priority import VesselPriority


class InvestigationReport(BaseModel):
    """Single response object: incident + ranked candidate vessels."""

    incident: SpillIncident
    candidate_count: int
    ranked_vessels: list[VesselPriority]
    disclaimer: str = (
        "This output provides investigation-support information and does not "
        "constitute a final determination of liability."
    )