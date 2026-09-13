import os
import sys
import uuid
import json
import shutil
import importlib.util
from contextlib import asynccontextmanager
from io import BytesIO

import cv2
import numpy as np
import pandas as pd
import torch

from PIL import Image, UnidentifiedImageError

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


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

OUTPUT_ROOT = os.path.join(
    ML_DIR,
    "data",
    "api_outputs"
)

MODEL_PATH = os.path.join(
    ML_DIR,
    "models",
    "spill_detector",
    "best_unet_oil_spill_stable.pth"
)

BEHAVIOUR_FILE = os.path.join(
    PROJECT_ROOT,
    "ais",
    "data",
    "behaviour_anomaly_results.csv"
)

FINAL_BEHAVIOUR_FILE = os.path.join(
    PROJECT_ROOT,
    "ais",
    "data",
    "final_behaviour_scores.csv"
)

os.makedirs(
    OUTPUT_ROOT,
    exist_ok=True
)


# ============================================================
# CONFIG
# ============================================================

API_VERSION = "5.1.0"

MAX_UPLOAD_SIZE_MB = int(
    os.getenv(
        "MAX_UPLOAD_SIZE_MB",
        "25"
    )
)

MAX_UPLOAD_SIZE = (
    MAX_UPLOAD_SIZE_MB
    * 1024
    * 1024
)

DEFAULT_LATITUDE = 30.36441

DEFAULT_LONGITUDE = -89.08701

DEFAULT_EVENT_TIME = (
    "2024-01-01 00:03:15"
)


# ============================================================
# GLOBALS
# ============================================================

MODULES = {}

MODEL = None

DEVICE = None


# ============================================================
# IMPORT MODULE
# ============================================================

