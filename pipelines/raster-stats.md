---
content_type: pipeline
name: raster-stats
type: dataset-ingest
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Run ERA5", ref: "954457722530604", schedule: "0 0 12 6 * ?", status: live }
    - { name: "Run IMERG", ref: "666239885322861", schedule: "56 40 14 * * ?", status: live }
    - { name: "Run SEAS5", ref: "710204563973283", schedule: "19 30 12 5 * ?", status: live }
inputs:
  - "blob: imb0chd0{dev|prod} raster container — seas5/monthly/processed/precip_em_i* (COG)"
  - "blob: imb0chd0{dev|prod} raster container — era5/monthly/processed/precip_reanalysis_v* (COG)"
  - "blob: imb0chd0{dev|prod} raster container — imerg/daily/late/v7/processed/imerg-daily-late-* (COG)"
  - "blob: imb0chd0{dev|prod} polygon container — {iso3}_shp.zip (COD boundaries)"
  - "DB table: public.iso3 (country list with max_adm_level, has_active_hrp)"
outputs:
  - "DB table: public.seas5 (zonal stats: mean/median/min/max/count/sum/std by iso3+pcode+valid_date+issued_date+leadtime+adm_level)"
  - "DB table: public.era5 (zonal stats: mean/median/min/max/count/sum/std by iso3+pcode+valid_date+adm_level)"
  - "DB table: public.imerg (zonal stats: mean/median/min/max/count/sum/std by iso3+pcode+valid_date+adm_level)"
  - "DB table: public.qa (error log per iso3/dataset/adm_level run)"
dependencies:
  - "azure-storage-blob (direct Azure SDK — NOT ocha-stratus; uses DSCI_AZ_SAS_DEV/PROD env vars)"
  - "sqlalchemy 2.0 + psycopg2 (direct DB connection via AZURE_DB_PW_DEV/PROD)"
  - "rioxarray, xarray, dask (raster I/O and COG stacking)"
  - "rasterio (rasterize admin boundaries, resampling)"
  - "geopandas (vector boundaries)"
  - "fieldmaps.io cod.csv (metadata for iso3 table bootstrap — manual step)"
  - "secrets: DSCI_AZ_SAS_DEV, DSCI_AZ_SAS_PROD, AZURE_DB_PW_DEV, AZURE_DB_PW_PROD"
downstream:
  - "apps/seas5-skill — reads public.seas5 AND public.era5 from prod rasterstats DB (via pipeline/compute_skill.py)"
  - "Any framework monitoring app that reads ERA5/SEAS5/IMERG zonal stats from the rasterstats DB"
depends_on:
  - "raster-pipelines"
source_repo: ocha-dap/ds-raster-stats
source_branch: main
source_sha: "0660cd9"
code_ref:
  - "run_raster_stats.py — entrypoint (CLI, orchestration, multiprocessing)"
  - "src/config/{seas5,era5,imerg}.yml — per-dataset blob prefix + date range config"
  - "src/config/settings.py — DB connection strings (dev/prod)"
  - "src/utils/cog_utils.py — blob listing, COG stacking into xarray Dataset"
  - "src/utils/raster_utils.py — zonal stats core (fast_zonal_stats, prep_raster, upsample)"
  - "src/utils/database_utils.py — table DDL, upsert, QA logging"
  - "src/utils/iso3_utils.py — loads public.iso3; bootstrap via fieldmaps.io (manual)"
extra:
  note_on_stratus: "This repo predates ocha-stratus adoption and uses raw Azure SDK calls (azure-storage-blob) plus raw SQLAlchemy engine URLs — it does NOT use ocha-stratus. A future update should migrate to stratus conventions."
  dedicated_db: "Has its own dedicated Azure PostgreSQL instances: chd-rasterstats-dev.postgres.database.azure.com and chd-rasterstats-prod.postgres.database.azure.com — separate from the shared stratus DB."
  iso3_table_bootstrap: "The public.iso3 table must be seeded manually with --build-iso3 flag using local CSV downloads from HDX (humanitarian-response-plans.csv) and fieldmaps.io (global-pcodes.csv). This is a one-time/periodic manual step, not automated."
  multiprocessing: "For date ranges > 1 year the pipeline splits into yearly chunks and runs 2 parallel processes via multiprocessing.Pool."
  SCHEMA_STRAIN: "No field for dedicated-DB (vs shared stratus DB) — captured in extra. No field for manual bootstrap steps."
