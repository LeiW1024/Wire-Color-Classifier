# Project Workflow — Full Detail

## 1. Starting New Work

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

## 2. TDD Development Cycle

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
pytest tests/integration/test_sam_pipeline.py::test_my_new_test -v   # must FAIL first
# Write implementation
pytest tests/integration/test_sam_pipeline.py::test_my_new_test -v   # must PASS
pytest tests/ -v   # run full suite before committing
```

**Frontend (Jest):**

```bash
cd frontend
npx jest ResultsView --watch   # must FAIL first
# Write implementation
npx jest ResultsView --watch   # must PASS
npx jest   # run full suite before committing
```

**SAM accuracy tests** — require model file, skip in CI automatically:

```bash
pytest tests/accuracy/ -v
```

---

## 3. Committing Changes

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

## 4. Code Review

Code review is performed using Claude Code skills and subagents — not manual-only review. Run at least one of the following before opening a PR.

### Primary: `/code-review` skill

Invoked via the Claude Code skill system. Analyzes the diff against the base branch for bugs, logic errors, security issues, and coding standard violations.

```
/code-review
```

Checks performed:
- SQL safety and injection risks
- LLM trust boundary violations (if applicable)
- Conditional side effects and edge cases
- Adherence to `rules/coding-standards.md`
- Test coverage gaps

### Secondary: `superpowers:requesting-code-review`

Use after completing a major feature or implementation step to verify work meets requirements before merging.

```
# In Claude Code — invoke via Skill tool
superpowers:requesting-code-review
```

### Independent opinion: `feature-dev:code-reviewer` subagent

For a fully independent review (no shared context with the current session), dispatch the `feature-dev:code-reviewer` subagent. It reads the codebase fresh and reports high-confidence issues only.

### Rules

- Run code review **before** pushing for PR — not after
- Address all high-confidence findings before merging
- Do not merge a PR with unresolved critical or security findings
- Low-confidence findings may be deferred with a comment explaining why

---

## 5. Opening a Pull Request

When the feature is complete, tests pass, and code review is done:

```bash
git push origin feature/<name>
```

PR requirements on GitHub:
- **Base branch:** `develop`
- **Title:** descriptive, matches commit type (`feat:`, `fix:`, etc.)
- **Body:** what changed and why, test plan checklist
- **Merge strategy:** Squash merge (keeps history clean)

CI checks that must pass:

| Check | Tool | Requirement |
|-------|------|-------------|
| Backend lint | Ruff | Zero errors |
| Backend tests | pytest | All pass, ≥80% coverage |
| Frontend lint | ESLint + tsc | Zero errors |
| Frontend tests | Jest | All pass, ≥70% coverage |
| E2E tests | Playwright | All critical paths pass |

---

## 6. Branch Flow

```
feature/* ──PR──→ develop ──PR──→ main
```

- `feature/*` branches are created from `develop`
- Merges into `develop` happen via PR only — never direct push
- `develop` is the integration branch — always in a working state
- `main` is production-ready — only receives merges from `develop` via PR

```bash
# After feature PR is merged into develop:
git checkout develop && git pull origin develop

# When develop is stable and ready for release:
# Open PR on GitHub: develop → main
```

---

## 7. CI/CD Pipeline

Triggered automatically on every PR and push:

```
On Pull Request
├── Backend CI     — Ruff lint → pytest (≥80% cov) → accuracy gate
├── Frontend CI    — ESLint → tsc → Jest (≥70% cov)
└── E2E Tests      — Playwright (runs after both above pass)

On Merge to main
└── Deploy         — docker compose build → test → push images
```

GitHub Actions workflow files:

| File | Trigger | What It Does |
|------|---------|--------------|
| `.github/workflows/backend-ci.yml` | PR touching `backend/**` | Lint, type check, pytest, coverage |
| `.github/workflows/frontend-ci.yml` | PR touching `frontend/**` | ESLint, tsc, Jest, coverage |
| `.github/workflows/e2e.yml` | All PRs (after CI passes) | Playwright upload/analyze flow |
| `.github/workflows/deploy.yml` | Push to `main` | Build + push Docker images |

**SAM model in CI:** The model file (`sam_vit_b.pth`) is not in git. Tests that require it are decorated with `@pytest.mark.skipif(not _sam_model_available(), ...)` and skipped automatically. Run and verify locally before merging.

---

## Complete Development Example

```bash
# 1. Start from develop
git checkout develop && git pull origin develop
git checkout -b feature/backend

# 2. Write a failing test first (TDD RED)
pytest tests/integration/test_sam_pipeline.py::test_new_feature -v  # FAIL ✓

# 3. Implement the feature (TDD GREEN)
pytest tests/integration/test_sam_pipeline.py::test_new_feature -v  # PASS ✓

# 4. Run full suite (TDD CLEAN)
pytest tests/ -v && cd ../frontend && npx jest

# 5. Run code review skill (before opening PR)
# In Claude Code: /code-review  or  superpowers:requesting-code-review
# Address all findings

# 6. Commit
git add backend/app/sam_pipeline.py backend/tests/integration/test_sam_pipeline.py
git commit -m "feat(backend): add new feature"

# 7. Push and open PR → develop on GitHub
git push origin feature/backend
# Open PR, request peer review, address comments

# 8. After PR merged, sync develop
git checkout develop && git pull origin develop

# 9. When develop is stable, open PR: develop → main
```
