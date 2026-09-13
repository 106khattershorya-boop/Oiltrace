# ============================================================
# VESSEL ATTRIBUTION
# ============================================================
#
# SIH 26143
#
# Match AIS vessels with a detected spill event using:
#   1. Spatial proximity
#   2. Temporal proximity
#   3. Behaviour anomaly
#   4. AIS data confidence
#
# Then rank vessels for investigation.
#
# IMPORTANT:
# This system ranks vessels for investigation.
# It does NOT determine guilt or prove responsibility.
#
# ============================================================

import os
import sys
import math

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# CURRENT_DIR = ...\sih26143\ais
AIS_DIR = CURRENT_DIR

# ...\sih26143
PROJECT_ROOT = os.path.dirname(
    AIS_DIR
)

DATA_DIR = os.path.join(
    AIS_DIR,
    "data"
)


# ============================================================
# DATA PATHS
# ============================================================

AIS_FILE = os.path.join(
    DATA_DIR,
    "ais_processed_sample.csv"
)

BEHAVIOUR_FILE = os.path.join(
    DATA_DIR,
    "final_behaviour_scores.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "vessel_attribution_results.csv"
)


# ============================================================
# ML RANKING PATH
# ============================================================

ML_SRC_DIR = os.path.join(
    PROJECT_ROOT,
    "ml",
    "src"
)

if ML_SRC_DIR not in sys.path:

    sys.path.insert(
        0,
        ML_SRC_DIR
    )

