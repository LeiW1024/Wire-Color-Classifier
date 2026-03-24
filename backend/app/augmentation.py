from __future__ import annotations

import cv2
import numpy as np


def augment_image(image: np.ndarray, seed: int | None = None) -> np.ndarray:
    """Apply random augmentations to an image."""
    rng = np.random.RandomState(seed)
    result = image.copy()

    # Random brightness adjustment
    brightness = rng.uniform(0.7, 1.3)
    result = np.clip(result * brightness, 0, 255).astype(np.uint8)

    # Random rotation
    angle = rng.uniform(-30, 30)
    h, w = result.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    result = cv2.warpAffine(result, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)

    # Random horizontal flip
    if rng.random() > 0.5:
        result = cv2.flip(result, 1)

    # Random Gaussian noise
    noise = rng.normal(0, 10, result.shape).astype(np.int16)
    result = np.clip(result.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return result


def augment_batch(image: np.ndarray, count: int = 50) -> list[np.ndarray]:
    """Generate multiple augmented versions of an image."""
    return [augment_image(image, seed=i) for i in range(count)]
