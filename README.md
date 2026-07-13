# Lattice - AI Product Image Intelligence Platform

A self-hosted version of the core pipeline behind catalog-automation platforms: 
upload a product photo and get attribute detection, an AI-written
description, background removal, an image-quality score, OCR on printed
labels, and visual (image-to-image) search — plus a dashboard over the whole
catalog.

## What it actually does (and how)

| Feature | Model / technique | Notes |
|---|---|---|
| Product localization | YOLOv8 (Ultralytics) | Crops the main product region before the other steps run. COCO's classes don't include "shirt" or "dress", so this stage is generic localization, not garment classification — that's CLIP's job below. |
| Attribute detection (category, color, pattern, sleeve, neckline) | CLIP zero-shot classification | Each attribute has a candidate label set; CLIP scores the image against every candidate and picks the best match, with a confidence score. No custom training data needed. |
| AI product description | BLIP image captioning + attribute merge | BLIP produces a free-form caption, which is combined with the structured attributes into a catalog-style description. |
| Background removal | rembg (U2Net) | Outputs a transparent PNG. |
| Image quality scoring | OpenCV (Laplacian variance, brightness, contrast, resolution) | Deterministic, no model — a composite 0–100 "is this photo good enough to publish" score with the specific issues listed. |
| OCR on labels/tags | EasyOCR | Runs on the full original image (labels are often outside the cropped product region). |
| Visual search | CLIP image embeddings + cosine similarity | Each upload is embedded once and stored in Postgres; search embeds the query and ranks the catalog. Simple `numpy` cosine similarity — swap in pgvector or FAISS if the catalog grows past tens of thousands of items. |
| Dashboard | Aggregation queries over the products table | Category/color/pattern breakdowns, average quality score, uploads-over-time. |

Nothing here is a stub — every endpoint runs real inference. The tradeoff is
model size and speed, covered below.

## Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL (SQLite fallback for local dev)
- **Frontend**: React + Vite, React Router, Recharts
- **ML**: PyTorch, Transformers (CLIP, BLIP), Ultralytics (YOLOv8), OpenCV, EasyOCR, rembg
- **Infra**: Docker Compose (Postgres + backend + frontend)

## Before you run it — read this

This pipeline downloads several pretrained model checkpoints the first time
each service is used (YOLOv8n ~6MB, CLIP ViT-B/32 ~600MB, BLIP-base ~900MB,
EasyOCR detector+recognizer ~100MB, U2Net ~180MB — roughly **2GB total**).
That download happens automatically via `transformers` / `ultralytics` /
`easyocr` / `rembg` the first time you hit an endpoint that needs it, which
means:

- **You need an internet connection** the first time each model is used.
- **The very first upload will be slow** (downloading + loading models into
  memory) — expect anywhere from 30 seconds to a few minutes depending on
  your connection. Subsequent uploads are fast (models stay cached in
  memory for the life of the process, and weights are cached on disk after
  the first download).
- **CPU inference works but is slow** — a few seconds per image on a modern
  laptop CPU. A GPU (set `FORCE_CPU=false`, default) speeds this up
  substantially if you have CUDA available.
- I built and syntax/wiring-tested this in a sandboxed environment without
  general internet access, so I could not run a real end-to-end inference
  pass with the actual model weights before handing it to you. The API
  routing, database layer, and pipeline orchestration are verified working
  (tested with mocked model outputs); the model-specific code follows the
  standard `transformers`/`ultralytics`/`easyocr`/`rembg` APIs but you
  should do a real first-run smoke test on your machine and expect to debug
  minor issues (a renamed parameter in a library version, a path issue,
  etc.) — that's normal for a project this size, not a sign the whole thing
  is broken.

## Quick start (Docker — recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- Postgres runs in its own container; data persists in a named volume.

First `docker compose up` will take a while: it builds the backend image
(installing PyTorch etc.) and then downloads model weights on first use.

## Quick start (local, no Docker)

```bash
./run.sh        # macOS/Linux
run.bat         # Windows
```

This creates a Python venv, installs backend dependencies, installs frontend
dependencies, and starts both. Uses SQLite by default — nothing to configure.

## Manual setup

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## API overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/products/upload` | POST | Upload an image, run the full pipeline, store the result |
| `/api/products` | GET | List catalog products |
| `/api/products/{id}` | GET | Get one product's full analysis |
| `/api/products/{id}` | DELETE | Remove a product |
| `/api/search/visual` | POST | Upload a query image, get visually similar catalog products |
| `/api/search/similar/{id}` | GET | Get products similar to an existing catalog item |
| `/api/dashboard/stats` | GET | Aggregated catalog analytics |
| `/api/health` | GET | Service + device (cpu/cuda) check |

Full interactive docs (with request/response schemas) are at `/docs` once the
backend is running.

## Project structure

```
backend/
  app/
    main.py              FastAPI app, CORS, static file mounts
    config.py             Settings (env-driven)
    database.py           SQLAlchemy engine/session
    models.py              Product table
    schemas.py             Pydantic response models
    routers/
      products.py         Upload / list / get / delete
      search.py            Visual search
      dashboard.py         Analytics
    services/
      model_registry.py   Lazy-loaded singleton models (loaded once, reused)
      detection.py         YOLO product localization + cropping
      attributes.py        CLIP zero-shot attribute classification
      captioning.py         BLIP caption + description builder
      background_removal.py rembg background removal
      quality.py            OpenCV quality scoring
      ocr.py                 EasyOCR text extraction
      embeddings.py          CLIP embeddings + cosine similarity
      pipeline.py            Orchestrates all of the above per upload
frontend/
  src/
    pages/               Upload, Catalog, ProductDetail, VisualSearch, Dashboard
    components/          Navbar, ProductCard
    api.js               Fetch wrapper for the backend
docker-compose.yml        Postgres + backend + frontend
run.sh / run.bat          Local dev launchers (no Docker)
```

## Known limitations / honest caveats

- **Attribute accuracy depends on CLIP's zero-shot ability**, which is good
  but not perfect — it won't match a model fine-tuned on a labeled fashion
  dataset. Confidence scores are shown in the UI so low-confidence calls are
  visible rather than hidden.
- **YOLO here is generic COCO detection**, used only to crop the product
  from background clutter. If you want true garment-part detection (sleeve
  boundary, collar region, etc.) you'd fine-tune YOLO on a fashion dataset
  such as DeepFashion2 — the `detection.py` module is where that model would
  plug in.
- **Visual search uses brute-force cosine similarity** in Python — fine up
  to tens of thousands of products, but you'd want pgvector or FAISS for a
  catalog in the millions.
- **No auth/multi-tenancy** — this is a single-catalog platform as built. Add
  an auth layer (e.g. JWT + a `user_id` column on `products`) before
  exposing it publicly.
