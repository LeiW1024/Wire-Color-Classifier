from __future__ import annotations

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.color_discovery import discover_colors
from app.config import DEFAULT_K_CLUSTERS
from app.models import AnalyzeResponse, ColorRangeResponse, ColorsResponse
from app.pipeline import analyze_image, get_color_ranges, set_color_ranges
from app.preprocessing import preprocess_image

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
    """Upload an image and get wire color detection results."""
    image = await _read_image(file)
    result = analyze_image(image)
    return AnalyzeResponse(**result)


@router.post("/calibrate")
async def calibrate(file: UploadFile = File(...)):
    """Upload a reference image to discover and set color ranges."""
    image = await _read_image(file)
    hsv = preprocess_image(image)
    ranges = discover_colors(hsv, k=DEFAULT_K_CLUSTERS)
    set_color_ranges(ranges)
    return {
        "message": f"Discovered {len(ranges)} colors",
        "colors": [r.name for r in ranges],
    }


@router.get("/colors", response_model=ColorsResponse)
async def get_colors():
    """Return current color definitions and HSV ranges."""
    ranges = get_color_ranges()
    return ColorsResponse(
        colors=[
            ColorRangeResponse(name=r.name, lower=r.lower, upper=r.upper)
            for r in ranges
        ]
    )
