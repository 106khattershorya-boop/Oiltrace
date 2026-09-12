import math
from typing import List

from app.schemas.correlation import VesselCorrelation
from app.schemas.spill import SpillIncident
from app.schemas.vessel import AISReport
from app.storage import vessel_store


MAX_DISTANCE_KM = 50.0
MAX_TIME_WINDOW_MINUTES = 180.0


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def _score_report(incident: SpillIncident, report: AISReport) -> VesselCorrelation:
    distance_km = _haversine_km(
        incident.latitude,
        incident.longitude,
        report.latitude,
        report.longitude,
    )

    time_diff_minutes = abs(
        (incident.detection_time - report.timestamp).total_seconds() / 60.0
    )

    spatial_score = max(
        0.0,
        1 - (distance_km / MAX_DISTANCE_KM)
    )

    temporal_score = max(
        0.0,
        1 - (time_diff_minutes / MAX_TIME_WINDOW_MINUTES)
    )

    combined_score = round(
        (spatial_score + temporal_score) / 2,
        3
    )

    return VesselCorrelation(
        mmsi=report.mmsi,
        vessel_name=report.vessel_name,
        distance_km=round(distance_km, 2),
        time_diff_minutes=round(time_diff_minutes, 1),
        spatial_temporal_score=combined_score,
    )

def find_candidate_vessels(incident: SpillIncident) -> List[VesselCorrelation]:
    all_reports = vessel_store.list_reports()

    best_by_mmsi = {}

    for report in all_reports:
        distance_km = _haversine_km(
            incident.latitude,
            incident.longitude,
            report.latitude,
            report.longitude,
        )

        time_diff_minutes = abs(
            (incident.detection_time - report.timestamp).total_seconds() / 60.0
        )

        if (
            distance_km <= MAX_DISTANCE_KM
            and time_diff_minutes <= MAX_TIME_WINDOW_MINUTES
        ):
            candidate = _score_report(incident, report)

            # Keep only the best AIS position for each vessel
            existing = best_by_mmsi.get(report.mmsi)

            if (
                existing is None
                or candidate.spatial_temporal_score
                > existing.spatial_temporal_score
            ):
                best_by_mmsi[report.mmsi] = candidate

    candidates = list(best_by_mmsi.values())

    candidates.sort(
        key=lambda c: c.spatial_temporal_score,
        reverse=True,
    )

    return candidates