discrepancies:
  - "[conflict] Page/source_sha reflects local checkout 0660cd9, but that is local `main` 104 commits BEHIND origin/main (5fe23b4). The deployed Databricks jobs run from origin/main, so the live code is 5fe23b4, NOT the 0660cd9 this page summarizes. Re-sync the local checkout (git pull) before trusting code_ref line detail."
  - "[conflict] An earlier draft of this page listed ds-floodexposure-monitoring as a downstream consumer ('triggered post-run for quantiles'). This is FALSE: floodexposure-monitoring computes its OWN raster stats internally (pipelines/update_raster_stats.py → app.floodscan_exposure) and its repository_dispatch chain is self-contained. It does NOT trigger or read from this ds-raster-stats pipeline. Removed from downstream."
  - "[stale] Dataset configs hardcode end_date: 2024-10-30 (src/config/*.yml). A catch-up run after a long gap reprocesses from start_date (1981/2000); configs need periodic bumping."
  - "[gap] Per-iso3 errors are caught and logged to public.qa, and the run still exits 0 — missing-country stats are invisible unless you query public.qa. SEAS5 all-NaN leadtime/date combos are skipped with NO qa entry."
visibility: internal
last_synced: "2026-06-22"
---

# Raster Statistics Pipeline

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On schedule: read COG rasters (SEAS5/ERA5/IMERG) from Azure blob → clip to country bounds → compute zonal stats per p-code per admin level → upsert into dedicated Azure PostgreSQL DB.*

## Jobs & schedule

Three separate Databricks jobs, one per dataset:

| job | ref | schedule | status |
|---|---|---|---|
| Run ERA5 | `954457722530604` | `0 0 12 6 * ?` (6th of month at 12:00 UTC) | live |
| Run IMERG | `666239885322861` | `56 40 14 * * ?` (daily at 14:40:56 UTC) | live |
| Run SEAS5 | `710204563973283` | `19 30 12 5 * ?` (5th of month at 12:30 UTC) | live |

There is no Databricks Asset Bundle (no `databricks.yml`) in this repo — the jobs are registered directly in the workspace (`adb-6009046713167663`). No GHA schedule workflow exists (the only GHA workflow, `run_tests.yml`, is CI only).

> **Deployed code ≠ this checkout.** The jobs run from `origin/main` (`5fe23b4`). This page's `source_sha` is `0660cd9`, the local `main` which is **104 commits behind** `origin/main`. `git pull` before relying on the `code_ref` line-level detail below.

## Inputs

**Raster COGs (Azure Blob Storage):**

- `seas5/monthly/processed/precip_em_i*` — SEAS5 monthly precip ensemble mean (blob: `raster` container)
- `era5/monthly/processed/precip_reanalysis_v*` — ERA5 monthly precip reanalysis (blob: `raster` container)
- `imerg/daily/late/v7/processed/imerg-daily-late-*` — IMERG daily late-run precipitation (blob: `raster` container)
- `{iso3}_shp.zip` — COD boundary shapefiles (blob: `polygon` container), one per country

**Database:**

- `public.iso3` (rasterstats DB) — country registry: iso3 code, `has_active_hrp`, `max_adm_level`

## Steps

1. **Parse CLI args** — dataset (`seas5`|`era5`|`imerg`), mode (`dev`|`prod`), optional `--test` / `--build-iso3`.
2. **Create tables** — DDL for the dataset table and `qa` error table (idempotent via SQLAlchemy `create_all`).
3. **Load country list** — query `public.iso3` for countries to process (or a subset if `--test`).
4. **Split date range** — if the configured date range exceeds 1 year, split into yearly chunks.
5. **For each date chunk (parallel if >1):**
   a. `stack_cogs` — list blob container for matching COG files, stream each via `rioxarray`, stack into a single `xarray.Dataset` with a `date` dimension (plus `leadtime` for SEAS5).
   b. For each country: download boundary zip from blob, load ADM0 shapefile, clip+upsample raster to country bounds (`prep_raster`).
   c. For each admin level (0 to `max_adm_level`): load admin shapefile, rasterize boundaries, compute `fast_zonal_stats` (mean/median/min/max/sum/std/count per p-code per date).
   d. **Upsert** all results for the country into the dataset table; on conflict update by `(valid_date, pcode [, leadtime])`.
   e. Log any per-iso3 errors to `public.qa` and continue.
