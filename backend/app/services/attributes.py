"""
Zero-shot clothing/product attribute classification using CLIP.

For each attribute (category, color, pattern, sleeve type, neckline) we
build a small set of natural-language candidate labels, embed them with
CLIP's text encoder, embed the product image with CLIP's vision encoder,
and pick the candidate with the highest cosine similarity. This is the
same "zero-shot classification via CLIP" pattern used in production
fashion-tech pipelines, and it works without needing a custom-labeled
training set.
"""
import torch
from PIL import Image
from app.services.model_registry import get_clip, get_device

ATTRIBUTE_CANDIDATES = {
    "category": [
        "t-shirt", "shirt", "blouse", "dress", "skirt", "jeans", "trousers",
        "jacket", "coat", "sweater", "hoodie", "shorts", "shoes", "sneakers",
        "handbag", "hat", "scarf", "suit", "sweatshirt", "jumpsuit",
    ],
    "color": [
        "black", "white", "grey", "navy blue", "blue", "red", "maroon",
        "green", "olive", "yellow", "orange", "pink", "purple", "brown",
        "beige", "cream", "gold", "silver", "multicolor",
    ],
    "pattern": [
        "solid / plain", "striped", "checkered / plaid", "floral",
        "polka dot", "graphic print", "animal print", "geometric pattern",
        "tie-dye", "camouflage",
    ],
    "sleeve_type": [
        "sleeveless", "short sleeve", "half sleeve", "long sleeve",
        "three-quarter sleeve", "cap sleeve", "not applicable (no sleeves in item)",
    ],
    "neckline": [
        "round neck / crew neck", "v-neck", "collared neck", "turtleneck",
        "boat neck", "halter neck", "off-shoulder", "not applicable",
    ],
}

# Clean, human-friendly labels for the same candidates above (used in the
# generated description instead of the raw CLIP prompt phrasing).
_CLEAN = {
    "solid / plain": "solid",
    "checkered / plaid": "checkered",
    "round neck / crew neck": "round neck",
    "not applicable (no sleeves in item)": "n/a",
    "not applicable": "n/a",
}


def _clean_label(label: str) -> str:
    return _CLEAN.get(label, label)


@torch.no_grad()
def classify_attributes(image: Image.Image) -> dict:
    model, processor = get_clip()
    device = get_device()

    image_inputs = processor(images=image, return_tensors="pt").to(device)
    image_features = model.get_image_features(**image_inputs)
    image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)

    results = {}
    confidences = {}

    for attr_name, candidates in ATTRIBUTE_CANDIDATES.items():
        prompts = [f"a photo of a {c} clothing item" if attr_name == "category"
                   else f"a product photo showing {c} {attr_name.replace('_', ' ')}"
                   for c in candidates]
        text_inputs = processor(text=prompts, return_tensors="pt", padding=True).to(device)
        text_features = model.get_text_features(**text_inputs)
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)

        similarity = (image_features @ text_features.T).squeeze(0)
        probs = similarity.softmax(dim=-1)

        top_idx = int(probs.argmax())
        results[attr_name] = _clean_label(candidates[top_idx])
        confidences[attr_name] = round(float(probs[top_idx]), 4)

    results["confidences"] = confidences
    return results
