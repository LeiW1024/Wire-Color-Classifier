# backend/app/color_discovery.py
import numpy as np
from sklearn.cluster import KMeans

from app.color_segmentation import HSVRange


# Map hue ranges to color names
HUE_NAMES = [
    (0, 10, "red"),
    (10, 25, "orange"),
    (25, 35, "yellow"),
    (35, 85, "green"),
    (85, 130, "blue"),
    (130, 160, "purple"),
    (160, 179, "red"),
]


def _hue_to_name(hue: int) -> str:
    """Map an HSV hue value to a human-readable color name."""
    for low, high, name in HUE_NAMES:
        if low <= hue <= high:
            return name
    return f"color_{hue}"


def discover_colors(hsv_image: np.ndarray, k: int = 8) -> list:
    """Use K-means clustering to discover dominant colors in an HSV image."""
    pixels = hsv_image.reshape(-1, 3).astype(np.float32)

    # Filter out very dark (background) and very bright (white) pixels
    mask = (pixels[:, 1] > 30) & (pixels[:, 2] > 30)
    filtered = pixels[mask]

    if len(filtered) < k:
        return []

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(filtered)
    centers = kmeans.cluster_centers_

    ranges = []
    used_names = {}

    for center in centers:
        h, s, v = int(center[0]), int(center[1]), int(center[2])
        base_name = _hue_to_name(h)

        # Deduplicate names
        if base_name in used_names:
            used_names[base_name] += 1
            name = f"{base_name}_{used_names[base_name]}"
        else:
            used_names[base_name] = 0
            name = base_name

        # Create range with tolerance around center
        h_tol, s_tol, v_tol = 10, 50, 50
        lower = (max(0, h - h_tol), max(0, s - s_tol), max(0, v - v_tol))
        upper = (min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol))

        ranges.append(HSVRange(name=name, lower=lower, upper=upper))

    return ranges
