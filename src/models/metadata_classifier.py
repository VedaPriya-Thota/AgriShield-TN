"""
PaddyMetadataClassifier
=======================
Fuses image features (ResNet-18 backbone, 512-dim) with metadata features
(variety embedding + age MLP, 32-dim) and classifies into disease categories.

Fusion pipeline
───────────────
  image        → ImageEncoder   → [B, 512]
  variety_idx  ┐
               ├─ MetadataEncoder → [B, 32]
  age          ┘
                  concatenate   → [B, 544]
                  BatchNorm1d
                  Linear(256) → ReLU → Dropout
                  Linear(128) → ReLU → Dropout
                  Linear(num_classes)           → logits

BatchNorm1d on the concatenated vector normalises the scale difference
between the 512-dim image features and the 32-dim metadata features,
preventing one branch from dominating the gradient signal.

NOTE: This model is fully trained but not yet wired into the Streamlit UI.
      The UI currently uses PaddyDiseaseClassifier (image-only).
"""

import torch
import torch.nn as nn

from src.config.config import NUM_CLASSES
from src.models.image_encoder import ImageEncoder
from src.models.metadata_encoder import MetadataEncoder


class PaddyMetadataClassifier(nn.Module):

    def __init__(
        self,
        num_varieties: int,
        num_classes: int = NUM_CLASSES,
        pretrained: bool = True,
        variety_embed_dim: int = 16,
        age_embed_dim: int = 16,
        dropout: float = 0.3,
    ):
        """
        Parameters
        ----------
        num_varieties     : vocabulary size from PaddyMetadataDataset.num_varieties
        num_classes       : number of disease output classes (default: 10)
        pretrained        : use ImageNet weights for the ResNet-18 backbone
        variety_embed_dim : dimension of the variety embedding vector
        age_embed_dim     : dimension of the age MLP output vector
        dropout           : dropout rate for the fusion classifier head
        """
        super().__init__()

        # Two separate encoders — one per modality
        self.image_encoder = ImageEncoder(pretrained=pretrained)
        self.metadata_encoder = MetadataEncoder(
            num_varieties=num_varieties,
            variety_embed_dim=variety_embed_dim,
            age_embed_dim=age_embed_dim,
            dropout=dropout * 0.67,   # slightly lower dropout inside the encoder
        )

        # Combined feature dimension: 512 (image) + 32 (metadata) = 544
        fusion_dim = self.image_encoder.output_dim + self.metadata_encoder.output_dim

        self.classifier = nn.Sequential(
            # BatchNorm bridges the scale gap between the two feature branches.
            # Without this, the 512-dim image features would dominate the 32-dim metadata.
            nn.BatchNorm1d(fusion_dim),
            nn.Linear(fusion_dim, 256),         # compress fused 544-dim → 256
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(256, 128),                # further compress 256 → 128
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout * 0.5),        # less dropout in deeper layers
            nn.Linear(128, num_classes),         # final projection to 10 disease classes
        )

    def forward(
        self,
        image: torch.Tensor,
        variety_idx: torch.Tensor,
        age: torch.Tensor,
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        image       : FloatTensor [B, 3, H, W]
        variety_idx : LongTensor  [B]
        age         : FloatTensor [B]  (z-score normalised)

        Returns
        -------
        logits      : FloatTensor [B, num_classes]
        """
        img_feat  = self.image_encoder(image)                # [B, 512] — visual features
        meta_feat = self.metadata_encoder(variety_idx, age)  # [B, 32]  — variety + age
        fused     = torch.cat([img_feat, meta_feat], dim=1)  # [B, 544] — combined
        return self.classifier(fused)                         # [B, 10]  — logits
