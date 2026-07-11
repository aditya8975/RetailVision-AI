"""
Orchestrates the full per-image analysis pipeline:

  1. Detect the main product region (YOLO)          -> crop
  2. Classify attributes on the crop (CLIP zero-shot)
  3. Caption the crop (BLIP) + merge with attributes -> description
  4. Score technical quality on the ORIGINAL image (OpenCV)
  5. Run OCR on the ORIGINAL image (labels/tags are often outside the crop)
  6. Remove background (rembg) -> processed image saved to disk
  7. Embed the crop for visual search (CLIP)

Each stage is independent and swappable; this module just wires them
together in the right order and decides which image (original vs crop)
each stage should run on.
"""
from PIL import Image

from app.services import detection, attributes, captioning, quality, ocr, embeddings, background_removal
from app.utils.image_utils import save_processed


def run_pipeline(image: Image.Image, filename: str) -> dict:
    result: dict = {}

    # 1. Localize product & crop
    det = detection.detect_main_object(image)
    result["detections"] = det["all_detections"]
    crop = detection.crop_to_box(image, det["box"]) if det["confidence"] else image

    # 2. Attribute classification
    attrs = attributes.classify_attributes(crop)
    confidences = attrs.pop("confidences")
    result.update(attrs)
    result["attribute_confidences"] = confidences

    # 3. Caption + description
    caption = captioning.generate_caption(crop)
    result["description"] = captioning.build_description(caption, attrs)

    # 4. Quality scoring (full original image, not the crop)
    result["quality"] = quality.score_image_quality(image)

    # 5. OCR (full original image)
    ocr_result = ocr.extract_text(image)
    result["ocr_text"] = ocr_result["full_text"]
    result["ocr_lines"] = ocr_result["lines"]

    # 6. Background removal
    bg_removed = background_removal.remove_background(image)
    processed_name = filename.rsplit(".", 1)[0] + "_nobg.png"
    result["processed_path"] = save_processed(bg_removed, processed_name)

    # 7. Embedding for visual search
    result["embedding"] = embeddings.embed_image(crop)

    return result
