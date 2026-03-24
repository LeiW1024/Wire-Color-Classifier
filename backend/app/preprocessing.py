# backend/app/preprocessing.py
import cv2
import numpy as np


def preprocess_image(
    image: np.ndarray,
    max_dimension: int = 800,
    blur_kernel: tuple = (5, 5),
) -> np.ndarray:
    """Resize, blur, and convert BGR image to HSV."""
    h, w = image.shape[:2]
    if max(h, w) > max_dimension:
        scale = max_dimension / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    blurred = cv2.GaussianBlur(image, blur_kernel, 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    return hsv
