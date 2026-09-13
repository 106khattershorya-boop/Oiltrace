# ============================================================
# EVIDENCE FUSION - VESSEL SPECIFIC VERSION
# ============================================================
#
# SIH 26143
#
# PURPOSE
# -------
# Combine vessel-specific evidence into an explainable
# investigation-priority score.
#
# IMPORTANT
# ---------
# This system prioritizes vessels for investigation.
# It does NOT prove that a vessel caused an oil spill.
#
#
# INCIDENT-LEVEL EVIDENCE
# -----------------------
# U-Net confidence
# False-positive filter score
# Spectral availability
#
#
# VESSEL-LEVEL EVIDENCE
# ---------------------
# Spatial proximity
# Temporal proximity
# Vessel behaviour
# Event behaviour
# AIS confidence
#
#
# The final investigation score uses only vessel-specific
# evidence.
#
# ============================================================

import os
import math

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ML_DIR = os.path.dirname(
    CURRENT_DIR
)

PROJECT_ROOT = os.path.dirname(
    ML_DIR
)

AIS_DIR = os.path.join(
    PROJECT_ROOT,
    "ais"
)

AIS_DATA_DIR = os.path.join(
    AIS_DIR,
    "data"
)

OUTPUT_DIR = os.path.join(
    ML_DIR,
    "data",
    "test",
    "pipeline_outputs"
)

BEHAVIOUR_FILE = os.path.join(
    AIS_DATA_DIR,
    "behaviour_anomaly_results.csv"
)

FINAL_BEHAVIOUR_FILE = os.path.join(
    AIS_DATA_DIR,
    "final_behaviour_scores.csv"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "evidence_fusion_results.csv"
)


# ============================================================
# DEMO SPILL EVENT
# ============================================================

SPILL_LATITUDE = 30.36441

SPILL_LONGITUDE = -89.08701

SPILL_TIME = pd.Timestamp(
    "2024-01-01 00:03:15"
)


# ============================================================
# INCIDENT-LEVEL EVIDENCE
# ============================================================

UNET_CONFIDENCE = 77.07

FALSE_POSITIVE_SCORE = 92.00

SPECTRAL_CATEGORY = (
    "INSUFFICIENT_MULTISPECTRAL_DATA"
)


# ============================================================
# VESSEL-SPECIFIC WEIGHTS
# ============================================================
#
# These are prototype configurable weights for the SIH demo.
# They are not scientific constants.
#
# Spatial and temporal association receive the highest weight
# because they directly describe the relationship between a
# vessel observation and the spill event.
#
# Behaviour is secondary evidence.
#
# AIS confidence adjusts the ranking according to data quality.
#
# ============================================================

VESSEL_WEIGHTS = {

    "spatial":
        0.35,

    "temporal":
        0.30,

    "behaviour":
        0.25,

    "ais_confidence":
        0.10
}


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=100.0
):

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


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    radius = 6371.0

    lat1 = math.radians(
        float(lat1)
    )

    lon1 = math.radians(
        float(lon1)
    )

    lat2 = math.radians(
        float(lat2)
    )

    lon2 = math.radians(
        float(lon2)
    )

    dlat = lat2 - lat1

    dlon = lon2 - lon1

    a = (
        math.sin(
            dlat / 2
        ) ** 2

        +

        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(
            dlon / 2
        ) ** 2
    )

    c = (
        2
        *
        math.atan2(
            math.sqrt(a),
            math.sqrt(
                1 - a
            )
        )
    )

    return radius * c


# ============================================================
# SPATIAL SCORE
# ============================================================

