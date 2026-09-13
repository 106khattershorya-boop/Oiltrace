from typing import List, Optional, Any

from psycopg.types.json import Jsonb

from app.database import get_connection
from app.schemas.spectral import SpectralResult, SpectralResultCreate


def _row_to_spectral_result(row) -> SpectralResult:
    return SpectralResult(
        incident_id=int(row[0]),
        spectral_features=row[1],
        probable_oil_category=row[2],
        spectral_score=float(row[3]) if row[3] is not None else 0.0,
    )


def set_spectral_result(
    incident_id: int,
    data: SpectralResultCreate,
) -> SpectralResult:

    spectral_features: Any = data.spectral_features

    if isinstance(spectral_features, str):
        import json

        try:
            spectral_features = json.loads(spectral_features)
        except json.JSONDecodeError:
            spectral_features = {
                "raw_features": spectral_features
            }

    with get_connection() as conn:
        row = conn.execute(
            """
            INSERT INTO spectral_analysis (
                incident_id,
                spectral_features,
                probable_oil_category,
                spectral_score
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (incident_id)
            DO UPDATE SET
                spectral_features = EXCLUDED.spectral_features,
                probable_oil_category = EXCLUDED.probable_oil_category,
                spectral_score = EXCLUDED.spectral_score
            RETURNING
                incident_id,
                spectral_features,
                probable_oil_category,
                spectral_score
            """,
            (
                incident_id,
                Jsonb(spectral_features),
                data.probable_oil_category,
                data.spectral_score,
            ),
        ).fetchone()

        return _row_to_spectral_result(row)


def get_spectral_result(
    incident_id: int,
) -> Optional[SpectralResult]:

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                incident_id,
                spectral_features,
                probable_oil_category,
                spectral_score
            FROM spectral_analysis
            WHERE incident_id = %s
            LIMIT 1
            """,
            (incident_id,),
        ).fetchone()

        if row is None:
            return None

        return _row_to_spectral_result(row)


def list_spectral_results() -> List[SpectralResult]:

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                incident_id,
                spectral_features,
                probable_oil_category,
                spectral_score
            FROM spectral_analysis
            ORDER BY incident_id
            """
        ).fetchall()

        return [_row_to_spectral_result(row) for row in rows]