def import_module_from_path(
    module_name,
    file_path
):

    if not os.path.exists(
        file_path
    ):

        raise RuntimeError(
            f"Required module not found:\n{file_path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path
    )

    if spec is None:

        raise RuntimeError(
            f"Could not create module spec:\n{file_path}"
        )

    if spec.loader is None:

        raise RuntimeError(
            f"Could not create module loader:\n{file_path}"
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

    print(
        "\nLoading ML modules..."
    )

    modules = {

        "unet":
            import_module_from_path(
                "sih_unet_api",
                os.path.join(
                    CURRENT_DIR,
                    "unet.py"
                )
            ),

        "false_positive":
            import_module_from_path(
                "sih_false_positive_api",
                os.path.join(
                    CURRENT_DIR,
                    "false_positive.py"
                )
            ),

        "spectral":
            import_module_from_path(
                "sih_spectral_api",
                os.path.join(
                    CURRENT_DIR,
                    "spectral_analysis.py"
                )
            ),

        "evidence":
            import_module_from_path(
                "sih_evidence_api",
                os.path.join(
                    CURRENT_DIR,
                    "evidence_fusion.py"
                )
            )
    }

    print(
        "ML modules loaded successfully."
    )

    return modules


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    global MODEL
    global DEVICE

    if torch.cuda.is_available():

        DEVICE = torch.device(
            "cuda"
        )

    else:

        DEVICE = torch.device(
            "cpu"
        )

    print(
        f"\nDevice: {DEVICE}"
    )

    if torch.cuda.is_available():

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    if not os.path.exists(
        MODEL_PATH
    ):

        raise RuntimeError(
            f"U-Net model not found:\n{MODEL_PATH}"
        )

    MODEL = (
        MODULES[
            "unet"
        ]
        .UNet()
        .to(
            DEVICE
        )
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    if (
        isinstance(
            checkpoint,
            dict
        )
        and
        "state_dict" in checkpoint
    ):

        state_dict = (
            checkpoint[
                "state_dict"
            ]
        )

    else:

        state_dict = checkpoint

    cleaned_state_dict = {}

    for key, value in state_dict.items():

        if key.startswith(
            "module."
        ):

            key = key[
                7:
            ]

        cleaned_state_dict[
            key
        ] = value

    MODEL.load_state_dict(
        cleaned_state_dict
    )

    MODEL.eval()

    print(
        "U-Net model loaded successfully."
    )


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(
    app
):

    global MODULES

    MODULES = load_modules()

    load_model()

    print(
        "\n=========================================="
    )

    print(
        "       SIH 26143 ML API READY"
    )

    print(
        "=========================================="
    )

    print(
        f"API version: {API_VERSION}"
    )

    print(
        "Swagger upload support: ENABLED"
    )

    print(
        "=========================================="
    )

    yield

    global MODEL

    MODEL = None


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="SIH 26143 Oil Spill Detection API",
    description=(
        "AI-assisted maritime oil spill detection, "
        "AIS correlation and vessel investigation ranking."
    ),
    version=API_VERSION,
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# STATIC OUTPUTS
# ============================================================

app.mount(
    "/outputs",
    StaticFiles(
        directory=OUTPUT_ROOT
    ),
    name="outputs"
)


# ============================================================
# JSON SAFE
# ============================================================

def make_json_safe(
    value
):

    if isinstance(
        value,
        dict
    ):

        return {
            str(key):
                make_json_safe(
                    item
                )
            for key, item in value.items()
        }

    if isinstance(
        value,
        list
    ):

        return [
            make_json_safe(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        tuple
    ):

        return [
            make_json_safe(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        np.integer
    ):

        return int(
            value
        )

    if isinstance(
        value,
        np.floating
    ):

        return float(
            value
        )

    if isinstance(
        value,
        np.bool_
    ):

        return bool(
            value
        )

    if value is None:

        return None

    try:

        if pd.isna(
            value
        ):

            return None

    except Exception:

        pass

    return value


# ============================================================
# IMAGE DECODER
# ============================================================

async def read_upload(
    upload: UploadFile
):
    """
    Read and validate an uploaded image.

    Returns:
        BGR image,
        original filename,
        content type,
        byte count
    """

    if upload is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "No image file was provided."
            )
        )

    filename = (
        upload.filename
        or
        "uploaded_image"
    )

    content_type = (
        upload.content_type
        or
        "unknown"
    )

    print(
        "\n=========================================="
    )

    print(
        "IMAGE UPLOAD RECEIVED"
    )

    print(
        "=========================================="
    )

    print(
        f"Filename: {filename}"
    )

    print(
        f"Content type: {content_type}"
    )

    # --------------------------------------------------------
    # Read all bytes
    # --------------------------------------------------------

    try:

        file_bytes = await upload.read()

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not read uploaded file: {error}"
            )
        )

    size_bytes = len(
        file_bytes
    )

    print(
        f"Uploaded bytes: {size_bytes:,}"
    )

    # --------------------------------------------------------
    # Empty file
    # --------------------------------------------------------

    if size_bytes == 0:

        raise HTTPException(
            status_code=400,
            detail={
                "error":
                    "EMPTY_UPLOAD",

                "message":
                    "The uploaded file contains 0 bytes.",

                "filename":
                    filename
            }
        )

    # --------------------------------------------------------
    # Size limit
    # --------------------------------------------------------

    if size_bytes > MAX_UPLOAD_SIZE:

        raise HTTPException(
            status_code=413,
            detail={
                "error":
                    "FILE_TOO_LARGE",

                "message":
                    (
                        f"Maximum file size is "
                        f"{MAX_UPLOAD_SIZE_MB} MB."
                    ),

                "received_bytes":
                    size_bytes
            }
        )

    # --------------------------------------------------------
    # File signature
    # --------------------------------------------------------

    first_bytes = file_bytes[
        :16
    ]

    print(
        f"First bytes: {first_bytes!r}"
    )

    # ========================================================
    # PILLOW
    # ========================================================

    try:

        print(
            "\nTrying Pillow decoder..."
        )

        pil_image = Image.open(
            BytesIO(
                file_bytes
            )
        )

        pil_image.load()

        image_format = (
            pil_image.format
            or
            "UNKNOWN"
        )

        image_mode = (
            pil_image.mode
        )

        image_size = (
            pil_image.size
        )

        print(
            f"Pillow format: {image_format}"
        )

        print(
            f"Pillow mode: {image_mode}"
        )

        print(
            f"Pillow size: {image_size}"
        )

        # ----------------------------------------------------
        # Convert all image modes to RGB.
        # ----------------------------------------------------

        pil_image = pil_image.convert(
            "RGB"
        )

        rgb_array = np.asarray(
            pil_image,
            dtype=np.uint8
        )

        if rgb_array.ndim != 3:

            raise ValueError(
                "Decoded image is not 3-dimensional."
            )

        if rgb_array.shape[
            2
        ] != 3:

            raise ValueError(
                "Decoded image does not have 3 channels."
            )

        # ----------------------------------------------------
        # RGB -> BGR
        # ----------------------------------------------------

        bgr_image = cv2.cvtColor(
            rgb_array,
            cv2.COLOR_RGB2BGR
        )

        print(
            f"Decoded image shape:"
            f" {bgr_image.shape}"
        )

        print(
            "Pillow decoding successful."
        )

        return (
            bgr_image,
            filename,
            content_type,
            size_bytes,
            image_format
        )

    except Exception as error:

        print(
            "\nPillow decoding failed:"
        )

        print(
            repr(
                error
            )
        )

    # ========================================================
    # OPENCV FALLBACK
    # ========================================================

    try:

        print(
            "\nTrying OpenCV decoder..."
        )

        encoded = np.frombuffer(
            file_bytes,
            dtype=np.uint8
        )

        bgr_image = cv2.imdecode(
            encoded,
            cv2.IMREAD_COLOR
        )

        if bgr_image is not None:

            print(
                f"OpenCV shape:"
                f" {bgr_image.shape}"
            )

            print(
                "OpenCV decoding successful."
            )

            return (
                bgr_image,
                filename,
                content_type,
                size_bytes,
                "OPENCV_DECODED"
            )

    except Exception as error:

        print(
            "\nOpenCV decoding failed:"
        )

        print(
            repr(
                error
            )
        )

    # ========================================================
    # FAILED
    # ========================================================

    raise HTTPException(
        status_code=400,
        detail={
            "error":
                "IMAGE_DECODE_FAILED",

            "message":
                (
                    "FastAPI received bytes, but they are "
                    "not a valid decodable image."
                ),

            "filename":
                filename,

            "content_type":
                content_type,

            "size_bytes":
                size_bytes,

            "first_bytes":
                repr(
                    first_bytes
                ),

            "hint":
                (
                    "In Swagger, remove the selected file "
                    "and choose the actual image again."
                )
        }
    )


