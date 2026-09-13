import os
import sys
import cv2
import torch
import numpy as np

from unet import UNet


# ============================================================
# CONFIGURATION
# ============================================================

# Stable model selected after final test evaluation
MODEL_PATH = (
    "ml/models/spill_detector/"
    "best_unet_oil_spill_stable.pth"
)

# Input/output image size used during training
IMAGE_SIZE = 256

# Probability threshold
THRESHOLD = 0.5

# Minimum spill area required to say "spill detected"
MIN_SPILL_AREA_PERCENTAGE = 0.5

# Output directory
OUTPUT_DIR = "ml/data/test"

# Automatically use GPU if available
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print("\nLoading U-Net model...")

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"\nModel not found:\n"
            f"{MODEL_PATH}\n\n"
            "Make sure the stable model exists."
        )

    model = UNet().to(DEVICE)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    model.load_state_dict(checkpoint)

    model.eval()

    print("Model loaded successfully.")

    return model


# ============================================================
# PREPROCESS IMAGE
# ============================================================

def preprocess_image(image_path):

    print("\nLoading input image...")

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise FileNotFoundError(
            f"\nCould not load image:\n"
            f"{image_path}"
        )

    print(
        "Original image size:",
        image.shape[1],
        "x",
        image.shape[0]
    )

    # Resize to model input size
    image = cv2.resize(
        image,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_AREA
    )

    # OpenCV uses BGR
    # Model was trained using RGB
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # Convert uint8 [0,255]
    # to float32 [0,1]
    image = image.astype(
        np.float32
    ) / 255.0

    # H,W,C → C,H,W
    image = np.transpose(
        image,
        (2, 0, 1)
    )

    # NumPy → PyTorch
    image = torch.tensor(
        image,
        dtype=torch.float32
    )

    # Add batch dimension
    # C,H,W → 1,C,H,W
    image = image.unsqueeze(0)

    return image


# ============================================================
# PREDICTION
# ============================================================

def predict(model, image):

    image = image.to(DEVICE)

    with torch.no_grad():

        # Raw U-Net output
        output = model(image)

        # Convert logits to probability
        probability = torch.sigmoid(
            output
        )

        # Convert probability to binary mask
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
# CALCULATE SPILL INFORMATION
# ============================================================

def calculate_spill_information(
    probability,
    prediction
):

    total_pixels = prediction.size

    spill_pixels = np.sum(
        prediction > 0
    )

    spill_percentage = (
        spill_pixels /
        total_pixels
    ) * 100

    # Pixels classified as spill
    spill_probabilities = (
        probability[prediction > 0]
    )

    if len(spill_probabilities) > 0:

        confidence = float(
            np.mean(
                spill_probabilities
            )
        )

    else:

        confidence = 0.0

    spill_detected = (
        spill_percentage
        >= MIN_SPILL_AREA_PERCENTAGE
    )

    return {
        "spill_detected": bool(
            spill_detected
        ),
        "spill_area_percentage": round(
            float(spill_percentage),
            2
        ),
        "confidence": round(
            confidence,
            4
        ),
        "spill_pixels": int(
            spill_pixels
        ),
        "total_pixels": int(
            total_pixels
        )
    }


# ============================================================
# SAVE BINARY MASK
# ============================================================

def save_mask(
    prediction,
    output_path
):

    mask = (
        prediction * 255
    ).astype(
        np.uint8
    )

    cv2.imwrite(
        output_path,
        mask
    )

    print(
        "\nBinary spill mask saved to:"
    )

    print(
        os.path.abspath(
            output_path
        )
    )


# ============================================================
# SAVE PROBABILITY MAP
# ============================================================

def save_probability_map(
    probability,
    output_path
):

    probability_image = (
        probability * 255
    ).clip(
        0,
        255
    ).astype(
        np.uint8
    )

    cv2.imwrite(
        output_path,
        probability_image
    )

    print(
        "\nProbability map saved to:"
    )

    print(
        os.path.abspath(
            output_path
        )
    )


