from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from PIL import Image
import io

from app.database import get_db
from app.models import Product
from app.services import embeddings

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/visual")
async def visual_search(
    file: UploadFile = File(...),
    top_k: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Finds catalog products visually similar to the uploaded image using
    CLIP embedding cosine similarity."""
    raw = await file.read()
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except Exception:
        raise HTTPException(400, "Could not read image file — it may be corrupted.")

    query_embedding = embeddings.embed_image(image)

    products = db.query(Product).filter(Product.embedding.isnot(None)).all()
    candidates = [(p.id, p.embedding) for p in products]
    ranked = embeddings.rank_by_similarity(query_embedding, candidates, top_k=top_k)

    by_id = {p.id: p for p in products}
    return [
        {"product": by_id[pid].to_dict(), "similarity": round(sim, 4)}
        for pid, sim in ranked
        if pid in by_id
    ]


@router.get("/similar/{product_id}")
def similar_products(product_id: int, top_k: int = Query(8, ge=1, le=50), db: Session = Depends(get_db)):
    """Finds products similar to an existing catalog item (e.g. for a
    'you might also like' widget)."""
    source = db.query(Product).filter(Product.id == product_id).first()
    if not source or not source.embedding:
        raise HTTPException(404, "Product not found or has no embedding")

    products = db.query(Product).filter(Product.id != product_id, Product.embedding.isnot(None)).all()
    candidates = [(p.id, p.embedding) for p in products]
    ranked = embeddings.rank_by_similarity(source.embedding, candidates, top_k=top_k)

    by_id = {p.id: p for p in products}
    return [
        {"product": by_id[pid].to_dict(), "similarity": round(sim, 4)}
        for pid, sim in ranked
        if pid in by_id
    ]
