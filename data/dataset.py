"""
data/dataset.py — PlantVillage ImageFolder-based dataset loader.

Supports both the standard PlantVillage structure:
    dataset/
        Apple___Apple_scab/
        Apple___Black_rot/
        ...

AND a pre-split structure (train/val/test sub-dirs), auto-detected at runtime.

All class discovery is dynamic — no hardcoded class list.
"""

import os
import json
from pathlib import Path
from typing import Tuple, Optional, List

import torch
from torch.utils.data import DataLoader, random_split, Subset, Dataset
from torchvision import datasets

from .transforms import get_train_transforms, get_val_transforms


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_presplit(data_dir: str) -> bool:
    """Return True if data_dir already has train/val (or train/test) sub-dirs."""
    required = {"train"}
    any_val  = {"val", "valid", "validation", "test"}
    subs     = {d.name.lower() for d in os.scandir(data_dir) if d.is_dir()}
    return bool(required & subs) and bool(any_val & subs)


def _find_classes(data_dir: str) -> List[str]:
    """
    Discover class names (sub-folder names) from data_dir.
    Works for both flat and pre-split structures.
    Returns sorted list of class names.
    """
    root = Path(data_dir)
    if _is_presplit(data_dir):
        # Use 'train' sub-dir to discover classes
        root = next((root / sub for sub in ["train", "Train", "TRAIN"] if (root / sub).exists()), root)

    classes = sorted([d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")])
    if not classes:
        raise FileNotFoundError(
            f"No class sub-folders found in '{root}'. "
            "Expected PlantVillage folder structure: dataset/<ClassName>/<image.jpg>"
        )
    return classes


def _save_class_index(classes: List[str], data_dir: str) -> None:
    """Persist class-to-index mapping for reproducibility across train/infer."""
    mapping = {cls: idx for idx, cls in enumerate(classes)}
    out_path = os.path.join(data_dir, "class_index.json")
    with open(out_path, "w") as f:
        json.dump(mapping, f, indent=2)


def load_class_index(data_dir: str) -> Optional[dict]:
    """Load saved class-to-index mapping if it exists."""
    path = os.path.join(data_dir, "class_index.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


# ── Main dataset builder ──────────────────────────────────────────────────────

def get_datasets(
    data_dir: str,
    split_ratios: Tuple[float, float, float] = (0.80, 0.10, 0.10),
    img_size: int = 224,
    seed: int = 42,
):
    """
    Load the PlantVillage dataset from data_dir.

    • Auto-detects flat vs. pre-split directory structure.
    • Dynamically discovers all class folders (no hardcoded class list).
    • Saves class_index.json for reproducible inference.
    • Returns (train_dataset, val_dataset, test_dataset, class_names).
    """
    data_dir = os.path.abspath(data_dir)

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(
            f"Dataset directory not found: '{data_dir}'\n"
            "Run: python download_data.py"
        )

    train_tfm = get_train_transforms(img_size=img_size)
    val_tfm   = get_val_transforms(img_size=img_size)

    # ── Case 1: Pre-split directories ────────────────────────────────────────
    if _is_presplit(data_dir):
        _train_root = _find_split_dir(data_dir, ["train", "Train", "TRAIN"])
        _val_root   = _find_split_dir(data_dir, ["val", "valid", "validation", "Val"])
        _test_root  = _find_split_dir(data_dir, ["test", "Test", "TEST"])

        train_ds = datasets.ImageFolder(_train_root, transform=train_tfm)
        val_ds   = datasets.ImageFolder(_val_root,   transform=val_tfm)
        if _test_root:
            test_ds = datasets.ImageFolder(_test_root, transform=val_tfm)
        else:
            # No test dir — borrow 50 % of val
            half = len(val_ds) // 2
            val_ds, test_ds = random_split(
                val_ds, [len(val_ds) - half, half],
                generator=torch.Generator().manual_seed(seed)
            )

        class_names = train_ds.classes

    # ── Case 2: Flat directory — split randomly ───────────────────────────────
    else:
        full_ds = datasets.ImageFolder(data_dir)   # no transform yet
        class_names = full_ds.classes

        n = len(full_ds)
        n_train = int(split_ratios[0] * n)
        n_val   = int(split_ratios[1] * n)
        n_test  = n - n_train - n_val

        gen = torch.Generator().manual_seed(seed)
        train_idx, val_idx, test_idx = random_split(
            range(n), [n_train, n_val, n_test], generator=gen
        )

        train_ds = _SubsetWithTransform(full_ds, list(train_idx), train_tfm)
        val_ds   = _SubsetWithTransform(full_ds, list(val_idx),   val_tfm)
        test_ds  = _SubsetWithTransform(full_ds, list(test_idx),  val_tfm)

    # Persist class index
    _save_class_index(class_names, data_dir)

    print(f"✅ Dataset loaded  | classes: {len(class_names)} | "
          f"train: {len(train_ds):,}  val: {len(val_ds):,}  test: {len(test_ds):,}")

    return train_ds, val_ds, test_ds, class_names


def get_dataloaders(
    data_dir: str,
    batch_size: int = 32,
    num_workers: int = 2,
    img_size: int = 224,
    pin_memory: bool = True,
):
    """
    Convenience wrapper — returns (train_loader, val_loader, test_loader, class_names).
    """
    train_ds, val_ds, test_ds, class_names = get_datasets(data_dir, img_size=img_size)

    _kw = dict(num_workers=num_workers, pin_memory=pin_memory, persistent_workers=num_workers > 0)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  **_kw)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, **_kw)
    test_loader  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False, **_kw)

    return train_loader, val_loader, test_loader, class_names


# ── Internal utilities ────────────────────────────────────────────────────────

def _find_split_dir(data_dir: str, candidates: List[str]) -> Optional[str]:
    for name in candidates:
        path = os.path.join(data_dir, name)
        if os.path.isdir(path):
            return path
    return None


class _SubsetWithTransform(Dataset):
    """Wraps an ImageFolder subsets and applies a specific transform."""

    def __init__(self, dataset: datasets.ImageFolder, indices: List[int], transform=None):
        self.dataset   = dataset
        self.indices   = indices
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        img, label = self.dataset[self.indices[idx]]
        if self.transform:
            # img is a PIL image from ImageFolder when no transform is set
            img = self.transform(img)
        return img, label
