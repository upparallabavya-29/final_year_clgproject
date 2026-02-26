"""
utils/email.py — Reusable email sending logic.
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

def try_send_email(name: str, email: str, subject: str, message: str) -> bool:
    """Send via Gmail SMTP if credentials configured. Returns True on success."""
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()
    smtp_to   = os.getenv("SMTP_TO", smtp_user).strip()

    if not smtp_user or not smtp_pass:
        logger.warning("SMTP_USER or SMTP_PASS not set. Email will not be sent.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"]    = smtp_user
        msg["To"]      = smtp_to
        msg["Subject"] = f"[PlantApp Contact] {subject}"
        body = f"From: {name} <{email}>\n\n{message}"
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, smtp_to, msg.as_string())
            
        logger.info("Contact email sent from %s", email)
        return True
    except Exception as exc:
        logger.warning("SMTP send failed: %s", exc)
        return False
