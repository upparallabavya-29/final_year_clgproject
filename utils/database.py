"""
utils/database.py — Production-grade SQLite database for CropGuard AI.

Features:
  - WAL journal mode for safe concurrent reads + writes
  - Per-user scoped queries (no cross-user data leakage)
  - SQL-level pagination with LIMIT/OFFSET (no OOM risk)
  - OTP persistence table (multi-process safe)
  - Thread-safe: one connection per call
"""

from __future__ import annotations
import os
import random
import string
import sqlite3
import time
from datetime import datetime
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scan_history.db")


# ── Connection factory ─────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


# ── Schema ─────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create / migrate tables. Called once at app startup."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = _get_conn()
    try:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                email        TEXT    UNIQUE,
                phone        TEXT    UNIQUE,
                password_hash TEXT   DEFAULT '',
                google_sub   TEXT    UNIQUE,
                name         TEXT    DEFAULT '',
                avatar       TEXT    DEFAULT '',
                provider     TEXT    NOT NULL DEFAULT 'email',
                created_at   TEXT    NOT NULL,
                last_login   TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS scans (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
                timestamp    TEXT    NOT NULL,
                crop         TEXT    NOT NULL,
                disease      TEXT    NOT NULL,
                confidence   REAL    NOT NULL,
                severity     TEXT    NOT NULL DEFAULT 'medium',
                model        TEXT    NOT NULL,
                filename     TEXT    DEFAULT '',
                inference_ms REAL    DEFAULT 0,
                image_path   TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id     INTEGER REFERENCES scans(id) ON DELETE CASCADE,
                timestamp   TEXT    NOT NULL,
                was_correct INTEGER NOT NULL DEFAULT -1,
                comment     TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS contacts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name      TEXT NOT NULL,
                email     TEXT NOT NULL,
                subject   TEXT DEFAULT '',
                message   TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS otp_codes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                phone      TEXT    NOT NULL,
                code       TEXT    NOT NULL,
                expires_at REAL   NOT NULL,
                used       INTEGER NOT NULL DEFAULT 0
            );

            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_users_email      ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_phone      ON users(phone);
            CREATE INDEX IF NOT EXISTS idx_users_google     ON users(google_sub);
            CREATE INDEX IF NOT EXISTS idx_scans_user       ON scans(user_id);
            CREATE INDEX IF NOT EXISTS idx_scans_timestamp  ON scans(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_scans_disease    ON scans(disease);
            CREATE INDEX IF NOT EXISTS idx_scans_crop       ON scans(crop);
            CREATE INDEX IF NOT EXISTS idx_contacts_ts      ON contacts(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_otp_phone        ON otp_codes(phone);
        """)
        con.commit()
    finally:
        con.close()


# ══════════════════════════════════════════════════════════════════════════════
# SCANS — User-scoped, SQL-paginated
# ══════════════════════════════════════════════════════════════════════════════

def insert_scan(record: dict[str, Any]) -> int:
    """Insert one scan record. Returns new row id."""
    con = _get_conn()
    try:
        cur = con.execute(
            """INSERT INTO scans
               (user_id, timestamp, crop, disease, confidence, severity,
                model, filename, inference_ms, image_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.get("user_id"),
                record.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                record.get("crop", ""),
                record.get("disease", ""),
                float(record.get("confidence", 0.0)),
                record.get("severity", "medium"),
                record.get("model", ""),
                record.get("filename", ""),
                float(record.get("inference_ms", 0.0)),
                record.get("image_path", ""),
            ),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def get_user_scans(user_id: int, page: int = 1, page_size: int = 20) -> dict:
    """SQL-paginated, user-scoped scan history."""
    con = _get_conn()
    try:
        total = con.execute(
            "SELECT COUNT(*) FROM scans WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

        offset = (page - 1) * page_size
        rows = con.execute(
            "SELECT * FROM scans WHERE user_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (user_id, page_size, offset),
        ).fetchall()

        return {
            "total":     total,
            "page":      page,
            "page_size": page_size,
            "pages":     max(1, (total + page_size - 1) // page_size),
            "scans":     [dict(r) for r in rows],
        }
    finally:
        con.close()


def get_all_scans(limit: int = 5000) -> list[dict]:
    """Return most recent scans (admin / legacy). Use get_user_scans for user-scoped."""
    con = _get_conn()
    try:
        rows = con.execute(
            "SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def insert_feedback(scan_id: int, was_correct: bool, comment: str = "") -> None:
    con = _get_conn()
    try:
        con.execute(
            "INSERT INTO feedback (scan_id, timestamp, was_correct, comment) VALUES (?, ?, ?, ?)",
            (scan_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), int(was_correct), comment),
        )
        con.commit()
    finally:
        con.close()


def get_user_stats(user_id: int) -> dict:
    """Aggregated stats scoped to a single user."""
    con = _get_conn()
    try:
        total = con.execute(
            "SELECT COUNT(*) FROM scans WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        if total == 0:
            return {"total": 0}

        top_diseases = con.execute(
            "SELECT disease, COUNT(*) AS count FROM scans WHERE user_id = ? "
            "GROUP BY disease ORDER BY count DESC LIMIT 10",
            (user_id,),
        ).fetchall()

        severity_dist = con.execute(
            "SELECT severity, COUNT(*) AS count FROM scans WHERE user_id = ? GROUP BY severity",
            (user_id,),
        ).fetchall()

        model_usage = con.execute(
            "SELECT model, COUNT(*) AS count FROM scans WHERE user_id = ? GROUP BY model",
            (user_id,),
        ).fetchall()

        daily = con.execute(
            "SELECT DATE(timestamp) AS day, COUNT(*) AS count FROM scans WHERE user_id = ? "
            "GROUP BY day ORDER BY day DESC LIMIT 14",
            (user_id,),
        ).fetchall()

        avg_conf = con.execute(
            "SELECT AVG(confidence) FROM scans WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

        healthy = con.execute(
            "SELECT COUNT(*) FROM scans WHERE user_id = ? AND disease = 'Healthy'",
            (user_id,),
        ).fetchone()[0]

        fb = con.execute(
            "SELECT SUM(f.was_correct), COUNT(*) FROM feedback f "
            "JOIN scans s ON s.id = f.scan_id "
            "WHERE s.user_id = ? AND f.was_correct >= 0",
            (user_id,),
        ).fetchone()
        fb_correct = fb[0] or 0
        fb_total   = fb[1] or 0

        return {
            "total":             total,
            "avg_confidence":    round(avg_conf or 0, 1),
            "healthy_count":     healthy,
            "healthy_pct":       round(healthy / total * 100, 1),
            "top_diseases":      [{"disease": r[0], "count": r[1]} for r in top_diseases],
            "severity_dist":     [{"severity": r[0], "count": r[1]} for r in severity_dist],
            "model_usage":       [{"model": r[0], "count": r[1]} for r in model_usage],
            "daily_scans":       [{"day": r[0], "count": r[1]} for r in daily],
            "feedback_accuracy": round(fb_correct / fb_total * 100, 1) if fb_total else None,
        }
    finally:
        con.close()


def get_public_summary() -> dict:
    """Lightweight public stats for landing page — no user scope."""
    con = _get_conn()
    try:
        total_scans = con.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        total_users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return {"total_scans": total_scans, "total_users": total_users}
    finally:
        con.close()


def get_stats() -> dict:
    """Global stats (admin / legacy). Prefer get_user_stats for per-user."""
    con = _get_conn()
    try:
        total = con.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        if total == 0:
            return {"total": 0}

        top_diseases = con.execute(
            "SELECT disease, COUNT(*) AS count FROM scans "
            "GROUP BY disease ORDER BY count DESC LIMIT 10"
        ).fetchall()
        severity_dist = con.execute(
            "SELECT severity, COUNT(*) AS count FROM scans GROUP BY severity"
        ).fetchall()
        model_usage = con.execute(
            "SELECT model, COUNT(*) AS count FROM scans GROUP BY model"
        ).fetchall()
        daily = con.execute(
            "SELECT DATE(timestamp) AS day, COUNT(*) AS count FROM scans "
            "GROUP BY day ORDER BY day DESC LIMIT 14"
        ).fetchall()
        avg_conf = con.execute("SELECT AVG(confidence) FROM scans").fetchone()[0]
        healthy = con.execute(
            "SELECT COUNT(*) FROM scans WHERE disease = 'Healthy'"
        ).fetchone()[0]
        fb = con.execute(
            "SELECT SUM(was_correct), COUNT(*) FROM feedback WHERE was_correct >= 0"
        ).fetchone()
        fb_correct = fb[0] or 0
        fb_total   = fb[1] or 0

        return {
            "total":             total,
            "avg_confidence":    round(avg_conf or 0, 1),
            "healthy_count":     healthy,
            "healthy_pct":       round(healthy / total * 100, 1),
            "top_diseases":      [{"disease": r[0], "count": r[1]} for r in top_diseases],
            "severity_dist":     [{"severity": r[0], "count": r[1]} for r in severity_dist],
            "model_usage":       [{"model": r[0], "count": r[1]} for r in model_usage],
            "daily_scans":       [{"day": r[0], "count": r[1]} for r in daily],
            "feedback_accuracy": round(fb_correct / fb_total * 100, 1) if fb_total else None,
        }
    finally:
        con.close()


def clear_user_scans(user_id: int) -> None:
    """Delete all scans and associated feedback for a specific user."""
    con = _get_conn()
    try:
        con.execute(
            "DELETE FROM feedback WHERE scan_id IN (SELECT id FROM scans WHERE user_id = ?)",
            (user_id,),
        )
        con.execute("DELETE FROM scans WHERE user_id = ?", (user_id,))
        con.commit()
    finally:
        con.close()


def clear_all_scans() -> None:
    """Delete all scan and feedback records (admin only)."""
    con = _get_conn()
    try:
        con.execute("DELETE FROM feedback")
        con.execute("DELETE FROM scans")
        con.commit()
    finally:
        con.close()


# ══════════════════════════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════════════════════════

def save_contact(record: dict[str, Any]) -> int:
    con = _get_conn()
    try:
        cur = con.execute(
            "INSERT INTO contacts (timestamp, name, email, subject, message) VALUES (?, ?, ?, ?, ?)",
            (
                record.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                record.get("name", ""),
                record.get("email", ""),
                record.get("subject", ""),
                record.get("message", ""),
            ),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


# ══════════════════════════════════════════════════════════════════════════════
# USERS
# ══════════════════════════════════════════════════════════════════════════════

def create_user(record: dict[str, Any]) -> int:
    con = _get_conn()
    try:
        cur = con.execute(
            """INSERT INTO users
               (email, phone, password_hash, google_sub, name, avatar, provider, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.get("email"),
                record.get("phone"),
                record.get("password_hash", ""),
                record.get("google_sub"),
                record.get("name", ""),
                record.get("avatar", ""),
                record.get("provider", "email"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def get_user_by_email(email: str) -> dict | None:
    con = _get_conn()
    try:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def get_user_by_phone(phone: str) -> dict | None:
    con = _get_conn()
    try:
        row = con.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def get_user_by_google_sub(sub: str) -> dict | None:
    con = _get_conn()
    try:
        row = con.execute("SELECT * FROM users WHERE google_sub = ?", (sub,)).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def get_user_by_id(user_id: int) -> dict | None:
    con = _get_conn()
    try:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def update_user_last_login(user_id: int) -> None:
    con = _get_conn()
    try:
        con.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )
        con.commit()
    finally:
        con.close()


# ══════════════════════════════════════════════════════════════════════════════
# OTP — Persistent (DB-backed, multi-process safe)
# ══════════════════════════════════════════════════════════════════════════════

def create_otp(phone: str, expire_secs: int = 300) -> str:
    """Generate, persist, and return a 6-digit OTP for the given phone."""
    code = "".join(random.choices(string.digits, k=6))
    expires_at = time.time() + expire_secs
    con = _get_conn()
    try:
        # Invalidate any existing unused OTPs for this phone
        con.execute(
            "UPDATE otp_codes SET used = 1 WHERE phone = ? AND used = 0",
            (phone,),
        )
        con.execute(
            "INSERT INTO otp_codes (phone, code, expires_at, used) VALUES (?, ?, ?, 0)",
            (phone, code, expires_at),
        )
        con.commit()
        return code
    finally:
        con.close()


def verify_otp_db(phone: str, code: str) -> bool:
    """Verify OTP. Consumes it on success. Returns False if expired/invalid."""
    con = _get_conn()
    try:
        row = con.execute(
            "SELECT id, expires_at FROM otp_codes "
            "WHERE phone = ? AND code = ? AND used = 0 "
            "ORDER BY id DESC LIMIT 1",
            (phone, code),
        ).fetchone()

        if not row:
            return False
        if time.time() > row["expires_at"]:
            # Expired — mark as used
            con.execute("UPDATE otp_codes SET used = 1 WHERE id = ?", (row["id"],))
            con.commit()
            return False

        # Valid — consume
        con.execute("UPDATE otp_codes SET used = 1 WHERE id = ?", (row["id"],))
        con.commit()
        return True
    finally:
        con.close()
