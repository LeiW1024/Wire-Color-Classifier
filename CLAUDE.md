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

## Project Workflow

### 1. Starting New Work

Every piece of work starts from a feature branch, never directly on `develop` or `main`.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<name>     # or fix/<name>, docs/<name>, ci/<name>
```

**Branch types:**
- `feature/frontend` — Next.js / React UI work
- `feature/backend` — FastAPI / Python API work
- `feature/ai-model` — SAM segmentation / CV model work
- `fix/<name>` — Bug fixes
- `docs/<name>` — Documentation only
- `ci/<name>` — CI/CD changes

---

### 2. TDD Development Cycle

Every feature follows RED → GREEN → CLEAN. No implementation without a test first.

```
1. Write a failing test       → RED
2. Write minimal code         → GREEN
3. Refactor                   → CLEAN
4. Repeat
```

**Backend (pytest):**

```bash
cd backend
# Write test first in tests/integration/ or tests/unit/
pytest tests/integration/test_sam_pipeline.py::test_my_new_test -v   # must FAIL first
# Write implementation
pytest tests/integration/test_sam_pipeline.py::test_my_new_test -v   # must PASS
# Run full suite before committing
pytest tests/ -v
```

**Frontend (Jest):**

```bash
cd frontend
# Write test first in __tests__/components/ or __tests__/api/
npx jest --testPathPattern=ResultsView --watch   # must FAIL first
# Write implementation
npx jest --testPathPattern=ResultsView --watch   # must PASS
# Run full suite before committing
npx jest
```

**SAM accuracy tests** — require model file, skip in CI automatically:

```bash
# Only run locally after downloading backend/models/sam_vit_b.pth
pytest tests/accuracy/ -v
```

---

### 3. Committing Changes

Commit messages follow `<type>(<scope>): <description>`:

```
feat(backend): add wire color grouping by hue band
fix(pipeline): reject background segments larger than 8% of image
test(backend): add unit tests for _classify_color edge cases
docs: update CLAUDE.md with workflow section
ci: add backend lint job to GitHub Actions
```

```bash
git add <specific files>      # never git add -A blindly
git commit -m "feat(backend): ..."
```

Run tests locally before every commit — CI will enforce this too.

---

### 4. Opening a Pull Request

When the feature is complete and all tests pass:

```bash
git push origin feature/<name>
```

Then open a PR on GitHub:
- **Base branch:** `develop`
- **Title:** descriptive, matches commit type (`feat:`, `fix:`, etc.)
- **Body:** what changed and why, test plan checklist
- **Merge strategy:** Squash merge (keeps history clean)

PRs require all CI checks to pass before merging:

| Check | Tool | Must Pass |
|-------|------|-----------|
| Backend lint | Ruff | Zero errors |
| Backend tests | pytest | All pass, ≥80% coverage |
| Frontend lint | ESLint + tsc | Zero errors |
| Frontend tests | Jest | All pass, ≥70% coverage |
| E2E tests | Playwright | All critical paths pass |

---

### 5. Branch Flow

```
feature/* ──PR──→ develop ──PR──→ main
```

- `feature/*` branches are created from `develop`
- Merges into `develop` happen via PR only — never direct push
- `develop` is the integration branch — always in a working state
- `main` is production-ready — only receives merges from `develop` via PR

```bash
# After feature PR is merged into develop:
git checkout develop
git pull origin develop

# When develop is stable and ready for release:
# Open PR on GitHub: develop → main
```

---

### 6. CI/CD Pipeline

Triggered automatically on every PR and push:

```
On Pull Request
├── Backend CI     — Ruff lint → pytest (≥80% cov) → accuracy gate
├── Frontend CI    — ESLint → tsc → Jest (≥70% cov)
└── E2E Tests      — Playwright (runs after both above pass)

On Merge to main
└── Deploy         — docker compose build → test → push images
```

**GitHub Actions workflow files:**

| File | Trigger | What It Does |
|------|---------|--------------|
| `.github/workflows/backend-ci.yml` | PR touching `backend/**` | Lint, type check, pytest, coverage |
| `.github/workflows/frontend-ci.yml` | PR touching `frontend/**` | ESLint, tsc, Jest, coverage |
| `.github/workflows/e2e.yml` | All PRs (after CI passes) | Playwright upload/analyze flow |
| `.github/workflows/deploy.yml` | Push to `main` | Build + push Docker images |

**SAM model in CI:** The model file (`sam_vit_b.pth`) is not in git and not available in CI. Tests that require it are decorated with `@pytest.mark.skipif(not _sam_model_available(), ...)` and are skipped automatically. They must be run and verified locally before merging.

---

### 7. Complete Development Example

```bash
# 1. Start from develop
git checkout develop && git pull origin develop
git checkout -b feature/backend

# 2. Write a failing test first (TDD RED)
# Edit backend/tests/integration/test_sam_pipeline.py
pytest tests/integration/test_sam_pipeline.py::test_new_feature -v  # FAIL ✓

# 3. Implement the feature (TDD GREEN)
# Edit backend/app/sam_pipeline.py
pytest tests/integration/test_sam_pipeline.py::test_new_feature -v  # PASS ✓

# 4. Run full suite (TDD CLEAN)
pytest tests/ -v                    # all pass
cd ../frontend && npx jest          # all pass

# 5. Commit
git add backend/app/sam_pipeline.py backend/tests/integration/test_sam_pipeline.py
git commit -m "feat(backend): add new feature"

# 6. Push and open PR → develop on GitHub
git push origin feature/backend
# Open PR: feature/backend → develop (squash merge)

# 7. After PR merged, sync develop
git checkout develop && git pull origin develop

# 8. When develop is stable, open PR: develop → main on GitHub
```

---

## Rules

**All rules are mandatory. Every rule in the `rules/` directory must be followed at every stage of development — writing code, testing, committing, reviewing, and deploying. When in doubt, consult the relevant rule file before proceeding. No exceptions.**

See the `rules/` directory for full detail:
- `coding-standards.md` — Code style, naming, PR requirements, branch strategy
- `tdd-workflow.md` — TDD cycle, test tables, coverage requirements, fixtures
- `cicd-pipeline.md` — GitHub Actions YAML, Docker config, quality gates
