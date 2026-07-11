"""
Product localization with YOLO.

The stock YOLO checkpoint (COCO classes) doesn't know clothing-specific
categories like "sleeve" or "neckline" -- that's handled downstream by CLIP
zero-shot classification in attributes.py. What YOLO gives us here is
general object localization: find the main product region in the frame so
that attribute classification, captioning and quality scoring can all run
on a tightly cropped image instead of a cluttered full photo.
"""
from PIL import Image
from app.services.model_registry import get_yolo


def detect_main_object(image: Image.Image) -> dict:
    """
    Runs YOLO on the image and returns the highest-confidence bounding box,
    plus the full list of raw detections. If nothing is detected (common for
    clean studio product shots with no COCO-recognizable object), falls back
    to treating the entire image as the product region.
    """
    model = get_yolo()
    results = model.predict(image, verbose=False)[0]

    detections = []
    for box in results.boxes:
        xyxy = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        label = model.names.get(cls_id, str(cls_id))
        detections.append({"label": label, "confidence": conf, "box": xyxy})

    if not detections:
        w, h = image.size
        return {
            "box": [0, 0, w, h],
            "label": "full_image",
            "confidence": None,
            "all_detections": [],
        }

    best = max(detections, key=lambda d: d["confidence"])
    return {
        "box": best["box"],
        "label": best["label"],
        "confidence": best["confidence"],
        "all_detections": detections,
    }


def crop_to_box(image: Image.Image, box: list[float], padding_ratio: float = 0.08) -> Image.Image:
    """Crops the image to the given box with a small margin so we don't
    slice through the edge of the product."""
    w, h = image.size
    x1, y1, x2, y2 = box
    pad_x = (x2 - x1) * padding_ratio
    pad_y = (y2 - y1) * padding_ratio
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)
    return image.crop((int(x1), int(y1), int(x2), int(y2)))
