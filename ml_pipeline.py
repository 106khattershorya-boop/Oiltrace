# ============================================================
# COMPLETE ML PIPELINE
# ============================================================
#
# SIH 26143
#
# Flow:
#
#   Satellite Image
#       ↓
#   U-Net Spill Segmentation
#       ↓
#   False-Positive Filtering
#       ↓
#   Spill Event
#       ↓
#   AIS Candidate Search
#       ↓
#   Vessel Behaviour
#       ↓
#   Spectral Analysis
#       ↓
#   Evidence Fusion
#       ↓
#   Investigation Ranking
#
# IMPORTANT:
# This system ranks vessels for investigation.
# It does NOT prove that a vessel caused the spill.
#
# ============================================================


import pandas as pd
import os
import sys
import importlib.util
from datetime import datetime

import cv2
import numpy as np
import torch


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

OUTPUT_DIR = os.path.join(
    ML_DIR,
    "data",
    "test",
    "pipeline_outputs"
)

DEFAULT_IMAGE_PATH = os.path.join(
    ML_DIR,
    "data",
    "processed",
    "images",
    "test",
    "sentinel_100.png"
)

# The actual IMAGE_PATH can be supplied from the command line:
#   python ml\src\ml_pipeline.py "C:\path\to\image.jpg"
IMAGE_PATH = DEFAULT_IMAGE_PATH


def set_input_image_path():

    global IMAGE_PATH

    if len(sys.argv) >= 2:

        candidate = sys.argv[1].strip().strip('"')

        if candidate:
            IMAGE_PATH = os.path.abspath(
                os.path.expanduser(candidate)
            )

    return IMAGE_PATH


def get_output_paths():

    base_name = os.path.splitext(
        os.path.basename(IMAGE_PATH)
    )[0]

    return {
        "mask": os.path.join(
            OUTPUT_DIR,
            f"{base_name}_mask.png"
        ),
        "probability": os.path.join(
            OUTPUT_DIR,
            f"{base_name}_probability.png"
        ),
        "overlay": os.path.join(
            OUTPUT_DIR,
            f"{base_name}_overlay.png"
        ),
        "summary": os.path.join(
            OUTPUT_DIR,
            f"{base_name}_pipeline_summary.txt"
        ),
        "fusion_csv": os.path.join(
            OUTPUT_DIR,
            f"{base_name}_evidence_fusion_results.csv"
        )
    }

MODEL_PATH = os.path.join(
    ML_DIR,
    "models",
    "spill_detector",
    "best_unet_oil_spill_stable.pth"
)

BEHAVIOUR_FILE = os.path.join(
    AIS_DIR,
    "data",
    "behaviour_anomaly_results.csv"
)

FINAL_BEHAVIOUR_FILE = os.path.join(
    AIS_DIR,
    "data",
    "final_behaviour_scores.csv"
)

# Output paths are initialized for the default image and refreshed
# after the command-line image path is selected.
_OUTPUT_PATHS = None
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "pipeline_summary.txt")
MASK_OUTPUT = os.path.join(OUTPUT_DIR, "sentinel_100_mask.png")
PROBABILITY_OUTPUT = os.path.join(OUTPUT_DIR, "sentinel_100_probability.png")
OVERLAY_OUTPUT = os.path.join(OUTPUT_DIR, "sentinel_100_overlay.png")


def refresh_output_paths():

    global _OUTPUT_PATHS
    global SUMMARY_FILE
    global MASK_OUTPUT
    global PROBABILITY_OUTPUT
    global OVERLAY_OUTPUT

    _OUTPUT_PATHS = get_output_paths()

    SUMMARY_FILE = _OUTPUT_PATHS["summary"]
    MASK_OUTPUT = _OUTPUT_PATHS["mask"]
    PROBABILITY_OUTPUT = _OUTPUT_PATHS["probability"]
    OVERLAY_OUTPUT = _OUTPUT_PATHS["overlay"]


# ============================================================
# DEMO SPILL EVENT
# ============================================================
#
# IMPORTANT:
# This is a manually supplied demonstration event.
# It is not being claimed to have been automatically derived
# from the satellite image timestamp/location.
# ============================================================

SPILL_LATITUDE = 30.36441

SPILL_LONGITUDE = -89.08701

SPILL_TIME = "2024-01-01 00:03:15"


# ============================================================
# U-NET THRESHOLD
# ============================================================

PREDICTION_THRESHOLD = 0.5


# ============================================================
# IMPORT MODULE FROM FILE
# ============================================================

