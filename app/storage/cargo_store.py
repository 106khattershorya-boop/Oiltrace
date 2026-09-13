from typing import Dict, Optional

from app.schemas.cargo import CargoScore, CargoScoreCreate

_cargo_scores: Dict[str, CargoScore] = {}


def _key(incident_id: str, mmsi: str) -> str:
    return f"{incident_id}:{mmsi}"


def set_cargo_score(incident_id: str, data: CargoScoreCreate) -> CargoScore:
    score = CargoScore(incident_id=incident_id, **data.model_dump())
    _cargo_scores[_key(incident_id, data.mmsi)] = score
    return score


def get_cargo_score(incident_id: str, mmsi: str) -> Optional[CargoScore]:
    return _cargo_scores.get(_key(incident_id, mmsi))


def get_all_scores_for_incident(incident_id: str) -> Dict[str, float]:
    """Returns {mmsi: cargo_score} for use in evidence fusion."""
    return {
        s.mmsi: s.cargo_score
        for s in _cargo_scores.values()
        if s.incident_id == incident_id
    }