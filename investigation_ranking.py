# ============================================================
# INVESTIGATION PRIORITY RANKING
# ============================================================
#
# SIH 26143
#
# Purpose:
# Rank vessels for further investigation after an oil-spill
# detection.
#
# IMPORTANT:
# This score is an INVESTIGATION PRIORITY score.
# It is NOT:
#   - probability of guilt
#   - proof that a vessel caused the spill
#   - legal evidence
#
# Evidence used:
#   1. Spatial proximity
#   2. Temporal proximity
#   3. Behaviour anomaly
#   4. AIS data confidence
#
# ============================================================


# ============================================================
# CLAMP VALUE
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):

    return max(
        minimum,
        min(
            maximum,
            float(value)
        )
    )


# ============================================================
# SPATIAL SCORE
# ============================================================

def calculate_spatial_score(
    distance_km,
    max_distance_km=20.0
):
    """
    Convert vessel distance from spill into a 0-100 score.

    Very close vessels receive a much stronger score.

    Distance:
        0 km       -> 100
        1 km       -> very high
        5 km       -> moderate-high
        10 km      -> moderate
        20+ km     -> 0
    """

    distance_km = max(
        0.0,
        float(distance_km)
    )

    max_distance_km = max(
        0.001,
        float(max_distance_km)
    )

    # --------------------------------------------------------
    # Very close
    # --------------------------------------------------------

    if distance_km <= 0.10:

        return 100.0

    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------

    elif distance_km <= 1.0:

        # 0.10 km -> 100
        # 1.00 km -> 90
        score = (
            100.0
            -
            (
                (
                    distance_km
                    -
                    0.10
                )
                /
                0.90
            )
            *
            10.0
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # 1-5 km
    # --------------------------------------------------------

    elif distance_km <= 5.0:

        score = (
            90.0
            -
            (
                (
                    distance_km
                    -
                    1.0
                )
                /
                4.0
            )
            *
            35.0
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # 5-10 km
    # --------------------------------------------------------

    elif distance_km <= 10.0:

        score = (
            55.0
            -
            (
                (
                    distance_km
                    -
                    5.0
                )
                /
                5.0
            )
            *
            30.0
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # 10-20 km
    # --------------------------------------------------------

    elif distance_km <= max_distance_km:

        remaining_range = (
            max_distance_km
            -
            10.0
        )

        if remaining_range <= 0:

            return 0.0

        score = (
            25.0
            *
            (
                1.0
                -
                (
                    (
                        distance_km
                        -
                        10.0
                    )
                    /
                    remaining_range
                )
            )
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # Outside search radius
    # --------------------------------------------------------

    return 0.0


# ============================================================
# TEMPORAL SCORE
# ============================================================

def calculate_temporal_score(
    time_difference_minutes,
    max_time_minutes=180.0
):
    """
    Convert time difference from spill detection into a
    0-100 score.

    Very close timestamps receive much stronger scores.

    Time:
        0 min      -> 100
        1 min      -> very high
        5 min      -> high
        30 min     -> moderate
        180 min    -> 0
    """

    time_difference_minutes = abs(
        float(
            time_difference_minutes
        )
    )

    max_time_minutes = max(
        0.001,
        float(
            max_time_minutes
        )
    )

    # --------------------------------------------------------
    # Immediate temporal match
    # --------------------------------------------------------

    if time_difference_minutes <= 1.0:

        return 100.0

    # --------------------------------------------------------
    # 1-5 minutes
    # --------------------------------------------------------

    elif time_difference_minutes <= 5.0:

        score = (
            100.0
            -
            (
                (
                    time_difference_minutes
                    -
                    1.0
                )
                /
                4.0
            )
            *
            15.0
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # 5-30 minutes
    # --------------------------------------------------------

    elif time_difference_minutes <= 30.0:

        score = (
            85.0
            -
            (
                (
                    time_difference_minutes
                    -
                    5.0
                )
                /
                25.0
            )
            *
            45.0
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # 30-60 minutes
    # --------------------------------------------------------

    elif time_difference_minutes <= 60.0:

        score = (
            40.0
            -
            (
                (
                    time_difference_minutes
                    -
                    30.0
                )
                /
                30.0
            )
            *
            25.0
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # 60-180 minutes
    # --------------------------------------------------------

    elif time_difference_minutes <= max_time_minutes:

        remaining_range = (
            max_time_minutes
            -
            60.0
        )

        if remaining_range <= 0:

            return 0.0

        score = (
            15.0
            *
            (
                1.0
                -
                (
                    (
                        time_difference_minutes
                        -
                        60.0
                    )
                    /
                    remaining_range
                )
            )
        )

        return max(
            0.0,
            min(
                100.0,
                score
            )
        )

    # --------------------------------------------------------
    # Outside time window
    # --------------------------------------------------------

    return 0.0


# ============================================================
# BEHAVIOUR SCORE
# ============================================================

def normalize_behaviour_score(
    behaviour_score
):
    """
    Convert behaviour anomaly score from 0-100 into
    normalized 0-100 form.
    """

    if behaviour_score is None:

        return 0.0

    try:

        score = float(
            behaviour_score
        )

    except Exception:

        return 0.0

    return clamp(
        score,
        0.0,
        100.0
    )


# ============================================================
# AIS CONFIDENCE SCORE
# ============================================================

def calculate_data_confidence_score(
    data_confidence
):
    """
    Convert categorical AIS confidence into 0-100.
    """

    if data_confidence is None:

        return 40.0

    value = str(
        data_confidence
    ).strip().upper()

    if value == "HIGH":

        return 100.0

    elif value == "MEDIUM":

        return 70.0

    elif value == "LOW":

        return 40.0

    else:

        return 40.0


# ============================================================
# PRIORITY LEVEL
# ============================================================

def classify_priority(
    score
):
    """
    Convert final investigation score into a priority level.
    """

    if score >= 75.0:

        return "HIGH_PRIORITY"

    elif score >= 50.0:

        return "MEDIUM_PRIORITY"

    else:

        return "LOW_PRIORITY"


# ============================================================
# INVESTIGATION SCORE
# ============================================================

def calculate_investigation_score(
    distance_km,
    time_difference_minutes,
    behaviour_score,
    data_confidence,
    max_distance_km=20.0,
    max_time_minutes=180.0
):
    """
    Calculate the final investigation priority score.

    Current prototype weights:

        Spatial proximity   = 40%
        Temporal proximity  = 35%
        Behaviour anomaly   = 15%
        AIS confidence      = 10%

    These are prototype weights and should be validated
    using domain-expert feedback and historical cases.
    """

    spatial_score = (
        calculate_spatial_score(
            distance_km,
            max_distance_km
        )
    )

    temporal_score = (
        calculate_temporal_score(
            time_difference_minutes,
            max_time_minutes
        )
    )

    behaviour_normalized = (
        normalize_behaviour_score(
            behaviour_score
        )
    )

    confidence_score = (
        calculate_data_confidence_score(
            data_confidence
        )
    )

    # --------------------------------------------------------
    # Weighted final score
    # --------------------------------------------------------

    final_score = (

        0.40
        *
        spatial_score

        +

        0.35
        *
        temporal_score

        +

        0.15
        *
        behaviour_normalized

        +

        0.10
        *
        confidence_score
    )

    final_score = clamp(
        final_score,
        0.0,
        100.0
    )

    return {
        "spatial_score":
            round(
                spatial_score,
                2
            ),

        "temporal_score":
            round(
                temporal_score,
                2
            ),

        "behaviour_score_normalized":
            round(
                behaviour_normalized,
                2
            ),

        "data_confidence_score":
            round(
                confidence_score,
                2
            ),

        "investigation_priority_score":
            round(
                final_score,
                2
            ),

        "priority_level":
            classify_priority(
                final_score
            )
    }


# ============================================================
# GENERATE INVESTIGATION REASONS
# ============================================================

def generate_investigation_reasons(
    distance_km,
    time_difference_minutes,
    behaviour_score,
    data_confidence
):
    """
    Generate human-readable evidence reasons.
    """

    reasons = []

    distance_km = float(
        distance_km
    )

    time_difference_minutes = abs(
        float(
            time_difference_minutes
        )
    )

    behaviour_score = normalize_behaviour_score(
        behaviour_score
    )

    confidence_score = (
        calculate_data_confidence_score(
            data_confidence
        )
    )

    # --------------------------------------------------------
    # Spatial evidence
    # --------------------------------------------------------

    if distance_km <= 0.10:

        reasons.append(
            "Vessel was at or extremely close to "
            "the detected spill location"
        )

    elif distance_km <= 1.0:

        reasons.append(
            "Vessel was very close to the "
            "detected spill"
        )

    elif distance_km <= 5.0:

        reasons.append(
            "Vessel was close to the "
            "detected spill"
        )

    elif distance_km <= 10.0:

        reasons.append(
            "Vessel was within the configured "
            "spill investigation radius"
        )

    else:

        reasons.append(
            "Vessel was relatively far from "
            "the detected spill"
        )

    # --------------------------------------------------------
    # Temporal evidence
    # --------------------------------------------------------

    if time_difference_minutes <= 1.0:

        reasons.append(
            "Vessel activity almost exactly matched "
            "the spill detection time"
        )

    elif time_difference_minutes <= 5.0:

        reasons.append(
            "Vessel activity was very close to "
            "the spill detection time"
        )

    elif time_difference_minutes <= 30.0:

        reasons.append(
            "Vessel activity was close to "
            "the spill detection time"
        )

    elif time_difference_minutes <= 60.0:

        reasons.append(
            "Vessel activity occurred within "
            "one hour of the spill detection"
        )

    else:

        reasons.append(
            "Vessel activity had a larger time gap "
            "from the spill detection"
        )

    # --------------------------------------------------------
    # Behaviour evidence
    # --------------------------------------------------------

    if behaviour_score >= 70.0:

        reasons.append(
            "High behavioural anomaly detected"
        )

    elif behaviour_score >= 40.0:

        reasons.append(
            "Moderate behavioural anomaly detected"
        )

    elif behaviour_score >= 20.0:

        reasons.append(
            "Some behavioural anomaly detected"
        )

    else:

        reasons.append(
            "Low behavioural anomaly"
        )

    # --------------------------------------------------------
    # AIS confidence
    # --------------------------------------------------------

    if confidence_score >= 100.0:

        reasons.append(
            "High AIS data confidence"
        )

    elif confidence_score >= 70.0:

        reasons.append(
            "Medium AIS data confidence"
        )

    else:

        reasons.append(
            "Low AIS data confidence"
        )

    return reasons


# ============================================================
# COMPLETE VESSEL RANKING
# ============================================================

def rank_vessel(
    mmsi,
    distance_km,
    time_difference_minutes,
    behaviour_score,
    data_confidence,
    latitude=None,
    longitude=None,
    speed=None,
    course=None,
    max_distance_km=20.0,
    max_time_minutes=180.0
):
    """
    Rank a vessel for investigation.
    """

    score_result = calculate_investigation_score(

        distance_km,

        time_difference_minutes,

        behaviour_score,

        data_confidence,

        max_distance_km,

        max_time_minutes
    )

    reasons = generate_investigation_reasons(

        distance_km,

        time_difference_minutes,

        behaviour_score,

        data_confidence
    )

    result = {

        "MMSI":
            mmsi,

        "distance_km":
            round(
                float(
                    distance_km
                ),
                3
            ),

        "time_difference_minutes":
            round(
                abs(
                    float(
                        time_difference_minutes
                    )
                ),
                2
            ),

        "behaviour_score":
            round(
                float(
                    behaviour_score
                    if behaviour_score is not None
                    else 0.0
                ),
                2
            ),

        "spatial_score":
            score_result[
                "spatial_score"
            ],

        "temporal_score":
            score_result[
                "temporal_score"
            ],

        "behaviour_score_normalized":
            score_result[
                "behaviour_score_normalized"
            ],

        "data_confidence_score":
            score_result[
                "data_confidence_score"
            ],

        "data_confidence":
            data_confidence,

        "investigation_priority_score":
            score_result[
                "investigation_priority_score"
            ],

        "priority_level":
            score_result[
                "priority_level"
            ],

        "reasons":
            reasons
    }

    # --------------------------------------------------------
    # Optional vessel metadata
    # --------------------------------------------------------

    if latitude is not None:

        result["latitude"] = latitude

    if longitude is not None:

        result["longitude"] = longitude

    if speed is not None:

        result["sog"] = speed

    if course is not None:

        result["cog"] = course

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n======================================"
    )

    print(
        "    INVESTIGATION RANKING TEST"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Example vessels
    # --------------------------------------------------------

    test_vessels = [

        {
            "mmsi":
                "EXACT_MATCH",

            "distance":
                0.0,

            "time":
                0.0,

            "behaviour":
                20.0,

            "confidence":
                "LOW"
        },

        {
            "mmsi":
                "VERY_CLOSE",

            "distance":
                0.05,

            "time":
                0.5,

            "behaviour":
                30.0,

            "confidence":
                "MEDIUM"
        },

        {
            "mmsi":
                "CLOSE",

            "distance":
                2.0,

            "time":
                5.0,

            "behaviour":
                40.0,

            "confidence":
                "HIGH"
        },

        {
            "mmsi":
                "FARTHER",

            "distance":
                10.0,

            "time":
                60.0,

            "behaviour":
                70.0,

            "confidence":
                "HIGH"
        }
    ]

    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    for vessel in test_vessels:

        result = rank_vessel(

            vessel["mmsi"],

            vessel["distance"],

            vessel["time"],

            vessel["behaviour"],

            vessel["confidence"]
        )

        print(
            "\n--------------------------------------"
        )

        print(
            f"MMSI: "
            f"{result['MMSI']}"
        )

        print(
            f"Distance: "
            f"{result['distance_km']:.3f} km"
        )

        print(
            f"Time difference: "
            f"{result['time_difference_minutes']:.2f} min"
        )

        print(
            f"Spatial score: "
            f"{result['spatial_score']:.2f}"
        )

        print(
            f"Temporal score: "
            f"{result['temporal_score']:.2f}"
        )

        print(
            f"Behaviour score: "
            f"{result['behaviour_score']:.2f}"
        )

        print(
            f"AIS confidence: "
            f"{result['data_confidence']}"
        )

        print(
            f"Investigation score: "
            f"{result['investigation_priority_score']:.2f}"
        )

        print(
            f"Priority: "
            f"{result['priority_level']}"
        )


# ============================================================
# END
# ============================================================