"""
models/__init__.py
Exposes get_vit_model and get_swin_model for use in train.py and evaluate.py.
"""
import timm


def get_vit_model(num_classes: int = 38, pretrained: bool = True):
    """Return a ViT-Base/16 model configured for num_classes."""
    try:
        model = timm.create_model(
            "vit_base_patch16_224",
            pretrained=pretrained,
            num_classes=num_classes,
        )
        return model
    except Exception as e:
        print(f"[ERROR] Could not create ViT model: {e}")
        return None


def get_swin_model(num_classes: int = 38, pretrained: bool = True):
    """Return a Swin-Base model configured for num_classes."""
    try:
        model = timm.create_model(
            "swin_base_patch4_window7_224",
            pretrained=pretrained,
            num_classes=num_classes,
        )
        return model
    except Exception as e:
        print(f"[ERROR] Could not create Swin model: {e}")
        return None
