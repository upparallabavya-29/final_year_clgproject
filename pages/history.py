"""
pages/history.py — Scan history page with pagination and CSV export.
"""

from __future__ import annotations
import logging

import pandas as pd
import streamlit as st

from core.i18n import t

logger = logging.getLogger(__name__)

PAGE_SIZE = 50   # rows per page


def render() -> None:
    from utils.database import get_all_scans, get_stats, clear_all_scans

    st.markdown("<h1 style='color:#1b4332;'>📋 Scan History</h1>", unsafe_allow_html=True)
    st.markdown("All plant disease detections recorded here — persists across refreshes.")

    try:
        rows = get_all_scans(limit=5000)
    except Exception as exc:
        logger.error("History load failed: %s", exc, exc_info=True)
        st.error("Could not load history from database.")
        return

    if not rows:
        st.info(t("history_empty"))
        return

    df = pd.DataFrame(rows)
    total = len(df)

    # Summary KPIs
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric(t("total_scans"), total)
    mc2.metric("Unique Crops", df["crop"].nunique())
    mc3.metric(t("avg_confidence"), f"{df['confidence'].mean():.1f}%")
    healthy_pct = (df["disease"] == "Healthy").sum() / total * 100
    mc4.metric(t("healthy_rate"), f"{healthy_pct:.0f}%")

    st.markdown("---")

    # Pagination
    n_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if n_pages > 1:
        page_num = st.number_input(
            f"Page (1–{n_pages})", min_value=1, max_value=n_pages, value=1, step=1
        )
    else:
        page_num = 1

    start = (page_num - 1) * PAGE_SIZE
    end   = start + PAGE_SIZE
    page_df = df.iloc[start:end].copy()
    page_df.index = range(start + 1, start + len(page_df) + 1)

    st.caption(f"Showing rows {start+1}–{min(end, total)} of {total}")
    st.dataframe(page_df, use_container_width=True)

    # Export full CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        f"📥 {t('export_csv')}", csv, "scan_history.csv", "text/csv",
        use_container_width=True,
    )

    # Clear history
    if st.button(f"🗑️ {t('clear_history')}"):
        try:
            clear_all_scans()
            st.success("History cleared.")
            st.rerun()
        except Exception as exc:
            logger.error("Clear history failed: %s", exc)
            st.error("Failed to clear history.")
