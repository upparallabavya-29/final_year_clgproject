"""
backend/routes/contact.py — Contact form endpoint.

POST /api/contact  — Submit a contact message.
"""
from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.schemas import ContactBody
from utils.database import save_contact
from utils.email import try_send_email

router = APIRouter(prefix="/api", tags=["contact"])


@router.post("/contact")
async def contact(body: ContactBody):
    try:
        row_id = save_contact({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name":      body.name,
            "email":     body.email,
            "subject":   body.subject,
            "message":   body.message,
        })
        try_send_email(body.name, body.email, body.subject or "No Subject", body.message)
        return {"message": "Message received!", "id": row_id}
    except Exception as exc:
        raise HTTPException(500, detail=str(exc))
