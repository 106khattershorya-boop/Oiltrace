import pandas as pd
import numpy as np


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "data/ais_processed_sample.csv"
OUTPUT_FILE = "data/vessel_trajectories.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("VESSEL TRAJECTORY CREATION")
print("=" * 60)

print("\nLoading processed AIS data...")

df = pd.read_csv(INPUT_FILE)


# ============================================================
# CONVERT TIMESTAMP
# ============================================================

df["base_date_time"] = pd.to_datetime(
    df["base_date_time"]
)


# ============================================================
# SORT
# ============================================================

print("Sorting vessel positions...")

df = df.sort_values(
    ["mmsi", "base_date_time"]
).reset_index(drop=True)


# ============================================================
# PREVIOUS POSITION
# ============================================================

print("Calculating previous vessel positions...")

df["previous_latitude"] = (
    df.groupby("mmsi")["latitude"].shift(1)
)

df["previous_longitude"] = (
    df.groupby("mmsi")["longitude"].shift(1)
)

df["previous_time"] = (
    df.groupby("mmsi")["base_date_time"].shift(1)
)

df["previous_sog"] = (
    df.groupby("mmsi")["sog"].shift(1)
)

df["previous_cog"] = (
    df.groupby("mmsi")["cog"].shift(1)
)


# ============================================================
# TIME DIFFERENCE
# ============================================================

df["time_difference_minutes"] = (
    (
        df["base_date_time"]
        - df["previous_time"]
    ).dt.total_seconds()
    / 60
)


# ============================================================
# DISTANCE USING HAVERSINE
# ============================================================

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        *
        np.cos(lat2)
        *
        np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(
        np.sqrt(a)
    )

    return R * c


print("Calculating distance travelled...")

df["distance_km"] = haversine_distance(
    df["previous_latitude"],
    df["previous_longitude"],
    df["latitude"],
    df["longitude"]
)


# ============================================================
# SPEED CHANGE
# ============================================================

df["speed_change"] = (
    df["sog"]
    -
    df["previous_sog"]
)


# ============================================================
# COURSE CHANGE
# ============================================================

course_difference = (
    df["cog"]
    -
    df["previous_cog"]
).abs()

df["course_change"] = np.minimum(
    course_difference,
    360 - course_difference
)


# ============================================================
# STOP DETECTION
# ============================================================

df["stopped"] = (
    df["sog"].fillna(0) <= 0.5
).astype(int)


# ============================================================
# AIS GAP
# ============================================================

df["ais_gap"] = (
    df["time_difference_minutes"]
    > 10
).astype(int)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 60)
print("TRAJECTORY CREATION COMPLETE")
print("=" * 60)

print("\nRows:", len(df))

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nNew trajectory features:")

print(
    df[
        [
            "mmsi",
            "base_date_time",
            "latitude",
            "longitude",
            "sog",
            "cog",
            "distance_km",
            "speed_change",
            "course_change",
            "stopped",
            "ais_gap"
        ]
    ]
    .head(15)
    .to_string(index=False)
)