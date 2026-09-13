# ============================================================
# SPECTRAL ANALYSIS
# ============================================================
#
# SIH 26143
#
# Purpose:
# Analyze the detected spill region using available spectral
# information.
#
# CURRENT VERSION:
# Works with RGB imagery as a spectral proxy.
#
# IMPORTANT:
# RGB alone is NOT sufficient for reliable chemical
# identification or scientifically validated light/medium/heavy
# oil classification.
#
# Therefore, when only RGB data is available, the module
# reports:
#
#     INSUFFICIENT_MULTISPECTRAL_DATA
#
# rather than inventing an oil category.
#
# FUTURE:
# When Sentinel-2 multispectral bands are supplied, the module
# can use actual reflectance bands and spectral indices.
#
# ============================================================

import os

import cv2
import numpy as np


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ML_SRC_DIR = CURRENT_DIR

ML_DIR = os.path.dirname(
    ML_SRC_DIR
)

PROJECT_ROOT = os.path.dirname(
    ML_DIR
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "ml",
    "data",
    "test",
    "pipeline_outputs"
)


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = 256

MIN_REGION_PIXELS = 20


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):
    """
    Clamp a value between minimum and maximum.
    """

    try:

        value = float(
            value
        )

    except Exception:

        return minimum

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def safe_mean(
    values
):
    """
    Calculate a safe mean.
    """

    values = np.asarray(
        values
    )

    if values.size == 0:

        return 0.0

    return float(
        np.mean(
            values
        )
    )


def safe_std(
    values
):
    """
    Calculate a safe standard deviation.
    """

    values = np.asarray(
        values
    )

    if values.size == 0:

        return 0.0

    return float(
        np.std(
            values
        )
    )


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(
    image_path
):
    """
    Load RGB image.
    """

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise FileNotFoundError(
            "\nCould not load image:\n"
            f"{image_path}"
        )

    image = cv2.resize(
        image,
        (
            IMAGE_SIZE,
            IMAGE_SIZE
        ),
        interpolation=cv2.INTER_AREA
    )

    return image


# ============================================================
# PREPARE MASK
# ============================================================

def prepare_mask(
    mask
):
    """
    Convert input mask to binary 256x256 mask.
    """

    if mask is None:

        raise ValueError(
            "Mask cannot be None."
        )

    mask = np.asarray(
        mask
    )

    # --------------------------------------------------------
    # Remove channel dimension
    # --------------------------------------------------------

    if mask.ndim == 3:

        mask = mask.squeeze()

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    if mask.shape != (
        IMAGE_SIZE,
        IMAGE_SIZE
    ):

        mask = cv2.resize(
            mask.astype(
                np.uint8
            ),
            (
                IMAGE_SIZE,
                IMAGE_SIZE
            ),
            interpolation=cv2.INTER_NEAREST
        )

    # --------------------------------------------------------
    # Binary
    # --------------------------------------------------------

    mask = (
        mask > 0
    ).astype(
        np.uint8
    )

    return mask


# ============================================================
# RGB STATISTICS
# ============================================================

def calculate_rgb_statistics(
    image,
    mask
):
    """
    Calculate RGB statistics inside detected spill region.

    OpenCV loads BGR.
    """

    region = (
        image[
            mask > 0
        ]
    )

    if region.shape[0] < MIN_REGION_PIXELS:

        return {

            "region_pixels":
                int(
                    region.shape[0]
                ),

            "mean_red":
                0.0,

            "mean_green":
                0.0,

            "mean_blue":
                0.0,

            "std_red":
                0.0,

            "std_green":
                0.0,

            "std_blue":
                0.0,

            "mean_intensity":
                0.0,

            "intensity_std":
                0.0
        }

    blue = region[
        :,
        0
    ].astype(
        np.float32
    )

    green = region[
        :,
        1
    ].astype(
        np.float32
    )

    red = region[
        :,
        2
    ].astype(
        np.float32
    )

    intensity = (
        0.299
        *
        red
        +

        0.587
        *
        green
        +

        0.114
        *
        blue
    )

    return {

        "region_pixels":
            int(
                region.shape[0]
            ),

        "mean_red":
            safe_mean(
                red
            ),

        "mean_green":
            safe_mean(
                green
            ),

        "mean_blue":
            safe_mean(
                blue
            ),

        "std_red":
            safe_std(
                red
            ),

        "std_green":
            safe_std(
                green
            ),

        "std_blue":
            safe_std(
                blue
            ),

        "mean_intensity":
            safe_mean(
                intensity
            ),

        "intensity_std":
            safe_std(
                intensity
            )
    }


