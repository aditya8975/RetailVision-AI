from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    """
    A single uploaded product image plus every artifact the pipeline
    produces for it (attributes, description, quality score, OCR text,
    embedding, background-removed variant).
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    processed_path = Column(String, nullable=True)  # background-removed image

    # Detected attributes
    category = Column(String, index=True, nullable=True)
    color = Column(String, index=True, nullable=True)
    pattern = Column(String, nullable=True)
    sleeve_type = Column(String, nullable=True)
    neckline = Column(String, nullable=True)
    attribute_confidences = Column(JSON, nullable=True)  # per-attribute confidence scores

    # Generated content
    description = Column(Text, nullable=True)
    ocr_text = Column(Text, nullable=True)

    # Quality scoring
    quality_score = Column(Float, nullable=True)
    quality_details = Column(JSON, nullable=True)

    # Visual search
    embedding = Column(JSON, nullable=True)  # list[float], CLIP image embedding

    # Detection metadata
    detections = Column(JSON, nullable=True)  # bounding boxes from YOLO

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_path": self.original_path,
            "processed_path": self.processed_path,
            "category": self.category,
            "color": self.color,
            "pattern": self.pattern,
            "sleeve_type": self.sleeve_type,
            "neckline": self.neckline,
            "attribute_confidences": self.attribute_confidences,
            "description": self.description,
            "ocr_text": self.ocr_text,
            "quality_score": self.quality_score,
            "quality_details": self.quality_details,
            "detections": self.detections,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
