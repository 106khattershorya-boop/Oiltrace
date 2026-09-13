import os
import pandas as pd


AIS_FILE = "ais/data/final_behaviour_scores.csv"


def load_ais_behaviour_data():

    if not os.path.exists(AIS_FILE):
        raise FileNotFoundError(
            f"AIS behaviour file not found:\n{AIS_FILE}"
        )

    df = pd.read_csv(AIS_FILE)

    # Remove accidental spaces from column names
    df.columns = df.columns.str.strip()

    # Automatically find MMSI column
    mmsi_column = None

    possible_mmsi_names = [
        "MMSI",
        "mmsi",
        "Mmsi",
        "vessel_id",
        "vessel",
        "ship_id"
    ]

    for name in possible_mmsi_names:
        if name in df.columns:
            mmsi_column = name
            break

    if mmsi_column is None:
        raise ValueError(
            "\nCould not find MMSI column.\n"
            f"Available columns:\n{df.columns.tolist()}"
        )

    # Rename it internally to MMSI
    if mmsi_column != "MMSI":
        df.rename(
            columns={mmsi_column: "MMSI"},
            inplace=True
        )

    required_columns = [
        "MMSI",
        "behaviour_score",
        "behaviour_level",
        "data_confidence"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"\nMissing required AIS columns: {missing}\n"
            f"Available columns:\n{df.columns.tolist()}"
        )

    return df


def get_top_vessels(limit=10):

    df = load_ais_behaviour_data()

    df = df.sort_values(
        by="behaviour_score",
        ascending=False
    )

    columns = [
        "MMSI",
        "behaviour_score",
        "behaviour_level",
        "data_confidence"
    ]

    return df[columns].head(limit).to_dict(
        orient="records"
    )


def get_vessel_behaviour(mmsi):

    df = load_ais_behaviour_data()

    vessel = df[
        df["MMSI"].astype(str) == str(mmsi)
    ]

    if vessel.empty:

        return {
            "found": False,
            "MMSI": str(mmsi),
            "message": "Vessel not found in AIS behaviour dataset."
        }

    row = vessel.iloc[0]

    result = {
        "found": True,
        "MMSI": str(row["MMSI"]),
        "behaviour_score": float(row["behaviour_score"]),
        "behaviour_level": str(row["behaviour_level"]),
        "data_confidence": str(row["data_confidence"])
    }

    if "reasons" in df.columns:

        reasons = row["reasons"]

        if pd.isna(reasons):

            result["reasons"] = []

        else:

            result["reasons"] = [
                reason.strip()
                for reason in str(reasons).split(";")
                if reason.strip()
            ]

    return result


if __name__ == "__main__":

    print("\nLoading AIS behaviour data...\n")

    try:

        top_vessels = get_top_vessels(10)

        print("Top 10 behaviour-anomaly vessels:\n")

        for vessel in top_vessels:

            print(
                f"MMSI: {vessel['MMSI']} | "
                f"Score: {vessel['behaviour_score']} | "
                f"Level: {vessel['behaviour_level']} | "
                f"Confidence: {vessel['data_confidence']}"
            )

    except Exception as e:

        print("\nERROR:")
        print(e)