# ============================================================
# SAVE OVERLAY
# ============================================================

def save_overlay(
    image_path,
    prediction,
    output_path
):

    original = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if original is None:

        return

    original = cv2.resize(
        original,
        (IMAGE_SIZE, IMAGE_SIZE),
        interpolation=cv2.INTER_AREA
    )

    # Create mask
    mask = (
        prediction * 255
    ).astype(
        np.uint8
    )

    # Convert mask to BGR
    mask_bgr = cv2.cvtColor(
        mask,
        cv2.COLOR_GRAY2BGR
    )

    # Highlight spill pixels
    overlay = original.copy()

    spill_region = (
        prediction > 0
    )

    # Highlight detected regions
    # using white in the overlay
    overlay[spill_region] = (
        255,
        255,
        255
    )

    # Blend original and detected region
    result = cv2.addWeighted(
        original,
        0.70,
        overlay,
        0.30,
        0
    )

    cv2.imwrite(
        output_path,
        result
    )

    print(
        "\nOverlay saved to:"
    )

    print(
        os.path.abspath(
            output_path
        )
    )


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    image_path,
    information
):

    print("\n")
    print("=" * 60)
    print("OIL SPILL PREDICTION")
    print("=" * 60)

    print(
        "\nInput image:"
    )

    print(
        image_path
    )

    print(
        "\nSpill detected:",
        information[
            "spill_detected"
        ]
    )

    print(
        "Spill area:",
        information[
            "spill_area_percentage"
        ],
        "%"
    )

    print(
        "Spill pixels:",
        information[
            "spill_pixels"
        ]
    )

    print(
        "Total pixels:",
        information[
            "total_pixels"
        ]
    )

    print(
        "Model confidence:",
        information[
            "confidence"
        ]
    )

    print(
        "\nConfidence percentage:",
        round(
            information[
                "confidence"
            ] * 100,
            2
        ),
        "%"
    )

    print("\n")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("OIL SPILL SINGLE IMAGE PREDICTION")
    print("=" * 60)

    # --------------------------------------------------------
    # Check command-line argument
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python ml\\src\\predict.py "
            "<image_path>"
        )

        print(
            "\nExample:"
        )

        print(
            "python ml\\src\\predict.py "
            "ml\\data\\processed\\images\\test\\example.png"
        )

        sys.exit(1)

    image_path = sys.argv[1]

    # --------------------------------------------------------
    # Check input image
    # --------------------------------------------------------

    if not os.path.exists(image_path):

        print(
            f"\nInput image not found:\n"
            f"{image_path}"
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Show device
    # --------------------------------------------------------

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
    # Load model
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    image = preprocess_image(
        image_path
    )

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    print(
        "\nRunning prediction..."
    )

    probability, prediction = predict(
        model,
        image
    )

    print(
        "Prediction completed."
    )

    # --------------------------------------------------------
    # Calculate results
    # --------------------------------------------------------

    information = (
        calculate_spill_information(
            probability,
            prediction
        )
    )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print_results(
        image_path,
        information
    )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Output paths
    # --------------------------------------------------------

    mask_path = os.path.join(
        OUTPUT_DIR,
        "predicted_spill_mask.png"
    )

    probability_path = os.path.join(
        OUTPUT_DIR,
        "spill_probability_map.png"
    )

    overlay_path = os.path.join(
        OUTPUT_DIR,
        "spill_overlay.png"
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    save_mask(
        prediction,
        mask_path
    )

    save_probability_map(
        probability,
        probability_path
    )

    save_overlay(
        image_path,
        prediction,
        overlay_path
    )

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("PREDICTION COMPLETE")
    print("=" * 60)

    print(
        "\nThree files were created:"
    )

    print(
        "\n1. predicted_spill_mask.png"
    )

    print(
        "2. spill_probability_map.png"
    )

    print(
        "3. spill_overlay.png"
    )

    print(
        "\nOutput folder:"
    )

    print(
        os.path.abspath(
            OUTPUT_DIR
        )
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()