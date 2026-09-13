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

result = detect_spill(image)

mask = result["mask"]


cv2.imshow(
    "Original Image",
    image
)

cv2.imshow(
    "Potential Spill Regions",
    mask
)

print(
    "Press any key to close..."
)

cv2.waitKey(0)

cv2.destroyAllWindows()