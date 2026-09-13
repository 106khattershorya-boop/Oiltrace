import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.schemas.spill import SpillIncident, SpillIncidentCreate

_incidents: Dict[str, SpillIncident] = {}


def create_incident(data: SpillIncidentCreate) -> SpillIncident:
    incident_id = f"OIL-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"

    incident = SpillIncident(
        incident_id=incident_id,
        created_at=datetime.now(timezone.utc),
        **data.model_dump(),
    )

    _incidents[incident_id] = incident
    return incident


def list_incidents() -> List[SpillIncident]:
    return list(_incidents.values())


def get_incident(incident_id: str) -> Optional[SpillIncident]:
    return _incidents.get(incident_id)