# ============================================================
# MODEL PREPARATION
# ============================================================

def prepare_model_image(
    bgr_image
):

    resized = cv2.resize(
        bgr_image,
        (
            256,
            256
        ),
        interpolation=cv2.INTER_AREA
    )

    return cv2.cvtColor(
        resized,
        cv2.COLOR_BGR2RGB
    )



# ============================================================
# INPUT DOMAIN VALIDATION
# ============================================================

def validate_input_domain(bgr_image):
    """
    Heuristic domain gate for the current U-Net model.

    The U-Net was trained on grayscale-like SAR imagery.
    This gate rejects obvious strongly colorful optical/RGB images
    before U-Net inference.

    IMPORTANT:
    This is NOT an oil-spill classifier.
    A grayscale image can still be a non-spill image.
    """

    if bgr_image is None:
        return {
            "accepted": False,
            "modality": "INVALID_IMAGE",
            "reason": "Image could not be decoded.",
            "color_statistics": {},
            "quality_statistics": {}
        }

    rgb = cv2.cvtColor(
        bgr_image,
        cv2.COLOR_BGR2RGB
    ).astype(np.float32)

    # Per-pixel RGB spread.
    channel_difference = (
        np.max(rgb, axis=2)
        -
        np.min(rgb, axis=2)
    )

    mean_channel_difference = float(
        np.mean(channel_difference)
    )

    # Pixels with noticeable RGB separation.
    colorful_pixel_percent = float(
        np.mean(channel_difference > 12.0)
        * 100.0
    )

    # Correlation between RGB channels.
    r = rgb[:, :, 0].reshape(-1)
    g = rgb[:, :, 1].reshape(-1)
    b = rgb[:, :, 2].reshape(-1)

    try:
        channel_correlation = float(
            np.corrcoef(
                r,
                g
            )[0, 1]
            +
            np.corrcoef(
                r,
                b
            )[0, 1]
        ) / 2.0

        if not np.isfinite(
            channel_correlation
        ):
            channel_correlation = 1.0

    except Exception:
        channel_correlation = 1.0

    gray = cv2.cvtColor(
        bgr_image,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    mean_intensity = float(
        np.mean(gray)
    )

    intensity_std = float(
        np.std(gray)
    )

    non_dark_percent = float(
        np.mean(gray > 10.0)
        * 100.0
    )

    # Current modality rules.
    strongly_colorful = (
        mean_channel_difference > 12.0
        and
        colorful_pixel_percent > 15.0
    )

    low_information = (
        non_dark_percent < 5.0
    )

    if strongly_colorful:
        accepted = False
        modality = "STRONGLY_COLORFUL_OPTICAL"
        reason = (
            "Image has strong RGB differences and appears "
            "outside the current U-Net training domain."
        )

    elif low_information:
        accepted = False
        modality = "LOW_INFORMATION"
        reason = (
            "Image contains too little visible information "
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
        "accepted": bool(accepted),
        "modality": modality,
        "reason": reason,
        "color_statistics": {
            "mean_channel_difference":
                mean_channel_difference,
            "colorful_pixel_percent":
                colorful_pixel_percent,
            "channel_correlation":
                channel_correlation
        },
        "quality_statistics": {
            "mean_intensity":
                mean_intensity,
            "intensity_std":
                intensity_std,
            "non_dark_percent":
                non_dark_percent
        }
    }


def print_input_validation_result(validation_result):
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
        f"\nAccepted: "
        f"{validation_result.get('accepted', False)}"
    )

    print(
        f"Modality: "
        f"{validation_result.get('modality', 'UNKNOWN')}"
    )

    print(
        f"Reason: "
        f"{validation_result.get('reason', 'N/A')}"
    )

    color_stats = validation_result.get(
        "color_statistics",
        {}
    )

    quality_stats = validation_result.get(
        "quality_statistics",
        {}
    )

    print(
        "\nColor statistics:"
    )

    print(
        f"  mean_channel_difference: "
        f"{color_stats.get('mean_channel_difference', 0):.4f}"
    )

    print(
        f"  colorful_pixel_percent: "
        f"{color_stats.get('colorful_pixel_percent', 0):.4f}"
    )

    print(
        f"  channel_correlation: "
        f"{color_stats.get('channel_correlation', 0):.4f}"
    )

    print(
        "\nQuality statistics:"
    )

    print(
        f"  mean_intensity: "
        f"{quality_stats.get('mean_intensity', 0):.4f}"
    )

    print(
        f"  intensity_std: "
        f"{quality_stats.get('intensity_std', 0):.4f}"
    )

    print(
        f"  non_dark_percent: "
        f"{quality_stats.get('non_dark_percent', 0):.4f}"
    )


