import os
import pandas as pd
import numpy as np


AIS_FILE = "ais/data/ais_processed_sample.csv"


def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate distance between two geographic points.

    Returns distance in kilometres.
    """

    R = 6371.0

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    delta_lat = np.radians(
        lat2 - lat1
    )

    delta_lon = np.radians(
        lon2 - lon1
    )

    a = (
        np.sin(delta_lat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    c = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a)
    )

    return R * c


def load_ais_data():

    if not os.path.exists(AIS_FILE):

        raise FileNotFoundError(
            f"AIS file not found:\n{AIS_FILE}"
        )

    df = pd.read_csv(
        AIS_FILE
    )

    # Remove accidental spaces
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    print(
        f"Loaded {len(df)} AIS records."
    )

    return df


def find_nearby_vessels(
    spill_lat,
    spill_lon,
    radius_km=20
):
    """
    Find AIS vessel positions within
    radius_km of a detected spill.
    """

    df = load_ais_data()

    required = [
        "latitude",
        "longitude"
    ]

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing AIS columns: {missing}\n"
            f"Available columns: "
            f"{df.columns.tolist()}"
        )

    # Remove invalid coordinates
    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    # Calculate distance
    df["distance_km"] = haversine_distance(
        spill_lat,
        spill_lon,
        df["latitude"],
        df["longitude"]
    )

    nearby = df[
        df["distance_km"] <= radius_km
    ].copy()

    nearby = nearby.sort_values(
        "distance_km"
    )

    return nearby


def rank_vessels(
    spill_lat,
    spill_lon,
    radius_km=20,
    limit=10
):
    """
    Find vessels near the detected
    spill location.
    """

    nearby = find_nearby_vessels(
        spill_lat,
        spill_lon,
        radius_km
    )

    if nearby.empty:

        return []

    if "mmsi" not in nearby.columns:

        raise ValueError(
            "MMSI column not found."
        )

    results = []

    # Keep only unique vessels
    # so the same vessel isn't repeated
    # unnecessarily.
    nearby = nearby.drop_duplicates(
        subset=["mmsi"]
    )

    nearby = nearby.sort_values(
        "distance_km"
    )

    for _, row in nearby.head(
        limit
    ).iterrows():

        vessel = {

            "MMSI":
                str(row["mmsi"]),

            "latitude":
                float(row["latitude"]),

            "longitude":
                float(row["longitude"]),

            "distance_km":
                round(
                    float(
                        row["distance_km"]
                    ),
                    3
                )
        }

        if "sog" in nearby.columns:

            vessel["speed"] = float(
                row["sog"]
            )

        if "cog" in nearby.columns:

            vessel["course"] = float(
                row["cog"]
            )

        if "base_date_time" in nearby.columns:

            vessel["timestamp"] = str(
                row["base_date_time"]
            )

        results.append(
            vessel
        )

    return results


if __name__ == "__main__":

    print(
        "\n================================"
    )

    print(
        "  VESSEL SPATIAL MATCHING TEST"
    )

    print(
        "================================\n"
    )

    # Load real AIS data
    df = load_ais_data()

    # Select the first valid AIS position
    sample = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    ).iloc[0]

    # Use a REAL AIS position as the
    # temporary spill location.
    spill_lat = float(
        sample["latitude"]
    )

    spill_lon = float(
        sample["longitude"]
    )

    print(
        "Using a real AIS position as "
        "the test spill location:\n"
    )

    print(
        f"Latitude : {spill_lat}"
    )

    print(
        f"Longitude: {spill_lon}"
    )

    print(
        "Radius   : 20 km\n"
    )

    # Find nearby vessels
    vessels = rank_vessels(
        spill_lat,
        spill_lon,
        radius_km=20,
        limit=10
    )

    if not vessels:

        print(
            "No vessels found within 20 km."
        )

    else:

        print(
            f"Found {len(vessels)} "
            "nearby vessels:\n"
        )

        for vessel in vessels:

            print(
                f"MMSI      : "
                f"{vessel['MMSI']}"
            )

            print(
                f"Distance  : "
                f"{vessel['distance_km']} km"
            )

            print(
                f"Location  : "
                f"{vessel['latitude']}, "
                f"{vessel['longitude']}"
            )

            if "speed" in vessel:

                print(
                    f"Speed     : "
                    f"{vessel['speed']}"
                )

            if "course" in vessel:

                print(
                    f"Course    : "
                    f"{vessel['course']}"
                )

            if "timestamp" in vessel:

                print(
                    f"Timestamp : "
                    f"{vessel['timestamp']}"
                )

            print(
                "------------------------------"
            )