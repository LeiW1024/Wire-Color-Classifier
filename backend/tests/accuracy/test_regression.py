"""Accuracy regression gate — fails CI if detection drops below 80%."""
from __future__ import annotations

import os

import cv2
import numpy as np
import pytest

from app.sam_pipeline import analyze_image_sam


def _sam_model_available() -> bool:
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "models", "sam_vit_b.pth"
    )
    return os.path.exists(path)


def _create_synthetic_wire_image():
    """Synthetic image with known wire colors and counts."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 200  # light gray background
    cv2.line(img, (20, 60),  (380, 60),  (0, 0, 255), 6)   # red
    cv2.line(img, (20, 120), (380, 120), (0, 0, 255), 6)   # red
    cv2.line(img, (20, 180), (380, 180), (0, 0, 255), 6)   # red
    cv2.line(img, (20, 250), (380, 250), (255, 0, 0), 6)   # blue
    cv2.line(img, (20, 310), (380, 310), (255, 0, 0), 6)   # blue
    cv2.line(img, (20, 370), (380, 370), (0, 255, 0), 6)   # green
    expected = {"red": 3, "blue": 2, "green": 1}
    return img, expected


@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_accuracy_above_80_percent():
    """CI gate: wire detection must be ≥80% accurate on synthetic image."""
    image, expected = _create_synthetic_wire_image()
    result = analyze_image_sam(image)

    total_expected = sum(expected.values())
    total_detected = result["total_wires"]
    accuracy = min(total_detected, total_expected) / total_expected if total_expected > 0 else 1.0

    assert accuracy >= 0.80, (
        f"Accuracy {accuracy:.1%} below 80% threshold. "
        f"Expected {total_expected} wires, detected {total_detected}."
    )


@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_no_phantom_colors_on_blank():
    """No wire colors should be detected on a plain white image."""
    blank = np.ones((200, 200, 3), dtype=np.uint8) * 230
    result = analyze_image_sam(blank)
    assert result["total_wires"] == 0, (
        f"Detected {result['total_wires']} phantom wires on blank image"
    )


@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_response_metrics_are_valid():
    """Metric fields must be in valid ranges."""
    image, _ = _create_synthetic_wire_image()
    result = analyze_image_sam(image)

    assert 0.0 <= result["avg_confidence"] <= 100.0
    assert 0.0 <= result["wire_coverage_pct"] <= 100.0
    assert result["processing_time_ms"] > 0
    assert result["segments_analyzed"] >= 0
