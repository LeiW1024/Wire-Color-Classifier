# Coding Standards

## General Principles

- Write simple, readable code — avoid premature abstraction
- Each file has one clear responsibility
- Functions do one thing and are named to describe what they do
- No dead code, no commented-out code in commits

## Python (Backend)

### Style

- Formatter/linter: **Ruff**
- Type hints on all function signatures
- Docstrings on public functions (Google style)
- Max line length: 88 characters (Ruff default)
- `from __future__ import annotations` at top of every Python file

### Naming

```python
# Functions and variables: snake_case
def analyze_image_sam(image: np.ndarray) -> dict[str, Any]:
    wire_counts: dict[str, int] = {}

# Constants: UPPER_SNAKE_CASE
COLOR_RANGES = {...}
DRAW_COLORS = {...}

# Private helpers: leading underscore
def _classify_color(hsv_region: np.ndarray) -> Optional[str]: ...
def _is_wire_like(mask: dict, image_area: int) -> bool: ...
def _load_sam() -> SamAutomaticMaskGenerator: ...
```

### Project Conventions

- Use Pydantic models for all API request/response schemas (`models.py`)
- Keep CV/ML processing in `sam_pipeline.py` — not in route handlers
- SAM model loaded as a module-level singleton — never reload per request
- All new metric fields have defaults in Pydantic models for backward compatibility

### Error Handling

- Use FastAPI `HTTPException` for API errors (400 for bad input, 500 for pipeline errors)
- Log errors with context (image dimensions, processing step)
- Never silently swallow exceptions in the pipeline
- SAM model load failures are logged as warnings; server still starts

## TypeScript/React (Frontend)

### Style

- Linter: **ESLint** with Next.js recommended config
- Strict TypeScript — no `any` types
- Functional components only
- Named exports (no default exports from components)

### Naming

```typescript
// Components: PascalCase
export function ImageUpload() {}
export function ResultsView() {}
export function ColorTable() {}

// Functions/variables: camelCase
const processingSeconds = (result.processing_time_ms / 1000).toFixed(1)

// Types/interfaces: PascalCase
interface AnalyzeResponse {}
interface ResultsViewProps {}
```

### Project Conventions

- API calls go in `src/lib/api.ts` — never inside components
- Types/interfaces go in `src/lib/types.ts`
- Components receive data via props — minimal internal state
- All API response shapes typed via `AnalyzeResponse` interface
- Handle loading and error states for every API call
- Use 2-minute AbortController timeout for SAM inference requests

## Git & PR Requirements

### Branch Naming

```
feature/<name>     — new functionality
fix/<name>         — bug fixes
test/<name>        — adding/fixing tests
chore/<name>       — tooling, config, dependencies
ci/<name>          — CI/CD changes
```

### Commit Messages

```
<type>(<scope>): <description>

Types: feat, fix, test, refactor, docs, chore, ci
Scopes: backend, frontend, pipeline, api, ui
```

Examples:
```
feat(backend): add SAM segmentation pipeline
feat(frontend): add image comparison tabs and metrics dashboard
fix(pipeline): reject background segments larger than 8% of image
test(backend): update accuracy tests to use analyze_image_sam
docs: rewrite CLAUDE.md for SAM-only approach
```

### Pull Request Rules

- All code merges via Pull Request — no direct pushes to `main` or `develop`
- Every PR requires all CI checks passing (tests, lint, type checks)
- Descriptive title and summary with what changed and why
- Squash merge to keep history clean
- One logical change per PR — don't bundle unrelated work

### Branch Strategy

```
main                            ← production-ready, protected
└── develop                     ← integration branch
    ├── feature/sam-segmentation     ← merged ✓
    ├── feature/ui-redesign          ← current
    └── fix/<name>
```

**Flow:** `feature/*` → PR → `develop` → PR → `main`

## File Organization

- Keep files focused and small — if a file grows beyond ~300 lines, consider splitting
- Group by feature/domain, not by file type
- Test files mirror source file structure
- No business logic in route handlers — delegate to `sam_pipeline.py`

## SAM Model

- Model weights (`sam_vit_b.pth`) are **excluded from git** (`.gitignore`)
- Download separately: `https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth`
- Place at `backend/models/sam_vit_b.pth`
- Tests that require the model use `@pytest.mark.skipif(not _sam_model_available(), ...)`