def calculate_spatial_score(
    distance_km
):
    """
    Convert distance to a 0-100 proximity score.
    """

    distance_km = max(
        0.0,
        float(distance_km)
    )

    # --------------------------------------------------------
    # 0 - 0.1 km
    # --------------------------------------------------------

    if distance_km <= 0.1:

        return 100.0

    # --------------------------------------------------------
    # 0.1 - 1 km
    # --------------------------------------------------------

    if distance_km <= 1.0:

        return (
            100.0
            -
            (
                distance_km
                -
                0.1
            )
            /
            0.9
            *
            10.0
        )

    # --------------------------------------------------------
    # 1 - 5 km
    # --------------------------------------------------------

    if distance_km <= 5.0:

        return (
            90.0
            -
            (
                distance_km
                -
                1.0
            )
            /
            4.0
            *
            35.0
        )

    # --------------------------------------------------------
    # 5 - 10 km
    # --------------------------------------------------------

    if distance_km <= 10.0:

        return (
            55.0
            -
            (
                distance_km
                -
                5.0
            )
            /
            5.0
            *
            30.0
        )

    # --------------------------------------------------------
    # 10 - 20 km
    # --------------------------------------------------------

    if distance_km <= 20.0:

        return (
            25.0
            -
            (
                distance_km
                -
                10.0
            )
            /
            10.0
            *
            25.0
        )

    return 0.0


# ============================================================
# TEMPORAL SCORE
# ============================================================

def calculate_temporal_score(
    minutes
):
    """
    Convert temporal difference to a 0-100 score.
    """

    minutes = abs(
        float(minutes)
    )

    # --------------------------------------------------------
    # 0 - 1 minute
    # --------------------------------------------------------

    if minutes <= 1:

        return 100.0

    # --------------------------------------------------------
    # 1 - 5 minutes
    # --------------------------------------------------------

    if minutes <= 5:

        return (
            100.0
            -
            (
                minutes
                -
                1
            )
            /
            4.0
            *
            15.0
        )

    # --------------------------------------------------------
    # 5 - 30 minutes
    # --------------------------------------------------------

    if minutes <= 30:

        return (
            85.0
            -
            (
                minutes
                -
                5
            )
            /
            25.0
            *
            45.0
        )

    # --------------------------------------------------------
    # 30 - 60 minutes
    # --------------------------------------------------------

    if minutes <= 60:

        return (
            40.0
            -
            (
                minutes
                -
                30
            )
            /
            30.0
            *
            25.0
        )

    # --------------------------------------------------------
    # 60 - 180 minutes
    # --------------------------------------------------------

    if minutes <= 180:

        return (
            15.0
            -
            (
                minutes
                -
                60
            )
            /
            120.0
            *
            15.0
        )

    return 0.0


# ============================================================
# AIS CONFIDENCE
# ============================================================

def calculate_ais_confidence(
    value
):
    """
    Convert AIS confidence label to numerical score.
    """

    if pd.isna(
        value
    ):

        return 40.0

    label = str(
        value
    ).strip().upper()

    if label == "HIGH":

        return 100.0

    if label == "MEDIUM":

        return 70.0

    if label == "LOW":

        return 40.0

    return 40.0


# ============================================================
# BEHAVIOUR SCORE
# ============================================================

def normalize_behaviour_score(
    value
):

    if pd.isna(
        value
    ):

        return 0.0

    return clamp(
        float(value)
    )


# ============================================================
# PRIORITY LEVEL
# ============================================================

def priority_level(
    score
):

    score = float(
        score
    )

    if score >= 75:

        return "HIGH"

    if score >= 50:

        return "MEDIUM"

    return "LOW"


# ============================================================
# BEHAVIOUR LEVEL
# ============================================================

def behaviour_level(
    score
):

    score = float(
        score
    )

    if score >= 75:

        return "HIGH"

    if score >= 50:

        return "MEDIUM"

    return "LOW"


# ============================================================
# HUMAN-READABLE REASONS
# ============================================================

