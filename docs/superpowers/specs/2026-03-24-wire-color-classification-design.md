# Wire Color Classification — Design Spec

## Problem Statement

Identify and classify thin, tangled wires of different colors from real-world industrial images. The system must:

1. **Count** how many wires of each color are present
2. **List** which colors exist in the image
3. **Highlight** each wire with bounding boxes/labels in its actual color

### Constraints

- Only 2 unannotated images available currently
- Real-world industrial images (varying lighting, busy backgrounds)
- 6-15 distinct wire colors expected
- Target accuracy: 80%+ (goal: 90%)
- No predefined color list — colors must be discovered from images

## Approach

### Phase 1: Classical Computer Vision (Current Scope)

Use OpenCV with HSV color space segmentation. No ML training required — works immediately with available images.

**If Phase 1 accuracy is insufficient**, discuss with industry partner about proceeding to Phase 2.

### Phase 2: Hybrid Approach (Future — Only If Needed)

Add a lightweight ML classifier (small CNN or YOLOv8-nano) for ambiguous colors that classical CV cannot distinguish. Requires more annotated data.

## Architecture

```
┌─────────────────────────┐         ┌──────────────────────────────┐
│    Next.js / React       │  HTTP   │    Python Backend (FastAPI)   │
│    Frontend              │ ──────→ │                              │
│                          │ ←────── │    - OpenCV processing       │
│  - Image upload          │         │    - HSV color segmentation  │
│  - Annotated image view  │         │    - Contour detection       │
│  - Color list & counts   │         │    - Bounding box generation │
│  - Bounding box overlay  │         │    - Data augmentation       │
└─────────────────────────┘         └──────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js / React |
| Backend API | Python / FastAPI |
| Computer Vision | OpenCV |
| Color Space | HSV segmentation |
| Data Augmentation | OpenCV / Albumentations |
| Communication | REST API (JSON + base64 images) |
| Version Control | Git + GitHub |
| CI/CD | GitHub Actions |
| Backend Testing | pytest |
| Frontend Testing | Jest + React Testing Library |
| E2E Testing | Playwright |
| Linting | ESLint (frontend) + Ruff (backend) |
| Containerization | Docker + Docker Compose (deployment & CI only) |

## Development vs Deployment Strategy

| Environment | How It Runs | Why |
|-------------|------------|-----|
| **Development** | Bare metal — `uvicorn` + `next dev` directly | Fast iteration, no container rebuild wait |
| **CI/CD** | Docker Compose | Reproducible, consistent across runners |
| **Sharing with partner** | Docker Compose | One command: `docker compose up` |
| **Production** | Docker Compose | Same image that passed CI; no env surprises |

### Docker Setup

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on:
      - backend
```

### Dockerfiles

| File | Base Image | Notes |
|------|-----------|-------|
| `backend/Dockerfile` | `python:3.11-slim` + OpenCV deps | Multi-stage to keep image small |
| `frontend/Dockerfile` | `node:20-alpine` | Build stage + nginx serve stage |

## Processing Pipeline

### Step 1: Image Preprocessing
- Resize to standard resolution
- Gaussian blur to reduce noise
- Convert BGR → HSV color space

### Step 2: Color Segmentation
- Define HSV ranges for each discoverable color
- Apply `cv2.inRange()` per color range to create masks
- Morphological operations (erode/dilate) to clean masks

### Step 3: Contour Detection
- `cv2.findContours()` on each color mask
- Filter contours by minimum area (remove noise)
- Generate bounding boxes via `cv2.boundingRect()`

### Step 4: Results Assembly
- Count contours per color → wire count
- List all detected colors
- Draw bounding boxes on original image with color labels
- Return annotated image + JSON data

### Step 5: Color Discovery (Initial Calibration)
- Since no predefined color list exists, run K-means clustering on the 2 provided images to discover dominant wire colors
- Use discovered clusters to define initial HSV ranges
- Allow manual tuning of thresholds via the web UI

## Data Augmentation Strategy

Generate 50-100+ variations from the 2 source images for testing and threshold tuning:

| Augmentation | Purpose |
|-------------|---------|
| Rotation (0-360) | Wire angle variation |
| Horizontal/vertical flip | Orientation variation |
| Brightness adjustment | Lighting variation |
| Contrast adjustment | Different exposure |
| Gaussian noise | Sensor noise simulation |
| Random crop | Partial views |
| Color jitter (slight) | Minor color shifts |

## API Design

### POST /api/analyze

**Request:** Multipart form with image file

**Response:**
```json
{
  "colors_found": ["red", "blue", "green", "yellow"],
  "wire_counts": {
    "red": 3,
    "blue": 5,
    "green": 2,
    "yellow": 4
  },
  "total_wires": 14,
  "bounding_boxes": [
    {
      "color": "red",
      "x": 100, "y": 200, "w": 50, "h": 30,
      "confidence": 0.85
    }
  ],
  "annotated_image": "<base64 encoded image>"
}
```

