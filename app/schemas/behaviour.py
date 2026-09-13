from pydantic import BaseModel


class BehaviourAnalysis(BaseModel):
    """Behaviour anomaly analysis result for one vessel, for one incident."""

    mmsi: str
    vessel_name: str
    speed_anomaly: bool
    stop_anomaly: bool
    course_deviation: bool
    ais_gap: bool
    loitering: bool
    behaviour_score: float