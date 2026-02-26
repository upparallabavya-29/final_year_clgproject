"""
backend/main.py — FastAPI application factory for CropGuard AI.

Slim entrypoint (~50 lines). All routes live in backend/routes/.
"""
from __future__ import annotations
import sys
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.database import init_db
import utils.logging_config  # noqa: F401

from backend.routes.auth import router as auth_router
from backend.routes.detect import router as detect_router
from backend.routes.history import router as history_router
from backend.routes.encyclopedia import router as encyclopedia_router
from backend.routes.contact import router as contact_router
from backend.dependencies import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


# ── Lifespan (replaces deprecated @app.on_event) ──────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    logger.info("Database initialised.")
    yield
    # Shutdown (cleanup if needed)
    logger.info("Application shutting down.")


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CropGuard AI API",
    description="Plant Disease Detection REST API — ViT & Swin Transformer",
    version="3.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(detect_router)
app.include_router(history_router)
app.include_router(encyclopedia_router)
app.include_router(contact_router)


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["system"])
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "version": "3.0.0"}
