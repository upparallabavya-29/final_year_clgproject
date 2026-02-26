"""
pages/detection.py — Plant disease detection page (upload / camera / batch).

Features:
  - Single image detection with ViT or Swin
  - Side-by-side model comparison
  - Batch processing with CSV export
  - Per-session scan rate limiting (20 scans/session)
  - Image quality check before inference
  - Grad-CAM heatmap (optional)
  - PDF report download
  - Feedback thumbs-up / thumbs-down persisted to SQLite
"""

from __future__ import annotations
import time
import logging
from datetime import datetime

import streamlit as st
from PIL import Image

from core.i18n import t
from core.inference import CLASS_NAMES, load_model, run_inference
from core.disease_info import get_disease_info, SEVERITY_CONFIG

logger = logging.getLogger(__name__)

MAX_UPLOAD_MB    = 10
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
MAX_SCANS_PER_SESSION = 20   # rate limit per browser session

_MODEL_OPTIONS = {"vit": "Vision Transformer (ViT)", "swin": "Swin Transformer"}


# ── Rate limiter ───────────────────────────────────────────────────────────────

def _check_rate_limit() -> bool:
    """Return True if user is within session limit."""
    count = st.session_state.get("session_scan_count", 0)
    if count >= MAX_SCANS_PER_SESSION:
        st.error(
            f"🚦 Session limit reached ({MAX_SCANS_PER_SESSION} scans). "
            "Refresh the page to start a new session."
        )
        return False
    return True


def _increment_scan_count() -> None:
    st.session_state["session_scan_count"] = (
        st.session_state.get("session_scan_count", 0) + 1
    )


# ── Image quality check ────────────────────────────────────────────────────────

def _check_quality(image: Image.Image) -> None:
    """Warn if image is blurry (non-blocking)."""
    try:
        from utils.image_utils import check_image_quality
        ok, _, msg = check_image_quality(image)
        if not ok:
            st.warning(f"⚠️ {msg}")
    except Exception:
        pass


# ── Result display ─────────────────────────────────────────────────────────────

