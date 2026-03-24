# Wire Color Classifier — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web app that detects, counts, and highlights colored wires in industrial images using classical computer vision.

**Architecture:** Python/FastAPI backend with OpenCV for HSV color segmentation, contour detection, and bounding box generation. Next.js/React frontend for image upload and results display. Docker Compose for deployment. GitHub Actions for CI/CD.

**Tech Stack:** Python 3.11, FastAPI, OpenCV, NumPy, scikit-learn (K-means), Next.js 14, React, TypeScript, Docker, GitHub Actions, pytest, Jest, Playwright

---

## File Map

### Backend (`backend/`)

| File | Responsibility |
|------|---------------|
| `app/__init__.py` | Package marker |
| `app/main.py` | FastAPI app, CORS, route registration |
| `app/routes.py` | API endpoint handlers (`/api/analyze`, `/api/calibrate`, `/api/colors`) |
| `app/models.py` | Pydantic request/response schemas |
| `app/color_segmentation.py` | HSV range definitions, `cv2.inRange()` masking, morphological ops |
| `app/contour_detection.py` | `cv2.findContours()`, area filtering, bounding box generation |
| `app/color_discovery.py` | K-means clustering to auto-discover wire colors from images |
| `app/pipeline.py` | Orchestrates preprocessing → segmentation → contours → results |
| `app/preprocessing.py` | Resize, blur, BGR→HSV conversion |
| `app/augmentation.py` | Data augmentation transforms (rotation, flip, brightness, etc.) |
| `app/config.py` | Environment-based configuration (MIN_CONTOUR_AREA, K_CLUSTERS, etc.) |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Ruff + pytest configuration |
| `Dockerfile` | Multi-stage Python + OpenCV image |

### Backend Tests (`backend/tests/`)

| File | What It Tests |
|------|--------------|
| `conftest.py` | Shared fixtures: sample images, blank image, ground truth |
| `unit/test_preprocessing.py` | Resize, blur, color conversion |
| `unit/test_color_segmentation.py` | HSV masking, morphological ops |
| `unit/test_contour_detection.py` | Contour finding, filtering, bounding boxes |
| `unit/test_color_discovery.py` | K-means clustering |
| `unit/test_augmentation.py` | Image transforms |
| `integration/test_pipeline.py` | Full pipeline end-to-end |
| `integration/test_api.py` | HTTP endpoint request/response |
| `accuracy/test_regression.py` | Accuracy gate (>= 80%) |

### Frontend (`frontend/`)

| File | Responsibility |
|------|---------------|
| `src/app/page.tsx` | Main page — upload + results layout |
| `src/app/layout.tsx` | Root layout |
| `src/app/globals.css` | Global styles |
| `src/components/ImageUpload.tsx` | Drag-and-drop / file select upload |
| `src/components/ResultsView.tsx` | Annotated image display with bounding boxes |
| `src/components/ColorTable.tsx` | Color list with wire counts |
| `src/lib/api.ts` | API client (`analyzeImage()`, `getColors()`) |
| `src/lib/types.ts` | TypeScript interfaces for API responses |
| `package.json` | Dependencies + scripts |
| `tsconfig.json` | TypeScript config |
| `jest.config.ts` | Jest config |
| `playwright.config.ts` | Playwright config |
| `Dockerfile` | Multi-stage Node + standalone build |

### Frontend Tests

| File | What It Tests |
|------|--------------|
| `__tests__/components/ImageUpload.test.tsx` | Upload render, file selection, validation |
| `__tests__/components/ResultsView.test.tsx` | Annotated image display |
| `__tests__/components/ColorTable.test.tsx` | Color list rendering |
| `__tests__/api/client.test.ts` | API client request/response |
| `e2e/analyze-flow.spec.ts` | Full upload → analyze → display flow |

### Root Files

| File | Responsibility |
|------|---------------|
| `docker-compose.yml` | Backend + frontend services |
| `.gitignore` | Ignore node_modules, __pycache__, .env, data/augmented/ |
| `.github/workflows/backend-ci.yml` | Backend lint + test + coverage |
| `.github/workflows/frontend-ci.yml` | Frontend lint + test + coverage |
| `.github/workflows/e2e.yml` | Playwright E2E tests |
| `.github/workflows/deploy.yml` | Build + deploy on merge to main |

---

## Task 1: Project Scaffolding & Git Init

**Files:**
- Create: `.gitignore`, `backend/requirements.txt`, `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/app/config.py`, `frontend/package.json`, `frontend/tsconfig.json`

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier
git init
git checkout -b main
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/
.coverage
htmlcov/

