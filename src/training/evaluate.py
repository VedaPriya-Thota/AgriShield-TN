from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset

from src.config.config import (
    BATCH_SIZE,
    CHECKPOINT_DIR,
    NUM_WORKERS,
    OUTPUT_DIR,
    RANDOM_SEED,
    IDX_TO_CLASS,
)
from src.datasets.image_dataset import PaddyImageDataset
from src.datasets.transforms import get_val_transforms
from src.models.disease_classifier import PaddyDiseaseClassifier


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(device):
    checkpoint_path = CHECKPOINT_DIR / "best_disease_classifier.pth"

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}\n"
            f"Please train the model first."
        )

    model = PaddyDiseaseClassifier(pretrained=False).to(device)
    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    return model


def create_val_loader():
    base_dataset = PaddyImageDataset(transform=None)

    labels = base_dataset.data["label"].tolist()
    indices = list(range(len(base_dataset)))

    _, val_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=labels
    )

    val_dataset = PaddyImageDataset(transform=get_val_transforms())
    val_subset = Subset(val_dataset, val_indices)

    val_loader = DataLoader(
        val_subset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    print(f"Validation samples: {len(val_subset)}")
    return val_loader


@torch.no_grad()
def get_predictions(model, loader, device):
    all_labels = []
    all_preds = []

    for images, labels, _ in loader:
        images = images.to(device)
        labels = labels.to(device)

        logits = model(images)
        preds = torch.argmax(logits, dim=1)

        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())

    return np.array(all_labels), np.array(all_preds)


def save_classification_report(report_dict, output_path: Path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=4)


def plot_confusion_matrix(cm, class_names, save_path: Path):
    plt.figure(figsize=(12, 10))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Confusion Matrix")
    plt.colorbar()

    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45, ha="right")
    plt.yticks(tick_marks, class_names)

    threshold = cm.max() / 2.0 if cm.max() > 0 else 0

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j, i, format(cm[i, j], "d"),
                horizontalalignment="center",
                color="white" if cm[i, j] > threshold else "black"
            )

    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    device = get_device()
    print(f"Using device: {device}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model = load_model(device)
    val_loader = create_val_loader()

    y_true, y_pred = get_predictions(model, val_loader, device)

    accuracy = accuracy_score(y_true, y_pred)

    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )

    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    class_names = [IDX_TO_CLASS[i] for i in range(len(IDX_TO_CLASS))]
    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(y_true, y_pred)

    print("\n========== Evaluation Results ==========")
    print(f"Accuracy           : {accuracy:.4f}")
    print(f"Precision (Macro)  : {precision_macro:.4f}")
    print(f"Recall (Macro)     : {recall_macro:.4f}")
    print(f"F1 Score (Macro)   : {f1_macro:.4f}")
    print(f"Precision (Weighted): {precision_weighted:.4f}")
    print(f"Recall (Weighted)   : {recall_weighted:.4f}")
    print(f"F1 Score (Weighted) : {f1_weighted:.4f}")

    print("\n========== Classification Report ==========")
    print(classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        zero_division=0
    ))

    metrics_summary = {
        "accuracy": accuracy,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "precision_weighted": precision_weighted,
        "recall_weighted": recall_weighted,
        "f1_weighted": f1_weighted,
    }

    metrics_path = OUTPUT_DIR / "evaluation_metrics.json"
    report_path = OUTPUT_DIR / "classification_report.json"
    cm_path = OUTPUT_DIR / "confusion_matrix.png"

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=4)

    save_classification_report(report, report_path)
    plot_confusion_matrix(cm, class_names, cm_path)

    print("\nSaved files:")
    print(f"- Metrics summary       : {metrics_path}")
    print(f"- Classification report : {report_path}")
    print(f"- Confusion matrix plot : {cm_path}")


if __name__ == "__main__":
    main()