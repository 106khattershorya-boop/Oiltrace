from typing import List, Optional

from app.database import get_connection
from app.schemas.spill import SpillIncident, SpillIncidentCreate


def _row_to_incident(row) -> SpillIncident:
    return SpillIncident(
        incident_id=row[0],
        latitude=float(row[1]),
        longitude=float(row[2]),
        detection_time=row[3],
        estimated_area_km2=(
            float(row[4]) if row[4] is not None else None
        ),
        detection_confidence=(
            float(row[5]) if row[5] is not None else None
        ),
        satellite_source=row[6],
    )


def create_incident(data: SpillIncidentCreate) -> SpillIncident:
    with get_connection() as conn:
        row = conn.execute(
            """
            INSERT INTO spill_incidents (
                latitude,
                longitude,
                detection_time,
                estimated_area,
                detection_confidence,
                satellite_source,
                location
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                ST_SetSRID(
                    ST_MakePoint(%s, %s),
                    4326
                )::geography
            )
            RETURNING
                incident_id,
                latitude,
                longitude,
                detection_time,
                estimated_area,
                detection_confidence,
                satellite_source
            """,
            (
                data.latitude,
                data.longitude,
                data.detection_time,
                data.estimated_area_km2,
                data.detection_confidence,
                data.satellite_source,
                data.longitude,
                data.latitude,
            ),
        ).fetchone()

        return _row_to_incident(row)


def list_incidents() -> List[SpillIncident]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                incident_id,
                latitude,
                longitude,
                detection_time,
                estimated_area,
                detection_confidence,
                satellite_source
            FROM spill_incidents
            ORDER BY detection_time DESC
            """
        ).fetchall()

        return [_row_to_incident(row) for row in rows]


def get_incident(incident_id: int) -> Optional[SpillIncident]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                incident_id,
                latitude,
                longitude,
                detection_time,
                estimated_area,
                detection_confidence,
                satellite_source
            FROM spill_incidents
            WHERE incident_id = %s
            """,
            (incident_id,),
        ).fetchone()

        if row is None:
            return None

        return _row_to_incident(row)