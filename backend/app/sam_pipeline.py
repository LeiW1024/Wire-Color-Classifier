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
        points_per_side=8,            # 64 points total — fast on CPU
        pred_iou_thresh=0.75,
        stability_score_thresh=0.80,
        min_mask_region_area=200,
        points_per_batch=16,
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


def _is_wire_like(mask: dict, image_area: int, min_aspect_ratio: float = 2.5) -> bool:
    """Check if a mask segment is elongated (wire-like) and not background."""
    bbox = mask["bbox"]  # x, y, w, h
    w, h = bbox[2], bbox[3]
    if w == 0 or h == 0:
        return False

    area = mask["area"]

    # Reject large segments (>8% of image) — these are background, not wires
    if area > image_area * 0.08:
        return False

    # Reject tiny noise segments
    if area < 150:
        return False

    aspect = max(w, h) / min(w, h)

    # Wire-like: elongated shape
    if aspect >= min_aspect_ratio:
        return True
    # Shorter but thick wire cross-sections (e.g., wire going into camera)
    if area > 800 and aspect >= 1.5:
        return True

    return False


def analyze_image_sam(image: np.ndarray) -> dict[str, Any]:
    """Run SAM-based wire color detection pipeline."""
    import time
    t_start = time.time()

    mask_generator = _load_sam()

    # Resize large images to max 800px on longest side for faster SAM inference
    h, w = image.shape[:2]
    max_side = 800
    scale = 1.0
    if max(h, w) > max_side:
        scale = max_side / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Convert BGR to RGB for SAM
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Generate masks
    masks = mask_generator.generate(image_rgb)

    # Convert to HSV for color classification
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    img_h, img_w = image.shape[:2]
    image_area = img_h * img_w

    colors_found: list[str] = []
    wire_counts: dict[str, int] = {}
    all_boxes: list[dict[str, Any]] = []
    annotated = image.copy()
    overlay = image.copy()

    confidence_scores: list[float] = []
    total_wire_pixels = 0
    covered_pixels = np.zeros((img_h, img_w), dtype=bool)

    for mask_data in masks:
        # Filter: only wire-like segments
        if not _is_wire_like(mask_data, image_area):
            continue

        # Get the pixels inside this mask
        binary_mask = mask_data["segmentation"]
        masked_hsv = hsv[binary_mask]

        # Classify color
        color = _classify_color(masked_hsv)
        if color is None or color in ("black", "gray", "white"):
            continue

        # Track SAM's predicted IoU as segment confidence
        confidence_scores.append(float(mask_data.get("predicted_iou", 0.85)))
        total_wire_pixels += mask_data["area"]
        covered_pixels |= binary_mask

        # Count
        if color not in wire_counts:
            wire_counts[color] = 0
            colors_found.append(color)
        wire_counts[color] += 1

        draw_color = DRAW_COLORS.get(color, (0, 255, 0))

        # Fill the mask area with semi-transparent color overlay
        overlay[binary_mask] = draw_color

        # Draw contour outline (no bounding box)
        contours, _ = cv2.findContours(
            binary_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(annotated, contours, -1, draw_color, 2)

        x, y, bw, bh = mask_data["bbox"]
        all_boxes.append({
            "color": color,
            "x": int(x),
            "y": int(y),
            "w": int(bw),
            "h": int(bh),
        })

    # Blend semi-transparent mask overlay onto annotated image
    cv2.addWeighted(overlay, 0.35, annotated, 0.65, 0, annotated)

    # Encode annotated image
    _, buffer = cv2.imencode(".png", annotated)
    annotated_b64 = base64.b64encode(buffer).decode("utf-8")

    # Compute metrics
    avg_confidence = round(float(np.mean(confidence_scores)) * 100, 1) if confidence_scores else 0.0
    wire_coverage_pct = round(float(np.sum(covered_pixels)) / image_area * 100, 1)

    return {
        "colors_found": colors_found,
        "wire_counts": wire_counts,
        "total_wires": sum(wire_counts.values()),
        "bounding_boxes": all_boxes,
        "annotated_image": annotated_b64,
        "processing_time_ms": int((time.time() - t_start) * 1000),
        "segments_analyzed": len(masks),
        "avg_confidence": avg_confidence,
        "wire_coverage_pct": wire_coverage_pct,
    }
