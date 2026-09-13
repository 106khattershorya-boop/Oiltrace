# ============================================================
# FINAL VESSEL BEHAVIOUR SCORE
# ============================================================
#
# SIH 26143
#
# Purpose:
# Convert AIS trajectory features + anomaly detection results
# into a vessel-level behaviour score.
#
# Signals:
#   1. Speed anomaly
#   2. Stopping behaviour
#   3. Course deviation
#   4. AIS transmission gaps
#   5. Loitering
#   6. Isolation Forest anomaly
#   7. AIS data availability
#
# IMPORTANT:
#
# Behaviour score = investigation evidence.
#
# It is NOT:
#   - probability of guilt
#   - proof of illegal activity
#   - proof of pollution responsibility
#
# ============================================================

import os
import math

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AIS_DIR = CURRENT_DIR

PROJECT_ROOT = os.path.dirname(
    AIS_DIR
)

DATA_DIR = os.path.join(
    AIS_DIR,
    "data"
)

INPUT_FILE = os.path.join(
    DATA_DIR,
    "behaviour_anomaly_results.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "final_behaviour_scores.csv"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):
    """
    Keep value inside a fixed range.
    """

    try:

        value = float(
            value
        )

    except Exception:

        return minimum

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def safe_float(
    value,
    default=0.0
):
    """
    Safely convert a value to float.
    """

    try:

        value = float(
            value
        )

        if math.isnan(
            value
        ):

            return default

        if math.isinf(
            value
        ):

            return default

        return value

    except Exception:

        return default


def find_column(
    dataframe,
    possible_names
):
    """
    Find the first matching column name.
    """

    lower_map = {
        str(column).lower():
            column

        for column
        in dataframe.columns
    }

    for name in possible_names:

        key = str(
            name
        ).lower()

        if key in lower_map:

            return lower_map[
                key
            ]

    return None


def normalize_series_0_1(
    series,
    minimum=None,
    maximum=None
):
    """
    Normalize a pandas series to 0-1.
    """

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(
        0.0
    )

    if minimum is None:

        minimum = float(
            values.min()
        )

    if maximum is None:

        maximum = float(
            values.max()
        )

    if maximum <= minimum:

        return pd.Series(
            0.0,
            index=series.index
        )

    normalized = (
        values
        -
        minimum
    ) / (
        maximum
        -
        minimum
    )

    return normalized.clip(
        0.0,
        1.0
    )


# ============================================================
# SPEED ANOMALY
# ============================================================

def calculate_speed_anomaly(
    group
):
    """
    Calculate vessel-level speed anomaly.

    We use:
        speed variation / typical speed

    Higher variation = stronger anomaly.

    Normalized to 0-1.
    """

    speed_column = find_column(
        group,
        [
            "sog",
            "speed"
        ]
    )

    speed_change_column = find_column(
        group,
        [
            "speed_change",
            "speed_variation"
        ]
    )

    values = []

    # --------------------------------------------------------
    # Direct speed-change signal
    # --------------------------------------------------------

    if speed_change_column is not None:

        speed_changes = pd.to_numeric(
            group[
                speed_change_column
            ],
            errors="coerce"
        ).dropna()

        if len(
            speed_changes
        ) > 0:

            median_change = float(
                speed_changes.abs().median()
            )

            values.append(
                clamp(
                    median_change /
                    5.0
                )
            )

            high_change_fraction = float(
                (
                    speed_changes.abs()
                    >=
                    3.0
                ).mean()
            )

            values.append(
                clamp(
                    high_change_fraction
                )
            )

    # --------------------------------------------------------
    # SOG variation signal
    # --------------------------------------------------------

    if speed_column is not None:

        speeds = pd.to_numeric(
            group[
                speed_column
            ],
            errors="coerce"
        ).dropna()

        if len(
            speeds
        ) > 1:

            standard_deviation = float(
                speeds.std()
            )

            values.append(
                clamp(
                    standard_deviation /
                    5.0
                )
            )

    if not values:

        return 0.0

    return clamp(
        np.mean(
            values
        )
    )


# ============================================================
# STOPPING BEHAVIOUR
# ============================================================

def calculate_stop_score(
    group
):
    """
    Detect unusual stopping behaviour.

    A stop is treated as stronger evidence when the vessel
    also shows movement before/after the stop.

    This prevents every vessel in a naturally slow/static area
    from being automatically treated as anomalous.
    """

    stopped_column = find_column(
        group,
        [
            "stopped",
            "is_stopped"
        ]
    )

    speed_column = find_column(
        group,
        [
            "sog",
            "speed"
        ]
    )

    stop_fraction = 0.0

    if stopped_column is not None:

        stopped = pd.to_numeric(
            group[
                stopped_column
            ],
            errors="coerce"
        ).fillna(
            0
        )

        stop_fraction = float(
            stopped.mean()
        )

    elif speed_column is not None:

        speeds = pd.to_numeric(
            group[
                speed_column
            ],
            errors="coerce"
        ).fillna(
            0
        )

        stop_fraction = float(
            (
                speeds
                <=
                0.5
            ).mean()
        )

    # --------------------------------------------------------
    # Movement fraction
    # --------------------------------------------------------

    movement_fraction = 0.0

    if speed_column is not None:

        speeds = pd.to_numeric(
            group[
                speed_column
            ],
            errors="coerce"
        ).fillna(
            0
        )

        movement_fraction = float(
            (
                speeds
                >
                1.0
            ).mean()
        )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------
    #
    # A vessel that is stopped all the time is less
    # informative than a vessel that was moving and then
    # stopped.
    #
    # --------------------------------------------------------

    transition_factor = clamp(
        movement_fraction
        *
        1.5
    )

    score = (
        stop_fraction
        *
        transition_factor
    )

    return clamp(
        score
    )


# ============================================================
# COURSE DEVIATION
# ============================================================

def calculate_course_score(
    group
):
    """
    Calculate vessel-level course deviation score.

    Uses:
        course_change

    or calculates changes from COG when available.
    """

    course_change_column = find_column(
        group,
        [
            "course_change",
            "course_deviation"
        ]
    )

    course_values = []

    # --------------------------------------------------------
    # Existing course-change feature
    # --------------------------------------------------------

    if course_change_column is not None:

        changes = pd.to_numeric(
            group[
                course_change_column
            ],
            errors="coerce"
        ).dropna()

        if len(
            changes
        ) > 0:

            course_values.extend(
                changes.abs().tolist()
            )

    # --------------------------------------------------------
    # Calculate from COG if necessary
    # --------------------------------------------------------

    if (
        not course_values
    ):

        cog_column = find_column(
            group,
            [
                "cog",
                "course"
            ]
        )

        if cog_column is not None:

            cog = pd.to_numeric(
                group[
                    cog_column
                ],
                errors="coerce"
            ).dropna()

            if len(
                cog
            ) > 1:

                differences = []

                previous = None

                for value in cog:

                    if previous is not None:

                        difference = abs(
                            value
                            -
                            previous
                        )

                        if difference > 180:

                            difference = (
                                360
                                -
                                difference
                            )

                        differences.append(
                            difference
                        )

                    previous = value

                course_values = differences

    if not course_values:

        return 0.0

    course_array = np.asarray(
        course_values,
        dtype=float
    )

    median_change = float(
        np.median(
            course_array
        )
    )

    large_change_fraction = float(
        (
            course_array
            >=
            20.0
        ).mean()
    )

    strong_change_fraction = float(
        (
            course_array
            >=
            45.0
        ).mean()
    )

    score = (
        0.35
        *
        clamp(
            median_change /
            90.0
        )

        +

        0.40
        *
        clamp(
            large_change_fraction
        )

        +

        0.25
        *
        clamp(
            strong_change_fraction
        )
    )

    return clamp(
        score
    )


# ============================================================
# AIS GAP SCORE
# ============================================================

def calculate_ais_gap_score(
    group
):
    """
    Detect unusually long AIS transmission gaps.

    Current implementation uses ais_gap if available.
    """

    gap_column = find_column(
        group,
        [
            "ais_gap",
            "gap",
            "is_ais_gap"
        ]
    )

    if gap_column is None:

        return 0.0

    values = pd.to_numeric(
        group[
            gap_column
        ],
        errors="coerce"
    ).fillna(
        0
    )

    if len(
        values
    ) == 0:

        return 0.0

    if values.max() <= 1:

        # Binary 0/1 column
        gap_fraction = float(
            values.mean()
        )

        return clamp(
            gap_fraction
            *
            2.0
        )

    # --------------------------------------------------------
    # If actual gap duration exists
    # --------------------------------------------------------

    long_gap_fraction = float(
        (
            values
            >=
            10.0
        ).mean()
    )

    very_long_gap_fraction = float(
        (
            values
            >=
            30.0
        ).mean()
    )

    score = (
        0.60
        *
        clamp(
            long_gap_fraction
        )

        +

        0.40
        *
        clamp(
            very_long_gap_fraction
        )
    )

    return clamp(
        score
    )


# ============================================================
# LOITERING SCORE
# ============================================================

def calculate_loitering_score(
    group
):
    """
    Use the existing loitering feature.
    """

    loitering_column = find_column(
        group,
        [
            "loitering",
            "is_loitering"
        ]
    )

    if loitering_column is None:

        return 0.0

    values = pd.to_numeric(
        group[
            loitering_column
        ],
        errors="coerce"
    ).fillna(
        0
    )

    if len(
        values
    ) == 0:

        return 0.0

    if values.max() <= 1:

        fraction = float(
            values.mean()
        )

        return clamp(
            fraction
            *
            2.0
        )

    return clamp(
        float(
            values.mean()
        )
    )


# ============================================================
# MACHINE LEARNING ANOMALY SCORE
# ============================================================

def calculate_ml_anomaly_score(
    group
):
    """
    Convert Isolation Forest results into 0-1 anomaly score.

    Supports multiple common column names.
    """

    anomaly_column = find_column(
        group,
        [
            "anomaly",
            "anomaly_score",
            "isolation_score",
            "is_anomaly",
            "outlier",
            "prediction"
        ]
    )

    if anomaly_column is None:

        return 0.0

    values = pd.to_numeric(
        group[
            anomaly_column
        ],
        errors="coerce"
    ).dropna()

    if len(
        values
    ) == 0:

        return 0.0

    # --------------------------------------------------------
    # Binary anomaly prediction
    # --------------------------------------------------------

    unique_values = set(
        values.unique()
    )

    if unique_values.issubset(
        {
            -1,
            0,
            1
        }
    ):

        # IsolationForest normally uses:
        #
        # -1 = anomaly
        #  1 = normal
        #
        anomaly_fraction = float(
            (
                values
                ==
                -1
            ).mean()
        )

        # Also support 1 = anomaly / 0 = normal
        if (
            -1 not in unique_values
            and
            1 in unique_values
        ):

            anomaly_fraction = float(
                (
                    values
                    ==
                    1
                ).mean()
            )

        return clamp(
            anomaly_fraction
            *
            2.5
        )

    # --------------------------------------------------------
    # Continuous anomaly score
    # --------------------------------------------------------

    numeric_values = values.abs()

    percentile_90 = float(
        np.percentile(
            numeric_values,
            90
        )
    )

    if percentile_90 <= 0:

        return 0.0

    return clamp(
        float(
            numeric_values.mean()
        )
        /
        percentile_90
    )


# ============================================================
# DATA CONFIDENCE
# ============================================================

def calculate_data_confidence(
    record_count,
    duration_hours,
    valid_position_fraction
):
    """
    Estimate confidence based on amount and quality of AIS
    data available for the vessel.

    This is data-quality confidence, not confidence that the
    behaviour indicates wrongdoing.
    """

    # --------------------------------------------------------
    # Record-count component
    # --------------------------------------------------------

    if record_count >= 100:

        record_score = 1.0

    elif record_count >= 50:

        record_score = 0.85

    elif record_count >= 20:

        record_score = 0.70

    elif record_count >= 10:

        record_score = 0.50

    elif record_count >= 5:

        record_score = 0.30

    else:

        record_score = 0.15

    # --------------------------------------------------------
    # Duration component
    # --------------------------------------------------------

    if duration_hours >= 6:

        duration_score = 1.0

    elif duration_hours >= 3:

        duration_score = 0.80

    elif duration_hours >= 1:

        duration_score = 0.60

    elif duration_hours >= 0.25:

        duration_score = 0.40

    else:

        duration_score = 0.20

    # --------------------------------------------------------
    # Position quality
    # --------------------------------------------------------

    valid_position_fraction = clamp(
        valid_position_fraction
    )

    confidence = (

        0.40
        *
        record_score

        +

        0.30
        *
        duration_score

        +

        0.30
        *
        valid_position_fraction
    )

    return clamp(
        confidence
    )


def classify_data_confidence(
    score
):
    """
    Convert confidence score into category.
    """

    if score >= 0.75:

        return "HIGH"

    elif score >= 0.50:

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# BEHAVIOUR LEVEL
# ============================================================

def classify_behaviour(
    score
):
    """
    Convert behaviour score into a human-readable level.
    """

    if score >= 70:

        return "HIGH_ANOMALY"

    elif score >= 40:

        return "MEDIUM_ANOMALY"

    elif score >= 20:

        return "LOW_ANOMALY"

    else:

        return "VERY_LOW_ANOMALY"


# ============================================================
# REASONS
# ============================================================

def generate_reasons(
    speed_score,
    stop_score,
    course_score,
    gap_score,
    loitering_score,
    anomaly_score
):
    """
    Create explanations for the behaviour score.
    """

    reasons = []

    # --------------------------------------------------------
    # Speed
    # --------------------------------------------------------

    if speed_score >= 0.70:

        reasons.append(
            "Significant speed variation detected"
        )

    elif speed_score >= 0.40:

        reasons.append(
            "Moderate speed variation detected"
        )

    # --------------------------------------------------------
    # Stop
    # --------------------------------------------------------

    if stop_score >= 0.70:

        reasons.append(
            "Unusual stopping behaviour detected"
        )

    elif stop_score >= 0.40:

        reasons.append(
            "Some stopping behaviour detected"
        )

    # --------------------------------------------------------
    # Course
    # --------------------------------------------------------

    if course_score >= 0.70:

        reasons.append(
            "Significant course deviation detected"
        )

    elif course_score >= 0.40:

        reasons.append(
            "Moderate course variation detected"
        )

    # --------------------------------------------------------
    # AIS gaps
    # --------------------------------------------------------

    if gap_score >= 0.70:

        reasons.append(
            "Frequent or long AIS transmission gaps detected"
        )

    elif gap_score >= 0.40:

        reasons.append(
            "Some AIS transmission gaps detected"
        )

    # --------------------------------------------------------
    # Loitering
    # --------------------------------------------------------

    if loitering_score >= 0.70:

        reasons.append(
            "Strong loitering pattern detected"
        )

    elif loitering_score >= 0.40:

        reasons.append(
            "Possible loitering behaviour detected"
        )

    # --------------------------------------------------------
    # ML anomaly
    # --------------------------------------------------------

    if anomaly_score >= 0.70:

        reasons.append(
            "Machine-learning anomaly detector flagged "
            "unusual AIS behaviour"
        )

    elif anomaly_score >= 0.40:

        reasons.append(
            "Machine-learning anomaly detector found "
            "some unusual behaviour"
        )

    # --------------------------------------------------------
    # No strong evidence
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "No strong behavioural anomaly detected"
        )

    return reasons


