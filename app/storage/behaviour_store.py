from typing import Optional

from app.database import get_connection
from app.schemas.behaviour import BehaviourAnalysis


def _row_to_behaviour(row) -> BehaviourAnalysis:
    return BehaviourAnalysis(
        mmsi=str(row[0]),
        vessel_name=row[1] or "",
        speed_anomaly=row[2],
        stop_anomaly=row[3],
        course_deviation=row[4],
        ais_gap=row[5],
        loitering=row[6],
        behaviour_score=float(row[7]) if row[7] is not None else 0.0,
    )


def get_behaviour(
    incident_id: int,
    mmsi: str,
) -> Optional[BehaviourAnalysis]:

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                v.mmsi,
                v.vessel_name,
                b.speed_anomaly,
                b.stop_anomaly,
                b.course_deviation,
                b.ais_gap,
                b.loitering,
                b.behaviour_score
            FROM behaviour_analysis b
            JOIN vessels v
                ON v.vessel_id = b.vessel_id
            WHERE b.incident_id = %s
              AND v.mmsi = %s
            LIMIT 1
            """,
            (incident_id, mmsi),
        ).fetchone()

        if row is None:
            return None

        return _row_to_behaviour(row)


def get_latest_behaviour(
    mmsi: str,
) -> Optional[BehaviourAnalysis]:

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                v.mmsi,
                v.vessel_name,
                b.speed_anomaly,
                b.stop_anomaly,
                b.course_deviation,
                b.ais_gap,
                b.loitering,
                b.behaviour_score
            FROM behaviour_analysis b
            JOIN vessels v
                ON v.vessel_id = b.vessel_id
            WHERE v.mmsi = %s
            ORDER BY b.incident_id DESC, b.id DESC
            LIMIT 1
            """,
            (mmsi,),
        ).fetchone()

        if row is None:
            return None

        return _row_to_behaviour(row)
