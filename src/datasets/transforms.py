# transforms.py — Albumentations augmentation pipelines for training and validation.
#
# Two separate transforms are used:
#   - Training: random flips, rotation, and brightness/contrast to improve generalisation
#   - Validation: resize only — no augmentation, so evaluation is deterministic
#
# Normalisation values (mean/std) are the ImageNet statistics.
# They MUST match because we use a pretrained ResNet-18 backbone.

import albumentations as A
from albumentations.pytorch import ToTensorV2

from src.config.config import IMAGE_SIZE


def get_train_transforms():
    # Augmentations applied randomly each time a training image is loaded.
    # This artificially increases dataset diversity and reduces overfitting.
    return A.Compose([
        A.Resize(IMAGE_SIZE, IMAGE_SIZE),                   # bring all images to 224×224
        A.HorizontalFlip(p=0.5),                            # mirror left-right (50% chance)
        A.VerticalFlip(p=0.2),                              # flip upside-down (20% chance)
        A.Rotate(limit=20, p=0.5),                          # rotate up to ±20° (50% chance)
        A.RandomBrightnessContrast(p=0.5),                  # vary lighting conditions
        A.Normalize(
            mean=(0.485, 0.456, 0.406),                     # ImageNet RGB channel means
            std=(0.229, 0.224, 0.225)                        # ImageNet RGB channel stds
        ),
        ToTensorV2()                                         # numpy HWC → PyTorch CHW tensor
    ])


def get_val_transforms():
    # Validation transform: only resize and normalise.
    # No random augmentations — we need consistent, reproducible results.
    return A.Compose([
        A.Resize(IMAGE_SIZE, IMAGE_SIZE),
        A.Normalize(
            mean=(0.485, 0.456, 0.406),
            std=(0.229, 0.224, 0.225)
        ),
        ToTensorV2()
    ])
