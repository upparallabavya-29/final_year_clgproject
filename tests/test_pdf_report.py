"""
Tests for utils/report.py — PDF report generator.
Run: python -m pytest tests/ -v
"""
import sys
import os
import pytest
from PIL import Image
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


SAMPLE_INFO = {
    "crop": "Tomato",
    "disease": "Early Blight",
    "cause": [
        "Caused by Alternaria solani.",
        "Survives in infected crop debris.",
    ],
    "treatment": [
        "Rotate crops; avoid planting tomatoes for 3 years.",
        "Apply chlorothalonil preventively.",
    ],
    "severity": "medium",
}

def _make_test_image(width=224, height=224, color=(80, 160, 80)):
    """Create a solid-color PIL image for testing."""
    img = Image.new("RGB", (width, height), color=color)
    return img


class TestGeneratePdfReport:
    def test_returns_bytes(self):
        pytest.importorskip("fpdf", reason="fpdf2 not installed")
        from utils.report import generate_pdf_report
        img = _make_test_image()
        result = generate_pdf_report(img, SAMPLE_INFO, 87.5, "vit", top3=[
            ("Tomato___Early_blight", 0.875),
            ("Tomato___Late_blight",  0.08),
            ("Tomato___healthy",      0.04),
        ])
        assert isinstance(result, bytes), "PDF output should be bytes"
        assert len(result) > 1000, "PDF should have non-trivial content"

    def test_pdf_starts_with_header(self):
        pytest.importorskip("fpdf", reason="fpdf2 not installed")
        from utils.report import generate_pdf_report
        img = _make_test_image()
        result = generate_pdf_report(img, SAMPLE_INFO, 92.0, "swin")
        assert result is not None
        # PDF binary files start with %PDF
        assert result[:4] == b"%PDF", "Output is not a valid PDF"

    def test_healthy_disease(self):
        """PDF should be generated for healthy plants too."""
        pytest.importorskip("fpdf", reason="fpdf2 not installed")
        from utils.report import generate_pdf_report
        healthy_info = {
            "crop": "Apple", "disease": "Healthy",
            "cause": ["No disease detected."],
            "treatment": ["Continue normal care."],
            "severity": "none",
        }
        img = _make_test_image(color=(50, 200, 50))
        result = generate_pdf_report(img, healthy_info, 98.1, "vit")
        assert isinstance(result, bytes) and len(result) > 500

    def test_graceful_without_fpdf(self, monkeypatch):
        """Should return None when fpdf2 is not installed."""
        import builtins
        real_import = builtins.__import__
        def mock_import(name, *args, **kwargs):
            if name in ("fpdf", "fpdf2"):
                raise ImportError("mocked missing fpdf")
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, "__import__", mock_import)

        from utils import report as rmod
        import importlib
        importlib.reload(rmod)
        result = rmod.generate_pdf_report(_make_test_image(), SAMPLE_INFO, 80.0, "vit")
        assert result is None


class TestImageQualityCheck:
    def test_sharp_image_passes(self):
        from utils.image_utils import check_image_quality
        # Create a high-contrast image (lots of edges)
        from PIL import ImageDraw
        img = Image.new("RGB", (200, 200), "white")
        draw = ImageDraw.Draw(img)
        for i in range(0, 200, 5):
            draw.line([(0, i), (200, i)], fill="black", width=1)
        ok, var, msg = check_image_quality(img)
        assert ok, f"Sharp image should pass: {msg}"

    def test_blurry_image_flagged(self):
        from utils.image_utils import check_image_quality
        # Solid color = no edges = Laplacian variance ≈ 0
        img = Image.new("RGB", (200, 200), color=(120, 180, 120))
        ok, var, msg = check_image_quality(img)
        # Solid image has near-zero variance — should fail
        assert not ok, f"Solid-color image should be flagged as blurry"
