from typing import Optional

from app.schemas.behaviour import BehaviourAnalysis
from app.storage import behaviour_store


def analyze_behaviour(
    mmsi: str,
    vessel_name: str,
    incident_id: Optional[int] = None,
) -> BehaviourAnalysis:

    if incident_id is not None:
        result = behaviour_store.get_behaviour(
            incident_id,
            mmsi,
        )
    else:
        result = behaviour_store.get_latest_behaviour(
            mmsi,
        )

    if result is None:
        return BehaviourAnalysis(
            mmsi=mmsi,
            vessel_name=vessel_name,
            speed_anomaly=None,
            stop_anomaly=None,
            course_deviation=None,
            ais_gap=None,
            loitering=None,
            behaviour_score=0.0,
        )

    return result