def build_reasons(
    row
):

    reasons = []

    spatial = float(
        row.get(
            "spatial_score",
            0.0
        )
    )

    temporal = float(
        row.get(
            "temporal_score",
            0.0
        )
    )

    behaviour = float(
        row.get(
            "combined_behaviour_score",
            0.0
        )
    )

    ais_confidence = float(
        row.get(
            "ais_confidence_score",
            40.0
        )
    )

    # --------------------------------------------------------
    # Spatial
    # --------------------------------------------------------

    if spatial >= 90:

        reasons.append(
            "Very close to spill location"
        )

    elif spatial >= 55:

        reasons.append(
            "Moderately close to spill location"
        )

    else:

        reasons.append(
            "Relatively distant from spill location"
        )

    # --------------------------------------------------------
    # Temporal
    # --------------------------------------------------------

    if temporal >= 85:

        reasons.append(
            "Very close to spill event time"
        )

    elif temporal >= 40:

        reasons.append(
            "Temporally associated with spill event"
        )

    else:

        reasons.append(
            "Weak temporal association"
        )

    # --------------------------------------------------------
    # Behaviour
    # --------------------------------------------------------

    if behaviour >= 75:

        reasons.append(
            "Strong vessel behaviour anomaly"
        )

    elif behaviour >= 50:

        reasons.append(
            "Moderate vessel behaviour anomaly"
        )

    elif behaviour >= 25:

        reasons.append(
            "Some behaviour anomaly detected"
        )

    else:

        reasons.append(
            "Low behaviour anomaly"
        )

    # --------------------------------------------------------
    # AIS confidence
    # --------------------------------------------------------

    if ais_confidence >= 100:

        reasons.append(
            "High AIS data confidence"
        )

    elif ais_confidence >= 70:

        reasons.append(
            "Medium AIS data confidence"
        )

    else:

        reasons.append(
            "Low AIS data confidence"
        )

    # --------------------------------------------------------
    # Spectral
    # --------------------------------------------------------

    spectral_available = bool(
        row.get(
            "spectral_available",
            False
        )
    )

    if spectral_available:

        reasons.append(
            "Multispectral evidence available"
        )

    else:

        reasons.append(
            "Multispectral oil-category evidence unavailable"
        )

    return reasons


# ============================================================
# LOAD BEHAVIOUR DATA
# ============================================================

def load_behaviour_data():

    if not os.path.exists(
        BEHAVIOUR_FILE
    ):

        raise FileNotFoundError(
            "\nBehaviour file not found:\n"
            f"{BEHAVIOUR_FILE}"
        )

    df = pd.read_csv(
        BEHAVIOUR_FILE
    )

    if df.empty:

        raise ValueError(
            "Behaviour CSV is empty."
        )

    return df


# ============================================================
# LOAD FINAL BEHAVIOUR DATA
# ============================================================

def load_final_behaviour_data():

    if not os.path.exists(
        FINAL_BEHAVIOUR_FILE
    ):

        print(
            "\nWARNING:"
            "\nFinal behaviour file not found."
        )

        return None

    try:

        df = pd.read_csv(
            FINAL_BEHAVIOUR_FILE
        )

    except Exception as error:

        print(
            "\nWARNING:"
            "\nCould not read final behaviour file."
            f"\nReason: {error}"
        )

        return None

    if df.empty:

        return None

    return df


# ============================================================
# NORMALIZE COLUMNS
# ============================================================

def normalize_columns(
    df
):

    df = df.copy()

    df.columns = [

        str(
            column
        ).strip()

        for column
        in df.columns
    ]

    return df


# ============================================================
# PREPARE BEHAVIOUR DATA
# ============================================================

