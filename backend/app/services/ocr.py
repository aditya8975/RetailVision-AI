"""OCR for product labels, size tags, and printed text using EasyOCR."""
import numpy as np
from PIL import Image
from app.services.model_registry import get_ocr_reader


def extract_text(image: Image.Image, min_confidence: float = 0.4) -> dict:
    reader = get_ocr_reader()
    arr = np.array(image.convert("RGB"))
    results = reader.readtext(arr)

    lines = []
    for bbox, text, conf in results:
        if conf >= min_confidence and text.strip():
            lines.append({"text": text.strip(), "confidence": round(float(conf), 3), "box": [[float(p[0]), float(p[1])] for p in bbox]})

    full_text = " ".join(l["text"] for l in lines)
    return {"full_text": full_text, "lines": lines}
