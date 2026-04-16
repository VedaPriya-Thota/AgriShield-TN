import torch
import torch.nn as nn


class MetadataEncoder(nn.Module):
    """
    Encodes:
    - variety (categorical embedding)
    - age (numerical scalar)
    """

    def __init__(self, num_varieties: int, variety_embed_dim: int = 16):
        super().__init__()

        self.variety_embedding = nn.Embedding(num_embeddings=num_varieties, embedding_dim=variety_embed_dim)

        self.age_mlp = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 16),
            nn.ReLU(inplace=True),
        )

        self.output_dim = variety_embed_dim + 16

    def forward(self, variety_idx: torch.Tensor, age: torch.Tensor) -> torch.Tensor:
        variety_features = self.variety_embedding(variety_idx)   # [B, embed_dim]

        age = age.unsqueeze(1)  # [B] -> [B, 1]
        age_features = self.age_mlp(age)  # [B, 16]

        features = torch.cat([variety_features, age_features], dim=1)
        return features