def import_module_from_path(
    module_name,
    file_path
):

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            "\nModule not found:\n"
            f"{file_path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path
    )

    if spec is None:

        raise ImportError(
            f"Could not create module spec for {file_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    sys.modules[
        module_name
    ] = module

    spec.loader.exec_module(
        module
    )

    return module


# ============================================================
# LOAD MODULES
# ============================================================

def load_modules():

    modules = {}

    # --------------------------------------------------------
    # U-Net
    # --------------------------------------------------------

    unet_path = os.path.join(
        CURRENT_DIR,
        "unet.py"
    )

    modules[
        "unet"
    ] = import_module_from_path(
        "sih_unet",
        unet_path
    )

    # --------------------------------------------------------
    # False-positive
    # --------------------------------------------------------

    false_positive_path = os.path.join(
        CURRENT_DIR,
        "false_positive.py"
    )

    modules[
        "false_positive"
    ] = import_module_from_path(
        "sih_false_positive",
        false_positive_path
    )

    # --------------------------------------------------------
    # Spectral
    # --------------------------------------------------------

    spectral_path = os.path.join(
        CURRENT_DIR,
        "spectral_analysis.py"
    )

    modules[
        "spectral"
    ] = import_module_from_path(
        "sih_spectral",
        spectral_path
    )

    # --------------------------------------------------------
    # Evidence fusion
    # --------------------------------------------------------

    evidence_path = os.path.join(
        CURRENT_DIR,
        "evidence_fusion.py"
    )

    modules[
        "evidence"
    ] = import_module_from_path(
        "sih_evidence",
        evidence_path
    )

    # --------------------------------------------------------
    # Correct AIS attribution module
    #
    # IMPORTANT:
    # We explicitly load ais/attribution.py so Python does not
    # accidentally import another file named attribution.py.
    # --------------------------------------------------------

    attribution_path = os.path.join(
        AIS_DIR,
        "attribution.py"
    )

    modules[
        "attribution"
    ] = import_module_from_path(
        "sih_ais_attribution",
        attribution_path
    )

    print(
        "\nAIS attribution module:"
    )

    print(
        attribution_path
    )

    return modules


# ============================================================
# INPUT DOMAIN VALIDATION
# ============================================================
#
# This is a heuristic domain gate for the current U-Net model.
# The model was trained on grayscale-like SAR imagery, so obvious
# strongly colorful optical images are rejected before inference.
# This is NOT an oil-spill classifier.
# ============================================================

def validate_input_domain(image_bgr):

    image_rgb = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2RGB
    )

    rgb = image_rgb.astype(np.float32)

    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]

    mean_channel_difference = float(
        (
            np.mean(np.abs(r - g))
            +
            np.mean(np.abs(g - b))
            +
            np.mean(np.abs(r - b))
        )
        /
        3.0
    )

    colorful_mask = (
        (np.abs(r - g) > 10)
        |
        (np.abs(g - b) > 10)
        |
        (np.abs(r - b) > 10)
    )

    colorful_pixel_percent = float(
        np.mean(colorful_mask) * 100.0
    )

    flat = rgb.reshape(-1, 3)

    try:
        channel_correlation = float(
            np.corrcoef(flat.T)[0, 1]
        )

        if not np.isfinite(channel_correlation):
            channel_correlation = 1.0

    except Exception:
        channel_correlation = 1.0

    intensity = cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    mean_intensity = float(
        intensity.mean()
    )

    intensity_std = float(
        intensity.std()
    )

    non_dark_percent = float(
        np.mean(intensity > 10) * 100.0
    )

    if (
        mean_channel_difference > 12.0
        and
        colorful_pixel_percent > 15.0
    ):

        accepted = False
        modality = "STRONGLY_COLORFUL_OPTICAL"
        reason = (
            "Image has strong RGB differences and appears "
            "outside the current U-Net training domain."
        )

    elif non_dark_percent < 5.0:

        accepted = False
        modality = "LOW_INFORMATION"
        reason = (
            "Image contains too little non-dark information "
            "for reliable analysis."
        )

    else:

        accepted = True
        modality = "GRAYSCALE_LIKE"
        reason = (
            "Image is compatible with the current "
            "grayscale-like U-Net input domain."
        )

    return {
        "accepted": accepted,
        "modality": modality,
        "reason": reason,
        "color_statistics": {
            "mean_channel_difference": mean_channel_difference,
            "colorful_pixel_percent": colorful_pixel_percent,
            "channel_correlation": channel_correlation
        },
        "quality_statistics": {
            "mean_intensity": mean_intensity,
            "intensity_std": intensity_std,
            "non_dark_percent": non_dark_percent
        }
    }


