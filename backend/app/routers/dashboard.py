from collections import Counter
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    total = len(products)

    if total == 0:
        return {
            "total_products": 0,
            "avg_quality_score": 0,
            "category_breakdown": {},
            "color_breakdown": {},
            "pattern_breakdown": {},
            "low_quality_count": 0,
            "uploads_by_day": {},
        }

    quality_scores = [p.quality_score for p in products if p.quality_score is not None]
    avg_quality = round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0

    category_breakdown = dict(Counter(p.category for p in products if p.category))
    color_breakdown = dict(Counter(p.color for p in products if p.color))
    pattern_breakdown = dict(Counter(p.pattern for p in products if p.pattern))
    low_quality_count = sum(1 for p in products if p.quality_score is not None and p.quality_score < 60)

    uploads_by_day: dict[str, int] = {}
    for p in products:
        if p.created_at:
            day = p.created_at.strftime("%Y-%m-%d")
            uploads_by_day[day] = uploads_by_day.get(day, 0) + 1

    return {
        "total_products": total,
        "avg_quality_score": avg_quality,
        "category_breakdown": category_breakdown,
        "color_breakdown": color_breakdown,
        "pattern_breakdown": pattern_breakdown,
        "low_quality_count": low_quality_count,
        "uploads_by_day": dict(sorted(uploads_by_day.items())),
    }
