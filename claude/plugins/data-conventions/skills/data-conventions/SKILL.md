---
name: data-conventions
description: Team defaults for data work in OCHA CHD DS repos — storage/DB access (ocha-stratus), blob path convention, valid_time vs issued_time, CRS, geo stack, Python tooling (uv), marimo idioms. Use when writing or reviewing data-loading, processing, or notebook code in a team repo.
---

# Team data conventions

**Advisory, not law** (last reviewed 2026-07): these are the team's defaults. The
repo you're in wins — check its CLAUDE.md and existing code first, and don't retrofit
a deliberately-divergent project. If a default here has drifted from practice, say so
and open an issue on `OCHA-DAP/ds-knowledge-base`.

## Data

- `ocha-stratus` for blob + Postgres access — not raw Azure SDK or psycopg2.
  Rasters live in blob; per-admin raster stats in the DB (ERA5, SEAS5, IMERG,
  Floodscan). Details + gotchas: the `blob-io` skill in this plugin;
  KB `infrastructure/libs/ocha-stratus.md`.
- Blob paths: `{PROJECT_PREFIX}/{raw|processed}/{datasource}/{filename}`;
  `PROJECT_PREFIX` comes from `src.constants`, never hardcoded.
- Try `ocha-lens` before writing custom processing.
  → KB `infrastructure/libs/ocha-lens.md`
- `valid_time` for observation/forecast validity, `issued_time` for publication;
  issued month + leadtime = valid month.
- CRS is EPSG:4326 unless noted; `xarray` for gridded, `geopandas` for vector,
  `rioxarray` for raster I/O and clipping.
- CODAB boundaries: the repo's own loader if present, else FieldMaps via stratus;
  name/code-only metadata from DB `public.polygons` (limited countries).

## Python

Python 3.11+ · `uv` (not pip) · type hints on signatures · f-strings · never silently
suppress exceptions. Typical layout: `src/constants.py` (PROJECT_PREFIX),
`src/datasources/`, `src/utils/` — a guide, not a rule; check the repo first.

## Marimo

Bare expression on the cell's last line to display (`_fig`, not `return _fig`);
`_`-prefix cell-local variables; `print()` is invisible in `marimo run` — use
`mo.md(...)` or `mo.ui.table(df)`.
