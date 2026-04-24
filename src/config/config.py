# config.py — Central configuration for all paths, hyperparameters, and class labels.
# Import from here instead of hardcoding values anywhere else in the project.

from pathlib import Path

# =========================
# Project Paths
# =========================
# __file__ is src/config/config.py → go up 2 levels to reach the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR       = PROJECT_ROOT / "data"
RAW_DATA_DIR   = DATA_DIR / "raw"
METADATA_DIR   = DATA_DIR / "metadata"    # stores variety vocab and age stats
PROCESSED_DIR  = DATA_DIR / "processed"  # reserved for future pre-processed tensors

# CSV files that came with the dataset
TRAIN_CSV             = RAW_DATA_DIR / "train.csv"
SAMPLE_SUBMISSION_CSV = RAW_DATA_DIR / "sample_submission.csv"

# Folder layout expected by PaddyImageDataset:
#   train_images/<disease_class>/<image_id>.jpg
TRAIN_IMAGE_DIR = RAW_DATA_DIR / "train_images"
TEST_IMAGE_DIR  = RAW_DATA_DIR / "test_images"

# Where trained model weights and evaluation results are saved
CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
OUTPUT_DIR     = PROJECT_ROOT / "outputs"

# Create output directories on import so training scripts don't fail on first run
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Image / Training Config
# =========================
IMAGE_SIZE    = 224    # ResNet-18 expects 224×224 input (ImageNet standard)
BATCH_SIZE    = 16     # fits comfortably in CPU RAM and most GPUs
NUM_WORKERS   = 0      # 0 = load data on the main process (safe on Windows)
LEARNING_RATE = 1e-4   # Adam default; low enough for fine-tuning a pretrained backbone
NUM_EPOCHS    = 10     # enough for convergence on 10k images with pretrained weights
RANDOM_SEED   = 42     # fixes train/val split and augmentation randomness for reproducibility

# =========================
# CSV Columns
# =========================
# These must match the actual column names in train.csv exactly
IMAGE_ID_COL = "image_id"   # filename without path (e.g. "100023.jpg")
LABEL_COL    = "label"      # disease class string (e.g. "blast")
VARIETY_COL  = "variety"    # paddy variety name (e.g. "ADT45") — used by metadata model
AGE_COL      = "age"        # days after transplanting (numeric, ~45–120)

# =========================
# Class Names
# IMPORTANT:
# The order here defines the integer label mapping used by the model.
# Do NOT reorder — it would invalidate existing checkpoints.
# =========================
CLASS_NAMES = [
    "bacterial_leaf_blight",    # 0 — Xanthomonas oryzae pv. oryzae
    "bacterial_leaf_streak",    # 1 — Xanthomonas oryzae pv. oryzicola
    "bacterial_panicle_blight", # 2 — Burkholderia glumae
    "blast",                    # 3 — Magnaporthe oryzae (most destructive)
    "brown_spot",               # 4 — Bipolaris oryzae
    "dead_heart",               # 5 — stem borer damage (insect, not pathogen)
    "downy_mildew",             # 6 — Sclerophthora macrospora
    "hispa",                    # 7 — Dicladispa armigera beetle
    "normal",                   # 8 — healthy leaf, no disease
    "tungro",                   # 9 — dual-virus, spread by leafhoppers
]

NUM_CLASSES = len(CLASS_NAMES)  # 10

# Bidirectional lookup maps used during training and inference
CLASS_TO_IDX = {class_name: idx for idx, class_name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {idx: class_name for class_name, idx in CLASS_TO_IDX.items()}
