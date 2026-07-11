"""
AI product description generation.

Two ingredients are combined:
 1. A BLIP image-captioning model gives a free-form visual caption
    ("a black jacket hanging on a rack").
 2. The structured attributes from attributes.py (category, color,
    pattern, sleeve, neckline) give precise, catalog-friendly facts.

We merge both into a short marketing-style product description rather than
returning the raw caption alone, since raw captions tend to describe the
photo ("a mannequin wearing...") rather than the product.
"""
import torch
from PIL import Image
from app.services.model_registry import get_captioner, get_device


@torch.no_grad()
def generate_caption(image: Image.Image) -> str:
    model, processor = get_captioner()
    device = get_device()
    inputs = processor(images=image, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=30)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption.strip()


def build_description(caption: str, attrs: dict) -> str:
    category = attrs.get("category", "item")
    color = attrs.get("color", "")
    pattern = attrs.get("pattern", "")
    sleeve = attrs.get("sleeve_type", "")
    neckline = attrs.get("neckline", "")

    details = []
    if pattern and pattern not in ("solid", "n/a"):
        details.append(f"{pattern} pattern")
    if sleeve and sleeve != "n/a":
        details.append(f"{sleeve} sleeves")
    if neckline and neckline != "n/a":
        details.append(f"{neckline}")

    detail_str = f" featuring {', '.join(details)}" if details else ""
    color_str = f"{color} " if color else ""

    description = (
        f"{color_str}{category}{detail_str}. {caption.capitalize()}."
        if caption else f"{color_str.capitalize()}{category}{detail_str}."
    )
    return description
