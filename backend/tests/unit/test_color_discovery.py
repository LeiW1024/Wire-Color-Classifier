# backend/tests/unit/test_color_discovery.py
import cv2
import numpy as np

from app.color_discovery import discover_colors
from app.color_segmentation import HSVRange


def test_discover_colors_finds_three_in_multicolor(sample_color_image: np.ndarray):
    hsv = cv2.cvtColor(sample_color_image, cv2.COLOR_BGR2HSV)
    ranges = discover_colors(hsv, k=3)
    assert len(ranges) == 3
    assert all(isinstance(r, HSVRange) for r in ranges)


def test_discover_colors_returns_requested_k():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[0:100, :] = (0, 100, 100)    # One color in HSV
    img[100:200, :] = (60, 100, 100)  # Another color in HSV
    ranges = discover_colors(img, k=2)
    assert len(ranges) == 2


def test_discover_colors_returns_valid_hsv_ranges(sample_color_image: np.ndarray):
    hsv = cv2.cvtColor(sample_color_image, cv2.COLOR_BGR2HSV)
    ranges = discover_colors(hsv, k=3)
    for r in ranges:
        assert 0 <= r.lower[0] <= 179
        assert 0 <= r.upper[0] <= 179
        assert r.name != ""
