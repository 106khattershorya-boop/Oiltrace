import os
import math
import torch

from torch.utils.data import DataLoader

from dataset import OilSpillDataset
from unet import UNet
from loss import combined_loss


# ============================================================
# PATHS
# ============================================================

TRAIN_IMAGE_DIR = "ml/data/processed/images/train"
TRAIN_MASK_DIR = "ml/data/processed/masks/train"

VAL_IMAGE_DIR = "ml/data/processed/images/val"
VAL_MASK_DIR = "ml/data/processed/masks/val"

MODEL_DIR = "ml/models/spill_detector"

# IMPORTANT:
# This is a NEW filename.
# It will NOT overwrite our previous best model.
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "best_unet_oil_spill_stable.pth"
)


# ============================================================
# TRAINING SETTINGS
# ============================================================

BATCH_SIZE = 4

EPOCHS = 20

# Previous:
# 0.001
#
# New safer learning rate:
LEARNING_RATE = 0.0001

# Prevent extremely large gradients
MAX_GRAD_NORM = 1.0

# Stop if validation does not improve
PATIENCE = 5

NUM_WORKERS = 0


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# DICE SCORE
# ============================================================

def dice_score(predictions, targets, threshold=0.5):

    probabilities = torch.sigmoid(
        predictions
    )

    predictions = (
        probabilities > threshold
    ).float()

    predictions = predictions.view(-1)
    targets = targets.view(-1)

    intersection = (
        predictions * targets
    ).sum()

    dice = (
        2 * intersection + 1.0
    ) / (
        predictions.sum()
        + targets.sum()
        + 1.0
    )

    return dice.item()


# ============================================================
# CHECK FOR NaN / INF
# ============================================================

def tensor_is_invalid(tensor):

    return not torch.isfinite(
        tensor
    ).all()


# ============================================================
# TRAINING
# ============================================================

