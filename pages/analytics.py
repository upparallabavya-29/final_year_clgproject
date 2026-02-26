"""
pages/analytics.py — Analytics dashboard with real SQLite data.
"""

from __future__ import annotations
import logging

import streamlit as st

logger = logging.getLogger(__name__)


def render() -> None:
    st.markdown("<h1 style='color:#1b4332;'>📊 Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("Aggregate statistics from all recorded scans across all sessions.")

    try:
        from utils.database import get_stats
        stats = get_stats()
    except Exception as exc:
        logger.error("Dashboard stats failed: %s", exc, exc_info=True)
        st.error("Could not load analytics. Check logs.")
        return

    if stats.get("total", 0) == 0:
        st.info("No scan data yet — analyse some plant images first, then come back here.")
        return

    try:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        st.error("Install plotly: `pip install plotly`")
        return

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Total Scans",     stats["total"])
    k2.metric("💯 Avg Confidence",  f"{stats['avg_confidence']}%")
    k3.metric("🌿 Healthy Plants",  f"{stats['healthy_pct']}%")
    fb_acc = stats.get("feedback_accuracy")
    k4.metric("👍 Feedback Accuracy", f"{fb_acc}%" if fb_acc is not None else "No feedback yet")

    st.markdown("---")
    c_left, c_right = st.columns(2)

    # Top diseases bar chart
    with c_left:
        st.markdown("#### Most Detected Diseases")
        top_d = stats.get("top_diseases", [])
        if top_d:
            df_d = pd.DataFrame(top_d)
            fig = px.bar(
                df_d, x="count", y="disease", orientation="h",
                color="count", color_continuous_scale="Greens",
                labels={"count": "Scans", "disease": "Disease"},
            )
            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=320,
            )
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # Severity pie
    with c_right:
        st.markdown("#### Severity Distribution")
        sev_d = stats.get("severity_dist", [])
        if sev_d:
            df_s = pd.DataFrame(sev_d)
            color_map = {
                "critical": "#7c3aed", "high": "#dc2626",
                "medium": "#d97706", "none": "#16a34a",
            }
            fig2 = px.pie(
                df_s, names="severity", values="count",
                color="severity", color_discrete_map=color_map,
                hole=0.45,
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=320,
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Daily scans line chart
    st.markdown("#### Scans per Day (Last 14 Days)")
    daily = stats.get("daily_scans", [])
    if daily:
        df_day = pd.DataFrame(daily).sort_values("day")
        fig3 = px.line(
            df_day, x="day", y="count",
            markers=True, color_discrete_sequence=["#16a34a"],
            labels={"day": "Date", "count": "Scans"},
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=20), height=260,
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Model usage
    mu = stats.get("model_usage", [])
    if mu:
        st.markdown("#### Model Usage")
        for m in mu:
            pct = m["count"] / stats["total"]
            st.progress(float(pct), text=f"{m['model']}: {m['count']} scans ({pct*100:.0f}%)")
