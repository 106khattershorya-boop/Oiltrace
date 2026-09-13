from typing import List

from app.database import get_connection
from app.schemas.correlation import VesselCorrelation
from app.schemas.spill import SpillIncident


def find_candidate_vessels(
    incident: SpillIncident,
) -> List[VesselCorrelation]:

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                m.vessel_id,
                v.mmsi,
                v.vessel_name,
                m.spatial_score,
                m.temporal_score,
                m.trajectory_score,

                nearest.distance_km,
                nearest.time_diff_minutes

            FROM spill_vessel_matches m

            JOIN vessels v
                ON v.vessel_id = m.vessel_id

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
                    ON si.incident_id = %s

                WHERE ap.vessel_id = m.vessel_id
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

            WHERE m.incident_id = %s

            ORDER BY
                m.spatial_score DESC,
                m.temporal_score DESC

            LIMIT 100
            """,
            (
                incident.incident_id,
                incident.incident_id,
            ),
        ).fetchall()

    candidates: List[VesselCorrelation] = []

    for row in rows:
        (
            vessel_id,
            mmsi,
            vessel_name,
            spatial_score,
            temporal_score,
            trajectory_score,
            distance_km,
            time_diff_minutes,
        ) = row

        spatial = (
            float(spatial_score)
            if spatial_score is not None
            else 0.0
        )

        temporal = (
            float(temporal_score)
            if temporal_score is not None
            else 0.0
        )

        trajectory = (
            float(trajectory_score)
            if trajectory_score is not None
            else None
        )

        available_scores = [spatial, temporal]

        if trajectory is not None:
            available_scores.append(trajectory)

        # DB scores are percentage-point values (0-100).
        # API combined_score remains normalized to 0-1.
        combined_score = (
            sum(available_scores)
            / len(available_scores)
            / 100.0
        )

        candidates.append(
            VesselCorrelation(
                mmsi=str(mmsi),
                vessel_name=vessel_name or "",
                distance_km=(
                    round(float(distance_km), 3)
                    if distance_km is not None
                    else 0.0
                ),
                time_diff_minutes=(
                    round(float(time_diff_minutes), 3)
                    if time_diff_minutes is not None
                    else 0.0
                ),
                spatial_score=spatial,
                temporal_score=temporal,
                trajectory_score=trajectory,
                combined_score=round(
                    combined_score,
                    3,
                ),
            )
        )

    return candidates
