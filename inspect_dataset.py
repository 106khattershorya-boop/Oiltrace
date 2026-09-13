import os
import cv2
import numpy as np


# ============================================================
# DATASET PATHS
# ============================================================

IMAGE_DIR = "ml/data/raw/images/train"
MASK_DIR = "ml/data/raw/masks/train"


# ============================================================
# SETTINGS
# ============================================================

# These are valid pairs found by matching filenames.
# We inspect a few different samples rather than only one.

SAMPLE_FILES = [
    "palsar_0.png",
    "palsar_1.png",
    "palsar_100.png",
    "palsar_1000.png",
]


# ============================================================
# HELPER
# ============================================================

def inspect_file(image_path, mask_path):

    print("\n" + "-" * 70)

    print("Image:")
    print(image_path)

    print("Mask:")
    print(mask_path)

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(
        image_path,
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        print("ERROR: Could not read image.")
        return

    # --------------------------------------------------------
    # Read mask
    # --------------------------------------------------------

    mask = cv2.imread(
        mask_path,
        cv2.IMREAD_UNCHANGED
    )

    if mask is None:
        print("ERROR: Could not read mask.")
        return

    # --------------------------------------------------------
    # Image information
    # --------------------------------------------------------

    print("\nIMAGE INFORMATION")

    print("Shape:", image.shape)
    print("Dimensions:", image.shape[:2])

    if len(image.shape) == 2:
        print("Channels: 1 (grayscale)")
    else:
        print("Channels:", image.shape[2])

    print("Data type:", image.dtype)

    print("Minimum value:", image.min())
    print("Maximum value:", image.max())

    print(
        "Mean:",
        round(float(image.mean()), 4)
    )

    print(
        "Standard deviation:",
        round(float(image.std()), 4)
    )

    # --------------------------------------------------------
    # Mask information
    # --------------------------------------------------------

    print("\nMASK INFORMATION")

    print("Shape:", mask.shape)
    print("Dimensions:", mask.shape[:2])

    if len(mask.shape) == 2:
        print("Channels: 1 (grayscale)")
    else:
        print("Channels:", mask.shape[2])

    print("Data type:", mask.dtype)

    print("Minimum value:", mask.min())
    print("Maximum value:", mask.max())

    # --------------------------------------------------------
    # Unique mask values
    # --------------------------------------------------------

    unique_values = np.unique(mask)

    print("\nUnique mask values:")

    if len(unique_values) <= 20:

        print(unique_values)

    else:

        print(
            "More than 20 unique values found."
        )

        print(
            "First 20:",
            unique_values[:20]
        )

    # --------------------------------------------------------
    # Mask pixel statistics
    # --------------------------------------------------------

    total_pixels = mask.size

    non_zero_pixels = np.count_nonzero(mask)

    zero_pixels = total_pixels - non_zero_pixels

    print("\nMASK PIXEL STATISTICS")

    print("Total pixels:", total_pixels)

    print("Background pixels:", zero_pixels)

    print("Non-zero pixels:", non_zero_pixels)

    if total_pixels > 0:

        percentage = (
            non_zero_pixels
            / total_pixels
            * 100
        )

        print(
            "Non-zero percentage:",
            round(percentage, 2),
            "%"
        )


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("OIL SPILL DATASET INSPECTION")
print("=" * 70)

print("\nImage directory:")
print(IMAGE_DIR)

print("\nMask directory:")
print(MASK_DIR)


# ============================================================
# CHECK DIRECTORIES
# ============================================================

if not os.path.exists(IMAGE_DIR):

    raise FileNotFoundError(
        f"\nImage directory not found:\n{IMAGE_DIR}"
    )


if not os.path.exists(MASK_DIR):

    raise FileNotFoundError(
        f"\nMask directory not found:\n{MASK_DIR}"
    )


# ============================================================
# GET VALID FILES
# ============================================================

image_files = {
    filename
    for filename in os.listdir(IMAGE_DIR)
    if filename.lower().endswith(".png")
}

mask_files = {
    filename
    for filename in os.listdir(MASK_DIR)
    if filename.lower().endswith(".png")
}


valid_files = sorted(
    image_files & mask_files
)


print("\nTotal images:", len(image_files))
print("Total masks:", len(mask_files))
print("Valid pairs:", len(valid_files))


# ============================================================
# SELECT SAMPLES
# ============================================================

print("\n" + "=" * 70)
print("INSPECTING SAMPLE FILES")
print("=" * 70)


samples_to_inspect = []

for filename in SAMPLE_FILES:

    if filename in valid_files:

        samples_to_inspect.append(filename)


# If one of the predefined samples doesn't exist,
# automatically select files from the dataset.

if len(samples_to_inspect) < 4:

    for filename in valid_files:

        if filename not in samples_to_inspect:

            samples_to_inspect.append(filename)

        if len(samples_to_inspect) >= 4:

            break


# ============================================================
# INSPECT
# ============================================================

for filename in samples_to_inspect:

    image_path = os.path.join(
        IMAGE_DIR,
        filename
    )

    mask_path = os.path.join(
        MASK_DIR,
        filename
    )

    inspect_file(
        image_path,
        mask_path
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)

print("\nSamples inspected:", len(samples_to_inspect))

print("\nDataset is ready for the next analysis step.")

print(
    "\nNext step will be to configure the U-Net input "
    "according to the actual image channels and dimensions."
)