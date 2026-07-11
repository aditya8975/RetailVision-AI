"""
Image quality scoring using classic OpenCV metrics -- no ML model needed.

Four signals are combined into a single 0-100 score:
  - Sharpness: variance of the Laplacian (low variance = blurry)
  - Brightness: mean pixel intensity, penalized if too dark/blown out
  - Contrast: standard deviation of pixel intensity
  - Resolution: penalize images below a usable e-commerce size

This mirrors the kind of automated "is this photo good enough to publish"
gate a catalog pipeline like Vue.ai's would run before an image ever
reaches customers.
"""
import cv2
import numpy as np
from PIL import Image

MIN_USABLE_DIMENSION = 400  # px, below this a product photo looks unusably small
IDEAL_MIN_DIMENSION = 1000  # px, at/above this resolution scores full marks


def _to_cv2(image: Image.Image) -> np.ndarray:
    arr = np.array(image.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def score_image_quality(image: Image.Image) -> dict:
    cv_img = _to_cv2(image)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # --- Sharpness ---
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = float(np.clip(laplacian_var / 500.0, 0, 1)) * 100

    # --- Brightness ---
    mean_brightness = float(gray.mean())  # 0-255
    # Best around 110-190; penalize extremes (too dark / blown-out)
    if mean_brightness < 40 or mean_brightness > 235:
        brightness_score = 20.0
    else:
        distance_from_ideal = abs(mean_brightness - 150) / 150
        brightness_score = float(np.clip(1 - distance_from_ideal, 0, 1)) * 100

    # --- Contrast ---
    contrast = float(gray.std())
    contrast_score = float(np.clip(contrast / 60.0, 0, 1)) * 100

    # --- Resolution ---
    min_dim = min(h, w)
    if min_dim <= MIN_USABLE_DIMENSION:
        resolution_score = float(np.clip(min_dim / MIN_USABLE_DIMENSION, 0, 1)) * 40
    else:
        resolution_score = 40 + float(
            np.clip((min_dim - MIN_USABLE_DIMENSION) / (IDEAL_MIN_DIMENSION - MIN_USABLE_DIMENSION), 0, 1)
        ) * 60

    composite = round(
        0.35 * sharpness_score + 0.20 * brightness_score + 0.15 * contrast_score + 0.30 * resolution_score,
        1,
    )

    issues = []
    if sharpness_score < 40:
        issues.append("Image appears blurry / out of focus")
    if brightness_score < 40:
        issues.append("Poor lighting (too dark or overexposed)")
    if contrast_score < 30:
        issues.append("Low contrast, image looks flat")
    if min_dim < MIN_USABLE_DIMENSION:
        issues.append(f"Resolution too low for e-commerce use ({w}x{h}px)")

    return {
        "score": composite,
        "sharpness_score": round(sharpness_score, 1),
        "brightness_score": round(brightness_score, 1),
        "contrast_score": round(contrast_score, 1),
        "resolution_score": round(resolution_score, 1),
        "width": w,
        "height": h,
        "issues": issues,
        "publish_ready": composite >= 60 and not issues,
    }
