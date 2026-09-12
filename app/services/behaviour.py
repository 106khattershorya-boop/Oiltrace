from typing import List

from app.schemas.behaviour import BehaviourAnalysis
from app.schemas.vessel import AISReport
from app.storage import vessel_store


SPEED_DROP_KNOTS = 8.0
STOP_SPEED_KNOTS = 1.0
COURSE_DEVIATION_DEGREES = 45.0
AIS_GAP_MINUTES = 60.0


def _sorted_reports(mmsi: str) -> List[AISReport]:
    reports = vessel_store.list_reports_by_mmsi(mmsi)
    return sorted(reports, key=lambda r: r.timestamp)


def analyze_behaviour(
    mmsi: str,
    vessel_name: str,
) -> BehaviourAnalysis:

    reports = _sorted_reports(mmsi)

    speed_anomaly = False
    stop_anomaly = False
    course_deviation = False
    ais_gap = False
    loitering = False

    for i in range(1, len(reports)):
        prev, curr = reports[i - 1], reports[i]

        # Sudden speed reduction
        if (prev.speed_knots - curr.speed_knots) >= SPEED_DROP_KNOTS:
            speed_anomaly = True

        # Unexpected stop
        if curr.speed_knots <= STOP_SPEED_KNOTS:
            stop_anomaly = True

        # Course deviation
        diff = abs(curr.course_degrees - prev.course_degrees)
        diff = min(diff, 360 - diff)

        if diff >= COURSE_DEVIATION_DEGREES:
            course_deviation = True

        # AIS transmission gap
        gap_minutes = (
            curr.timestamp - prev.timestamp
        ).total_seconds() / 60.0

        if gap_minutes >= AIS_GAP_MINUTES:
            ais_gap = True

        # Loitering
        if (
            prev.speed_knots <= STOP_SPEED_KNOTS
            and curr.speed_knots <= STOP_SPEED_KNOTS
        ):
            loitering = True

    anomalies = [
        speed_anomaly,
        stop_anomaly,
        course_deviation,
        ais_gap,
        loitering,
    ]

    behaviour_score = round(
        sum(anomalies) / len(anomalies),
        3,
    )

    return BehaviourAnalysis(
        mmsi=mmsi,
        vessel_name=vessel_name,
        speed_anomaly=speed_anomaly,
        stop_anomaly=stop_anomaly,
        course_deviation=course_deviation,
        ais_gap=ais_gap,
        loitering=loitering,
        behaviour_score=behaviour_score,
    )