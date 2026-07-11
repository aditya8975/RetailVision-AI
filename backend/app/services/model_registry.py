"""
Lazy, process-wide singletons for every ML model the pipeline uses.

Models are large (hundreds of MB to a few GB) so we load each one at most
once per process, the first time it's actually needed, and cache it here.
This keeps API startup fast and avoids re-loading weights on every request.
"""
import threading
import torch
from app.config import settings

_lock = threading.Lock()
_registry: dict = {}


def get_device() -> str:
    if settings.force_cpu:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _cached(key, builder):
    if key not in _registry:
        with _lock:
            if key not in _registry:
                _registry[key] = builder()
    return _registry[key]


def get_yolo():
    from ultralytics import YOLO

    def build():
        return YOLO(settings.yolo_model)

    return _cached("yolo", build)


def get_clip():
    """Returns (model, processor) for the CLIP model used for zero-shot
    attribute classification and for visual-search embeddings."""
    from transformers import CLIPModel, CLIPProcessor

    def build():
        model = CLIPModel.from_pretrained(settings.clip_model).to(get_device())
        model.eval()
        processor = CLIPProcessor.from_pretrained(settings.clip_model)
        return model, processor

    return _cached("clip", build)


def get_captioner():
    """Returns (model, processor) for BLIP image captioning."""
    from transformers import BlipForConditionalGeneration, BlipProcessor

    def build():
        model = BlipForConditionalGeneration.from_pretrained(settings.caption_model).to(get_device())
        model.eval()
        processor = BlipProcessor.from_pretrained(settings.caption_model)
        return model, processor

    return _cached("captioner", build)


def get_ocr_reader():
    import easyocr

    def build():
        return easyocr.Reader(["en"], gpu=(get_device() == "cuda"))

    return _cached("ocr", build)


def get_bg_remover_session():
    from rembg import new_session

    def build():
        return new_session("u2net")

    return _cached("rembg", build)
