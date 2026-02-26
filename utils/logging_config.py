"""
utils/logging_config.py — Centralised logging setup for Plant Disease Detection app

Usage:
    from utils.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Model loaded successfully")
    logger.error("Inference failed", exc_info=True)
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Console + rotating-file format
_FMT  = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
_DATE = "%Y-%m-%d %H:%M:%S"


def _setup_root_logger() -> None:
    """Configure the root logger once, called at module import."""
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    root.setLevel(logging.DEBUG)

    # ── Rotating file handler (10 MB × 5 backups) ─────────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FMT, _DATE))

    # ── Console handler (INFO+ only) ──────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(_FMT, _DATE))

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    # Silence noisy third-party loggers
    for noisy in ("PIL", "urllib3", "torch", "timm", "matplotlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


_setup_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call this at module level in any file."""
    return logging.getLogger(name)
