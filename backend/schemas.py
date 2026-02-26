"""
backend/schemas.py — All Pydantic request/response models.
Single source of truth for API contracts.
"""
from __future__ import annotations
import re
from pydantic import BaseModel, field_validator


# ── Validators ─────────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_PHONE_RE = re.compile(r"^\d{7,15}$")


# ── Auth ───────────────────────────────────────────────────────────────────────

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email address.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return v


class LoginBody(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class SendOTPBody(BaseModel):
    phone: str
    name: str = ""

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not _PHONE_RE.match(v):
            raise ValueError("Phone must be 7-15 digits.")
        return v


class VerifyOTPBody(BaseModel):
    phone: str
    otp: str
    name: str = ""


# ── App ────────────────────────────────────────────────────────────────────────

class FeedbackBody(BaseModel):
    scan_id: int
    was_correct: bool
    comment: str = ""


class ContactBody(BaseModel):
    name: str
    email: str
    subject: str = ""
    message: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email address.")
        return v
