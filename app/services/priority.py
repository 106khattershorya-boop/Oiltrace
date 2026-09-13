from typing import List

from app.database import get_connection
from app.schemas.priority import VesselPriority, PriorityLevel


def _priority_level(value: str | None) -> PriorityLevel:
    if value == "HIGH":
        return PriorityLevel.high

    if value == "MEDIUM-HIGH":
        return PriorityLevel.medium_high

    if value == "LOW":
        return PriorityLevel.low

    return PriorityLevel.medium


def _build_reasons(
    spatial_score: float | None,
    temporal_score: float | None,
    trajectory_score: float | None,
    behaviour_score: float | None,
    spectral_score: float | None,
    cargo_score: float | None,
) -> List[str]:

    reasons: List[str] = []

    if spatial_score is not None and spatial_score >= 80:
        reasons.append("Strong spatial match")

    if temporal_score is not None and temporal_score >= 80:
        reasons.append("Strong temporal match")

    if trajectory_score is not None and trajectory_score >= 70:
        reasons.append("Strong trajectory match")

    if behaviour_score is not None and behaviour_score >= 30:
        reasons.append("Significant behaviour anomaly score")

    if spectral_score is not None and spectral_score >= 60:
        reasons.append("Strong spectral compatibility")

    if cargo_score is not None and cargo_score >= 60:
        reasons.append("Cargo category compatibility")

    if not reasons:
        reasons.append(
            "Limited or inconclusive supporting evidence"
        )

    return reasons


def rank_vessels(
    incident_id: int,
) -> List[VesselPriority]:

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT
                v.mmsi,
                v.vessel_name,

                m.spatial_score,
                m.temporal_score,
                m.trajectory_score,

                b.behaviour_score,

                i.spectral_score,
                i.cargo_score,

                i.final_priority_score,
                i.priority_level,

                nearest.distance_km,
                nearest.time_diff_minutes

            FROM investigation_scores i

            JOIN vessels v
                ON v.vessel_id = i.vessel_id

            LEFT JOIN spill_vessel_matches m
                ON m.incident_id = i.incident_id
               AND m.vessel_id = i.vessel_id

            LEFT JOIN behaviour_analysis b
                ON b.incident_id = i.incident_id
               AND b.vessel_id = i.vessel_id

            LEFT JOIN LATERAL (
                SELECT
                    ST_Distance(
                        si.location,
                        ST_SetSRID(
                            ST_MakePoint(
                                ap.longitude,
                                ap.latitude
                            ),
                            4326
                        )::geography
                    ) / 1000.0 AS distance_km,

                    ABS(
                        EXTRACT(
                            EPOCH FROM (
                                si.detection_time - ap.timestamp
                            )
                        ) / 60.0
                    ) AS time_diff_minutes

                FROM ais_positions ap
                JOIN spill_incidents si
                    ON si.incident_id = i.incident_id

                WHERE ap.vessel_id = i.vessel_id
                  AND ap.latitude IS NOT NULL
                  AND ap.longitude IS NOT NULL

                ORDER BY
                    ST_Distance(
                        si.location,
                        ST_SetSRID(
                            ST_MakePoint(
                                ap.longitude,
                                ap.latitude
                            ),
                            4326
                        )::geography
                    )

                LIMIT 1
            ) nearest ON TRUE

            WHERE i.incident_id = %s

            ORDER BY
                i.final_priority_score DESC
            """,
            (incident_id,),
        ).fetchall()

    results: List[VesselPriority] = []

    for row in rows:

        (
            mmsi,
            vessel_name,
            spatial_score,
            temporal_score,
            trajectory_score,
            behaviour_score,
            spectral_score,
            cargo_score,
            final_priority_score,
            priority_level,
            distance_km,
            time_diff_minutes,
        ) = row

        spatial = (
            float(spatial_score)
            if spatial_score is not None
            else None
        )

        temporal = (
            float(temporal_score)
            if temporal_score is not None
            else None
        )

        trajectory = (
            float(trajectory_score)
            if trajectory_score is not None
            else None
        )

        behaviour = (
            float(behaviour_score)
            if behaviour_score is not None
            else 0.0
        )

        spectral = (
            float(spectral_score)
            if spectral_score is not None
            else None
        )

        cargo = (
            float(cargo_score)
            if cargo_score is not None
            else None
        )

        available = [
            score
            for score in (
                spatial,
                temporal,
                trajectory,
            )
            if score is not None
        ]

        if available:
            combined_score = (
                sum(available)
                / len(available)
                / 100.0
            )
        else:
            combined_score = 0.0

        reasons = _build_reasons(
            spatial,
            temporal,
            trajectory,
            behaviour,
            spectral,
            cargo,
        )

        results.append(
            VesselPriority(
                mmsi=str(mmsi),
                vessel_name=vessel_name or "",

                # IMPORTANT:
                # Preserve the ML final score exactly.
                final_priority_score=float(
                    final_priority_score
                ),

                priority_level=_priority_level(
                    priority_level
                ),

                reasons=reasons,

                # API combined_score stays normalized.
                combined_score=round(
                    combined_score,
                    3,
                ),

                # Preserve ML behaviour score.
                behaviour_score=behaviour,

                spectral_score=spectral,
                cargo_score=cargo,
                distance_km=(
                    round(float(distance_km), 3)
                    if distance_km is not None
                    else None
                ),
                time_difference_minutes=(
                    round(float(time_diff_minutes), 3)
                    if time_diff_minutes is not None
                    else None
                ),
                spatial_score=spatial,
                temporal_score=temporal,
                trajectory_score=trajectory,
            )
        )

    return results
