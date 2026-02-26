"""
pages/about.py — About page with project structure and training instructions.
"""

from __future__ import annotations
import streamlit as st
from core.inference import CLASS_NAMES


def render() -> None:
    st.markdown("<h1 style='color:#1b4332;'>ℹ️ About</h1>", unsafe_allow_html=True)
    st.markdown(f"""
This application is a **final-year college project** that uses state-of-the-art
Transformer deep learning to detect plant diseases from leaf images.

### 🧠 AI Models Used

| Model | Architecture | Parameters |
|---|---|---|
| **ViT** | `vit_base_patch16_224` | ~86M |
| **Swin** | `swin_base_patch4_window7_224` | ~88M |

### 📊 Dataset
- **Name:** PlantVillage
- **Images:** 87,000+
- **Classes:** {len(CLASS_NAMES)} (disease + healthy)
- **Crops:** 14+ species

### 📁 Project Structure
```
app.py                  ← Streamlit router (~80 lines)
core/
  inference.py          ← Model loading + inference pipeline
  disease_info.py       ← Disease knowledge base (38 classes)
  i18n.py               ← Multi-language support
pages/
  home.py  detection.py  history.py  analytics.py
  encyclopedia.py  about.py  contact.py
data/
  dataset.py            ← PlantVillage ImageFolder loader
  transforms.py         ← Image augmentation
models/
  __init__.py           ← Model factory
utils/
  database.py           ← SQLite (WAL mode)
  report.py             ← PDF export
  image_utils.py        ← Image quality checker
  gradcam.py            ← Grad-CAM heatmap
tools/
  create_placeholders.py ← Dummy model creator
  download_data.py       ← Dataset downloader
  organise_dataset.py    ← Dataset organiser
checkpoints/            ← Saved model weights (.pth)
eval_results/           ← Model evaluation outputs
translations/           ← en / hi / te JSON files
```

### 🚀 Quick Start
```bash
pip install -r requirements.txt
python tools/create_placeholders.py   # placeholder weights for smoke test
streamlit run app.py
```

### 🎓 Training on Real Data
```bash
# Step 1 — Download PlantVillage (Kaggle)
kaggle datasets download -d emmarex/plantdisease
unzip plantdisease.zip -d dataset/

# Step 2 — Train
python train.py --model vit --data_dir dataset --epochs 30 --amp

# Step 3 — Evaluate
python evaluate.py --model vit --data_dir dataset

# Step 4 — Run app (accuracy auto-loads from eval_results/)
streamlit run app.py
```
""")
