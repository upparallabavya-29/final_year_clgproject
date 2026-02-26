"""
Tests for the disease information database in app.py.
Run: python -m pytest tests/ -v
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Import helpers from app (import just the data, not the Streamlit parts) ──
def _load_app_data():
    """Load CLASS_NAMES and DISEASE_INFO without triggering st.set_page_config."""
    import importlib, types

    # Stub out streamlit so the module-level st calls don't fail in tests
    st_stub = types.ModuleType("streamlit")
    for attr in [
        "set_page_config", "markdown", "session_state", "sidebar",
        "cache_resource", "error", "warning", "info", "success",
        "metric", "progress", "columns", "tabs", "radio", "checkbox",
        "selectbox", "text_input", "text_area", "form_submit_button",
        "form", "file_uploader", "camera_input", "button", "spinner",
        "balloons", "dataframe", "download_button", "rerun", "caption",
        "plotly_chart", "image", "expander", "write",
    ]:
        setattr(st_stub, attr, lambda *a, **kw: None)
    st_stub.session_state = {}
    sys.modules.setdefault("streamlit", st_stub)

    # Also stub torch/timm to avoid heavy imports
    for mod in ("torch", "timm", "torchvision", "torchvision.transforms",
                "torch.nn", "torch.nn.functional"):
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)

    # Now parse the CLASS_NAMES and DISEASE_INFO from the source file directly
    import ast
    src = open(os.path.join(os.path.dirname(__file__), "..", "app.py"), encoding="utf-8").read()
    tree = ast.parse(src)

    class_names = None
    disease_info = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "CLASS_NAMES" and class_names is None:
                        class_names = ast.literal_eval(node.value)
                    elif target.id == "DISEASE_INFO" and disease_info is None:
                        disease_info = ast.literal_eval(node.value)
    return class_names, disease_info


CLASS_NAMES, DISEASE_INFO = _load_app_data()


# ─────────────────────────────────────────────────────────────────────────────
class TestClassNames:
    def test_has_38_classes(self):
        assert len(CLASS_NAMES) == 38, f"Expected 38, got {len(CLASS_NAMES)}"

    def test_no_duplicates(self):
        assert len(set(CLASS_NAMES)) == len(CLASS_NAMES), "Duplicate class names found"

    def test_format_consistent(self):
        for c in CLASS_NAMES:
            assert "___" in c, f"Missing '___' separator in: {c}"

    def test_known_classes_present(self):
        required = [
            "Tomato___Late_blight", "Apple___Apple_scab",
            "Potato___Early_blight", "Corn_(maize)___Common_rust_",
            "Tomato___healthy", "Apple___healthy",
        ]
        for r in required:
            assert r in CLASS_NAMES, f"Missing class: {r}"


class TestDiseaseInfoDatabase:
    def test_all_38_classes_have_entries(self):
        missing = [c for c in CLASS_NAMES if c not in DISEASE_INFO]
        assert not missing, f"Missing DISEASE_INFO entries for: {missing}"

    def test_all_entries_have_required_keys(self):
        required_keys = {"crop", "disease", "cause", "treatment", "severity"}
        for cls, info in DISEASE_INFO.items():
            missing = required_keys - set(info.keys())
            assert not missing, f"{cls} is missing keys: {missing}"

    def test_cause_and_treatment_are_non_empty_lists(self):
        for cls, info in DISEASE_INFO.items():
            assert isinstance(info["cause"], list) and len(info["cause"]) > 0, \
                f"{cls}: 'cause' must be a non-empty list"
            assert isinstance(info["treatment"], list) and len(info["treatment"]) > 0, \
                f"{cls}: 'treatment' must be a non-empty list"

    def test_severity_values_valid(self):
        valid = {"none", "medium", "high", "critical"}
        for cls, info in DISEASE_INFO.items():
            assert info["severity"] in valid, \
                f"{cls}: invalid severity '{info['severity']}'"

    def test_healthy_classes_have_none_severity(self):
        healthy = [c for c in CLASS_NAMES if c.endswith("___healthy")]
        for c in healthy:
            sev = DISEASE_INFO[c]["severity"]
            assert sev == "none", f"{c}: healthy class should have severity='none', got '{sev}'"

    def test_no_placeholder_text(self):
        """Ensure no entries still have the generic fallback placeholder text."""
        bad_phrases = ["being researched", "may involve fungal", "extension expert"]
        for cls, info in DISEASE_INFO.items():
            for text_list in (info.get("cause", []), info.get("treatment", [])):
                for text in text_list:
                    for phrase in bad_phrases:
                        assert phrase not in text, \
                            f"{cls} contains placeholder text: '{phrase}'"


class TestNormalization:
    def test_inference_transform_uses_imagenet_mean(self):
        src = open(os.path.join(os.path.dirname(__file__), "..", "app.py"), encoding="utf-8").read()
        assert "0.485" in src, "Inference transform must use ImageNet mean 0.485"
        assert "0.456" in src, "Inference transform must use ImageNet mean 0.456"
        assert "0.406" in src, "Inference transform must use ImageNet mean 0.406"
        # Ensure the wrong normalization is gone
        wrong = "[0.5, 0.5, 0.5]"
        assert wrong not in src, f"Found incorrect normalization: {wrong}"
