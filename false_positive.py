# ============================================================
# FALSE POSITIVE FILTERING
# ============================================================
#
# SIH 26143
#
# Purpose:
# Analyze the region detected by the U-Net model and calculate
# an image-based candidate score.
#
# Signals used:
#   1. Texture
#   2. Shape
#   3. Fragmentation
#   4. Area
#   5. Border contact
#
# IMPORTANT:
# This is an image-based heuristic filter.
# It is NOT a scientifically validated oil classifier.
# It does NOT prove that a detected region is oil.
#
# ============================================================

import os
import cv2
import numpy as np


# ============================================================
# CLAMP
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):
    return max(
        minimum,
        min(
            maximum,
            float(value)
        )
    )


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(
    image_path
):
    """
    Load and resize image to 256x256.
    """

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
        (256, 256),
        interpolation=cv2.INTER_AREA
    )

    return image


# ============================================================
# CLEAN MASK
# ============================================================

def clean_mask(
    mask
):
    """
    Remove small isolated regions and close small gaps.
    """

    mask = (
        mask.astype(
            np.uint8
        )
        * 255
    )

    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    # Remove tiny isolated pixels
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    # Connect nearby pixels
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    return mask


# ============================================================
# AREA SCORE
# ============================================================

def calculate_area_score(
    mask
):
    """
    Calculate a heuristic area consistency score.

    The score is not an oil probability.
    """

    total_pixels = (
        mask.shape[0]
        *
        mask.shape[1]
    )

    spill_pixels = int(
        np.count_nonzero(
            mask
        )
    )

    if total_pixels == 0:

        return 0.0

    area_percent = (
        spill_pixels
        /
        total_pixels
        *
        100.0
    )

    # Very small region
    if area_percent < 0.1:

        return 0.15

    # Small region
    elif area_percent < 0.5:

        return 0.45

    # Reasonable candidate range
    elif area_percent <= 20.0:

        return 1.0

    # Very large candidate
    elif area_percent <= 40.0:

        return 0.65

    # Extremely large candidate
    else:

        return 0.25


# ============================================================
# CONNECTED COMPONENT ANALYSIS
# ============================================================

def connected_component_analysis(
    mask
):
    """
    Find connected regions in the predicted mask.
    """

    binary = (
        mask > 0
    ).astype(
        np.uint8
    )

    (
        number_of_labels,
        labels,
        stats,
        centroids
    ) = cv2.connectedComponentsWithStats(
        binary,
        connectivity=8
    )

    components = []

    for label in range(
        1,
        number_of_labels
    ):

        area = stats[
            label,
            cv2.CC_STAT_AREA
        ]

        x = stats[
            label,
            cv2.CC_STAT_LEFT
        ]

        y = stats[
            label,
            cv2.CC_STAT_TOP
        ]

        width = stats[
            label,
            cv2.CC_STAT_WIDTH
        ]

        height = stats[
            label,
            cv2.CC_STAT_HEIGHT
        ]

        centroid_x = (
            centroids[label][0]
        )

        centroid_y = (
            centroids[label][1]
        )

        components.append(
            {
                "area": int(area),
                "x": int(x),
                "y": int(y),
                "width": int(width),
                "height": int(height),
                "centroid_x":
                    float(
                        centroid_x
                    ),
                "centroid_y":
                    float(
                        centroid_y
                    )
            }
        )

    components.sort(
        key=lambda item: item[
            "area"
        ],
        reverse=True
    )

    return components


# ============================================================
# FRAGMENTATION SCORE
# ============================================================

def calculate_fragmentation_score(
    components,
    total_spill_pixels
):
    """
    Measure how fragmented the predicted region is.

    Higher score = more coherent detection.
    """

    if total_spill_pixels <= 0:

        return 0.0

    if len(components) == 0:

        return 0.0

    largest_area = (
        components[0]["area"]
    )

    largest_fraction = (
        largest_area
        /
        total_spill_pixels
    )

    component_count = len(
        components
    )

    if (
        largest_fraction >= 0.80
        and component_count <= 5
    ):

        return 1.0

    elif (
        largest_fraction >= 0.60
        and component_count <= 10
    ):

        return 0.80

    elif (
        largest_fraction >= 0.40
        and component_count <= 20
    ):

        return 0.60

    elif component_count <= 40:

        return 0.40

    else:

        return 0.20


