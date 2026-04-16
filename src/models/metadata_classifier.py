import torch
import torch.nn as nn

from src.config.config import NUM_CLASSES
from src.models.image_encoder import ImageEncoder
from src.models.metadata_encoder import MetadataEncoder


class PaddyMetadataClassifier(nn.Module):
    """
    Image + metadata disease classifier.
    """

    def __init__(self, num_varieties: int, num_classes: int = NUM_CLASSES, pretrained: bool = True):
        super().__init__()

        self.image_encoder = ImageEncoder(pretrained=pretrained)
        self.metadata_encoder = MetadataEncoder(num_varieties=num_varieties)

        fusion_dim = self.image_encoder.output_dim + self.metadata_encoder.output_dim

        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, image: torch.Tensor, variety_idx: torch.Tensor, age: torch.Tensor) -> torch.Tensor:
        image_features = self.image_encoder(image)
        metadata_features = self.metadata_encoder(variety_idx, age)

        fused_features = torch.cat([image_features, metadata_features], dim=1)
        logits = self.classifier(fused_features)

        return logits