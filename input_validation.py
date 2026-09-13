# ============================================================
# SIH 26143 - INPUT VALIDATION / MODALITY GATE
# ============================================================
#
# Purpose:
# Reject unsupported satellite imagery BEFORE U-Net inference.
#
# Current U-Net was trained on the available Deep-SAR style
# dataset. We therefore do not allow strongly colorful optical
# images to be treated as normal U-Net input.
#
# This is a safety/rejection gate, NOT an oil classifier.
#
# ============================================================

import cv2
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum average channel difference allowed before the image
# is considered strongly colorful / optical-like.

MAX_MEAN_CHANNEL_DIFFERENCE = 12.0

# Percentage of pixels that must have a noticeable RGB
# difference before the image is considered strongly colorful.

MAX_COLORFUL_PIXEL_PERCENT = 15.0

# If fewer than this percentage of pixels contain useful
# non-dark information, the image may be too empty/dark.

MIN_NON_DARK_PERCENT = 5.0


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(
    image_path
):
    """
    Load an image using OpenCV.
    """

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise ValueError(
            f"Could not read image:\n{image_path}"
        )

    return image


# ============================================================
# ANALYZE COLOR
# ============================================================

def calculate_color_statistics(
    image
):
    """
    Calculate RGB/BGR colorfulness statistics.

    Returns:
        mean_channel_difference
        colorful_pixel_percent
        channel_correlation
    """

    image_float = (
        image.astype(
            np.float32
        )
    )

    blue = image_float[
        :,
        :,
        0
    ]

    green = image_float[
        :,
        :,
        1
    ]

    red = image_float[
        :,
        :,
        2
    ]

    # --------------------------------------------------------
    # Average difference between channels
    # --------------------------------------------------------

    diff_bg = np.abs(
        blue - green
    )

    diff_br = np.abs(
        blue - red
    )

    diff_gr = np.abs(
        green - red
    )

    mean_channel_difference = float(
        (
            diff_bg.mean()
            +
            diff_br.mean()
            +
            diff_gr.mean()
        )
        /
        3.0
    )

    # --------------------------------------------------------
    # Colorful pixel percentage
    # --------------------------------------------------------

    maximum_channel = np.maximum.reduce(
        [
            blue,
            green,
            red
        ]
    )

    minimum_channel = np.minimum.reduce(
        [
            blue,
            green,
            red
        ]
    )

    pixel_difference = (
        maximum_channel
        -
        minimum_channel
    )

    colorful_pixels = (
        pixel_difference
        >
        20.0
    )

    colorful_pixel_percent = float(
        colorful_pixels.mean()
        *
        100.0
    )

    # --------------------------------------------------------
    # Channel correlation
    # --------------------------------------------------------

    flat_blue = blue.flatten()

    flat_green = green.flatten()

    flat_red = red.flatten()

    try:

        correlation_matrix = np.corrcoef(
            [
                flat_blue,
                flat_green,
                flat_red
            ]
        )

        channel_correlation = float(
            (
                correlation_matrix[
                    0,
                    1
                ]
                +
                correlation_matrix[
                    0,
                    2
                ]
                +
                correlation_matrix[
                    1,
                    2
                ]
            )
            /
            3.0
        )

    except Exception:

        channel_correlation = 0.0

    return {

        "mean_channel_difference":
            mean_channel_difference,

        "colorful_pixel_percent":
            colorful_pixel_percent,

        "channel_correlation":
            channel_correlation
    }


# ============================================================
# IMAGE QUALITY
# ============================================================

