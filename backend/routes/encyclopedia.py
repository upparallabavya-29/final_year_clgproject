"""
backend/routes/encyclopedia.py — Disease encyclopedia, crops, severities.

GET /api/encyclopedia       — Filtered disease list
GET /api/encyclopedia/{key} — Single disease detail
GET /api/crops              — Supported crop names
GET /api/severities         — Severity levels
GET /api/stats/summary      — Public summary stats for landing page
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query

from core.disease_info import DISEASE_INFO, SEVERITY_CONFIG
from utils.database import get_public_summary

router = APIRouter(prefix="/api", tags=["encyclopedia"])


@router.get("/encyclopedia")
async def encyclopedia(
    crop: str = Query(None),
    severity: str = Query(None),
    search: str = Query(None),
):
    results = []
    for key, info in DISEASE_INFO.items():
        if crop and info["crop"].lower() != crop.lower():
            continue
        if severity and info["severity"] != severity:
            continue
        if search:
            q = search.lower()
            if q not in info["disease"].lower() and q not in info["crop"].lower():
                continue
        sev_cfg = SEVERITY_CONFIG.get(info["severity"], SEVERITY_CONFIG["medium"])
        results.append({
            "key":            key,
            "crop":           info["crop"],
            "disease":        info["disease"],
            "severity":       info["severity"],
            "severity_label": sev_cfg["label"],
            "severity_color": sev_cfg["color"],
            "cause":          info["cause"],
            "treatment":      info["treatment"],
        })
    return {"total": len(results), "items": results}


@router.get("/encyclopedia/{key}")
async def encyclopedia_item(key: str):
    info = DISEASE_INFO.get(key)
    if not info:
        raise HTTPException(404, detail="Disease not found.")
    sev_cfg = SEVERITY_CONFIG.get(info["severity"], SEVERITY_CONFIG["medium"])
    return {
        "key":            key,
        "crop":           info["crop"],
        "disease":        info["disease"],
        "severity":       info["severity"],
        "severity_label": sev_cfg["label"],
        "severity_color": sev_cfg["color"],
        "cause":          info["cause"],
        "treatment":      info["treatment"],
    }


@router.get("/crops")
async def list_crops():
    return {"crops": sorted(set(v["crop"] for v in DISEASE_INFO.values()))}


@router.get("/severities")
async def list_severities():
    return [
        {"key": k, "label": v["label"], "color": v["color"]}
        for k, v in SEVERITY_CONFIG.items()
    ]


@router.get("/stats/summary")
async def public_summary():
    """Public landing page stats — no auth required."""
    db_stats = get_public_summary()
    return {
        "disease_classes": len(DISEASE_INFO),
        "crop_species":    len(set(v["crop"] for v in DISEASE_INFO.values())),
        "ai_models":       2,
        "total_scans":     db_stats.get("total_scans", 0),
        "total_users":     db_stats.get("total_users", 0),
    }
