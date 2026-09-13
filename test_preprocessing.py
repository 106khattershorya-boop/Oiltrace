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

from src.preprocessing import preprocess


image, processed = preprocess(
    "data/test/sample.jpg"
)

print("Original image shape:")
print(image.shape)

print("\nProcessed image shape:")
print(processed.shape)