---
content_type: pipeline
name: ds-sahel-flashflooding
type: exploration   # not a live ingest/monitoring job — pre-framework data-gathering notebooks
status: in-development
deployment:
  platform: manual
  jobs:
    - { name: "exploration notebooks (manual)", ref: "exploration/codab.md, exploration/cerf.md, exploration/emdat.md", schedule: "on-demand", status: development }
inputs:
  - "FieldMaps CODAB shapefiles (`https://data.fieldmaps.io/cod/originals/{iso3}.shp.zip`) for bfa/ner/tcd/nga/cmr"
  - "CERF `AllocationsByYear` extract (manually downloaded Excel, accessed 2024-11-22), placed in blob by hand"
  - "EM-DAT Africa floods extract (manually downloaded Excel, accessed 2024-11-22), placed in blob by hand"
outputs:
  - "blob: dev `projects/ds-sahel-flashflooding/raw/codab/{iso3}.shp.zip` (bfa, ner, tcd, nga, cmr)"
  - "blob: dev `projects/ds-sahel-flashflooding/raw/cerf/AllocationsByYear_<date>.xlsx` (manually staged, not written by code)"
  - "blob: dev `projects/ds-sahel-flashflooding/raw/emdat/emdat_africa_floods_accessed_<date>.xlsx` (manually staged, not written by code)"
  - "no DB writes, no email/Listmonk output, no dashboard — analysis is inline plots in jupytext notebooks, not persisted"
dependencies:
  - "azure-storage-blob (raw SDK via src/utils/blob_utils.py — does NOT use ocha-stratus, unlike current team convention)"
  - "sqlalchemy + psycopg2 (src/utils/db_utils.py builds a chd-rasterstats dev/prod engine, but nothing in the repo calls it — unused/dead)"
  - "geopandas, rioxarray, xarray, pandas, requests, pycountry"
  - "jupytext + jupyter_black (notebooks are stored as paired .md/.ipynb)"
  - "env vars: PROD_BLOB_SAS, DEV_BLOB_SAS (blob), AZURE_DB_PW_DEV, AZURE_DB_PW_PROD (unused DB engine)"
downstream: []
depends_on: []
source_repo: ocha-dap/ds-sahel-flashflooding
source_branch: seasonal-forecasts
source_sha: 64e4c6c
code_ref:
  - src/datasources/codab.py
  - src/datasources/cerf.py
  - src/datasources/emdat.py
  - src/utils/blob_utils.py
  - src/utils/db_utils.py
  - src/constants.py
  - exploration/codab.md
  - exploration/cerf.md
  - exploration/emdat.md
extra:
  reclassification_candidate: "This repo has no jobs, no schedule, no deployment, and no trigger logic — it reads as pre-framework exploration (cf. analysis/eth-flooding.md, analysis/cod-flooding.md), not a living pipeline. Ingested here as a pipeline page per the requesting task; flagged for a maintainer to consider moving to analysis/ds-sahel-flashflooding.md, matching the sibling *-flooding analysis pages."
  branch_name_mismatch: "Active branch is `seasonal-forecasts`, but no seasonal-forecast code (SEAS5/ECMWF/IRI or similar) exists anywhere in src/ or exploration/ — the branch name reflects an intended next step, not current content."
visibility: internal
last_synced: "2026-07-02"
---

# Sahel Flash Flooding — exploration

> **Not a live pipeline.** No CI/cron schedule, no deployment, and no code writes to a shared DB or sends comms. This page documents an early-stage, repo-only exploration project for a possible future flash-flood AA framework, kept in the `pipelines/` shape per the ingestion task that produced this page. See `extra.reclassification_candidate`.

## One-liner
*manual, on-demand: pull CODAB admin boundaries + historical CERF flood allocations + EM-DAT flood events for 5 Sahel/Lake-Chad-basin countries (BFA, NER, TCD, NGA, CMR) → stage in dev blob → eyeball plots in jupytext notebooks, as due-diligence for a possible flash-flood AA framework.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| exploration notebooks (manual re-run) | `exploration/codab.md`, `exploration/cerf.md`, `exploration/emdat.md` (jupytext-paired `.md`/`.ipynb`) | on-demand, run by hand in a local Jupyter kernel | development |

No `.github/workflows/`, no `databricks.yml`/`.yaml`, and no CLI/`main.py` entrypoint exist in the repo — there is nothing for `infrastructure/pipeline-registry.md` to track, and indeed this repo does not appear there or in `infrastructure/deployments.md`.

## Inputs

- **CODAB admin boundaries** — fetched live per-country from FieldMaps (`data.fieldmaps.io/cod/originals/{iso3}.shp.zip`) for `bfa`, `ner`, `tcd`, `nga`, `cmr` (`src/constants.py: ISO3S`).
- **CERF allocations** — a manually downloaded `AllocationsByYear_2024-11-22.xlsx` extract, expected already present in blob (the loader does not fetch it; someone must upload it by hand first).
- **EM-DAT Africa floods** — a manually downloaded `emdat_africa_floods_accessed_2024-11-22.xlsx` extract, same manual-staging pattern.

Both spreadsheet inputs are single point-in-time snapshots from November 2024 and are not refreshed by any code in the repo.

