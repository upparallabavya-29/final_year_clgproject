"""
backend/dependencies.py — Shared FastAPI dependencies.

- get_current_user   (optional auth — returns None if no token)
- require_user       (mandatory auth — raises 401)
- get_model          (cached model loader)
"""
from __future__ import annotations
import logging
from typing import Optional

from fastapi import Request, HTTPException

from backend.auth import decode_token
from utils.database import get_user_by_id

from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# ── API Rate Limiter ───────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Model cache (process-level singleton) ──────────────────────────────────────
_model_cache: dict[str, tuple] = {}


def get_model(model_name: str):
    """Load ML model with process-level caching. Returns (model, error_msg)."""
    if model_name not in _model_cache:
        try:
            from core.inference import load_model
            model, err = load_model(model_name)
            _model_cache[model_name] = (model, err)
        except Exception as e:
            _model_cache[model_name] = (None, str(e))
    return _model_cache[model_name]


# ── Auth dependencies ──────────────────────────────────────────────────────────

def get_current_user(request: Request) -> Optional[dict]:
    """Extract user from Bearer token. Returns None if unauthenticated."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        return get_user_by_id(int(user_id))
    except Exception:
        return None


def require_user(request: Request) -> dict:
    """Mandatory auth. Raises 401 if no valid token."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user
