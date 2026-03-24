"""Tests for SAM-based wire color detection pipeline."""
from __future__ import annotations

import os

import cv2
import numpy as np
import pytest

from app.sam_pipeline import _classify_color, _is_wire_like, analyze_image_sam

IMAGE_AREA = 640 * 480  # reference area for wire-like tests


def _sam_model_available() -> bool:
    """Check if SAM model weights are available."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "models", "sam_vit_b.pth"
    )
    return os.path.exists(path)


# ── Color classification ──────────────────────────────────────────────────────

def test_classify_color_red():
    hsv = np.repeat(np.array([[[5, 200, 200]]], dtype=np.uint8), 100, axis=0)
    assert _classify_color(hsv.reshape(-1, 3)) == "red"


def test_classify_color_blue():
    hsv = np.repeat(np.array([[[110, 200, 200]]], dtype=np.uint8), 100, axis=0)
    assert _classify_color(hsv.reshape(-1, 3)) == "blue"


def test_classify_color_green():
    hsv = np.repeat(np.array([[[60, 200, 200]]], dtype=np.uint8), 100, axis=0)
    assert _classify_color(hsv.reshape(-1, 3)) == "green"


def test_classify_color_yellow():
    hsv = np.repeat(np.array([[[30, 200, 200]]], dtype=np.uint8), 100, axis=0)
    assert _classify_color(hsv.reshape(-1, 3)) == "yellow"


def test_classify_color_returns_none_for_low_saturation():
    """Very low saturation pixels should not match a strong color."""
    rng = np.random.RandomState(42)
    hsv = rng.randint(0, 180, size=(100, 3), dtype=np.uint8)
    hsv[:, 1] = 10   # near-zero saturation
    hsv[:, 2] = 128
    color = _classify_color(hsv)
    assert color in (None, "gray", "white", "black")


# ── Wire-like shape filter ────────────────────────────────────────────────────

def test_is_wire_like_elongated():
    mask = {"bbox": [0, 0, 200, 10], "area": 2000}
    assert _is_wire_like(mask, IMAGE_AREA) is True


def test_is_wire_like_square_rejected():
    mask = {"bbox": [0, 0, 50, 50], "area": 2500}
    assert _is_wire_like(mask, IMAGE_AREA) is False


def test_is_wire_like_zero_dimension_rejected():
    mask = {"bbox": [0, 0, 0, 50], "area": 0}
    assert _is_wire_like(mask, IMAGE_AREA) is False


def test_is_wire_like_too_large_rejected():
    """Segments covering >8% of the image are background, not wires."""
    large_area = int(IMAGE_AREA * 0.10)
    mask = {"bbox": [0, 0, 400, 200], "area": large_area}
    assert _is_wire_like(mask, IMAGE_AREA) is False


def test_is_wire_like_tiny_rejected():
    """Segments smaller than 150 px are noise."""
    mask = {"bbox": [0, 0, 20, 5], "area": 100}
    assert _is_wire_like(mask, IMAGE_AREA) is False


# ── Full SAM pipeline (requires model weights) ────────────────────────────────

@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_sam_pipeline_returns_expected_schema():
    """analyze_image_sam returns all required fields with correct types."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 200
    cv2.line(img, (20, 100), (380, 100), (0, 0, 255), 8)   # red
    cv2.line(img, (20, 200), (380, 200), (255, 0, 0), 8)   # blue
    cv2.line(img, (20, 300), (380, 300), (0, 255, 0), 8)   # green

    result = analyze_image_sam(img)

    assert "colors_found" in result
    assert "wire_counts" in result
    assert "total_wires" in result
    assert "bounding_boxes" in result
    assert "annotated_image" in result
    assert "processing_time_ms" in result
    assert "segments_analyzed" in result
    assert "avg_confidence" in result
    assert "wire_coverage_pct" in result
    assert isinstance(result["annotated_image"], str)
    assert isinstance(result["processing_time_ms"], int)
    assert 0.0 <= result["avg_confidence"] <= 100.0
    assert 0.0 <= result["wire_coverage_pct"] <= 100.0
