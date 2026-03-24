# backend/tests/unit/test_augmentation.py
import numpy as np

from app.augmentation import augment_image


def test_augment_returns_valid_image(sample_color_image: np.ndarray):
    result = augment_image(sample_color_image)
    assert result.shape[2] == 3
    assert result.dtype == np.uint8


def test_augment_preserves_dimensions(sample_color_image: np.ndarray):
    result = augment_image(sample_color_image)
    assert result.shape == sample_color_image.shape


def test_augment_produces_different_image(sample_color_image: np.ndarray):
    result = augment_image(sample_color_image, seed=42)
    # The augmented image should differ from the original
    assert not np.array_equal(result, sample_color_image)


def test_augment_batch_produces_multiple(sample_color_image: np.ndarray):
    from app.augmentation import augment_batch
    results = augment_batch(sample_color_image, count=5)
    assert len(results) == 5
    assert all(r.shape == sample_color_image.shape for r in results)
