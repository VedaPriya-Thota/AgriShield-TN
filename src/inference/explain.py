from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms as T

from src.config.config import CHECKPOINT_DIR, IDX_TO_CLASS, IMAGE_SIZE
from src.models.disease_classifier import PaddyDiseaseClassifier


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer

        self.gradients = None
        self.activations = None

        self.forward_hook = target_layer.register_forward_hook(self.save_activation)
        self.backward_hook = target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def remove_hooks(self):
        self.forward_hook.remove()
        self.backward_hook.remove()

    def generate(self, input_tensor, class_idx=None):
        self.model.zero_grad()

        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = torch.argmax(output, dim=1).item()

        score = output[:, class_idx]
        score.backward()

        gradients = self.gradients[0]      # [C, H, W]
        activations = self.activations[0]  # [C, H, W]

        weights = gradients.mean(dim=(1, 2))  # [C]

        cam = torch.zeros(activations.shape[1:], dtype=torch.float32).to(input_tensor.device)

        for i, w in enumerate(weights):
            cam += w * activations[i]

        cam = torch.relu(cam)
        cam = cam.cpu().numpy()

        if cam.max() > 0:
            cam = cam / cam.max()

        return cam, class_idx


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(device=None):
    if device is None:
        device = get_device()

    checkpoint_path = CHECKPOINT_DIR / "best_disease_classifier.pth"

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}. Please train the model first."
        )

    model = PaddyDiseaseClassifier(pretrained=False).to(device)
    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    return model


def preprocess_pil_image(pil_image: Image.Image, device):
    pil_image = pil_image.convert("RGB")

    preprocess = T.Compose([
        T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]),
    ])

    input_tensor = preprocess(pil_image).unsqueeze(0).to(device)
    return input_tensor


def overlay_heatmap_on_image(
    original_image: Image.Image,
    cam: np.ndarray,
    alpha: float = 0.4
) -> np.ndarray:
    original_np = np.array(original_image.convert("RGB"))
    original_np = cv2.resize(original_np, (IMAGE_SIZE, IMAGE_SIZE))

    heatmap = cv2.resize(cam, (IMAGE_SIZE, IMAGE_SIZE))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(original_np, 1 - alpha, heatmap, alpha, 0)
    return overlay


def generate_gradcam(pil_image: Image.Image) -> Tuple[np.ndarray, str, float]:
    device = get_device()
    model = load_model(device=device)

    input_tensor = preprocess_pil_image(pil_image, device=device)

    with torch.enable_grad():
        target_layer = model.encoder.feature_extractor[-1]
        gradcam = GradCAM(model, target_layer)

        logits = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)
        predicted_idx = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0, predicted_idx].item()

        cam, class_idx = gradcam.generate(input_tensor, class_idx=predicted_idx)
        gradcam.remove_hooks()

    overlay = overlay_heatmap_on_image(pil_image, cam)
    predicted_class = IDX_TO_CLASS[class_idx]

    return overlay, predicted_class, confidence