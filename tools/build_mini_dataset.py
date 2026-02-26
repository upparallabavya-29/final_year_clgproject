"""
tools/build_mini_dataset.py — Build a small (~190 image) training dataset for all 38 PlantVillage classes.

Combines:
  1. Existing images from dataset/ (partial classes)
  2. Test images from test_images/ (one per class)
  3. Augmented copies (flip, rotate, color jitter) to fill gaps

Target: ~5 images per class × 38 classes ≈ 190 images
"""

import os
import shutil
import random
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path

# Class names → test image filename mapping
TEST_IMAGE_MAP = {
    "Apple___Apple_scab": "Apple_scab.JPG",
    "Apple___Black_rot": "apple_black_rot.JPG",
    "Apple___Cedar_apple_rust": "Apple_ceder_apple_rust.JPG",
    "Apple___healthy": "apple_healthy.JPG",
    "Blueberry___healthy": "blueberry_healthy.JPG",
    "Cherry_(including_sour)___Powdery_mildew": "cherry_powdery_mildew.JPG",
    "Cherry_(including_sour)___healthy": "cherry_healthy.JPG",
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot": "corn_cercospora_leaf.JPG",
    "Corn_(maize)___Common_rust_": "corn_common_rust.JPG",
    "Corn_(maize)___Northern_Leaf_Blight": "corn_northen_leaf_blight.JPG",
    "Corn_(maize)___healthy": "corn_healthy.jpg",
    "Grape___Black_rot": "grape_black_rot.JPG",
    "Grape___Esca_(Black_Measles)": "Grape_esca.JPG",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "grape_leaf_blight.JPG",
    "Grape___healthy": "grape_healthy.JPG",
    "Orange___Haunglongbing_(Citrus_greening)": "orange_haunglongbing.JPG",
    "Peach___Bacterial_spot": "peach_bacterial_spot.JPG",
    "Peach___healthy": "peach_healthy.JPG",
    "Pepper,_bell___Bacterial_spot": "pepper_bacterial_spot.JPG",
    "Pepper,_bell___healthy": "pepper_bell_healthy.JPG",
    "Potato___Early_blight": "potato_early_blight.JPG",
    "Potato___Late_blight": "potato_late_blight.JPG",
    "Potato___healthy": "potato_healthy.JPG",
    "Raspberry___healthy": "raspberry_healthy.JPG",
    "Soybean___healthy": "soyaben healthy.JPG",
    "Squash___Powdery_mildew": "squash_powdery_mildew.JPG",
    "Strawberry___Leaf_scorch": "starwberry_leaf_scorch.JPG",
    "Strawberry___healthy": "starwberry_healthy.JPG",
    "Tomato___Bacterial_spot": "tomato_bacterial_spot.JPG",
    "Tomato___Early_blight": "tomato_early_blight.JPG",
    "Tomato___Late_blight": "tomato_late_blight.JPG",
    "Tomato___Leaf_Mold": "tomato_leaf_mold.JPG",
    "Tomato___Septoria_leaf_spot": "tomato_septoria_leaf_spot.JPG",
    "Tomato___Spider_mites_Two-spotted_spider_mite": "tomato_spider_mites_two_spotted_spider_mites.JPG",
    "Tomato___Target_Spot": "tomato_target_spot.JPG",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "tomato_yellow_leaf_curl_virus.JPG",
    "Tomato___Tomato_mosaic_virus": "tomato_mosaic_virus.JPG",
    "Tomato___healthy": "tomato_healthy.JPG",
}

ALL_CLASSES = list(TEST_IMAGE_MAP.keys())
TARGET_PER_CLASS = 5
DATASET_DIR = "dataset"
TEST_DIR = "test_images"


def augment_image(img, idx):
    """Create an augmented version of the image."""
    augmentations = [
        lambda i: i.transpose(Image.FLIP_LEFT_RIGHT),
        lambda i: i.transpose(Image.FLIP_TOP_BOTTOM),
        lambda i: i.rotate(random.choice([90, 180, 270]), expand=True),
        lambda i: i.rotate(random.randint(-30, 30), expand=False, fillcolor=(0, 0, 0)),
        lambda i: ImageEnhance.Brightness(i).enhance(random.uniform(0.7, 1.3)),
        lambda i: ImageEnhance.Contrast(i).enhance(random.uniform(0.7, 1.3)),
        lambda i: ImageEnhance.Color(i).enhance(random.uniform(0.7, 1.4)),
        lambda i: i.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5))),
    ]
    aug_fn = augmentations[idx % len(augmentations)]
    return aug_fn(img)


def main():
    print("=" * 60)
    print("  Building Mini Training Dataset (~190 images)")
    print("=" * 60)
    
    total_original = 0
    total_augmented = 0
    total_from_test = 0
    
    for cls_name in ALL_CLASSES:
        cls_dir = os.path.join(DATASET_DIR, cls_name)
        os.makedirs(cls_dir, exist_ok=True)
        
        # Count existing images
        existing = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Copy test image if class is empty or has few images
        test_file = TEST_IMAGE_MAP.get(cls_name)
        test_path = os.path.join(TEST_DIR, test_file) if test_file else None
        
        if test_path and os.path.isfile(test_path):
            # Check if test image already copied
            test_dest = os.path.join(cls_dir, f"test_{test_file}")
            if not os.path.isfile(test_dest):
                shutil.copy2(test_path, test_dest)
                existing.append(f"test_{test_file}")
                total_from_test += 1
        
        total_original += len(existing)
        
        # Augment to reach target
        need = TARGET_PER_CLASS - len(existing)
        if need > 0 and existing:
            # Pick source images to augment from
            sources = existing.copy()
            aug_idx = 0
            for i in range(need):
                src_name = sources[i % len(sources)]
                src_path = os.path.join(cls_dir, src_name)
                try:
                    img = Image.open(src_path).convert("RGB")
                    aug_img = augment_image(img, aug_idx)
                    aug_name = f"aug_{aug_idx}_{src_name}"
                    aug_img.save(os.path.join(cls_dir, aug_name), "JPEG", quality=90)
                    aug_idx += 1
                    total_augmented += 1
                except Exception as e:
                    print(f"  ⚠️  Failed to augment {src_path}: {e}")
        
        final_count = len([f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        status = "✅" if final_count >= TARGET_PER_CLASS else "⚠️"
        print(f"  {status} {cls_name}: {final_count} images")
    
    # Final summary
    grand_total = sum(
        len([f for f in os.listdir(os.path.join(DATASET_DIR, d)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d)) and d != '_unclassified'
    )
    
    print(f"""
{"=" * 60}
  ✅ Mini dataset ready!
  
  📁 Location: {os.path.abspath(DATASET_DIR)}
  📊 Total images: {grand_total}
  📂 Classes: {len(ALL_CLASSES)}
  🆕 From test images: {total_from_test}
  🔄 Augmented: {total_augmented}

  Next: Train the model with:
    python train.py --model vit --data_dir dataset --epochs 10
{"=" * 60}
""")


if __name__ == "__main__":
    main()
