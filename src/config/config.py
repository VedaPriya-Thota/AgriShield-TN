from pathlib import Path

# =========================
# Project Paths
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
METADATA_DIR = DATA_DIR / "metadata"
PROCESSED_DIR = DATA_DIR / "processed"

TRAIN_CSV = RAW_DATA_DIR / "train.csv"
SAMPLE_SUBMISSION_CSV = RAW_DATA_DIR / "sample_submission.csv"
TRAIN_IMAGE_DIR = RAW_DATA_DIR / "train_images"
TEST_IMAGE_DIR = RAW_DATA_DIR / "test_images"

CHECKPOINT_DIR = PROJECT_ROOT / "checkpoints"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Image / Training Config
# =========================
IMAGE_SIZE = 224
BATCH_SIZE = 16
NUM_WORKERS = 0
LEARNING_RATE = 1e-4
NUM_EPOCHS = 10
RANDOM_SEED = 42

# =========================
# CSV Columns
# =========================
IMAGE_ID_COL = "image_id"
LABEL_COL = "label"
VARIETY_COL = "variety"
AGE_COL = "age"

# =========================
# Class Names
# IMPORTANT:
# If labels differ in your train.csv, update this list
# =========================
CLASS_NAMES = [
    "bacterial_leaf_blight",
    "bacterial_leaf_streak",
    "bacterial_panicle_blight",
    "blast",
    "brown_spot",
    "dead_heart",
    "downy_mildew",
    "hispa",
    "normal",
    "tungro",
]

NUM_CLASSES = len(CLASS_NAMES)

CLASS_TO_IDX = {class_name: idx for idx, class_name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS = {idx: class_name for class_name, idx in CLASS_TO_IDX.items()}