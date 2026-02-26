"""
core/inference.py — Model loading and inference pipeline.

Provides:
    CLASS_NAMES       — dynamically loaded from checkpoints/class_names.json
    INFERENCE_TRANSFORM — shared transform (same as training val pipeline)
    load_model(name)  — cached model loader; safe for multi-user Streamlit
    run_inference(model, pil_image) → (pred_idx, confidence_pct, top3)
"""

from __future__ import annotations
import json
import os
import time
import logging

import functools
import torch
import torch.nn.functional as F
import timm
import torchvision.transforms as T

# ── Simple lru_cache-based model cache (works in FastAPI & Streamlit) ──────────
_MODEL_CACHE: dict = {}

logger = logging.getLogger(__name__)

# ── Fallback 38-class PlantVillage list ───────────────────────────────────────
_FALLBACK_38 = [
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

_CLASS_NAMES_PATH = os.path.join("checkpoints", "class_names.json")


def load_class_names() -> list[str]:
    """Load class names from checkpoints/class_names.json, fall back to 38-class list."""
    if os.path.isfile(_CLASS_NAMES_PATH):
        try:
            with open(_CLASS_NAMES_PATH, encoding="utf-8") as f:
                names = json.load(f)
            if isinstance(names, list) and len(names) >= 2:
                logger.info("Loaded %d class names from %s", len(names), _CLASS_NAMES_PATH)
                return names
        except Exception as exc:
            logger.warning("Could not read class_names.json: %s — using fallback", exc)
    return _FALLBACK_38


# Module-level class names — loaded once at import time
CLASS_NAMES: list[str] = load_class_names()

# ── Inference transform — single source of truth ──────────────────────────────
try:
    from data.transforms import get_inference_transforms
    INFERENCE_TRANSFORM = get_inference_transforms(img_size=224)
except Exception:
    INFERENCE_TRANSFORM = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

# ── Model loading — cached per model name ────────────────────────────────────
def load_model(model_name: str):
    """
    Load a trained model from checkpoints/best_model_{model_name}.pth.
    Returns (model, error_msg). model is None if loading fails.
    Results are cached in _MODEL_CACHE so the model loads only once.
    Error is returned as a string (not raised) to avoid cache poisoning.
    """
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]
    model_path = f"checkpoints/best_model_{model_name}.pth"
    num_classes = len(CLASS_NAMES)

    if not os.path.isfile(model_path):
        return None, f"Checkpoint not found: `{model_path}`"

    try:
        arch_map = {
            "vit":  "vit_base_patch16_224",
            "swin": "swin_base_patch4_window7_224",
        }
        arch = arch_map.get(model_name, model_name)
        model = timm.create_model(arch, pretrained=False, num_classes=num_classes)
        state = torch.load(model_path, map_location="cpu", weights_only=True)
        model.load_state_dict(state)
        model.eval()
        logger.info("Loaded %s (%d classes) from %s", arch, num_classes, model_path)
        _MODEL_CACHE[model_name] = (model, None)
        return model, None
    except Exception as exc:
        logger.error("Failed to load model %s: %s", model_name, exc, exc_info=True)
        _MODEL_CACHE[model_name] = (None, str(exc))
        return None, str(exc)


def run_inference(model, pil_image) -> tuple[int, float, list[tuple[str, float]]]:
    """
    Run forward pass on a PIL image.

    Returns:
        pred_idx    — integer index of top-1 class
        confidence  — float 0–100
        top3        — list of (class_name, probability) for top 3 predictions
    """
    tensor = INFERENCE_TRANSFORM(pil_image).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor)
        probs  = F.softmax(logits, dim=1)
        top3_p, top3_i = torch.topk(probs, min(3, len(CLASS_NAMES)), dim=1)

    pred_idx   = top3_i[0][0].item()
    confidence = top3_p[0][0].item() * 100.0
    top3 = [
        (CLASS_NAMES[top3_i[0][j].item()], float(top3_p[0][j]))
        for j in range(top3_p.shape[1])
    ]
    return pred_idx, confidence, top3
