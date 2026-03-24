# CI/CD Pipeline & GitHub Actions

## Pipeline Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    On Pull Request                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Backend CI   │  │ Frontend CI  │  │   E2E Tests       │  │
│  │              │  │              │  │  (after both pass) │  │
│  │ - Ruff lint  │  │ - ESLint     │  │                   │  │
│  │ - Type check │  │ - Type check │  │ - Playwright      │  │
│  │ - pytest     │  │ - Jest tests │  │ - Upload/analyze  │  │
│  │   (no model) │  │ - Coverage   │  │   workflow        │  │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                  On Merge to main                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐  ┌───────────┐  ┌──────────────────────────┐ │
│  │  Build     │→ │  Test     │→ │  Deploy                  │ │
│  │  Docker    │  │  Suite    │  │  - Build Docker images   │ │
│  │  images    │  │  Full     │  │  - Push to registry      │ │
│  └───────────┘  └───────────┘  └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

> **Note on SAM model in CI:** The SAM model weights (~357MB) are not stored in git.
> Accuracy regression tests use `@pytest.mark.skipif(not _sam_model_available(), ...)` and
> are **skipped** in CI unless the model is pre-cached. API and pipeline unit tests run
> without the model and cover all non-inference code paths.

## Workflow Files

### 1. Backend CI — `.github/workflows/backend-ci.yml`

**Trigger:** Pull request touching `backend/**`

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
      - run: pip install pytest pytest-cov
      - run: |
          cd backend
          pytest tests/ --cov=app --cov-report=term --cov-fail-under=80 -v
          # Note: accuracy/ tests are auto-skipped (SAM model not present in CI)
```

### 2. Frontend CI — `.github/workflows/frontend-ci.yml`

**Trigger:** Pull request touching `frontend/**`

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

### 3. E2E Tests — `.github/workflows/e2e.yml`

**Trigger:** Pull request (after backend + frontend CI pass)

```yaml
name: E2E Tests

on:
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest
    needs: [backend-ci, frontend-ci]
    steps:
      - uses: actions/checkout@v4
      - run: docker compose up -d
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci
      - run: cd frontend && npx playwright install --with-deps
      - run: cd frontend && npx playwright test
      - run: docker compose down
```

### 4. Deploy — `.github/workflows/deploy.yml`

**Trigger:** Push to `main` (after merge)

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
      - run: docker compose run backend pytest tests/ -v
      - run: docker compose run frontend npx jest
      # Push to registry (configure as needed):
      # - run: docker push <registry>/wire-color-backend
      # - run: docker push <registry>/wire-color-frontend
```

## CI Quality Gates

Every PR must pass ALL of these before merge:

| Gate | Tool | Threshold |
|------|------|-----------|
| Backend lint | Ruff | Zero errors |
| Backend type check | Ruff | Zero errors |
| Backend unit tests | pytest | All pass |
| Backend coverage | pytest-cov | ≥ 80% |
| Backend accuracy | pytest (accuracy/) | ≥ 80% — skipped in CI if no SAM model |
| Frontend lint | ESLint | Zero errors |
| Frontend type check | TypeScript (`tsc --noEmit`) | Zero errors |
| Frontend unit tests | Jest | All pass |
| Frontend coverage | Jest | ≥ 70% |
| E2E tests | Playwright | All critical paths pass |

## Docker Configuration

### docker-compose.yml

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
      - ./backend/models:/app/models   # mount SAM model weights
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

### backend/Dockerfile

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
# models/ directory is mounted at runtime — not baked into image
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile

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

## Local Development Commands

```bash
# Backend (from backend/)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (from frontend/)
npm run dev

# Run backend tests locally
cd backend && pytest tests/ -v

# Run frontend tests locally
cd frontend && npx jest
cd frontend && npx playwright test
```

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `ENVIRONMENT` | Backend | `development` or `production` |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend API URL (default: `http://localhost:8000`) |
| `SAM_MODEL_PATH` | Backend | Override path to SAM weights file |
