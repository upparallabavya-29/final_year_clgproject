# CropGuard AI — Plant Disease Detection 🌿

Production-grade plant disease detection using Vision Transformers (ViT & Swin) trained on the PlantVillage dataset (87K+ images, 38 classes, 14 crops).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create placeholder checkpoints (random weights — for UI smoke test only)
python tools/create_placeholders.py

# 3. Run the app
streamlit run app.py
```

## Training on Real Data

```bash
# Step 1 — Get the Kaggle PlantVillage dataset
kaggle datasets download -d emmarex/plantdisease
unzip plantdisease.zip -d dataset/

# Step 2 — Train models (approx. 2–3 hours on GPU)
python train.py --model vit  --data_dir dataset --epochs 30 --amp
python train.py --model swin --data_dir dataset --epochs 30 --amp

# Step 3 — Evaluate and save accuracy
python evaluate.py --model vit  --data_dir dataset
python evaluate.py --model swin --data_dir dataset

# Step 4 — Launch (accuracy auto-loads from eval_results/)
streamlit run app.py
```

## Project Structure

```
app.py                  ← Streamlit router (~110 lines)
core/
  inference.py          ← Model loader (returns error tuple — cache-safe)
  disease_info.py       ← 38-class disease knowledge base
  i18n.py               ← Multi-language support (en / hi / te)
pages/
  home.py               ← Landing page (loads real accuracy from eval_results/)
  detection.py          ← Detection + rate limiting + batch processing
  history.py            ← Paginated scan history
  analytics.py          ← Dashboard (SQLite charts)
  encyclopedia.py       ← 38-class filterable encyclopedia
  about.py              ← About + training guide
  contact.py            ← Contact form → SQLite contacts table
data/
  dataset.py            ← PlantVillage ImageFolder loader
  transforms.py         ← Training + inference transforms
utils/
  database.py           ← SQLite WAL mode + contacts table
  report.py             ← PDF export (fpdf2)
  image_utils.py        ← Image quality checker
  gradcam.py            ← Grad-CAM heatmap
  logging_config.py     ← Structured logging
models/
  __init__.py
tools/
  create_placeholders.py← Dummy checkpoint creator (replaces create_dummy_models.py)
  download_data.py      ← Dataset downloader
  organise_dataset.py   ← Dataset organiser
checkpoints/            ← model .pth weights + class_names.json
eval_results/           ← evaluate.py JSON output (accuracy auto-loaded by home.py)
translations/           ← en.json  hi.json  te.json
```

## Production Deployment

```bash
# Docker
docker compose up -d

# Environment variables (copy .env.example → .env)
cp .env.example .env
# Edit SMTP_USER / SMTP_PASS for contact-form emails
```

## What Changed in v4.0

| Area                      | Change                                                      |
| ------------------------- | ----------------------------------------------------------- |
| **app.py**                | 1426-line monolith → 110-line router                        |
| **core/inference.py**     | `load_model()` returns `(model, err)` — never poisons cache |
| **core/disease_info.py**  | Graceful fallback for any unknown class                     |
| **utils/database.py**     | WAL mode + `contacts` table (no JSON race condition)        |
| **pages/home.py**         | Real accuracy from `eval_results/` (no more fake 97.93%)    |
| **pages/detection.py**    | Per-session rate limit (20 scans/session)                   |
| **pages/history.py**      | Pagination (50 rows/page)                                   |
| **pages/encyclopedia.py** | Dynamic class count from `CLASS_NAMES`                      |
| **tools/**                | All dev scripts consolidated here                           |
| **docker-compose.yml**    | Added with volume mounts + health check                     |
| **pyproject.toml**        | Proper packaging with optional extras                       |
