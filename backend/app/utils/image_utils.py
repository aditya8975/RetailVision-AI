import uuid
from pathlib import Path
from PIL import Image
from app.config import settings


def unique_filename(original_name: str) -> str:
    ext = Path(original_name).suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    return f"{uuid.uuid4().hex}{ext}"


def save_upload(image: Image.Image, filename: str) -> str:
    path = settings.upload_dir / filename
    image.convert("RGB").save(path, quality=92)
    return str(path)


def save_processed(image: Image.Image, filename: str) -> str:
    """Saves an image (e.g. background-removed, which has an alpha
    channel) to the processed directory, preserving transparency."""
    path = settings.processed_dir / filename
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    image.save(path)
    return str(path)


def open_image(path: str) -> Image.Image:
    return Image.open(path)
