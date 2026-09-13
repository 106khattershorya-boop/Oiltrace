import os
import shutil
import random


# ============================================================
# PATHS
# ============================================================

SOURCE_IMAGE_DIR = "ml/data/raw/images/train"
SOURCE_MASK_DIR = "ml/data/raw/masks/train"

OUTPUT_DIR = "ml/data/processed"


# ============================================================
# DATASET SPLIT
# ============================================================

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

RANDOM_SEED = 42


# ============================================================
# CHECK RATIOS
# ============================================================

if TRAIN_RATIO + VAL_RATIO + TEST_RATIO != 1.0:
    raise ValueError(
        "Train, validation and test ratios must add up to 1.0"
    )


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

for split in ["train", "val", "test"]:

    os.makedirs(
        os.path.join(
            OUTPUT_DIR,
            "images",
            split
        ),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            OUTPUT_DIR,
            "masks",
            split
        ),
        exist_ok=True
    )


# ============================================================
# CHECK SOURCE DIRECTORIES
# ============================================================

if not os.path.exists(SOURCE_IMAGE_DIR):

    raise FileNotFoundError(
        f"\nImage directory not found:\n{SOURCE_IMAGE_DIR}"
    )


if not os.path.exists(SOURCE_MASK_DIR):

    raise FileNotFoundError(
        f"\nMask directory not found:\n{SOURCE_MASK_DIR}"
    )


# ============================================================
# GET FILES
# ============================================================

image_files = {
    filename
    for filename in os.listdir(SOURCE_IMAGE_DIR)
    if filename.lower().endswith(".png")
}

mask_files = {
    filename
    for filename in os.listdir(SOURCE_MASK_DIR)
    if filename.lower().endswith(".png")
}


# ============================================================
# VALID PAIRS ONLY
# ============================================================

valid_files = sorted(
    image_files & mask_files
)


print("=" * 70)
print("PREPARING OIL SPILL DATASET")
print("=" * 70)

print("\nImages found:", len(image_files))
print("Masks found :", len(mask_files))
print("Valid pairs :", len(valid_files))


if len(valid_files) == 0:

    raise ValueError(
        "No valid image-mask pairs were found."
    )


# ============================================================
# SHUFFLE
# ============================================================

random.seed(RANDOM_SEED)

random.shuffle(valid_files)


# ============================================================
# CALCULATE SPLIT SIZES
# ============================================================

total = len(valid_files)

train_count = int(
    total * TRAIN_RATIO
)

val_count = int(
    total * VAL_RATIO
)

test_count = total - train_count - val_count


print("\nDataset split:")
print(
    f"Train      : {train_count}"
)

print(
    f"Validation : {val_count}"
)

print(
    f"Test       : {test_count}"
)

print(
    f"Total      : {train_count + val_count + test_count}"
)


# ============================================================
# SPLIT FILES
# ============================================================

train_files = valid_files[
    :train_count
]

val_files = valid_files[
    train_count:
    train_count + val_count
]

test_files = valid_files[
    train_count + val_count:
]


# ============================================================
# COPY FUNCTION
# ============================================================

def copy_pairs(files, split):

    image_destination = os.path.join(
        OUTPUT_DIR,
        "images",
        split
    )

    mask_destination = os.path.join(
        OUTPUT_DIR,
        "masks",
        split
    )

    print(
        f"\nCopying {split} dataset..."
    )

    for index, filename in enumerate(files, start=1):

        source_image = os.path.join(
            SOURCE_IMAGE_DIR,
            filename
        )

        source_mask = os.path.join(
            SOURCE_MASK_DIR,
            filename
        )

        destination_image = os.path.join(
            image_destination,
            filename
        )

        destination_mask = os.path.join(
            mask_destination,
            filename
        )

        shutil.copy2(
            source_image,
            destination_image
        )

        shutil.copy2(
            source_mask,
            destination_mask
        )

        if index % 500 == 0:

            print(
                f"  Copied {index}/{len(files)}"
            )

    print(
        f"  Completed {len(files)} pairs."
    )


# ============================================================
# COPY DATASETS
# ============================================================

copy_pairs(
    train_files,
    "train"
)

copy_pairs(
    val_files,
    "val"
)

copy_pairs(
    test_files,
    "test"
)


# ============================================================
# VERIFY DATASET
# ============================================================

print("\n" + "=" * 70)
print("VERIFYING DATASET")
print("=" * 70)


def verify_split(split):

    image_dir = os.path.join(
        OUTPUT_DIR,
        "images",
        split
    )

    mask_dir = os.path.join(
        OUTPUT_DIR,
        "masks",
        split
    )

    images = {
        filename
        for filename in os.listdir(image_dir)
        if filename.lower().endswith(".png")
    }

    masks = {
        filename
        for filename in os.listdir(mask_dir)
        if filename.lower().endswith(".png")
    }

    valid = images & masks

    missing_masks = images - masks
    missing_images = masks - images

    print(f"\n{split.upper()}")

    print("Images:", len(images))
    print("Masks :", len(masks))
    print("Pairs :", len(valid))

    print(
        "Images without masks:",
        len(missing_masks)
    )

    print(
        "Masks without images:",
        len(missing_images)
    )

    return (
        len(images),
        len(masks),
        len(valid),
        len(missing_masks),
        len(missing_images)
    )


train_result = verify_split("train")
val_result = verify_split("val")
test_result = verify_split("test")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("DATASET PREPARATION COMPLETE")
print("=" * 70)

print("\nFinal dataset:")

print(
    f"Train      : {train_result[2]} pairs"
)

print(
    f"Validation : {val_result[2]} pairs"
)

print(
    f"Test       : {test_result[2]} pairs"
)

print(
    f"TOTAL      : "
    f"{train_result[2] + val_result[2] + test_result[2]} pairs"
)

print("\nDataset location:")
print(OUTPUT_DIR)

print("\nExpected structure:")

print(
    """
ml/
└── data/
    ├── raw/
    │   ├── images/
    │   │   └── train/
    │   └── masks/
    │       └── train/
    │
    └── processed/
        ├── images/
        │   ├── train/
        │   ├── val/
        │   └── test/
        │
        └── masks/
            ├── train/
            ├── val/
            └── test/
"""
)

print("\nReady for U-Net dataset loading.")