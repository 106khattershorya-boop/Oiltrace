import os
import cv2
import torch
import numpy as np
from unet import UNet
from dataset import OilSpillDataset

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "ml/models/spill_detector/best_unet_oil_spill_stable.pth"

TEST_IMAGE_DIR = "ml/data/processed/images/test"
TEST_MASK_DIR = "ml/data/processed/masks/test"

OUTPUT_DIR = "ml/data/test/predictions"

IMAGE_SIZE = 256
THRESHOLD = 0.5

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# DICE SCORE
# ============================================================

def calculate_dice(prediction, target, smooth=1e-6):

    prediction = prediction.astype(bool)
    target = target.astype(bool)

    intersection = np.logical_and(
        prediction,
        target
    ).sum()

    dice = (
        2 * intersection + smooth
    ) / (
        prediction.sum()
        + target.sum()
        + smooth
    )

    return dice


# ============================================================
# IOU
# ============================================================

def calculate_iou(prediction, target, smooth=1e-6):

    prediction = prediction.astype(bool)
    target = target.astype(bool)

    intersection = np.logical_and(
        prediction,
        target
    ).sum()

    union = np.logical_or(
        prediction,
        target
    ).sum()

    iou = (
        intersection + smooth
    ) / (
        union + smooth
    )

    return iou


# ============================================================
# PRECISION
# ============================================================

def calculate_precision(prediction, target, smooth=1e-6):

    prediction = prediction.astype(bool)
    target = target.astype(bool)

    true_positive = np.logical_and(
        prediction,
        target
    ).sum()

    false_positive = np.logical_and(
        prediction,
        np.logical_not(target)
    ).sum()

    precision = (
        true_positive + smooth
    ) / (
        true_positive
        + false_positive
        + smooth
    )

    return precision


# ============================================================
# RECALL
# ============================================================

def calculate_recall(prediction, target, smooth=1e-6):

    prediction = prediction.astype(bool)
    target = target.astype(bool)

    true_positive = np.logical_and(
        prediction,
        target
    ).sum()

    false_negative = np.logical_and(
        np.logical_not(prediction),
        target
    ).sum()

    recall = (
        true_positive + smooth
    ) / (
        true_positive
        + false_negative
        + smooth
    )

    return recall


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print("\nLoading stable U-Net model...")

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"\nModel not found:\n{MODEL_PATH}"
        )

    model = UNet().to(DEVICE)

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )
    )

    model.eval()

    print("Stable model loaded successfully.")

    return model


# ============================================================
# SAVE VISUALIZATION
# ============================================================

def save_visualization(
    image,
    ground_truth,
    prediction,
    output_path
):

    # Convert RGB → BGR for OpenCV
    original = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )

    # Ground truth
    ground_truth_image = (
        ground_truth.astype(np.uint8) * 255
    )

    # Prediction
    prediction_image = (
        prediction.astype(np.uint8) * 255
    )

    # Convert grayscale masks to BGR
    ground_truth_image = cv2.cvtColor(
        ground_truth_image,
        cv2.COLOR_GRAY2BGR
    )

    prediction_image = cv2.cvtColor(
        prediction_image,
        cv2.COLOR_GRAY2BGR
    )

    combined = np.hstack([
        original,
        ground_truth_image,
        prediction_image
    ])

    cv2.imwrite(
        output_path,
        combined
    )


# ============================================================
# MAIN EVALUATION
# ============================================================

