# Test-Driven Development Workflow

## The TDD Cycle

Every feature follows this cycle — no exceptions:

```
1. Write a failing test     → RED
2. Write minimal code       → GREEN
3. Refactor                 → CLEAN
4. Repeat
```

Tests are written BEFORE implementation code. No feature code is merged without corresponding tests.

## Backend Tests (pytest)

### Unit Tests

| Module | What To Test | Examples |
|--------|-------------|---------|
| `color_segmentation.py` | HSV range detection per color | `test_detect_red_wire_in_hsv_range()` |
| | Mask generation correctness | `test_mask_isolates_single_color()` |
| | Edge case: no matching color | `test_returns_empty_mask_for_absent_color()` |
| `contour_detection.py` | Contour filtering by area | `test_filter_small_contours_as_noise()` |
| | Bounding box coordinates | `test_bounding_box_contains_wire()` |
| | Edge case: overlapping contours | `test_merge_adjacent_contours()` |
| `pipeline.py` | Full image → results flow | `test_pipeline_returns_colors_and_counts()` |
| | Edge case: blank image | `test_pipeline_handles_blank_image()` |
| `augmentation.py` | Image transforms produce valid output | `test_rotation_preserves_dimensions()` |
| | Augmented images are valid | `test_brightness_adjustment_within_bounds()` |
| K-means clustering | Color discovery from image | `test_kmeans_finds_dominant_colors()` |
| | Correct number of clusters | `test_kmeans_returns_requested_k_colors()` |

### Integration Tests

| Scope | What To Test | Examples |
|-------|-------------|---------|
| API endpoints | HTTP request/response schema | `test_analyze_endpoint_returns_json()` |
| | File upload handling | `test_analyze_rejects_non_image_file()` |
| | Error responses | `test_analyze_returns_400_for_corrupt_image()` |
| Pipeline + API | End-to-end processing | `test_upload_image_get_annotated_result()` |
| Calibration | Color range updates | `test_calibrate_updates_hsv_ranges()` |

### Accuracy Regression Tests

Special tests that act as quality gates in CI:

```python
def test_accuracy_above_80_percent():
    """Fails the build if wire detection accuracy drops below 80%."""
    results = run_pipeline_on_ground_truth_images()
    assert results.accuracy >= 0.80, (
        f"Accuracy {results.accuracy:.1%} is below 80% threshold"
    )

def test_no_false_color_detection():
    """Ensure no phantom colors are detected."""
    results = run_pipeline_on_known_image()
    assert set(results.colors_found).issubset(KNOWN_COLORS)
```

### Test Fixtures (conftest.py)

```python
# Provide reusable test data
@pytest.fixture
def sample_wire_image():
    """Load a test image with known wire colors."""

@pytest.fixture
def blank_image():
    """A plain white image with no wires."""

@pytest.fixture
def single_color_image():
    """An image with only red wires for isolation testing."""

@pytest.fixture
def ground_truth():
    """Manual annotations: {color: count} for accuracy tests."""
```

## Frontend Tests (Jest + React Testing Library)

### Component Tests

| Component | What To Test | Examples |
|-----------|-------------|---------|
| `ImageUpload` | Render, file selection, validation | `test_accepts_png_and_jpg()` |
| | Drag and drop | `test_drag_drop_triggers_upload()` |
| | Invalid file rejection | `test_rejects_non_image_file()` |
| `ResultsView` | Displays annotated image | `test_renders_annotated_image()` |
| | Shows bounding boxes | `test_displays_bounding_box_overlay()` |
| `ColorTable` | Renders color list with counts | `test_shows_all_detected_colors()` |
| | Handles empty results | `test_shows_no_colors_message()` |

### API Client Tests

| Function | What To Test | Examples |
|----------|-------------|---------|
| `analyzeImage()` | Sends multipart form correctly | `test_sends_image_as_form_data()` |
| | Parses response | `test_parses_analyze_response()` |
| | Handles API error | `test_throws_on_server_error()` |

## E2E Tests (Playwright)

| Test | User Flow |
|------|-----------|
| `test_upload_and_analyze` | Upload image → wait for processing → see annotated result with bounding boxes |
| `test_color_count_display` | Upload image → verify color table shows correct counts |
| `test_calibrate_flow` | Upload reference image → verify color ranges update |
| `test_invalid_upload` | Upload non-image file → see error message |

## Coverage Requirements

| Area | Minimum Coverage | Enforced In |
|------|-----------------|-------------|
| Backend unit tests | 80% | CI — fails build if below |
| Frontend unit tests | 70% | CI — fails build if below |
| E2E critical paths | All MVP flows covered | CI — Playwright suite |
| Accuracy regression | 80% detection accuracy | CI — pytest accuracy gate |

## TDD Rules

1. **No implementation without a test first** — Write the test, see it fail, then implement
2. **Tests describe behavior, not implementation** — Test what the function does, not how
3. **One assertion per test when possible** — Keep tests focused and clear
4. **Test names describe the scenario** — `test_returns_empty_when_no_wires_detected`
5. **Don't test framework code** — Trust FastAPI/Next.js; test your logic
6. **Mock external boundaries only** — File system, network calls; not internal modules
7. **Run tests before every commit** — CI enforces this, but run locally first

## Test File Structure

```
backend/tests/
├── conftest.py                  # Shared fixtures
├── unit/
│   ├── test_color_segmentation.py
│   ├── test_contour_detection.py
│   ├── test_bounding_box.py
│   ├── test_kmeans.py
│   └── test_augmentation.py
├── integration/
│   ├── test_pipeline.py
│   └── test_api.py
└── accuracy/
    └── test_regression.py

frontend/__tests__/
├── components/
│   ├── ImageUpload.test.tsx
│   ├── ResultsView.test.tsx
│   └── ColorTable.test.tsx
└── api/
    └── client.test.ts

frontend/e2e/
└── analyze-flow.spec.ts
```
