"""
pages/encyclopedia.py — Disease encyclopedia with filters and search.
"""

from __future__ import annotations
import streamlit as st

from core.inference import CLASS_NAMES
from core.disease_info import DISEASE_INFO, SEVERITY_CONFIG, get_disease_info


def render() -> None:
    st.markdown("<h1 style='color:#1b4332;'>📚 Disease Encyclopedia</h1>", unsafe_allow_html=True)
    st.markdown(
        f"Browse all **{len(CLASS_NAMES)}** plant disease and healthy classes. "
        "No image upload required."
    )

    # Filter controls
    all_crops = sorted({get_disease_info(c)["crop"] for c in CLASS_NAMES})
    fc1, fc2, fc3 = st.columns([2, 2, 2])
    crop_filter = fc1.selectbox("Filter by Crop", ["All Crops"] + all_crops)
    sev_filter  = fc2.selectbox(
        "Filter by Severity",
        ["All"] + [s.title() for s in ["none", "medium", "high", "critical"]],
    )
    search_q = fc3.text_input("🔍 Search Disease Name", placeholder="e.g. blight")

    filtered = list(CLASS_NAMES)
    if crop_filter != "All Crops":
        filtered = [c for c in filtered if get_disease_info(c)["crop"] == crop_filter]
    if sev_filter != "All":
        filtered = [c for c in filtered
                    if get_disease_info(c).get("severity", "").lower() == sev_filter.lower()]
    if search_q:
        filtered = [c for c in filtered
                    if search_q.lower() in get_disease_info(c)["disease"].lower()]

    st.markdown(f"**Showing {len(filtered)} of {len(CLASS_NAMES)} classes**")
    st.markdown("---")

    for cls in filtered:
        info = get_disease_info(cls)
        sev  = SEVERITY_CONFIG.get(info.get("severity", "medium"), SEVERITY_CONFIG["medium"])
        with st.expander(
            f"{sev['label']} &nbsp;&nbsp; **{info['crop']}** — *{info['disease']}*",
            expanded=False,
        ):
            e1, e2 = st.columns(2)
            with e1:
                st.markdown("**Cause:**")
                for c in info["cause"]:
                    st.markdown(f"- {c}")
            with e2:
                st.markdown("**Treatment:**")
                for tx in info["treatment"]:
                    st.markdown(f"- {tx}")
