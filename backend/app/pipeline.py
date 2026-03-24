from __future__ import annotations

import base64
from typing import Any, Optional

import cv2
import numpy as np

from app.color_discovery import discover_colors
from app.color_segmentation import HSVRange, segment_by_color
from app.config import DEFAULT_K_CLUSTERS, MIN_CONTOUR_AREA
from app.contour_detection import detect_contours
from app.preprocessing import preprocess_image

# Module-level mutable state for calibrated color ranges
_current_ranges: list[HSVRange] = []


def get_color_ranges() -> list[HSVRange]:
    """Return the current calibrated color ranges."""
    return _current_ranges


def set_color_ranges(ranges: list[HSVRange]) -> None:
    """Update the calibrated color ranges."""
    global _current_ranges
    _current_ranges = ranges


def analyze_image(
    image: np.ndarray,
    color_ranges: Optional[list[HSVRange]] = None,
) -> dict[str, Any]:
    """Run the full wire color detection pipeline on an image."""
    hsv = preprocess_image(image)

    # Discover colors if none provided
    if color_ranges is None:
        color_ranges = _current_ranges if _current_ranges else discover_colors(
            hsv, k=DEFAULT_K_CLUSTERS
        )

    colors_found: list[str] = []
    wire_counts: dict[str, int] = {}
    all_boxes: list[dict[str, Any]] = []
    annotated = image.copy()

    for color_range in color_ranges:
        mask = segment_by_color(hsv, color_range)
        boxes = detect_contours(mask, min_area=MIN_CONTOUR_AREA)

        if boxes:
            colors_found.append(color_range.name)
            wire_counts[color_range.name] = len(boxes)

            for box in boxes:
                cv2.rectangle(
                    annotated,
                    (box.x, box.y),
                    (box.x + box.w, box.y + box.h),
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    annotated,
                    color_range.name,
                    (box.x, box.y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
                all_boxes.append({
                    "color": color_range.name,
                    "x": box.x,
                    "y": box.y,
                    "w": box.w,
                    "h": box.h,
                })

    _, buffer = cv2.imencode(".png", annotated)
    annotated_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "colors_found": colors_found,
        "wire_counts": wire_counts,
        "total_wires": sum(wire_counts.values()),
        "bounding_boxes": all_boxes,
        "annotated_image": annotated_b64,
    }
