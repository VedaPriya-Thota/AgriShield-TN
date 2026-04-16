import torch
import torch.nn as nn
from torchvision import models


class ImageEncoder(nn.Module):
    """
    Image feature extractor using a pretrained ResNet18 backbone.
    Output: feature vector of size 512
    """

    def __init__(self, pretrained: bool = True):
        super().__init__()

        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        backbone = models.resnet18(weights=weights)

        # Remove final classification layer
        self.feature_extractor = nn.Sequential(*list(backbone.children())[:-1])
        self.output_dim = backbone.fc.in_features  # 512 for resnet18

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.feature_extractor(x)   # [B, 512, 1, 1]
        features = torch.flatten(features, 1)  # [B, 512]
        return features