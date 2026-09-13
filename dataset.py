import os
import cv2
import torch
from torch.utils.data import Dataset


class OilSpillDataset(Dataset):

    def __init__(self, image_dir, mask_dir):

        self.image_dir = image_dir
        self.mask_dir = mask_dir

        # ----------------------------------------------------
        # Find only images that have a matching mask
        # ----------------------------------------------------

        image_files = {
            filename
            for filename in os.listdir(image_dir)
            if filename.lower().endswith(".png")
        }

        mask_files = {
            filename
            for filename in os.listdir(mask_dir)
            if filename.lower().endswith(".png")
        }

        self.images = sorted(
            image_files & mask_files
        )

        if len(self.images) == 0:
            raise ValueError(
                "\nNo matching image-mask pairs found.\n"
                f"Image directory: {image_dir}\n"
                f"Mask directory: {mask_dir}"
            )

        print(
            f"Loaded {len(self.images)} image-mask pairs."
        )


    def __len__(self):

        return len(self.images)


    def __getitem__(self, index):

        filename = self.images[index]

        image_path = os.path.join(
            self.image_dir,
            filename
        )

        mask_path = os.path.join(
            self.mask_dir,
            filename
        )


        # ====================================================
        # LOAD IMAGE
        # ====================================================

        image = cv2.imread(
            image_path,
            cv2.IMREAD_COLOR
        )

        if image is None:
            raise ValueError(
                f"Could not read image:\n{image_path}"
            )


        # ====================================================
        # LOAD MASK
        # ====================================================

        mask = cv2.imread(
            mask_path,
            cv2.IMREAD_GRAYSCALE
        )

        if mask is None:
            raise ValueError(
                f"Could not read mask:\n{mask_path}"
            )


        # ====================================================
        # CHECK IMAGE SIZE
        # ====================================================

        if image.shape[:2] != (256, 256):

            image = cv2.resize(
                image,
                (256, 256),
                interpolation=cv2.INTER_AREA
            )


        # ====================================================
        # CHECK MASK SIZE
        # ====================================================

        if mask.shape[:2] != (256, 256):

            mask = cv2.resize(
                mask,
                (256, 256),
                interpolation=cv2.INTER_NEAREST
            )


        # ====================================================
        # CONVERT BGR → RGB
        # ====================================================

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )


        # ====================================================
        # NORMALIZE IMAGE
        # 0-255 → 0-1
        # ====================================================

        image = image.astype("float32") / 255.0


        # ====================================================
        # CONVERT MASK TO BINARY
        #
        # Original:
        # 0   = background
        # 255 = oil spill
        #
        # New:
        # 0 = background
        # 1 = oil spill
        # ====================================================

        mask = (mask > 127).astype("float32")


        # ====================================================
        # CONVERT NUMPY → PYTORCH TENSORS
        # ====================================================

        image = torch.tensor(
            image,
            dtype=torch.float32
        )

        mask = torch.tensor(
            mask,
            dtype=torch.float32
        )


        # ====================================================
        # CHANGE DIMENSIONS
        #
        # Image:
        # H × W × C
        # ↓
        # C × H × W
        #
        # Mask:
        # H × W
        # ↓
        # 1 × H × W
        # ====================================================

        image = image.permute(
            2,
            0,
            1
        )

        mask = mask.unsqueeze(0)


        return image, mask