# Test Report — Wire Color Classifier

**Date:** 2026-03-24
**Branch:** develop
**Total Tests:** 35 (25 backend + 10 frontend)
**Status:** ALL PASSING

---

## Backend Test Results (25/25 PASSED)

**Platform:** Python 3.9.6, pytest 8.4.2
**Runtime:** 2.65s

### Accuracy Regression Tests (2/2)

| Test | Status | Description |
|------|--------|-------------|
| `test_accuracy_above_80_percent` | PASSED | Verifies wire detection accuracy >= 80% on synthetic ground truth |
| `test_no_phantom_colors_on_blank` | PASSED | Ensures no false colors detected on blank image |

### Integration Tests — API (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `test_analyze_endpoint_returns_json` | PASSED | POST /api/analyze returns correct JSON schema |
| `test_analyze_rejects_non_image` | PASSED | POST /api/analyze returns 400 for non-image files |
| `test_colors_endpoint_returns_list` | PASSED | GET /api/colors returns color list |

### Integration Tests — Pipeline (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `test_pipeline_returns_colors_and_counts` | PASSED | Full pipeline returns colors, counts, boxes, annotated image |
| `test_pipeline_handles_blank_image` | PASSED | Pipeline returns zero results for blank image |
| `test_pipeline_bounding_boxes_match_counts` | PASSED | Bounding box count matches wire count totals |

### Unit Tests — Augmentation (4/4)

| Test | Status | Description |
|------|--------|-------------|
| `test_augment_returns_valid_image` | PASSED | Augmented image has 3 channels, uint8 dtype |
| `test_augment_preserves_dimensions` | PASSED | Output dimensions match input |
| `test_augment_produces_different_image` | PASSED | Augmented image differs from original |
| `test_augment_batch_produces_multiple` | PASSED | Batch generates correct number of variations |

### Unit Tests — Color Discovery (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `test_discover_colors_finds_three_in_multicolor` | PASSED | K-means finds 3 colors in RGB test image |
| `test_discover_colors_returns_requested_k` | PASSED | Returns exactly k color ranges |
| `test_discover_colors_returns_valid_hsv_ranges` | PASSED | All ranges have valid HSV values (H: 0-179) |

### Unit Tests — Color Segmentation (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `test_segment_red_from_multicolor_image` | PASSED | Isolates red region, excludes blue |
| `test_segment_returns_empty_mask_for_absent_color` | PASSED | Returns empty mask for yellow (not in image) |
| `test_segment_applies_morphological_cleanup` | PASSED | Morphological ops preserve thin wire in mask |

### Unit Tests — Contour Detection (4/4)

| Test | Status | Description |
|------|--------|-------------|
| `test_detect_contours_finds_rectangle` | PASSED | Detects filled rectangle, correct bounding box |
| `test_detect_contours_filters_small_noise` | PASSED | Filters 4px noise, keeps large contour |
| `test_detect_contours_returns_empty_on_blank` | PASSED | Returns empty list on blank mask |
| `test_bounding_box_has_area` | PASSED | BoundingBox.area property computes correctly |

### Unit Tests — Preprocessing (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `test_preprocess_returns_hsv_image` | PASSED | Output is HSV (hue max <= 179) |
| `test_preprocess_resizes_large_image` | PASSED | 2000x3000 resized to max 800px dimension |
| `test_preprocess_keeps_small_image_size` | PASSED | 200x200 image not resized |

---

## Frontend Test Results (10/10 PASSED)

**Platform:** Node 20, Jest, React Testing Library
**Runtime:** 1.55s | **Test Suites:** 4/4 passed

### API Client Tests (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `analyzeImage sends file as FormData` | PASSED | Sends POST with FormData, parses response |
| `analyzeImage throws on server error` | PASSED | Throws error on HTTP 500 |
| `getColors returns color list` | PASSED | Fetches and returns color list |

### ImageUpload Component Tests (3/3)

| Test | Status | Description |
|------|--------|-------------|
| `renders upload area` | PASSED | Shows "upload" text |
| `calls onFileSelected with valid image` | PASSED | Triggers callback on file selection |
| `shows loading state when isLoading is true` | PASSED | Displays "processing" during load |

### ColorTable Component Tests (2/2)

| Test | Status | Description |
|------|--------|-------------|
| `renders all detected colors with counts` | PASSED | Shows color names, counts, and total |
| `shows message when no colors detected` | PASSED | Displays "no colors detected" for empty |

### ResultsView Component Tests (2/2)

| Test | Status | Description |
|------|--------|-------------|
| `renders annotated image` | PASSED | Renders img with base64 data URI src |
| `renders color table` | PASSED | Shows color names and total wire count |

---

## Test Coverage Summary

| Area | Tests | Passed | Failed | Coverage Target |
|------|-------|--------|--------|----------------|
| Backend Unit | 17 | 17 | 0 | 80% |
| Backend Integration | 6 | 6 | 0 | — |
| Backend Accuracy | 2 | 2 | 0 | >= 80% accuracy |
| Frontend Unit | 10 | 10 | 0 | 70% |
| **Total** | **35** | **35** | **0** | — |