# ============================================================

# ============================================================
# U-NET
# ============================================================

def run_unet(
    rgb_image
):

    image = (
        rgb_image.astype(
            np.float32
        )
        /
        255.0
    )

    tensor = torch.from_numpy(
        image
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
        DEVICE
    )

    with torch.inference_mode():

        output = MODEL(
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
        probability >= 0.5
    ).astype(
        np.uint8
    )

    return (
        probability,
        mask
    )


# ============================================================
# SPILL STATISTICS
# ============================================================

def calculate_spill_statistics(
    probability,
    mask
):

    spill_pixels = int(
        mask.sum()
    )

    total_pixels = int(
        mask.size
    )

    area_percent = (
        spill_pixels
        /
        total_pixels
        *
        100.0
    )

    if spill_pixels:

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

    return {

        "detected":
            bool(
                spill_pixels > 0
            ),

        "spill_pixels":
            spill_pixels,

        "total_pixels":
            total_pixels,

        "spill_area_percent":
            float(
                area_percent
            ),

        "mean_confidence_percent":
            float(
                mean_probability
            ),

        "max_confidence_percent":
            float(
                probability.max()
                *
                100.0
            )
    }


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    run_dir,
    original_bgr,
    probability,
    mask
):

    # --------------------------------------------------------
    # Mask
    # --------------------------------------------------------

    mask_path = os.path.join(
        run_dir,
        "mask.png"
    )

    mask_image = (
        mask
        *
        255
    ).astype(
        np.uint8
    )

    cv2.imwrite(
        mask_path,
        mask_image
    )

    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    probability_path = os.path.join(
        run_dir,
        "probability.png"
    )

    probability_image = (
        probability
        *
        255
    ).clip(
        0,
        255
    ).astype(
        np.uint8
    )

    cv2.imwrite(
        probability_path,
        probability_image
    )

    # --------------------------------------------------------
    # Overlay
    # --------------------------------------------------------

    overlay_path = os.path.join(
        run_dir,
        "overlay.png"
    )

    resized = cv2.resize(
        original_bgr,
        (
            256,
            256
        ),
        interpolation=cv2.INTER_AREA
    )

    overlay = resized.copy()

    red = np.zeros_like(
        overlay
    )

    red[
        :,
        :,
        2
    ] = 255

    detected = (
        mask > 0
    )

    if np.any(
        detected
    ):

        overlay[
            detected
        ] = cv2.addWeighted(
            overlay[
                detected
            ],
            0.55,
            red[
                detected
            ],
            0.45,
            0
        )

    cv2.imwrite(
        overlay_path,
        overlay
    )

    return {
        "mask":
            mask_path,

        "probability":
            probability_path,

        "overlay":
            overlay_path
    }


