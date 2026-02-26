"""
utils/gradcam.py — Grad-CAM heatmap for Vision Transformer models

Highlights which regions of the leaf image influenced the model's prediction.
Uses pytorch-grad-cam library (pip install grad-cam).
Gracefully degrades if not installed.
"""
from utils.logging_config import get_logger

logger = get_logger(__name__)


def generate_gradcam(model, pil_image, target_class: int):
    """
    Generate a Grad-CAM heatmap overlay on the input PIL image.

    Args:
        model:         PyTorch model (ViT or Swin)
        pil_image:     PIL Image (RGB)
        target_class:  int — the class index to explain (top-1 prediction)

    Returns:
        PIL Image with heatmap overlay, or None if grad-cam is unavailable
    """
    try:
        import numpy as np
        import cv2
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image
        import torchvision.transforms as T
        import torch

        # Resize to 224×224 and normalise (must match inference transform)
        transform = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        input_tensor = transform(pil_image).unsqueeze(0)

        # ── Pick the last attention/conv layer for each architecture ──────────
        if hasattr(model, "blocks"):         # ViT
            target_layers = [model.blocks[-1].norm1]
        elif hasattr(model, "layers"):       # Swin
            target_layers = [model.layers[-1].blocks[-1].norm1]
        else:
            logger.warning("GradCAM: unknown model architecture — using default")
            target_layers = [list(model.modules())[-3]]

        with GradCAM(model=model, target_layers=target_layers) as cam:
            from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
            targets = [ClassifierOutputTarget(target_class)]
            grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0]

        # ── Overlay on original image ─────────────────────────────────────────
        img_224 = pil_image.resize((224, 224))
        img_np  = np.array(img_224).astype(np.float32) / 255.0
        visualisation = show_cam_on_image(img_np, grayscale_cam, use_rgb=True)

        from PIL import Image
        return Image.fromarray(visualisation)

    except ImportError:
        logger.info("GradCAM skipped — pytorch-grad-cam not installed (pip install grad-cam)")
        return None
    except Exception as e:
        logger.error(f"GradCAM failed: {e}", exc_info=True)
        return None
