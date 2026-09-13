import os
import pandas as pd


# ============================================================
# FILE PATHS
# ============================================================

INPUT_FILE = "ais/data/behaviour_anomaly_results.csv"
OUTPUT_FILE = "ais/data/vessel_level_features.csv"


print("=" * 60)
print("VESSEL-LEVEL BEHAVIOUR FEATURES")
print("=" * 60)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading anomaly results...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}\n\n"
        "Run train_behaviour_model.py first."
    )

df = pd.read_csv(INPUT_FILE)

print("Rows loaded:", len(df))


# ============================================================
# CLEAN NUMERIC DATA
# ============================================================

numeric_columns = [
    "sog",
    "speed_change",
    "course_change",
    "distance_km",
    "stopped",
    "ais_gap",
    "loitering",
    "behaviour_anomaly_score"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


# ============================================================
# VESSEL-LEVEL AGGREGATION
# ============================================================

print("\nAggregating vessel behaviour...")

vessel_features = df.groupby("mmsi").agg(

    observation_count=(
        "mmsi",
        "count"
    ),

    average_speed=(
        "sog",
        "mean"
    ),

    maximum_speed=(
        "sog",
        "max"
    ),

    minimum_speed=(
        "sog",
        "min"
    ),

    speed_variability=(
        "sog",
        "std"
    ),

    average_speed_change=(
        "speed_change",
        "mean"
    ),

    maximum_speed_change=(
        "speed_change",
        "max"
    ),

    average_course_change=(
        "course_change",
        "mean"
    ),

    maximum_course_change=(
        "course_change",
        "max"
    ),

    stop_fraction=(
        "stopped",
        "mean"
    ),

    ais_gap_fraction=(
        "ais_gap",
        "mean"
    ),

    loitering_fraction=(
        "loitering",
        "mean"
    ),

    average_anomaly_score=(
        "behaviour_anomaly_score",
        "mean"
    ),

    maximum_anomaly_score=(
        "behaviour_anomaly_score",
        "max"
    )
).reset_index()


# ============================================================
# HANDLE MISSING VALUES
# ============================================================

vessel_features["speed_variability"] = (
    vessel_features["speed_variability"]
    .fillna(0)
)


# ============================================================
# CONVERT FRACTIONS TO PERCENTAGES
# ============================================================

vessel_features["stop_percentage"] = (
    vessel_features["stop_fraction"] * 100
)

vessel_features["ais_gap_percentage"] = (
    vessel_features["ais_gap_fraction"] * 100
)

vessel_features["loitering_percentage"] = (
    vessel_features["loitering_fraction"] * 100
)


# ============================================================
# ROUND VALUES
# ============================================================

numeric_output_columns = [
    "average_speed",
    "maximum_speed",
    "minimum_speed",
    "speed_variability",
    "average_speed_change",
    "maximum_speed_change",
    "average_course_change",
    "maximum_course_change",
    "stop_fraction",
    "ais_gap_fraction",
    "loitering_fraction",
    "average_anomaly_score",
    "maximum_anomaly_score",
    "stop_percentage",
    "ais_gap_percentage",
    "loitering_percentage"
]

vessel_features[numeric_output_columns] = (
    vessel_features[numeric_output_columns]
    .round(2)
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

vessel_features.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("VESSEL-LEVEL FEATURES COMPLETE")
print("=" * 60)

print(
    "\nUnique vessels:",
    len(vessel_features)
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nTop vessels by average anomaly score:")

top = vessel_features.sort_values(
    "average_anomaly_score",
    ascending=False
).head(10)

print(
    top[
        [
            "mmsi",
            "observation_count",
            "average_speed",
            "average_speed_change",
            "average_course_change",
            "stop_percentage",
            "ais_gap_percentage",
            "loitering_percentage",
            "average_anomaly_score"
        ]
    ].to_string(index=False)
)