def train():

    print("\n")
    print("=" * 70)
    print("STABLE OIL SPILL U-NET TRAINING")
    print("=" * 70)

    print("\nDevice:", DEVICE)

    if DEVICE.type == "cuda":

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

        print(
            "VRAM:",
            round(
                torch.cuda.get_device_properties(
                    0
                ).total_memory / (1024 ** 3),
                2
            ),
            "GB"
        )

    print("\nTraining configuration:")

    print(
        "Batch size:",
        BATCH_SIZE
    )

    print(
        "Learning rate:",
        LEARNING_RATE
    )

    print(
        "Epochs:",
        EPOCHS
    )

    print(
        "Gradient clipping:",
        MAX_GRAD_NORM
    )

    print(
        "Early stopping patience:",
        PATIENCE
    )

    print(
        "Mixed precision: DISABLED"
    )

    print(
        "\nNew model will be saved as:"
    )

    print(
        MODEL_PATH
    )


    # ========================================================
    # DATASET
    # ========================================================

    print("\n")
    print("=" * 70)
    print("LOADING DATASETS")
    print("=" * 70)

    print("\nLoading training dataset...")

    train_dataset = OilSpillDataset(
        TRAIN_IMAGE_DIR,
        TRAIN_MASK_DIR
    )

    print("\nLoading validation dataset...")

    val_dataset = OilSpillDataset(
        VAL_IMAGE_DIR,
        VAL_MASK_DIR
    )

    print(
        "\nTraining samples:",
        len(train_dataset)
    )

    print(
        "Validation samples:",
        len(val_dataset)
    )


    # ========================================================
    # DATALOADERS
    # ========================================================

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE.type == "cuda")
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=(DEVICE.type == "cuda")
    )


    # ========================================================
    # MODEL
    # ========================================================

    print("\n")
    print("=" * 70)
    print("CREATING U-NET")
    print("=" * 70)

    model = UNet().to(DEVICE)

    print(
        "\nModel created successfully."
    )


    # ========================================================
    # OPTIMIZER
    # ========================================================

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )


    # ========================================================
    # CREATE MODEL DIRECTORY
    # ========================================================

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )


    # ========================================================
    # TRACK BEST MODEL
    # ========================================================

    best_val_dice = 0.0

    epochs_without_improvement = 0


    # ========================================================
    # TRAINING LOOP
    # ========================================================

    for epoch in range(EPOCHS):

        print("\n")
        print("=" * 70)

        print(
            f"EPOCH {epoch + 1}/{EPOCHS}"
        )

        print("=" * 70)


        # ====================================================
        # TRAIN
        # ====================================================

        model.train()

        total_train_loss = 0.0

        valid_training_batches = 0

        training_failed = False


        for batch_index, (images, masks) in enumerate(
            train_loader
        ):

            images = images.to(
                DEVICE,
                non_blocking=True
            )

            masks = masks.to(
                DEVICE,
                non_blocking=True
            )


            # ------------------------------------------------
            # Check input
            # ------------------------------------------------

            if tensor_is_invalid(images):

                print(
                    "\nERROR: Invalid values detected in images."
                )

                training_failed = True

                break


            if tensor_is_invalid(masks):

                print(
                    "\nERROR: Invalid values detected in masks."
                )

                training_failed = True

                break


            # ------------------------------------------------
            # Reset gradients
            # ------------------------------------------------

            optimizer.zero_grad(
                set_to_none=True
            )


            # ------------------------------------------------
            # Forward pass
            # ------------------------------------------------

            predictions = model(
                images
            )


            # ------------------------------------------------
            # Check predictions
            # ------------------------------------------------

            if tensor_is_invalid(
                predictions
            ):

                print(
                    "\nERROR: Model produced NaN/Inf values."
                )

                print(
                    "Stopping training safely."
                )

                training_failed = True

                break


            # ------------------------------------------------
            # Calculate loss
            # ------------------------------------------------

            loss = combined_loss(
                predictions,
                masks
            )


            # ------------------------------------------------
            # Check loss
            # ------------------------------------------------

            if not torch.isfinite(loss):

                print(
                    "\nERROR: Loss became NaN/Inf."
                )

                print(
                    "Stopping training safely."
                )

                training_failed = True

                break


            # ------------------------------------------------
            # Backpropagation
            # ------------------------------------------------

            loss.backward()


            # ------------------------------------------------
            # Gradient clipping
            # ------------------------------------------------

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                MAX_GRAD_NORM
            )


            # ------------------------------------------------
            # Optimizer step
            # ------------------------------------------------

            optimizer.step()


            # ------------------------------------------------
            # Record loss
            # ------------------------------------------------

            total_train_loss += (
                loss.item()
            )

            valid_training_batches += 1


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if (
                batch_index + 1
            ) % 100 == 0:

                print(
                    f"Training batch "
                    f"{batch_index + 1}/"
                    f"{len(train_loader)} "
                    f"- Loss: "
                    f"{loss.item():.4f}"
                )


        # ====================================================
        # HANDLE TRAINING FAILURE
        # ====================================================

        if training_failed:

            print("\n")
            print("=" * 70)

            print(
                "TRAINING STOPPED SAFELY"
            )

            print("=" * 70)

            print(
                "\nThe current best model is still safe:"
            )

            print(
                "ml/models/spill_detector/"
                "best_unet_oil_spill.pth"
            )

            print(
                "\nNo existing model was overwritten."
            )

            break


        # ====================================================
        # TRAINING LOSS
        # ====================================================

        if valid_training_batches == 0:

            print(
                "\nNo valid training batches."
            )

            break


        average_train_loss = (
            total_train_loss
            / valid_training_batches
        )


        # ====================================================
        # VALIDATION
        # ====================================================

        model.eval()

        total_val_loss = 0.0

        total_val_dice = 0.0

        valid_validation_batches = 0


        with torch.no_grad():

            for images, masks in val_loader:

                images = images.to(
                    DEVICE,
                    non_blocking=True
                )

                masks = masks.to(
                    DEVICE,
                    non_blocking=True
                )


                # --------------------------------------------
                # Prediction
                # --------------------------------------------

                predictions = model(
                    images
                )


                # --------------------------------------------
                # Check prediction
                # --------------------------------------------

                if tensor_is_invalid(
                    predictions
                ):

                    print(
                        "\nERROR: Validation produced NaN/Inf."
                    )

                    break


                # --------------------------------------------
                # Loss
                # --------------------------------------------

                loss = combined_loss(
                    predictions,
                    masks
                )


                if not torch.isfinite(loss):

                    print(
                        "\nERROR: Validation loss is NaN/Inf."
                    )

                    break


                # --------------------------------------------
                # Dice
                # --------------------------------------------

                dice = dice_score(
                    predictions,
                    masks
                )


                # --------------------------------------------
                # Accumulate
                # --------------------------------------------

                total_val_loss += (
                    loss.item()
                )

                total_val_dice += dice

                valid_validation_batches += 1


        # ====================================================
        # VALIDATION FAILURE CHECK
        # ====================================================

        if valid_validation_batches == 0:

            print(
                "\nValidation failed."
            )

            break


        # ====================================================
        # AVERAGES
        # ====================================================

        average_val_loss = (
            total_val_loss
            / valid_validation_batches
        )

        average_val_dice = (
            total_val_dice
            / valid_validation_batches
        )


        # ====================================================
        # EPOCH RESULTS
        # ====================================================

        print("\nEpoch results:")

        print(
            "Training Loss:",
            round(
                average_train_loss,
                4
            )
        )

        print(
            "Validation Loss:",
            round(
                average_val_loss,
                4
            )
        )

        print(
            "Validation Dice:",
            round(
                average_val_dice,
                4
            )
        )


        # ====================================================
        # BEST MODEL
        # ====================================================

        if (
            average_val_dice
            > best_val_dice
        ):

            best_val_dice = (
                average_val_dice
            )

            epochs_without_improvement = 0


            torch.save(
                model.state_dict(),
                MODEL_PATH
            )


            print("\n")
            print(
                "✓ NEW BEST STABLE MODEL SAVED"
            )

            print(
                "Best Validation Dice:",
                round(
                    best_val_dice,
                    4
                )
            )

            print(
                "Saved to:",
                MODEL_PATH
            )


        else:

            epochs_without_improvement += 1

            print(
                "\nNo improvement."
            )

            print(
                "Epochs without improvement:",
                epochs_without_improvement,
                "/",
                PATIENCE
            )


        # ====================================================
        # GPU MEMORY
        # ====================================================

        if DEVICE.type == "cuda":

            allocated = (
                torch.cuda.memory_allocated()
                / (1024 ** 3)
            )

            reserved = (
                torch.cuda.memory_reserved()
                / (1024 ** 3)
            )

            print(
                f"GPU Memory: "
                f"{allocated:.2f} GB allocated / "
                f"{reserved:.2f} GB reserved"
            )


        # ====================================================
        # EARLY STOPPING
        # ====================================================

        if (
            epochs_without_improvement
            >= PATIENCE
        ):

            print("\n")
            print(
                "=" * 70
            )

            print(
                "EARLY STOPPING"
            )

            print(
                "=" * 70
            )

            print(
                "\nValidation score stopped improving."
            )

            break


    # ========================================================
    # TRAINING COMPLETE
    # ========================================================

    print("\n")
    print("=" * 70)
    print("STABLE TRAINING COMPLETE")
    print("=" * 70)

    print(
        "\nBest Validation Dice:",
        round(
            best_val_dice,
            4
        )
    )

    print(
        "\nNew model:",
        MODEL_PATH
    )

    print("\nIMPORTANT:")

    print(
        "Your previous best model remains untouched:"
    )

    print(
        "ml/models/spill_detector/"
        "best_unet_oil_spill.pth"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    train()