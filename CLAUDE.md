# Wire Color Classifier

## Goal

Build a web application that identifies and classifies thin, tangled wires of different colors from real-world industrial images.

## Project Overview

An industry partner provides images of tangled wires with 6-15 distinct colors. The system must automatically detect each wire's color, count them, and visually highlight them with bounding boxes. This is a computer vision challenge — not a simple color picker — because wires are thin, overlapping, and photographed in uncontrolled lighting conditions.

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
3. **Wire counting** — Count how many wires of each color are present
4. **Visual annotation** — Draw bounding boxes/labels on each wire in its actual color
5. **Color discovery** — Auto-discover color categories from images using K-means clustering
6. **Calibration** — Allow manual tuning of color detection thresholds

## Approach

### Phase 1: Classical Computer Vision (Current Scope)

Use OpenCV with HSV color space segmentation. No ML training required — works with the 2 available images immediately.

### Phase 2: Hybrid ML (Future — Only If Needed)

If Phase 1 accuracy is insufficient, add a lightweight ML classifier (small CNN or YOLOv8-nano) for ambiguous colors. Requires more annotated data. Decision made with industry partner.

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
| Containerization | Docker + Docker Compose (deployment & CI only) |
| Version Control | Git + GitHub |
| CI/CD | GitHub Actions |
| Backend Testing | pytest |
| Frontend Testing | Jest + React Testing Library |
| E2E Testing | Playwright |
| Linting | ESLint (frontend) + Ruff (backend) |

## Processing Pipeline

1. **Preprocessing** — Resize, Gaussian blur, BGR → HSV conversion
2. **Color Segmentation** — HSV range masks per color, morphological cleanup
3. **Contour Detection** — Find contours, filter by area, generate bounding boxes
4. **Results Assembly** — Count per color, annotated image, JSON response
5. **Color Discovery** — K-means clustering to auto-discover wire colors

## Development vs Deployment

| Environment | How It Runs | Why |
|-------------|------------|-----|
| Development | Bare metal — `uvicorn` + `next dev` | Fast iteration |
| CI/CD | Docker Compose | Reproducible |
| Sharing | Docker Compose | One command: `docker compose up` |
| Production | Docker Compose | Same image that passed CI |

## Project Structure

```
wire-color-classifier/
├── .github/workflows/            # CI/CD pipelines
├── frontend/                     # Next.js app
│   ├── src/app/                 # Pages
│   ├── src/components/          # UI components
│   ├── src/lib/                 # API client
│   ├── __tests__/               # Jest tests
│   ├── e2e/                     # Playwright E2E
│   └── Dockerfile
├── backend/                     # Python API
│   ├── app/                     # Application code
│   ├── tests/                   # pytest (unit, integration, accuracy)
│   └── Dockerfile
├── data/                        # Images (raw, augmented, ground truth)
├── rules/                       # Coding standards & workflow docs
├── docs/superpowers/specs/      # Design spec
├── docker-compose.yml
└── CLAUDE.md                    # This file
```

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/analyze` | Upload image → get colors, counts, bounding boxes |
| POST | `/api/calibrate` | Upload reference images to discover/tune color ranges |
| GET | `/api/colors` | Return current color definitions and HSV ranges |

## Rules

See the `rules/` directory for:
- `coding-standards.md` — Code style, project conventions, PR requirements
- `tdd-workflow.md` — Test-driven development process and test strategy
- `cicd-pipeline.md` — GitHub Actions workflows and deployment pipeline
