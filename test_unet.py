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

import torch

from src.unet import UNet


model = UNet()

input_image = torch.randn(
    2,
    3,
    256,
    256
)

output = model(
    input_image
)

print(
    "Input shape:",
    input_image.shape
)

print(
    "Output shape:",
    output.shape
)