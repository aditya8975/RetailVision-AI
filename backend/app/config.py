"""
Central configuration for the AI Product Image Intelligence Platform.

All values can be overridden with environment variables (see .env.example).
Defaults to a local SQLite database so the API can be started with zero
external setup; docker-compose overrides DATABASE_URL to point at Postgres.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "AI Product Image Intelligence Platform"
    api_prefix: str = "/api"

    # Database
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")

    # Storage
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    processed_dir: Path = BASE_DIR / "data" / "processed"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    # Model configuration (HuggingFace / Ultralytics model IDs)
    yolo_model: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
    clip_model: str = os.getenv("CLIP_MODEL", "openai/clip-vit-base-patch32")
    caption_model: str = os.getenv("CAPTION_MODEL", "Salesforce/blip-image-captioning-base")

    # Device: "cuda" if a GPU is available, else "cpu" (auto-detected in services/device.py)
    force_cpu: bool = os.getenv("FORCE_CPU", "false").lower() == "true"

    # Visual search
    embedding_dim: int = 512  # CLIP ViT-B/32 image embedding size

    class Config:
        env_file = ".env"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.processed_dir.mkdir(parents=True, exist_ok=True)
if settings.database_url.startswith("sqlite"):
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