from investigation_ranking import rank_vessel


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate distance between two coordinates.

    Returns distance in kilometres.
    """

    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

    except Exception:

        return np.nan

    earth_radius = 6371.0

    lat1_rad = math.radians(
        lat1
    )

    lat2_rad = math.radians(
        lat2
    )

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(
            delta_lat / 2
        ) ** 2

        +

        math.cos(
            lat1_rad
        )
        *
        math.cos(
            lat2_rad
        )
        *
        math.sin(
            delta_lon / 2
        ) ** 2
    )

    c = (
        2.0
        *
        math.atan2(
            math.sqrt(a),
            math.sqrt(1.0 - a)
        )
    )

    return earth_radius * c


# ============================================================
# LOAD AIS DATA
# ============================================================

def load_ais_data():

    print(
        "AIS file found:"
    )

    print(
        AIS_FILE
    )

    if not os.path.exists(
        AIS_FILE
    ):

        raise FileNotFoundError(
            "\nAIS file not found:\n"
            f"{AIS_FILE}"
        )

    dataframe = pd.read_csv(
        AIS_FILE
    )

    print(
        f"AIS records loaded: "
        f"{len(dataframe)}"
    )

    return dataframe


# ============================================================
# LOAD BEHAVIOUR DATA
# ============================================================

def load_behaviour_data():

    if not os.path.exists(
        BEHAVIOUR_FILE
    ):

        raise FileNotFoundError(
            "\nBehaviour file not found:\n"
            f"{BEHAVIOUR_FILE}\n\n"
            "Run this first:\n"
            "python ais\\final_behaviour_score.py"
        )

    dataframe = pd.read_csv(
        BEHAVIOUR_FILE
    )

    print(
        f"Behaviour records loaded: "
        f"{len(dataframe)}"
    )

    return dataframe


# ============================================================
# NORMALIZE MMSI
# ============================================================

def normalize_mmsi(
    dataframe,
    column="mmsi"
):

    dataframe = dataframe.copy()

    if column not in dataframe.columns:

        return dataframe

    dataframe[column] = (
        dataframe[column]
        .astype(str)
        .str.strip()
        .str.replace(
            ".0",
            "",
            regex=False
        )
    )

    return dataframe


# ============================================================
# PREPARE AIS DATA
# ============================================================

def prepare_ais_data(
    dataframe
):

    dataframe = dataframe.copy()

    required_columns = [
        "mmsi",
        "latitude",
        "longitude",
        "base_date_time"
    ]

    for column in required_columns:

        if column not in dataframe.columns:

            raise ValueError(
                f"Required AIS column missing: "
                f"{column}"
            )

    dataframe = normalize_mmsi(
        dataframe,
        "mmsi"
    )

    dataframe["latitude"] = pd.to_numeric(
        dataframe["latitude"],
        errors="coerce"
    )

    dataframe["longitude"] = pd.to_numeric(
        dataframe["longitude"],
        errors="coerce"
    )

    dataframe["base_date_time"] = (
        pd.to_datetime(
            dataframe["base_date_time"],
            errors="coerce"
        )
    )

    dataframe = dataframe.dropna(
        subset=[
            "mmsi",
            "latitude",
            "longitude",
            "base_date_time"
        ]
    )

    return dataframe


# ============================================================
# PREPARE BEHAVIOUR DATA
# ============================================================

def prepare_behaviour_data(
    dataframe
):

    dataframe = dataframe.copy()

    if "mmsi" not in dataframe.columns:

        raise ValueError(
            "Behaviour file does not contain MMSI."
        )

    if "behaviour_score" not in dataframe.columns:

        raise ValueError(
            "Behaviour file does not contain "
            "'behaviour_score'."
        )

    dataframe = normalize_mmsi(
        dataframe,
        "mmsi"
    )

    dataframe["behaviour_score"] = (
        pd.to_numeric(
            dataframe["behaviour_score"],
            errors="coerce"
        )
        .fillna(
            0.0
        )
    )

    if "behaviour_level" not in dataframe.columns:

        dataframe["behaviour_level"] = (
            "VERY_LOW_ANOMALY"
        )

    if "data_confidence" not in dataframe.columns:

        dataframe["data_confidence"] = "LOW"

    # --------------------------------------------------------
    # One behaviour record per MMSI
    # --------------------------------------------------------

    dataframe = (
        dataframe
        .sort_values(
            by="behaviour_score",
            ascending=False
        )
        .drop_duplicates(
            subset=["mmsi"],
            keep="first"
        )
        .reset_index(
            drop=True
        )
    )

    return dataframe


# ============================================================
# SPATIAL CANDIDATES
# ============================================================

def find_spatial_candidates(
    ais,
    spill_lat,
    spill_lon,
    radius_km
):

    print(
        f"\nSearching for vessels within "
        f"{radius_km} km..."
    )

    ais = ais.copy()

    # --------------------------------------------------------
    # Vectorized Haversine
    # --------------------------------------------------------

    lat1 = np.radians(
        float(spill_lat)
    )

    lat2 = np.radians(
        ais["latitude"]
    )

    delta_lat = np.radians(
        ais["latitude"]
        -
        float(spill_lat)
    )

    delta_lon = np.radians(
        ais["longitude"]
        -
        float(spill_lon)
    )

    a = (
        np.sin(
            delta_lat / 2
        ) ** 2

        +

        np.cos(
            lat1
        )
        *
        np.cos(
            lat2
        )
        *
        np.sin(
            delta_lon / 2
        ) ** 2
    )

    c = (
        2.0
        *
        np.arctan2(
            np.sqrt(a),
            np.sqrt(
                1.0 - a
            )
        )
    )

    ais["distance_km"] = (
        6371.0
        *
        c
    )

    candidates = ais[
        ais["distance_km"]
        <=
        float(radius_km)
    ].copy()

    print(
        f"Vessels within {radius_km} km: "
        f"{candidates['mmsi'].nunique()}"
    )

    return candidates


# ============================================================
# TIME DIFFERENCE
# ============================================================

def calculate_time_difference(
    dataframe,
    spill_time
):

    dataframe = dataframe.copy()

    spill_time = pd.to_datetime(
        spill_time
    )

    dataframe[
        "time_difference_minutes"
    ] = (
        (
            dataframe[
                "base_date_time"
            ]
            -
            spill_time
        )
        .dt
        .total_seconds()
        .abs()
        /
        60.0
    )

    return dataframe


# ============================================================
# TIME FILTER
# ============================================================

def filter_time_window(
    dataframe,
    time_window_minutes
):

    candidates = dataframe[
        dataframe[
            "time_difference_minutes"
        ]
        <=
        float(time_window_minutes)
    ].copy()

    print(
        f"Vessels within "
        f"{time_window_minutes} minutes: "
        f"{candidates['mmsi'].nunique()}"
    )

    return candidates


# ============================================================
# BEST RECORD PER VESSEL
# ============================================================

def select_best_vessel_records(
    dataframe
):

    if dataframe.empty:

        return dataframe

    dataframe = dataframe.sort_values(
        by=[
            "mmsi",
            "time_difference_minutes",
            "distance_km"
        ],
        ascending=[
            True,
            True,
            True
        ]
    )

    best_records = (
        dataframe
        .groupby(
            "mmsi",
            as_index=False
        )
        .first()
    )

    return best_records


# ============================================================
# MERGE BEHAVIOUR
# ============================================================

def merge_behaviour(
    candidates,
    behaviour
):

    candidates = candidates.copy()

    behaviour = behaviour.copy()

    candidates = normalize_mmsi(
        candidates,
        "mmsi"
    )

    behaviour = normalize_mmsi(
        behaviour,
        "mmsi"
    )

    behaviour_columns = [
        "mmsi",
        "behaviour_score",
        "behaviour_level",
        "data_confidence"
    ]

    existing_columns = [
        column
        for column
        in behaviour_columns
        if column in behaviour.columns
    ]

    behaviour_subset = (
        behaviour[
            existing_columns
        ]
        .copy()
    )

    merged = candidates.merge(
        behaviour_subset,
        on="mmsi",
        how="left"
    )

    merged[
        "behaviour_score"
    ] = (
        pd.to_numeric(
            merged[
                "behaviour_score"
            ],
            errors="coerce"
        )
        .fillna(
            0.0
        )
    )

    merged[
        "behaviour_level"
    ] = (
        merged[
            "behaviour_level"
        ]
        .fillna(
            "VERY_LOW_ANOMALY"
        )
    )

    merged[
        "data_confidence"
    ] = (
        merged[
            "data_confidence"
        ]
        .fillna(
            "LOW"
        )
    )

    return merged


# ============================================================
# CALCULATE RANKINGS
# ============================================================

def calculate_rankings(
    dataframe,
    radius_km,
    time_window_minutes
):

    results = []

    for _, row in dataframe.iterrows():

        mmsi = row["mmsi"]

        distance = float(
            row["distance_km"]
        )

        time_difference = float(
            row[
                "time_difference_minutes"
            ]
        )

        behaviour_score = float(
            row[
                "behaviour_score"
            ]
        )

        data_confidence = (
            row[
                "data_confidence"
            ]
        )

        latitude = row.get(
            "latitude",
            np.nan
        )

        longitude = row.get(
            "longitude",
            np.nan
        )

        speed = row.get(
            "sog",
            np.nan
        )

        course = row.get(
            "cog",
            np.nan
        )

        ranked = rank_vessel(

            mmsi=mmsi,

            distance_km=distance,

            time_difference_minutes=
                time_difference,

            behaviour_score=
                behaviour_score,

            data_confidence=
                data_confidence,

            latitude=
                latitude,

            longitude=
                longitude,

            speed=
                speed,

            course=
                course,

            max_distance_km=
                radius_km,

            max_time_minutes=
                time_window_minutes
        )

        # ----------------------------------------------------
        # Vessel metadata
        # ----------------------------------------------------

        ranked[
            "vessel_name"
        ] = row.get(
            "vessel_name",
            np.nan
        )

        ranked[
            "vessel_type"
        ] = row.get(
            "vessel_type",
            np.nan
        )

        ranked[
            "imo"
        ] = row.get(
            "imo",
            np.nan
        )

        ranked[
            "call_sign"
        ] = row.get(
            "call_sign",
            np.nan
        )

        ranked[
            "cargo"
        ] = row.get(
            "cargo",
            np.nan
        )

        ranked[
            "ais_timestamp"
        ] = row.get(
            "base_date_time",
            np.nan
        )

        ranked[
            "behaviour_level"
        ] = row.get(
            "behaviour_level",
            "VERY_LOW_ANOMALY"
        )

        results.append(
            ranked
        )

    if not results:

        return pd.DataFrame()

    results_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    results_df = results_df.sort_values(
        by=[
            "investigation_priority_score",
            "behaviour_score",
            "time_difference_minutes",
            "distance_km"
        ],
        ascending=[
            False,
            False,
            True,
            True
        ]
    ).reset_index(
        drop=True
    )

    results_df[
        "investigation_rank"
    ] = (
        results_df.index
        +
        1
    )

    return results_df


# ============================================================
# MAIN ATTRIBUTION FUNCTION
# ============================================================

def attribute_vessels(
    spill_lat,
    spill_lon,
    spill_time,
    radius_km=20,
    time_window_minutes=180
):
    """
    Match vessels against a spill event.

    Parameters:
        spill_lat
        spill_lon
        spill_time
        radius_km
        time_window_minutes

    Returns:
        pandas.DataFrame
    """

    # ========================================================
    # LOAD AIS
    # ========================================================

    ais = load_ais_data()

    # ========================================================
    # PREPARE AIS
    # ========================================================

    ais = prepare_ais_data(
        ais
    )

    # ========================================================
    # LOAD BEHAVIOUR
    # ========================================================

    behaviour = load_behaviour_data()

    # ========================================================
    # PREPARE BEHAVIOUR
    # ========================================================

    behaviour = prepare_behaviour_data(
        behaviour
    )

    # ========================================================
    # SPATIAL FILTER
    # ========================================================

    candidates = find_spatial_candidates(

        ais,

        spill_lat,

        spill_lon,

        radius_km
    )

    if candidates.empty:

        print(
            "\nNo vessels found within "
            "the spatial radius."
        )

        return pd.DataFrame()

    # ========================================================
    # TEMPORAL FILTER
    # ========================================================

    candidates = calculate_time_difference(

        candidates,

        spill_time
    )

    candidates = filter_time_window(

        candidates,

        time_window_minutes
    )

    if candidates.empty:

        print(
            "\nNo vessels found within "
            "the time window."
        )

        return pd.DataFrame()

    # ========================================================
    # BEST RECORD PER VESSEL
    # ========================================================

    candidates = select_best_vessel_records(
        candidates
    )

    # ========================================================
    # MERGE BEHAVIOUR
    # ========================================================

    candidates = merge_behaviour(

        candidates,

        behaviour
    )

    # ========================================================
    # CALCULATE INVESTIGATION RANKING
    # ========================================================

    results = calculate_rankings(

        candidates,

        radius_km,

        time_window_minutes
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # RETURN
    # ========================================================

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    results,
    top_n=10
):

    print(
        "\n======================================"
    )

    print(
        "        VESSEL ATTRIBUTION"
    )

    print(
        "======================================"
    )

    if results is None:

        print(
            "\nNo results."
        )

        return

    if results.empty:

        print(
            "\nNo candidate vessels found."
        )

        return

    top_results = results.head(
        top_n
    )

    for index, (_, row) in enumerate(
        top_results.iterrows(),
        start=1
    ):

        print(
            f"\n#{index}"
        )

        print(
            f"MMSI: "
            f"{row.get('MMSI', 'N/A')}"
        )

        vessel_name = row.get(
            "vessel_name",
            None
        )

        if (
            vessel_name is not None
            and
            str(vessel_name) != "nan"
        ):

            print(
                f"Vessel name: "
                f"{vessel_name}"
            )

        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        try:

            print(
                f"Distance: "
                f"{float(row['distance_km']):.3f} km"
            )

        except Exception:

            print(
                f"Distance: "
                f"{row.get('distance_km', 'N/A')}"
            )

        # ----------------------------------------------------
        # Time
        # ----------------------------------------------------

        try:

            print(
                f"Time difference: "
                f"{float(row['time_difference_minutes']):.2f} min"
            )

        except Exception:

            print(
                f"Time difference: "
                f"{row.get('time_difference_minutes', 'N/A')}"
            )

        # ----------------------------------------------------
        # Behaviour
        # ----------------------------------------------------

        try:

            print(
                f"Behaviour score: "
                f"{float(row['behaviour_score']):.2f}"
            )

        except Exception:

            print(
                f"Behaviour score: "
                f"{row.get('behaviour_score', 'N/A')}"
            )

        print(
            f"Behaviour level: "
            f"{row.get('behaviour_level', 'N/A')}"
        )

        print(
            f"Data confidence: "
            f"{row.get('data_confidence', 'N/A')}"
        )

        # ----------------------------------------------------
        # Investigation
        # ----------------------------------------------------

        try:

            print(
                f"Investigation score: "
                f"{float(row['investigation_priority_score']):.2f}"
            )

        except Exception:

            print(
                f"Investigation score: "
                f"{row.get('investigation_priority_score', 'N/A')}"
            )

        print(
            f"Priority: "
            f"{row.get('priority_level', 'N/A')}"
        )

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        print(
            f"Location: "
            f"{row.get('latitude', 'N/A')}, "
            f"{row.get('longitude', 'N/A')}"
        )

        print(
            f"Speed: "
            f"{row.get('sog', 'N/A')}"
        )

        print(
            f"Course: "
            f"{row.get('cog', 'N/A')}"
        )

        # ----------------------------------------------------
        # Evidence
        # ----------------------------------------------------

        reasons = row.get(
            "reasons",
            []
        )

        print(
            "Evidence:"
        )

        if isinstance(
            reasons,
            (list, tuple)
        ):

            for reason in reasons:

                print(
                    f"  - {reason}"
                )

        elif (
            reasons is not None
            and
            str(reasons) != "nan"
        ):

            print(
                f"  - {reasons}"
            )

    print(
        "\n======================================"
    )

    print(
        f"Displayed top "
        f"{len(top_results)} vessels."
    )

    print(
        "======================================"
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n======================================"
    )

    print(
        "     VESSEL ATTRIBUTION TEST"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Load AIS
    # --------------------------------------------------------

    ais_test = load_ais_data()

    ais_test = prepare_ais_data(
        ais_test
    )

    if ais_test.empty:

        raise ValueError(
            "AIS dataset is empty."
        )

    # --------------------------------------------------------
    # First real AIS record as simulated spill event
    # --------------------------------------------------------

    test_record = (
        ais_test.iloc[0]
    )

    spill_lat = float(
        test_record[
            "latitude"
        ]
    )

    spill_lon = float(
        test_record[
            "longitude"
        ]
    )

    spill_time = (
        test_record[
            "base_date_time"
        ]
    )

    print(
        "\nUsing a REAL AIS record "
        "as the simulated spill event:"
    )

    print(
        f"\nSpill latitude : "
        f"{spill_lat}"
    )

    print(
        f"Spill longitude: "
        f"{spill_lon}"
    )

    print(
        f"Spill time     : "
        f"{spill_time}"
    )

    print(
        "\nSearch radius: 20 km"
    )

    print(
        "Time window: 180 minutes"
    )

    # --------------------------------------------------------
    # Run attribution
    # --------------------------------------------------------

    results = attribute_vessels(

        spill_lat,

        spill_lon,

        spill_time,

        radius_km=20,

        time_window_minutes=180
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    display_results(
        results,
        top_n=10
    )

    print(
        "\nResults saved:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\n======================================"
    )

    print(
        "         TEST COMPLETED"
    )

    print(
        "======================================"
    )