# ============================================================
# SHAPE SCORE
# ============================================================

def calculate_shape_score(
    mask
):
    """
    Calculate a shape consistency score using the largest
    connected contour.

    Irregular shapes are allowed.
    """

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:

        return 0.0

    largest_contour = max(
        contours,
        key=cv2.contourArea
    )

    area = cv2.contourArea(
        largest_contour
    )

    perimeter = cv2.arcLength(
        largest_contour,
        True
    )

    if area <= 0:

        return 0.0

    if perimeter <= 0:

        return 0.0

    # Compactness:
    # 1.0 = highly compact
    # lower = increasingly irregular
    compactness = (
        4.0
        *
        np.pi
        *
        area
        /
        (
            perimeter
            *
            perimeter
        )
    )

    compactness = clamp(
        compactness
    )

    if compactness >= 0.65:

        return 0.90

    elif compactness >= 0.40:

        return 1.00

    elif compactness >= 0.20:

        return 0.80

    elif compactness >= 0.10:

        return 0.55

    else:

        return 0.25


# ============================================================
# TEXTURE SCORE
# ============================================================

def calculate_texture_score(
    image,
    mask
):
    """
    Calculate grayscale texture variation inside the
    detected region.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    region = gray[
        mask > 0
    ]

    if region.size < 10:

        return 0.0

    std_value = float(
        np.std(region)
    )

    # --------------------------------------------------------
    # Low variation
    # --------------------------------------------------------

    if std_value < 3.0:

        score = 0.30

    elif std_value < 8.0:

        score = 0.60

    # --------------------------------------------------------
    # Moderate variation
    # --------------------------------------------------------

    elif std_value <= 35.0:

        score = 1.00

    # --------------------------------------------------------
    # High variation
    # --------------------------------------------------------

    elif std_value <= 55.0:

        score = 0.65

    else:

        score = 0.35

    return clamp(
        score
    )


# ============================================================
# BORDER SCORE
# ============================================================

def calculate_border_score(
    mask
):
    """
    Determine how strongly the detection touches image
    boundaries.

    Border contact is only a weak signal and does not
    automatically mean false positive.
    """

    border_pixels = np.concatenate(
        [
            mask[0, :],
            mask[-1, :],
            mask[:, 0],
            mask[:, -1]
        ]
    )

    border_count = int(
        np.count_nonzero(
            border_pixels
        )
    )

    total_mask_pixels = int(
        np.count_nonzero(
            mask
        )
    )

    if total_mask_pixels == 0:

        return 0.0

    ratio = (
        border_count
        /
        total_mask_pixels
    )

    if ratio < 0.05:

        return 1.00

    elif ratio < 0.20:

        return 0.80

    elif ratio < 0.50:

        return 0.55

    else:

        return 0.30


# ============================================================
# FINAL CANDIDATE SCORE
# ============================================================

def calculate_false_positive_score(
    texture_score,
    shape_score,
    fragmentation_score,
    area_score,
    border_score
):
    """
    Calculate final image consistency score.

    Higher score = stronger spill-candidate consistency.

    This is NOT the probability that the object is oil.
    """

    texture_score = clamp(
        texture_score
    )

    shape_score = clamp(
        shape_score
    )

    fragmentation_score = clamp(
        fragmentation_score
    )

    area_score = clamp(
        area_score
    )

    border_score = clamp(
        border_score
    )

    score = (

        0.25
        *
        texture_score

        +

        0.25
        *
        shape_score

        +

        0.20
        *
        fragmentation_score

        +

        0.20
        *
        area_score

        +

        0.10
        *
        border_score
    )

    return round(
        score,
        3
    )


# ============================================================
# CLASSIFY CANDIDATE
# ============================================================

def classify_candidate(
    score
):
    """
    Classify the image-based candidate consistency.
    """

    if score >= 0.70:

        return "HIGH"

    elif score >= 0.45:

        return "MEDIUM"

    else:

        return "LOW"


# ============================================================
# GENERATE REASONS
# ============================================================

def generate_reasons(
    texture_score,
    shape_score,
    fragmentation_score,
    area_score,
    border_score,
    component_count
):
    """
    Generate human-readable explanations.
    """

    reasons = []

    # --------------------------------------------------------
    # Texture
    # --------------------------------------------------------

    if texture_score >= 0.70:

        reasons.append(
            "Detected region has consistent image texture"
        )

    elif texture_score < 0.40:

        reasons.append(
            "Detected region has weak texture consistency"
        )

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    if shape_score >= 0.70:

        reasons.append(
            "Detected region has a coherent spatial shape"
        )

    elif shape_score < 0.40:

        reasons.append(
            "Detected region has weak or highly irregular shape"
        )

    # --------------------------------------------------------
    # Fragmentation
    # --------------------------------------------------------

    if fragmentation_score >= 0.70:

        reasons.append(
            "Detection is concentrated in coherent regions"
        )

    elif fragmentation_score < 0.40:

        reasons.append(
            "Detection is highly fragmented"
        )

    # --------------------------------------------------------
    # Area
    # --------------------------------------------------------

    if area_score >= 0.70:

        reasons.append(
            "Detected area is within the configured candidate range"
        )

    elif area_score < 0.40:

        reasons.append(
            "Detected area is unusually small or large"
        )

    # --------------------------------------------------------
    # Border
    # --------------------------------------------------------

    if border_score < 0.40:

        reasons.append(
            "Candidate strongly touches image boundaries"
        )

    # --------------------------------------------------------
    # Components
    # --------------------------------------------------------

    reasons.append(
        f"Detected {component_count} connected region(s)"
    )

    if len(reasons) == 0:

        reasons.append(
            "No strong image-based evidence available"
        )

    return reasons


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def analyze_false_positive(
    image_path,
    mask,
    probability=None
):
    """
    Run complete false-positive analysis.

    Parameters
    ----------
    image_path : str
        Path to original image.

    mask : numpy.ndarray
        Binary U-Net mask.

    probability : numpy.ndarray, optional
        U-Net probability map.

    Returns
    -------
    dict
        Analysis results.
    """

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = load_image(
        image_path
    )

    # --------------------------------------------------------
    # Validate mask
    # --------------------------------------------------------

    if mask is None:

        raise ValueError(
            "Mask cannot be None."
        )

    mask = np.asarray(
        mask
    )

    # --------------------------------------------------------
    # Remove extra dimensions
    # --------------------------------------------------------

    if mask.ndim == 3:

        mask = mask.squeeze()

    # --------------------------------------------------------
    # Resize if necessary
    # --------------------------------------------------------

    if mask.shape != (
        256,
        256
    ):

        mask = cv2.resize(
            mask.astype(
                np.uint8
            ),
            (256, 256),
            interpolation=cv2.INTER_NEAREST
        )

    # --------------------------------------------------------
    # Convert to binary
    # --------------------------------------------------------

    mask = (
        mask > 0
    ).astype(
        np.uint8
    )

    # --------------------------------------------------------
    # Clean mask
    # --------------------------------------------------------

    cleaned_mask = clean_mask(
        mask
    )

    binary_mask = (
        cleaned_mask > 0
    ).astype(
        np.uint8
    )

    # --------------------------------------------------------
    # Area
    # --------------------------------------------------------

    total_pixels = (
        binary_mask.shape[0]
        *
        binary_mask.shape[1]
    )

    spill_pixels = int(
        np.count_nonzero(
            binary_mask
        )
    )

    if total_pixels == 0:

        return {
            "candidate_score": 0.0,
            "classification": "LOW",
            "spill_area_percent": 0.0,
            "spill_pixels": 0,
            "texture_score": 0.0,
            "shape_score": 0.0,
            "fragmentation_score": 0.0,
            "area_score": 0.0,
            "border_score": 0.0,
            "connected_components": 0,
            "reasons": [
                "Invalid image dimensions"
            ]
        }

    area_percent = (
        spill_pixels
        /
        total_pixels
        *
        100.0
    )

    # --------------------------------------------------------
    # No detection
    # --------------------------------------------------------

    if spill_pixels == 0:

        return {
            "candidate_score": 0.0,
            "classification": "LOW",
            "spill_area_percent": 0.0,
            "spill_pixels": 0,
            "texture_score": 0.0,
            "shape_score": 0.0,
            "fragmentation_score": 0.0,
            "area_score": 0.0,
            "border_score": 0.0,
            "connected_components": 0,
            "reasons": [
                "No detected spill region"
            ]
        }

    # --------------------------------------------------------
    # Connected components
    # --------------------------------------------------------

    components = (
        connected_component_analysis(
            binary_mask
        )
    )

    component_count = len(
        components
    )

    # --------------------------------------------------------
    # Calculate individual scores
    # --------------------------------------------------------

    texture_score = (
        calculate_texture_score(
            image,
            binary_mask
        )
    )

    shape_score = (
        calculate_shape_score(
            cleaned_mask
        )
    )

    fragmentation_score = (
        calculate_fragmentation_score(
            components,
            spill_pixels
        )
    )

    area_score = (
        calculate_area_score(
            binary_mask
        )
    )

    border_score = (
        calculate_border_score(
            binary_mask
        )
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    candidate_score = (
        calculate_false_positive_score(

            texture_score,

            shape_score,

            fragmentation_score,

            area_score,

            border_score
        )
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    classification = (
        classify_candidate(
            candidate_score
        )
    )

    # --------------------------------------------------------
    # Reasons
    # --------------------------------------------------------

    reasons = generate_reasons(

        texture_score,

        shape_score,

        fragmentation_score,

        area_score,

        border_score,

        component_count
    )

    # --------------------------------------------------------
    # Optional U-Net confidence information
    # --------------------------------------------------------

    probability_mean = None

    if probability is not None:

        probability = np.asarray(
            probability
        )

        if probability.ndim == 3:

            probability = probability.squeeze()

        if probability.shape != (
            256,
            256
        ):

            probability = cv2.resize(
                probability.astype(
                    np.float32
                ),
                (256, 256),
                interpolation=cv2.INTER_LINEAR
            )

        detected_probabilities = (
            probability[
                binary_mask > 0
            ]
        )

        if detected_probabilities.size > 0:

            probability_mean = float(
                np.mean(
                    detected_probabilities
                )
            )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    result = {

        "candidate_score":
            candidate_score,

        "classification":
            classification,

        "spill_area_percent":
            round(
                area_percent,
                3
            ),

        "spill_pixels":
            spill_pixels,

        "texture_score":
            round(
                texture_score,
                3
            ),

        "shape_score":
            round(
                shape_score,
                3
            ),

        "fragmentation_score":
            round(
                fragmentation_score,
                3
            ),

        "area_score":
            round(
                area_score,
                3
            ),

        "border_score":
            round(
                border_score,
                3
            ),

        "connected_components":
            component_count,

        "reasons":
            reasons
    }

    if probability_mean is not None:

        result[
            "mean_unet_probability"
        ] = round(
            probability_mean,
            4
        )

    return result


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n======================================"
    )

    print(
        "       FALSE POSITIVE FILTER"
    )

    print(
        "======================================\n"
    )

    # --------------------------------------------------------
    # Determine project root correctly
    # --------------------------------------------------------

    CURRENT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    PROJECT_ROOT = os.path.dirname(
        os.path.dirname(
            CURRENT_DIR
        )
    )

    # --------------------------------------------------------
    # Image path
    # --------------------------------------------------------

    IMAGE_PATH = os.path.join(
        PROJECT_ROOT,
        "ml",
        "data",
        "processed",
        "images",
        "test",
        "sentinel_100.png"
    )

    # --------------------------------------------------------
    # U-Net mask path
    # --------------------------------------------------------

    MASK_PATH = os.path.join(
        PROJECT_ROOT,
        "ml",
        "data",
        "test",
        "pipeline_outputs",
        "sentinel_100_mask.png"
    )

    # --------------------------------------------------------
    # U-Net probability path
    # --------------------------------------------------------

    PROBABILITY_PATH = os.path.join(
        PROJECT_ROOT,
        "ml",
        "data",
        "test",
        "pipeline_outputs",
        "sentinel_100_probability.png"
    )

    # --------------------------------------------------------
    # Print paths
    # --------------------------------------------------------

    print(
        "Project root:"
    )

    print(
        PROJECT_ROOT
    )

    print(
        "\nImage:"
    )

    print(
        IMAGE_PATH
    )

    print(
        "\nMask:"
    )

    print(
        MASK_PATH
    )

    # --------------------------------------------------------
    # Check image
    # --------------------------------------------------------

    image = cv2.imread(
        IMAGE_PATH
    )

    if image is None:

        raise FileNotFoundError(
            "\nImage not found:\n"
            f"{IMAGE_PATH}"
        )

    # --------------------------------------------------------
    # Check mask
    # --------------------------------------------------------

    mask = cv2.imread(
        MASK_PATH,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:

        raise FileNotFoundError(
            "\nU-Net mask not found:\n"
            f"{MASK_PATH}"
            "\n\n"
            "Run this first:\n"
            "python ml\\src\\ml_pipeline.py"
        )

    # --------------------------------------------------------
    # Optional probability map
    # --------------------------------------------------------

    probability = None

    if os.path.exists(
        PROBABILITY_PATH
    ):

        probability_image = cv2.imread(
            PROBABILITY_PATH,
            cv2.IMREAD_GRAYSCALE
        )

        if probability_image is not None:

            probability = (
                probability_image.astype(
                    np.float32
                )
                /
                255.0
            )

    # --------------------------------------------------------
    # Run analysis
    # --------------------------------------------------------

    result = analyze_false_positive(

        IMAGE_PATH,

        mask,

        probability
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print(
        "\n--------------------------------------"
    )

    print(
        "      FALSE-POSITIVE ANALYSIS"
    )

    print(
        "--------------------------------------"
    )

    print(
        f"\nCandidate score: "
        f"{result['candidate_score'] * 100:.2f}%"
    )

    print(
        f"Classification: "
        f"{result['classification']}"
    )

    print(
        f"Spill area: "
        f"{result['spill_area_percent']:.2f}%"
    )

    print(
        f"Spill pixels: "
        f"{result['spill_pixels']}"
    )

    print(
        f"Connected components: "
        f"{result['connected_components']}"
    )

    # --------------------------------------------------------
    # U-Net probability
    # --------------------------------------------------------

    if (
        "mean_unet_probability"
        in result
    ):

        print(
            f"Mean U-Net probability: "
            f"{result['mean_unet_probability'] * 100:.2f}%"
        )

    # --------------------------------------------------------
    # Individual scores
    # --------------------------------------------------------

    print(
        "\nIndividual scores:"
    )

    print(
        f"  Texture       : "
        f"{result['texture_score'] * 100:.2f}"
    )

    print(
        f"  Shape         : "
        f"{result['shape_score'] * 100:.2f}"
    )

    print(
        f"  Fragmentation : "
        f"{result['fragmentation_score'] * 100:.2f}"
    )

    print(
        f"  Area          : "
        f"{result['area_score'] * 100:.2f}"
    )

    print(
        f"  Border        : "
        f"{result['border_score'] * 100:.2f}"
    )

    # --------------------------------------------------------
    # Reasons
    # --------------------------------------------------------

    print(
        "\nReasons:"
    )

    for reason in result[
        "reasons"
    ]:

        print(
            f"  - {reason}"
        )

    # --------------------------------------------------------
    # Final interpretation
    # --------------------------------------------------------

    print(
        "\n--------------------------------------"
    )

    if result[
        "classification"
    ] == "HIGH":

        print(
            "Decision: "
            "STRONG SPILL CANDIDATE"
        )

    elif result[
        "classification"
    ] == "MEDIUM":

        print(
            "Decision: "
            "REQUIRES ADDITIONAL EVIDENCE"
        )

    else:

        print(
            "Decision: "
            "POSSIBLE FALSE POSITIVE / LOOK-ALIKE"
        )

    print(
        "--------------------------------------"
    )

    print(
        "\n======================================"
    )

    print(
        "          TEST COMPLETED"
    )

    print(
        "======================================"
    )