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

### Naming

```python
# Functions and variables: snake_case
def detect_wire_colors(image: np.ndarray) -> list[str]:
    color_count = 0

# Classes: PascalCase
class ColorSegmenter:

# Constants: UPPER_SNAKE_CASE
MIN_CONTOUR_AREA = 100
DEFAULT_HSV_RANGES = {...}
```

### Project Conventions

- Use Pydantic models for API request/response schemas
- Use FastAPI dependency injection for shared resources
- Keep CV processing in dedicated modules — not in route handlers
- Configuration via environment variables or config file, not hardcoded

### Error Handling

- Use FastAPI HTTPException for API errors
- Log errors with context (image name, processing step)
- Never silently swallow exceptions in the CV pipeline

## TypeScript/React (Frontend)

### Style

- Linter: **ESLint** with Next.js recommended config
- Strict TypeScript — no `any` types
- Functional components only
- Named exports (no default exports)

### Naming

```typescript
// Components: PascalCase
export function ImageUpload() {}
export function ColorTable() {}

// Functions/variables: camelCase
const wireCount = getWireCount(results)

// Types/interfaces: PascalCase
interface AnalyzeResponse {}
type WireColor = string
```

### Project Conventions

- API calls go in `src/lib/` — not inside components
- Components receive data via props — minimal internal state
- Use TypeScript interfaces for all API response shapes
- Handle loading and error states for every API call

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
Scopes: backend, frontend, pipeline, api, augmentation
```

Examples:
```
feat(backend): add HSV color segmentation module
test(backend): add unit tests for contour detection
fix(pipeline): handle zero-contour edge case
ci: add backend test workflow
```

### Pull Request Rules

- All code merges via Pull Request — no direct pushes to `main` or `develop`
- Every PR requires all CI checks passing (tests, lint, type checks)
- Descriptive title and summary with what changed and why
- Squash merge to keep history clean
- One logical change per PR — don't bundle unrelated work

### Branch Strategy

```
main                        ← production-ready, protected
├── develop                 ← integration branch
│   ├── feature/backend-pipeline
│   ├── feature/frontend-upload
│   ├── feature/api-endpoints
│   └── fix/color-threshold
```

## File Organization

- Keep files focused and small — if a file grows beyond ~200 lines, consider splitting
- Group by feature/domain, not by file type
- Test files mirror source file structure
- No business logic in route handlers — delegate to service modules
