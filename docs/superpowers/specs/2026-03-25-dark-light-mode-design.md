# Dark / Light Mode Toggle — Design Spec

**Date:** 2026-03-25
**Scope:** Frontend only — `wire-color-classifier/frontend`

## Summary

Add a dark/light mode toggle to the Wire Color Classifier UI. The toggle is a monospace text button in the header. Light mode uses a blueprint/cool-white slate palette. Preference persists via `localStorage`, with `prefers-color-scheme` as the first-visit fallback.

## Toggle Placement

Header, right side — inline with "SAM · v2.0", separated by a `|` divider:

```
WIRE COLOR CLASSIFIER          SAM · v2.0  |  ☀ LIGHT
```

When in light mode the label flips to `🌙 DARK`. Styled in `var(--accent-cyan)`, monospace font, matching the existing header aesthetic.

## Theming Approach

All colors are already CSS custom properties in `globals.css`. Light mode is implemented as a `[data-theme="light"]` override block that redefines every variable. No Tailwind dark mode, no extra libraries.

**Light theme palette (Blueprint / Cool White):**

| Variable | Dark | Light |
|---|---|---|
| `--bg-deep` | `#07080a` | `#f8fafc` |
| `--bg-surface` | `#0d0f12` | `#f0f4f8` |
| `--bg-elevated` | `#141618` | `#e8eef4` |
| `--bg-hover` | `#1c1f23` | `#dde5ef` |
| `--border` | `#232830` | `#d0d8e4` |
| `--border-bright` | `#2e3440` | `#b8c8d8` |
| `--text-primary` | `#e8eaf0` | `#1e293b` |
| `--text-secondary` | `#8892a0` | `#64748b` |
| `--text-muted` | `#4a5260` | `#94a3b8` |
| `--accent-cyan` | `#00d4ff` | `#0099cc` |
| `--accent-cyan-dim` | `rgba(0,212,255,0.12)` | `rgba(0,153,204,0.12)` |
| `--accent-red` | `#ff3b5c` | `#e8324a` |
| `--scan-color` | `rgba(0,212,255,0.08)` | `rgba(0,153,204,0.05)` |

The `body` radial gradient background is also adjusted for light mode.

## Components

### `ThemeToggle` (new — `src/components/ThemeToggle.tsx`)

- `'use client'` React component
- Reads initial theme from `localStorage` → falls back to `prefers-color-scheme` → defaults to `dark`
- On mount, sets `document.documentElement.dataset.theme`
- On click, toggles theme + writes to `localStorage`
- Renders: `☀ LIGHT` (dark mode active) or `🌙 DARK` (light mode active)

### `page.tsx` (modified)

- Import and render `<ThemeToggle />` in the header's right section, after the `SAM · v2.0` span

### `globals.css` (modified)

- Add `[data-theme="light"]` block with all variable overrides
- Adjust `body` background-image for light mode

## Persistence

- `localStorage` key: `"theme"`, values: `"dark"` | `"light"`
- On first visit with no stored preference: read `window.matchMedia('(prefers-color-scheme: light)')`

## Testing

- Unit test for `ThemeToggle` in `__tests__/components/ThemeToggle.test.tsx`
  - Renders correct label in dark mode (`☀ LIGHT`)
  - Renders correct label in light mode (`🌙 DARK`)
  - Clicking toggles the label and updates `document.documentElement.dataset.theme`
  - Persists preference to `localStorage`

## Branch & Commit

- Branch: `feature/frontend`
- Commit: `feat(frontend): add dark/light mode toggle with blueprint light theme`
- PR base: `develop`