### POST /api/calibrate

Upload reference images to discover/tune color ranges.

### GET /api/colors

Return current color definitions and HSV ranges.

## Frontend Components

| Component | Purpose |
|-----------|---------|
| ImageUpload | Drag-and-drop or file select for wire images |
| ResultsView | Display annotated image with bounding boxes |
| ColorTable | Table showing color list and wire counts |
| CalibrationPanel | Tune HSV thresholds per color (optional) |

## Git Workflow & PR Strategy

### Branch Strategy

```
main                        ← production-ready, protected
├── develop                 ← integration branch
│   ├── feature/backend-pipeline
│   ├── feature/frontend-upload
│   ├── feature/api-endpoints
│   └── fix/color-threshold
```

### PR Rules

- All code merges via Pull Request — no direct pushes to `main` or `develop`
- Every PR requires:
  - All CI checks passing (tests, lint, type checks)
  - Descriptive title and summary
- Branch naming: `feature/<name>`, `fix/<name>`, `chore/<name>`
- Squash merge to keep history clean

### Commit Convention

```
<type>(<scope>): <description>

Types: feat, fix, test, refactor, docs, chore, ci
Scopes: backend, frontend, pipeline, api, augmentation
```

## CI/CD Pipeline

### GitHub Actions Workflows

```
┌──────────────────────────────────────────────────────────┐
│                    On Pull Request                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Backend CI  │  │ Frontend CI │  │   E2E Tests     │  │
│  │             │  │             │  │   (if both pass) │  │
│  │ - Ruff lint │  │ - ESLint    │  │                 │  │
│  │ - Type check│  │ - Type check│  │ - Playwright    │  │
│  │ - pytest    │  │ - Jest tests│  │ - Upload/analyze│  │
│  │ - Coverage  │  │ - Coverage  │  │   workflow      │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                  On Merge to main                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │
│  │  Build    │→ │  Test    │→ │  Deploy (future)       │ │
│  │  Docker   │  │  Suite   │  │  - Build Docker images │ │
│  │  images   │  │  Full    │  │  - Push to registry    │ │
│  └──────────┘  └──────────┘  └────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Workflow Files

| File | Trigger | Jobs |
|------|---------|------|
| `.github/workflows/backend-ci.yml` | PR (backend/**) | Lint, type check, pytest + coverage |
| `.github/workflows/frontend-ci.yml` | PR (frontend/**) | Lint, type check, Jest + coverage |
| `.github/workflows/e2e.yml` | PR (after unit tests pass) | Playwright E2E tests |
| `.github/workflows/deploy.yml` | Merge to main | Build, test, deploy |

## Test-Driven Development (TDD) Strategy

### TDD Workflow

For every feature, the cycle is:

```
1. Write failing test     → RED
2. Write minimal code     → GREEN
3. Refactor              → CLEAN
4. Repeat
```

Tests are written BEFORE implementation code. No feature code is merged without corresponding tests.

### Backend Tests (pytest)

| Test Category | What It Tests | Example |
|--------------|---------------|---------|
| **Unit: Color Segmentation** | HSV range detection per color | `test_detect_red_wire_in_hsv_range()` |
| **Unit: Contour Detection** | Contour filtering by area | `test_filter_small_contours_as_noise()` |
| **Unit: Bounding Box** | Correct box coordinates | `test_bounding_box_contains_wire()` |
| **Unit: K-Means Clustering** | Color discovery from image | `test_kmeans_finds_dominant_colors()` |
| **Unit: Augmentation** | Image transforms produce valid output | `test_rotation_preserves_dimensions()` |
| **Integration: Pipeline** | Full image → results flow | `test_pipeline_returns_colors_and_counts()` |
| **Integration: API** | HTTP endpoints return correct schema | `test_analyze_endpoint_returns_json()` |
| **Accuracy: Regression** | Detection accuracy vs ground truth | `test_accuracy_above_80_percent()` |

### Frontend Tests (Jest + React Testing Library)

| Test Category | What It Tests | Example |
|--------------|---------------|---------|
| **Unit: Components** | Render and interaction | `test_image_upload_accepts_valid_formats()` |
| **Unit: API Client** | Request/response handling | `test_analyze_sends_multipart_form()` |
| **Integration: Results** | Display of bounding boxes + counts | `test_results_view_shows_color_table()` |
| **Error Handling** | Invalid file, API failure | `test_shows_error_on_invalid_image()` |

### E2E Tests (Playwright)

| Test | Flow |
|------|------|
| `test_upload_and_analyze` | Upload image → see annotated result with bounding boxes |
| `test_color_count_display` | Upload image → verify color table matches API response |
| `test_calibrate_flow` | Upload reference → verify color ranges update |

### Test File Structure

```
backend/
├── tests/
│   ├── conftest.py              # Fixtures: sample images, mock data
│   ├── unit/
│   │   ├── test_color_segmentation.py
│   │   ├── test_contour_detection.py
│   │   ├── test_bounding_box.py
│   │   ├── test_kmeans.py
│   │   └── test_augmentation.py
│   ├── integration/
│   │   ├── test_pipeline.py
│   │   └── test_api.py
│   └── accuracy/
│       └── test_regression.py   # Accuracy gate: fails if < 80%
frontend/
├── __tests__/
│   ├── components/
│   │   ├── ImageUpload.test.tsx
│   │   ├── ResultsView.test.tsx
│   │   └── ColorTable.test.tsx
│   └── api/
│       └── client.test.ts
├── e2e/
│   └── analyze-flow.spec.ts
```

### Coverage Requirements

| Area | Minimum Coverage |
|------|-----------------|
| Backend unit tests | 80% |
| Frontend unit tests | 70% |
| E2E critical paths | Upload → analyze → display results |

### Accuracy Regression Gate

A special test that acts as a quality gate in CI:

```python
def test_accuracy_above_80_percent():
    """Fails the build if wire detection accuracy drops below 80%."""
    results = run_pipeline_on_ground_truth_images()
    assert results.accuracy >= 0.80, (
        f"Accuracy {results.accuracy:.1%} is below 80% threshold"
    )