def calculate_quality_statistics(
    image
):
    """
    Basic image-quality measurements.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    mean_intensity = float(
        gray.mean()
    )

    intensity_std = float(
        gray.std()
    )

    non_dark_percent = float(
        (
            gray
            >
            10
        ).mean()
        *
        100.0
    )

    return {

        "mean_intensity":
            mean_intensity,

        "intensity_std":
            intensity_std,

        "non_dark_percent":
            non_dark_percent
    }


# ============================================================
# DETERMINE MODALITY
# ============================================================

def classify_input(
    image
):
    """
    Determine whether the current U-Net should process
    the image.

    Supported:
        GRAYSCALE_LIKE

    Rejected:
        STRONGLY_COLORFUL_OPTICAL

    The rejection is based on compatibility with the current
    training domain, not on whether the image contains oil.
    """

    color_stats = (
        calculate_color_statistics(
            image
        )
    )

    quality_stats = (
        calculate_quality_statistics(
            image
        )
    )

    mean_channel_difference = (
        color_stats[
            "mean_channel_difference"
        ]
    )

    colorful_pixel_percent = (
        color_stats[
            "colorful_pixel_percent"
        ]
    )

    non_dark_percent = (
        quality_stats[
            "non_dark_percent"
        ]
    )

    # --------------------------------------------------------
    # Very colorful image
    # --------------------------------------------------------

    strongly_colorful = (
        mean_channel_difference
        >
        MAX_MEAN_CHANNEL_DIFFERENCE
        and
        colorful_pixel_percent
        >
        MAX_COLORFUL_PIXEL_PERCENT
    )

    # --------------------------------------------------------
    # Too little useful information
    # --------------------------------------------------------

    too_dark = (
        non_dark_percent
        <
        MIN_NON_DARK_PERCENT
    )

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    if strongly_colorful:

        return {

            "accepted":
                False,

            "modality":
                "STRONGLY_COLORFUL_OPTICAL",

            "reason":
                (
                    "Image has strong RGB differences and "
                    "appears outside the current U-Net "
                    "training domain."
                ),

            "color_statistics":
                color_stats,

            "quality_statistics":
                quality_stats,

            "recommendation":
                (
                    "Use imagery compatible with the "
                    "trained SAR model or provide a "
                    "model trained specifically for "
                    "optical/multispectral imagery."
                )
        }

    if too_dark:

        return {

            "accepted":
                False,

            "modality":
                "LOW_INFORMATION",

            "reason":
                (
                    "Image contains very little "
                    "non-dark information."
                ),

            "color_statistics":
                color_stats,

            "quality_statistics":
                quality_stats,

            "recommendation":
                (
                    "Check image quality before "
                    "running spill detection."
                )
        }

    return {

        "accepted":
            True,

        "modality":
            "GRAYSCALE_LIKE",

        "reason":
            (
                "Image is compatible with the current "
                "U-Net input characteristics."
            ),

        "color_statistics":
            color_stats,

        "quality_statistics":
            quality_stats,

        "recommendation":
            (
                "Proceed with the current U-Net model."
            )
    }


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def validate_image(
    image_path
):
    """
    Main validation function.
    """

    image = load_image(
        image_path
    )

    result = classify_input(
        image
    )

    result[
        "image_shape"
    ] = list(
        image.shape
    )

    return result


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    import os
    import sys

    print(
        "\n======================================"
    )

    print(
        "       INPUT VALIDATION TEST"
    )

    print(
        "======================================"
    )

    if len(
        sys.argv
    ) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python input_validation.py <image_path>"
        )

        print(
            "\nExample:"
        )

        print(
            "python input_validation.py "
            "C:\\path\\to\\sentinel_811.png"
        )

        sys.exit(
            1
        )

    image_path = sys.argv[
        1
    ]

    if not os.path.exists(
        image_path
    ):

        print(
            "\nFile not found:"
        )

        print(
            image_path
        )

        sys.exit(
            1
        )

    result = validate_image(
        image_path
    )

    print(
        f"\nAccepted:"
        f" {result['accepted']}"
    )

    print(
        f"Modality:"
        f" {result['modality']}"
    )

    print(
        f"Reason:"
        f" {result['reason']}"
    )

    print(
        "\nColor statistics:"
    )

    for key, value in result[
        "color_statistics"
    ].items():

        print(
            f"  {key}: {value:.4f}"
        )

    print(
        "\nQuality statistics:"
    )

    for key, value in result[
        "quality_statistics"
    ].items():

        print(
            f"  {key}: {value:.4f}"
        )

    print(
        "\nRecommendation:"
    )

    print(
        f"  {result['recommendation']}"
    )

    print(
        "\n======================================"
    )