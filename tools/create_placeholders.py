"""
tools/create_placeholders.py — Create zero-weight model checkpoints for smoke testing.

Creates:
    checkpoints/best_model_vit.pth
    checkpoints/best_model_swin.pth
    checkpoints/class_names.json

These placeholders let you run the app (with random predictions) before real
training. Replace them with `python train.py` output for accurate predictions.

Usage:
    python tools/create_placeholders.py
    python tools/create_placeholders.py --classes 38   # use 38-class fallback
"""

from __future__ import annotations
import argparse
import json
import os
import sys

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import timm

CHECKPOINTS_DIR = "checkpoints"

FALLBACK_38 = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust",
    "Apple___healthy", "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn_(maize)___Common_rust_", "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy", "Grape___Black_rot", "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Raspberry___healthy", "Soybean___healthy", "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites_Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

MODELS = {
    "vit":  "vit_base_patch16_224",
    "swin": "swin_base_patch4_window7_224",
}


def create_placeholder(name: str, arch: str, num_classes: int) -> str:
    path = os.path.join(CHECKPOINTS_DIR, f"best_model_{name}.pth")
    model = timm.create_model(arch, pretrained=False, num_classes=num_classes)
    torch.save(model.state_dict(), path)
    mb = os.path.getsize(path) / 1024 / 1024
    print(f"  ✅ {path}  ({mb:.1f} MB)")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create placeholder model checkpoints")
    parser.add_argument("--classes", type=int, default=len(FALLBACK_38),
                        help="Number of output classes")
    args = parser.parse_args()

    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    num_classes = args.classes
    class_names = FALLBACK_38[:num_classes] if num_classes <= len(FALLBACK_38) else FALLBACK_38

    print(f"\nCreating placeholder checkpoints ({num_classes} classes) …\n")
    for name, arch in MODELS.items():
        create_placeholder(name, arch, num_classes)

    # Save class names JSON
    names_path = os.path.join(CHECKPOINTS_DIR, "class_names.json")
    with open(names_path, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    print(f"  ✅ {names_path}")

    print(f"""
⚠️  These are PLACEHOLDER models with RANDOM weights.
    Predictions will be meaningless until you train real models:

    python train.py --model vit --data_dir dataset --epochs 30
""")


if __name__ == "__main__":
    main()
