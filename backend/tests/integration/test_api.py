import io

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_test_image() -> bytes:
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (90, 50), (0, 0, 255), -1)
    _, buffer = cv2.imencode(".png", img)
    return buffer.tobytes()


def test_analyze_endpoint_returns_json():
    image_bytes = _make_test_image()
    response = client.post(
        "/api/analyze",
        files={"file": ("test.png", io.BytesIO(image_bytes), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "colors_found" in data
    assert "wire_counts" in data
    assert "total_wires" in data
    assert "bounding_boxes" in data
    assert "annotated_image" in data


def test_analyze_rejects_non_image():
    response = client.post(
        "/api/analyze",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 400


def test_colors_endpoint_returns_list():
    response = client.get("/api/colors")
    assert response.status_code == 200
    data = response.json()
    assert "colors" in data
