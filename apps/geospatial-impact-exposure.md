---
content_type: app
name: geospatial-impact-exposure
purpose: Static GitHub Pages map+table of population-in-damaged-buildings per admin per damage source for the 2026-06-24 Venezuela earthquake, with an HNO pre-existing-need overlay. Its own in-repo one-off pipelines pre-compute the data it serves.
status: live
tech: other                # MapLibre GL + sortable-table static SPA over committed web/data/*
related: standalone
deployment:
  platform: gh-pages
  ref: "OCHA-DAP/ds-geospatial-impact-exposure @ main (artifact deploy via deploy-pages.yml)"
  url: https://ocha-dap.github.io/ds-geospatial-impact-exposure/
  resource_group: null
inputs:
  - "web/data/exposure.json (committed) — per-admin per-source figures + HNO need overlay; what the page renders"
  - "web/data/adm1.geojson, adm2.geojson (committed) — simplified admin boundaries for the choropleth"
  - "web/data/buildings.pmtiles, worldpop.png (committed) — validation-only per-building population tiles + colorized population grid"
  - "(upstream, via the in-repo one-off pipelines that generate web/data/*) chd-ds-geospatial-impact-viewer lake gold building_flags + silver Overture base + bronze CODAB; WorldPop 100m R2025A VEN 2026; Overture buildings 2026-06-17.0; HNO 2025 (HDX)"
depends_on: [chd-ds-geospatial-impact-viewer, worldpop, hnrp]
source_repo: ocha-dap/ds-geospatial-impact-exposure
source_branch: main
source_sha: 64ed375
code_ref:
  - web/index.html
  - README.md
  - pipelines/fetch_worldpop.py
  - pipelines/fetch_overture_attrs.py
  - pipelines/fetch_hno.py
  - pipelines/estimate_exposure.py
  - pipelines/build_validation_layers.py
  - pipelines/mirror.py
  - src/giex/config.py
  - src/giex/db.py
  - docs/decisions/0001-dasymetric-building-population-exposure.md
  - docs/decisions/0002-residential-only-and-clamped-area-weight.md
  - docs/decisions/0003-pre-existing-need-overlay.md
  - .github/workflows/deploy-pages.yml
extra:
  event: "2026-06-24 Venezuela earthquake (USGS us6000t7zp; EMSR884)"
  adm0: VE
  data_prep: "The app serves static committed web/data/*. Those files are pre-computed by the repo's own one-off, on-demand pipelines (fetch_worldpop → fetch_overture_attrs → fetch_hno → estimate_exposure → optional build_validation_layers), run locally via `uv run`. No Databricks or cron'd GHA compute job → not in infrastructure/pipeline-registry.md; only the GitHub Pages publish step is a GHA workflow (push/dispatch, not cron)."
  reclassified: "2026-07-06 pipeline -> app (PR #151 review): the deliverable is a GitHub Pages map+table; the in-repo pipelines exist only to prepare its data. Briefly reclassified to analysis mid-review before landing on app."
visibility: public
last_synced: "2026-07-02"
---

