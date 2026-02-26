"""
pages/home.py — Home / landing page for CropGuard AI.
"""

from __future__ import annotations
import json
import os

import streamlit as st

from core.i18n import t


def _load_real_accuracy() -> str | None:
    """Read actual model accuracy from evaluate.py output if it exists."""
    for fname in ("eval_results/eval_vit.json", "eval_results/eval_swin.json"):
        if os.path.isfile(fname):
            try:
                with open(fname) as f:
                    data = json.load(f)
                acc = data.get("metrics", {}).get("accuracy")
                if acc is not None:
                    return f"{float(acc) * 100:.2f}%"
            except Exception:
                pass
    return None


def render() -> None:
    st.markdown("""
<div id="home" style="text-align:center;padding:4rem 2rem 2rem;">
  <h1 style="font-size:3.5rem;font-weight:800;color:#1b4332;">Protect Your Crops with AI</h1>
  <p style="font-size:1.25rem;color:#555;max-width:800px;margin:0 auto 2rem;line-height:1.6;">
    Early detection is key to healthy harvests. Upload a photo of your plant leaf and get
    an instant AI-powered disease diagnosis with treatment recommendations.
  </p>
</div>
""", unsafe_allow_html=True)

    accuracy_display = _load_real_accuracy() or "Train model to see accuracy"
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
<div class="card" style="border-top:5px solid #2ecc71;text-align:center;">
  <div style="font-size:3rem;">🌿</div>
  <h3>38 Disease Classes</h3>
  <p style="color:#666;">Covers Apple, Tomato, Corn, Potato, Grape, Cherry, Peach and more.</p>
  <div style="background:#dcfce7;color:#166534;padding:6px 12px;border-radius:50px;display:inline-block;font-weight:600;">{accuracy_display}</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
<div class="card" style="border-top:5px solid #3b82f6;text-align:center;">
  <div style="font-size:3rem;">⚡</div>
  <h3>Results in &lt; 3 sec</h3>
  <p style="color:#666;">Transformer-based Vision AI — ViT and Swin — for superior accuracy.</p>
  <div style="background:#dbeafe;color:#1e40af;padding:6px 12px;border-radius:50px;display:inline-block;font-weight:600;">Two AI Models</div>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
<div class="card" style="border-top:5px solid #f59e0b;text-align:center;">
  <div style="font-size:3rem;">📋</div>
  <h3>Full Treatment Plans</h3>
  <p style="color:#666;">Cause, severity badge, recommendations and downloadable PDF report.</p>
  <div style="background:#fef3c7;color:#92400e;padding:6px 12px;border-radius:50px;display:inline-block;font-weight:600;">PDF Export</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div id="about" style="padding:2rem;background:rgba(255,255,255,0.9);border-radius:20px;margin-top:1rem;">
  <h2 style="text-align:center;color:#1b4332;">About This Application</h2>
  <p style="color:#555;font-size:1.05rem;line-height:1.8;max-width:900px;margin:0 auto;">
    This application uses state-of-the-art <strong>Vision Transformers (ViT)</strong> and
    <strong>Swin Transformers</strong> — attention-based deep learning architectures — trained
    on the <strong>PlantVillage dataset</strong> (87,000+ images, 38 disease classes, 14 crop species).
    Unlike CNNs, Transformers capture global context across the entire leaf image, enabling
    superior detection of subtle symptoms even in complex field conditions.
  </p>
</div>
""", unsafe_allow_html=True)