def display_input_validation(result):

    print(
        "\n=========================================="
    )

    print(
        "          INPUT DOMAIN VALIDATION"
    )

    print(
        "=========================================="
    )

    print(
        f"\nAccepted: {result['accepted']}"
    )

    print(
        f"Modality: {result['modality']}"
    )

    print(
        f"Reason: {result['reason']}"
    )

    color = result["color_statistics"]
    quality = result["quality_statistics"]

    print(
        "\nColor statistics:"
    )

    print(
        f"  mean_channel_difference: "
        f"{color['mean_channel_difference']:.4f}"
    )

    print(
        f"  colorful_pixel_percent: "
        f"{color['colorful_pixel_percent']:.4f}"
    )

    print(
        f"  channel_correlation: "
        f"{color['channel_correlation']:.4f}"
    )

    print(
        "\nQuality statistics:"
    )

    print(
        f"  mean_intensity: "
        f"{quality['mean_intensity']:.4f}"
    )

    print(
        f"  intensity_std: "
        f"{quality['intensity_std']:.4f}"
    )

    print(
        f"  non_dark_percent: "
        f"{quality['non_dark_percent']:.4f}"
    )


def score_to_percent(value):

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    if 0.0 <= score <= 1.0:
        return score * 100.0

    return score


# ============================================================
# LOAD IMAGE
# ============================================================

