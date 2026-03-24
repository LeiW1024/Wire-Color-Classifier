# backend/tests/unit/test_contour_detection.py
import cv2
import numpy as np

from app.contour_detection import detect_contours, BoundingBox


def test_detect_contours_finds_rectangle():
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(mask, (50, 50), (150, 80), 255, -1)  # Filled white rect
    boxes = detect_contours(mask, min_area=100)
    assert len(boxes) == 1
    assert boxes[0].x >= 50
    assert boxes[0].y >= 50
    assert boxes[0].w <= 101
    assert boxes[0].h <= 31


def test_detect_contours_filters_small_noise():
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(mask, (50, 50), (150, 80), 255, -1)  # Large rect
    cv2.rectangle(mask, (10, 10), (12, 12), 255, -1)    # Tiny noise (4px area)
    boxes = detect_contours(mask, min_area=100)
    assert len(boxes) == 1  # Only the large rectangle


def test_detect_contours_returns_empty_on_blank():
    mask = np.zeros((200, 200), dtype=np.uint8)
    boxes = detect_contours(mask, min_area=100)
    assert len(boxes) == 0


def test_bounding_box_has_area():
    box = BoundingBox(x=10, y=20, w=50, h=30)
    assert box.area == 1500
