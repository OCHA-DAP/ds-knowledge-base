---
content_type: pipeline
name: ds-geospatial-impact-exposure
type: exposure
status: live
deployment:
  platform: manual
  resource_group:
  jobs:
    - { name: "Compute exposure pipeline (fetch_worldpop -> fetch_overture_attrs -> fetch_hno -> estimate_exposure -> build_validation_layers)", ref: "pipelines/*.py (uv run, local)", schedule: "on-demand", status: live }
    - { name: "Deploy web to GitHub Pages", ref: ".github/workflows/deploy-pages.yml", schedule: "event (push to main touching web/** or workflow_dispatch)", status: live }
inputs:
  - "viewer gold model=common/adm0=VE/building_flags.parquet (per-building damage flags, from ds-geospatial-impact-estimates)"
  - "viewer silver source=overture/adm0=VE (Overture building footprints, id + geometry only)"
  - "Overture buildings theme, release 2026-06-17.0, public S3 (subtype/class/height attrs, bbox-filtered) -> this project's bronze"
  - "viewer bronze source=codab/adm0=VE (adm1/adm2 CODAB boundaries)"
  - "WorldPop 100 m constrained population, VEN 2026 R2025A, from data.worldpop.org -> this project's bronze"
  - "HNO 2025 People-in-Need per municipio (HDX ven_hpc_needs_api_2025.csv) -> this project's bronze"
dependencies:
  - ocha-stratus
  - duckdb (spatial, azure, httpfs extensions)
  - rioxarray/rasterio
  - geopandas/shapely/pyproj
  - pillow
  - azure-storage-blob
  - tippecanoe (external binary, validation layers only, not in pyproject deps)
  - "DSCI_AZ_BLOB_{DEV,PROD}_SAS[_WRITE] (shared team SAS tokens, same as ocha-stratus)"
  - "GIEX_BLOB_ACCOUNT_PREFIX (local .env)"
outputs:
  - "blob processed/exposure/adm0=VE/exposure_by_admin.parquet (tidy long: level, pcode, metric, pop_exposed, n_damaged)"
  - "web/data/exposure.json (per-admin per-source figures + HNO need overlay, committed to repo)"
  - "web/data/adm1.geojson, web/data/adm2.geojson (simplified admin boundaries, committed to repo)"
  - "web/data/buildings.pmtiles, web/data/worldpop.png (optional validation-map layers, committed to repo)"
  - "GitHub Pages static site (MapLibre choropleth + sortable table)"
downstream: []
depends_on: [chd-ds-geospatial-impact-viewer, worldpop, hnrp]
source_repo: ocha-dap/ds-geospatial-impact-exposure
source_branch: main
source_sha: 64ed375
code_ref:
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
  not_in_pipeline_registry: "no Databricks/GHA scheduled job exists for the compute step; only the GH Pages publish step is a GHA workflow, and it's push/dispatch-triggered, not cron"
visibility: public
last_synced: "2026-07-02"
---

# ds-geospatial-impact-exposure

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On-demand, single-event: take another repo's harmonized per-building
satellite-damage flags for Venezuela, redistribute WorldPop population onto
residential building footprints (dasymetric), sum population-in-damaged-buildings
per admin per source, overlay pre-existing HNO need, and publish a static
GitHub Pages map+table.*

## Jobs & schedule

Not a scheduled pipeline — it was stood up for a single event (the 2026-06-24
Venezuela earthquake) and the compute steps are run manually. Only the web
publish step is automated (GHA on push).

| job | ref | schedule | status |
|---|---|---|---|
| Compute exposure pipeline (`fetch_worldpop.py` → `fetch_overture_attrs.py` → `fetch_hno.py` → `estimate_exposure.py` → optional `build_validation_layers.py`) | run locally via `uv run python pipelines/<script>.py` | on-demand | live |
| Deploy web to GitHub Pages | `.github/workflows/deploy-pages.yml` | `push` to `main` touching `web/**`, or `workflow_dispatch` | live |

Not in `infrastructure/pipeline-registry.md` — there is no Databricks job or cron'd
GHA workflow to register; the registry only tracks scheduled compute.

## Inputs

