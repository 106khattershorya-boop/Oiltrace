from pydantic import BaseModel


class BehaviourAnalysis(BaseModel):
    """Behaviour analysis result stored in PostgreSQL."""

    mmsi: str
    vessel_name: str

    speed_anomaly: bool | None = None
    stop_anomaly: bool | None = None
    course_deviation: bool | None = None
    ais_gap: bool | None = None
    loitering: bool | None = None

    behaviour_score: float