def prepare_behaviour_data(
    behaviour_df,
    final_df
):

    behaviour_df = normalize_columns(
        behaviour_df
    )

    required_columns = [

        "mmsi",

        "base_date_time",

        "latitude",

        "longitude"
    ]

    for column in required_columns:

        if column not in behaviour_df.columns:

            raise ValueError(
                "\nRequired column missing:"
                f"\n{column}"
            )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    behaviour_df[
        "base_date_time"
    ] = pd.to_datetime(
        behaviour_df[
            "base_date_time"
        ],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    behaviour_df[
        "latitude"
    ] = pd.to_numeric(
        behaviour_df[
            "latitude"
        ],
        errors="coerce"
    )

    behaviour_df[
        "longitude"
    ] = pd.to_numeric(
        behaviour_df[
            "longitude"
        ],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Merge vessel-level behaviour
    # --------------------------------------------------------

    if final_df is not None:

        final_df = normalize_columns(
            final_df
        )

        if "mmsi" in final_df.columns:

            score_candidates = [

                "behaviour_score",

                "final_behaviour_score",

                "vessel_behaviour_score",

                "behaviour_anomaly_score"
            ]

            score_column = None

            for candidate in score_candidates:

                if candidate in final_df.columns:

                    score_column = candidate

                    break

            confidence_candidates = [

                "data_confidence",

                "confidence"
            ]

            confidence_column = None

            for candidate in confidence_candidates:

                if candidate in final_df.columns:

                    confidence_column = candidate

                    break

            merge_columns = [
                "mmsi"
            ]

            if score_column is not None:

                merge_columns.append(
                    score_column
                )

            if confidence_column is not None:

                merge_columns.append(
                    confidence_column
                )

            final_small = (
                final_df[
                    merge_columns
                ]
                .drop_duplicates(
                    subset=[
                        "mmsi"
                    ]
                )
            )

            rename_map = {}

            if score_column is not None:

                rename_map[
                    score_column
                ] = "vessel_behaviour_score"

            if confidence_column is not None:

                rename_map[
                    confidence_column
                ] = "vessel_data_confidence"

            final_small = final_small.rename(
                columns=rename_map
            )

            behaviour_df = behaviour_df.merge(
                final_small,
                on="mmsi",
                how="left"
            )

    # --------------------------------------------------------
    # Fallback vessel behaviour
    # --------------------------------------------------------

    if (
        "vessel_behaviour_score"
        not in behaviour_df.columns
    ):

        if (
            "behaviour_anomaly_score"
            in behaviour_df.columns
        ):

            behaviour_df[
                "vessel_behaviour_score"
            ] = pd.to_numeric(
                behaviour_df[
                    "behaviour_anomaly_score"
                ],
                errors="coerce"
            )

        elif (
            "anomaly_score"
            in behaviour_df.columns
        ):

            raw = pd.to_numeric(
                behaviour_df[
                    "anomaly_score"
                ],
                errors="coerce"
            )

            behaviour_df[
                "vessel_behaviour_score"
            ] = (
                raw.rank(
                    pct=True
                )
                *
                100.0
            )

        else:

            behaviour_df[
                "vessel_behaviour_score"
            ] = 0.0

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    if (
        "vessel_data_confidence"
        not in behaviour_df.columns
    ):

        behaviour_df[
            "vessel_data_confidence"
        ] = "MEDIUM"

    # --------------------------------------------------------
    # Numeric
    # --------------------------------------------------------

    behaviour_df[
        "vessel_behaviour_score"
    ] = pd.to_numeric(
        behaviour_df[
            "vessel_behaviour_score"
        ],
        errors="coerce"
    ).fillna(
        0.0
    )

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    behaviour_df = behaviour_df.dropna(
        subset=[
            "base_date_time",
            "latitude",
            "longitude"
        ]
    )

    return behaviour_df


# ============================================================
# FIND AIS EVENT CANDIDATES
# ============================================================

def find_event_candidates(
    df,
    max_distance_km=20.0,
    max_time_minutes=180.0
):

    rows = []

    for _, row in df.iterrows():

        distance = haversine_distance_km(

            SPILL_LATITUDE,

            SPILL_LONGITUDE,

            row[
                "latitude"
            ],

            row[
                "longitude"
            ]
        )

        time_difference = abs(
            (
                row[
                    "base_date_time"
                ]
                -
                SPILL_TIME
            ).total_seconds()
        ) / 60.0

        if (
            distance <= max_distance_km
            and
            time_difference <= max_time_minutes
        ):

            item = row.to_dict()

            item[
                "distance_km"
            ] = distance

            item[
                "time_difference_minutes"
            ] = time_difference

            rows.append(
                item
            )

    if not rows:

        return pd.DataFrame()

    return pd.DataFrame(
        rows
    )


# ============================================================
# CREATE ONE CANDIDATE PER VESSEL
# ============================================================

def create_vessel_candidates(
    event_df
):

    records = []

    for mmsi, group in event_df.groupby(
        "mmsi"
    ):

        group = group.sort_values(
            [
                "distance_km",
                "time_difference_minutes"
            ]
        )

        best = group.iloc[
            0
        ].copy()

        records.append(
            best
        )

    if not records:

        return pd.DataFrame()

    return pd.DataFrame(
        records
    ).reset_index(
        drop=True
    )


# ============================================================
# EVENT-TIME BEHAVIOUR
# ============================================================

def calculate_event_behaviour(
    vessel_mmsi,
    full_df
):

    vessel = full_df[
        full_df[
            "mmsi"
        ]
        ==
        vessel_mmsi
    ].copy()

    if vessel.empty:

        return {

            "event_behaviour_score":
                0.0,

            "event_behaviour_level":
                "LOW",

            "event_records":
                0,

            "event_average_speed":
                0.0,

            "event_stopped_percent":
                0.0,

            "event_average_course_change":
                0.0,

            "event_ais_gap_percent":
                0.0,

            "event_loitering_percent":
                0.0,

            "event_ml_anomaly_percent":
                0.0
        }

    vessel[
        "event_minutes"
    ] = (
        (
            vessel[
                "base_date_time"
            ]
            -
            SPILL_TIME
        )
        .abs()
        .dt.total_seconds()
        /
        60.0
    )

    event_window = vessel[
        vessel[
            "event_minutes"
        ]
        <= 30.0
    ].copy()

    if event_window.empty:

        return {

            "event_behaviour_score":
                0.0,

            "event_behaviour_level":
                "LOW",

            "event_records":
                0,

            "event_average_speed":
                0.0,

            "event_stopped_percent":
                0.0,

            "event_average_course_change":
                0.0,

            "event_ais_gap_percent":
                0.0,

            "event_loitering_percent":
                0.0,

            "event_ml_anomaly_percent":
                0.0
        }

    # --------------------------------------------------------
    # Safe numeric columns
    # --------------------------------------------------------

    def column_or_zero(
        name
    ):

        if name in event_window.columns:

            return pd.to_numeric(
                event_window[
                    name
                ],
                errors="coerce"
            ).fillna(
                0.0
            )

        return pd.Series(
            np.zeros(
                len(
                    event_window
                )
            ),
            index=event_window.index
        )

    sog = column_or_zero(
        "sog"
    )

    speed_change = column_or_zero(
        "speed_change"
    )

    course_change = column_or_zero(
        "course_change"
    )

    stopped = column_or_zero(
        "stopped"
    )

    ais_gap = column_or_zero(
        "ais_gap"
    )

    loitering = column_or_zero(
        "loitering"
    )

    # --------------------------------------------------------
    # ML anomaly
    # --------------------------------------------------------

    if (
        "behaviour_anomaly_score"
        in event_window.columns
    ):

        ml_anomaly = pd.to_numeric(
            event_window[
                "behaviour_anomaly_score"
            ],
            errors="coerce"
        ).fillna(
            0.0
        )

    elif (
        "anomaly_score"
        in event_window.columns
    ):

        raw = pd.to_numeric(
            event_window[
                "anomaly_score"
            ],
            errors="coerce"
        ).fillna(
            0.0
        )

        ml_anomaly = (
            raw.rank(
                pct=True
            )
            *
            100.0
        )

    else:

        ml_anomaly = pd.Series(
            np.zeros(
                len(
                    event_window
                )
            ),
            index=event_window.index
        )

    # --------------------------------------------------------
    # Event statistics
    # --------------------------------------------------------

    avg_speed = float(
        sog.mean()
    )

    stopped_percent = float(
        stopped.mean()
        *
        100.0
    )

    avg_course_change = float(
        course_change.mean()
    )

    ais_gap_percent = float(
        ais_gap.mean()
        *
        100.0
    )

    loitering_percent = float(
        loitering.mean()
        *
        100.0
    )

    ml_anomaly_percent = float(
        ml_anomaly.mean()
    )

    # --------------------------------------------------------
    # Individual signal scores
    # --------------------------------------------------------

    speed_change_score = clamp(
        speed_change.mean()
        *
        5.0
    )

    stop_score = clamp(
        stopped_percent
    )

    course_score = clamp(
        avg_course_change
        /
        90.0
        *
        100.0
    )

    gap_score = clamp(
        ais_gap_percent
    )

    loitering_score = clamp(
        loitering_percent
    )

    ml_score = clamp(
        ml_anomaly_percent
    )

    # --------------------------------------------------------
    # Event behaviour score
    # --------------------------------------------------------

    event_score = (

        0.15
        *
        speed_change_score

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

        0.15
        *
        loitering_score

        +

        0.20
        *
        ml_score
    )

    event_score = clamp(
        event_score
    )

    return {

        "event_behaviour_score":
            event_score,

        "event_behaviour_level":
            behaviour_level(
                event_score
            ),

        "event_records":
            len(
                event_window
            ),

        "event_average_speed":
            avg_speed,

        "event_stopped_percent":
            stopped_percent,

        "event_average_course_change":
            avg_course_change,

        "event_ais_gap_percent":
            ais_gap_percent,

        "event_loitering_percent":
            loitering_percent,

        "event_ml_anomaly_percent":
            ml_anomaly_percent
    }


# ============================================================
# COMBINE VESSEL + EVENT BEHAVIOUR
# ============================================================

def combine_behaviour_scores(
    vessel_score,
    event_score
):

    # Vessel-level historical behaviour:
    # 35%
    #
    # Event-time behaviour:
    # 65%

    return clamp(

        0.35
        *
        float(vessel_score)

        +

        0.65
        *
        float(event_score)
    )


# ============================================================
# FUSE VESSEL EVIDENCE
# ============================================================

def fuse_evidence(
    candidate,
    event_behaviour
):

    # --------------------------------------------------------
    # Spatial
    # --------------------------------------------------------

    distance = float(
        candidate[
            "distance_km"
        ]
    )

    spatial_score = calculate_spatial_score(
        distance
    )

    # --------------------------------------------------------
    # Temporal
    # --------------------------------------------------------

    time_difference = float(
        candidate[
            "time_difference_minutes"
        ]
    )

    temporal_score = calculate_temporal_score(
        time_difference
    )

    # --------------------------------------------------------
    # Behaviour
    # --------------------------------------------------------

    vessel_behaviour_score = (
        normalize_behaviour_score(
            candidate[
                "vessel_behaviour_score"
            ]
        )
    )

    event_behaviour_score = (
        normalize_behaviour_score(
            event_behaviour[
                "event_behaviour_score"
            ]
        )
    )

    combined_behaviour_score = (
        combine_behaviour_scores(

            vessel_behaviour_score,

            event_behaviour_score
        )
    )

    # --------------------------------------------------------
    # AIS confidence
    # --------------------------------------------------------

    ais_confidence_label = candidate.get(
        "vessel_data_confidence",
        "MEDIUM"
    )

    ais_confidence_score = (
        calculate_ais_confidence(
            ais_confidence_label
        )
    )

    # --------------------------------------------------------
    # VESSEL-SPECIFIC FINAL SCORE
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # U-Net confidence and false-positive score are NOT used
    # here because they are identical incident-level evidence
    # for all vessels.
    #
    # They are still reported separately below.
    #
    # --------------------------------------------------------

    final_score = (

        VESSEL_WEIGHTS[
            "spatial"
        ]
        *
        spatial_score

        +

        VESSEL_WEIGHTS[
            "temporal"
        ]
        *
        temporal_score

        +

        VESSEL_WEIGHTS[
            "behaviour"
        ]
        *
        combined_behaviour_score

        +

        VESSEL_WEIGHTS[
            "ais_confidence"
        ]
        *
        ais_confidence_score
    )

    final_score = clamp(
        final_score
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = {

        "MMSI":
            candidate[
                "mmsi"
            ],

        "vessel_name":
            candidate.get(
                "vessel_name",
                "UNKNOWN"
            ),

        "latitude":
            float(
                candidate[
                    "latitude"
                ]
            ),

        "longitude":
            float(
                candidate[
                    "longitude"
                ]
            ),

        # --------------------------------------------
        # Event relationship
        # --------------------------------------------

        "distance_km":
            distance,

        "time_difference_minutes":
            time_difference,

        # --------------------------------------------
        # Incident-level evidence
        # --------------------------------------------

        "unet_confidence":
            UNET_CONFIDENCE,

        "false_positive_score":
            FALSE_POSITIVE_SCORE,

        "probable_oil_category":
            SPECTRAL_CATEGORY,

        # --------------------------------------------
        # Vessel-level evidence
        # --------------------------------------------

        "spatial_score":
            spatial_score,

        "temporal_score":
            temporal_score,

        "vessel_behaviour_score":
            vessel_behaviour_score,

        "vessel_behaviour_level":
            behaviour_level(
                vessel_behaviour_score
            ),

        "event_behaviour_score":
            event_behaviour_score,

        "event_behaviour_level":
            event_behaviour[
                "event_behaviour_level"
            ],

        "combined_behaviour_score":
            combined_behaviour_score,

        # --------------------------------------------
        # Event signals
        # --------------------------------------------

        "event_records":
            event_behaviour[
                "event_records"
            ],

        "event_average_speed":
            event_behaviour[
                "event_average_speed"
            ],

        "event_stopped_percent":
            event_behaviour[
                "event_stopped_percent"
            ],

        "event_average_course_change":
            event_behaviour[
                "event_average_course_change"
            ],

        "event_ais_gap_percent":
            event_behaviour[
                "event_ais_gap_percent"
            ],

        "event_loitering_percent":
            event_behaviour[
                "event_loitering_percent"
            ],

        "event_ml_anomaly_percent":
            event_behaviour[
                "event_ml_anomaly_percent"
            ],

        # --------------------------------------------
        # AIS
        # --------------------------------------------

        "ais_confidence":
            str(
                ais_confidence_label
            ),

        "ais_confidence_score":
            ais_confidence_score,

        # --------------------------------------------
        # Spectral status
        # --------------------------------------------

        "spectral_available":
            False,

        # --------------------------------------------
        # Final
        # --------------------------------------------

        "investigation_priority_score":
            final_score,

        "priority_level":
            priority_level(
                final_score
            )
    }

    result[
        "reasons"
    ] = build_reasons(
        result
    )

    return result


# ============================================================
# RUN EVIDENCE FUSION
# ============================================================

def run_evidence_fusion():

    print(
        "\n======================================"
    )

    print(
        "        VESSEL-SPECIFIC FUSION"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Incident information
    # --------------------------------------------------------

    print(
        "\nINCIDENT-LEVEL EVIDENCE"
    )

    print(
        f"  U-Net confidence       : "
        f"{UNET_CONFIDENCE:.2f}%"
    )

    print(
        f"  False-positive score   : "
        f"{FALSE_POSITIVE_SCORE:.2f}%"
    )

    print(
        f"  Spectral category      : "
        f"{SPECTRAL_CATEGORY}"
    )

    # --------------------------------------------------------
    # Behaviour data
    # --------------------------------------------------------

    print(
        "\nLoading behaviour data..."
    )

    behaviour_df = load_behaviour_data()

    print(
        f"Behaviour records: "
        f"{len(behaviour_df):,}"
    )

    print(
        "\nLoading vessel-level behaviour..."
    )

    final_df = load_final_behaviour_data()

    if final_df is not None:

        print(
            f"Vessel-level records: "
            f"{len(final_df):,}"
        )

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    print(
        "\nPreparing AIS behaviour data..."
    )

    behaviour_df = prepare_behaviour_data(
        behaviour_df,
        final_df
    )

    # --------------------------------------------------------
    # Event candidates
    # --------------------------------------------------------

    print(
        "\nFinding AIS candidates..."
    )

    event_df = find_event_candidates(
        behaviour_df
    )

    print(
        f"Candidates within event window: "
        f"{len(event_df):,}"
    )

    if event_df.empty:

        print(
            "\nNo AIS candidates found."
        )

        return

    # --------------------------------------------------------
    # Unique vessels
    # --------------------------------------------------------

    vessel_df = create_vessel_candidates(
        event_df
    )

    print(
        f"Unique vessels: "
        f"{len(vessel_df):,}"
    )

    # --------------------------------------------------------
    # Calculate
    # --------------------------------------------------------

    results = []

    print(
        "\nCalculating vessel-specific evidence..."
    )

    for _, candidate in vessel_df.iterrows():

        event_behaviour = (
            calculate_event_behaviour(

                candidate[
                    "mmsi"
                ],

                behaviour_df
            )
        )

        result = fuse_evidence(

            candidate,

            event_behaviour
        )

        results.append(
            result
        )

    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    result_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    result_df = result_df.sort_values(
        "investigation_priority_score",
        ascending=False
    )

    result_df = result_df.reset_index(
        drop=True
    )

    result_df.insert(
        0,
        "rank",
        np.arange(
            1,
            len(result_df) + 1
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # TOP 10
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "      TOP INVESTIGATION TARGETS"
    )

    print(
        "======================================"
    )

    display_columns = [

        "rank",

        "MMSI",

        "vessel_name",

        "distance_km",

        "time_difference_minutes",

        "spatial_score",

        "temporal_score",

        "vessel_behaviour_score",

        "event_behaviour_score",

        "combined_behaviour_score",

        "ais_confidence",

        "investigation_priority_score",

        "priority_level"
    ]

    available_columns = [

        column
        for column
        in display_columns
        if column
        in result_df.columns
    ]

    print(
        result_df[
            available_columns
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    # ========================================================
    # TOP CANDIDATE
    # ========================================================

    if not result_df.empty:

        top = result_df.iloc[
            0
        ]

        print(
            "\n======================================"
        )

        print(
            "      TOP CANDIDATE EVIDENCE"
        )

        print(
            "======================================"
        )

        print(
            f"\nRank                    : "
            f"{int(top['rank'])}"
        )

        print(
            f"MMSI                    : "
            f"{top['MMSI']}"
        )

        print(
            f"Vessel                  : "
            f"{top['vessel_name']}"
        )

        print(
            f"\nDistance                : "
            f"{top['distance_km']:.3f} km"
        )

        print(
            f"Time difference         : "
            f"{top['time_difference_minutes']:.2f} min"
        )

        print(
            "\n--------------------------------------"
        )

        print(
            "INCIDENT EVIDENCE"
        )

        print(
            "--------------------------------------"
        )

        print(
            f"U-Net confidence        : "
            f"{top['unet_confidence']:.2f}%"
        )

        print(
            f"False-positive score    : "
            f"{top['false_positive_score']:.2f}%"
        )

        print(
            f"Spectral category       : "
            f"{top['probable_oil_category']}"
        )

        print(
            "\n--------------------------------------"
        )

        print(
            "VESSEL EVIDENCE"
        )

        print(
            "--------------------------------------"
        )

        print(
            f"Spatial score           : "
            f"{top['spatial_score']:.2f}"
        )

        print(
            f"Temporal score          : "
            f"{top['temporal_score']:.2f}"
        )

        print(
            f"Vessel behaviour       : "
            f"{top['vessel_behaviour_score']:.2f}"
        )

        print(
            f"Vessel behaviour level : "
            f"{top['vessel_behaviour_level']}"
        )

        print(
            f"Event behaviour        : "
            f"{top['event_behaviour_score']:.2f}"
        )

        print(
            f"Event behaviour level  : "
            f"{top['event_behaviour_level']}"
        )

        print(
            f"Combined behaviour     : "
            f"{top['combined_behaviour_score']:.2f}"
        )

        print(
            f"AIS confidence         : "
            f"{top['ais_confidence']}"
        )

        print(
            "\n--------------------------------------"
        )

        print(
            "EVENT SIGNALS"
        )

        print(
            "--------------------------------------"
        )

        print(
            f"AIS records             : "
            f"{int(top['event_records'])}"
        )

        print(
            f"Average speed           : "
            f"{top['event_average_speed']:.2f}"
        )

        print(
            f"Stopped percentage      : "
            f"{top['event_stopped_percent']:.2f}%"
        )

        print(
            f"Course change           : "
            f"{top['event_average_course_change']:.2f}"
        )

        print(
            f"AIS gap percentage      : "
            f"{top['event_ais_gap_percent']:.2f}%"
        )

        print(
            f"Loitering percentage    : "
            f"{top['event_loitering_percent']:.2f}%"
        )

        print(
            f"ML anomaly              : "
            f"{top['event_ml_anomaly_percent']:.2f}"
        )

        print(
            "\n--------------------------------------"
        )

        print(
            "FINAL INVESTIGATION RESULT"
        )

        print(
            "--------------------------------------"
        )

        print(
            f"\nInvestigation score    : "
            f"{top['investigation_priority_score']:.2f}"
        )

        print(
            f"Priority level          : "
            f"{top['priority_level']}"
        )

        print(
            "\nEvidence reasons:"
        )

        for reason in top[
            "reasons"
        ]:

            print(
                f"  - {reason}"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "       EVIDENCE FUSION COMPLETE"
    )

    print(
        "======================================"
    )

    print(
        f"\nResults saved to:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        "\nImportant:"
    )

    print(
        "The investigation score is a prioritization "
        "score, not a causation or guilt score."
    )

    print(
        "======================================"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_evidence_fusion()