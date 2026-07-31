---
content_type: app
name: regional-forecasts
purpose: "Gallery + year-viewer of African regional seasonal forecast products (ACMAD, AGRHYMET) for comparison against global forecasts (SEAS5)"
status: live
tech: other
related: standalone
deployment:
  platform: gh-pages
  ref: OCHA-DAP/ds-regional-forecasts main /docs
  url: https://ocha-dap.github.io/ds-regional-forecasts/
inputs:
  - "blob: ds-regional-forecasts/raw/{acmad,agrhymet,zenodo}/... (dev) — mirrored raw archive"
  - "docs/catalog.json — derived metadata catalog committed with the site"
depends_on: []
source_repo: ocha-dap/ds-regional-forecasts
source_branch: main
source_sha:
code_ref:
  - docs/index.html
  - src/run_grab.py
  - src/derive_assets.py
extra:
  data_pages: "infrastructure/datasets/acmad.md + agrhymet.md hold the source-access knowledge"
visibility: public
last_synced: "2026-07-26"
---

# regional-forecasts

> Static gallery + year-viewer of African regional seasonal forecasts, GitHub Pages.

## What it shows

Every seasonal forecast product we could retrieve from **ACMAD** (continental
Long-Range Forecast, ACCOF statements, hosted RCOF outputs) and **AGRHYMET**
(PRESASS, PRESAGG — including Wayback-rescued 2016–2022 issues and the digitized
Zenodo NetCDF record), so regional consensus products can be browsed together and
compared with global forecasts such as ECMWF SEAS5.

## Key features

- **Gallery tab** — filter by org / product / year / season / format / language;
  coverage matrix of issues per calendar month (the around-the-year view).
- **Year viewer tab** — pick a product, flip through years with arrow keys; forecast
  maps are extracted from inside AGRHYMET PDFs (largest embedded raster) so the
  tercile maps display directly, falling back to page-1 renders.

## Data

Two-layer storage: raw archive in **dev blob** (`ds-regional-forecasts/raw/...`,
uploaded by `src/upload_blob.py`); the repo/Pages carries only derived assets
(thumbnails, resized maps, `catalog.json`). Scrapers are resumable; re-running
`src/run_grab.py` + `src/derive_assets.py` refreshes everything. Source-access
details and gotchas live on the dataset pages
([acmad](../infrastructure/datasets/acmad.md),
[agrhymet](../infrastructure/datasets/agrhymet.md)).
