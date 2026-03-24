from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models import AnalyzeResponse, ColorRangeResponse, ColorsResponse
from app.sam_pipeline import analyze_image_sam

router = APIRouter(prefix="/api")

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


async def _read_image(file: UploadFile) -> np.ndarray:
    """Read an uploaded file and decode it as an OpenCV image."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File must be an image (PNG, JPEG, WebP)",
        )

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

    return image


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    """Upload an image and get wire color detection results using SAM."""
    image = await _read_image(file)
    result = analyze_image_sam(image)
    return AnalyzeResponse(**result)


@router.get("/colors", response_model=ColorsResponse)
async def get_colors():
    """Return supported color definitions."""
    from app.sam_pipeline import COLOR_RANGES
    colors = [
        ColorRangeResponse(name=name, lower=lower, upper=upper)
        for name, (lower, upper) in COLOR_RANGES.items()
        if name != "red_high"
    ]
    return ColorsResponse(colors=colors)