# Node
node_modules/
.next/
out/

# Environment
.env
.env.local

# Data
data/augmented/

# OS
.DS_Store
```

- [ ] **Step 3: Create backend/requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
opencv-python-headless==4.10.0.84
numpy==1.26.4
scikit-learn==1.5.1
pydantic==2.9.0
```

- [ ] **Step 4: Create backend/pyproject.toml**

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 5: Create backend/app/__init__.py**

```python
```

- [ ] **Step 6: Create backend/app/config.py**

```python
import os


MIN_CONTOUR_AREA: int = int(os.environ.get("MIN_CONTOUR_AREA", "100"))
DEFAULT_K_CLUSTERS: int = int(os.environ.get("DEFAULT_K_CLUSTERS", "8"))
ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
```

- [ ] **Step 7: Initialize Next.js frontend**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier
npx create-next-app@14 frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
```

- [ ] **Step 8: Create data directories**

```bash
mkdir -p data/raw data/augmented data/ground_truth
echo "*\n!.gitkeep" > data/raw/.gitignore
echo "*\n!.gitkeep" > data/augmented/.gitignore
echo "*\n!.gitkeep" > data/ground_truth/.gitignore
```

- [ ] **Step 9: Commit**

```bash
git add .gitignore backend/requirements.txt backend/pyproject.toml backend/app/__init__.py backend/app/config.py frontend/ data/ CLAUDE.md rules/ docs/
git commit -m "chore: scaffold project structure with backend, frontend, and config"
```

---

## Task 2: Backend — Preprocessing Module

**Files:**
- Create: `backend/app/preprocessing.py`
- Test: `backend/tests/unit/test_preprocessing.py`
- Create: `backend/tests/__init__.py`, `backend/tests/unit/__init__.py`, `backend/tests/conftest.py`

- [ ] **Step 1: Create test scaffolding files**

```bash
touch backend/tests/__init__.py backend/tests/unit/__init__.py
```

- [ ] **Step 2: Create conftest.py with shared fixtures**

```python
# backend/tests/conftest.py
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
    cv2.line(img, (10, 100), (190, 100), (0, 0, 255), 3)  # Red line, 3px thick
    return img
```

- [ ] **Step 3: Write failing test for preprocessing**

```python
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
```

- [ ] **Step 4: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_preprocessing.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.preprocessing'`

- [ ] **Step 5: Write minimal implementation**

```python
# backend/app/preprocessing.py
import cv2
import numpy as np


def preprocess_image(
    image: np.ndarray,
    max_dimension: int = 800,
    blur_kernel: tuple[int, int] = (5, 5),
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
```

- [ ] **Step 6: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_preprocessing.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/preprocessing.py backend/tests/
git commit -m "feat(backend): add image preprocessing module with HSV conversion"
```

---

## Task 3: Backend — Color Segmentation Module

**Files:**
- Create: `backend/app/color_segmentation.py`
- Test: `backend/tests/unit/test_color_segmentation.py`

- [ ] **Step 1: Write failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_color_segmentation.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/app/color_segmentation.py
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class HSVRange:
    """Defines an HSV color range for segmentation."""
    name: str
    lower: tuple[int, int, int]
    upper: tuple[int, int, int]


def segment_by_color(hsv_image: np.ndarray, color_range: HSVRange) -> np.ndarray:
    """Create a binary mask for pixels within the given HSV range."""
    lower = np.array(color_range.lower, dtype=np.uint8)
    upper = np.array(color_range.upper, dtype=np.uint8)

    mask = cv2.inRange(hsv_image, lower, upper)

    # Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_color_segmentation.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/color_segmentation.py backend/tests/unit/test_color_segmentation.py
git commit -m "feat(backend): add HSV color segmentation with morphological cleanup"
```

---

## Task 4: Backend — Contour Detection Module