# ============================================================
# FALSE POSITIVE
# ============================================================

def run_false_positive(
    input_path,
    mask,
    probability
):

    result = (
        MODULES[
            "false_positive"
        ]
        .analyze_false_positive(

            input_path,

            mask,

            probability
        )
    )

    score = float(
        result.get(
            "candidate_score",
            0
        )
    )

    if 0 <= score <= 1:

        score *= 100

    result[
        "candidate_score_percent"
    ] = score

    return result


# ============================================================
# SPECTRAL
# ============================================================

def run_spectral(
    input_path,
    mask
):

    return (
        MODULES[
            "spectral"
        ]
        .analyze_spectral_features(

            input_path,

            mask
        )
    )


# ============================================================
# EVIDENCE FUSION
# ============================================================

def run_evidence(
    latitude,
    longitude,
    event_time
):

    evidence = MODULES[
        "evidence"
    ]

    evidence.SPILL_LATITUDE = float(
        latitude
    )

    evidence.SPILL_LONGITUDE = float(
        longitude
    )

    evidence.SPILL_TIME = pd.Timestamp(
        event_time
    )

    if not os.path.exists(
        BEHAVIOUR_FILE
    ):

        raise RuntimeError(
            "Behaviour data file not found."
        )

    behaviour_df = pd.read_csv(
        BEHAVIOUR_FILE
    )

    if os.path.exists(
        FINAL_BEHAVIOUR_FILE
    ):

        final_df = pd.read_csv(
            FINAL_BEHAVIOUR_FILE
        )

    else:

        final_df = None

    behaviour_df = (
        evidence
        .prepare_behaviour_data(

            behaviour_df,

            final_df
        )
    )

    event_df = (
        evidence
        .find_event_candidates(

            behaviour_df
        )
    )

    if event_df.empty:

        return (
            pd.DataFrame(),
            0
        )

    vessel_df = (
        evidence
        .create_vessel_candidates(

            event_df
        )
    )

    results = []

    for _, candidate in vessel_df.iterrows():

        event_behaviour = (
            evidence
            .calculate_event_behaviour(

                candidate[
                    "mmsi"
                ],

                behaviour_df
            )
        )

        result = (
            evidence
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
            len(
                event_df
            )
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
        len(
            event_df
        )
    )


