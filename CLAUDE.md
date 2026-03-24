# Wire Color Classifier

## Goal

Build a web application that identifies and classifies thin, tangled wires of different colors from real-world industrial images.

## Project Overview

An industry partner provides images of tangled wires with 6-15 distinct colors. The system automatically detects each wire's color, counts them, and visually highlights them using SAM (Segment Anything Model) segmentation + HSV color classification. No training data or annotations required.

## The Challenge

- **Thin wires:** Small pixel footprint, easy to miss or merge with background
- **Tangled/overlapping:** Wires occlude each other, breaking contour continuity
- **Real-world images:** Varying lighting, reflections on insulation, busy backgrounds
- **No predefined color list:** Colors must be discovered from the images themselves
- **Minimal data:** Only 2 unannotated images available — no training dataset
- **Accuracy target:** 80%+ (goal: 90%)

## MVP Features

1. **Image upload** — Upload a wire image via web UI
2. **Color detection** — Identify which wire colors exist in the image
3. **Wire counting** — Count how many wire segments of each color are present
4. **Visual annotation** — Highlight each wire segment with colored contour + semi-transparent fill
5. **Image comparison** — Toggle between original and annotated image in the UI
6. **Metrics dashboard** — Wire count, colors found, avg confidence, wire coverage %, process time

## Approach: SAM + HSV Classification (Zero-Shot)

Use Meta's **Segment Anything Model (SAM vit_b)** for zero-shot segmentation, followed by HSV color space classification. No training data or annotations needed — SAM was pre-trained by Meta on millions of images.

**Why SAM:** Classical HSV + contour detection failed on real wire images — background textures were classified as wire colors and thin tangled wires produced fragmented, incorrect contours. SAM correctly segments individual wire objects regardless of shape complexity.

## Architecture

```
┌──────────────────────────┐         ┌──────────────────────────────────────┐
│   Next.js / React         │  HTTP   │   Python Backend (FastAPI)            │
│   Frontend                │ ──────→ │                                      │
│                           │ ←────── │   1. Resize image (max 800px)        │
│  - Image upload           │         │   2. SAM generates all segments      │
│  - Original / detected    │         │   3. Filter wire-like shapes         │
│    image comparison tabs  │         │   4. HSV classify each segment color │
│  - Color distribution     │         │   5. Draw contours + color overlay   │
│  - Metrics dashboard      │         │   6. Return JSON + base64 image      │
└──────────────────────────┘         └──────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 / React |
| Backend API | Python / FastAPI |
| Segmentation | SAM (Segment Anything Model, vit_b) — Meta AI |
| Color Classification | OpenCV HSV color space |
| Communication | REST API (JSON + base64 images) |
| Containerization | Docker + Docker Compose (deployment & CI only) |
| Version Control | Git + GitHub |
| CI/CD | GitHub Actions |
| Backend Testing | pytest |
| Frontend Testing | Jest + React Testing Library |
| E2E Testing | Playwright |
| Linting | ESLint (frontend) + Ruff (backend) |

## Processing Pipeline

1. **Resize** — Scale image to max 800px on longest side (speed optimization)
2. **SAM Segmentation** — Generate all object masks (points_per_side=8, ~10s on CPU)
3. **Wire Filter** — Keep segments with aspect ratio ≥ 2.5, area < 8% of image (removes background)
4. **Color Classification** — HSV range matching per segment, require 15% pixel dominance
5. **Annotation** — Draw contour outlines + 35% opacity color fill on each wire segment
6. **Metrics** — Avg SAM confidence (predicted IoU), wire coverage %, processing time

## SAM Model

- Model: `vit_b` (ViT-Base, ~357MB)
- File: `backend/models/sam_vit_b.pth` (excluded from git — download separately)
- Download: `https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth`
- Loaded once as singleton; stays in memory between requests

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/analyze` | Upload image → colors, counts, annotated image, metrics |
| GET | `/api/colors` | Return supported HSV color definitions |

## Response Schema (`/api/analyze`)

```json
{
  "colors_found": ["red", "blue", "green"],
  "wire_counts": {"red": 3, "blue": 5, "green": 2},
  "total_wires": 10,
  "bounding_boxes": [{"color": "red", "x": 10, "y": 20, "w": 80, "h": 6}],
  "annotated_image": "<base64 PNG>",
  "processing_time_ms": 9800,
  "segments_analyzed": 64,
  "avg_confidence": 87.5,
  "wire_coverage_pct": 12.3
}
```

## Development vs Deployment

| Environment | How It Runs | Why |
|-------------|------------|-----|
| Development | Bare metal — `uvicorn` + `next dev` | Fast iteration |
| CI/CD | Docker Compose | Reproducible |
| Production | Docker Compose | Same image that passed CI |

## Running Locally

```bash
# Backend (from backend/)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (from frontend/)
npm run dev
```

## Project Structure

```
wire-color-classifier/
├── .github/workflows/            # CI/CD pipelines
├── frontend/                     # Next.js app
│   ├── src/app/                 # Pages + global styles
│   ├── src/components/          # ImageUpload, ResultsView, ColorTable
│   ├── src/lib/                 # API client, TypeScript types
│   ├── __tests__/               # Jest unit tests
│   ├── e2e/                     # Playwright E2E tests
│   └── Dockerfile
├── backend/                     # Python FastAPI
│   ├── app/
│   │   ├── sam_pipeline.py      # Core: SAM segmentation + HSV classification
│   │   ├── routes.py            # API endpoints
│   │   ├── models.py            # Pydantic response schemas
│   │   └── main.py              # FastAPI app + SAM startup preload
│   ├── models/                  # SAM weights (not in git)
│   ├── tests/
│   │   ├── unit/                # _classify_color, _is_wire_like
│   │   ├── integration/         # API endpoints, SAM pipeline
│   │   └── accuracy/            # Regression gate (≥80% on synthetic image)
│   └── Dockerfile
├── data/                        # Wire images (raw, ground truth)
├── rules/                       # Coding standards, TDD workflow, CI/CD docs
├── docs/superpowers/specs/      # Design spec
├── docker-compose.yml
└── CLAUDE.md                    # This file
```

## Rules

See the `rules/` directory for:
- `coding-standards.md` — Code style, project conventions, PR requirements
- `tdd-workflow.md` — Test-driven development process and test strategy
- `cicd-pipeline.md` — GitHub Actions workflows and deployment pipeline
