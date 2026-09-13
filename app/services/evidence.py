from typing import List

from app.schemas.evidence import VesselEvidence
from app.schemas.spill import SpillIncident
from app.services import correlation as correlation_service
from app.services import behaviour as behaviour_service
from app.storage import spectral_store, cargo_store


def fuse_evidence(
    incident: SpillIncident,
) -> List[VesselEvidence]:

    candidates = correlation_service.find_candidate_vessels(
        incident
    )

    spectral_result = spectral_store.get_spectral_result(
        incident.incident_id
    )

    cargo_scores = cargo_store.get_all_scores_for_incident(
        incident.incident_id
    )

    evidence_list: List[VesselEvidence] = []

    for candidate in candidates:

        behaviour = behaviour_service.analyze_behaviour(
            candidate.mmsi,
            candidate.vessel_name,
            incident.incident_id,
        )

        evidence_list.append(
            VesselEvidence(
                mmsi=candidate.mmsi,
                vessel_name=candidate.vessel_name,

                combined_score=candidate.combined_score,
                distance_km=candidate.distance_km,
                time_diff_minutes=candidate.time_diff_minutes,

                behaviour_score=behaviour.behaviour_score,

                speed_anomaly=behaviour.speed_anomaly,
                stop_anomaly=behaviour.stop_anomaly,
                course_deviation=behaviour.course_deviation,
                ais_gap=behaviour.ais_gap,
                loitering=behaviour.loitering,

                spectral_score=(
                    spectral_result.spectral_score
                    if spectral_result
                    else None
                ),

                probable_oil_category=(
                    spectral_result.probable_oil_category
                    if spectral_result
                    else None
                ),

                cargo_score=cargo_scores.get(
                    candidate.mmsi
                ),
            )
        )

    return evidence_list
