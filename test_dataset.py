import sys
import os

# ------------------------------------------------------------
# Make sure Python can find the src folder
# ------------------------------------------------------------

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from dataset import OilSpillDataset


# ============================================================
# PATHS
# ============================================================

IMAGE_DIR = "ml/data/processed/images/train"
MASK_DIR = "ml/data/processed/masks/train"


# ============================================================
# CREATE DATASET
# ============================================================

print("=" * 70)
print("TESTING OIL SPILL DATASET")
print("=" * 70)

dataset = OilSpillDataset(
    IMAGE_DIR,
    MASK_DIR
)


# ============================================================
# DATASET SIZE
# ============================================================

print("\nDataset size:")
print(len(dataset))


# ============================================================
# LOAD FIRST SAMPLE
# ============================================================

print("\nLoading first sample...")

image, mask = dataset[0]


# ============================================================
# PRINT SHAPES
# ============================================================

print("\nImage information:")
print("Shape:", image.shape)
print("Data type:", image.dtype)
print("Minimum:", image.min().item())
print("Maximum:", image.max().item())


print("\nMask information:")
print("Shape:", mask.shape)
print("Data type:", mask.dtype)
print("Minimum:", mask.min().item())
print("Maximum:", mask.max().item())


# ============================================================
# CHECK EXPECTED SHAPES
# ============================================================

expected_image_shape = (3, 256, 256)
expected_mask_shape = (1, 256, 256)


print("\nChecking shapes...")


if tuple(image.shape) == expected_image_shape:

    print(
        "✓ Image shape is correct:",
        expected_image_shape
    )

else:

    print(
        "✗ Image shape is WRONG."
    )


if tuple(mask.shape) == expected_mask_shape:

    print(
        "✓ Mask shape is correct:",
        expected_mask_shape
    )

else:

    print(
        "✗ Mask shape is WRONG."
    )


# ============================================================
# CHECK MASK VALUES
# ============================================================

unique_mask_values = mask.unique()

print("\nUnique mask values:")
print(unique_mask_values)


if all(
    value.item() in [0.0, 1.0]
    for value in unique_mask_values
):

    print(
        "✓ Mask is correctly binary."
    )

else:

    print(
        "✗ Mask contains unexpected values."
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("DATASET TEST COMPLETE")
print("=" * 70)

print(
    "\nThe dataset loader is ready for U-Net."
)