"""
pages/contact.py — Contact form.

Messages are saved to the SQLite 'contacts' table (no race-condition JSON file).
SMTP email is sent if SMTP_USER + SMTP_PASS env vars are configured.
Basic input sanitisation applied.
"""

from __future__ import annotations
import logging
import os
import re
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

logger = logging.getLogger(__name__)

_MAX_MSG_LEN  = 2000
_MAX_NAME_LEN = 100
_EMAIL_RE     = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate(name: str, email: str, message: str) -> str | None:
    """Return error string or None if valid."""
    if not name.strip():
        return "Name is required."
    if len(name) > _MAX_NAME_LEN:
        return f"Name must be under {_MAX_NAME_LEN} characters."
    if not _EMAIL_RE.match(email.strip()):
        return "Please enter a valid email address."
    if not message.strip():
        return "Message is required."
    if len(message) > _MAX_MSG_LEN:
        return f"Message must be under {_MAX_MSG_LEN} characters."
    return None


def _try_send_email(name: str, email: str, subject: str, message: str) -> bool:
    """Send via Gmail SMTP if credentials configured. Returns True on success."""
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()
    smtp_to   = os.getenv("SMTP_TO", smtp_user).strip()

    if not smtp_user or not smtp_pass:
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


def render() -> None:
    from utils.database import save_contact

    st.markdown("<h1 style='color:#1b4332;'>✉️ Contact Us</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.markdown("""
<div class="card">
  <h3 style="color:#1b4332;">Contact Information</h3>
  <p>📧 &nbsp;<strong>info@plantdisease.com</strong></p>
  <p>🕐 &nbsp;Mon – Fri: 9:00 AM – 6:00 PM (IST)</p>
  <p>🌐 &nbsp;www.plantdisease.com</p>
  <hr>
  <p style="color:#888;font-size:0.9rem;">
    This app is an academic project. For agricultural emergencies,
    contact your local Krishi Vigyan Kendra (KVK) or agricultural extension office.
  </p>
</div>
""", unsafe_allow_html=True)

    with c2:
        with st.form("contact_form", clear_on_submit=True):
            name    = st.text_input("Full Name",      max_chars=_MAX_NAME_LEN)
            email   = st.text_input("Email Address")
            subject = st.text_input("Subject",        max_chars=150)
            message = st.text_area("Message", height=140,
                                   max_chars=_MAX_MSG_LEN,
                                   placeholder="Describe your issue or query…")
            submitted = st.form_submit_button("📨 Send Message", use_container_width=True)

        if submitted:
            err = _validate(name, email, message)
            if err:
                st.error(err)
                return

            # Persist to SQLite (always)
            try:
                save_contact({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name":    name.strip(),
                    "email":   email.strip(),
                    "subject": subject.strip(),
                    "message": message.strip(),
                })
            except Exception as exc:
                logger.error("Save contact failed: %s", exc, exc_info=True)
                st.error("Could not save your message. Please try again.")
                return

            # Optionally send email
            sent = _try_send_email(name, email, subject, message)
            if sent:
                st.success("✅ Message sent! We'll reply within 24 hours.")
            else:
                st.success("✅ Your message has been saved. We'll get back to you soon.")
