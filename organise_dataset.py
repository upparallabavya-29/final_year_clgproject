"""
organise_dataset.py — One-shot helper to organise flat PlantVillage images into
class sub-directories by parsing class codes from filenames.

Run ONCE after extracting the zip if it came with flat images:
    python organise_dataset.py
    python organise_dataset.py --data_dir my_other_folder
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

# ── Short-code → PlantVillage class mappings ─────────────────────────────────
# Based on the embedded codes in plantvillage filenames
SHORTCODE_MAP = {
    "RS_HL":              "Strawberry___healthy",
    "RS_Late.B":          "Strawberry___Leaf_scorch",
    "RS_Early.B":         "Potato___Early_blight",
    "RS_LB":              "Potato___Late_blight",
    "GH_HL Leaf":         "Grape___healthy",
    "GH_HL":              "Grape___healthy",
    "PSU_CG":             "Corn_(maize)___Common_rust_",
    "GHLB2 Leaf":         "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "GHLB2":              "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "JR_HL":              "Tomato___healthy",
    "JR_B.Spot":          "Tomato___Bacterial_spot",
    "NREC_B.Spot":        "Pepper,_bell___Bacterial_spot",
    "Com.G_SpM_FL":       "Tomato___Spider_mites_Two-spotted_spider_mite",
    "HL Leaf":            "Apple___healthy",   # GH prefix already caught above
}

# Known PlantVillage class names (exact folder names)
PLANTVILLAGE_CLASSES = {
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
}


def guess_class(filename: str) -> str | None:
    stem = Path(filename).stem
    name = filename

    # Check if filename itself starts with a known PlantVillage class
    for cls in PLANTVILLAGE_CLASSES:
        if name.startswith(cls):
            return cls

    # Check for short-codes (longest match first to avoid substring issues)
    for code in sorted(SHORTCODE_MAP, key=len, reverse=True):
        if code in stem:
            return SHORTCODE_MAP[code]

    # Check UUID___CODE pattern: "<uuid>___<CODE>_<desc>.jpg"
    if "___" in stem:
        code_part = stem.split("___", 1)[1]
        for code in sorted(SHORTCODE_MAP, key=len, reverse=True):
            if code_part.startswith(code) or code in code_part:
                return SHORTCODE_MAP[code]

    return None


def organise(data_dir: str, dry_run: bool = False) -> None:
    data_dir   = os.path.abspath(data_dir)
    img_exts   = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    flat_files = [
        f for f in os.scandir(data_dir)
        if f.is_file() and Path(f.name).suffix.lower() in img_exts
    ]

    if not flat_files:
        print("✅ No flat image files found — dataset may already be organised.")
        _show_summary(data_dir)
        return

    print(f"Found {len(flat_files)} flat images. Organising by class …\n")
    stats       = defaultdict(int)
    unresolved  = []
    unclass_dir = os.path.join(data_dir, "_unclassified")

    for f in flat_files:
        cls = guess_class(f.name)
        if cls:
            target_dir = os.path.join(data_dir, cls)
            if not dry_run:
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(f.path, os.path.join(target_dir, f.name))
            stats[cls] += 1
        else:
            unresolved.append(f.name)

    # Move unresolved files
    if unresolved and not dry_run:
        os.makedirs(unclass_dir, exist_ok=True)
        for fname in unresolved:
            src = os.path.join(data_dir, fname)
            if os.path.exists(src):
                shutil.move(src, os.path.join(unclass_dir, fname))

    # Report
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"{prefix}Classes created from filenames:")
    for cls in sorted(stats):
        print(f"  {cls:<55} {stats[cls]:>4} images")

    if unresolved:
        print(f"\n⚠️  {len(unresolved)} unrecognised files → {'would go to' if dry_run else 'moved to'} _unclassified/")
        for fname in unresolved[:10]:
            print(f"  {fname}")
        if len(unresolved) > 10:
            print(f"  … and {len(unresolved)-10} more")

    if not dry_run:
        n_classes = len([d for d in os.scandir(data_dir) if d.is_dir() and not d.name.startswith((".", "_"))])
        print(f"\n✅  Done! {n_classes} class folders in: {data_dir}")


def _show_summary(data_dir: str) -> None:
    dirs = [d for d in os.scandir(data_dir) if d.is_dir() and not d.name.startswith((".", "_"))]
    print(f"\nCurrent structure: {len(dirs)} class folders")
    for d in sorted(dirs, key=lambda x: x.name):
        n = len([f for f in os.scandir(d.path) if f.is_file()])
        print(f"  {d.name:<55} {n:>4} images")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organise flat PlantVillage images into class folders")
    parser.add_argument("--data_dir", default="dataset", help="Dataset directory (default: ./dataset)")
    parser.add_argument("--dry-run",  action="store_true", help="Preview changes without moving files")
    args = parser.parse_args()
    organise(args.data_dir, dry_run=args.dry_run)
