from typing import List

from app.schemas.evidence import VesselEvidence
from app.schemas.priority import VesselPriority, PriorityLevel


BASE_WEIGHTS = {
    "spatial_temporal": 0.50,
    "behaviour": 0.20,
    "spectral": 0.15,
    "cargo": 0.15,
}

SPATIAL_ANOMALY_THRESHOLD = 0.6
SPECTRAL_MATCH_THRESHOLD = 0.6
CARGO_MATCH_THRESHOLD = 0.6


def _priority_level(score: float) -> PriorityLevel:
    if score >= 0.75:
        return PriorityLevel.high
    elif score >= 0.55:
        return PriorityLevel.medium_high
    elif score >= 0.35:
        return PriorityLevel.medium
    return PriorityLevel.low


def _build_reasons(evidence: VesselEvidence) -> List[str]:
    reasons = []

    if evidence.combined_score >= SPATIAL_ANOMALY_THRESHOLD:
        reasons.append("Strong spatial and temporal match")

    if evidence.speed_anomaly:
        reasons.append("Sudden speed reduction detected")

    if evidence.stop_anomaly:
        reasons.append("Unexpected stop detected")

    if evidence.course_deviation:
        reasons.append("Course deviation detected")

    if evidence.ais_gap:
        reasons.append("AIS transmission gap detected")

    if evidence.loitering:
        reasons.append("Loitering behaviour detected")

    if (
        evidence.spectral_score is not None
        and evidence.spectral_score >= SPECTRAL_MATCH_THRESHOLD
    ):
        reasons.append(
            f"Spectral analysis compatible ({evidence.probable_oil_category})"
        )

    if (
        evidence.cargo_score is not None
        and evidence.cargo_score >= CARGO_MATCH_THRESHOLD
    ):
        reasons.append(
            "Cargo category compatible with detected oil type"
        )

    if not reasons:
        reasons.append("Weak or no significant evidence found")

    return reasons


def score_vessel(evidence: VesselEvidence) -> VesselPriority:

    available = {
        "spatial_temporal": evidence.combined_score,
        "behaviour": evidence.behaviour_score,
    }

    if evidence.spectral_score is not None:
        available["spectral"] = evidence.spectral_score

    if evidence.cargo_score is not None:
        available["cargo"] = evidence.cargo_score

    total_weight = sum(
        BASE_WEIGHTS[key]
        for key in available
    )

    final_score = sum(
        (BASE_WEIGHTS[key] / total_weight) * value
        for key, value in available.items()
    )

    final_score = round(final_score, 3)

    return VesselPriority(
        mmsi=evidence.mmsi,
        vessel_name=evidence.vessel_name,
        final_priority_score=final_score,
        priority_level=_priority_level(final_score),
        reasons=_build_reasons(evidence),
        combined_score=evidence.combined_score,
        behaviour_score=evidence.behaviour_score,
        spectral_score=evidence.spectral_score,
        cargo_score=evidence.cargo_score,
    )


def rank_vessels(
    evidence_list: List[VesselEvidence],
) -> List[VesselPriority]:

    scored = [
        score_vessel(evidence)
        for evidence in evidence_list
    ]

    scored.sort(
        key=lambda vessel: vessel.final_priority_score,
        reverse=True,
    )

    return scored