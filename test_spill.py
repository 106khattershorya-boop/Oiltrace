import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import cv2

from src.spill_detection import detect_spill


image = cv2.imread(
    "data/test/sample.jpg"
)

if image is None:
    raise FileNotFoundError(
        "sample.jpg not found"
    )


result = detect_spill(image)


print("\n===== SPILL DETECTION =====")

print(
    "Spill detected:",
    result["spill_detected"]
)

print(
    "Candidate area:",
    result["candidate_area_percentage"],
    "%"
)