6. Done.

See `run_raster_stats.py` and `src/utils/` for full detail.

## Outputs

**Dedicated Azure PostgreSQL** (`chd-rasterstats-{dev|prod}.postgres.database.azure.com`):

- `public.seas5` — columns: `iso3`, `pcode`, `valid_date`, `issued_date`, `leadtime`, `adm_level`, `mean`, `median`, `min`, `max`, `count`, `sum`, `std`. Unique on `(valid_date, pcode, leadtime)`.
- `public.era5` — same schema minus `issued_date`/`leadtime`. Unique on `(valid_date, pcode)`.
- `public.imerg` — same schema as era5. Unique on `(valid_date, pcode)`.
- `public.qa` — error log: `date`, `iso3`, `adm_level`, `dataset`, `error`, `stack_trace`.
- `public.iso3` — country registry (written only during manual `--build-iso3` bootstrap).

No blob outputs. No email outputs.

## Dependencies

| Dependency | Notes |
|---|---|
| `azure-storage-blob==12.20.0` | Direct Azure SDK — **not** ocha-stratus; SAS tokens from env vars |
| `sqlalchemy==2.0.33` + `psycopg2_binary` | Direct DB; password from `AZURE_DB_PW_{DEV\|PROD}` env vars |
| `rioxarray==0.16.0`, `xarray==2024.3.0`, `dask==2024.7.0` | Raster I/O and lazy COG stacking |
| `rasterio==1.3.10` | Admin boundary rasterization, resampling |
| `geopandas==1.0.1` | Boundary shapefile loading |
| `DSCI_AZ_SAS_DEV` / `DSCI_AZ_SAS_PROD` | SAS tokens for blob access |
| `AZURE_DB_PW_DEV` / `AZURE_DB_PW_PROD` | DB passwords |

Note: `PGSSLMODE=require` may need to be set for Azure PostgreSQL connections depending on environment — see `infrastructure/conventions.md`.

## Failure modes & debugging

**"No COGs found to process"** — blob listing returned empty. Check: (a) the blob prefix in `src/config/{dataset}.yml` matches the actual blob paths; (b) the date range in the config hasn't gone stale (configs were last set to end `2024-10-30`); (c) the SAS token hasn't expired.

**Per-country errors silently swallowed** — the pipeline catches per-iso3 exceptions and logs to `public.qa` then continues. If stats appear missing for a specific country, query `SELECT * FROM public.qa WHERE iso3 = 'XYZ'` to see the error. The pipeline still exits `0`.

**SEAS5 leadtime/date combos skipped** — when `np.all(np.isnan(ds__.values))` for a leadtime/date, that combo is silently skipped (no QA entry). This is expected for invalid forecast combinations.

**Admin boundary not found in blob** — `load_shp_from_azure` will raise if `{iso3}_shp.zip` doesn't exist in the `polygon` container. Fix: upload the boundary zip, or exclude the iso3 from `public.iso3`.

**Stale date range in config** — the configs have hardcoded `end_date: 2024-10-30`. A catch-up run after a long gap will try to process from `start_date` (1981/2000) and may attempt already-existing rows — the upsert handles this, but the run will be slow. The configs should be updated periodically.

**DB connection failures** — check `AZURE_DB_PW_{DEV|PROD}` env vars are set on the Databricks cluster. Also check `PGSSLMODE=require` if the connection is refused.

**Databricks logs** — the three jobs are registered in workspace `adb-6009046713167663`. Check job run logs via the Databricks UI or `databricks runs list --job-id <id>`.

## Downstream consumers

- **seas5-skill** — the SEAS5 skill app reads both `public.seas5` and `public.era5` from the prod rasterstats DB (via `pipeline/compute_skill.py`) to compute skill-adjusted drought probabilities. See [apps/seas5-skill](../apps/seas5-skill.md).
- **Framework monitoring apps** — any AA framework monitor that reads ERA5/SEAS5/IMERG zonal stats from the rasterstats DB consumes this pipeline's output.

> **Not a consumer:** `ds-floodexposure-monitoring` has its *own* internal "raster stats" step (`pipelines/update_raster_stats.py` → `app.floodscan_exposure`) and a self-contained `repository_dispatch` chain. It does **not** trigger or read from this `ds-raster-stats` pipeline. See [pipelines/floodexposure-monitoring](../pipelines/floodexposure-monitoring.md) for that separate system.