# ============================================================
# PROCESS ONE VESSEL
# ============================================================

def process_vessel(
    mmsi,
    group
):
    """
    Calculate final vessel-level behaviour information.
    """

    group = group.copy()

    # --------------------------------------------------------
    # Basic values
    # --------------------------------------------------------

    record_count = len(
        group
    )

    # --------------------------------------------------------
    # Speed anomaly
    # --------------------------------------------------------

    speed_score = (
        calculate_speed_anomaly(
            group
        )
    )

    # --------------------------------------------------------
    # Stop
    # --------------------------------------------------------

    stop_score = (
        calculate_stop_score(
            group
        )
    )

    # --------------------------------------------------------
    # Course
    # --------------------------------------------------------

    course_score = (
        calculate_course_score(
            group
        )
    )

    # --------------------------------------------------------
    # AIS gap
    # --------------------------------------------------------

    gap_score = (
        calculate_ais_gap_score(
            group
        )
    )

    # --------------------------------------------------------
    # Loitering
    # --------------------------------------------------------

    loitering_score = (
        calculate_loitering_score(
            group
        )
    )

    # --------------------------------------------------------
    # ML anomaly
    # --------------------------------------------------------

    anomaly_score = (
        calculate_ml_anomaly_score(
            group
        )
    )

    # ========================================================
    # FINAL BEHAVIOUR SCORE
    # ========================================================
    #
    # Prototype weights:
    #
    # Speed       20%
    # Stop        15%
    # Course      20%
    # AIS gap     15%
    # Loitering   10%
    # ML anomaly  20%
    #
    # ========================================================

    final_score = (

        0.20
        *
        speed_score

        +

        0.15
        *
        stop_score

        +

        0.20
        *
        course_score

        +

        0.15
        *
        gap_score

        +

        0.10
        *
        loitering_score

        +

        0.20
        *
        anomaly_score
    )

    final_score = (
        clamp(
            final_score
        )
        *
        100.0
    )

    final_score = round(
        final_score,
        2
    )

    # ========================================================
    # BEHAVIOUR LEVEL
    # ========================================================

    behaviour_level = classify_behaviour(
        final_score
    )

    # ========================================================
    # TIME COVERAGE
    # ========================================================

    time_column = find_column(
        group,
        [
            "base_date_time",
            "timestamp",
            "datetime",
            "time"
        ]
    )

    duration_hours = 0.0

    if time_column is not None:

        timestamps = pd.to_datetime(
            group[
                time_column
            ],
            errors="coerce"
        ).dropna()

        if len(
            timestamps
        ) > 1:

            duration_seconds = (
                timestamps.max()
                -
                timestamps.min()
            ).total_seconds()

            duration_hours = (
                max(
                    0.0,
                    duration_seconds
                )
                /
                3600.0
            )

    # ========================================================
    # POSITION QUALITY
    # ========================================================

    latitude_column = find_column(
        group,
        [
            "latitude",
            "lat"
        ]
    )

    longitude_column = find_column(
        group,
        [
            "longitude",
            "lon",
            "lng"
        ]
    )

    if (
        latitude_column is not None
        and
        longitude_column is not None
    ):

        latitude = pd.to_numeric(
            group[
                latitude_column
            ],
            errors="coerce"
        )

        longitude = pd.to_numeric(
            group[
                longitude_column
            ],
            errors="coerce"
        )

        valid_positions = (
            latitude.notna()
            &
            longitude.notna()
        )

        valid_position_fraction = float(
            valid_positions.mean()
        )

    else:

        valid_position_fraction = 0.0

    # ========================================================
    # DATA CONFIDENCE
    # ========================================================

    confidence_score = (
        calculate_data_confidence(
            record_count,
            duration_hours,
            valid_position_fraction
        )
    )

    data_confidence = (
        classify_data_confidence(
            confidence_score
        )
    )

    # ========================================================
    # REASONS
    # ========================================================

    reasons = generate_reasons(

        speed_score,

        stop_score,

        course_score,

        gap_score,

        loitering_score,

        anomaly_score
    )

    # ========================================================
    # ADDITIONAL STATISTICS
    # ========================================================

    speed_column = find_column(
        group,
        [
            "sog",
            "speed"
        ]
    )

    if speed_column is not None:

        speed_values = pd.to_numeric(
            group[
                speed_column
            ],
            errors="coerce"
        ).dropna()

        if len(
            speed_values
        ) > 0:

            average_speed = float(
                speed_values.mean()
            )

            maximum_speed = float(
                speed_values.max()
            )

        else:

            average_speed = 0.0
            maximum_speed = 0.0

    else:

        average_speed = 0.0
        maximum_speed = 0.0

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "mmsi":
            mmsi,

        "behaviour_score":
            final_score,

        "behaviour_level":
            behaviour_level,

        "speed_anomaly_score":
            round(
                speed_score * 100.0,
                2
            ),

        "stop_score":
            round(
                stop_score * 100.0,
                2
            ),

        "course_deviation_score":
            round(
                course_score * 100.0,
                2
            ),

        "ais_gap_score":
            round(
                gap_score * 100.0,
                2
            ),

        "loitering_score":
            round(
                loitering_score * 100.0,
                2
            ),

        "ml_anomaly_score":
            round(
                anomaly_score * 100.0,
                2
            ),

        "average_speed":
            round(
                average_speed,
                3
            ),

        "maximum_speed":
            round(
                maximum_speed,
                3
            ),

        "record_count":
            record_count,

        "duration_hours":
            round(
                duration_hours,
                3
            ),

        "data_confidence_score":
            round(
                confidence_score * 100.0,
                2
            ),

        "data_confidence":
            data_confidence,

        "reasons":
            " | ".join(
                reasons
            )
    }