## Steps

1. **`exploration/codab.md`** — for each of the 5 ISO3s, `codab.download_codab_to_blob()` fetches the FieldMaps shapefile zip and uploads it to dev blob (skips if already present, no `clobber` by default). `codab.load_all_codabs(admin_level, aoi_only=True)` then reloads and concatenates them; for Nigeria and Cameroon this restricts to an area-of-interest subset via `AOI_ADM1_PCODES` (Yobe/Borno/Adamawa for `nga`, Extrême-Nord for `cmr`) — i.e. the Lake Chad basin states, not the whole country. Ends with a quick `.plot()` of the AOI geometries.
2. **`exploration/cerf.md`** — `cerf.load_cerf()` reads the staged CERF extract, filters to the 5 target countries where `Emergency == "Flood"` and `Window == "Rapid Response"`, maps country names back to lower-case ISO3, and derives an `effective_year` (an allocation dated before May is attributed to the *previous* year, to align with typical rainy-season timing). Plots total CERF flood allocation by country/year as a grouped bar chart — a quick look at how often/how much flood CERF money has flowed to these countries historically.
3. **`exploration/emdat.md`** — loads the staged EM-DAT extract via `emdat.load_emdat()`. The notebook is otherwise an empty stub (one blank code cell) — no analysis has been written yet.

Full detail: `code_ref` above (`src/datasources/*.py`, `exploration/*.md`).

## Outputs

- Blob (`projects` container, `stage="dev"`): `ds-sahel-flashflooding/raw/codab/{iso3}.shp.zip` for `bfa`, `ner`, `tcd`, `nga`, `cmr` — written by `codab.download_codab_to_blob`.
- Blob: the manually-staged `raw/cerf/AllocationsByYear_<date>.xlsx` and `raw/emdat/emdat_africa_floods_accessed_<date>.xlsx` — read, not written, by this code.
- No Postgres writes (`db_utils.get_engine` exists but is never called), no email/Listmonk send, no dashboard. Analysis output is inline matplotlib plots inside the notebooks, not persisted anywhere.

## Dependencies

- **`azure-storage-blob`** used directly in `src/utils/blob_utils.py` (`ContainerClient.from_container_url` + a SAS token per stage) — this repo predates/bypasses `ocha-stratus`, which is the current team convention for blob & DB access (see `infrastructure/conventions.md`). Needs `PROD_BLOB_SAS` / `DEV_BLOB_SAS` env vars.
- **`sqlalchemy` + `psycopg2`**, via `src/utils/db_utils.py` (`get_engine("dev"|"prod")` against `chd-rasterstats-{dev,prod}.postgres.database.azure.com`) — defined but **unused**: no caller anywhere in `src/` or `exploration/`. Needs `AZURE_DB_PW_DEV` / `AZURE_DB_PW_PROD` if it were ever exercised.
- `geopandas`, `rioxarray`, `xarray`, `pandas`, `requests`, `pycountry`.
- `jupytext` (notebooks stored as paired `.md`/`.ipynb`) + `jupyter_black`, `ruff` (lint/format), `pre-commit`.

## Failure modes & debugging

Since nothing is scheduled, there is no "it broke overnight" scenario — the risks are staleness and bit-rot instead:

- **Stale manual extracts:** the CERF and EM-DAT inputs are frozen at 2024-11-22 and are not re-fetched by any code — anyone re-running these notebooks today is looking at >1-year-old allocation/event data unless they manually re-download and re-upload both spreadsheets first.
- **Missing SAS tokens:** every blob call goes through `blob_utils.get_container_client`, which reads `DEV_BLOB_SAS`/`PROD_BLOB_SAS` straight from the environment — if unset, every load/upload call fails with an auth error at the Azure SDK level (no friendly error message).
- **FieldMaps dependency:** `codab.download_codab_to_blob` hits `data.fieldmaps.io` live with `response.raise_for_status()` and no retry — if FieldMaps renames or moves a country's shapefile zip, the download hard-fails.
- **Dead DB code:** `db_utils.py` wires up a full `chd-rasterstats` Postgres engine that nothing calls — if someone later builds on this expecting it to be load-bearing, it isn't yet.
- **Branch/registry mismatch:** the active branch is `seasonal-forecasts`, but no seasonal-forecast-related code exists yet (see `extra.branch_name_mismatch`); the repo also does not appear in `infrastructure/pipeline-registry.md` or `infrastructure/deployments.md`, consistent with it never having been deployed as a live job.

## Downstream consumers

None yet. No AA framework for Sahel/Lake-Chad-basin flash flooding exists in this KB's `frameworks/` (the closest neighbours are the separate, endorsed `frameworks/bfa-flooding` framework — a different, Burkina-Faso-only fluvial-flood plan (PNAAI) whose primary trigger is an ECMWF SEAS5 seasonal-rainfall forecast, not a flash-flood trigger — and the drought-focused `analysis/sahel-drought` regional overview). This repo's CERF-history and hazard-extent scoping work is plausible groundwork for a future multi-country flash-flood framework covering BFA/NER/TCD plus the Nigeria/Cameroon Lake Chad basin states, but nothing currently consumes its output.
