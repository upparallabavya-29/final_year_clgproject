"""
backend/auth.py — JWT, Password hashing, OTP helpers.
All config read from env. OTPs are persisted to the DB (not in-memory).
"""
from __future__ import annotations
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
SECRET_KEY      = os.getenv("SECRET_KEY", "cropguard-super-secret-change-in-prod-2024")
ALGORITHM       = "HS256"
TOKEN_EXPIRE_H  = 24 * 7   # 7 days

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

OTP_EXPIRE_SECS = 300   # 5 minutes


# ── Password helpers ───────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ── JWT helpers ────────────────────────────────────────────────────────────────

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_H)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
