# backend/app/color_segmentation.py
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class HSVRange:
    """Defines an HSV color range for segmentation."""
    name: str
    lower: tuple
    upper: tuple


def segment_by_color(hsv_image: np.ndarray, color_range: HSVRange) -> np.ndarray:
    """Create a binary mask for pixels within the given HSV range."""
    lower = np.array(color_range.lower, dtype=np.uint8)
    upper = np.array(color_range.upper, dtype=np.uint8)

    mask = cv2.inRange(hsv_image, lower, upper)

    # Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask
