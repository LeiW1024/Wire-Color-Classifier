import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

logger = logging.getLogger(__name__)

app = FastAPI(title="Wire Color Classifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def preload_sam():
    """Pre-load SAM model on startup so first request isn't slow."""
    try:
        from app.sam_pipeline import _load_sam
        logger.info("Pre-loading SAM model...")
        _load_sam()
        logger.info("SAM model loaded and ready.")
    except Exception as e:
        logger.warning(f"SAM model pre-load failed (will load on first request): {e}")