# ============================================================
# RGB RATIOS
# ============================================================

def calculate_rgb_ratios(
    statistics
):
    """
    Calculate normalized RGB relationships.

    These are image descriptors only.
    """

    red = float(
        statistics[
            "mean_red"
        ]
    )

    green = float(
        statistics[
            "mean_green"
        ]
    )

    blue = float(
        statistics[
            "mean_blue"
        ]
    )

    total = (
        red
        +
        green
        +
        blue
        +
        1e-6
    )

    return {

        "red_ratio":
            red
            /
            total,

        "green_ratio":
            green
            /
            total,

        "blue_ratio":
            blue
            /
            total,

        "red_blue_difference":
            abs(
                red
                -
                blue
            )
            /
            255.0,

        "green_blue_difference":
            abs(
                green
                -
                blue
            )
            /
            255.0
    }


# ============================================================
# DARK REGION SCORE
# ============================================================

def calculate_dark_region_score(
    statistics
):
    """
    Estimate how dark the detected region is.

    This is useful as an image descriptor, but darkness alone
    does NOT indicate oil.
    """

    intensity = float(
        statistics[
            "mean_intensity"
        ]
    )

    # 0 -> very bright
    # 1 -> very dark

    score = (
        1.0
        -
        clamp(
            intensity
            /
            255.0
        )
    )

    return clamp(
        score
    )


# ============================================================
# SPECTRAL-CONTRAST PROXY
# ============================================================

def calculate_contrast_proxy(
    statistics
):
    """
    Calculate an RGB contrast descriptor.

    This is NOT a real multispectral index.
    """

    red = float(
        statistics[
            "mean_red"
        ]
    )

    green = float(
        statistics[
            "mean_green"
        ]
    )

    blue = float(
        statistics[
            "mean_blue"
        ]
    )

    maximum = max(
        red,
        green,
        blue
    )

    minimum = min(
        red,
        green,
        blue
    )

    if maximum <= 0:

        return 0.0

    contrast = (
        maximum
        -
        minimum
    ) / 255.0

    return clamp(
        contrast
    )


# ============================================================
# TEXTURE PROXY
# ============================================================

def calculate_texture_proxy(
    statistics
):
    """
    Calculate intensity variation.

    Higher value = more texture variation.
    """

    standard_deviation = float(
        statistics[
            "intensity_std"
        ]
    )

    return clamp(
        standard_deviation
        /
        64.0
    )


# ============================================================
# RGB SPECTRAL PROXY SCORE
# ============================================================

def calculate_rgb_proxy_score(
    statistics,
    ratios
):
    """
    Calculate a descriptor score from RGB information.

    IMPORTANT:
    This is NOT an oil probability.
    """

    dark_score = (
        calculate_dark_region_score(
            statistics
        )
    )

    contrast_score = (
        calculate_contrast_proxy(
            statistics
        )
    )

    texture_score = (
        calculate_texture_proxy(
            statistics
        )
    )

    # The score is intentionally described as a proxy.
    #
    # It should NOT be converted directly into:
    #
    # light oil
    # medium oil
    # heavy oil
    #
    # without actual multispectral data.

    score = (

        0.40
        *
        dark_score

        +

        0.30
        *
        contrast_score

        +

        0.30
        *
        texture_score
    )

    return clamp(
        score
    )


# ============================================================
# MULTISPECTRAL AVAILABILITY
# ============================================================

def check_multispectral_data(
    multispectral_data
):
    """
    Check whether actual multispectral bands are available.

    Expected future format:

        {
            "B02": array,
            "B03": array,
            "B04": array,
            "B08": array,
            ...
        }
    """

    if multispectral_data is None:

        return False

    if not isinstance(
        multispectral_data,
        dict
    ):

        return False

    # At least four actual bands should be available for the
    # multispectral branch of this prototype.

    available_bands = [
        band
        for band, value
        in multispectral_data.items()
        if value is not None
    ]

    return (
        len(
            available_bands
        )
        >=
        4
    )


# ============================================================
# PROBABLE OIL CATEGORY
# ============================================================

