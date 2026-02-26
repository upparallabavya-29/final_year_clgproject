"""
core/i18n.py — Internationalisation helper.

Usage:
    from core.i18n import t
    label = t("confidence_label")
"""

from __future__ import annotations
import json
import os
import streamlit as st

_CACHE: dict[str, dict] = {}


def t(key: str) -> str:
    """Return translated string for the current UI language, falling back to key."""
    lang = st.session_state.get("lang", "en")
    if lang not in _CACHE:
        path = os.path.join("translations", f"{lang}.json")
        try:
            with open(path, encoding="utf-8") as f:
                _CACHE[lang] = json.load(f)
        except Exception:
            _CACHE[lang] = {}
    return _CACHE[lang].get(key, key)


def clear_cache() -> None:
    """Flush translation cache (call when language changes)."""
    _CACHE.clear()