**Files:**
- Create: `backend/app/contour_detection.py`
- Test: `backend/tests/unit/test_contour_detection.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/unit/test_contour_detection.py
import cv2
import numpy as np

from app.contour_detection import detect_contours, BoundingBox


def test_detect_contours_finds_rectangle():
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(mask, (50, 50), (150, 80), 255, -1)  # Filled white rect
    boxes = detect_contours(mask, min_area=100)
    assert len(boxes) == 1
    assert boxes[0].x >= 50
    assert boxes[0].y >= 50
    assert boxes[0].w <= 101
    assert boxes[0].h <= 31


def test_detect_contours_filters_small_noise():
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.rectangle(mask, (50, 50), (150, 80), 255, -1)  # Large rect
    cv2.rectangle(mask, (10, 10), (12, 12), 255, -1)    # Tiny noise (4px area)
    boxes = detect_contours(mask, min_area=100)
    assert len(boxes) == 1  # Only the large rectangle


def test_detect_contours_returns_empty_on_blank():
    mask = np.zeros((200, 200), dtype=np.uint8)
    boxes = detect_contours(mask, min_area=100)
    assert len(boxes) == 0


def test_bounding_box_has_area():
    box = BoundingBox(x=10, y=20, w=50, h=30)
    assert box.area == 1500
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_contour_detection.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/app/contour_detection.py
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class BoundingBox:
    """Bounding box for a detected wire region."""
    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return self.w * self.h


def detect_contours(mask: np.ndarray, min_area: int = 100) -> list[BoundingBox]:
    """Find contours in a binary mask and return bounding boxes, filtering by area."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes: list[BoundingBox] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(contour)
            boxes.append(BoundingBox(x=x, y=y, w=w, h=h))

    return boxes
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_contour_detection.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/contour_detection.py backend/tests/unit/test_contour_detection.py
git commit -m "feat(backend): add contour detection with area filtering and bounding boxes"
```

---

## Task 5: Backend — Color Discovery (K-Means)

**Files:**
- Create: `backend/app/color_discovery.py`
- Test: `backend/tests/unit/test_color_discovery.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/unit/test_color_discovery.py
import cv2
import numpy as np

from app.color_discovery import discover_colors
from app.color_segmentation import HSVRange


def test_discover_colors_finds_three_in_multicolor(sample_color_image: np.ndarray):
    hsv = cv2.cvtColor(sample_color_image, cv2.COLOR_BGR2HSV)
    ranges = discover_colors(hsv, k=3)
    assert len(ranges) == 3
    assert all(isinstance(r, HSVRange) for r in ranges)


def test_discover_colors_returns_requested_k():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[0:100, :] = (0, 100, 100)    # One color in HSV
    img[100:200, :] = (60, 100, 100)  # Another color in HSV
    ranges = discover_colors(img, k=2)
    assert len(ranges) == 2


def test_discover_colors_returns_valid_hsv_ranges(sample_color_image: np.ndarray):
    hsv = cv2.cvtColor(sample_color_image, cv2.COLOR_BGR2HSV)
    ranges = discover_colors(hsv, k=3)
    for r in ranges:
        assert 0 <= r.lower[0] <= 179
        assert 0 <= r.upper[0] <= 179
        assert r.name != ""
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_color_discovery.py -v
```

Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
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


def discover_colors(hsv_image: np.ndarray, k: int = 8) -> list[HSVRange]:
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

    ranges: list[HSVRange] = []
    used_names: dict[str, int] = {}

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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_color_discovery.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/color_discovery.py backend/tests/unit/test_color_discovery.py
git commit -m "feat(backend): add K-means color discovery for auto-detecting wire colors"
```

---

## Task 6: Backend — Pydantic Models

**Files:**
- Create: `backend/app/models.py`

- [ ] **Step 1: Write the models**

```python
# backend/app/models.py
from pydantic import BaseModel


class BoundingBoxResponse(BaseModel):
    color: str
    x: int
    y: int
    w: int
    h: int


class AnalyzeResponse(BaseModel):
    colors_found: list[str]
    wire_counts: dict[str, int]
    total_wires: int
    bounding_boxes: list[BoundingBoxResponse]
    annotated_image: str  # base64 encoded


class ColorRangeResponse(BaseModel):
    name: str
    lower: tuple[int, int, int]
    upper: tuple[int, int, int]


class ColorsResponse(BaseModel):
    colors: list[ColorRangeResponse]
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models.py
git commit -m "feat(backend): add Pydantic request/response models"
```

---

## Task 7: Backend — Processing Pipeline

**Files:**
- Create: `backend/app/pipeline.py`
- Test: `backend/tests/integration/test_pipeline.py`
- Create: `backend/tests/integration/__init__.py`

- [ ] **Step 1: Create integration test directory**

```bash
touch backend/tests/integration/__init__.py
```

- [ ] **Step 2: Write failing test**

```python
# backend/tests/integration/test_pipeline.py
import cv2
import numpy as np

from app.pipeline import analyze_image