# ============================================================
# SWAGGER UPLOAD TEST
# ============================================================

@app.post(
    "/test-upload"
)
async def test_upload(

    image: UploadFile = File(
        ...
    )
):

    (
        bgr_image,
        filename,
        content_type,
        size_bytes,
        detected_format
    ) = await read_upload(
        image
    )

    return {

        "status":
            "success",

        "message":
            "Swagger upload and image decoding are working.",

        "filename":
            filename,

        "content_type":
            content_type,

        "size_bytes":
            size_bytes,

        "detected_format":
            detected_format,

        "decoded_shape":
            list(
                bgr_image.shape
            ),

        "decoded_channels":
            int(
                bgr_image.shape[2]
            ),

        "next_step":
            "Use POST /analyze with the same image."
    }


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health"
)
async def health():

    return {

        "status":
            "ok",

        "service":
            "SIH 26143 ML API",

        "version":
            API_VERSION,

        "device":
            str(
                DEVICE
            ),

        "cuda_available":
            bool(
                torch.cuda.is_available()
            ),

        "gpu":
            (
                torch.cuda.get_device_name(0)
                if torch.cuda.is_available()
                else None
            ),

        "model_loaded":
            MODEL is not None
    }


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/"
)
async def root():

    return {

        "service":
            "SIH 26143 ML API",

        "version":
            API_VERSION,

        "status":
            "running",

        "docs":
            "/docs",

        "health":
            "/health",

        "analyze":
            "/analyze",

        "test_upload":
            "/test-upload"
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post(
    "/analyze"
)
async def analyze(

    image: UploadFile = File(
        ...
    ),

    latitude: float = Form(
        DEFAULT_LATITUDE
    ),

    longitude: float = Form(
        DEFAULT_LONGITUDE
    ),

    event_time: str = Form(
        DEFAULT_EVENT_TIME
    )
):

    run_id = uuid.uuid4().hex[
        :12
    ]

    run_dir = os.path.join(
        OUTPUT_ROOT,
        run_id
    )

    os.makedirs(
        run_dir,
        exist_ok=True
    )

    try:

        # ====================================================
        # LOCATION
        # ====================================================

        try:

            latitude = float(
                latitude
            )

            longitude = float(
                longitude
            )

        except Exception:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Latitude and longitude must "
                    "be valid numbers."
                )
            )

        if not (
            -90
            <=
            latitude
            <=
            90
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Latitude must be between "
                    "-90 and 90."
                )
            )

        if not (
            -180
            <=
            longitude
            <=
            180
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Longitude must be between "
                    "-180 and 180."
                )
            )

        # ====================================================
        # TIME
        # ====================================================

        try:

            parsed_time = pd.Timestamp(
                event_time
            )

        except Exception:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid event_time. "
                    "Use YYYY-MM-DD HH:MM:SS."
                )
            )

        # ====================================================
        # READ IMAGE
        # ====================================================

        (
            original_bgr,
            original_filename,
            content_type,
            file_size,
            detected_format
        ) = await read_upload(
            image
        )

        # ====================================================
        # INPUT DOMAIN VALIDATION
        # ====================================================

        validation_result = validate_input_domain(
            original_bgr
        )

        print_input_validation_result(
            validation_result
        )

        if not validation_result["accepted"]:
            rejection_response = {
                "status": "rejected",
                "run_id": run_id,
                "api_version": API_VERSION,
                "error": "UNSUPPORTED_INPUT_DOMAIN",
                "message": (
                    "The uploaded image is outside the "
                    "current U-Net training domain."
                ),
                "ml_analysis_started": False,
                "source_file": {
                    "filename": original_filename,
                    "content_type": content_type,
                    "size_bytes": file_size,
                    "detected_format": detected_format
                },
                "input_validation": validation_result,
                "recommendation": (
                    "Use grayscale-like Sentinel-1 SAR "
                    "imagery compatible with the trained "
                    "model, or provide a model trained "
                    "specifically for optical/multispectral imagery."
                )
            }

            rejection_path = os.path.join(
                run_dir,
                "summary.json"
            )

            with open(
                rejection_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    make_json_safe(
                        rejection_response
                    ),
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                "\n=========================================="
            )

            print(
                "       INPUT REJECTED SAFELY"
            )

            print(
                "=========================================="
            )

            print(
                "\nU-Net inference was NOT started."
            )

            return make_json_safe(
                rejection_response
            )

        # ====================================================
        # SAVE INPUT
        # ====================================================

        input_path = os.path.join(
            run_dir,
            "input.png"
        )

        cv2.imwrite(
            input_path,
            original_bgr
        )

        # ====================================================
        # PREPARE
        # ====================================================

        rgb_image = (
            prepare_model_image(
                original_bgr
            )
        )

        # ====================================================
        # STEP 1
        # ====================================================

        print(
            "\nSTEP 1: U-NET SPILL DETECTION"
        )

        probability, mask = run_unet(
            rgb_image
        )

        spill_result = (
            calculate_spill_statistics(

                probability,

                mask
            )
        )

        print(
            f"Spill detected: "
            f"{spill_result['detected']}"
        )

        print(
            f"Spill area: "
            f"{spill_result['spill_area_percent']:.2f}%"
        )

        print(
            f"Mean confidence: "
            f"{spill_result['mean_confidence_percent']:.2f}%"
        )

        # ====================================================
        # OUTPUT IMAGES
        # ====================================================

        output_files = save_outputs(

            run_dir,

            original_bgr,

            probability,

            mask
        )

        # ====================================================
        # STEP 2
        # ====================================================

        print(
            "\nSTEP 2: FALSE-POSITIVE FILTER"
        )

        fp_result = run_false_positive(

            input_path,

            mask,

            probability
        )

        print(
            f"Candidate score: "
            f"{fp_result['candidate_score_percent']:.2f}%"
        )

        print(
            f"Classification: "
            f"{fp_result.get('classification', 'N/A')}"
        )

        # ====================================================
        # STEP 3
        # ====================================================

        print(
            "\nSTEP 3: SPECTRAL ANALYSIS"
        )

        spectral_result = run_spectral(

            input_path,

            mask
        )

        print(
            f"RGB proxy score: "
            f"{float(spectral_result.get('rgb_spectral_proxy_score', 0)) * 100:.2f}"
        )

        print(
            f"Oil category: "
            f"{spectral_result.get('probable_oil_category', 'N/A')}"
        )

        # ====================================================
        # STEP 4
        # ====================================================

        print(
            "\nSTEP 4: AIS + BEHAVIOUR + EVIDENCE FUSION"
        )

        (
            fusion_df,
            event_records
        ) = run_evidence(

            latitude,

            longitude,

            parsed_time
        )

        print(
            f"AIS observations: "
            f"{event_records}"
        )

        print(
            f"Unique vessels: "
            f"{len(fusion_df)}"
        )

        # ====================================================
        # VESSELS
        # ====================================================

        if fusion_df.empty:

            targets = []

        else:

            targets = (
                fusion_df
                .head(20)
                .to_dict(
                    orient="records"
                )
            )

        # ====================================================
        # SAVE CSV
        # ====================================================

        evidence_csv = os.path.join(
            run_dir,
            "evidence_fusion_results.csv"
        )

        if not fusion_df.empty:

            fusion_df.to_csv(
                evidence_csv,
                index=False
            )

        # ====================================================
        # RESPONSE
        # ====================================================

        response = {

            "status":
                "success",

            "run_id":
                run_id,

            "api_version":
                API_VERSION,

            "source_file":
            {
                "filename":
                    original_filename,

                "content_type":
                    content_type,

                "size_bytes":
                    file_size,

                "detected_format":
                    detected_format
            },

            "incident":
            {
                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "time":
                    parsed_time.isoformat()
            },

            "spill_detection":
                spill_result,

            "false_positive":
            {
                "candidate_score_percent":
                    fp_result[
                        "candidate_score_percent"
                    ],

                "classification":
                    fp_result.get(
                        "classification",
                        "N/A"
                    ),

                "spill_area_percent":
                    float(
                        fp_result.get(
                            "spill_area_percent",
                            0
                        )
                    ),

                "connected_components":
                    int(
                        fp_result.get(
                            "connected_components",
                            0
                        )
                    )
            },

            "spectral_analysis":
            {
                "rgb_proxy_score":
                    float(
                        spectral_result.get(
                            "rgb_spectral_proxy_score",
                            0
                        )
                        *
                        100
                    ),

                "probable_oil_category":
                    spectral_result.get(
                        "probable_oil_category",
                        "N/A"
                    ),

                "category_confidence_percent":
                    float(
                        spectral_result.get(
                            "category_confidence",
                            0
                        )
                        *
                        100
                    )
            },

            "ais":
            {
                "event_observations":
                    int(
                        event_records
                    ),

                "unique_vessels":
                    int(
                        len(
                            fusion_df
                        )
                    )
            },

            "investigation_targets":
                targets,

            "files":
            {
                "mask":
                    f"/outputs/{run_id}/mask.png",

                "probability":
                    f"/outputs/{run_id}/probability.png",

                "overlay":
                    f"/outputs/{run_id}/overlay.png",

                "evidence_csv":
                    f"/outputs/{run_id}/evidence_fusion_results.csv"
            },

            "disclaimer":
                (
                    "Investigation priority is a "
                    "decision-support ranking and does "
                    "not establish that a vessel caused "
                    "the spill."
                )
        }

        # ====================================================
        # SAVE JSON
        # ====================================================

        summary_path = os.path.join(
            run_dir,
            "summary.json"
        )

        with open(
            summary_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                make_json_safe(
                    response
                ),
                file,
                indent=2,
                ensure_ascii=False
            )

        # ====================================================
        # SUCCESS
        # ====================================================

        print(
            "\n=========================================="
        )

        print(
            "ANALYSIS COMPLETED SUCCESSFULLY"
        )

        print(
            f"Run ID: {run_id}"
        )

        print(
            "=========================================="
        )

        return make_json_safe(
            response
        )

    except HTTPException:

        shutil.rmtree(
            run_dir,
            ignore_errors=True
        )

        raise

    except Exception as error:

        print(
            "\n=========================================="
        )

        print(
            "UNEXPECTED API ERROR"
        )

        print(
            repr(
                error
            )
        )

        print(
            "=========================================="
        )

        shutil.rmtree(
            run_dir,
            ignore_errors=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "ML analysis failed: "
                f"{error}"
            )
        )

    finally:

        try:

            await image.close()

        except Exception:

            pass


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\nStart with:"
    )

    print(
        "uvicorn ml.src.api:app --host 0.0.0.0 --port 8000"
    )