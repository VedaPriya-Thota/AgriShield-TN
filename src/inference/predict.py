from pathlib import Path
from typing import Dict, Tuple

import cv2
import torch

from src.config.config import (
    CHECKPOINT_DIR,
    IDX_TO_CLASS,
)
from src.datasets.transforms import get_val_transforms
from src.models.disease_classifier import PaddyDiseaseClassifier


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(
    checkpoint_path: Path = CHECKPOINT_DIR / "best_disease_classifier.pth",
    device: torch.device = None
):
    if device is None:
        device = get_device()

    model = PaddyDiseaseClassifier(pretrained=False).to(device)

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}\n"
            f"Train the model first before running inference."
        )

    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    return model


def preprocess_image(image_path: str):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    transform = get_val_transforms()
    transformed = transform(image=image)
    image_tensor = transformed["image"].unsqueeze(0)  # [1, C, H, W]

    return image, image_tensor


@torch.no_grad()
def predict_image(image_path: str) -> Tuple[str, float, Dict[str, float]]:
    device = get_device()
    model = load_model(device=device)

    original_image, image_tensor = preprocess_image(image_path)
    image_tensor = image_tensor.to(device)

    logits = model(image_tensor)
    probabilities = torch.softmax(logits, dim=1)[0]

    predicted_idx = torch.argmax(probabilities).item()
    predicted_class = IDX_TO_CLASS[predicted_idx]
    confidence = probabilities[predicted_idx].item()

    class_probabilities = {
        IDX_TO_CLASS[i]: float(probabilities[i].item())
        for i in range(len(probabilities))
    }

    return predicted_class, confidence, class_probabilities


if __name__ == "__main__":
    sample_path = input("Enter image path: ").strip()
    pred_class, confidence, probs = predict_image(sample_path)

    print(f"\nPredicted Class: {pred_class}")
    print(f"Confidence: {confidence:.4f}")
    print("\nTop class probabilities:")
    for class_name, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
        print(f"{class_name}: {prob:.4f}")