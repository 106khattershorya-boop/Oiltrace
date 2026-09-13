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

def _trajectory_score(incident: SpillIncident, reports: list[AISReport]) -> float:
    """
    Estimate how relevant the vessel's movement direction is to the spill.

    Uses the latest AIS position and course to check whether the vessel
    is moving generally toward the spill location.
    """

    if not reports:
        return 0.0

    latest_report = max(reports, key=lambda r: r.timestamp)

    # Calculate bearing from vessel to spill
    lat1 = math.radians(latest_report.latitude)
    lon1 = math.radians(latest_report.longitude)
    lat2 = math.radians(incident.latitude)
    lon2 = math.radians(incident.longitude)

    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    )

    bearing = math.degrees(math.atan2(x, y))
    bearing = (bearing + 360) % 360

    # Smallest difference between vessel course and direction to spill
    difference = abs(latest_report.course_degrees - bearing)
    difference = min(difference, 360 - difference)

    # 0° difference = perfect heading toward spill
    if difference <= 30:
        return 1.0
    elif difference <= 60:
        return 0.75
    elif difference <= 90:
        return 0.5
    elif difference <= 120:
        return 0.25
    else:
        return 0.0

    
def _score_report(
    incident: SpillIncident,
    report: AISReport,
    reports: list[AISReport],
) -> VesselCorrelation:
    distance_km = _haversine_km(
        incident.latitude,
        incident.longitude,
        report.latitude,
        report.longitude,
    )

    time_diff_minutes = abs(
        (incident.detection_time - report.timestamp).total_seconds() / 60.0
    )

    spatial_score = max(0.0, 1.0 - distance_km / MAX_DISTANCE_KM)

    temporal_score = max(
    0.0,
    1.0 - time_diff_minutes / MAX_TIME_WINDOW_MINUTES,
    )

    # Temporary MVP trajectory score.
    # Will be replaced by actual trajectory analysis later.
    trajectory_score = _trajectory_score(incident, reports)

    combined_score = (
    0.4 * spatial_score
    + 0.3 * temporal_score
    + 0.3 * trajectory_score
    )


    return VesselCorrelation(
        mmsi=report.mmsi,
        vessel_name=report.vessel_name,
        distance_km=round(distance_km, 3),
        time_diff_minutes=round(time_diff_minutes, 3),
        spatial_score=round(spatial_score, 3),
        temporal_score=round(temporal_score, 3),
        trajectory_score=round(trajectory_score, 3),
        combined_score=round(combined_score, 3),
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
            vessel_reports = [
             r for r in all_reports
            if r.mmsi == report.mmsi
        ]

        candidate = _score_report(
            incident,
            report,
            vessel_reports,
        )

        # Keep only the best AIS position for each vessel
        existing = best_by_mmsi.get(report.mmsi)

        if (
                existing is None
                or candidate.combined_score
                > existing.combined_score
            ):
                best_by_mmsi[report.mmsi] = candidate

    candidates = list(best_by_mmsi.values())

    candidates.sort(
        key=lambda c: c.combined_score,
        reverse=True,
    )

    return candidates