def test_pipeline_returns_colors_and_counts(sample_color_image: np.ndarray):
    result = analyze_image(sample_color_image)
    assert len(result["colors_found"]) > 0
    assert result["total_wires"] > 0
    assert isinstance(result["wire_counts"], dict)
    assert isinstance(result["bounding_boxes"], list)
    assert isinstance(result["annotated_image"], str)  # base64


def test_pipeline_handles_blank_image(blank_image: np.ndarray):
    result = analyze_image(blank_image)
    assert result["total_wires"] == 0
    assert len(result["colors_found"]) == 0
    assert result["bounding_boxes"] == []


def test_pipeline_bounding_boxes_match_counts(sample_color_image: np.ndarray):
    result = analyze_image(sample_color_image)
    total_from_boxes = len(result["bounding_boxes"])
    total_from_counts = sum(result["wire_counts"].values())
    assert total_from_boxes == total_from_counts == result["total_wires"]
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/integration/test_pipeline.py -v
```

Expected: FAIL

- [ ] **Step 4: Write minimal implementation**

```python
# backend/app/pipeline.py
import base64
from typing import Any

import cv2
import numpy as np

from app.color_discovery import discover_colors
from app.color_segmentation import HSVRange, segment_by_color
from app.config import DEFAULT_K_CLUSTERS, MIN_CONTOUR_AREA
from app.contour_detection import detect_contours
from app.preprocessing import preprocess_image

# Module-level mutable state for calibrated color ranges
_current_ranges: list[HSVRange] = []


def get_color_ranges() -> list[HSVRange]:
    """Return the current calibrated color ranges."""
    return _current_ranges


def set_color_ranges(ranges: list[HSVRange]) -> None:
    """Update the calibrated color ranges."""
    global _current_ranges
    _current_ranges = ranges


