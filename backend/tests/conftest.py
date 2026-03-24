import cv2
import numpy as np
import pytest


@pytest.fixture
def sample_color_image() -> np.ndarray:
    """A 200x200 image with red, blue, and green rectangles."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[0:60, 0:200] = (0, 0, 255)    # Red (BGR)
    img[70:130, 0:200] = (255, 0, 0)   # Blue (BGR)
    img[140:200, 0:200] = (0, 255, 0)  # Green (BGR)
    return img


@pytest.fixture
def blank_image() -> np.ndarray:
    """A plain white 200x200 image with no wires."""
    return np.ones((200, 200, 3), dtype=np.uint8) * 255


@pytest.fixture
def single_red_wire_image() -> np.ndarray:
    """A white image with a single thin red horizontal line (simulating a wire)."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    cv2.line(img, (10, 100), (190, 100), (0, 0, 255), 3)
    return img
