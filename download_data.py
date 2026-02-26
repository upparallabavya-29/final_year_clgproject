"""
download_data.py — Download and organise the PlantVillage dataset from Google Drive.

Drive file ID: 1x1frAh0rR323GyCIIbESUUOIpnPw7KMs

The downloaded ZIP contains flat image files whose filenames encode the class:
    <uuid>___<crop>_<condition>_<code>.jpg        (PlantVillage naming scheme)
    e.g. 000bf685___GH_HL Leaf 308.1.jpg
    OR already a clean name like  Apple___Black_rot/img0.jpg

This script handles BOTH:
  1. ImageFolder-style (class sub-dirs)  → validated and used as-is
  2. Flat files with class in filename   → auto-sorted into sub-dirs

Usage:
    python download_data.py               # to ./dataset/
    python download_data.py --out mydata  # to ./mydata/
    python download_data.py --keep-old    # don't delete existing dataset
    python download_data.py --inspect     # show structure without downloading again
"""

import argparse
import gdown
import zipfile
import tarfile
import os
import re
import sys
import shutil
from pathlib import Path
from collections import defaultdict

# ── Dataset config ────────────────────────────────────────────────────────────
DRIVE_FILE_ID       = "19WI95cBDxKUHofZ_cVKD4_p60ECkNH8l"
DEFAULT_OUT         = "dataset"
EXPECTED_MIN_CLASSES = 2   # relaxed — even a small dataset is usable

