import torch
import torch.nn.functional as F


def dice_loss(predictions, targets, smooth=1.0):
    predictions = torch.sigmoid(predictions)

    predictions = predictions.view(-1)
    targets = targets.view(-1)

    intersection = (predictions * targets).sum()

    dice = (
        2.0 * intersection + smooth
    ) / (
        predictions.sum()
        + targets.sum()
        + smooth
    )

    return 1 - dice


def combined_loss(predictions, targets):

    bce = F.binary_cross_entropy_with_logits(
        predictions,
        targets
    )

    dice = dice_loss(
        predictions,
        targets
    )

    return bce + dice