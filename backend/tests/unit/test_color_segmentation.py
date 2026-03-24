# backend/tests/unit/test_color_segmentation.py
import cv2
import numpy as np

from app.color_segmentation import segment_by_color, HSVRange


def test_segment_red_from_multicolor_image(sample_color_image: np.ndarray):
    hsv = cv2.cvtColor(sample_color_image, cv2.COLOR_BGR2HSV)
    red_range = HSVRange(name="red", lower=(0, 100, 100), upper=(10, 255, 255))
    mask = segment_by_color(hsv, red_range)
    assert mask.shape == (200, 200)
    # Red region (rows 0-60) should have white pixels
    assert mask[30, 100] == 255
    # Blue region should have no pixels
    assert mask[100, 100] == 0


def test_segment_returns_empty_mask_for_absent_color(sample_color_image: np.ndarray):
    hsv = cv2.cvtColor(sample_color_image, cv2.COLOR_BGR2HSV)
    # Yellow is not in the image
    yellow_range = HSVRange(name="yellow", lower=(20, 100, 100), upper=(35, 255, 255))
    mask = segment_by_color(hsv, yellow_range)
    assert mask.sum() == 0


def test_segment_applies_morphological_cleanup(single_red_wire_image: np.ndarray):
    hsv = cv2.cvtColor(single_red_wire_image, cv2.COLOR_BGR2HSV)
    red_range = HSVRange(name="red", lower=(0, 100, 100), upper=(10, 255, 255))
    mask = segment_by_color(hsv, red_range)
    # After morphological ops, mask should still contain the wire
    assert mask.sum() > 0
