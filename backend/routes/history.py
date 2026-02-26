"""
backend/routes/history.py — Scan history, analytics, and feedback.

GET    /api/history    — Paginated scan history (user-scoped)
GET    /api/analytics  — Aggregated dashboard (user-scoped)
DELETE /api/history    — Clear user's scan history (protected)
POST   /api/feedback   — Submit scan feedback
"""
from __future__ import annotations
import logging

from fastapi import APIRouter, HTTPException, Query, Request, Depends

from backend.dependencies import require_user, get_current_user
from backend.schemas import FeedbackBody
from utils.database import (
    get_user_scans, get_user_stats,
    insert_feedback, clear_user_scans,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def history(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Paginated scan history. Scoped to current user if authenticated."""
    user = require_user(request)
    result = get_user_scans(user["id"], page, page_size)
    return result


@router.get("/analytics")
async def analytics(request: Request):
    """Aggregated stats. Scoped to current user if authenticated."""
    user = require_user(request)
    return get_user_stats(user["id"])


@router.delete("/history")
async def clear_history(request: Request):
    """Clear all scan history for the current user."""
    user = require_user(request)
    clear_user_scans(user["id"])
    return {"message": "Your scan history has been cleared."}


@router.post("/feedback")
async def feedback(body: FeedbackBody, request: Request):
    try:
        insert_feedback(body.scan_id, body.was_correct, body.comment)
        return {"message": "Feedback saved."}
    except Exception as exc:
        raise HTTPException(500, detail=str(exc))
