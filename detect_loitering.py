import pandas as pd
import numpy as np

INPUT_FILE = "ais/data/vessel_trajectories.csv"
OUTPUT_FILE = "ais/data/vessel_behaviour_features.csv"

print("=" * 60)
print("IMPROVED LOITERING DETECTION")
print("=" * 60)

print("\nLoading trajectory data...")

df = pd.read_csv(INPUT_FILE)

print("Rows loaded:", len(df))

# ---------------------------------------------------------
# Clean data
# ---------------------------------------------------------

numeric_columns = [
    "sog",
    "distance_km",
    "time_difference_minutes",
    "speed_change",
    "course_change"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

# ---------------------------------------------------------
# Identify stopped vessels
# ---------------------------------------------------------

# SOG <= 0.5 knots = essentially stopped
df["stopped"] = (df["sog"] <= 0.5).astype(int)

# ---------------------------------------------------------
# Improved loitering logic
# ---------------------------------------------------------
#
# A vessel is NOT considered loitering simply because
# it is stopped.
#
# We require:
#
# 1. Low/moderate speed
# 2. Vessel is actually moving around its area
# 3. Course changes are occurring
# 4. Multiple observations exist
#
# This reduces docked/anchored vessels being automatically
# classified as loitering.
# ---------------------------------------------------------

df["slow_movement"] = (df["sog"] > 0.5) & (df["sog"] <= 5.0)

df["course_change_signal"] = (
    df["course_change"] >= 20
).astype(int)

df["movement_signal"] = (
    df["distance_km"] > 0.05
).astype(int)

df["loitering"] = (
    (df["slow_movement"]) &
    (df["course_change_signal"] == 1) &
    (df["movement_signal"] == 1)
).astype(int)

# ---------------------------------------------------------
# AIS gap
# ---------------------------------------------------------

df["ais_gap"] = (
    df["time_difference_minutes"] > 10
).astype(int)

# ---------------------------------------------------------
# Remove temporary columns
# ---------------------------------------------------------

df.drop(
    columns=[
        "slow_movement",
        "course_change_signal",
        "movement_signal"
    ],
    inplace=True
)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("LOITERING DETECTION COMPLETE")
print("=" * 60)

print("\nRows:", len(df))

print(
    "Stopped points:",
    int(df["stopped"].sum())
)

print(
    "Potential loitering points:",
    int(df["loitering"].sum())
)

print(
    "Loitering percentage:",
    round(df["loitering"].mean() * 100, 2),
    "%"
)

print("\nSaved to:")
print(OUTPUT_FILE)