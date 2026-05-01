# disease_classifier.py — Image-only paddy disease classifier.
#
# Architecture:
#   ResNet-18 backbone (image_encoder.py)  →  512-dim features
#   Linear(512 → 256) + ReLU + Dropout(0.3)
#   Linear(256 → 10)  →  logits (one per disease class)
#
# This is the model that gets saved to checkpoints/best_disease_classifier.pth
# and used by the Streamlit UI (2_Analyze_Leaf.py).
# The metadata fusion model (metadata_classifier.py) is a separate variant.

import torch
import torch.nn as nn

from src.config.config import NUM_CLASSES
from src.models.image_encoder import ImageEncoder


class PaddyDiseaseClassifier(nn.Module):
    """
    Image-only disease classifier for paddy disease detection.
    """

    def __init__(self, num_classes: int = NUM_CLASSES, pretrained: bool = True):
        super().__init__()

        # ResNet-18 backbone that outputs a 512-dim feature vector per image
        self.encoder = ImageEncoder(pretrained=pretrained)

        # Two-layer MLP classifier head on top of the image features.
        # Dropout(0.3) helps prevent overfitting on the 10k training set.
        self.classifier = nn.Sequential(
            nn.Linear(self.encoder.output_dim, 256),  # compress 512 → 256
            nn.ReLU(inplace=True),                    # non-linearity
            nn.Dropout(p=0.3),                        # regularisation
            nn.Linear(256, num_classes)               # 256 → 10 raw logits
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Extract visual features from the image
        features = self.encoder(x)        # [B, 512]
        # Project features to class scores (logits, not probabilities)
        logits = self.classifier(features) # [B, 10]
        return logits
        # Note: softmax is NOT applied here — CrossEntropyLoss does it internally
