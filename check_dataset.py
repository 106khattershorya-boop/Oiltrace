import os

# ============================================================
# DATASET PATHS
# ============================================================

IMAGE_DIR = "ml/data/raw/images/train"
MASK_DIR = "ml/data/raw/masks/train"


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_png_files(folder):
    """
    Return all PNG filenames from a folder.
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"\nFolder not found:\n{folder}\n\n"
            "Check that you extracted the dataset into the correct location."
        )

    files = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".png"):
            files.append(filename)

    return sorted(files)


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("OIL SPILL DATASET CHECK")
print("=" * 70)

print("\nImage folder:")
print(IMAGE_DIR)

print("\nMask folder:")
print(MASK_DIR)


# ------------------------------------------------------------
# Load filenames
# ------------------------------------------------------------

print("\nReading image filenames...")

image_files = get_png_files(IMAGE_DIR)

print("Images found:", len(image_files))


print("\nReading mask filenames...")

mask_files = get_png_files(MASK_DIR)

print("Masks found:", len(mask_files))


# ------------------------------------------------------------
# Convert to sets
# ------------------------------------------------------------

image_set = set(image_files)
mask_set = set(mask_files)


# ------------------------------------------------------------
# Find missing masks
# ------------------------------------------------------------

missing_masks = sorted(
    image_set - mask_set
)


# ------------------------------------------------------------
# Find masks without images
# ------------------------------------------------------------

missing_images = sorted(
    mask_set - image_set
)


# ------------------------------------------------------------
# Find duplicate filenames
# ------------------------------------------------------------

image_duplicates = (
    len(image_files) - len(image_set)
)

mask_duplicates = (
    len(mask_files) - len(mask_set)
)


# ------------------------------------------------------------
# Valid pairs
# ------------------------------------------------------------

valid_pairs = sorted(
    image_set & mask_set
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("DATASET RESULTS")
print("=" * 70)

print("\nTotal images:", len(image_files))
print("Total masks :", len(mask_files))

print("\nValid image-mask pairs:", len(valid_pairs))

print("\nImages without masks:", len(missing_masks))
print("Masks without images:", len(missing_images))

print("\nDuplicate image filenames:", image_duplicates)
print("Duplicate mask filenames :", mask_duplicates)


# ============================================================
# SHOW MISSING MASKS
# ============================================================

if missing_masks:

    print("\n" + "-" * 70)
    print("IMAGES WITHOUT MATCHING MASKS")
    print("-" * 70)

    for filename in missing_masks:
        print(filename)

else:

    print("\nAll images have matching masks.")


# ============================================================
# SHOW MISSING IMAGES
# ============================================================

if missing_images:

    print("\n" + "-" * 70)
    print("MASKS WITHOUT MATCHING IMAGES")
    print("-" * 70)

    for filename in missing_images:
        print(filename)

else:

    print("\nAll masks have matching images.")


# ============================================================
# SHOW SAMPLE PAIRS
# ============================================================

print("\n" + "-" * 70)
print("SAMPLE VALID IMAGE-MASK PAIRS")
print("-" * 70)

for filename in valid_pairs[:10]:

    print(
        f"Image: {filename}  <-->  Mask: {filename}"
    )


# ============================================================
# SAVE MISSING FILE LIST
# ============================================================

REPORT_FILE = "ml/data/dataset_check_report.txt"

os.makedirs(
    os.path.dirname(REPORT_FILE),
    exist_ok=True
)

with open(REPORT_FILE, "w", encoding="utf-8") as file:

    file.write("OIL SPILL DATASET CHECK REPORT\n")
    file.write("=" * 70 + "\n\n")

    file.write(
        f"Total images: {len(image_files)}\n"
    )

    file.write(
        f"Total masks: {len(mask_files)}\n"
    )

    file.write(
        f"Valid pairs: {len(valid_pairs)}\n"
    )

    file.write(
        f"Images without masks: {len(missing_masks)}\n"
    )

    file.write(
        f"Masks without images: {len(missing_images)}\n"
    )

    file.write(
        f"Duplicate image filenames: {image_duplicates}\n"
    )

    file.write(
        f"Duplicate mask filenames: {mask_duplicates}\n\n"
    )

    file.write("=" * 70 + "\n")
    file.write("IMAGES WITHOUT MASKS\n")
    file.write("=" * 70 + "\n")

    for filename in missing_masks:
        file.write(filename + "\n")

    file.write("\n" + "=" * 70 + "\n")
    file.write("MASKS WITHOUT IMAGES\n")
    file.write("=" * 70 + "\n")

    for filename in missing_images:
        file.write(filename + "\n")


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)

print("\nReport saved to:")
print(REPORT_FILE)

if len(valid_pairs) > 0:

    print(
        "\nYou have",
        len(valid_pairs),
        "valid image-mask pairs ready for preprocessing."
    )

else:

    print(
        "\nWARNING: No valid image-mask pairs were found."
    )

print("\nNext step: inspect the results before training U-Net.")