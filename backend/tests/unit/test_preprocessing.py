# backend/tests/unit/test_preprocessing.py
import numpy as np

from app.preprocessing import preprocess_image


def test_preprocess_returns_hsv_image(sample_color_image: np.ndarray):
    result = preprocess_image(sample_color_image)
    assert result.shape[2] == 3  # Still 3 channels
    # HSV hue range is 0-179 in OpenCV
    assert result[:, :, 0].max() <= 179


def test_preprocess_resizes_large_image():
    large_img = np.zeros((2000, 3000, 3), dtype=np.uint8)
    result = preprocess_image(large_img, max_dimension=800)
    assert max(result.shape[0], result.shape[1]) <= 800


def test_preprocess_keeps_small_image_size(sample_color_image: np.ndarray):
    result = preprocess_image(sample_color_image, max_dimension=800)
    assert result.shape[0] == 200
    assert result.shape[1] == 200