# ── PlantVillage class names (used for filename-to-class matching) ─────────────
# These are the canonical folder names from the PlantVillage dataset
PLANTVILLAGE_CLASSES = [
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

# Short-code to class mapping derived from PlantVillage filename conventions:
# RS = Raspberry/Strawberry, HL = Healthy Leaf, GH = Grape/Healthy,
# PSU_CG = Corn/Grape data, NREC/JR = Tomato etc.
# We parse by matching the 3-letter crop code embedded in filename
_SHORTCODE_MAP = {
    # Filename fragment → PlantVillage class
    "HL Leaf":            None,   # need crop context
    "RS_HL":              "Strawberry___healthy",
    "RS_Late.B":          "Strawberry___Leaf_scorch",
    "RS_Early.B":         "Potato___Early_blight",
    "RS_LB":              "Potato___Late_blight",
    "GH_HL":              "Grape___healthy",
    "PSU_CG":             "Corn_(maize)___Common_rust_",
    "GHLB2":              "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "JR_HL":              "Tomato___healthy",
    "JR_B.Spot":          "Tomato___Bacterial_spot",
    "NREC_B.Spot":        "Pepper,_bell___Bacterial_spot",
    "Com.G_SpM_FL":       "Tomato___Spider_mites_Two-spotted_spider_mite",
}


# ── Core helpers ──────────────────────────────────────────────────────────────

def _detect_and_extract(archive_path: str, out_dir: str) -> None:
    """Extract zip or tar archive into out_dir."""
    if zipfile.is_zipfile(archive_path):
        print("  Extracting ZIP archive …")
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(out_dir)
    elif tarfile.is_tarfile(archive_path):
        print("  Extracting TAR archive …")
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(out_dir)
    else:
        raise ValueError(f"Unrecognised archive format: {archive_path}")


def _find_deepest_class_root(root: str) -> str:
    """
    Recursively traverse single-child directory chains until we find a directory
    that contains multiple sub-dirs (the class folders) or image files.
    Handles N levels of nesting, e.g.: root/Plant/PlantVillage/<classes>
    """
    path = Path(root)
    while True:
        children = [c for c in path.iterdir() if not c.name.startswith(".")]
        dirs     = [c for c in children if c.is_dir()]
        files    = [c for c in children if c.is_file()]

        if len(dirs) == 1 and len(files) == 0:
            # Exactly one sub-dir, no files → go deeper
            print(f"  Traversing nested folder: {dirs[0].name} …")
            path = dirs[0]
        else:
            # Multiple dirs found (class folders) OR files found (flat dataset)
            return str(path)


def _move_to_root(src_dir: str, dst_dir: str) -> None:
    """Move all contents of src_dir into dst_dir (one level up)."""
    for item in os.scandir(src_dir):
        dest = os.path.join(dst_dir, item.name)
        if not os.path.exists(dest):
            shutil.move(item.path, dest)
    shutil.rmtree(src_dir)


def _guess_class_from_filename(filename: str) -> str | None:
    """
    Attempt to infer PlantVillage class from a flat filename.
    Handles formats like:
      000bf685___GH_HL Leaf 308.1.jpg
      Apple___Black_rot/img0.jpg   (already class-prefixed)
    Returns class name string or None if unrecognised.
    """
    stem = Path(filename).stem

    # Case 1: filename is already "<Class>___<desc>" or path has class folder
    if "___" in filename:
        parts = filename.split("___")
        candidate = parts[0].strip()
        if candidate in PLANTVILLAGE_CLASSES:
            return candidate
        # Might be uuid___SHORTCODE format
        if len(parts) >= 2:
            code_part = parts[1]
            for code, cls in _SHORTCODE_MAP.items():
                if code in code_part and cls:
                    return cls

    # Case 2: match short-codes in full filename
    for code, cls in _SHORTCODE_MAP.items():
        if code in stem and cls:
            return cls

    return None


def _organise_flat_images(out_dir: str) -> dict:
    """
    If dataset directory contains flat image files (no class sub-dirs),
    parse the class from each filename and move into <out_dir>/<class>/ folders.
    Returns stats dict: {class_name: count}.
    """
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    all_files  = [
        f for f in os.scandir(out_dir)
        if f.is_file() and Path(f.name).suffix.lower() in image_exts
    ]
    if not all_files:
        return {}

    print(f"\n  Found {len(all_files)} flat image files — organising into class folders …")

    unclassified_dir = os.path.join(out_dir, "_unclassified")
    stats      = defaultdict(int)
    unresolved = []

    for f in all_files:
        cls = _guess_class_from_filename(f.name)
        if cls:
            target_dir = os.path.join(out_dir, cls)
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(f.path, os.path.join(target_dir, f.name))
            stats[cls] += 1
        else:
            unresolved.append(f.name)

    if unresolved:
        os.makedirs(unclassified_dir, exist_ok=True)
        for fname in unresolved:
            src = os.path.join(out_dir, fname)
            if os.path.exists(src):
                shutil.move(src, os.path.join(unclassified_dir, fname))
        print(f"  ⚠️  {len(unresolved)} images could not be classified → moved to _unclassified/")

    return dict(stats)


def _validate(out_dir: str) -> int:
    """Return number of class folders. Raises if fewer than minimum."""
    classes = [
        d.name for d in os.scandir(out_dir)
        if d.is_dir() and not d.name.startswith((".", "_"))
    ]
    n = len(classes)
    if n < EXPECTED_MIN_CLASSES:
        raise RuntimeError(
            f"Validation failed: only {n} usable class folders found in '{out_dir}'.\n"
            f"Expected ≥ {EXPECTED_MIN_CLASSES}.\n"
            "Check the archive contents or confirm the Google Drive file is set to "
            "'Anyone with link can view'."
        )
    return n


def _inspect(out_dir: str) -> None:
    """Print a summary of what's currently in the dataset directory."""
    if not os.path.isdir(out_dir):
        print(f"❌ Directory '{out_dir}' does not exist.")
        return

    all_entries = list(os.scandir(out_dir))
    dirs   = [e for e in all_entries if e.is_dir()  and not e.name.startswith((".", "_"))]
    files  = [e for e in all_entries if e.is_file()]
    hidden = [e for e in all_entries if e.name.startswith((".", "_"))]

    print(f"\n📁 Dataset at: {os.path.abspath(out_dir)}")
    print(f"   Class folders : {len(dirs)}")
    print(f"   Flat files    : {len(files)}")
    print(f"   Hidden/misc   : {len(hidden)}")

    if dirs:
        print("\n  Class folders found:")
        for d in sorted(dirs, key=lambda x: x.name):
            n_imgs = len([f for f in os.scandir(d.path) if f.is_file()])
            print(f"    {d.name:<55} {n_imgs:>5} images")
    elif files:
        print(f"\n  Sample filenames:")
        for f in files[:6]:
            print(f"    {f.name}")
        if len(files) > 6:
            print(f"    … and {len(files)-6} more")


def delete_old_dataset(out_dir: str) -> None:
    if os.path.exists(out_dir):
        print(f"🗑️  Deleting old dataset at: {out_dir}")
        shutil.rmtree(out_dir)
    else:
        print(f"  No existing dataset at '{out_dir}' — nothing to delete.")


# ── Main ─────────────────────────────────────────────────────────────────────

def download_plantvillage(out_dir: str = DEFAULT_OUT, delete_old: bool = True) -> None:
    if delete_old:
        delete_old_dataset(out_dir)

    os.makedirs(out_dir, exist_ok=True)
    archive_path = os.path.join(out_dir, "_download.archive")

    print(f"⬇️  Downloading dataset (Drive ID: {DRIVE_FILE_ID}) …")
    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    try:
        gdown.download(url, archive_path, quiet=False, fuzzy=True)
    except Exception as exc:
        print(f"  Retrying without cookies ({exc}) …")
        gdown.download(url, archive_path, quiet=False, fuzzy=True, use_cookies=False)

    if not os.path.exists(archive_path) or os.path.getsize(archive_path) < 1024:
        print("❌ Download seems to have failed. Ensure the Drive file is publicly accessible.")
        sys.exit(1)

    _detect_and_extract(archive_path, out_dir)
    os.remove(archive_path)

    # ── Handle nesting at any depth ──
    actual_root = _find_deepest_class_root(out_dir)
    if actual_root != out_dir:
        print(f"  Moving contents from '{actual_root}' → '{out_dir}' …")
        _move_to_root(actual_root, out_dir)

    # ── Check if class sub-dirs exist yet ──
    existing_dirs = [d for d in os.scandir(out_dir) if d.is_dir() and not d.name.startswith((".", "_"))]

    if not existing_dirs:
        # Flat image files → auto-organise by class from filename
        stats = _organise_flat_images(out_dir)
        if stats:
            print(f"\n  Classes organised from filenames:")
            for cls, cnt in sorted(stats.items()):
                print(f"    {cls:<55} {cnt:>4} images")
        else:
            print("⚠️  No images could be classified. Inspect the archive structure manually.")

    n_classes = _validate(out_dir)
    print(f"\n✅  Dataset ready at: {os.path.abspath(out_dir)}")
    print(f"    {n_classes} class folders found.")
    print(f"\n    Next step:")
    print(f"    python train.py --model vit --data_dir {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download & organise PlantVillage dataset")
    parser.add_argument("--out",      default=DEFAULT_OUT, help="Output directory (default: ./dataset)")
    parser.add_argument("--keep-old", action="store_true",  help="Keep existing dataset instead of deleting")
    parser.add_argument("--inspect",  action="store_true",  help="Inspect current dataset structure (no download)")
    args = parser.parse_args()

    if args.inspect:
        _inspect(args.out)
    else:
        download_plantvillage(out_dir=args.out, delete_old=not args.keep_old)
