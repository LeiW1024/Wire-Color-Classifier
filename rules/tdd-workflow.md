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
| `sam_pipeline._classify_color` | HSV color matching per color name | `test_classify_color_red()` |
| | Red-high hue range merges to red | `test_classify_color_red_high_maps_to_red()` |
| | Low saturation returns None | `test_classify_color_returns_none_for_low_saturation()` |
| | All supported colors detected | `test_classify_color_yellow()`, `test_classify_color_blue()` |
| `sam_pipeline._is_wire_like` | Elongated shape accepted | `test_is_wire_like_elongated()` |
| | Square shape rejected | `test_is_wire_like_square_rejected()` |
| | Zero dimension rejected | `test_is_wire_like_zero_dimension_rejected()` |
| | Background-size segment rejected (>8% image) | `test_is_wire_like_too_large_rejected()` |
| | Tiny noise segment rejected (<150px) | `test_is_wire_like_tiny_rejected()` |

### Integration Tests

| Scope | What To Test | Examples |
|-------|-------------|---------|
| API endpoints | HTTP request/response schema | `test_analyze_endpoint_returns_json()` |
| | New metric fields present | `test_analyze_endpoint_returns_json()` (checks `avg_confidence`, `wire_coverage_pct`) |
| | File upload validation | `test_analyze_rejects_non_image()` |
| | Corrupt image handling | `test_analyze_rejects_corrupt_image()` |
| | Colors endpoint | `test_colors_endpoint_returns_list()` |
| SAM pipeline | Full response schema | `test_sam_pipeline_returns_expected_schema()` |
| | Metric value ranges | `avg_confidence` in [0,100], `wire_coverage_pct` in [0,100] |

### Accuracy Regression Tests

Quality gates — always `skipif` SAM model not available (not stored in git):

```python
@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_accuracy_above_80_percent():
    """Fails CI if wire detection drops below 80% on synthetic image."""

@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_no_phantom_colors_on_blank():
    """No colors detected on plain gray image."""

@pytest.mark.skipif(not _sam_model_available(), reason="SAM model not downloaded")
def test_response_metrics_are_valid():
    """avg_confidence, wire_coverage_pct, processing_time_ms in valid ranges."""
```

### Test Fixtures (conftest.py)

```python
@pytest.fixture
def sample_color_image():
    """Synthetic image with red, blue, green wire lines."""

@pytest.fixture
def blank_image():
    """Plain gray image with no wires."""
```

## Frontend Tests (Jest + React Testing Library)

### Component Tests

| Component | What To Test | Examples |
|-----------|-------------|---------|
| `ImageUpload` | Renders drop zone | `renders upload area` |
| | File selection callback | `calls onFileSelected with valid image` |
| | Loading state display | `shows loading state when isLoading is true` |
| `ResultsView` | Renders annotated image | `renders annotated image` |
| | Shows detected color names | `renders color names` |
| | Shows total wire count | `renders total wire count` |
| `ColorTable` | Renders all colors with counts | `renders all detected colors with counts` |
| | Empty state message | `shows message when no colors detected` |

### API Client Tests

| Function | What To Test | Examples |
|----------|-------------|---------|
| `analyzeImage()` | Sends multipart form | `analyzeImage sends file as FormData` |
| | Parses response with new metric fields | `analyzeImage throws on server error` |
| `getColors()` | Returns color list | `getColors returns color list` |

## E2E Tests (Playwright)

| Test | User Flow |
|------|-----------|
| `test_upload_and_analyze` | Upload wire image → wait for SAM processing → see annotated result |
| `test_color_count_display` | Upload image → verify color distribution panel shows counts |
| `test_metrics_displayed` | Upload image → verify metric cards show processing_time, confidence |
| `test_comparison_tabs` | Upload image → click Original tab → verify raw image shown |
| `test_invalid_upload` | Upload non-image file → see error message |

## Coverage Requirements

| Area | Minimum Coverage | Enforced In |
|------|-----------------|-------------|
| Backend unit tests | 80% | CI — fails build if below |
| Frontend unit tests | 70% | CI — fails build if below |
| E2E critical paths | All MVP flows covered | CI — Playwright suite |
| Accuracy regression | 80% detection accuracy | CI — skipped if SAM model absent |

## TDD Rules

1. **No implementation without a test first** — Write the test, see it fail, then implement
2. **Tests describe behavior, not implementation** — Test what the function does, not how
3. **One assertion per test when possible** — Keep tests focused and clear
4. **Test names describe the scenario** — `test_returns_empty_when_no_wires_detected`
5. **Don't test framework code** — Trust FastAPI/Next.js; test your logic
6. **Mock external boundaries only** — File system, network calls; not internal modules
7. **Run tests before every commit** — CI enforces this, but run locally first
8. **SAM model tests use skipif** — Accuracy tests skip gracefully when model not downloaded

## Test File Structure

```
backend/tests/
├── conftest.py                    # Shared fixtures (sample images)
├── unit/                          # (empty — all logic is in integration tests)
├── integration/
│   ├── test_api.py                # FastAPI endpoint tests
│   └── test_sam_pipeline.py      # _classify_color, _is_wire_like, analyze_image_sam
└── accuracy/
    └── test_regression.py        # CI quality gate (skipif no SAM model)

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
