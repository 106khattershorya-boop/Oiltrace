import numpy as np

from spectral_analysis import (
    calculate_spectral_features,
    calculate_band_ratio,
    analyze_spectral_data
)


# ============================================================
# CREATE SAMPLE SPECTRAL DATA
# ============================================================

bands = {

    "B2": np.array([
        0.20,
        0.22,
        0.21,
        0.19,
        0.23
    ]),

    "B3": np.array([
        0.30,
        0.32,
        0.31,
        0.29,
        0.33
    ]),

    "B4": np.array([
        0.25,
        0.27,
        0.26,
        0.24,
        0.28
    ])
}


# ============================================================
# FEATURE EXTRACTION
# ============================================================

features = calculate_spectral_features(
    bands
)


print("=" * 60)
print("SPECTRAL ANALYSIS TEST")
print("=" * 60)

print("\nExtracted features:")

for key, value in features.items():

    print(
        f"{key}: {value:.4f}"
    )


# ============================================================
# BAND RATIO
# ============================================================

ratio = calculate_band_ratio(
    bands["B4"],
    bands["B3"]
)


print("\nB4/B3 ratio:")

print(
    "Mean:",
    round(
        ratio["mean"],
        4
    )
)

print(
    "Std:",
    round(
        ratio["std"],
        4
    )
)


# ============================================================
# CATEGORY ESTIMATION
# ============================================================

result = analyze_spectral_data(
    bands
)


print(
    "\nProbable oil category:"
)

print(
    result[
        "probable_oil_category"
    ]
)

print(
    "\nCategory confidence:"
)

print(
    result[
        "confidence"
    ]
)


print("\n")
print("=" * 60)
print("SPECTRAL TEST COMPLETE")
print("=" * 60)