def display_result(
    image_pil: Image.Image,
    pred_idx: int,
    confidence: float,
    top3: list,
    model_choice: str,
    *,
    show_pdf: bool = True,
    inference_ms: float = 0.0,
    filename: str = "",
) -> None:
    from utils.database import insert_scan, insert_feedback

    class_name = CLASS_NAMES[pred_idx]
    info = get_disease_info(class_name)
    sev  = SEVERITY_CONFIG.get(info.get("severity", "medium"), SEVERITY_CONFIG["medium"])

    logger.info(
        "Result: %s | conf=%.1f%% | model=%s | %.0fms",
        class_name, confidence, model_choice, inference_ms,
    )

    # Timing badge
    if inference_ms > 0:
        st.markdown(
            f'<span class="timing-badge">⏱️ {inference_ms:.0f} ms inference</span>',
            unsafe_allow_html=True,
        )

    # Confidence gauge
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence,
            number={"suffix": "%", "font": {"size": 28}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar":  {"color": sev["color"]},
                "steps": [
                    {"range": [0,  60], "color": "#fee2e2"},
                    {"range": [60, 90], "color": "#fef3c7"},
                    {"range": [90, 100], "color": "#dcfce7"},
                ],
            },
            title={"text": t("confidence_label")},
        ))
        fig.update_layout(
            height=220,
            margin=dict(t=40, b=0, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.metric(t("confidence_label"), f"{confidence:.1f}%")

    # Severity badge
    st.markdown(
        f'<div style="display:inline-block;background:{sev["bg"]};color:{sev["color"]};'
        f'padding:6px 16px;border-radius:50px;font-weight:700;margin-bottom:12px;">'
        f'{sev["label"]}</div>',
        unsafe_allow_html=True,
    )

    # Analysis card
    st.markdown(f"""
<div class="card" style="border-left:5px solid {sev['color']};">
  <h4 style="margin-top:0;color:{sev['color']};">📋 Analysis Result</h4>
  <p><strong>Crop:</strong> {info['crop']}</p>
  <p><strong>Disease:</strong> {info['disease']}</p>
  <p><strong>Cause:</strong><br>{'<br>'.join(f"• {c}" for c in info['cause'])}</p>
</div>
""", unsafe_allow_html=True)

    # Top-3 predictions
    st.markdown(f"#### 🔢 {t('top3_label')}")
    medals = ["🥇", "🥈", "🥉"]
    for i, (cls, prob) in enumerate(top3):
        label = cls.replace("___", " — ").replace("_", " ")
        medal = medals[i] if i < len(medals) else f"{i+1}."
        st.progress(float(prob), text=f"{medal} {label}: {prob*100:.1f}%")

    # Treatment card
    st.markdown(f"""
<div class="card" style="border-left:5px solid #16a34a;margin-top:16px;">
  <h4 style="color:#16a34a;margin-top:0;">💊 {t('treatment_label')}</h4>
  <ul style="padding-left:20px;line-height:1.9;">
    {''.join(f"<li>{tx}</li>" for tx in info['treatment'])}
  </ul>
</div>
""", unsafe_allow_html=True)

    # Grad-CAM
    with st.expander("🔬 Show AI Heatmap (Grad-CAM)", expanded=False):
        st.caption("Highlights leaf regions that influenced the prediction.")
        if st.button("Generate Heatmap", key=f"gcam_{pred_idx}_{model_choice}_{id(image_pil)}"):
            with st.spinner("Generating Grad-CAM…"):
                try:
                    from utils.gradcam import generate_gradcam
                    mdl, err = load_model(model_choice)
                    if mdl:
                        hm = generate_gradcam(mdl, image_pil, pred_idx)
                        if hm:
                            _c1, _c2 = st.columns(2)
                            _c1.image(image_pil, caption="Original", use_column_width=True)
                            _c2.image(hm, caption="Grad-CAM", use_column_width=True)
                        else:
                            st.info("Install grad-cam: `pip install grad-cam`")
                except Exception as exc:
                    logger.error("GradCAM error: %s", exc, exc_info=True)
                    st.warning("Heatmap failed — see logs.")

    # PDF download
    if show_pdf:
        try:
            from utils.report import generate_pdf_report
            pdf_bytes = generate_pdf_report(image_pil, info, confidence, model_choice, top3)
            if pdf_bytes:
                st.download_button(
                    f"📥 {t('download_pdf')}",
                    data=pdf_bytes,
                    file_name=f"plant_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as exc:
            logger.error("PDF generation failed: %s", exc, exc_info=True)

    # Persist to SQLite
    scan_id = None
    record = {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crop":         info["crop"],
        "disease":      info["disease"],
        "confidence":   round(confidence, 1),
        "severity":     info.get("severity", "medium"),
        "model":        model_choice.upper(),
        "filename":     filename,
        "inference_ms": round(inference_ms, 1),
    }
    try:
        scan_id = insert_scan(record)
        _increment_scan_count()
    except Exception as exc:
        logger.error("DB insert failed: %s", exc, exc_info=True)

    # Feedback buttons
    if scan_id:
        st.markdown(f"---\n**{t('feedback_q')}**")
        fc1, fc2, _ = st.columns([1, 1, 4])
        with fc1:
            if st.button(f"👍 {t('feedback_yes')}", key=f"fb_yes_{scan_id}"):
                try:
                    insert_feedback(scan_id, was_correct=True)
                    st.success(t("feedback_thanks"))
                except Exception as exc:
                    logger.error("Feedback failed: %s", exc)
        with fc2:
            if st.button(f"👎 {t('feedback_no')}", key=f"fb_no_{scan_id}"):
                try:
                    insert_feedback(scan_id, was_correct=False)
                    st.success(t("feedback_thanks"))
                except Exception as exc:
                    logger.error("Feedback failed: %s", exc)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _infer_and_show(
    image: Image.Image,
    model_choice: str,
    *,
    show_pdf: bool = True,
    filename: str = "",
) -> None:
    model_path = f"checkpoints/best_model_{model_choice}.pth"
    import os
    if not os.path.isfile(model_path):
        st.warning(
            f"⚠️ **{_MODEL_OPTIONS[model_choice]}** checkpoint not found.\n\n"
            f"Run: `python train.py --model {model_choice}` to train, or\n"
            f"`python tools/create_placeholders.py` for a smoke-test placeholder."
        )
        return

    if not st.button(
        f"🔍 Analyse with {_MODEL_OPTIONS[model_choice]}",
        use_container_width=True,
        key=f"btn_{model_choice}_{id(image)}",
    ):
        return

    if not _check_rate_limit():
        return

    with st.spinner("Loading model…"):
        model, err = load_model(model_choice)

    if err:
        st.error(f"Model failed to load: {err}")
        logger.error("load_model('%s') error: %s", model_choice, err)
        return

    t0 = time.perf_counter()
    pred_idx, confidence, top3 = run_inference(model, image)
    ms = (time.perf_counter() - t0) * 1000
    st.balloons()
    display_result(
        image, pred_idx, confidence, top3, model_choice,
        show_pdf=show_pdf, inference_ms=ms, filename=filename,
    )


def _run_single(
    image: Image.Image,
    model_choice: str,
    compare_mode: bool,
    filename: str = "",
) -> None:
    col_img, col_res = st.columns([1, 1], gap="large")
    with col_img:
        st.image(image, caption="Uploaded Image", use_container_width=True)
        _check_quality(image)

    with col_res:
        if not compare_mode:
            _infer_and_show(image, model_choice, filename=filename)
        else:
            st.markdown("#### ViT vs Swin Comparison")
            c_vit, c_swin = st.columns(2)
            with c_vit:
                st.markdown("**Vision Transformer (ViT)**")
                _infer_and_show(image, "vit", show_pdf=False, filename=filename)
            with c_swin:
                st.markdown("**Swin Transformer**")
                _infer_and_show(image, "swin", show_pdf=False, filename=filename)


def _run_batch(batch_files: list, model_choice: str) -> None:
    import os, pandas as pd
    from utils.database import insert_scan

    model_path = f"checkpoints/best_model_{model_choice}.pth"
    if not os.path.isfile(model_path):
        st.warning(f"⚠️ Checkpoint not found: `{model_path}`")
        return

    if not st.button("🚀 Run Batch Analysis", use_container_width=True):
        return

    if not _check_rate_limit():
        return

    with st.spinner("Loading model…"):
        model, err = load_model(model_choice)
    if err:
        st.error(f"Model failed to load: {err}")
        return

    results = []
    prog = st.progress(0)
    for i, f in enumerate(batch_files):
        try:
            img = Image.open(f).convert("RGB")
            pred_idx, confidence, top3 = run_inference(model, img)
            info = get_disease_info(CLASS_NAMES[pred_idx])
            results.append({
                "File":       f.name,
                "Crop":       info["crop"],
                "Disease":    info["disease"],
                "Confidence": f"{confidence:.1f}%",
                "Severity":   info.get("severity", "—").title(),
                "Model":      model_choice.upper(),
            })
            try:
                insert_scan({
                    "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "crop":       info["crop"],
                    "disease":    info["disease"],
                    "confidence": round(confidence, 1),
                    "severity":   info.get("severity", "medium"),
                    "model":      model_choice.upper(),
                    "filename":   f.name,
                })
            except Exception as exc:
                logger.error("Batch DB insert failed for %s: %s", f.name, exc)
        except Exception as exc:
            logger.error("Batch inference failed for %s: %s", f.name, exc)
            results.append({"File": f.name, "Error": str(exc)})

        prog.progress((i + 1) / len(batch_files))

    df = pd.DataFrame(results)
    st.success(f"✅ Processed {len(results)} images.")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Results CSV", csv, "batch_results.csv", "text/csv",
        use_container_width=True,
    )


# ── Page entry point ───────────────────────────────────────────────────────────

def render() -> None:
    with st.sidebar:
        st.markdown("### ⚙️ Model Configuration")
        model_choice = st.selectbox(
            "Select Model Architecture",
            list(_MODEL_OPTIONS.keys()),
            format_func=lambda x: _MODEL_OPTIONS[x],
        )
        compare_mode = st.checkbox("🔬 Compare Both Models Side-by-Side")
        st.markdown("---")
        st.markdown("**Supports:** JPG · PNG · WEBP")
        st.markdown("**Resolution:** 224 × 224 px (auto-resized)")
        st.markdown("**Dataset:** PlantVillage · 87K images")
        scans_done = st.session_state.get("session_scan_count", 0)
        st.caption(f"Session scans: {scans_done} / {MAX_SCANS_PER_SESSION}")

    st.markdown(
        "<h1 style='text-align:center;color:#1b4332;'>🔍 Plant Disease Detection</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;color:#666;'>Upload an image or take a photo of your plant leaf to get an instant AI diagnosis.</p>",
        unsafe_allow_html=True,
    )

    tab_up, tab_cam, tab_batch = st.tabs(
        ["📁 Upload Image", "📷 Take Photo", "📦 Batch Detection"]
    )

    with tab_up:
        uploaded = st.file_uploader(
            "Choose a leaf image",
            type=["jpg", "png", "jpeg", "webp"],
            label_visibility="collapsed",
        )
        if uploaded:
            if uploaded.size > MAX_UPLOAD_BYTES:
                st.error(
                    f"🚫 File too large ({uploaded.size // (1024*1024)} MB). "
                    f"Maximum: {MAX_UPLOAD_MB} MB."
                )
            else:
                image = Image.open(uploaded).convert("RGB")
                _run_single(image, model_choice, compare_mode, filename=uploaded.name)

    with tab_cam:
        camera_img = st.camera_input(t("camera_label"))
        if camera_img:
            image = Image.open(camera_img).convert("RGB")
            _run_single(image, model_choice, compare_mode, filename="camera_capture.jpg")

    with tab_batch:
        st.markdown("Upload multiple leaf images to process them all at once.")
        batch_files = st.file_uploader(
            "Upload multiple images",
            type=["jpg", "png", "jpeg", "webp"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if batch_files:
            _run_batch(batch_files, model_choice)