# ds-geospatial-impact-exposure

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."
>
> **App with its own one-off data prep** (reclassified 2026-07-06 per PR #151 review). The
> deliverable is a static GitHub Pages map+table stood up for a single event — the 2026-06-24
> Venezuela earthquake. The repo's `pipelines/*` scripts are its bespoke, on-demand data
> preparation, not a living scheduled system; they're documented below because re-running them
> is how the page's data is refreshed.

## What it shows

A static, single-event **map + sortable table** of *population living in damaged buildings* for
the 2026-06-24 Venezuela earthquake response, broken out **per admin unit (adm1/adm2) per damage
source**, plus an **HNO pre-existing-need overlay**. The headline decision-useful figure is
`agree2` (population in buildings that ≥2 independent damage sources flag as damaged). It is a
**floor from partial assessments** — it tracks *residents of damaged buildings*, not casualties.
A companion `web/validate.html` zoom-in page shows per-building population for a sanity check.

## Key features

- **MapLibre GL choropleth** of exposure per admin unit, with a source selector (Microsoft AI,
  Copernicus EMS `EMSR884`, IMPACT SAR, OSU coherence) plus `any` (union) and `agree2` (≥2 agree)
  metrics, over the committed `web/data/*.geojson` + `exposure.json`.
- **Sortable table** of per-admin figures — population exposed and `n_damaged` per metric — and
  the HNO overlay (`exposed_in_need = exposure × min(1, PiN_sector / population)`, assumed uniform
  across the admin — ADR-0003).
- **Validation view** (`web/validate.html`): a PMTiles vector layer of the ~340k damaged building
  footprints (per-building population on hover) over a colorized WorldPop PNG.
- Standalone — a one-off response product, not wired into any AA framework or other app.

## Data

The page renders **static files committed under `web/data/`** — there is no live backend, DB, or
runtime blob read from the deployed site:

| file | what |
|---|---|
| `exposure.json` | per-admin per-source figures + HNO need overlay |
| `adm1.geojson`, `adm2.geojson` | simplified admin boundaries for the map |
| `buildings.pmtiles`, `worldpop.png` | validation-only: per-building population tiles + colorized population grid |

**How those files are produced — the in-repo one-off pipelines.** Compute is run on-demand
(locally, `uv run python pipelines/<script>.py`); it never writes back to the upstream viewer lake
— all of its own outputs land under its own blob prefix
(`projects/ds-geospatial-impact-exposure/...`), and the committed `web/data/*` are the copy the
site serves. The tidy long table `exposure_by_admin.parquet` (level, pcode, metric, pop_exposed,
n_damaged) also lands at `projects/ds-geospatial-impact-exposure/processed/exposure/adm0=VE/`.

Read-only downstream of **`ds-geospatial-impact-estimates`** (the "damage viewer", see
[apps/chd-ds-geospatial-impact-viewer](chd-ds-geospatial-impact-viewer.md)):

- viewer **gold** `model=common/adm0=VE/building_flags.parquet` — per-building flags for whether
  Microsoft, Copernicus EMS, IMPACT SAR (S1 amplitude), and OSU (S1 coherence) each called a
  building damaged.
- viewer **silver** `source=overture/adm0=VE` — Overture building base (`id` + `geometry` only;
  attributes were dropped at the viewer's ingest).
- viewer **bronze** `source=codab/adm0=VE` — adm1/adm2 CODAB boundaries.

Fetched independently into this project's own bronze:

- **Overture building attributes** (subtype/class/height/num_floors) — pulled straight from the
  Overture buildings theme on public S3, release `2026-06-17.0` (the same release the viewer's
  base was built from), filtered to a bbox over the assessed north-central VE states. Only the
  tagged minority (~3% of VE) is stored; an `id` missing from this table is "untagged."
- **WorldPop** 100 m constrained population, VEN 2026 `R2025A` — pulled at 100 m directly from the
  WorldPop portal (the team's shared blob mirror is only 1 km, too coarse to redistribute to
  individual footprints; see [dataset: WorldPop](../infrastructure/datasets/worldpop.md)).
- **HNO 2025** People-in-Need per sector per municipio (HDX, `ven_hpc_needs_api_2025.csv`) — the
  pre-existing-need overlay; 2025 is the latest year with admin-2 detail (see
  [dataset: HNRP](../infrastructure/datasets/hnrp.md)).

**Pipeline steps (data-prep, run in order):**

1. **`fetch_worldpop.py`** — download the 100 m constrained WorldPop GeoTIFF for VE, land it in
   this project's bronze.
2. **`fetch_overture_attrs.py`** — query Overture S3 (DuckDB `httpfs`) over a bbox for
   subtype/class/height, land tagged rows in bronze.
3. **`fetch_hno.py`** — pull the HDX HNO 2025 CSV, split cluster codes into a People-in-Need column
   per sector, join key = normalized `state|municipio` name (the HNO uses legacy `VE####` pcodes,
   not the FieldMaps pcodes the admin boundaries use), land in bronze.
4. **`estimate_exposure.py`** (the core) — mirrors upstream + own bronze blobs to local disk first
   (`mirror.py`; the blob endpoint stalls on sustained reads), then in DuckDB (spatial extension):
   spatially join Overture base → adm2 + damage flags + attributes; drop explicitly-tagged
   non-residential buildings (ADR-0002); **dasymetric redistribution** — split each WorldPop 100 m
   cell's population across the residential buildings whose centroid falls in it, weighted by
   *clamped* footprint area (floor 30 m², cap 99th pctile — ADR-0001/0002); sum per-building
   population over each source's damaged set, plus `any` (union) and `agree2` (≥2 sources agree);
   overlay HNO need (ADR-0003); write `exposure_by_admin.parquet` to blob and the `web/data/*`
   files.
5. **`build_validation_layers.py`** (optional, needs `tippecanoe` on PATH) — reuses the same
   building load + dasymetric assignment, keeps only the ~340k damaged footprints, builds the
   `buildings.pmtiles` layer + colorized `worldpop.png` for `web/validate.html`.
6. Commit the regenerated `web/data/*` and push to `main` — that fires `deploy-pages.yml`, which
   uploads `web/` as-is (it does **not** re-run the pipeline; the workflow has no blob secrets).

Full method rationale: [ADR-0001](https://github.com/OCHA-DAP/ds-geospatial-impact-exposure/blob/main/docs/decisions/0001-dasymetric-building-population-exposure.md),
[ADR-0002](https://github.com/OCHA-DAP/ds-geospatial-impact-exposure/blob/main/docs/decisions/0002-residential-only-and-clamped-area-weight.md),
[ADR-0003](https://github.com/OCHA-DAP/ds-geospatial-impact-exposure/blob/main/docs/decisions/0003-pre-existing-need-overlay.md).

## Deployment & access

- **GitHub Pages**, artifact deploy via `.github/workflows/deploy-pages.yml`
  (`upload-pages-artifact` + `deploy-pages@v4`; there is **no `gh-pages` branch**). URL:
  https://ocha-dap.github.io/ds-geospatial-impact-exposure/ (public).
- Triggered on `push` to `main` touching `web/**`, or `workflow_dispatch`. The workflow only
  publishes the contents of `web/` — it never runs the compute pipeline.
- No Azure resource, no Databricks job, no cron; **not in `infrastructure/pipeline-registry.md`**
  (that registry only tracks scheduled compute).

## Maintenance / known issues

- **Refreshing the page's data means re-running the compute locally, then committing.** If
  `web/data/*.json` / `*.geojson` look stale on the live site, check whether `estimate_exposure.py`
  was rerun *and* the regenerated files were committed and pushed to `main`; `deploy-pages.yml`
  itself never runs the compute pipeline.
- **Everything hardcodes `STAGE = "dev"`** at the top of each `pipelines/*.py` script, independent
  of the `GIEX_STAGE` env var read by `load_settings()` — there is effectively no prod slot in use
  yet; don't expect `GIEX_STAGE=prod` to change behavior without also editing the scripts.
- **Blob endpoint stalls on sustained reads** — this is why `mirror.py` downloads the Overture base
  + `building_flags` to local disk (`/tmp/giex_cache` by default, `GIEX_CACHE` env override) before
  DuckDB reads them; if a fetch hangs, check whether it's trying to read `az://` directly instead of
  through `mirror_blob`/`mirror_prefix`.
- **Missing `GIEX_BLOB_ACCOUNT_PREFIX`** raises immediately from `Settings.account_name` — check
  `.env`. **Missing SAS token** raises from `Settings.sas_token` — same shared `DSCI_AZ_BLOB_*`
  tokens as `ocha-stratus` (see [libs/ocha-stratus](../infrastructure/libs/ocha-stratus.md)); check
  the shell environment, not the repo (never committed).
- **Overture attribute coverage is ~3% for VE** — an untagged building is *assumed* residential
  (ADR-0002); if a future country/event has much better Overture tagging,
  `residential_subset()`'s untagged-is-residential default may need revisiting.
- **HNO name-join misses** — `state + municipio` name matching (HDX legacy `VE####` pcodes vs.
  FieldMaps pcodes) matches 92 of the 95 municipios in the output (~98.5% of exposure by weight —
  verified against `web/data/exposure.json`) for this event; unmatched municipios show "no HNO
  data" rather than erroring. A different country's HNO extract would need its own
  name-normalization check.
- **`build_validation_layers.py` requires `tippecanoe` on PATH** (`brew install tippecanoe`; not
  pip-installable) — will fail outright without it; this step is optional (only feeds
  `web/validate.html`).
- **This is single-event, single-country (`ADM0 = "VE"`) code** — extending to another
  country/event means editing constants (`ADM0`, `WORLDPOP_FILE`, the HNO year/URL, the Overture
  release/bbox) at the top of each script, not passing a parameter.
- **Runtime deps for the data prep:** DuckDB with `spatial` / `azure` / `httpfs` extensions;
  `rioxarray`/`rasterio` (WorldPop raster I/O); `geopandas`/`shapely`/`pyproj` (boundary
  simplification/export); `pillow` (validation PNG). Config via `.env` (`GIEX_BLOB_ACCOUNT_PREFIX`,
  `GIEX_STAGE` default `dev`, `GIEX_CONTAINER` default `projects`, `GIEX_PROJECT_PREFIX`) — see
  `src/giex/config.py`.