# ============================================================
# LOAD DATA
# ============================================================

def load_input_data():

    print(
        "\nLoading behaviour data..."
    )

    print(
        f"Input file:"
        f"\n{INPUT_FILE}"
    )

    if not os.path.exists(
        INPUT_FILE
    ):

        raise FileNotFoundError(
            "\nBehaviour file not found:\n"
            f"{INPUT_FILE}\n\n"
            "Run this first:\n"
            "python ais\\train_behaviour_model.py"
        )

    dataframe = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"\nRows loaded: "
        f"{len(dataframe)}"
    )

    print(
        f"Columns: "
        f"{len(dataframe.columns)}"
    )

    print(
        "\nAvailable columns:"
    )

    for column in dataframe.columns:

        print(
            f"  - {column}"
        )

    return dataframe


# ============================================================
# VALIDATE MMSI
# ============================================================

def validate_mmsi(
    dataframe
):

    mmsi_column = find_column(
        dataframe,
        [
            "mmsi"
        ]
    )

    if mmsi_column is None:

        raise ValueError(
            "\nMMSI column not found."
        )

    if mmsi_column != "mmsi":

        dataframe = dataframe.rename(
            columns={
                mmsi_column:
                    "mmsi"
            }
        )

    dataframe["mmsi"] = (
        dataframe["mmsi"]
        .astype(str)
        .str.strip()
    )

    dataframe = dataframe[
        dataframe["mmsi"]
        !=
        ""
    ]

    dataframe = dataframe[
        dataframe["mmsi"]
        !=
        "nan"
    ]

    return dataframe


