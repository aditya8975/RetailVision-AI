"""
CLIP image embeddings for visual search.

Each product image is embedded into a 512-dim vector at upload time and
stored in the database (JSON column -- see models.py). Visual search then
embeds the query image the same way and ranks the catalog by cosine
similarity. This keeps the search index trivially consistent with the
database (no separate vector store to sync) and is more than fast enough
for catalogs up to tens of thousands of items; at larger scale this is the
natural place to swap in pgvector or FAISS without changing the rest of
the pipeline.
"""
import torch
import numpy as np
from PIL import Image
from app.services.model_registry import get_clip, get_device


@torch.no_grad()
def embed_image(image: Image.Image) -> list[float]:
    model, processor = get_clip()
    device = get_device()
    inputs = processor(images=image, return_tensors="pt").to(device)
    features = model.get_image_features(**inputs)
    features = features / features.norm(p=2, dim=-1, keepdim=True)
    return features.squeeze(0).cpu().tolist()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def rank_by_similarity(query_embedding: list[float], candidates: list[tuple[int, list[float]]], top_k: int = 12):
    """candidates: list of (product_id, embedding). Returns sorted list of
    (product_id, similarity) descending."""
    scored = [(pid, cosine_similarity(query_embedding, emb)) for pid, emb in candidates if emb]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
