# train_classifier.py — Main training script for the image-only disease classifier.
#
# What this script does:
#   1. Loads the full dataset from train.csv and splits it 80/20 (stratified by class)
#   2. Creates two DataLoaders: one with augmentation (train) and one without (val)
#   3. Trains PaddyDiseaseClassifier for NUM_EPOCHS using Adam + CrossEntropyLoss
#   4. Saves the best model weights (by val accuracy) to checkpoints/
#
# Run with: python -m src.training.train_classifier

import random
from copy import deepcopy

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset
from tqdm import tqdm

from src.config.config import (
    BATCH_SIZE,
    CHECKPOINT_DIR,
    LEARNING_RATE,
    NUM_EPOCHS,
    NUM_WORKERS,
    RANDOM_SEED,
)
from src.datasets.image_dataset import PaddyImageDataset
from src.datasets.transforms import get_train_transforms, get_val_transforms
from src.models.disease_classifier import PaddyDiseaseClassifier


def set_seed(seed: int = RANDOM_SEED):
    # Fix all random number generators so results are reproducible across runs
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device():
    # Use GPU if available, otherwise fall back to CPU
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def create_dataloaders():
    # Load dataset once without any transform just to get the list of labels for stratified split
    base_dataset = PaddyImageDataset(transform=None)

    labels  = base_dataset.data["label"].tolist()
    indices = list(range(len(base_dataset)))

    # Stratified split ensures each class has ~80% in train and ~20% in val
    train_indices, val_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=labels  # preserves class distribution across both splits
    )

    # Create two separate dataset objects with different transforms
    # (we can't reuse one dataset object because the transform is baked in)
    train_dataset = PaddyImageDataset(transform=get_train_transforms())
    val_dataset   = PaddyImageDataset(transform=get_val_transforms())

    # Wrap with Subset to apply the train/val index split
    train_subset = Subset(train_dataset, train_indices)
    val_subset   = Subset(val_dataset, val_indices)

    # shuffle=True for training (important for SGD convergence)
    # shuffle=False for validation (order doesn't matter, just need consistent metrics)
    train_loader = DataLoader(
        train_subset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS
    )

    val_loader = DataLoader(
        val_subset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    print(f"Train samples: {len(train_subset)}")
    print(f"Validation samples: {len(val_subset)}")

    return train_loader, val_loader


def train_one_epoch(model, loader, criterion, optimizer, device):
    # Switch model to training mode: activates Dropout and BatchNorm updates
    model.train()

    running_loss = 0.0
    correct      = 0
    total        = 0

    progress_bar = tqdm(loader, desc="Training", leave=False)

    for images, labels, _ in progress_bar:
        # Move batch to GPU/CPU
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()          # clear gradients from the previous step

        logits = model(images)         # forward pass → raw class scores
        loss   = criterion(logits, labels)  # CrossEntropyLoss (applies softmax internally)

        loss.backward()                # backpropagation: compute gradients
        optimizer.step()               # update weights using Adam

        # Accumulate metrics for reporting at end of epoch
        running_loss += loss.item() * images.size(0)  # weight by batch size

        preds    = torch.argmax(logits, dim=1)         # predicted class index
        correct += (preds == labels).sum().item()
        total   += labels.size(0)

        progress_bar.set_postfix(loss=loss.item())

    epoch_loss = running_loss / total
    epoch_acc  = correct / total

    return epoch_loss, epoch_acc


@torch.no_grad()  # disable gradient tracking — faster and uses less memory during eval
def validate_one_epoch(model, loader, criterion, device):
    # Switch model to eval mode: disables Dropout, fixes BatchNorm stats
    model.eval()

    running_loss = 0.0
    correct      = 0
    total        = 0

    progress_bar = tqdm(loader, desc="Validation", leave=False)

    for images, labels, _ in progress_bar:
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        loss   = criterion(logits, labels)

        running_loss += loss.item() * images.size(0)

        preds    = torch.argmax(logits, dim=1)
        correct += (preds == labels).sum().item()
        total   += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc  = correct / total

    return epoch_loss, epoch_acc


def main():
    set_seed()
    device = get_device()

    print(f"Using device: {device}")

    train_loader, val_loader = create_dataloaders()

    # Build model with pretrained ImageNet backbone for faster convergence
    model = PaddyDiseaseClassifier(pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()  # standard multi-class loss
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Track the best validation accuracy to know when to save the checkpoint
    best_val_acc    = 0.0
    best_model_state = None

    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch [{epoch + 1}/{NUM_EPOCHS}]")

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )

        val_loss, val_acc = validate_one_epoch(
            model, val_loader, criterion, device
        )

        print(
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
        )

        # Save checkpoint only when validation accuracy improves
        # deepcopy ensures we store a snapshot, not a reference to the live model
        if val_acc > best_val_acc:
            best_val_acc    = val_acc
            best_model_state = deepcopy(model.state_dict())

            save_path = CHECKPOINT_DIR / "best_disease_classifier.pth"
            torch.save(best_model_state, save_path)
            print(f"Saved best model to: {save_path}")

    print(f"\nBest Validation Accuracy: {best_val_acc:.4f}")


if __name__ == "__main__":
    main()