def classify_probable_oil_category(
    multispectral_data=None
):
    """
    Return probable oil category ONLY when actual
    multispectral data is supplied.

    Current RGB-only pipeline does not attempt to guess
    the chemical category.
    """

    if not check_multispectral_data(
        multispectral_data
    ):

        return {

            "probable_oil_category":
                "INSUFFICIENT_MULTISPECTRAL_DATA",

            "category_confidence":
                0.0,

            "category_reason":
                (
                    "Only RGB imagery is available. "
                    "Actual multispectral bands are required "
                    "for a defensible probable oil-category "
                    "assessment."
                )
        }

    # --------------------------------------------------------
    # Future implementation
    # --------------------------------------------------------
    #
    # Actual Sentinel-2 reflectance bands will be processed
    # here using validated spectral features.
    #
    # We deliberately do not invent chemical classification
    # rules from RGB data.
    # --------------------------------------------------------

    return {

        "probable_oil_category":
            "MULTISPECTRAL_ANALYSIS_PENDING",

        "category_confidence":
            0.0,

        "category_reason":
            (
                "Multispectral data detected, but the "
                "validated oil-category classifier has not "
                "yet been trained."
            )
    }


# ============================================================
# COMPLETE SPECTRAL ANALYSIS
# ============================================================

def analyze_spectral_features(
    image_path,
    mask,
    multispectral_data=None
):
    """
    Run complete spectral/proxy analysis.
    """

    image = load_image(
        image_path
    )

    mask = prepare_mask(
        mask
    )

    statistics = (
        calculate_rgb_statistics(
            image,
            mask
        )
    )

    ratios = (
        calculate_rgb_ratios(
            statistics
        )
    )

    proxy_score = (
        calculate_rgb_proxy_score(
            statistics,
            ratios
        )
    )

    category = (
        classify_probable_oil_category(
            multispectral_data
        )
    )

    # --------------------------------------------------------
    # Interpretation
    # --------------------------------------------------------

    if (
        statistics[
            "region_pixels"
        ]
        <
        MIN_REGION_PIXELS
    ):

        interpretation = (
            "Insufficient detected-region pixels "
            "for spectral analysis."
        )

    elif (
        proxy_score
        >=
        0.70
    ):

        interpretation = (
            "Detected region has strong RGB-based "
            "darkness/contrast/texture characteristics. "
            "This is only a visual proxy and does not "
            "confirm oil."
        )

    elif (
        proxy_score
        >=
        0.45
    ):

        interpretation = (
            "Detected region has moderate RGB-based "
            "spectral/visual characteristics. "
            "Additional multispectral evidence is required."
        )

    else:

        interpretation = (
            "Detected region has weak RGB-based "
            "spectral characteristics for further interpretation."
        )

    return {

        # ----------------------------------------------------
        # RGB statistics
        # ----------------------------------------------------

        "region_pixels":
            statistics[
                "region_pixels"
            ],

        "mean_red":
            round(
                statistics[
                    "mean_red"
                ],
                3
            ),

        "mean_green":
            round(
                statistics[
                    "mean_green"
                ],
                3
            ),

        "mean_blue":
            round(
                statistics[
                    "mean_blue"
                ],
                3
            ),

        "std_red":
            round(
                statistics[
                    "std_red"
                ],
                3
            ),

        "std_green":
            round(
                statistics[
                    "std_green"
                ],
                3
            ),

        "std_blue":
            round(
                statistics[
                    "std_blue"
                ],
                3
            ),

        "mean_intensity":
            round(
                statistics[
                    "mean_intensity"
                ],
                3
            ),

        "intensity_std":
            round(
                statistics[
                    "intensity_std"
                ],
                3
            ),

        # ----------------------------------------------------
        # Ratios
        # ----------------------------------------------------

        "red_ratio":
            round(
                ratios[
                    "red_ratio"
                ],
                4
            ),

        "green_ratio":
            round(
                ratios[
                    "green_ratio"
                ],
                4
            ),

        "blue_ratio":
            round(
                ratios[
                    "blue_ratio"
                ],
                4
            ),

        "red_blue_difference":
            round(
                ratios[
                    "red_blue_difference"
                ],
                4
            ),

        "green_blue_difference":
            round(
                ratios[
                    "green_blue_difference"
                ],
                4
            ),

        # ----------------------------------------------------
        # Proxy scores
        # ----------------------------------------------------

        "dark_region_score":
            round(
                calculate_dark_region_score(
                    statistics
                ),
                4
            ),

        "contrast_proxy_score":
            round(
                calculate_contrast_proxy(
                    statistics
                ),
                4
            ),

        "texture_proxy_score":
            round(
                calculate_texture_proxy(
                    statistics
                ),
                4
            ),

        "rgb_spectral_proxy_score":
            round(
                proxy_score,
                4
            ),

        # ----------------------------------------------------
        # Oil category
        # ----------------------------------------------------

        "probable_oil_category":
            category[
                "probable_oil_category"
            ],

        "category_confidence":
            category[
                "category_confidence"
            ],

        "category_reason":
            category[
                "category_reason"
            ],

        # ----------------------------------------------------
        # Interpretation
        # ----------------------------------------------------

        "interpretation":
            interpretation
    }


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    result
):

    print(
        "\n======================================"
    )

    print(
        "         SPECTRAL ANALYSIS"
    )

    print(
        "======================================"
    )

    print(
        f"\nDetected region pixels: "
        f"{result['region_pixels']}"
    )

    print(
        "\nRGB statistics:"
    )

    print(
        f"  Mean Red       : "
        f"{result['mean_red']:.3f}"
    )

    print(
        f"  Mean Green     : "
        f"{result['mean_green']:.3f}"
    )

    print(
        f"  Mean Blue      : "
        f"{result['mean_blue']:.3f}"
    )

    print(
        f"  Mean intensity : "
        f"{result['mean_intensity']:.3f}"
    )

    print(
        f"  Intensity std  : "
        f"{result['intensity_std']:.3f}"
    )

    print(
        "\nRGB ratios:"
    )

    print(
        f"  Red ratio      : "
        f"{result['red_ratio']:.4f}"
    )

    print(
        f"  Green ratio    : "
        f"{result['green_ratio']:.4f}"
    )

    print(
        f"  Blue ratio     : "
        f"{result['blue_ratio']:.4f}"
    )

    print(
        "\nProxy scores:"
    )

    print(
        f"  Dark region    : "
        f"{result['dark_region_score'] * 100:.2f}"
    )

    print(
        f"  Contrast proxy : "
        f"{result['contrast_proxy_score'] * 100:.2f}"
    )

    print(
        f"  Texture proxy  : "
        f"{result['texture_proxy_score'] * 100:.2f}"
    )

    print(
        f"  RGB proxy      : "
        f"{result['rgb_spectral_proxy_score'] * 100:.2f}"
    )

    print(
        "\nProbable oil category:"
    )

    print(
        f"  {result['probable_oil_category']}"
    )

    print(
        f"Category confidence: "
        f"{result['category_confidence'] * 100:.2f}%"
    )

    print(
        "\nCategory reason:"
    )

    print(
        f"  {result['category_reason']}"
    )

    print(
        "\nInterpretation:"
    )

    print(
        f"  {result['interpretation']}"
    )

    print(
        "\n======================================"
    )


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n======================================"
    )

    print(
        "       SPECTRAL ANALYSIS TEST"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Input image
    # --------------------------------------------------------

    image_path = os.path.join(
        PROJECT_ROOT,
        "ml",
        "data",
        "processed",
        "images",
        "test",
        "sentinel_100.png"
    )

    # --------------------------------------------------------
    # U-Net mask
    # --------------------------------------------------------

    mask_path = os.path.join(
        OUTPUT_DIR,
        "sentinel_100_mask.png"
    )

    # --------------------------------------------------------
    # Check image
    # --------------------------------------------------------

    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            "\nImage not found:\n"
            f"{image_path}"
        )

    # --------------------------------------------------------
    # Check mask
    # --------------------------------------------------------

    if not os.path.exists(
        mask_path
    ):

        raise FileNotFoundError(
            "\nMask not found:\n"
            f"{mask_path}\n\n"
            "Run this first:\n"
            "python ml\\src\\ml_pipeline.py"
        )

    # --------------------------------------------------------
    # Load mask
    # --------------------------------------------------------

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:

        raise ValueError(
            "\nCould not read mask:\n"
            f"{mask_path}"
        )

    # --------------------------------------------------------
    # Run analysis
    # --------------------------------------------------------

    result = analyze_spectral_features(

        image_path,

        mask
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    display_results(
        result
    )

    print(
        "\n======================================"
    )

    print(
        "       TEST COMPLETED"
    )

    print(
        "======================================"
    )