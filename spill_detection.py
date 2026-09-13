import cv2
import numpy as np


def detect_dark_regions(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Identify unusually dark pixels
    threshold = np.percentile(
        gray,
        15
    )

    mask = np.zeros_like(gray)

    mask[gray < threshold] = 255

    return mask


def remove_small_regions(mask):

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    return mask


def calculate_area(mask):

    total_pixels = mask.shape[0] * mask.shape[1]

    spill_pixels = np.sum(
        mask > 0
    )

    percentage = (
        spill_pixels /
        total_pixels
    ) * 100

    return percentage


def detect_spill(image):

    mask = detect_dark_regions(image)

    mask = remove_small_regions(mask)

    area = calculate_area(mask)

    if area > 0.5:
        detected = True
    else:
        detected = False

    return {
        "spill_detected": detected,
        "candidate_area_percentage": round(
            area,
            2
        ),
        "mask": mask
    }