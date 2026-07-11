from pydantic import BaseModel
from typing import Optional, Any


class ProductOut(BaseModel):
    id: int
    filename: str
    original_path: str
    processed_path: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    pattern: Optional[str] = None
    sleeve_type: Optional[str] = None
    neckline: Optional[str] = None
    attribute_confidences: Optional[dict[str, Any]] = None
    description: Optional[str] = None
    ocr_text: Optional[str] = None
    quality_score: Optional[float] = None
    quality_details: Optional[dict[str, Any]] = None
    detections: Optional[list[Any]] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    product: ProductOut
    similarity: float


class DashboardStats(BaseModel):
    total_products: int
    avg_quality_score: float
    category_breakdown: dict[str, int]
    color_breakdown: dict[str, int]
    pattern_breakdown: dict[str, int]
    low_quality_count: int
    uploads_by_day: dict[str, int]
