"""Tests for SAM-based wire color detection pipeline."""
import os

import cv2
import numpy as np
import pytest

from app.sam_pipeline import _classify_color, _is_wire_like, analyze_image_sam


def _sam_model_available() -> bool:
    """Check if SAM model weights are available."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "models", "sam_vit_b.pth"
    )
    return os.path.exists(path)


def test_classify_color_red():
    """Red pixels should be classified as red."""
    # Create a small HSV region that is red (hue ~0)
    hsv = np.array([[[5, 200, 200]]], dtype=np.uint8)
    hsv = np.repeat(hsv, 100, axis=0)
    color = _classify_color(hsv.reshape(-1, 3))
    assert color == "red"


def test_classify_color_blue():
    """Blue pixels should be classified as blue."""
    hsv = np.array([[[110, 200, 200]]], dtype=np.uint8)
    hsv = np.repeat(hsv, 100, axis=0)
    color = _classify_color(hsv.reshape(-1, 3))
    assert color == "blue"


def test_classify_color_green():
    """Green pixels should be classified as green."""
    hsv = np.array([[[60, 200, 200]]], dtype=np.uint8)
    hsv = np.repeat(hsv, 100, axis=0)
    color = _classify_color(hsv.reshape(-1, 3))
    assert color == "green"


def test_classify_color_returns_none_for_mixed():
    """Mixed/ambiguous pixels return None if no color dominates."""
    # Random noise - no dominant color
    rng = np.random.RandomState(42)
    hsv = rng.randint(0, 180, size=(100, 3), dtype=np.uint8)
    hsv[:, 1] = 10  # Very low saturation = no clear color
    hsv[:, 2] = 128
    color = _classify_color(hsv)
    # Should be None or a neutral color since saturation is very low
    assert color in (None, "gray", "white", "black")


def test_is_wire_like_elongated():
    """Elongated mask should be wire-like."""
    mask = {"bbox": [0, 0, 200, 10], "area": 2000}
    assert _is_wire_like(mask) is True


def test_is_wire_like_square_is_not_wire():
    """Square mask should not be wire-like."""
    mask = {"bbox": [0, 0, 50, 50], "area": 2500}
    assert _is_wire_like(mask) is False


def test_is_wire_like_zero_dimension():
    """Zero dimension mask should not be wire-like."""
    mask = {"bbox": [0, 0, 0, 50], "area": 0}
    assert _is_wire_like(mask) is False


@pytest.mark.skipif(
    not _sam_model_available(),
    reason="SAM model not downloaded"
)
def test_sam_pipeline_on_synthetic_image():
    """SAM pipeline returns expected structure on synthetic image."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 200
    # Draw thick colored lines
    cv2.line(img, (20, 100), (380, 100), (0, 0, 255), 8)  # Red
    cv2.line(img, (20, 200), (380, 200), (255, 0, 0), 8)  # Blue
    cv2.line(img, (20, 300), (380, 300), (0, 255, 0), 8)  # Green

    result = analyze_image_sam(img)
    assert "colors_found" in result
    assert "wire_counts" in result
    assert "total_wires" in result
    assert "bounding_boxes" in result
    assert "annotated_image" in result
    assert isinstance(result["annotated_image"], str)


