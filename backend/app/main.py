from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import products, search, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Upload product photos and get attribute detection, AI-generated "
        "descriptions, background removal, quality scoring, OCR and "
        "visual similarity search — the core building blocks behind "
        "catalog-automation platforms like Vue.ai."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
app.mount("/media/processed", StaticFiles(directory=str(settings.processed_dir)), name="processed")

app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)


@app.get("/api/health")
def health_check():
    from app.services.model_registry import get_device
    return {"status": "ok", "device": get_device()}


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
    }
