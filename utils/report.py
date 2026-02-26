"""
utils/report.py — PDF report generator for Plant Disease Detection app
"""
import io
from datetime import datetime


def generate_pdf_report(image_pil, info, confidence, model_name, top3=None):
    """
    Generate a PDF report for a single disease detection result.

    Args:
        image_pil: PIL Image object
        info: dict with keys crop, disease, cause (list), treatment (list)
        confidence: float (0–100)
        model_name: str ("vit" or "swin")
        top3: list of (class_name, prob) tuples for top-3 predictions

    Returns:
        bytes: PDF file content
    """
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ─── Header ────────────────────────────────────────────────────────────────
    pdf.set_fill_color(27, 67, 50)          # dark green
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(10, 8)
    pdf.cell(0, 14, "Plant Disease Detection Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(10, 20)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}   |   Model: {model_name.upper()}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # ─── Uploaded image (thumbnail) ────────────────────────────────────────────
    try:
        img_buf = io.BytesIO()
        img_thumb = image_pil.copy()
        img_thumb.thumbnail((120, 120))
        img_thumb.save(img_buf, format="JPEG")
        img_buf.seek(0)
        # save temp
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.write(img_buf.read())
        tmp.close()
        pdf.image(tmp.name, x=10, y=pdf.get_y(), w=60)
        img_y_start = pdf.get_y()
        pdf.set_xy(80, img_y_start)
        os.unlink(tmp.name)
    except Exception:
        img_y_start = pdf.get_y()
        pdf.set_xy(80, img_y_start)

    # ─── Disease Summary Box ───────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"{info['crop']} — {info['disease']}", ln=True)
    pdf.set_font("Helvetica", "", 11)
    severity = "High Confidence" if confidence >= 90 else "Moderate Confidence" if confidence >= 60 else "Low Confidence"
    pdf.set_text_color(46, 204, 113) if confidence >= 90 else pdf.set_text_color(230, 126, 34) if confidence >= 60 else pdf.set_text_color(231, 76, 60)
    pdf.cell(0, 8, f"Confidence: {confidence:.1f}%  ({severity})", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(40)  # space for image

    # ─── Top 3 Predictions ────────────────────────────────────────────────────
    if top3:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Top-3 Alternative Predictions:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for i, (cls, prob) in enumerate(top3):
            pdf.cell(0, 6, f"  {i+1}. {cls.replace('___', ' — ').replace('_', ' ')}  ({prob*100:.1f}%)", ln=True)
        pdf.ln(5)

    # ─── Cause Section ────────────────────────────────────────────────────────
    pdf.set_fill_color(240, 253, 244)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Cause of Disease:", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    for cause in info.get("cause", []):
        pdf.multi_cell(0, 6, f"  • {cause}")
    pdf.ln(4)

    # ─── Treatment Section ────────────────────────────────────────────────────
    pdf.set_fill_color(232, 244, 253)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Recommended Treatment:", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    for treatment in info.get("treatment", []):
        pdf.multi_cell(0, 6, f"  • {treatment}")
    pdf.ln(6)

    # ─── Footer ───────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5, "Disclaimer: This report is AI-generated. Consult a certified agronomist before applying treatments.")

    return bytes(pdf.output())
