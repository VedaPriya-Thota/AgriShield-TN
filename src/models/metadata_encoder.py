"""
MetadataEncoder
===============
Encodes two metadata fields into a fixed-size feature vector:

  variety (categorical)
      Embedding  →  LayerNorm
      [B] → [B, variety_embed_dim]

  age (numerical, pre-normalised to ~N(0,1))
      Linear → ReLU → Dropout → Linear → ReLU
      [B] → [B, age_embed_dim]

  concatenate → [B, variety_embed_dim + age_embed_dim]

The LayerNorm on the variety embedding stabilises training when the
embedding table is small.  Dropout in the age MLP prevents the network
from over-fitting to age alone on small datasets.
"""

import torch
import torch.nn as nn


class MetadataEncoder(nn.Module):

    def __init__(
        self,
        num_varieties: int,
        variety_embed_dim: int = 16,
        age_embed_dim: int = 16,
        dropout: float = 0.2,
    ):
        """
        Parameters
        ----------
        num_varieties     : vocabulary size (number of unique variety tokens)
        variety_embed_dim : output dimension of the variety embedding
        age_embed_dim     : output dimension of the age MLP
        dropout           : dropout rate applied inside the age MLP
        """
        super().__init__()

        # ── Variety branch ────────────────────────────────────────────────────
        self.variety_embedding = nn.Embedding(
            num_embeddings=num_varieties,
            embedding_dim=variety_embed_dim,
        )
        # LayerNorm smooths the embedding space; helpful when num_varieties is
        # small and embeddings are randomly initialised.
        self.variety_norm = nn.LayerNorm(variety_embed_dim)

        # ── Age branch ────────────────────────────────────────────────────────
        # Two-layer MLP: input → 2× hidden → hidden
        hidden = age_embed_dim * 2
        self.age_mlp = nn.Sequential(
            nn.Linear(1, hidden),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(hidden, age_embed_dim),
            nn.ReLU(inplace=True),
        )

        self.output_dim: int = variety_embed_dim + age_embed_dim

    def forward(self, variety_idx: torch.Tensor, age: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        variety_idx : LongTensor  [B]   – variety class indices
        age         : FloatTensor [B]   – z-score normalised age values

        Returns
        -------
        features    : FloatTensor [B, output_dim]
        """
        v_feat = self.variety_norm(self.variety_embedding(variety_idx))  # [B, V]
        a_feat = self.age_mlp(age.unsqueeze(1))                          # [B, A]
        return torch.cat([v_feat, a_feat], dim=1)                        # [B, V+A]
