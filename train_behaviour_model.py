import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "ais/data/vessel_behaviour_features.csv"
OUTPUT_FILE = "ais/data/behaviour_anomaly_results.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("VESSEL BEHAVIOUR ANOMALY MODEL")
print("=" * 60)

print("\nLoading behaviour data...")

df = pd.read_csv(INPUT_FILE)

print("Rows loaded:", len(df))


# ============================================================
# SELECT ML FEATURES
# ============================================================

features = [
    "sog",
    "speed_change",
    "course_change",
    "distance_km",
    "stopped",
    "ais_gap",
    "loitering"
]

print("\nML features:")

for feature in features:
    print("-", feature)


# ============================================================
# CLEAN DATA
# ============================================================

print("\nCleaning data...")

X = df[features].copy()

# Replace infinite values
X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

# Replace missing values
X = X.fillna(0)


# ============================================================
# SCALE FEATURES
# ============================================================

print("Preparing feature scaling...")


# ============================================================
# ISOLATION FOREST
# ============================================================

print("\nTraining Isolation Forest...")

model = Pipeline(
    [
        (
            "scaler",
            StandardScaler()
        ),

        (
            "isolation_forest",
            IsolationForest(
                n_estimators=100,
                contamination=0.10,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)


model.fit(X)


# ============================================================
# PREDICTION
# ============================================================

print("Detecting anomalous behaviour...")

predictions = model.predict(X)

anomaly_scores = (
    model
    .named_steps["isolation_forest"]
    .decision_function(
        model
        .named_steps["scaler"]
        .transform(X)
    )
)


# ============================================================
# ADD RESULTS
# ============================================================

df["anomaly_prediction"] = predictions

df["anomaly_score"] = anomaly_scores

df["behaviour_label"] = np.where(
    predictions == -1,
    "ANOMALOUS",
    "NORMAL"
)


# ============================================================
# NORMALIZE ANOMALY SCORE
# ============================================================

# Isolation Forest decision_function:
#
# higher score → more normal
# lower score  → more anomalous
#
# We convert it into a simple 0–100
# behaviour anomaly score.

minimum = df["anomaly_score"].min()
maximum = df["anomaly_score"].max()

if maximum != minimum:

    df["behaviour_anomaly_score"] = (
        (
            maximum
            - df["anomaly_score"]
        )
        /
        (
            maximum
            - minimum
        )
        * 100
    )

else:

    df["behaviour_anomaly_score"] = 0


df["behaviour_anomaly_score"] = (
    df["behaviour_anomaly_score"]
    .round(2)
)


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

anomalous_count = (
    df["behaviour_label"]
    == "ANOMALOUS"
).sum()

normal_count = (
    df["behaviour_label"]
    == "NORMAL"
).sum()


print("\n" + "=" * 60)
print("MODEL COMPLETE")
print("=" * 60)

print("\nNormal records:", normal_count)

print(
    "Anomalous records:",
    anomalous_count
)

print(
    "Anomaly percentage:",
    round(
        anomalous_count / len(df) * 100,
        2
    ),
    "%"
)

print("\nSaved results to:")

print(OUTPUT_FILE)


# ============================================================
# SHOW MOST ANOMALOUS RECORDS
# ============================================================

print("\nMost anomalous records:")

result_columns = [
    "mmsi",
    "base_date_time",
    "sog",
    "speed_change",
    "course_change",
    "stopped",
    "ais_gap",
    "loitering",
    "behaviour_anomaly_score",
    "behaviour_label"
]

print(
    df
    .sort_values(
        "behaviour_anomaly_score",
        ascending=False
    )
    [result_columns]
    .head(20)
    .to_string(index=False)
)