# ============================================================
# PROCESS ALL VESSELS
# ============================================================

def calculate_vessel_scores(
    dataframe
):

    print(
        "\nProcessing vessel behaviour..."
    )

    results = []

    grouped = dataframe.groupby(
        "mmsi",
        sort=False
    )

    total_vessels = len(
        grouped
    )

    print(
        f"Unique vessels: "
        f"{total_vessels}"
    )

    for index, (
        mmsi,
        group
    ) in enumerate(
        grouped,
        start=1
    ):

        result = process_vessel(

            mmsi,

            group
        )

        results.append(
            result
        )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        if (
            index % 1000
            == 0
            or
            index == total_vessels
        ):

            print(
                f"Processed "
                f"{index}/"
                f"{total_vessels}"
            )

    results_df = pd.DataFrame(
        results
    )

    # ========================================================
    # RANKING
    # ========================================================

    results_df = results_df.sort_values(
        by=[
            "behaviour_score",
            "data_confidence_score"
        ],
        ascending=False
    ).reset_index(
        drop=True
    )

    results_df[
        "behaviour_rank"
    ] = (
        results_df.index
        +
        1
    )

    return results_df


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    results
):

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\nFinal behaviour scores saved:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    results
):

    print(
        "\n======================================"
    )

    print(
        "      FINAL BEHAVIOUR ANALYSIS"
    )

    print(
        "======================================"
    )

    print(
        f"\nTotal vessels: "
        f"{len(results)}"
    )

    # --------------------------------------------------------
    # Behaviour categories
    # --------------------------------------------------------

    print(
        "\nBehaviour levels:"
    )

    level_counts = (
        results[
            "behaviour_level"
        ]
        .value_counts()
    )

    for level, count in (
        level_counts.items()
    ):

        print(
            f"  {level}: "
            f"{count}"
        )

    # --------------------------------------------------------
    # Data confidence
    # --------------------------------------------------------

    print(
        "\nData confidence:"
    )

    confidence_counts = (
        results[
            "data_confidence"
        ]
        .value_counts()
    )

    for confidence, count in (
        confidence_counts.items()
    ):

        print(
            f"  {confidence}: "
            f"{count}"
        )

    # ========================================================
    # TOP 10
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "      TOP BEHAVIOURAL ANOMALIES"
    )

    print(
        "======================================"
    )

    top_results = results.head(
        10
    )

    for index, row in (
        top_results.iterrows()
    ):

        print(
            f"\n#{int(row['behaviour_rank'])}"
        )

        print(
            f"MMSI: "
            f"{row['mmsi']}"
        )

        print(
            f"Behaviour score: "
            f"{row['behaviour_score']:.2f}"
        )

        print(
            f"Behaviour level: "
            f"{row['behaviour_level']}"
        )

        print(
            f"Speed anomaly: "
            f"{row['speed_anomaly_score']:.2f}"
        )

        print(
            f"Stop score: "
            f"{row['stop_score']:.2f}"
        )

        print(
            f"Course deviation: "
            f"{row['course_deviation_score']:.2f}"
        )

        print(
            f"AIS gap: "
            f"{row['ais_gap_score']:.2f}"
        )

        print(
            f"Loitering: "
            f"{row['loitering_score']:.2f}"
        )

        print(
            f"ML anomaly: "
            f"{row['ml_anomaly_score']:.2f}"
        )

        print(
            f"Data confidence: "
            f"{row['data_confidence']}"
        )

        print(
            "Reasons:"
        )

        reasons = str(
            row["reasons"]
        ).split(
            " | "
        )

        for reason in reasons:

            print(
                f"  - {reason}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n======================================"
    )

    print(
        "     VESSEL BEHAVIOUR SCORING"
    )

    print(
        "======================================"
    )

    # ========================================================
    # LOAD
    # ========================================================

    dataframe = load_input_data()

    # ========================================================
    # VALIDATE
    # ========================================================

    dataframe = validate_mmsi(
        dataframe
    )

    print(
        f"\nRows after MMSI validation: "
        f"{len(dataframe)}"
    )

    # ========================================================
    # CALCULATE
    # ========================================================

    results = calculate_vessel_scores(
        dataframe
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_results(
        results
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print_summary(
        results
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "       BEHAVIOUR SCORING COMPLETE"
    )

    print(
        "======================================"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()