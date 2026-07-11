from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from PIL import Image
import io

from app.database import get_db
from app.models import Product
from app.schemas import ProductOut
from app.utils.image_utils import unique_filename, save_upload
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/products", tags=["products"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/upload", response_model=ProductOut)
async def upload_product(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}. Use JPEG, PNG or WebP.")

    raw = await file.read()
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except Exception:
        raise HTTPException(400, "Could not read image file — it may be corrupted.")

    filename = unique_filename(file.filename or "upload.jpg")
    original_path = save_upload(image, filename)

    pipeline_result = run_pipeline(image, filename)

    product = Product(
        filename=filename,
        original_path=original_path,
        processed_path=pipeline_result["processed_path"],
        category=pipeline_result.get("category"),
        color=pipeline_result.get("color"),
        pattern=pipeline_result.get("pattern"),
        sleeve_type=pipeline_result.get("sleeve_type"),
        neckline=pipeline_result.get("neckline"),
        attribute_confidences=pipeline_result.get("attribute_confidences"),
        description=pipeline_result.get("description"),
        ocr_text=pipeline_result.get("ocr_text"),
        quality_score=pipeline_result["quality"]["score"],
        quality_details=pipeline_result["quality"],
        detections=pipeline_result.get("detections"),
        embedding=pipeline_result.get("embedding"),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product.to_dict()


@router.get("", response_model=list[ProductOut])
def list_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    products = db.query(Product).order_by(desc(Product.created_at)).offset(skip).limit(limit).all()
    return [p.to_dict() for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    return product.to_dict()


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    db.delete(product)
    db.commit()
    return {"status": "deleted", "id": product_id}