def load_test_image():

    if not os.path.exists(
        IMAGE_PATH
    ):

        raise FileNotFoundError(
            "\nTest image not found:\n"
            f"{IMAGE_PATH}"
        )

    image = cv2.imread(
        IMAGE_PATH,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise ValueError(
            "\nCould not read image:\n"
            f"{IMAGE_PATH}"
        )

    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image_rgb = cv2.resize(
        image_rgb,
        (
            256,
            256
        ),
        interpolation=cv2.INTER_AREA
    )

    return image, image_rgb


# ============================================================
# LOAD U-NET
# ============================================================

def load_model(
    unet_module,
    device
):

    if not os.path.exists(
        MODEL_PATH
    ):

        raise FileNotFoundError(
            "\nU-Net model not found:\n"
            f"{MODEL_PATH}"
        )

    model = (
        unet_module.UNet()
        .to(
            device
        )
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device
    )

    # --------------------------------------------------------
    # Support normal state_dict and checkpoint dictionaries
    # --------------------------------------------------------

    if isinstance(
        checkpoint,
        dict
    ) and "state_dict" in checkpoint:

        state_dict = checkpoint[
            "state_dict"
        ]

    else:

        state_dict = checkpoint

    # --------------------------------------------------------
    # Remove DataParallel prefix if present
    # --------------------------------------------------------

    cleaned_state_dict = {}

    for key, value in state_dict.items():

        if key.startswith(
            "module."
        ):

            cleaned_state_dict[
                key[7:]
            ] = value

        else:

            cleaned_state_dict[
                key
            ] = value

    model.load_state_dict(
        cleaned_state_dict
    )

    model.eval()

    return model


# ============================================================
# U-NET PREDICTION
# ============================================================

def predict_spill(
    model,
    image_rgb,
    device
):

    image = (
        image_rgb
        .astype(
            np.float32
        )
        /
        255.0
    )

    tensor = torch.tensor(
        image,
        dtype=torch.float32
    )

    tensor = tensor.permute(
        2,
        0,
        1
    )

    tensor = tensor.unsqueeze(
        0
    )

    tensor = tensor.to(
        device
    )

    with torch.no_grad():

        output = model(
            tensor
        )

        probability = torch.sigmoid(
            output
        )

    probability = (
        probability[
            0,
            0
        ]
        .cpu()
        .numpy()
    )

    mask = (
        probability
        >=
        PREDICTION_THRESHOLD
    ).astype(
        np.uint8
    )

    return probability, mask


# ============================================================
# SAVE U-NET OUTPUTS
# ============================================================

def save_segmentation_outputs(
    original_bgr,
    probability,
    mask
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Binary mask
    # --------------------------------------------------------

    mask_image = (
        mask
        *
        255
    ).astype(
        np.uint8
    )

    cv2.imwrite(
        MASK_OUTPUT,
        mask_image
    )

    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    probability_image = (
        probability
        *
        255.0
    ).clip(
        0,
        255
    ).astype(
        np.uint8
    )

    cv2.imwrite(
        PROBABILITY_OUTPUT,
        probability_image
    )

    # --------------------------------------------------------
    # Overlay
    # --------------------------------------------------------

    original_resized = cv2.resize(
        original_bgr,
        (
            256,
            256
        ),
        interpolation=cv2.INTER_AREA
    )

    overlay = original_resized.copy()

    # Use a red overlay for detected spill pixels.
    # This is only visualization, not another score.

    red_layer = np.zeros_like(
        overlay
    )

    red_layer[
        :,
        :,
        2
    ] = 255

    detected = (
        mask
        >
        0
    )

    overlay[
        detected
    ] = cv2.addWeighted(
        overlay[
            detected
        ],
        0.55,
        red_layer[
            detected
        ],
        0.45,
        0
    )

    cv2.imwrite(
        OVERLAY_OUTPUT,
        overlay
    )


# ============================================================
# U-NET METRICS
# ============================================================

def calculate_spill_statistics(
    probability,
    mask
):

    spill_pixels = int(
        np.sum(
            mask
        )
    )

    total_pixels = int(
        mask.size
    )

    spill_area_percent = (
        spill_pixels
        /
        total_pixels
        *
        100.0
    )

    if spill_pixels > 0:

        mean_probability = (
            float(
                probability[
                    mask > 0
                ].mean()
            )
            *
            100.0
        )

    else:

        mean_probability = 0.0

    max_probability = (
        float(
            probability.max()
        )
        *
        100.0
    )

    return {

        "spill_detected":
            spill_pixels > 0,

        "spill_pixels":
            spill_pixels,

        "total_pixels":
            total_pixels,

        "spill_area_percent":
            spill_area_percent,

        "mean_probability":
            mean_probability,

        "max_probability":
            max_probability
    }


# ============================================================
# FALSE-POSITIVE ANALYSIS
# ============================================================

def run_false_positive_analysis(
    false_positive_module,
    input_path,
    mask,
    probability
):

    result = (
        false_positive_module
        .analyze_false_positive(

            input_path,

            mask,

            probability
        )
    )

    return result


# ============================================================
# SPECTRAL ANALYSIS
# ============================================================

def run_spectral_analysis(
    spectral_module,
    input_path,
    mask
):

    result = (
        spectral_module
        .analyze_spectral_features(

            input_path,

            mask
        )
    )

    return result


# ============================================================
# EVIDENCE FUSION
# ============================================================
#
# We call the evidence-fusion functions directly instead of
# launching evidence_fusion.py again.
#
# This keeps the complete system inside one process.
# ============================================================

def run_evidence_fusion(
    evidence_module
):

    # --------------------------------------------------------
    # Load behaviour data
    # --------------------------------------------------------

    if not os.path.exists(
        BEHAVIOUR_FILE
    ):

        raise FileNotFoundError(
            "\nBehaviour data not found:\n"
            f"{BEHAVIOUR_FILE}"
        )

    behaviour_df = pd.read_csv(
        BEHAVIOUR_FILE
    )

    # --------------------------------------------------------
    # Load vessel-level data
    # --------------------------------------------------------

    if os.path.exists(
        FINAL_BEHAVIOUR_FILE
    ):

        final_df = pd.read_csv(
            FINAL_BEHAVIOUR_FILE
        )

    else:

        final_df = None

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    behaviour_df = (
        evidence_module
        .prepare_behaviour_data(

            behaviour_df,

            final_df
        )
    )

    # --------------------------------------------------------
    # Candidate detection
    # --------------------------------------------------------

    event_df = (
        evidence_module
        .find_event_candidates(

            behaviour_df
        )
    )

    if event_df.empty:

        return (
            pd.DataFrame(),
            event_df
        )

    # --------------------------------------------------------
    # One candidate per vessel
    # --------------------------------------------------------

    vessel_df = (
        evidence_module
        .create_vessel_candidates(

            event_df
        )
    )

    results = []

    # --------------------------------------------------------
    # Calculate evidence
    # --------------------------------------------------------

    for _, candidate in vessel_df.iterrows():

        event_behaviour = (
            evidence_module
            .calculate_event_behaviour(

                candidate[
                    "mmsi"
                ],

                behaviour_df
            )
        )

        result = (
            evidence_module
            .fuse_evidence(

                candidate,

                event_behaviour
            )
        )

        results.append(
            result
        )

    if not results:

        return (
            pd.DataFrame(),
            event_df
        )

    result_df = pd.DataFrame(
        results
    )

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

    return (
        result_df,
        event_df
    )


# ============================================================
# SAVE FINAL SUMMARY
# ============================================================

def save_summary(
    spill_stats,
    false_positive_result,
    spectral_result,
    fusion_df
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "==================================================\n"
        )

        file.write(
            "SIH 26143 - COMPLETE ML PIPELINE SUMMARY\n"
        )

        file.write(
            "==================================================\n\n"
        )

        file.write(
            f"Generated: "
            f"{datetime.now().isoformat()}\n\n"
        )

        # ----------------------------------------------------
        # Incident
        # ----------------------------------------------------

        file.write(
            "INCIDENT\n"
        )

        file.write(
            "--------------------------------------------------\n"
        )

        file.write(
            f"Latitude: {SPILL_LATITUDE}\n"
        )

        file.write(
            f"Longitude: {SPILL_LONGITUDE}\n"
        )

        file.write(
            f"Time: {SPILL_TIME}\n\n"
        )

        # ----------------------------------------------------
        # U-Net
        # ----------------------------------------------------

        file.write(
            "U-NET SPILL DETECTION\n"
        )

        file.write(
            "--------------------------------------------------\n"
        )

        file.write(
            f"Spill detected: "
            f"{spill_stats['spill_detected']}\n"
        )

        file.write(
            f"Spill pixels: "
            f"{spill_stats['spill_pixels']}\n"
        )

        file.write(
            f"Spill area: "
            f"{spill_stats['spill_area_percent']:.2f}%\n"
        )

        file.write(
            f"Mean U-Net probability: "
            f"{spill_stats['mean_probability']:.2f}%\n"
        )

        file.write(
            f"Maximum U-Net probability: "
            f"{spill_stats['max_probability']:.2f}%\n\n"
        )

        # ----------------------------------------------------
        # False positive
        # ----------------------------------------------------

        file.write(
            "FALSE-POSITIVE ANALYSIS\n"
        )

        file.write(
            "--------------------------------------------------\n"
        )

        file.write(
            f"Candidate score: "
            f"{score_to_percent(false_positive_result.get('candidate_score', 0)):.2f}%\n"
        )

        file.write(
            f"Classification: "
            f"{false_positive_result.get('classification', 'N/A')}\n"
        )

        file.write(
            f"Connected components: "
            f"{false_positive_result.get('connected_components', 0)}\n"
        )

        file.write(
            f"Filtered area: "
            f"{false_positive_result.get('spill_area_percent', 0):.2f}%\n\n"
        )

        # ----------------------------------------------------
        # Spectral
        # ----------------------------------------------------

        file.write(
            "SPECTRAL ANALYSIS\n"
        )

        file.write(
            "--------------------------------------------------\n"
        )

        file.write(
            f"RGB proxy score: "
            f"{spectral_result.get('rgb_spectral_proxy_score', 0) * 100:.2f}\n"
        )

        file.write(
            f"Probable oil category: "
            f"{spectral_result.get('probable_oil_category', 'N/A')}\n"
        )

        file.write(
            f"Category confidence: "
            f"{spectral_result.get('category_confidence', 0) * 100:.2f}%\n\n"
        )

        # ----------------------------------------------------
        # Fusion
        # ----------------------------------------------------

        file.write(
            "INVESTIGATION RANKING\n"
        )

        file.write(
            "--------------------------------------------------\n"
        )

        file.write(
            "Scoring model:\n"
        )

        file.write(
            "  Spatial proximity       35%\n"
        )

        file.write(
            "  Temporal proximity      30%\n"
        )

        file.write(
            "  Behaviour                25%\n"
        )

        file.write(
            "  AIS confidence           10%\n\n"
        )

        if fusion_df.empty:

            file.write(
                "No AIS candidates found.\n"
            )

        else:

            for _, row in fusion_df.head(
                10
            ).iterrows():

                file.write(
                    f"Rank {int(row['rank'])}: "
                    f"{row['vessel_name']} "
                    f"(MMSI {row['MMSI']})\n"
                )

                file.write(
                    f"  Distance: "
                    f"{row['distance_km']:.3f} km\n"
                )

                file.write(
                    f"  Time difference: "
                    f"{row['time_difference_minutes']:.2f} min\n"
                )

                file.write(
                    f"  Spatial score: "
                    f"{row['spatial_score']:.2f}\n"
                )

                file.write(
                    f"  Temporal score: "
                    f"{row['temporal_score']:.2f}\n"
                )

                file.write(
                    f"  Combined behaviour: "
                    f"{row['combined_behaviour_score']:.2f}\n"
                )

                file.write(
                    f"  AIS confidence: "
                    f"{row['ais_confidence']}\n"
                )

                file.write(
                    f"  Investigation score: "
                    f"{row['investigation_priority_score']:.2f}\n"
                )

                file.write(
                    f"  Priority: "
                    f"{row['priority_level']}\n"
                )

                file.write(
                    "  Reasons:\n"
                )

                for reason in row[
                    "reasons"
                ]:

                    file.write(
                        f"    - {reason}\n"
                    )

                file.write(
                    "\n"
                )

        file.write(
            "==================================================\n"
        )

        file.write(
            "IMPORTANT: Investigation priority is not causation.\n"
        )

        file.write(
            "A high-ranked vessel is a candidate for investigation,\n"
        )

        file.write(
            "not a proven source of the spill.\n"
        )

        file.write(
            "==================================================\n"
        )


# ============================================================
# DISPLAY FINAL RESULTS
# ============================================================

def display_final_results(
    spill_stats,
    false_positive_result,
    spectral_result,
    fusion_df
):

    print(
        "\n"
        "=================================================="
    )

    print(
        "          COMPLETE PIPELINE RESULTS"
    )

    print(
        "=================================================="
    )

    # --------------------------------------------------------
    # Incident
    # --------------------------------------------------------

    print(
        "\nINCIDENT"
    )

    print(
        f"  Location : "
        f"{SPILL_LATITUDE}, {SPILL_LONGITUDE}"
    )

    print(
        f"  Time     : "
        f"{SPILL_TIME}"
    )

    # --------------------------------------------------------
    # U-Net
    # --------------------------------------------------------

    print(
        "\nU-NET"
    )

    print(
        f"  Spill detected     : "
        f"{spill_stats['spill_detected']}"
    )

    print(
        f"  Spill area         : "
        f"{spill_stats['spill_area_percent']:.2f}%"
    )

    print(
        f"  Spill pixels       : "
        f"{spill_stats['spill_pixels']}"
    )

    print(
        f"  Mean probability   : "
        f"{spill_stats['mean_probability']:.2f}%"
    )

    # --------------------------------------------------------
    # False positive
    # --------------------------------------------------------

    print(
        "\nFALSE-POSITIVE FILTER"
    )

    print(
        f"  Candidate score    : "
        f"{score_to_percent(false_positive_result.get('candidate_score', 0)):.2f}%"
    )

    print(
        f"  Classification     : "
        f"{false_positive_result.get('classification', 'N/A')}"
    )

    print(
        f"  Components         : "
        f"{false_positive_result.get('connected_components', 0)}"
    )

    # --------------------------------------------------------
    # Spectral
    # --------------------------------------------------------

    print(
        "\nSPECTRAL"
    )

    print(
        f"  RGB proxy score    : "
        f"{spectral_result.get('rgb_spectral_proxy_score', 0) * 100:.2f}"
    )

    print(
        f"  Oil category       : "
        f"{spectral_result.get('probable_oil_category', 'N/A')}"
    )

    # --------------------------------------------------------
    # AIS
    # --------------------------------------------------------

    if fusion_df.empty:

        print(
            "\nAIS"
        )

        print(
            "  No matching vessels found."
        )

        return

    print(
        "\nAIS"
    )

    print(
        f"  Candidate records  : "
        f"{len(fusion_df)} unique vessels"
    )

    # --------------------------------------------------------
    # Top candidates
    # --------------------------------------------------------

    print(
        "\n=================================================="
    )

    print(
        "          TOP INVESTIGATION TARGETS"
    )

    print(
        "=================================================="
    )

    display_columns = [

        "rank",

        "MMSI",

        "vessel_name",

        "distance_km",

        "time_difference_minutes",

        "spatial_score",

        "temporal_score",

        "combined_behaviour_score",

        "ais_confidence",

        "investigation_priority_score",

        "priority_level"
    ]

    print(
        fusion_df[
            display_columns
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Top candidate details
    # --------------------------------------------------------

    top = fusion_df.iloc[
        0
    ]

    print(
        "\n=================================================="
    )

    print(
        "          TOP CANDIDATE DETAILS"
    )

    print(
        "=================================================="
    )

    print(
        f"\nRank                 : "
        f"{int(top['rank'])}"
    )

    print(
        f"MMSI                 : "
        f"{top['MMSI']}"
    )

    print(
        f"Vessel               : "
        f"{top['vessel_name']}"
    )

    print(
        f"Distance             : "
        f"{top['distance_km']:.3f} km"
    )

    print(
        f"Time difference      : "
        f"{top['time_difference_minutes']:.2f} min"
    )

    print(
        f"\nSpatial score        : "
        f"{top['spatial_score']:.2f}"
    )

    print(
        f"Temporal score       : "
        f"{top['temporal_score']:.2f}"
    )

    print(
        f"Vessel behaviour     : "
        f"{top['vessel_behaviour_score']:.2f}"
    )

    print(
        f"Event behaviour      : "
        f"{top['event_behaviour_score']:.2f}"
    )

    print(
        f"Combined behaviour   : "
        f"{top['combined_behaviour_score']:.2f}"
    )

    print(
        f"AIS confidence       : "
        f"{top['ais_confidence']}"
    )

    print(
        f"\nInvestigation score  : "
        f"{top['investigation_priority_score']:.2f}"
    )

    print(
        f"Priority level       : "
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


# ============================================================
# MAIN
# ============================================================

def main():

    global IMAGE_PATH

    set_input_image_path()
    refresh_output_paths()

    start_time = datetime.now()

    print(
        "\n"
        "=================================================="
    )

    print(
        "           SIH 26143 ML PIPELINE"
    )

    print(
        "=================================================="
    )

    print(
        f"\nProject root:"
        f"\n{PROJECT_ROOT}"
    )

    print(
        f"\nTest image:"
        f"\n{IMAGE_PATH}"
    )

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    if torch.cuda.is_available():

        device = torch.device(
            "cuda"
        )

        print(
            "\nDevice:"
            "\nNVIDIA CUDA GPU"
        )

        print(
            f"GPU:"
            f"\n{torch.cuda.get_device_name(0)}"
        )

    else:

        device = torch.device(
            "cpu"
        )

        print(
            "\nDevice:"
            "\nCPU"
        )

    # --------------------------------------------------------
    # Modules
    # --------------------------------------------------------

    print(
        "\nLoading ML modules..."
    )

    modules = load_modules()

    # --------------------------------------------------------
    # Image
    # --------------------------------------------------------

    print(
        "\nLoading satellite image..."
    )

    original_bgr, image_rgb = (
        load_test_image()
    )

    print(
        "Image loaded successfully."
    )

    print(
        f"Image shape: "
        f"{image_rgb.shape}"
    )

    # --------------------------------------------------------
    # Input domain validation
    # --------------------------------------------------------

    validation_result = validate_input_domain(
        original_bgr
    )

    display_input_validation(
        validation_result
    )

    if not validation_result["accepted"]:

        print(
            "\n------------------------------------------"
        )

        print(
            "PIPELINE REJECTED INPUT"
        )

        print(
            "------------------------------------------"
        )

        print(
            "\nU-Net inference was NOT started."
        )

        print(
            "Use imagery compatible with the trained "
            "SAR/grayscale-like model."
        )

        print(
            f"\nRuntime: "
            f"{(datetime.now() - start_time).total_seconds():.2f} seconds"
        )

        return

    # --------------------------------------------------------
    # U-Net
    # --------------------------------------------------------

    print(
        "\n------------------------------------------"
    )

    print(
        "STEP 1: U-NET SPILL DETECTION"
    )

    print(
        "------------------------------------------"
    )

    model = load_model(
        modules[
            "unet"
        ],
        device
    )

    probability, mask = predict_spill(
        model,
        image_rgb,
        device
    )

    spill_stats = (
        calculate_spill_statistics(

            probability,

            mask
        )
    )

    save_segmentation_outputs(
        original_bgr,
        probability,
        mask
    )

    print(
        f"\nSpill detected:"
        f" {spill_stats['spill_detected']}"
    )

    print(
        f"Spill area:"
        f" {spill_stats['spill_area_percent']:.2f}%"
    )

    print(
        f"Spill pixels:"
        f" {spill_stats['spill_pixels']}"
    )

    print(
        f"Mean confidence:"
        f" {spill_stats['mean_probability']:.2f}%"
    )

    print(
        f"Mask saved:"
        f"\n{MASK_OUTPUT}"
    )

    print(
        f"Overlay saved:"
        f"\n{OVERLAY_OUTPUT}"
    )

    # --------------------------------------------------------
    # False positive
    # --------------------------------------------------------

    print(
        "\n------------------------------------------"
    )

    print(
        "STEP 2: FALSE-POSITIVE FILTER"
    )

    print(
        "------------------------------------------"
    )

    false_positive_result = (
        run_false_positive_analysis(

            modules[
                "false_positive"
            ],

            IMAGE_PATH,

            mask,

            probability
        )
    )

    print(
        f"\nCandidate score:"
        f" {score_to_percent(false_positive_result.get('candidate_score', 0)):.2f}%"
    )

    print(
        f"Classification:"
        f" {false_positive_result.get('classification', 'N/A')}"
    )

    print(
        f"Filtered area:"
        f" {false_positive_result.get('spill_area_percent', 0):.2f}%"
    )

    print(
        f"Connected components:"
        f" {false_positive_result.get('connected_components', 0)}"
    )

    # --------------------------------------------------------
    # Incident
    # --------------------------------------------------------

    print(
        "\n------------------------------------------"
    )

    print(
        "STEP 3: SPILL INCIDENT"
    )

    print(
        "------------------------------------------"
    )

    print(
        f"\nLatitude:"
        f" {SPILL_LATITUDE}"
    )

    print(
        f"Longitude:"
        f" {SPILL_LONGITUDE}"
    )

    print(
        f"Time:"
        f" {SPILL_TIME}"
    )

    print(
        "\nNOTE:"
    )

    print(
        "This incident metadata is supplied manually "
        "for the current demonstration."
    )

    # --------------------------------------------------------
    # Spectral
    # --------------------------------------------------------

    print(
        "\n------------------------------------------"
    )

    print(
        "STEP 4: SPECTRAL ANALYSIS"
    )

    print(
        "------------------------------------------"
    )

    spectral_result = (
        run_spectral_analysis(

            modules[
                "spectral"
            ],

            IMAGE_PATH,

            mask
        )
    )

    print(
        f"\nRGB proxy score:"
        f" {spectral_result.get('rgb_spectral_proxy_score', 0) * 100:.2f}"
    )

    print(
        f"Probable oil category:"
        f" {spectral_result.get('probable_oil_category', 'N/A')}"
    )

    print(
        f"Category confidence:"
        f" {spectral_result.get('category_confidence', 0) * 100:.2f}%"
    )

    # --------------------------------------------------------
    # AIS / Behaviour / Fusion
    # --------------------------------------------------------

    print(
        "\n------------------------------------------"
    )

    print(
        "STEP 5: AIS + BEHAVIOUR + EVIDENCE FUSION"
    )

    print(
        "------------------------------------------"
    )

    fusion_df, event_df = (
        run_evidence_fusion(

            modules[
                "evidence"
            ]
        )
    )

    if fusion_df.empty:

        print(
            "\nNo AIS candidates found."
        )

    else:

        print(
            f"\nAIS event observations:"
            f" {len(event_df):,}"
        )

        print(
            f"Unique vessels:"
            f" {len(fusion_df):,}"
        )

    # --------------------------------------------------------
    # Save final summary
    # --------------------------------------------------------

    save_summary(

        spill_stats,

        false_positive_result,

        spectral_result,

        fusion_df
    )

    # --------------------------------------------------------
    # Final display
    # --------------------------------------------------------

    display_final_results(

        spill_stats,

        false_positive_result,

        spectral_result,

        fusion_df
    )

    # --------------------------------------------------------
    # Output files
    # --------------------------------------------------------

    print(
        "\n=================================================="
    )

    print(
        "              OUTPUT FILES"
    )

    print(
        "=================================================="
    )

    print(
        f"\nMask:"
        f"\n{MASK_OUTPUT}"
    )

    print(
        f"\nProbability map:"
        f"\n{PROBABILITY_OUTPUT}"
    )

    print(
        f"\nOverlay:"
        f"\n{OVERLAY_OUTPUT}"
    )

    fusion_csv = _OUTPUT_PATHS["fusion_csv"]

    print(
        f"\nEvidence fusion CSV:"
        f"\n{fusion_csv}"
    )

    # --------------------------------------------------------
    # Save CSV ourselves because this invocation did not run
    # evidence_fusion.py as a standalone script.
    # --------------------------------------------------------

    if not fusion_df.empty:

        fusion_csv = _OUTPUT_PATHS["fusion_csv"]

        fusion_df.to_csv(
            fusion_csv,
            index=False
        )

    print(
        f"\nPipeline summary:"
        f"\n{SUMMARY_FILE}"
    )

    # --------------------------------------------------------
    # Runtime
    # --------------------------------------------------------

    end_time = datetime.now()

    runtime = (
        end_time
        -
        start_time
    ).total_seconds()

    print(
        "\n=================================================="
    )

    print(
        "          PIPELINE COMPLETED"
    )

    print(
        "=================================================="
    )

    print(
        f"\nRuntime: "
        f"{runtime:.2f} seconds"
    )

    print(
        "\nImportant:"
    )

    print(
        "The investigation ranking identifies vessels "
        "for further investigation; it does not establish "
        "causation."
    )

    print(
        "\n=================================================="
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()