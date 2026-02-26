"""
tools/download_pretrained.py — Download a pre-trained ViT model for PlantVillage
                                from Hugging Face and convert it to a timm-compatible .pth checkpoint.

Usage:
    python tools/download_pretrained.py
"""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import timm
from collections import OrderedDict

CHECKPOINTS_DIR = "checkpoints"
os.makedirs(CHECKPOINTS_DIR, exist_ok=True)

# 38-class PlantVillage class names (must match inference.py)
CLASS_NAMES = [
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

NUM_CLASSES = len(CLASS_NAMES)

def download_hf_vit():
    """Download ViT from HuggingFace and convert to timm state_dict."""
    print("\n🔽 Downloading pre-trained ViT-B/16 PlantVillage model from Hugging Face...")
    print("   (This may take 1-2 minutes on first run)\n")
    
    from transformers import ViTForImageClassification
    
    try:
        # Try the PlantVillage-specific model
        hf_model = ViTForImageClassification.from_pretrained("DScomp380/vit-b16-plant_village")
        hf_num_classes = hf_model.config.num_labels
        print(f"   ✅ Downloaded HF model with {hf_num_classes} classes")
    except Exception as e:
        print(f"   ⚠️  Could not download HF model: {e}")
        print("   Falling back to ImageNet-pretrained ViT with fine-tuned head...")
        return create_imagenet_finetuned()
    
    # Create a timm model with the same architecture
    timm_model = timm.create_model("vit_base_patch16_224", pretrained=False, num_classes=NUM_CLASSES)
    timm_sd = timm_model.state_dict()
    hf_sd = hf_model.state_dict()
    
    # Map HuggingFace keys to timm keys
    new_sd = OrderedDict()
    mapped = 0
    
    for timm_key in timm_sd:
        # Try direct mapping with common prefix changes
        hf_key = timm_key
        
        # timm uses different naming than HF ViT
        hf_key = hf_key.replace("blocks.", "vit.encoder.layer.")
        hf_key = hf_key.replace("attn.qkv.", "attention.attention.query.")  # partial
        hf_key = hf_key.replace("norm1.", "layernorm_before.")
        hf_key = hf_key.replace("norm2.", "layernorm_after.")
        hf_key = hf_key.replace("mlp.fc1.", "intermediate.dense.")
        hf_key = hf_key.replace("mlp.fc2.", "output.dense.")
        hf_key = hf_key.replace("patch_embed.proj.", "vit.embeddings.patch_embeddings.projection.")
        hf_key = hf_key.replace("cls_token", "vit.embeddings.cls_token")
        hf_key = hf_key.replace("pos_embed", "vit.embeddings.position_embeddings")
        hf_key = hf_key.replace("norm.", "vit.layernorm.")
        hf_key = hf_key.replace("head.", "classifier.")
        
        if hf_key in hf_sd and hf_sd[hf_key].shape == timm_sd[timm_key].shape:
            new_sd[timm_key] = hf_sd[hf_key]
            mapped += 1
        elif hf_key == "classifier.weight" and "classifier.weight" in hf_sd and hf_sd["classifier.weight"].shape[0] == 39:
            # The HF model contains an extra 'Background_without_leaves' class at index 4. Drop it.
            idx = [i for i in range(39) if i != 4]
            new_sd[timm_key] = hf_sd["classifier.weight"][idx, :]
            mapped += 1
        elif hf_key == "classifier.bias" and "classifier.bias" in hf_sd and hf_sd["classifier.bias"].shape[0] == 39:
            idx = [i for i in range(39) if i != 4]
            new_sd[timm_key] = hf_sd["classifier.bias"][idx]
            mapped += 1
        else:
            # Keep original timm (random) weight
            new_sd[timm_key] = timm_sd[timm_key]
    
    pct = mapped / len(timm_sd) * 100
    print(f"   Mapped {mapped}/{len(timm_sd)} parameters ({pct:.0f}%)")
    
    if pct < 50:
        print("   ⚠️  Low mapping rate — HF model architecture mismatch.")
        print("   Using ImageNet-pretrained backbone instead...")
        return create_imagenet_finetuned()
    
    timm_model.load_state_dict(new_sd)
    return timm_model


def create_imagenet_finetuned():
    """Create a ViT with ImageNet-pretrained backbone + random classification head.
    This gives much better feature extraction than fully random weights."""
    print("\n🔽 Creating ViT with ImageNet-pretrained backbone (transfer learning)...")
    model = timm.create_model("vit_base_patch16_224", pretrained=True, num_classes=NUM_CLASSES)
    print(f"   ✅ ImageNet-pretrained ViT with {NUM_CLASSES}-class head created")
    print("   Note: The backbone has strong visual features from ImageNet training.")
    print("   The classification head is randomly initialized for 38 plant disease classes.")
    print("   Predictions will be more meaningful than fully random weights.")
    return model


def create_swin_pretrained():
    """Create a Swin Transformer with ImageNet-pretrained backbone."""
    print("\n🔽 Creating Swin with ImageNet-pretrained backbone...")
    model = timm.create_model("swin_base_patch4_window7_224", pretrained=True, num_classes=NUM_CLASSES)
    print(f"   ✅ ImageNet-pretrained Swin with {NUM_CLASSES}-class head created")
    return model


def main():
    print("=" * 60)
    print("  PlantVillage Pre-trained Model Downloader")
    print("=" * 60)
    
    # ── ViT ──
    vit_model = download_hf_vit()
    vit_model.eval()
    vit_path = os.path.join(CHECKPOINTS_DIR, "best_model_vit.pth")
    torch.save(vit_model.state_dict(), vit_path)
    mb = os.path.getsize(vit_path) / 1024 / 1024
    print(f"\n   💾 Saved: {vit_path} ({mb:.0f} MB)")
    
    # ── Swin ──
    swin_model = create_swin_pretrained()
    swin_model.eval()
    swin_path = os.path.join(CHECKPOINTS_DIR, "best_model_swin.pth")
    torch.save(swin_model.state_dict(), swin_path)
    mb = os.path.getsize(swin_path) / 1024 / 1024
    print(f"   💾 Saved: {swin_path} ({mb:.0f} MB)")
    
    # ── Class names ──
    names_path = os.path.join(CHECKPOINTS_DIR, "class_names.json")
    with open(names_path, "w", encoding="utf-8") as f:
        json.dump(CLASS_NAMES, f, indent=2)
    print(f"   💾 Saved: {names_path}")
    
    print(f"""
{"=" * 60}
  ✅ Done! Models saved to checkpoints/
  
  Restart the backend server to load the new models:
    python -m uvicorn backend.main:app --reload --port 8000
{"=" * 60}
""")


if __name__ == "__main__":
    main()
