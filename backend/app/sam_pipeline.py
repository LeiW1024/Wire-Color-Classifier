"""Wire color detection pipeline using SAM (Segment Anything Model).

Replaces the classical CV pipeline with:
1. SAM auto-segments all objects in the image
2. Filter segments by shape (elongated = wire-like)
3. Classify each segment's dominant color
4. Return colors, counts, bounding boxes, annotated image
"""
from __future__ import annotations

import base64
import os
from typing import Any, Optional

import cv2
import numpy as np
import torch
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

# Color classification in HSV space
COLOR_RANGES = {
    "red": [(0, 70, 50), (10, 255, 255)],
    "red_high": [(160, 70, 50), (180, 255, 255)],
    "orange": [(10, 70, 50), (25, 255, 255)],
    "yellow": [(25, 70, 50), (35, 255, 255)],
    "green": [(35, 70, 50), (85, 255, 255)],
    "blue": [(85, 70, 50), (130, 255, 255)],
    "purple": [(130, 70, 50), (160, 255, 255)],
    "pink": [(140, 30, 150), (170, 150, 255)],
    "white": [(0, 0, 180), (180, 40, 255)],
    "gray": [(0, 0, 80), (180, 40, 180)],
    "black": [(0, 0, 0), (180, 80, 50)],
}

# BGR colors for drawing bounding boxes per detected color
DRAW_COLORS = {
    "red": (0, 0, 255),
    "orange": (0, 140, 255),
    "yellow": (0, 255, 255),
    "green": (0, 200, 0),
    "blue": (255, 100, 0),
    "purple": (200, 0, 200),
    "pink": (180, 105, 255),
    "white": (220, 220, 220),
    "gray": (150, 150, 150),
    "black": (50, 50, 50),
}

# SAM model singleton
_sam_model = None
_mask_generator = None


def _get_model_path() -> str:
    """Find the SAM model weights file."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "models", "sam_vit_b.pth"),
        os.environ.get("SAM_MODEL_PATH", ""),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise FileNotFoundError(
        "SAM model not found. Download sam_vit_b_01ec64.pth to backend/models/sam_vit_b.pth"
    )


def _load_sam():
    """Load SAM model (singleton, loaded once)."""
    global _sam_model, _mask_generator
    if _mask_generator is not None:
        return _mask_generator

    model_path = _get_model_path()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    _sam_model = sam_model_registry["vit_b"](checkpoint=model_path)
    _sam_model.to(device=device)

    _mask_generator = SamAutomaticMaskGenerator(
        model=_sam_model,
        points_per_side=32,
        pred_iou_thresh=0.86,
        stability_score_thresh=0.92,
        min_mask_region_area=500,
    )
    return _mask_generator


def _classify_color(hsv_region: np.ndarray) -> Optional[str]:
    """Classify the dominant color of an HSV image region.

    Args:
        hsv_region: Array of shape (N, 3) with HSV pixel values.
    """
    if hsv_region.size == 0:
        return None

    # Ensure shape is (N, 1, 3) for cv2.inRange
    if hsv_region.ndim == 2:
        hsv_for_cv = hsv_region.reshape(-1, 1, 3)
    else:
        hsv_for_cv = hsv_region

    best_color = None
    best_count = 0

    for color_name, (lower, upper) in COLOR_RANGES.items():
        lower_np = np.array(lower, dtype=np.uint8)
        upper_np = np.array(upper, dtype=np.uint8)
        mask = cv2.inRange(hsv_for_cv, lower_np, upper_np)
        count = cv2.countNonZero(mask)

        if count > best_count:
            best_count = count
            best_color = color_name

    # Merge red ranges
    if best_color == "red_high":
        best_color = "red"

    # Require at least 15% of pixels to match a color
    total_pixels = hsv_region.shape[0]
    if total_pixels > 0 and best_count / total_pixels < 0.15:
        return None

    return best_color


def _is_wire_like(mask: dict, min_aspect_ratio: float = 2.0) -> bool:
    """Check if a mask segment is elongated (wire-like)."""
    bbox = mask["bbox"]  # x, y, w, h
    w, h = bbox[2], bbox[3]
    if w == 0 or h == 0:
        return False

    aspect = max(w, h) / min(w, h)
    area = mask["area"]

    # Wire-like: elongated shape OR reasonable size
    # Allow less elongated shapes if area is reasonable (thick wires)
    if aspect >= min_aspect_ratio:
        return True
    if area > 1000 and aspect >= 1.3:
        return True

    return False


def analyze_image_sam(image: np.ndarray) -> dict[str, Any]:
    """Run SAM-based wire color detection pipeline."""
    mask_generator = _load_sam()

    # Convert BGR to RGB for SAM
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Generate masks
    masks = mask_generator.generate(image_rgb)

    # Convert to HSV for color classification
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    colors_found: list[str] = []
    wire_counts: dict[str, int] = {}
    all_boxes: list[dict[str, Any]] = []
    annotated = image.copy()

    for mask_data in masks:
        # Filter: only wire-like segments
        if not _is_wire_like(mask_data):
            continue

        # Get the pixels inside this mask
        binary_mask = mask_data["segmentation"]
        masked_hsv = hsv[binary_mask]

        # Classify color
        color = _classify_color(masked_hsv)
        if color is None or color in ("black", "gray", "white"):
            # Skip background-like colors
            continue

        # Count
        if color not in wire_counts:
            wire_counts[color] = 0
            colors_found.append(color)
        wire_counts[color] += 1

        # Bounding box
        x, y, w, h = mask_data["bbox"]
        draw_color = DRAW_COLORS.get(color, (0, 255, 0))

        # Draw on annotated image
        cv2.rectangle(annotated, (x, y), (x + w, y + h), draw_color, 2)
        cv2.putText(
            annotated, color, (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2,
        )

        # Also draw the mask outline for clarity
        contours, _ = cv2.findContours(
            binary_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(annotated, contours, -1, draw_color, 2)

        all_boxes.append({
            "color": color,
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
        })

    # Encode annotated image
    _, buffer = cv2.imencode(".png", annotated)
    annotated_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "colors_found": colors_found,
        "wire_counts": wire_counts,
        "total_wires": sum(wire_counts.values()),
        "bounding_boxes": all_boxes,
        "annotated_image": annotated_b64,
    }
