---
name: data-conventions
description: The team's opinionated defaults for writing data code in OCHA CHD DS repos — Python tooling (uv), repo layout, processing-library preferences (ocha-lens), geo stack, marimo idioms. Use when writing or reviewing data-loading, processing, or notebook code in a team repo. Advisory — the repo's own conventions always win.
---

# Team data conventions (opinionated house style)

**Advisory, not law** (last reviewed 2026-07): these are the team's defaults. The
repo you're in wins — check its CLAUDE.md and existing code first, and don't retrofit
a deliberately-divergent project. If a default here has drifted from practice, say so
and open an issue on `OCHA-DAP/ds-knowledge-base`.

(For *access* to team data — stratus, blob naming, `valid_time` semantics, third-party
loaders — see the `data-access` plugin; those are facts, not style.)

## Processing

- **Try `ocha-lens` before writing custom processing.**
  → KB `infrastructure/libs/ocha-lens.md`
- Geo stack: `xarray` for gridded, `geopandas` for vector, `rioxarray` for raster
  I/O and clipping.

## Python

Python 3.11+ · `uv` (not pip) · type hints on signatures · f-strings · never silently
suppress exceptions. Typical layout: `src/constants.py` (PROJECT_PREFIX),
`src/datasources/`, `src/utils/` — a guide, not a rule; check the repo first.

## Marimo

Bare expression on the cell's last line to display (`_fig`, not `return _fig`);
`_`-prefix cell-local variables; `print()` is invisible in `marimo run` — use
`mo.md(...)` or `mo.ui.table(df)`.
