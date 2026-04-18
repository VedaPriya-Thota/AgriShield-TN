"""
evaluate.py
===========
Full evaluation suite for the trained PaddyDiseaseClassifier.

Outputs (all written to OUTPUT_DIR)
────────────────────────────────────
  confusion_matrix.png            – raw-count confusion matrix
  confusion_matrix_normalized.png – row-normalised (recall-per-class) matrix
  class_accuracy.png              – per-class accuracy horizontal bar chart
  class_metrics.png               – per-class precision / recall / F1 grouped bars
  evaluation_metrics.json         – overall + per-class scalar metrics
  classification_report.json      – sklearn classification_report dict

Usage
─────
  python -m src.training.evaluate
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")                    # headless backend — no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    IDX_TO_CLASS,
    NUM_WORKERS,
    OUTPUT_DIR,
    RANDOM_SEED,
)
from src.datasets.image_dataset import PaddyImageDataset
from src.datasets.transforms import get_val_transforms
from src.models.disease_classifier import PaddyDiseaseClassifier


# ─────────────────────────────────────────────────────────────────────────────
#  Colour palette (consistent across all charts)
# ─────────────────────────────────────────────────────────────────────────────
_BG       = "#0d1117"   # dark background
_FG       = "#c9d1d9"   # primary text
_GRID     = "#21262d"   # subtle gridline
_GREEN    = "#3fb950"   # precision / high-accuracy
_BLUE     = "#58a6ff"   # recall
_PURPLE   = "#bc8cff"   # F1
_AMBER    = "#d29922"   # low-accuracy warning
_RED      = "#f85149"   # lowest tier

# Ordered display names (underscore → title-case)
_CLASS_NAMES: List[str] = [IDX_TO_CLASS[i] for i in range(len(IDX_TO_CLASS))]
_SHORT_NAMES: List[str] = [n.replace("_", "\n") for n in _CLASS_NAMES]


# ─────────────────────────────────────────────────────────────────────────────
#  Setup helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _apply_dark_style(fig: plt.Figure, axes) -> None:
    """Apply dark theme to a figure and one or more axes."""
    fig.patch.set_facecolor(_BG)
    ax_list = axes if isinstance(axes, (list, np.ndarray)) else [axes]
    for ax in np.array(ax_list).flat:
        ax.set_facecolor(_BG)
        ax.tick_params(colors=_FG, labelsize=9)
        ax.xaxis.label.set_color(_FG)
        ax.yaxis.label.set_color(_FG)
        ax.title.set_color(_FG)
        for spine in ax.spines.values():
            spine.set_edgecolor(_GRID)


# ─────────────────────────────────────────────────────────────────────────────
#  Model + data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_model(device: torch.device) -> PaddyDiseaseClassifier:
    checkpoint_path = CHECKPOINT_DIR / "best_disease_classifier.pth"
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}\n"
            "Please train the model first using train_classifier.py"
        )
    model = PaddyDiseaseClassifier(pretrained=False).to(device)
    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def create_val_loader() -> Tuple[DataLoader, int]:
    base_dataset = PaddyImageDataset(transform=None)
    labels  = base_dataset.data["label"].tolist()
    indices = list(range(len(base_dataset)))

    _, val_indices = train_test_split(
        indices, test_size=0.2, random_state=RANDOM_SEED, stratify=labels
    )

    val_dataset = PaddyImageDataset(transform=get_val_transforms())
    val_subset  = Subset(val_dataset, val_indices)
    val_loader  = DataLoader(
        val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS
    )
    print(f"Validation samples : {len(val_subset)}")
    return val_loader, len(val_subset)


@torch.no_grad()
def get_predictions(
    model: PaddyDiseaseClassifier,
    loader: DataLoader,
    device: torch.device,
) -> Tuple[np.ndarray, np.ndarray]:
    all_labels: List[int] = []
    all_preds:  List[int] = []

    for images, labels, _ in loader:
        images = images.to(device)
        preds  = torch.argmax(model(images), dim=1)
        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())

    return np.array(all_labels), np.array(all_preds)


# ─────────────────────────────────────────────────────────────────────────────
#  Plot 1 – Raw-count confusion matrix
# ─────────────────────────────────────────────────────────────────────────────

def plot_confusion_matrix(cm: np.ndarray, save_path: Path) -> None:
    """Dark-themed confusion matrix showing raw sample counts."""
    n = len(_CLASS_NAMES)
    fig, ax = plt.subplots(figsize=(13, 11))
    _apply_dark_style(fig, ax)

    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=_FG, labelsize=8)
    cbar.outline.set_edgecolor(_GRID)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(_SHORT_NAMES, fontsize=8, color=_FG)
    ax.set_yticklabels(_SHORT_NAMES, fontsize=8, color=_FG)
    ax.xaxis.set_tick_params(rotation=45)

    threshold = cm.max() / 2.0 if cm.max() > 0 else 1
    for i in range(n):
        for j in range(n):
            val = cm[i, j]
            color = "white" if val > threshold else _FG
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=8, color=color, fontweight="bold" if i == j else "normal")

    ax.set_xlabel("Predicted Label", fontsize=11, labelpad=10)
    ax.set_ylabel("True Label",      fontsize=11, labelpad=10)
    ax.set_title("Confusion Matrix  (raw counts)", fontsize=13,
                 color=_FG, pad=14, fontweight="bold")

    # Highlight diagonal with a green border
    for i in range(n):
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (i - 0.5, i - 0.5), 1, 1,
                linewidth=1.4, edgecolor=_GREEN,
                boxstyle="square,pad=0", fill=False, zorder=3,
            )
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  Saved : {save_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  Plot 2 – Row-normalised confusion matrix
# ─────────────────────────────────────────────────────────────────────────────

def plot_confusion_matrix_normalized(cm: np.ndarray, save_path: Path) -> None:
    """
    Row-normalised matrix: each row sums to 1.0 so diagonal = per-class recall.
    Makes class-imbalance visible without count magnitudes overwhelming the plot.
    """
    n          = len(_CLASS_NAMES)
    row_sums   = cm.sum(axis=1, keepdims=True).clip(min=1)
    cm_norm    = cm.astype(float) / row_sums

    fig, ax = plt.subplots(figsize=(13, 11))
    _apply_dark_style(fig, ax)

    im = ax.imshow(cm_norm, interpolation="nearest", cmap="RdYlGn",
                   vmin=0.0, vmax=1.0)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=_FG, labelsize=8)
    cbar.ax.set_ylabel("Recall proportion", color=_FG, fontsize=9, labelpad=8)
    cbar.outline.set_edgecolor(_GRID)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(_SHORT_NAMES, fontsize=8, color=_FG)
    ax.set_yticklabels(_SHORT_NAMES, fontsize=8, color=_FG)
    ax.xaxis.set_tick_params(rotation=45)

    for i in range(n):
        for j in range(n):
            pct   = cm_norm[i, j]
            count = cm[i, j]
            # Label: percentage on top, raw count in small text below
            ax.text(j, i - 0.12, f"{pct:.0%}", ha="center", va="center",
                    fontsize=7, color="black" if pct > 0.45 else _FG,
                    fontweight="bold")
            ax.text(j, i + 0.22, f"n={count}", ha="center", va="center",
                    fontsize=6, color="black" if pct > 0.45 else "#6e7681")

    ax.set_xlabel("Predicted Label", fontsize=11, labelpad=10)
    ax.set_ylabel("True Label",      fontsize=11, labelpad=10)
    ax.set_title("Confusion Matrix  (row-normalised · diagonal = per-class recall)",
                 fontsize=12, color=_FG, pad=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  Saved : {save_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  Plot 3 – Per-class accuracy horizontal bar chart
# ─────────────────────────────────────────────────────────────────────────────

def plot_class_accuracy(cm: np.ndarray, save_path: Path) -> None:
    """
    Horizontal bar chart: one bar per class showing that class's accuracy
    (TP / total true instances for that class = per-row recall).
    Sorted ascending so lowest-accuracy classes appear at top for easy scanning.
    """
    row_sums     = cm.sum(axis=1).clip(min=1)
    per_class_acc = cm.diagonal().astype(float) / row_sums   # same as recall

    # Sort ascending (worst → best)
    order        = np.argsort(per_class_acc)
    sorted_acc   = per_class_acc[order]
    sorted_names = [_CLASS_NAMES[i].replace("_", " ").title() for i in order]

    fig, ax = plt.subplots(figsize=(11, 7))
    _apply_dark_style(fig, ax)

    # Colour each bar by its value: red < 0.60, amber < 0.80, green >= 0.80
    colors = [
        _RED   if v < 0.60 else
        _AMBER if v < 0.80 else
        _GREEN
        for v in sorted_acc
    ]

    bars = ax.barh(range(len(sorted_acc)), sorted_acc, color=colors,
                   height=0.6, edgecolor=_BG, linewidth=0.6)

    # Value labels at the end of each bar
    for bar, val in zip(bars, sorted_acc):
        ax.text(
            val + 0.008, bar.get_y() + bar.get_height() / 2,
            f"{val:.1%}", va="center", ha="left",
            fontsize=9, color=_FG, fontweight="bold",
        )

    ax.set_yticks(range(len(sorted_names)))
    ax.set_yticklabels(sorted_names, fontsize=9)
    ax.set_xlim(0, 1.12)
    ax.set_xlabel("Per-class Accuracy (= Recall)", fontsize=11, labelpad=8)
    ax.set_title("Class-wise Accuracy", fontsize=13,
                 color=_FG, pad=12, fontweight="bold")

    ax.axvline(x=per_class_acc.mean(), color=_BLUE, linestyle="--",
               linewidth=1.2, label=f"Mean  {per_class_acc.mean():.1%}")

    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1))
    ax.grid(axis="x", color=_GRID, linewidth=0.6, linestyle="--")

    # Legend: colour key + mean line
    patches = [
        mpatches.Patch(color=_GREEN, label="≥ 80%"),
        mpatches.Patch(color=_AMBER, label="60–80%"),
        mpatches.Patch(color=_RED,   label="< 60%"),
    ]
    ax.legend(handles=patches + [
        plt.Line2D([0], [0], color=_BLUE, linestyle="--", linewidth=1.2,
                   label=f"Mean  {per_class_acc.mean():.1%}")
    ], loc="lower right", facecolor=_BG, edgecolor=_GRID,
       labelcolor=_FG, fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  Saved : {save_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  Plot 4 – Per-class Precision / Recall / F1 grouped bars
# ─────────────────────────────────────────────────────────────────────────────

def plot_class_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    save_path: Path,
) -> None:
    """
    Grouped horizontal bar chart: precision, recall and F1 side-by-side for
    each class.  Classes sorted by F1 ascending (worst-first, best at bottom).
    """
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(_CLASS_NAMES))),
        average=None, zero_division=0,
    )

    # Sort by F1 ascending
    order = np.argsort(f1)
    n     = len(_CLASS_NAMES)

    fig, ax = plt.subplots(figsize=(12, 8))
    _apply_dark_style(fig, ax)

    bar_h  = 0.24
    y_base = np.arange(n)

    ax.barh(y_base + bar_h,      precision[order], height=bar_h,
            color=_GREEN,  label="Precision", edgecolor=_BG, linewidth=0.5)
    ax.barh(y_base,              recall[order],    height=bar_h,
            color=_BLUE,   label="Recall",    edgecolor=_BG, linewidth=0.5)
    ax.barh(y_base - bar_h,      f1[order],        height=bar_h,
            color=_PURPLE, label="F1 Score",  edgecolor=_BG, linewidth=0.5)

    # Value annotations
    for i, idx in enumerate(order):
        for val, offset, color in [
            (precision[idx], bar_h,  _GREEN),
            (recall[idx],    0,      _BLUE),
            (f1[idx],       -bar_h,  _PURPLE),
        ]:
            ax.text(val + 0.006, i + offset,
                    f"{val:.2f}", va="center", ha="left",
                    fontsize=7.5, color=color)

    sorted_names = [_CLASS_NAMES[i].replace("_", " ").title() for i in order]
    ax.set_yticks(y_base)
    ax.set_yticklabels(sorted_names, fontsize=9)
    ax.set_xlim(0, 1.18)
    ax.set_xlabel("Score", fontsize=11, labelpad=8)
    ax.set_title("Per-class Precision · Recall · F1",
                 fontsize=13, color=_FG, pad=12, fontweight="bold")

    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1))
    ax.grid(axis="x", color=_GRID, linewidth=0.6, linestyle="--")

    ax.legend(facecolor=_BG, edgecolor=_GRID, labelcolor=_FG, fontsize=9,
              loc="lower right")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  Saved : {save_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  Metrics serialisation
# ─────────────────────────────────────────────────────────────────────────────

def build_metrics_dict(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    cm: np.ndarray,
) -> Dict:
    """
    Returns a JSON-serialisable dict with:
    - overall scalar metrics (accuracy, macro / weighted P/R/F1)
    - per-class breakdown (accuracy, precision, recall, F1, support)
    """
    accuracy = float(accuracy_score(y_true, y_pred))

    p_mac, r_mac, f_mac, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    p_wt, r_wt, f_wt, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    # Per-class
    p_cls, r_cls, f_cls, sup_cls = precision_recall_fscore_support(
        y_true, y_pred,
        labels=list(range(len(_CLASS_NAMES))),
        average=None, zero_division=0,
    )
    row_sums      = cm.sum(axis=1).clip(min=1)
    per_class_acc = (cm.diagonal().astype(float) / row_sums).tolist()

    per_class = {}
    for i, cls_name in enumerate(_CLASS_NAMES):
        per_class[cls_name] = {
            "accuracy" : round(per_class_acc[i], 6),
            "precision": round(float(p_cls[i]),  6),
            "recall"   : round(float(r_cls[i]),  6),
            "f1"       : round(float(f_cls[i]),  6),
            "support"  : int(sup_cls[i]),
        }

    return {
        "overall": {
            "accuracy"          : round(accuracy,        6),
            "precision_macro"   : round(float(p_mac),    6),
            "recall_macro"      : round(float(r_mac),    6),
            "f1_macro"          : round(float(f_mac),    6),
            "precision_weighted": round(float(p_wt),     6),
            "recall_weighted"   : round(float(r_wt),     6),
            "f1_weighted"       : round(float(f_wt),     6),
        },
        "per_class": per_class,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Console summary
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(metrics: Dict) -> None:
    ov = metrics["overall"]
    print("\n" + "=" * 52)
    print("  EVALUATION RESULTS")
    print("=" * 52)
    print(f"  Accuracy              : {ov['accuracy']:.4f}")
    print(f"  Precision  (macro)    : {ov['precision_macro']:.4f}")
    print(f"  Recall     (macro)    : {ov['recall_macro']:.4f}")
    print(f"  F1         (macro)    : {ov['f1_macro']:.4f}")
    print(f"  Precision  (weighted) : {ov['precision_weighted']:.4f}")
    print(f"  Recall     (weighted) : {ov['recall_weighted']:.4f}")
    print(f"  F1         (weighted) : {ov['f1_weighted']:.4f}")
    print("-" * 52)
    print(f"  {'Class':<36} {'Acc':>6}  {'F1':>6}")
    print("-" * 52)
    for cls, v in sorted(metrics["per_class"].items(),
                         key=lambda kv: kv[1]["f1"]):
        print(f"  {cls:<36} {v['accuracy']:>6.1%}  {v['f1']:>6.4f}")
    print("=" * 52)


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    device = get_device()
    print(f"Device : {device}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model      = load_model(device)
    val_loader, _ = create_val_loader()

    print("\nRunning inference…")
    y_true, y_pred = get_predictions(model, val_loader, device)

    cm      = confusion_matrix(y_true, y_pred, labels=list(range(len(_CLASS_NAMES))))
    metrics = build_metrics_dict(y_true, y_pred, cm)
    report  = classification_report(
        y_true, y_pred,
        target_names=_CLASS_NAMES,
        output_dict=True,
        zero_division=0,
    )

    print_summary(metrics)

    # ── Console text report ───────────────────────────────────────────────────
    print("\n" + classification_report(
        y_true, y_pred, target_names=_CLASS_NAMES, zero_division=0
    ))

    # ── Save plots ────────────────────────────────────────────────────────────
    print("\nSaving outputs…")

    plot_confusion_matrix(
        cm,
        OUTPUT_DIR / "confusion_matrix.png",
    )
    plot_confusion_matrix_normalized(
        cm,
        OUTPUT_DIR / "confusion_matrix_normalized.png",
    )
    plot_class_accuracy(
        cm,
        OUTPUT_DIR / "class_accuracy.png",
    )
    plot_class_metrics(
        y_true, y_pred,
        OUTPUT_DIR / "class_metrics.png",
    )

    # ── Save JSON ─────────────────────────────────────────────────────────────
    metrics_path = OUTPUT_DIR / "evaluation_metrics.json"
    report_path  = OUTPUT_DIR / "classification_report.json"

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print(f"  Saved : {metrics_path}")

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"  Saved : {report_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
