"""
train_metadata_classifier.py
=============================
Trains PaddyMetadataClassifier (image + variety + age fusion).

Improvements over image-only training
──────────────────────────────────────
- Age is z-score normalised using training-split statistics only (no leakage).
- Cosine-annealing LR schedule for smooth convergence.
- Label smoothing (ε=0.05) to improve calibration.
- L2 weight decay via Adam.
- Early stopping with configurable patience.
- Checkpoint saves variety vocabulary + age stats alongside model weights so
  that inference can reconstruct the exact preprocessing transform.

Checkpoint format
─────────────────
{
    "model_state_dict" : OrderedDict,   # model.state_dict()
    "num_varieties"    : int,
    "variety_to_idx"   : Dict[str, int],
    "age_mean"         : float,
    "age_std"          : float,
    "val_acc"          : float,
    "epoch"            : int,
}

Usage
─────
  python -m src.training.train_metadata_classifier
"""

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
from src.datasets.metadata_dataset import PaddyMetadataDataset
from src.datasets.transforms import get_train_transforms, get_val_transforms
from src.models.metadata_classifier import PaddyMetadataClassifier

# ── Early stopping patience (epochs without val_acc improvement) ───────────────
PATIENCE = 5


# ─────────────────────────────────────────────────────────────────────────────
#  Utilities
# ─────────────────────────────────────────────────────────────────────────────

def set_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ─────────────────────────────────────────────────────────────────────────────
#  Data loading
# ─────────────────────────────────────────────────────────────────────────────

def create_dataloaders():
    """
    Returns
    -------
    train_loader, val_loader, num_varieties, variety_to_idx, age_mean, age_std
    """
    # Load dataset once (no transforms) to compute split indices and age stats.
    base_dataset = PaddyMetadataDataset(transform=None)

    labels  = base_dataset.data["label"].tolist()
    indices = list(range(len(base_dataset)))

    train_indices, val_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=labels,
    )

    # Compute age normalisation statistics from the training split only.
    train_ages = base_dataset.data.iloc[train_indices]["age"].fillna(0.0).astype(float)
    age_mean   = float(train_ages.mean())
    age_std    = float(train_ages.std())
    if age_std < 1e-6:
        age_std = 1.0   # guard: constant-age dataset

    print(f"  Train samples  : {len(train_indices)}")
    print(f"  Val   samples  : {len(val_indices)}")
    print(f"  Varieties      : {base_dataset.num_varieties}")
    print(f"  Age  mean/std  : {age_mean:.2f} / {age_std:.2f}")

    # Build augmented datasets that share the same vocabulary and age stats.
    train_dataset = PaddyMetadataDataset(
        transform=get_train_transforms(),
        age_mean=age_mean,
        age_std=age_std,
    )
    val_dataset = PaddyMetadataDataset(
        transform=get_val_transforms(),
        age_mean=age_mean,
        age_std=age_std,
    )

    train_loader = DataLoader(
        Subset(train_dataset, train_indices),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
    )
    val_loader = DataLoader(
        Subset(val_dataset, val_indices),
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
    )

    return (
        train_loader,
        val_loader,
        base_dataset.num_varieties,
        base_dataset.variety_to_idx,
        age_mean,
        age_std,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Train / validate one epoch
# ─────────────────────────────────────────────────────────────────────────────

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct      = 0
    total        = 0

    progress = tqdm(loader, desc="Train", leave=False)
    for images, variety_idx, age, labels, _ in progress:
        images      = images.to(device)
        variety_idx = variety_idx.to(device)
        age         = age.to(device)
        labels      = labels.to(device)

        optimizer.zero_grad()
        logits = model(images, variety_idx, age)
        loss   = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        correct      += (torch.argmax(logits, dim=1) == labels).sum().item()
        total        += labels.size(0)
        progress.set_postfix(loss=f"{loss.item():.4f}")

    return running_loss / total, correct / total


@torch.no_grad()
def validate_one_epoch(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct      = 0
    total        = 0

    for images, variety_idx, age, labels, _ in tqdm(loader, desc="Val", leave=False):
        images      = images.to(device)
        variety_idx = variety_idx.to(device)
        age         = age.to(device)
        labels      = labels.to(device)

        logits = model(images, variety_idx, age)
        loss   = criterion(logits, labels)

        running_loss += loss.item() * images.size(0)
        correct      += (torch.argmax(logits, dim=1) == labels).sum().item()
        total        += labels.size(0)

    return running_loss / total, correct / total


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    set_seed()
    device = get_device()
    print(f"\nDevice : {device}")

    (
        train_loader,
        val_loader,
        num_varieties,
        variety_to_idx,
        age_mean,
        age_std,
    ) = create_dataloaders()

    model = PaddyMetadataClassifier(
        num_varieties=num_varieties,
        pretrained=True,
    ).to(device)

    # Label smoothing improves calibration without extra cost.
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    # Adam with L2 regularisation.
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=1e-4,
    )

    # Cosine annealing: lr decays from LEARNING_RATE → LEARNING_RATE * 0.01
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=NUM_EPOCHS,
        eta_min=LEARNING_RATE * 0.01,
    )

    best_val_acc      = 0.0
    best_model_state  = None
    patience_counter  = 0
    save_path         = CHECKPOINT_DIR / "best_metadata_classifier.pth"

    for epoch in range(NUM_EPOCHS):
        current_lr = scheduler.get_last_lr()[0]
        print(f"\nEpoch [{epoch + 1}/{NUM_EPOCHS}]  lr={current_lr:.2e}")

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_loss, val_acc = validate_one_epoch(
            model, val_loader, criterion, device
        )

        scheduler.step()

        print(
            f"  train  loss={train_loss:.4f}  acc={train_acc:.4f}\n"
            f"  val    loss={val_loss:.4f}  acc={val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc     = val_acc
            best_model_state = deepcopy(model.state_dict())
            patience_counter = 0

            # Save model weights + preprocessing vocabulary so inference can
            # reconstruct the exact transform without reloading the dataset.
            checkpoint = {
                "model_state_dict": best_model_state,
                "num_varieties":    num_varieties,
                "variety_to_idx":   variety_to_idx,
                "age_mean":         age_mean,
                "age_std":          age_std,
                "val_acc":          best_val_acc,
                "epoch":            epoch + 1,
            }
            torch.save(checkpoint, save_path)
            print(f"  Saved best model → {save_path}  (val_acc={best_val_acc:.4f})")

        else:
            patience_counter += 1
            print(f"  No improvement ({patience_counter}/{PATIENCE})")
            if patience_counter >= PATIENCE:
                print(f"\nEarly stopping triggered after {epoch + 1} epochs.")
                break

    print(f"\nBest Validation Accuracy : {best_val_acc:.4f}")


if __name__ == "__main__":
    main()