def analyze_image(
    image: np.ndarray,
    color_ranges: list[HSVRange] | None = None,
) -> dict[str, Any]:
    """Run the full wire color detection pipeline on an image."""
    hsv = preprocess_image(image)

    # Discover colors if none provided
    if color_ranges is None:
        color_ranges = _current_ranges if _current_ranges else discover_colors(
            hsv, k=DEFAULT_K_CLUSTERS
        )

    colors_found: list[str] = []
    wire_counts: dict[str, int] = {}
    all_boxes: list[dict[str, Any]] = []
    annotated = image.copy()

    for color_range in color_ranges:
        mask = segment_by_color(hsv, color_range)
        boxes = detect_contours(mask, min_area=MIN_CONTOUR_AREA)

        if boxes:
            colors_found.append(color_range.name)
            wire_counts[color_range.name] = len(boxes)

            # Draw bounding boxes on annotated image
            for box in boxes:
                cv2.rectangle(
                    annotated,
                    (box.x, box.y),
                    (box.x + box.w, box.y + box.h),
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    annotated,
                    color_range.name,
                    (box.x, box.y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
                all_boxes.append({
                    "color": color_range.name,
                    "x": box.x,
                    "y": box.y,
                    "w": box.w,
                    "h": box.h,
                })

    # Encode annotated image to base64
    _, buffer = cv2.imencode(".png", annotated)
    annotated_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "colors_found": colors_found,
        "wire_counts": wire_counts,
        "total_wires": sum(wire_counts.values()),
        "bounding_boxes": all_boxes,
        "annotated_image": annotated_b64,
    }
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/integration/test_pipeline.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/pipeline.py backend/tests/integration/
git commit -m "feat(backend): add full processing pipeline orchestrating all CV modules"
```

---

## Task 8: Backend — FastAPI Endpoints

**Files:**
- Create: `backend/app/main.py`, `backend/app/routes.py`
- Test: `backend/tests/integration/test_api.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/integration/test_api.py
import io

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_test_image() -> bytes:
    """Create a simple test image as PNG bytes."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(img, (10, 10), (90, 50), (0, 0, 255), -1)  # Red rect
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/integration/test_api.py -v
```

Expected: FAIL

- [ ] **Step 3: Write routes.py**

```python
# backend/app/routes.py
import io

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.color_discovery import discover_colors
from app.models import AnalyzeResponse, ColorsResponse, ColorRangeResponse
from app.pipeline import analyze_image, get_color_ranges, set_color_ranges
from app.preprocessing import preprocess_image
from app.config import DEFAULT_K_CLUSTERS

router = APIRouter(prefix="/api")

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


async def _read_image(file: UploadFile) -> np.ndarray:
    """Read an uploaded file and decode it as an OpenCV image."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="File must be an image (PNG, JPEG, WebP)")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

    return image


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    """Upload an image and get wire color detection results."""
    image = await _read_image(file)
    result = analyze_image(image)
    return AnalyzeResponse(**result)


@router.post("/calibrate")
async def calibrate(file: UploadFile = File(...)):
    """Upload a reference image to discover and set color ranges."""
    image = await _read_image(file)
    hsv = preprocess_image(image)
    ranges = discover_colors(hsv, k=DEFAULT_K_CLUSTERS)
    set_color_ranges(ranges)
    return {"message": f"Discovered {len(ranges)} colors", "colors": [r.name for r in ranges]}


@router.get("/colors", response_model=ColorsResponse)
async def get_colors():
    """Return current color definitions and HSV ranges."""
    ranges = get_color_ranges()
    return ColorsResponse(
        colors=[
            ColorRangeResponse(name=r.name, lower=r.lower, upper=r.upper)
            for r in ranges
        ]
    )
```

- [ ] **Step 4: Write main.py**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

app = FastAPI(title="Wire Color Classifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/integration/test_api.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/main.py backend/app/routes.py backend/tests/integration/test_api.py
git commit -m "feat(backend): add FastAPI endpoints for analyze, calibrate, and colors"
```

---

## Task 9: Backend — Data Augmentation Module

**Files:**
- Create: `backend/app/augmentation.py`
- Test: `backend/tests/unit/test_augmentation.py`

- [ ] **Step 1: Write failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_augmentation.py -v
```

Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/app/augmentation.py
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/unit/test_augmentation.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/augmentation.py backend/tests/unit/test_augmentation.py
git commit -m "feat(backend): add data augmentation module for generating training variations"
```

---

## Task 10: Frontend — TypeScript Types & API Client

**Files:**
- Create: `frontend/src/lib/types.ts`, `frontend/src/lib/api.ts`
- Test: `frontend/__tests__/api/client.test.ts`

- [ ] **Step 1: Create types**

```typescript
// frontend/src/lib/types.ts
export interface BoundingBox {
  color: string
  x: number
  y: number
  w: number
  h: number
}

export interface AnalyzeResponse {
  colors_found: string[]
  wire_counts: Record<string, number>
  total_wires: number
  bounding_boxes: BoundingBox[]
  annotated_image: string
}

export interface ColorRange {
  name: string
  lower: [number, number, number]
  upper: [number, number, number]
}

export interface ColorsResponse {
  colors: ColorRange[]
}
```

- [ ] **Step 2: Write failing test for API client**

```typescript
// frontend/__tests__/api/client.test.ts
import { analyzeImage, getColors } from '@/lib/api'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('API Client', () => {
  afterEach(() => {
    mockFetch.mockReset()
  })

  test('analyzeImage sends file as FormData', async () => {
    const mockResponse = {
      colors_found: ['red'],
      wire_counts: { red: 1 },
      total_wires: 1,
      bounding_boxes: [],
      annotated_image: 'base64data',
    }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    const result = await analyzeImage(file)

    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toContain('/api/analyze')
    expect(options.method).toBe('POST')
    expect(options.body).toBeInstanceOf(FormData)
    expect(result).toEqual(mockResponse)
  })

  test('analyzeImage throws on server error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    })

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    await expect(analyzeImage(file)).rejects.toThrow()
  })

  test('getColors returns color list', async () => {
    const mockResponse = { colors: [] }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const result = await getColors()
    expect(result).toEqual(mockResponse)
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/api/client.test.ts --no-cache
```

Expected: FAIL — module not found

- [ ] **Step 4: Write API client**

```typescript
// frontend/src/lib/api.ts
import { AnalyzeResponse, ColorsResponse } from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function getColors(): Promise<ColorsResponse> {
  const response = await fetch(`${API_BASE}/api/colors`)

  if (!response.ok) {
    throw new Error(`Failed to fetch colors: ${response.status}`)
  }

  return response.json()
}
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/api/client.test.ts --no-cache
```

Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/api.ts frontend/__tests__/api/
git commit -m "feat(frontend): add TypeScript types and API client"
```

---

## Task 11: Frontend — ImageUpload Component

**Files:**
- Create: `frontend/src/components/ImageUpload.tsx`
- Test: `frontend/__tests__/components/ImageUpload.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/__tests__/components/ImageUpload.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { ImageUpload } from '@/components/ImageUpload'

describe('ImageUpload', () => {
  test('renders upload area', () => {
    render(<ImageUpload onFileSelected={jest.fn()} />)
    expect(screen.getByText(/upload/i)).toBeInTheDocument()
  })

  test('calls onFileSelected with valid image', () => {
    const onFileSelected = jest.fn()
    render(<ImageUpload onFileSelected={onFileSelected} />)

    const input = screen.getByTestId('file-input')
    const file = new File(['test'], 'test.png', { type: 'image/png' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelected).toHaveBeenCalledWith(file)
  })

  test('shows loading state when isLoading is true', () => {
    render(<ImageUpload onFileSelected={jest.fn()} isLoading={true} />)
    expect(screen.getByText(/processing/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/components/ImageUpload.test.tsx --no-cache
```

Expected: FAIL

- [ ] **Step 3: Write component**

```typescript
// frontend/src/components/ImageUpload.tsx
'use client'

import { useCallback, useRef } from 'react'

interface ImageUploadProps {
  onFileSelected: (file: File) => void
  isLoading?: boolean
}

export function ImageUpload({ onFileSelected, isLoading = false }: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        onFileSelected(file)
      }
    },
    [onFileSelected]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const file = e.dataTransfer.files?.[0]
      if (file) {
        onFileSelected(file)
      }
    },
    [onFileSelected]
  )

  return (
    <div
      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      <input
        ref={inputRef}
        data-testid="file-input"
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={handleChange}
        className="hidden"
      />
      {isLoading ? (
        <p className="text-gray-500">Processing image...</p>
      ) : (
        <div>
          <p className="text-lg font-medium">Upload wire image</p>
          <p className="text-sm text-gray-500 mt-1">
            Drag and drop or click to select (PNG, JPEG, WebP)
          </p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/components/ImageUpload.test.tsx --no-cache
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ImageUpload.tsx frontend/__tests__/components/ImageUpload.test.tsx
git commit -m "feat(frontend): add ImageUpload component with drag-and-drop"
```

---

## Task 12: Frontend — ColorTable Component

**Files:**
- Create: `frontend/src/components/ColorTable.tsx`
- Test: `frontend/__tests__/components/ColorTable.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/__tests__/components/ColorTable.test.tsx
import { render, screen } from '@testing-library/react'
import { ColorTable } from '@/components/ColorTable'

describe('ColorTable', () => {
  test('renders all detected colors with counts', () => {
    const wireCounts = { red: 3, blue: 5, green: 2 }
    render(<ColorTable wireCounts={wireCounts} totalWires={10} />)

    expect(screen.getByText('red')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('blue')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  test('shows message when no colors detected', () => {
    render(<ColorTable wireCounts={{}} totalWires={0} />)
    expect(screen.getByText(/no colors detected/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/components/ColorTable.test.tsx --no-cache
```

Expected: FAIL

- [ ] **Step 3: Write component**

```typescript
// frontend/src/components/ColorTable.tsx
interface ColorTableProps {
  wireCounts: Record<string, number>
  totalWires: number
}

export function ColorTable({ wireCounts, totalWires }: ColorTableProps) {
  const entries = Object.entries(wireCounts)

  if (entries.length === 0) {
    return <p className="text-gray-500 text-center py-4">No colors detected</p>
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left font-medium">Color</th>
            <th className="px-4 py-2 text-right font-medium">Count</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([color, count]) => (
            <tr key={color} className="border-t border-gray-100">
              <td className="px-4 py-2">{color}</td>
              <td className="px-4 py-2 text-right">{count}</td>
            </tr>
          ))}
          <tr className="border-t-2 border-gray-300 font-bold">
            <td className="px-4 py-2">Total</td>
            <td className="px-4 py-2 text-right">{totalWires}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/components/ColorTable.test.tsx --no-cache
```

Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ColorTable.tsx frontend/__tests__/components/ColorTable.test.tsx
git commit -m "feat(frontend): add ColorTable component for wire count display"
```

---

## Task 13: Frontend — ResultsView Component

**Files:**
- Create: `frontend/src/components/ResultsView.tsx`
- Test: `frontend/__tests__/components/ResultsView.test.tsx`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/__tests__/components/ResultsView.test.tsx
import { render, screen } from '@testing-library/react'
import { ResultsView } from '@/components/ResultsView'
import type { AnalyzeResponse } from '@/lib/types'

describe('ResultsView', () => {
  const mockResult: AnalyzeResponse = {
    colors_found: ['red', 'blue'],
    wire_counts: { red: 3, blue: 5 },
    total_wires: 8,
    bounding_boxes: [],
    annotated_image: 'dGVzdA==', // base64 "test"
  }

  test('renders annotated image', () => {
    render(<ResultsView result={mockResult} />)
    const img = screen.getByRole('img')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', expect.stringContaining('data:image/png;base64'))
  })

  test('renders color table', () => {
    render(<ResultsView result={mockResult} />)
    expect(screen.getByText('red')).toBeInTheDocument()
    expect(screen.getByText('blue')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/components/ResultsView.test.tsx --no-cache
```

Expected: FAIL

- [ ] **Step 3: Write component**

```typescript
// frontend/src/components/ResultsView.tsx
import type { AnalyzeResponse } from '@/lib/types'
import { ColorTable } from './ColorTable'

interface ResultsViewProps {
  result: AnalyzeResponse
}

export function ResultsView({ result }: ResultsViewProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-lg overflow-hidden border border-gray-200">
        <img
          src={`data:image/png;base64,${result.annotated_image}`}
          alt="Annotated wire image with bounding boxes"
          className="w-full h-auto"
        />
      </div>
      <ColorTable
        wireCounts={result.wire_counts}
        totalWires={result.total_wires}
      />
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/frontend
npx jest __tests__/components/ResultsView.test.tsx --no-cache
```

Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ResultsView.tsx frontend/__tests__/components/ResultsView.test.tsx
git commit -m "feat(frontend): add ResultsView component for annotated image and color table"
```

---

## Task 14: Frontend — Main Page Integration

**Files:**
- Modify: `frontend/src/app/page.tsx`

- [ ] **Step 1: Write the main page**

```typescript
// frontend/src/app/page.tsx
'use client'

import { useState } from 'react'
import { ImageUpload } from '@/components/ImageUpload'
import { ResultsView } from '@/components/ResultsView'
import { analyzeImage } from '@/lib/api'
import type { AnalyzeResponse } from '@/lib/types'

export default function Home() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleFileSelected(file: File) {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await analyzeImage(file)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="max-w-4xl mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold">Wire Color Classifier</h1>
      <p className="text-gray-600">
        Upload an image of colored wires to detect and count each color.
      </p>

      <ImageUpload onFileSelected={handleFileSelected} isLoading={isLoading} />

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {result && <ResultsView result={result} />}
    </main>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/page.tsx
git commit -m "feat(frontend): integrate upload, analysis, and results on main page"
```

---

## Task 15: Docker & Docker Compose Setup

**Files:**
- Create: `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`

- [ ] **Step 1: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create frontend/Dockerfile**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
CMD ["node", "server.js"]
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - ENVIRONMENT=production

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

- [ ] **Step 4: Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile docker-compose.yml
git commit -m "chore: add Docker and Docker Compose configuration"
```

---

## Task 16: GitHub Actions CI/CD Workflows

**Files:**
- Create: `.github/workflows/backend-ci.yml`, `.github/workflows/frontend-ci.yml`, `.github/workflows/e2e.yml`, `.github/workflows/deploy.yml`

- [ ] **Step 1: Create workflow directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create backend-ci.yml**

```yaml
name: Backend CI

on:
  pull_request:
    paths: ['backend/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check backend/
      - run: ruff format --check backend/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-cov httpx
      - run: cd backend && python -m pytest tests/ --cov=app --cov-report=term --cov-fail-under=80

  accuracy:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest
      - run: cd backend && python -m pytest tests/accuracy/ -v
```

- [ ] **Step 3: Create frontend-ci.yml**

```yaml
name: Frontend CI

on:
  pull_request:
    paths: ['frontend/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npx eslint src/
      - run: cd frontend && npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npx jest --coverage --coverageThreshold='{"global":{"lines":70}}'
```

- [ ] **Step 4: Create e2e.yml**

```yaml
name: E2E Tests

on:
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose up -d --build
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npx playwright install --with-deps
      - run: cd frontend && npx playwright test
      - run: docker compose down
```

- [ ] **Step 5: Create deploy.yml**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
      - run: docker compose run backend python -m pytest tests/ -v
      - run: docker compose down
```

- [ ] **Step 6: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions workflows for backend, frontend, E2E, and deploy"
```

---

## Task 17: Backend — Accuracy Regression Test

**Files:**
- Create: `backend/tests/accuracy/__init__.py`, `backend/tests/accuracy/test_regression.py`

- [ ] **Step 1: Create accuracy test directory**

```bash
mkdir -p backend/tests/accuracy
touch backend/tests/accuracy/__init__.py
```

- [ ] **Step 2: Write accuracy test**

Note: This test uses synthetic ground truth until real annotated images are available. Update with real ground truth when the industry partner provides annotations.

```python
# backend/tests/accuracy/test_regression.py
import cv2
import numpy as np

from app.pipeline import analyze_image


def _create_ground_truth_image() -> tuple[np.ndarray, dict[str, int]]:
    """Create a synthetic image with known wire colors and counts.

    Returns the image and the expected color counts.
    """
    img = np.ones((400, 400, 3), dtype=np.uint8) * 200  # Gray background

    # Draw red wires (3 lines)
    for y in [50, 100, 150]:
        cv2.line(img, (20, y), (380, y), (0, 0, 255), 4)

    # Draw blue wires (2 lines)
    for y in [220, 270]:
        cv2.line(img, (20, y), (380, y), (255, 0, 0), 4)

    # Draw green wires (2 lines)
    for y in [330, 370]:
        cv2.line(img, (20, y), (380, y), (0, 255, 0), 4)

    expected = {"red": 3, "blue": 2, "green": 2}
    return img, expected


def test_accuracy_above_80_percent():
    """Fails the build if wire detection accuracy drops below 80%."""
    image, expected = _create_ground_truth_image()
    result = analyze_image(image)

    total_expected = sum(expected.values())
    total_detected = result["total_wires"]

    # Check that we detected at least 80% of expected wires
    if total_expected > 0:
        accuracy = min(total_detected, total_expected) / total_expected
    else:
        accuracy = 1.0

    assert accuracy >= 0.80, (
        f"Accuracy {accuracy:.1%} is below 80% threshold. "
        f"Expected {total_expected} wires, detected {total_detected}."
    )


def test_no_phantom_colors_on_blank():
    """Ensure no colors are detected on a blank image."""
    blank = np.ones((200, 200, 3), dtype=np.uint8) * 255
    result = analyze_image(blank)
    assert result["total_wires"] == 0, (
        f"Detected {result['total_wires']} phantom wires on blank image"
    )
```

- [ ] **Step 3: Run accuracy tests**

```bash
cd /Users/macbookpro/Documents/claude/wire-color-classifier/backend
python -m pytest tests/accuracy/ -v
```

Expected: PASS (if pipeline is working correctly from Tasks 2-7)

- [ ] **Step 4: Commit**

```bash
git add backend/tests/accuracy/
git commit -m "test(backend): add accuracy regression gate tests"
```

---

## Task 18: Create develop Branch & Initial PR

- [ ] **Step 1: Push main to GitHub**

```bash
# First create the repo on GitHub
gh repo create wire-color-classifier --private --source=. --push
```

- [ ] **Step 2: Create develop branch**

```bash
git checkout -b develop
git push -u origin develop
```

- [ ] **Step 3: Set up branch protection (optional)**

```bash
gh api repos/:owner/wire-color-classifier/branches/main/protection -X PUT \
  -f required_status_checks='{"strict":true,"contexts":["lint","test"]}' \
  -F enforce_admins=false \
  -f required_pull_request_reviews='{"required_approving_review_count":0}'
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: complete project scaffolding with all CI/CD and TDD infrastructure"
```

---

## Execution Order Summary

| Task | Depends On | Description |
|------|-----------|-------------|
| 1 | — | Project scaffolding & git init |
| 2 | 1 | Preprocessing module (TDD) |
| 3 | 2 | Color segmentation module (TDD) |
| 4 | 3 | Contour detection module (TDD) |
| 5 | 3 | Color discovery / K-means (TDD) |
| 6 | — | Pydantic models |
| 7 | 2, 3, 4, 5, 6 | Processing pipeline (TDD) |
| 8 | 7 | FastAPI endpoints (TDD) |
| 9 | 2 | Data augmentation module (TDD) |
| 10 | — | Frontend types & API client (TDD) |
| 11 | 10 | ImageUpload component (TDD) |
| 12 | 10 | ColorTable component (TDD) |
| 13 | 11, 12 | ResultsView component (TDD) |
| 14 | 13 | Main page integration |
| 15 | 8, 14 | Docker setup |
| 16 | 15 | GitHub Actions CI/CD |
| 17 | 7 | Accuracy regression tests |
| 18 | All | Create develop branch & push |

**Parallelizable groups:**
- Tasks 2-5 (backend modules) can partially overlap — 2 must go first, then 3/4/5 in parallel
- Tasks 10-12 (frontend) can run in parallel with backend tasks
- Task 6 (models) can run anytime before Task 7