```

## Accuracy Measurement

- Manually count wires in the 2 source images as ground truth
- Compare system output vs. ground truth
- Accuracy = correct detections / total actual wires
- Target: 80%+ (goal: 90%)

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Similar colors hard to distinguish (dark blue vs. black) | Tune HSV ranges carefully; upgrade to hybrid if needed |
| Wire occlusion (hidden behind other wires) | Accept partial detection; count visible segments |
| Lighting variation across images | Histogram equalization preprocessing |
| Thin wires produce small contours | Adjust minimum contour area threshold |
| Reflections on wire insulation | Gaussian blur + morphological operations |

## Project Structure

```
wire-color-classifier/
├── .github/
│   └── workflows/
│       ├── backend-ci.yml        # Backend lint + test + coverage
│       ├── frontend-ci.yml       # Frontend lint + test + coverage
│       ├── e2e.yml               # Playwright E2E tests
│       └── deploy.yml            # Build + deploy on merge to main
├── frontend/                     # Next.js app
│   ├── src/
│   │   ├── app/                 # Pages
│   │   ├── components/          # UI components
│   │   └── lib/                 # API client
│   ├── __tests__/               # Jest unit/integration tests
│   ├── e2e/                     # Playwright E2E tests
│   ├── jest.config.ts
│   ├── playwright.config.ts
│   ├── Dockerfile               # Node + nginx image
│   └── package.json
├── backend/                     # Python API
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── pipeline.py          # CV processing pipeline
│   │   ├── color_segmentation.py
│   │   ├── contour_detection.py
│   │   ├── augmentation.py
│   │   └── models.py            # Pydantic schemas
│   ├── tests/
│   │   ├── conftest.py          # Fixtures + sample images
│   │   ├── unit/                # Unit tests (TDD)
│   │   ├── integration/         # API + pipeline tests
│   │   └── accuracy/            # Accuracy regression gate
│   ├── Dockerfile               # Python + OpenCV image
│   ├── pyproject.toml           # Ruff + pytest config
│   └── requirements.txt
├── data/
│   ├── raw/                     # Original 2 images
│   ├── augmented/               # Generated variations
│   └── ground_truth/            # Manual annotations for accuracy tests
├── docker-compose.yml           # Backend + frontend services
├── .gitignore
└── README.md
```

## Decision Log

| Decision | Reasoning |
|----------|-----------|
| Classical CV first (no ML) | Only 2 images available; no training data |
| HSV over RGB | HSV separates color from brightness — better for varying lighting |
| K-means for color discovery | No predefined color list; auto-discover from images |
| FastAPI over Flask | Async support, automatic docs, modern Python |
| Phase 2 hybrid only if needed | Avoid over-engineering; validate Phase 1 with partner first |
| TDD approach | Tests written before code; ensures reliability and prevents regressions |
| GitHub Actions for CI/CD | Native GitHub integration; free for public repos; easy PR checks |
| Git feature branch workflow | Clean history; all changes via PR; no direct pushes to main |
| Accuracy regression gate in CI | Prevents merging code that degrades detection accuracy below 80% |
| Squash merge | Keeps main branch history clean and readable |
