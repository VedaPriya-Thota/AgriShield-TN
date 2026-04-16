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

        self.encoder = ImageEncoder(pretrained=pretrained)

        self.classifier = nn.Sequential(
            nn.Linear(self.encoder.output_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.encoder(x)
        logits = self.classifier(features)
        return logits