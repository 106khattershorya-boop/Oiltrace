def create_ml_output(
    spill_detected,
    spill_confidence,
    spill_area,
    oil_category,
    spectral_score,
    speed_anomaly,
    stop_anomaly,
    course_deviation,
    ais_gap,
    loitering,
    behaviour_score
):

    return {

        "spill": {

            "detected": spill_detected,

            "confidence": spill_confidence,

            "area": spill_area

        },

        "spectral": {

            "probable_oil_category":
                oil_category,

            "spectral_score":
                spectral_score

        },

        "behaviour": {

            "speed_anomaly":
                speed_anomaly,

            "stop_anomaly":
                stop_anomaly,

            "course_deviation":
                course_deviation,

            "ais_gap":
                ais_gap,

            "loitering":
                loitering,

            "behaviour_score":
                behaviour_score

        }
    }