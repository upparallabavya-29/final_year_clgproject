"""
utils/image_utils.py — Image quality validator using OpenCV
"""

def check_image_quality(pil_image, blur_threshold=80.0):
    """
    Check if an image is sharp enough for reliable model inference.

    Uses the Laplacian variance method:
    - High variance = sharp image (lots of edges)
    - Low variance = blurry image (few distinct edges)

    Args:
        pil_image: PIL Image object
        blur_threshold: float — images below this are considered blurry

    Returns:
        (is_ok: bool, variance: float, message: str)
    """
    try:
        import cv2
        import numpy as np

        img_array = np.array(pil_image.convert("L"))   # convert to grayscale
        laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
        variance = laplacian.var()

        if variance < blur_threshold:
            return False, variance, f"Image appears blurry (sharpness score: {variance:.1f}). For best results, retake in good lighting with a steady hand."
        else:
            return True, variance, f"Image quality OK (sharpness score: {variance:.1f})"

    except ImportError:
        # If OpenCV is not yet installed, skip the check gracefully
        return True, -1, "Quality check unavailable (opencv not installed)"
    except Exception as e:
        return True, -1, f"Quality check skipped: {e}"
