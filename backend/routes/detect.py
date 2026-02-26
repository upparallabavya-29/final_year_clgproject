"""
backend/routes/detect.py — Plant disease detection endpoint.

POST /api/detect  — Upload image, run inference, save scan.
Public endpoint (no auth required), but scan is linked to user if authenticated.
"""
from __future__ import annotations
import io
import time
import logging
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Request
from PIL import Image

from core.disease_info import get_disease_info, SEVERITY_CONFIG
from backend.dependencies import get_current_user, get_model
from utils.database import insert_scan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["detection"])


@router.post("/detect")
async def detect(
    request: Request,
    file: UploadFile = File(...),
    model: str = Query("vit", pattern="^(vit|swin)$"),
):
    # ── Validate file ──────────────────────────────────────────────────────
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, detail="Only image files are accepted.")

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(413, detail="Image too large (max 20 MB).")

    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(400, detail="Could not open image. Please upload a valid JPG/PNG/WEBP.")

    # ── Load model ─────────────────────────────────────────────────────────
    ml_model, err = get_model(model)
    if ml_model is None:
        raise HTTPException(
            503,
            detail=f"Model '{model}' is not available: {err}. "
                   "Please ensure model checkpoints are present in checkpoints/ directory.",
        )

    # ── Inference ──────────────────────────────────────────────────────────
    try:
        from core.inference import run_inference
        t0 = time.perf_counter()
        pred_idx, confidence, top3 = run_inference(ml_model, pil_image)
        inference_ms = round((time.perf_counter() - t0) * 1000, 1)
    except Exception as exc:
        logger.error("Inference failed: %s", exc, exc_info=True)
        raise HTTPException(500, detail=f"Inference error: {exc}")

    # ── Build result ───────────────────────────────────────────────────────
    class_name = top3[0][0]
    info       = get_disease_info(class_name)
    sev_cfg    = SEVERITY_CONFIG.get(info["severity"], SEVERITY_CONFIG["medium"])

    # ── Persist scan (link to user if authenticated) ───────────────────────
    current_user = get_current_user(request)
    user_id      = current_user["id"] if current_user else None

    scan_record = {
        "user_id":      user_id,
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crop":         info["crop"],
        "disease":      info["disease"],
        "confidence":   round(confidence, 2),
        "severity":     info["severity"],
        "model":        model,
        "filename":     file.filename or "upload",
        "inference_ms": inference_ms,
    }
    scan_id = insert_scan(scan_record)

    return {
        "demo_mode":      False,
        "model":          model,
        "class_name":     class_name,
        "crop":           info["crop"],
        "disease":        info["disease"],
        "confidence":     round(confidence, 2),
        "severity":       info["severity"],
        "severity_label": sev_cfg["label"],
        "severity_color": sev_cfg["color"],
        "cause":          info["cause"],
        "treatment":      info["treatment"],
        "top3":           [{"class": c, "probability": round(p, 4)} for c, p in top3],
        "inference_ms":   inference_ms,
        "scan_id":        scan_id,
    }
