"""Background removal using rembg (U2Net segmentation model)."""
from PIL import Image
from rembg import remove
from app.services.model_registry import get_bg_remover_session


def remove_background(image: Image.Image) -> Image.Image:
    session = get_bg_remover_session()
    result = remove(image, session=session)
    return result