def evaluate():

    print("=" * 70)
    print("STABLE OIL SPILL U-NET TEST EVALUATION")
    print("=" * 70)

    print("\nDevice:", DEVICE)

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

    model = load_model()

    print("\nLoading test dataset...")

    test_dataset = OilSpillDataset(
        TEST_IMAGE_DIR,
        TEST_MASK_DIR
    )

    print(
        "Test samples:",
        len(test_dataset)
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    print("\nStarting evaluation...")

    dice_scores = []
    iou_scores = []
    precision_scores = []
    recall_scores = []

    total_tp = 0
    total_fp = 0
    total_fn = 0

    visualization_count = 0

    with torch.no_grad():

        for index in range(
            len(test_dataset)
        ):

            image_tensor, mask_tensor = (
                test_dataset[index]
            )

            image_input = (
                image_tensor
                .unsqueeze(0)
                .to(DEVICE)
            )

            output = model(
                image_input
            )

            probability = torch.sigmoid(
                output
            )

            prediction = (
                probability
                > THRESHOLD
            ).float()

            prediction = (
                prediction
                .squeeze()
                .cpu()
                .numpy()
            )

            target = (
                mask_tensor
                .squeeze()
                .cpu()
                .numpy()
            )

            # Metrics
            dice = calculate_dice(
                prediction,
                target
            )

            iou = calculate_iou(
                prediction,
                target
            )

            precision = calculate_precision(
                prediction,
                target
            )

            recall = calculate_recall(
                prediction,
                target
            )

            dice_scores.append(dice)
            iou_scores.append(iou)
            precision_scores.append(precision)
            recall_scores.append(recall)

            # Confusion counts
            prediction_bool = prediction.astype(bool)
            target_bool = target.astype(bool)

            tp = np.logical_and(
                prediction_bool,
                target_bool
            ).sum()

            fp = np.logical_and(
                prediction_bool,
                np.logical_not(target_bool)
            ).sum()

            fn = np.logical_and(
                np.logical_not(prediction_bool),
                target_bool
            ).sum()

            total_tp += tp
            total_fp += fp
            total_fn += fn

            # Save first 5 visualizations
            if visualization_count < 5:

                image_np = (
                    image_tensor
                    .permute(1, 2, 0)
                    .cpu()
                    .numpy()
                    * 255
                )

                image_np = image_np.astype(
                    np.uint8
                )

                output_path = os.path.join(
                    OUTPUT_DIR,
                    f"stable_prediction_{visualization_count + 1}.png"
                )

                save_visualization(
                    image_np,
                    target,
                    prediction,
                    output_path
                )

                visualization_count += 1

            if (index + 1) % 200 == 0:

                print(
                    f"Processed {index + 1}/"
                    f"{len(test_dataset)} images"
                )

    # ========================================================
    # AVERAGE METRICS
    # ========================================================

    average_dice = np.mean(
        dice_scores
    )

    average_iou = np.mean(
        iou_scores
    )

    average_precision = np.mean(
        precision_scores
    )

    average_recall = np.mean(
        recall_scores
    )

    # Dataset-level metrics
    dataset_dice = (
        2 * total_tp
    ) / (
        2 * total_tp
        + total_fp
        + total_fn
    )

    dataset_iou = (
        total_tp
    ) / (
        total_tp
        + total_fp
        + total_fn
    )

    dataset_precision = (
        total_tp
    ) / (
        total_tp
        + total_fp
    )

    dataset_recall = (
        total_tp
    ) / (
        total_tp
        + total_fn
    )

    # ========================================================
    # RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("STABLE MODEL TEST RESULTS")
    print("=" * 70)

    print(
        "\nNumber of test images:",
        len(test_dataset)
    )

    print("\nAverage per-image metrics:")

    print(
        f"Dice:      {average_dice:.4f}"
    )

    print(
        f"IoU:       {average_iou:.4f}"
    )

    print(
        f"Precision: {average_precision:.4f}"
    )

    print(
        f"Recall:    {average_recall:.4f}"
    )

    print("\nDataset-level pixel metrics:")

    print(
        f"Dice:      {dataset_dice:.4f}"
    )

    print(
        f"IoU:       {dataset_iou:.4f}"
    )

    print(
        f"Precision: {dataset_precision:.4f}"
    )

    print(
        f"Recall:    {dataset_recall:.4f}"
    )

    print("\nConfusion counts:")

    print(
        "True Positive:",
        total_tp
    )

    print(
        "False Positive:",
        total_fp
    )

    print(
        "False Negative:",
        total_fn
    )

    print("\nVisual predictions saved to:")

    print(
        os.path.abspath(
            OUTPUT_DIR
        )
    )

    print("\nSaved visualizations:")

    for i in range(1, 6):

        print(
            f"stable_prediction_{i}.png"
        )

    print("\n")
    print("=" * 70)
    print("STABLE MODEL EVALUATION COMPLETE")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    evaluate()