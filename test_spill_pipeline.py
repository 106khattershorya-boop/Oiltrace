import sys
import os
import cv2
import torch
import numpy as np

from unet import UNet
from false_positive import filter_candidate


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = (
    "ml/models/spill_detector/"
    "best_unet_oil_spill_stable.pth"
)

IMAGE_SIZE = 256
THRESHOLD = 0.5

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    model = UNet().to(DEVICE)

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )
    )

    model.eval()

    return model


# ============================================================
# PREPROCESS
# ============================================================

def preprocess_image(image_path):

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise FileNotFoundError(
            f"Could not load image:\n{image_path}"
        )

    image = cv2.resize(
        image,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_AREA
    )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = image.astype(
        np.float32
    ) / 255.0

    image = np.transpose(
        image,
        (2, 0, 1)
    )

    image = torch.tensor(
        image,
        dtype=torch.float32
    ).unsqueeze(0)

    return image


# ============================================================
# U-NET PREDICTION
# ============================================================

def detect_spill(model, image):

    image = image.to(DEVICE)

    with torch.no_grad():

        output = model(image)

        probability = torch.sigmoid(
            output
        )

        prediction = (
            probability > THRESHOLD
        ).float()

    probability = (
        probability
        .squeeze()
        .cpu()
        .numpy()
    )

    prediction = (
        prediction
        .squeeze()
        .cpu()
        .numpy()
    )

    return probability, prediction


# ============================================================
# CALCULATE BASIC FEATURES
# ============================================================

def calculate_features(
    probability,
    prediction
):

    total_pixels = prediction.size

    spill_pixels = np.sum(
        prediction > 0
    )

    spill_area = (
        spill_pixels /
        total_pixels
    )

    # Average probability of predicted spill pixels
    if spill_pixels > 0:

        unet_confidence = float(
            np.mean(
                probability[prediction > 0]
            )
        )

    else:

        unet_confidence = 0.0

    # --------------------------------------------------------
    # Prototype evidence scores
    # --------------------------------------------------------
    #
    # These are NOT learned yet.
    # They are temporary values so that we can test
    # the complete pipeline architecture.
    #

    texture_score = unet_confidence

    shape_score = min(
        1.0,
        spill_area * 10
    )

    weather_score = 0.70

    temporal_score = 0.70

    area_score = min(
        1.0,
        spill_area * 10
    )

    return {
        "spill_area_percentage":
            spill_area * 100,

        "unet_confidence":
            unet_confidence,

        "texture_score":
            texture_score,

        "shape_score":
            shape_score,

        "weather_score":
            weather_score,

        "temporal_score":
            temporal_score,

        "area_score":
            area_score
    }


# ============================================================
# COMPLETE PIPELINE
# ============================================================

def run_pipeline(image_path):

    print("=" * 65)
    print("OIL SPILL ML PIPELINE")
    print("=" * 65)

    print(
        "\nDevice:",
        DEVICE
    )

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

    # --------------------------------------------------------
    # Step 1: Load model
    # --------------------------------------------------------

    print(
        "\n[1/4] Loading U-Net..."
    )

    model = load_model()

    print(
        "U-Net loaded successfully."
    )

    # --------------------------------------------------------
    # Step 2: Preprocess
    # --------------------------------------------------------

    print(
        "\n[2/4] Preprocessing image..."
    )

    image = preprocess_image(
        image_path
    )

    print(
        "Preprocessing complete."
    )

    # --------------------------------------------------------
    # Step 3: U-Net
    # --------------------------------------------------------

    print(
        "\n[3/4] Detecting possible spill..."
    )

    probability, prediction = (
        detect_spill(
            model,
            image
        )
    )

    features = calculate_features(
        probability,
        prediction
    )

    print(
        "U-Net prediction complete."
    )

    # --------------------------------------------------------
    # Step 4: False-positive filtering
    # --------------------------------------------------------

    print(
        "\n[4/4] Running false-positive filtering..."
    )

    filtering_result = filter_candidate(

        texture_score=
            features["texture_score"],

        shape_score=
            features["shape_score"],

        weather_score=
            features["weather_score"],

        temporal_score=
            features["temporal_score"],

        area_score=
            features["area_score"]
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    spill_detected = (
        features[
            "spill_area_percentage"
        ] >= 0.5
    )

    result = {

        "image": image_path,

        "spill": {

            "detected":
                bool(spill_detected),

            "area_percentage":
                round(
                    features[
                        "spill_area_percentage"
                    ],
                    2
                ),

            "unet_confidence":
                round(
                    features[
                        "unet_confidence"
                    ],
                    4
                )
        },

        "false_positive_filter": {

            "score":
                filtering_result[
                    "false_positive_score"
                ],

            "confidence_level":
                filtering_result[
                    "confidence_level"
                ]
        }
    }

    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python ml\\src\\test_spill_pipeline.py "
            "<image_path>"
        )

        print(
            "\nExample:"
        )

        print(
            "python ml\\src\\test_spill_pipeline.py "
            "ml\\data\\processed\\images\\test\\sentinel_100.png"
        )

        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):

        print(
            f"\nImage not found:\n"
            f"{image_path}"
        )

        sys.exit(1)

    result = run_pipeline(
        image_path
    )

    print("\n")
    print("=" * 65)
    print("FINAL ML PIPELINE RESULT")
    print("=" * 65)

    print("\nInput image:")
    print(result["image"])

    print("\n--- SPILL DETECTION ---")

    print(
        "Spill detected:",
        result["spill"]["detected"]
    )

    print(
        "Spill area:",
        result["spill"]["area_percentage"],
        "%"
    )

    print(
        "U-Net confidence:",
        result["spill"]["unet_confidence"]
    )

    print(
        "\n--- FALSE-POSITIVE FILTER ---"
    )

    print(
        "Filter score:",
        result[
            "false_positive_filter"
        ]["score"]
    )

    print(
        "Confidence level:",
        result[
            "false_positive_filter"
        ]["confidence_level"]
    )

    print("\n")
    print("=" * 65)