Read-only downstream of **`ds-geospatial-impact-estimates`** (the "damage
viewer", see [apps/chd-ds-geospatial-impact-viewer](../apps/chd-ds-geospatial-impact-viewer.md)) —
this project never writes to that lake:

- viewer **gold** `model=common/adm0=VE/building_flags.parquet` — per-building
  flags for whether Microsoft, Copernicus EMS, IMPACT SAR (S1 amplitude), and
  OSU (S1 coherence) each called a building damaged.
- viewer **silver** `source=overture/adm0=VE` — Overture building base
  (`id` + `geometry` only; attributes were dropped at the viewer's ingest).
- viewer **bronze** `source=codab/adm0=VE` — adm1/adm2 CODAB boundaries.

Fetched independently into this project's own bronze:

- **Overture building attributes** (subtype/class/height/num_floors) — pulled
  straight from the Overture buildings theme on public S3, release
  `2026-06-17.0` (the same release the viewer's base was built from), filtered
  to a bbox over the assessed north-central VE states. Only the tagged minority
  (~3% of VE) is stored; an `id` missing from this table is "untagged."
- **WorldPop** 100 m constrained population, VEN 2026 `R2025A` — pulled at
  100 m directly from the WorldPop portal (the team's shared blob mirror is
  only 1 km, too coarse to redistribute to individual footprints).
- **HNO 2025** People-in-Need per sector per municipio (HDX,
  `ven_hpc_needs_api_2025.csv`) — the pre-existing-need overlay; 2025 is the
  latest year with admin-2 detail (see [dataset: HNRP](../infrastructure/datasets/hnrp.md)).

## Steps

1. **`fetch_worldpop.py`** — download the 100 m constrained WorldPop GeoTIFF for
   VE, land it in this project's bronze.
2. **`fetch_overture_attrs.py`** — query Overture S3 (DuckDB `httpfs`) over a
   bbox for subtype/class/height, land tagged rows in bronze.
3. **`fetch_hno.py`** — pull the HDX HNO 2025 CSV, split cluster codes into a
   People-in-Need column per sector, join key = normalized `state|municipio`
   name (the HNO uses legacy `VE####` pcodes, not the FieldMaps pcodes the
   admin boundaries use), land in bronze.
4. **`estimate_exposure.py`** (the core) — mirrors upstream + own bronze blobs
   to local disk first (`mirror.py`; the blob endpoint stalls on sustained
   reads), then in DuckDB (spatial extension): spatially join Overture base →
   adm2 + damage flags + attributes; drop explicitly-tagged non-residential
   buildings (ADR-0002); **dasymetric redistribution** — split each WorldPop
   100 m cell's population across the residential buildings whose centroid
   falls in it, weighted by *clamped* footprint area (floor 30 m², cap 99th
   pctile — ADR-0001/0002); sum per-building population over each source's
   damaged set, plus `any` (union) and `agree2` (≥2 sources agree, the most
   decision-useful figure); overlay HNO need (`exposed_in_need = exposure ×
   min(1, PiN_sector / population)`, assumed uniform across the admin —
   ADR-0003); write outputs.
5. **`build_validation_layers.py`** (optional, needs `tippecanoe` on PATH) —
   reuses the same building load + dasymetric assignment, keeps only the
   ~340k damaged footprints, builds a PMTiles vector-tile layer (per-building
   population on hover) plus a colorized WorldPop PNG overlay, for the
   `web/validate.html` zoom-in sanity-check page.
6. Commit the regenerated `web/data/*` — pushing to `main` fires
   `deploy-pages.yml`, which uploads `web/` as-is (it does not re-run the
   pipeline; the workflow has no blob secrets).

Full method rationale: [ADR-0001](https://github.com/OCHA-DAP/ds-geospatial-impact-exposure/blob/main/docs/decisions/0001-dasymetric-building-population-exposure.md),
[ADR-0002](https://github.com/OCHA-DAP/ds-geospatial-impact-exposure/blob/main/docs/decisions/0002-residential-only-and-clamped-area-weight.md),
[ADR-0003](https://github.com/OCHA-DAP/ds-geospatial-impact-exposure/blob/main/docs/decisions/0003-pre-existing-need-overlay.md).

## Outputs

| output | where | what |
|---|---|---|
| `exposure_by_admin.parquet` | blob `projects/ds-geospatial-impact-exposure/processed/exposure/adm0=VE/` | tidy long table: level, pcode, metric, pop_exposed, n_damaged |
| `exposure.json` | `web/data/` (committed) | per-admin per-source figures + HNO need overlay, for the static page |
| `adm1.geojson`, `adm2.geojson` | `web/data/` (committed) | simplified admin boundaries for the map |
| `buildings.pmtiles`, `worldpop.png` | `web/data/` (committed) | validation-only: per-building population vector tiles + colorized population grid |
| static site | GitHub Pages (artifact deploy via `deploy-pages.yml`) | MapLibre choropleth + sortable table over `web/data/*` |

This project never writes back to the upstream `ds-geospatial-impact-estimates`
lake — all of its own outputs land under its own blob prefix
(`projects/ds-geospatial-impact-exposure/...`).

## Dependencies

- **`ocha-stratus`** — blob container-client auth (`mirror.py`), shared
  `DSCI_AZ_BLOB_{DEV,PROD}_SAS[_WRITE]` tokens (same ones the upstream viewer
  and `ocha-stratus` use generally); no DB access (this pipeline uses no
  Postgres tables).
- **DuckDB** with `spatial` (building↔admin join, area calc), `azure`
  (direct small blob reads/writes), and `httpfs` (Overture S3 read) extensions
  installed at runtime.
- `rioxarray`/`rasterio` — WorldPop raster I/O; `geopandas`/`shapely`/`pyproj`
  — admin boundary simplification/export; `pillow` — validation PNG overlay.
- `tippecanoe` — external binary (not pip-installable; `brew install
  tippecanoe`), needed only for `build_validation_layers.py`.
- Config via `.env` (`GIEX_BLOB_ACCOUNT_PREFIX`, `GIEX_STAGE` default `dev`,
  `GIEX_CONTAINER` default `projects`, `GIEX_PROJECT_PREFIX`) — see
  `src/giex/config.py`. All pipeline scripts currently hardcode
  `STAGE = "dev"` regardless of `GIEX_STAGE`.

## Failure modes & debugging

- **Everything hardcodes `STAGE = "dev"`** at the top of each `pipelines/*.py`
  script, independent of the `GIEX_STAGE` env var read by `load_settings()` —
  there is effectively no prod slot in use yet; don't expect `GIEX_STAGE=prod`
  to change behavior without also editing the scripts.
- **Blob endpoint stalls on sustained reads** — this is why `mirror.py`
  downloads the Overture base + `building_flags` to local disk
  (`/tmp/giex_cache` by default, `GIEX_CACHE` env override) before DuckDB
  reads them; if a fetch hangs, check whether it's trying to read `az://`
  directly instead of through `mirror_blob`/`mirror_prefix`.
- **Missing `GIEX_BLOB_ACCOUNT_PREFIX`** raises immediately from
  `Settings.account_name` — check `.env`.
- **Missing SAS token** raises from `Settings.sas_token` — same shared
  `DSCI_AZ_BLOB_*` tokens as `ocha-stratus`; check the shell environment, not
  the repo (never committed).
- **Overture attribute coverage is ~3% for VE** — an untagged building is
  *assumed* residential (ADR-0002); if a future country/event has much better
  Overture tagging, `residential_subset()`'s untagged-is-residential default
  may need revisiting.
- **HNO name-join misses** — `state + municipio` name matching (HDX legacy
  `VE####` pcodes vs. FieldMaps pcodes) matches 92 of the 95 municipios in the
  output (~98.5% of exposure by weight — verified against `web/data/exposure.json`)
  for this event; unmatched municipios show "no HNO
  data" rather than erroring. A different country's HNO extract would need
  its own name-normalization check.
- **`build_validation_layers.py` requires `tippecanoe` on PATH** — will fail
  outright without it; this step is optional (only feeds `web/validate.html`).
- **This is single-event, single-country (`ADM0 = "VE"`) code** — extending
  to another country/event means editing constants (`ADM0`, `WORLDPOP_FILE`,
  the HNO year/URL, the Overture release/bbox) at the top of each script, not
  passing a parameter.
- **`deploy-pages.yml` only republishes `web/`** — if `web/data/*.json` /
  `*.geojson` look stale on the live site, check whether `estimate_exposure.py`
  was rerun *and* the regenerated files were committed and pushed to `main`;
  the workflow itself never runs the compute pipeline.

## Downstream consumers

None currently — output is a standalone static GitHub Pages page for the
2026-06-24 Venezuela earthquake response, not yet wired into any framework
monitoring or other app. Its only upstream is the "damage viewer"
[chd-ds-geospatial-impact-viewer](../apps/chd-ds-geospatial-impact-viewer.md)
(`ds-geospatial-impact-estimates`), which it reads from but never writes to.
