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
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def create_dataloaders():
    # Load full dataset once to get labels and indices
    base_dataset = PaddyImageDataset(transform=None)

    labels = base_dataset.data["label"].tolist()
    indices = list(range(len(base_dataset)))

    train_indices, val_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=labels
    )

    train_dataset = PaddyImageDataset(transform=get_train_transforms())
    val_dataset = PaddyImageDataset(transform=get_val_transforms())

    train_subset = Subset(train_dataset, train_indices)
    val_subset = Subset(val_dataset, val_indices)

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
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    progress_bar = tqdm(loader, desc="Training", leave=False)

    for images, labels, _ in progress_bar:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        logits = model(images)
        loss = criterion(logits, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

        preds = torch.argmax(logits, dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

        progress_bar.set_postfix(loss=loss.item())

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc


@torch.no_grad()
def validate_one_epoch(model, loader, criterion, device):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    progress_bar = tqdm(loader, desc="Validation", leave=False)

    for images, labels, _ in progress_bar:
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        loss = criterion(logits, labels)

        running_loss += loss.item() * images.size(0)

        preds = torch.argmax(logits, dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc


def main():
    set_seed()
    device = get_device()

    print(f"Using device: {device}")

    train_loader, val_loader = create_dataloaders()

    model = PaddyDiseaseClassifier(pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_acc = 0.0
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

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = deepcopy(model.state_dict())

            save_path = CHECKPOINT_DIR / "best_disease_classifier.pth"
            torch.save(best_model_state, save_path)
            print(f"Saved best model to: {save_path}")

    print(f"\nBest Validation Accuracy: {best_val_acc:.4f}")


if __name__ == "__main__":
    main()