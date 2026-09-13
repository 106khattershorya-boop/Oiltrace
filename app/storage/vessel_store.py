from typing import List

from app.database import get_connection
from app.schemas.vessel import AISReport, AISReportCreate


def _row_to_report(row) -> AISReport:
    return AISReport(
        report_id=str(row[0]),
        mmsi=row[1],
        vessel_name=row[2],
        vessel_type=row[3],
        latitude=float(row[4]) if row[4] is not None else None,
        longitude=float(row[5]) if row[5] is not None else None,
        speed_knots=float(row[6]) if row[6] is not None else None,
        course_degrees=float(row[7]) if row[7] is not None else None,
        timestamp=row[8],
    )


def add_report(data: AISReportCreate) -> AISReport:
    with get_connection() as conn:

        vessel = conn.execute(
            """
            SELECT vessel_id
            FROM vessels
            WHERE mmsi = %s
            LIMIT 1
            """,
            (data.mmsi,),
        ).fetchone()

        if vessel is None:
            vessel = conn.execute(
                """
                INSERT INTO vessels (
                    mmsi,
                    vessel_name,
                    vessel_type
                )
                VALUES (%s, %s, %s)
                RETURNING vessel_id
                """,
                (
                    data.mmsi,
                    data.vessel_name,
                    data.vessel_type,
                ),
            ).fetchone()

        else:
            conn.execute(
                """
                UPDATE vessels
                SET vessel_name = %s,
                    vessel_type = %s
                WHERE vessel_id = %s
                """,
                (
                    data.vessel_name,
                    data.vessel_type,
                    vessel[0],
                ),
            )

        vessel_id = vessel[0]

        row = conn.execute(
            """
            INSERT INTO ais_positions (
                vessel_id,
                latitude,
                longitude,
                speed,
                course,
                timestamp
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                vessel_id,
                data.latitude,
                data.longitude,
                data.speed_knots,
                data.course_degrees,
                data.timestamp,
            ),
        ).fetchone()

        return AISReport(
            report_id=str(row[0]),
            mmsi=data.mmsi,
            vessel_name=data.vessel_name,
            vessel_type=data.vessel_type,
            latitude=data.latitude,
            longitude=data.longitude,
            speed_knots=data.speed_knots,
            course_degrees=data.course_degrees,
            timestamp=data.timestamp,
        )


def list_reports() -> List[AISReport]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                ap.id,
                v.mmsi,
                v.vessel_name,
                v.vessel_type,
                ap.latitude,
                ap.longitude,
                ap.speed,
                ap.course,
                ap.timestamp
            FROM ais_positions ap
            JOIN vessels v
                ON v.vessel_id = ap.vessel_id
            ORDER BY ap.timestamp DESC
            """
        ).fetchall()

        return [_row_to_report(row) for row in rows]


def list_reports_by_mmsi(mmsi: str) -> List[AISReport]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                ap.id,
                v.mmsi,
                v.vessel_name,
                v.vessel_type,
                ap.latitude,
                ap.longitude,
                ap.speed,
                ap.course,
                ap.timestamp
            FROM ais_positions ap
            JOIN vessels v
                ON v.vessel_id = ap.vessel_id
            WHERE v.mmsi = %s
            ORDER BY ap.timestamp DESC
            """,
            (mmsi,),
        ).fetchall()

        return [_row_to_report(row) for row in rows]