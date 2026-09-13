from typing import Dict, Optional

from app.database import get_connection
from app.schemas.cargo import CargoScore, CargoScoreCreate


def _row_to_cargo_score(row) -> CargoScore:
    return CargoScore(
        incident_id=int(row[0]),
        mmsi=str(row[1]),
        vessel_cargo_category=row[2] or "",
        cargo_score=float(row[3]) if row[3] is not None else 0.0,
    )


def set_cargo_score(
    incident_id: int,
    data: CargoScoreCreate,
) -> CargoScore:

    with get_connection() as conn:

        vessel = conn.execute(
            """
            SELECT vessel_id, mmsi, cargo_category
            FROM vessels
            WHERE mmsi = %s
            LIMIT 1
            """,
            (data.mmsi,),
        ).fetchone()

        if vessel is None:
            raise ValueError(
                f"Vessel with MMSI {data.mmsi} was not found"
            )

        vessel_id = vessel[0]
        mmsi = vessel[1]

        conn.execute(
            """
            INSERT INTO investigation_scores (
                incident_id,
                vessel_id,
                cargo_score
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (incident_id, vessel_id)
            DO UPDATE SET
                cargo_score = EXCLUDED.cargo_score
            """,
            (
                incident_id,
                vessel_id,
                data.cargo_score,
            ),
        )

        row = conn.execute(
            """
            SELECT
                i.incident_id,
                v.mmsi,
                v.cargo_category,
                i.cargo_score
            FROM investigation_scores i
            JOIN vessels v
                ON v.vessel_id = i.vessel_id
            WHERE i.incident_id = %s
              AND i.vessel_id = %s
            LIMIT 1
            """,
            (
                incident_id,
                vessel_id,
            ),
        ).fetchone()

        return _row_to_cargo_score(row)


def get_cargo_score(
    incident_id: int,
    mmsi: str,
) -> Optional[CargoScore]:

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                i.incident_id,
                v.mmsi,
                v.cargo_category,
                i.cargo_score
            FROM investigation_scores i
            JOIN vessels v
                ON v.vessel_id = i.vessel_id
            WHERE i.incident_id = %s
              AND v.mmsi = %s
            LIMIT 1
            """,
            (
                incident_id,
                mmsi,
            ),
        ).fetchone()

        if row is None:
            return None

        if row[3] is None:
            return None

        return _row_to_cargo_score(row)


def get_all_scores_for_incident(
    incident_id: int,
) -> Dict[str, float]:

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                v.mmsi,
                i.cargo_score
            FROM investigation_scores i
            JOIN vessels v
                ON v.vessel_id = i.vessel_id
            WHERE i.incident_id = %s
              AND i.cargo_score IS NOT NULL
            ORDER BY i.cargo_score DESC
            """,
            (incident_id,),
        ).fetchall()

        return {
            str(mmsi): float(cargo_score)
            for mmsi, cargo_score in rows
        }