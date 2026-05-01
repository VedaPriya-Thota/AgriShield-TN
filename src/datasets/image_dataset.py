# image_dataset.py — PyTorch Dataset that loads paddy leaf images and their labels.
#
# Reads image paths from train.csv and loads each image from the folder structure:
#   train_images/<disease_label>/<image_id>.jpg
#
# Each call to __getitem__ returns:
#   (image_tensor, label_tensor, metadata_dict)

from pathlib import Path

import cv2
import pandas as pd
import torch
from torch.utils.data import Dataset

from src.config.config import (
    TRAIN_CSV,
    TRAIN_IMAGE_DIR,
    IMAGE_ID_COL,
    LABEL_COL,
    VARIETY_COL,
    AGE_COL,
    CLASS_TO_IDX,
)


class PaddyImageDataset(Dataset):
    """
    PyTorch Dataset for Paddy Disease Classification.

    Expected training image structure:
        train_images/
            bacterial_leaf_blight/
                100023.jpg
            blast/
                100071.jpg
            ...

    Returns:
        image_tensor,
        label_tensor,
        metadata_dict
    """

    def __init__(self, csv_path=TRAIN_CSV, image_dir=TRAIN_IMAGE_DIR, transform=None):
        self.csv_path  = Path(csv_path)
        self.image_dir = Path(image_dir)
        self.transform = transform  # Albumentations pipeline (or None for raw numpy)

        # Validate that both the CSV and image folder exist before loading anything
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        if not self.image_dir.exists():
            raise FileNotFoundError(f"Image directory not found: {self.image_dir}")

        self.data = pd.read_csv(self.csv_path)

        # Ensure the CSV has all the columns the model needs
        required_columns = [IMAGE_ID_COL, LABEL_COL, VARIETY_COL, AGE_COL]
        missing_cols = [col for col in required_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in CSV: {missing_cols}")

        # Drop rows with no image_id or label — they can't be loaded
        self.data = self.data.dropna(subset=[IMAGE_ID_COL, LABEL_COL]).reset_index(drop=True)

        # Catch label typos early rather than crashing mid-training
        unknown_labels = sorted(set(self.data[LABEL_COL].unique()) - set(CLASS_TO_IDX.keys()))
        if unknown_labels:
            raise ValueError(
                f"These labels are present in train.csv but not in CLASS_NAMES/config.py: {unknown_labels}"
            )

    def __len__(self):
        return len(self.data)

    def _resolve_image_path(self, image_id: str, label_name: str) -> Path:
        """
        Training images are stored inside class folders:
        train_images/<label_name>/<image_id>.jpg

        Tries multiple extensions (.jpg, .JPG, .jpeg, .png) so the dataset
        works even if file extensions are inconsistent.
        """
        label_folder = self.image_dir / label_name

        possible_names = []

        # If image_id already has extension, use it directly
        if image_id.lower().endswith((".jpg", ".jpeg", ".png")):
            possible_names.append(image_id)
        else:
            # Try common image extensions since the CSV doesn't always include them
            possible_names.extend([
                f"{image_id}.jpg",
                f"{image_id}.JPG",
                f"{image_id}.jpeg",
                f"{image_id}.png",
            ])

        for name in possible_names:
            candidate = label_folder / name
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            f"Image not found for image_id='{image_id}' in label folder '{label_folder}'"
        )

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        # Read row values and handle missing metadata gracefully
        image_id   = str(row[IMAGE_ID_COL]).strip()
        label_name = str(row[LABEL_COL]).strip()
        variety    = str(row[VARIETY_COL]).strip() if pd.notna(row[VARIETY_COL]) else "unknown"
        age        = float(row[AGE_COL]) if pd.notna(row[AGE_COL]) else 0.0

        image_path = self._resolve_image_path(image_id=image_id, label_name=label_name)

        # Load image with OpenCV (reads as BGR by default)
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")

        # Convert BGR → RGB so colours match what the pretrained ResNet-18 expects
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Apply augmentation / normalisation if a transform pipeline was provided
        if self.transform is not None:
            transformed = self.transform(image=image)
            image = transformed["image"]   # now a CHW float tensor

        # Convert string label to integer index for CrossEntropyLoss
        label = CLASS_TO_IDX[label_name]

        # Pass along raw metadata so callers can inspect or log it
        metadata = {
            "image_id":   image_id,
            "label_name": label_name,
            "variety":    variety,
            "age":        age,
            "image_path": str(image_path),
        }

        return image, torch.tensor(label, dtype=torch.long), metadata
