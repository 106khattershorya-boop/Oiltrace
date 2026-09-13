def speed_anomaly(current_speed, normal_speed):
    """
    Calculate speed anomaly.

    Returns a value between 0 and 1.
    """

    if normal_speed <= 0:
        return 0.0

    difference = abs(
        current_speed - normal_speed
    )

    score = (
        difference / normal_speed
    )

    return min(
        score,
        1.0
    )


# ============================================================
# COURSE DEVIATION
# ============================================================

def course_deviation(
    expected_course,
    actual_course
):
    """
    Calculate circular course deviation.

    Both courses should be in degrees.
    """

    difference = abs(
        expected_course -
        actual_course
    )

    if difference > 180:

        difference = (
            360 - difference
        )

    return difference / 180.0


# ============================================================
# BEHAVIOUR SCORE
# ============================================================

def behaviour_score(
    speed,
    stop,
    course,
    ais_gap,
    loitering
):
    """
    Calculate vessel behaviour anomaly score.

    All inputs should be between 0 and 1.

    This is an investigation-priority
    behaviour score, NOT a probability
    that a vessel caused a spill.
    """

    speed = max(
        0.0,
        min(1.0, speed)
    )

    stop = max(
        0.0,
        min(1.0, stop)
    )

    course = max(
        0.0,
        min(1.0, course)
    )

    ais_gap = max(
        0.0,
        min(1.0, ais_gap)
    )

    loitering = max(
        0.0,
        min(1.0, loitering)
    )

    score = (

        0.25 * speed

        + 0.20 * stop

        + 0.20 * course

        + 0.20 * ais_gap

        + 0.15 * loitering
    )

    return round(
        score * 100,
        2
    )


# ============================================================
# BEHAVIOUR LEVEL
# ============================================================

def classify_behaviour(score):

    if score >= 70:

        return "HIGH_ANOMALY"

    elif score >= 40:

        return "MEDIUM_ANOMALY"

    else:

        return "LOW_ANOMALY"


# ============================================================
# EXPLANATION
# ============================================================

def generate_reasons(
    speed,
    stop,
    course,
    ais_gap,
    loitering
):

    reasons = []

    if speed >= 0.5:

        reasons.append(
            "Significant speed anomaly"
        )

    if stop >= 0.5:

        reasons.append(
            "Unusual stopping behaviour"
        )

    if course >= 0.5:

        reasons.append(
            "Significant course deviation"
        )

    if ais_gap >= 0.5:

        reasons.append(
            "AIS transmission gap detected"
        )

    if loitering >= 0.5:

        reasons.append(
            "Possible loitering behaviour"
        )

    if not reasons:

        reasons.append(
            "No strong behavioural anomaly detected"
        )

    return reasons


# ============================================================
# COMPLETE VESSEL ANALYSIS
# ============================================================

def analyze_vessel_behaviour(
    speed,
    stop,
    course,
    ais_gap,
    loitering
):

    score = behaviour_score(
        speed,
        stop,
        course,
        ais_gap,
        loitering
    )

    level = classify_behaviour(
        score
    )

    reasons = generate_reasons(
        speed,
        stop,
        course,
        ais_gap,
        loitering
    )

    return {

        "behaviour_score":
            score,

        "behaviour_level":
            level,

        "reasons":
            reasons
    }