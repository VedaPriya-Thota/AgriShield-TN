"""
PaddyMetadataDataset
====================
Extends PaddyImageDataset with two metadata tensors:
  - variety_idx  : LongTensor  [B]  categorical variety label
  - age_norm     : FloatTensor [B]  z-score normalised plant age in days

Age normalisation statistics are computed from the training split and can be
passed in explicitly so that validation / test splits use the same transform
(no leakage).

Return signature per sample
───────────────────────────
  (image, variety_idx, age_norm, label, metadata_dict)
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import pandas as pd
import torch

from src.config.config import (
    TRAIN_CSV,
    TRAIN_IMAGE_DIR,
    VARIETY_COL,
    AGE_COL,
)
from src.datasets.image_dataset import PaddyImageDataset


class PaddyMetadataDataset(PaddyImageDataset):
    """
    Inherits all image-loading, path-resolution and CSV validation from
    PaddyImageDataset and adds encoded metadata tensors.

    Parameters
    ----------
    csv_path    : path to train.csv
    image_dir   : root directory of training images
    transform   : albumentations transform (or None)
    age_mean    : pre-computed age mean (pass from train split to val/test)
    age_std     : pre-computed age std  (pass from train split to val/test)
    """

    def __init__(
        self,
        csv_path=TRAIN_CSV,
        image_dir=TRAIN_IMAGE_DIR,
        transform=None,
        age_mean: Optional[float] = None,
        age_std: Optional[float] = None,
    ):
        super().__init__(csv_path=csv_path, image_dir=image_dir, transform=transform)

        # ── Variety vocabulary ────────────────────────────────────────────────
        self.data[VARIETY_COL] = (
            self.data[VARIETY_COL].fillna("unknown").astype(str).str.strip()
        )
        unique_varieties = sorted(self.data[VARIETY_COL].unique().tolist())
        self.variety_to_idx: Dict[str, int] = {
            v: i for i, v in enumerate(unique_varieties)
        }
        self.idx_to_variety: Dict[int, str] = {
            i: v for v, i in self.variety_to_idx.items()
        }

        # ── Age normalisation statistics ──────────────────────────────────────
        # Callers should pass training-split stats to val/test datasets so that
        # the same transform is applied consistently (prevents leakage).
        raw_ages = self.data[AGE_COL].fillna(0.0).astype(float)
        self.age_mean: float = float(age_mean) if age_mean is not None else float(raw_ages.mean())
        computed_std = float(raw_ages.std()) if age_std is None else float(age_std)
        self.age_std: float = computed_std if computed_std > 1e-6 else 1.0

    # ── Public properties ──────────────────────────────────────────────────────

    @property
    def num_varieties(self) -> int:
        """Number of unique variety tokens in the vocabulary."""
        return len(self.variety_to_idx)

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _normalize_age(self, age: float) -> float:
        """Z-score normalise a raw age value using stored statistics."""
        return (age - self.age_mean) / self.age_std

    def _variety_idx(self, variety_str: str) -> int:
        """Return the integer index for a variety string (fallback: 0)."""
        return self.variety_to_idx.get(variety_str, 0)

    # ── Dataset protocol ───────────────────────────────────────────────────────

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, dict]:
        """
        Returns
        -------
        image        : FloatTensor [3, H, W]
        variety_idx  : LongTensor  []   – variety category index
        age_norm     : FloatTensor []   – z-score normalised age
        label        : LongTensor  []   – disease class index
        metadata     : dict             – auxiliary info (id, path, raw values…)
        """
        image, label_tensor, base_meta = super().__getitem__(idx)

        variety_str = base_meta["variety"]
        v_idx = self._variety_idx(variety_str)
        age_norm = self._normalize_age(base_meta["age"])

        # Enrich metadata dict with encoded values for downstream inspection
        base_meta["variety_idx"] = v_idx
        base_meta["age_normalized"] = age_norm

        return (
            image,
            torch.tensor(v_idx,    dtype=torch.long),
            torch.tensor(age_norm, dtype=torch.float32),
            label_tensor,
            base_meta,
        )
