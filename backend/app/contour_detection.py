# backend/app/contour_detection.py
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class BoundingBox:
    """Bounding box for a detected wire region."""
    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return self.w * self.h


def detect_contours(mask: np.ndarray, min_area: int = 100) -> list:
    """Find contours in a binary mask and return bounding boxes, filtering by area."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(contour)
            boxes.append(BoundingBox(x=x, y=y, w=w, h=h))

    return boxes
