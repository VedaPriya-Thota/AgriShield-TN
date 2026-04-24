# image_encoder.py — ResNet-18 feature extractor backbone.
#
# Loads a pretrained ResNet-18, removes its final classification layer,
# and returns a 512-dimensional feature vector for each input image.
# This vector is then passed to the classifier head (disease_classifier.py)
# or fused with metadata features (metadata_classifier.py).

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

        # Load ResNet-18 with ImageNet weights (pretrained=True) or random weights
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        backbone = models.resnet18(weights=weights)

        # Strip the final fully-connected classification layer (fc: 512 → 1000).
        # We keep everything up to (but not including) that layer as our feature extractor.
        # children()[-1] is the fc layer; children()[:-1] gives us all earlier layers.
        self.feature_extractor = nn.Sequential(*list(backbone.children())[:-1])

        # Record the output size (512 for ResNet-18) for downstream modules to use
        self.output_dim = backbone.fc.in_features  # 512

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.feature_extractor(x)   # [B, 512, 1, 1] — spatial dims collapsed by AvgPool
        features = torch.flatten(features, 1)  # [B, 512] — flatten to a flat feature vector
        return features
