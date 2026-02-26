"""
backend/routes/auth.py — Authentication endpoints.

POST /api/auth/register          — Email + password signup
POST /api/auth/login             — Email + password login
GET  /api/auth/google            — Redirect to Google consent
GET  /api/auth/google/callback   — Google OAuth callback → JWT
POST /api/auth/mobile/send-otp   — Send OTP
POST /api/auth/mobile/verify     — Verify OTP → JWT
GET  /api/auth/me                — Current authenticated user
"""
from __future__ import annotations
import os
import logging
import urllib.parse

from fastapi import APIRouter, HTTPException, Query, Request

from backend.auth import (
    hash_password, verify_password, create_token,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    OTP_EXPIRE_SECS,
)
from backend.schemas import RegisterBody, LoginBody, SendOTPBody, VerifyOTPBody
from backend.dependencies import require_user, limiter
from utils.database import (
    create_user, get_user_by_email, get_user_by_phone,
    get_user_by_google_sub, get_user_by_id, update_user_last_login,
    create_otp, verify_otp_db,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _user_response(user: dict) -> dict:
    """Build public user object + JWT."""
    token = create_token({
        "sub": str(user["id"]),
        "email": user.get("email"),
        "name": user.get("name"),
    })
    return {
        "token": token,
        "user": {
            "id":       user["id"],
            "name":     user.get("name", ""),
            "email":    user.get("email", ""),
            "phone":    user.get("phone", ""),
            "avatar":   user.get("avatar", ""),
            "provider": user.get("provider", "email"),
        },
    }


# ── Email/Password ─────────────────────────────────────────────────────────────

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterBody):
    existing = get_user_by_email(body.email)
    if existing:
        raise HTTPException(409, detail="An account with this email already exists.")

    user_id = create_user({
        "email":         body.email,
        "name":          body.name.strip(),
        "password_hash": hash_password(body.password),
        "provider":      "email",
    })
    user = get_user_by_id(user_id)
    update_user_last_login(user_id)
    return _user_response(user)


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginBody):
    user = get_user_by_email(body.email)
    if not user:
        raise HTTPException(401, detail="Invalid email or password.")
    if not user.get("password_hash"):
        raise HTTPException(
            401,
            detail=f"This account uses {user['provider']} sign-in. Please use that method.",
        )
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, detail="Invalid email or password.")

    update_user_last_login(user["id"])
    return _user_response(user)


# ── Google OAuth ───────────────────────────────────────────────────────────────

@router.get("/google")
async def google_login():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(503, detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID env var.")
    params = urllib.parse.urlencode({
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
    })
    from fastapi.responses import RedirectResponse
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@router.get("/google/callback")
async def google_callback(code: str = Query(...)):
    import httpx
    from fastapi.responses import RedirectResponse

    # Use context manager to prevent socket leak
    async with httpx.AsyncClient(timeout=15.0) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":          code,
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri":  GOOGLE_REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
        )
        token_data = token_res.json()
        if "error" in token_data:
            raise HTTPException(400, detail=token_data.get("error_description", "Google auth failed."))

        userinfo_res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        info = userinfo_res.json()

    sub    = info.get("sub")
    email  = info.get("email", "").lower()
    name   = info.get("name", "")
    avatar = info.get("picture", "")

    # Find or create user
    user = get_user_by_google_sub(sub)
    if not user and email:
        user = get_user_by_email(email)
    if not user:
        user_id = create_user({
            "email": email, "google_sub": sub,
            "name": name, "avatar": avatar, "provider": "google",
        })
        user = get_user_by_id(user_id)

    update_user_last_login(user["id"])
    result = _user_response(user)
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback#token={result['token']}"
        f"&name={urllib.parse.quote(name)}"
        f"&email={urllib.parse.quote(email)}"
        f"&avatar={urllib.parse.quote(avatar)}"
    )


# ── Mobile OTP ─────────────────────────────────────────────────────────────────

import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

@router.post("/mobile/send-otp")
@limiter.limit("3/minute")
async def send_otp(request: Request, body: SendOTPBody):
    otp = create_otp(body.phone, OTP_EXPIRE_SECS)
    
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your CropGuard AI verification code is: {otp}. It expires in {OTP_EXPIRE_SECS // 60} minutes.",
                from_=TWILIO_PHONE_NUMBER,
                to=f"+91{body.phone}" 
            )
            logger.info("OTP sent to %s via Twilio (SID: %s)", body.phone, message.sid)
        except Exception as e:
            logger.error("Failed to send OTP via Twilio: %s", e)
            raise HTTPException(500, detail="Failed to send SMS. Please try again later. Verify your Twilio credentials.")
    else:
        logger.warning("Twilio credentials missing. OTP generated but NOT sent via SMS.")

    return {
        "message": f"OTP sent to {body.phone}.",
        "expires_in": OTP_EXPIRE_SECS,
    }


@router.post("/mobile/verify")
@limiter.limit("5/minute")
async def verify_mobile(request: Request, body: VerifyOTPBody):
    if not verify_otp_db(body.phone.strip(), body.otp.strip()):
        raise HTTPException(401, detail="Invalid or expired OTP. Please request a new one.")

    user = get_user_by_phone(body.phone.strip())
    if not user:
        user_id = create_user({
            "phone":    body.phone.strip(),
            "name":     body.name or f"User {body.phone[-4:]}",
            "provider": "mobile",
        })
        user = get_user_by_id(user_id)

    update_user_last_login(user["id"])
    return _user_response(user)


# ── Profile ────────────────────────────────────────────────────────────────────

@router.get("/me")
async def me(request: Request):
    user = require_user(request)
    return {
        "id":         user["id"],
        "name":       user.get("name", ""),
        "email":      user.get("email", ""),
        "phone":      user.get("phone", ""),
        "avatar":     user.get("avatar", ""),
        "provider":   user.get("provider", "email"),
        "created_at": user.get("created_at", ""),
    }
