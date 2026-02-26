"""
setup.py — One-command project setup for CropGuard AI.

Runs:
    1. pip install -r requirements.txt
    2. python download_data.py           (new PlantVillage dataset)
    3. python create_dummy_models.py     (placeholder weights for app demo)

Then prints instructions.
"""
import os
import subprocess
import sys


def run(cmd, check=True):
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def main():
    print("=" * 60)
    print("  CropGuard AI — Project Setup")
    print("=" * 60)

    # 1. Install dependencies
    print("\n[1/3] Installing Python dependencies …")
    if not run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        print("⚠️  pip install failed. Check requirements.txt and your network.")
        sys.exit(1)
    print("✅ Dependencies installed.")

    # 2. Download new dataset
    print("\n[2/3] Downloading PlantVillage dataset from Google Drive …")
    print("      (This may take a few minutes depending on your connection)")
    ok = run([sys.executable, "download_data.py"], check=False)
    if not ok:
        print("⚠️  Dataset download failed.")
        print("    You can retry later with:  python download_data.py")
        print("    Or manually place images in:  dataset/<ClassName>/image.jpg")
    else:
        print("✅ Dataset ready at: ./dataset/")

    # 3. Create placeholder model weights (for app demo)
    print("\n[3/3] Creating placeholder model checkpoints …")
    if os.path.exists("create_dummy_models.py"):
        run([sys.executable, "create_dummy_models.py"], check=False)
        print("✅ Placeholder weights created in ./checkpoints/")
    else:
        print("   create_dummy_models.py not found — skipping.")

    # Final instructions
    print("\n" + "=" * 60)
    print("  Setup complete!")
    print("=" * 60)
    print("""
Next steps:
  1. Run the demo app (uses placeholder weights — random predictions):
       streamlit run app.py

  2. Train real models (requires dataset to be ready):
       python train.py --model vit  --data_dir dataset --epochs 30
       python train.py --model swin --data_dir dataset --epochs 30

  3. (Optional) Configure email for contact form:
       copy .env.example .env   →  fill in SMTP_USER / SMTP_PASS / SMTP_TO

  4. Run tests:
       python -m pytest tests/ -v

  5. Build Docker image:
       docker build -t cropguard-ai .
       docker run -p 8501:8501 cropguard-ai
""")


if __name__ == "__main__":
    main()
