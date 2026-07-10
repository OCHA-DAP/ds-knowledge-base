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
    - { name: "Run SEAS5", ref: "710204563973283", schedule: "19 30 12 5 * ?", status: live }
    - { name: "Run IMERG", ref: "666239885322861", schedule: "56 40 14 * * ?", status: live }
    - { name: "Run FloodScan", ref: "792911256578092", schedule: "36 0 20 * * ?", status: live }
inputs:
  - "blob: imb0chd0{dev|prod} raster container — seas5/monthly/processed/precip_em_i* (per-issued/leadtime COG)"
  - "blob: imb0chd0{dev|prod} raster container — era5/monthly/processed/precip_reanalysis_v* (monthly COG)"
  - "blob: imb0chd0{dev|prod} raster container — imerg/daily/late/v7/processed/imerg-daily-late-* (daily COG)"
  - "blob: imb0chd0{dev|prod} raster container — floodscan/daily/v5/processed/aer_area_300s_* (daily COG, SFED+MFED bands)"
  - "blob: imb0chd0{dev|prod} polygon container — {iso3}_shp.zip (COD admin boundaries)"
  - "DB table: public.iso3 (rasterstats DB — country list with max_adm_level, has_active_hrp, per-dataset coverage flags)"
  - "https://data.fieldmaps.io/cod.csv (COD metadata, only for --update-metadata)"
  - "local data/humanitarian-response-plans.csv + data/global-pcodes.csv (only for --update-metadata, downloaded manually from HDX + fieldmaps.io)"
outputs:
  - "DB table: public.seas5 (forecast zonal stats: mean/median/min/max/count/sum/std by iso3+pcode+valid_date+issued_date+leadtime+adm_level)"
  - "DB table: public.era5 (observational zonal stats by iso3+pcode+valid_date+adm_level)"
  - "DB table: public.imerg (observational zonal stats by iso3+pcode+valid_date+adm_level)"
  - "DB table: public.floodscan (observational zonal stats by iso3+pcode+valid_date+band[SFED|MFED]+adm_level)"
  - "DB table: public.qa (per-iso3/dataset/adm_level error log)"
  - "DB table: public.iso3 (country registry — rewritten only on --update-metadata)"
  - "DB table: public.polygon (per-pcode metadata: name, area, per-dataset pixel-coverage counts — written only on --update-metadata)"
dependencies:
  - "azure-storage-blob==12.20.0 (direct Azure SDK — NOT ocha-stratus; SAS tokens from env)"
  - "sqlalchemy==2.0.33 + psycopg2_binary==2.9.9 (direct DB connection; creds from env)"
  - "rioxarray==0.16.0, xarray==2024.3.0, dask==2024.7.0 (raster I/O + lazy COG stacking)"
  - "rasterio==1.3.10 (admin-boundary rasterization, resampling); geopandas==1.0.1 (vector boundaries)"
  - "requests (fieldmaps.io COD metadata, --update-metadata only)"
  - "secrets: DSCI_AZ_BLOB_{DEV|PROD}_SAS, DSCI_AZ_BLOB_{DEV|PROD}_SAS_WRITE, DSCI_AZ_DB_{DEV|PROD}_UID_WRITE, DSCI_AZ_DB_{DEV|PROD}_PW_WRITE"
downstream:
  - "raster-stats-app (ds-raster-stats-app) — Dash explorer reads public.era5/seas5/imerg + public.iso3/polygon from the prod rasterstats DB"
  - "Any framework monitoring app that reads ERA5/SEAS5/IMERG/FloodScan zonal stats from the rasterstats DB"
depends_on:
  - "raster-pipelines"
  - "dbx-job-compute"
source_repo: ocha-dap/ds-raster-stats
source_branch: main
source_sha: "5fe23b4"
code_ref:
  - "run_raster_stats.py — entrypoint (CLI dispatch, --update-metadata branch, multiprocessing.Pool over date chunks)"
  - "src/utils/inputs.py — CLI args (dataset, --mode, --test, --update-stats, --backfill, --update-metadata, --chunksize)"
  - "src/config/{seas5,era5,imerg,floodscan}.yml — per-dataset blob prefix, start_date, frequency, forecast flag, extra_dims, coverage"
  - "src/config/settings.py — DATABASES dict (local sqlite / dev / prod), config_pipeline(), date-chunk generation"
  - "src/utils/cloud_utils.py — get_container_client / get_cog_url (raw azure-storage-blob)"
  - "src/utils/cog_utils.py — stack_cogs: list blob, stream COGs via rioxarray, combine into xarray Dataset"
  - "src/utils/raster_utils.py — fast_zonal_stats(_runner), prep_raster (clip+upsample), rasterize_admin, validate_stats"
  - "src/utils/database_utils.py — table DDL + check constraints, postgres_upsert, qa logging"
  - "src/utils/iso3_utils.py — load public.iso3, load_shp_from_azure, create_iso3_df bootstrap"
  - "src/utils/metadata_utils.py — process_polygon_metadata (public.polygon build)"
  - "src/utils/general_utils.py — parse_date, get_missing_dates (backfill), get_most_recent_date (update-stats)"
extra:
  not_ocha_stratus: "Predates ocha-stratus adoption: uses raw azure-storage-blob (ContainerClient) for blob I/O and raw SQLAlchemy engine URLs for the DB. Does NOT use ocha-stratus. A future update should migrate."
  dedicated_db: "Has its own dedicated Azure PostgreSQL instances chd-rasterstats-{dev|prod}.postgres.database.azure.com — separate from the shared stratus DB. local mode uses a sqlite file (chd-rasterstats-local.db)."
  env_vars_changed: "settings.py + cloud_utils.py now read DSCI_AZ_BLOB_{DEV|PROD}_SAS (+ _SAS_WRITE) for blob and DSCI_AZ_DB_{DEV|PROD}_{UID|PW}_WRITE for the DB. The README still documents the OLD names (DSCI_AZ_SAS_DEV/PROD, AZURE_DB_PW_DEV/PROD) — README is stale; trust the code."
  run_modes: "Flag-driven, not date-config-driven: default = archival rebuild from config start_date to yesterday; --update-stats = stats against the single most-recent COG; --backfill = diff expected dates vs DB and fill gaps; --update-metadata = rebuild public.iso3 + public.polygon then exit; --test = 3-country subset (BDI/NGA/TCD)."
  metadata_bootstrap: "--update-metadata rebuilds public.iso3 (from fieldmaps.io cod.csv) and public.polygon. create_iso3_df ALSO requires local data/humanitarian-response-plans.csv (HDX) + data/global-pcodes.csv (fieldmaps.io) — so this is effectively a manual/local step, not a clean scheduled job."
  multiprocessing: "Dates are split into chunks of 100 (src/config/settings.py generate_date_series) and processed by a multiprocessing.Pool of NUM_PROCESSES=2 workers; each worker opens its own engine + stacks its own COGs."
  floodscan_bands: "FloodScan carries a 4th dim `band` mapped to SFED/MFED long-names in upsample_raster; written as the `band` column in public.floodscan."
  no_deploy_manifest: "This repo ships NO deployment config — no databricks.yml/DAB bundle and no scheduled GHA (the only workflow, .github/workflows/run_tests.yml, is push/PR CI on main). The scheduled jobs are registered directly in workspace adb-6009046713167663."
  SCHEMA_STRAIN: "No frontmatter field for dedicated-DB (vs shared stratus DB), for manual bootstrap steps, or for the job→repo attribution conflict — all captured in extra/discrepancies."
discrepancies:
  - "[conflict] infrastructure/pipeline-registry.md attributes the four scheduled Databricks jobs (954457722530604 ERA5, 710204563973283 SEAS5, 666239885322861 IMERG, 792911256578092 FloodScan) to repo OCHA-DAP/ds-raster-pipelines, and pipelines/raster-pipelines.md ALSO claims the same four job_ids as ITS COG-production jobs. Their registry `writes` column (public.era5/seas5/imerg/floodscan) is THIS repo's output tables, and this repo has no deployment manifest of its own — so the job→repo boundary is genuinely blurred. Listed here because these jobs are what produce this pipeline's tables on schedule, but the exact repo each Databricks task runs needs human confirmation in the workspace."
  - "[resolved] The previous version of this page (sha 0660cd9) warned the local checkout was 104 commits behind origin/main; the current checkout IS main @ 5fe23b4, so that gap is closed."
  - "[resolved] The previous page flagged hardcoded end_date: 2024-10-30 in the configs. The configs now set end_date: Null, so the default run goes from start_date to yesterday (date.today() - 1 day) — no longer stale, but a long-gap archival rebuild reprocesses the full history."
  - "[stale] README documents the pre-rename env vars (DSCI_AZ_SAS_DEV/PROD, AZURE_DB_PW_DEV/PROD) and a `floodscan` positional that exists in inputs.py but does not list --update-metadata under its own section cleanly. Code (settings.py/cloud_utils.py/inputs.py) is authoritative."
  - "[gap] Per-iso3 errors are caught and logged to public.qa; the run still exits 0, so missing-country stats are invisible unless you query public.qa. SEAS5/FloodScan all-NaN leadtime/band+date combos are silently skipped with NO qa entry."
visibility: internal
last_synced: "2026-06-29"
---

# Raster Statistics Pipeline

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On schedule: read COG rasters (SEAS5 / ERA5 / IMERG / FloodScan) from Azure blob → clip to country bounds → upsample → compute zonal stats per p-code per admin level → upsert into the dedicated Azure PostgreSQL "rasterstats" DB.*

## Jobs & schedule

Four scheduled Databricks jobs, one per dataset, in workspace `adb-6009046713167663`:

| job | ref | schedule | status |
|---|---|---|---|
| Run ERA5 | `954457722530604` | `0 0 12 6 * ?` (6th of month, 12:00 UTC) | live |
| Run SEAS5 | `710204563973283` | `19 30 12 5 * ?` (5th of month, 12:30 UTC) | live |
| Run IMERG | `666239885322861` | `56 40 14 * * ?` (daily, 14:40 UTC) | live |
| Run FloodScan | `792911256578092` | `36 0 20 * * ?` (daily, 20:00 UTC) | live |

> **Attribution conflict — read before debugging.** This repo contains **no deployment manifest**: no `databricks.yml`/DAB bundle and no scheduled GitHub Action (the only workflow, `run_tests.yml`, is push/PR CI). The four job_ids above are what write this pipeline's output tables on schedule, but [`infrastructure/pipeline-registry.md`](../infrastructure/pipeline-registry.md) attributes those same ids to **`ds-raster-pipelines`** (the COG *producer*), and [`pipelines/raster-pipelines.md`](raster-pipelines.md) claims them too. The COG-production and zonal-stats steps appear to share Databricks jobs — confirm which task runs which repo in the workspace before assuming a failure is "this" pipeline.

This checkout is `main` @ `5fe23b4` and matches what the workspace runs (no longer the 104-commits-behind gap the prior page warned about).

## Inputs

**Raster COGs** (Azure Blob `raster` container, `imb0chd0{dev|prod}`), prefix per `src/config/{dataset}.yml`:

- `seas5/monthly/processed/precip_em_i*` — SEAS5 monthly precip ensemble mean (forecast; per issued-date + leadtime)
- `era5/monthly/processed/precip_reanalysis_v*` — ERA5 monthly precip reanalysis
- `imerg/daily/late/v7/processed/imerg-daily-late-*` — IMERG daily late-run precip
- `floodscan/daily/v5/processed/aer_area_300s_*` — FloodScan daily flood fraction (SFED + MFED bands)

**Boundaries:** `{iso3}_shp.zip` per country in the `polygon` blob container (COD admin shapefiles).

**Database:** `public.iso3` in the rasterstats DB — `iso3`, `has_active_hrp`, `max_adm_level`, `stats_last_updated`, `shp_url`, and per-dataset coverage flags (e.g. `floodscan`).

The `--update-metadata` path additionally pulls `https://data.fieldmaps.io/cod.csv` and reads local `data/humanitarian-response-plans.csv` + `data/global-pcodes.csv`.

## Steps

1. **Parse CLI** (`src/utils/inputs.py`) — positional dataset (`seas5|era5|imerg|floodscan`), `--mode {local,dev,prod}`, `--test`, `--update-stats`, `--backfill`, `--update-metadata`, `--chunksize`.
2. **`--update-metadata` short-circuit** — rebuild `public.iso3` (`create_iso3_df`) and `public.polygon` (`process_polygon_metadata`), then `sys.exit(0)`. (Needs local CSVs — effectively manual.)
3. **Create tables** — `create_qa_table` + `create_dataset_table` (idempotent `MetaData.create_all`; forecast datasets get `issued_date`/`leadtime`, extra_dims add columns; check constraints enforce min≤max, mean/median∈[min,max], leadtime∈0..6, etc.).
4. **Resolve dates** (`config_pipeline`) — default = config `start_date` → yesterday; `--update-stats` = single most-recent COG date; `--backfill` = expected-vs-existing date diff (`get_missing_dates`). Dates are chunked (100/chunk).
5. **Load country list** — `get_iso3_data` queries `public.iso3` (or the `--test` 3-country subset).
6. **Process chunks in parallel** (`multiprocessing.Pool`, 2 workers; `process_chunk`):
   a. `stack_cogs` — list blob by prefix, stream matching COGs via `rioxarray`, combine into one `xarray.Dataset` (`date` dim, plus `leadtime`/`band` where applicable).
   b. Per country: download boundary zip, read ADM0, `prep_raster` (clip to bounds + upsample to 0.05°).
   c. Per admin level `0..max_adm_level`: `fast_zonal_stats_runner` (rasterize boundaries, compute mean/median/min/max/sum/std/count per p-code per date; `validate_stats` each row).
   d. **Upsert** all rows for the country via `postgres_upsert` (on-conflict update on the `(valid_date, pcode[, leadtime/band])` unique key).
   e. Any per-iso3 exception → `insert_qa_table` and continue.

See `run_raster_stats.py` + `src/utils/` for detail.

## Methodology rationale

Why the pipeline computes stats the way it does (2024 design work):

- **Boundary pixels: whole-pixel vs pixel-weighting.** Two standard ways to treat pixels straddling polygon boundaries: *whole-pixel* methods (à la `rasterstats` — include a pixel by centroid-in-polygon or any-touch, optionally upsampling first to shrink the weight of boundary pixels) vs *pixel-weighting* methods (à la `exactextract` — weight each boundary pixel by its area fraction inside the polygon). Discrepancy is largest for small, coastline-heavy geographies.
- **Choice: whole-pixel with upsampling.** All input rasters are upscaled to **0.05°** with `nearest` resampling — `nearest` preserves original cell values, and the upsampling acts as a simplified area-weighting proxy. Per-dataset upscales: SEAS5 0.4°→0.05°, ERA5 0.25°→0.05°, IMERG 0.1°→0.05°.
- **exactextract was evaluated and rejected** for this general pipeline — much slower for repeated calculations across many dates, and output very similar — though it *is* used in the storms exposure path. Validation on the Philippines ADM2 stress case (small country, lots of coastline): the majority of ADM2 means agree within ±5% between the two methods; only a minority exceed ±10%. A higher upsample resolution shrinks the gap further but costs memory/performance.
- **Simplify then rasterize once.** Input polygons are simplified with a conservative 0.001° tolerance before rasterizing (big speedup, no material boundary change). Boundaries are rasterized **once per admin level** (pixels whose centroid falls inside the polygon) and cached across all dates — the major speedup vs baseline `rasterstats`, which re-rasterizes per date; valid because admin polygons don't overlap. Smaller geometries get less accurate stats at the reference resolution.
- **Scoping choices** (2024): stats are min/max/mean/median/sum; any quantiles would be in tens only (10/20/30…) — no team framework uses a non-multiple-of-10 threshold (quantiles are not in the current output schema). Output format was scoped as one big parquet internally + CSVs for HDX/ad-hoc country sends; the implementation landed on the Postgres tables below.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Admin boundary reference & quirks

- **Source & cache.** All admin boundaries are the **Fieldmaps.io original-shapefile CODs** (fieldmaps.io/data/cod), cached in the prod `polygon` blob container to pin versions and avoid hammering the Fieldmaps server. The cache is refreshed **manually** — no automation; last prod refresh from Fieldmaps was **2024-10-07** (as of the source doc). <!-- TODO: check whether the polygon cache has been refreshed since 2024-10-07 -->
- **Coverage.** ADM0/1 for all COD countries; ADM2 only for HRP countries. Encoded in `public.iso3`: `max_adm_level = 2` where `has_active_hrp` (pulled from the HDX humanitarian-response-plans dataset, where the source CODs allow), else 1; `src_lvl`/`src_update`/`o_shp` are copied from the Fieldmaps COD metadata CSV (`data.fieldmaps.io/cod.csv`).
- **Quirk: tiny countries have no data** — their extent is smaller than the raw raster pixels, so clipping fails: DMA, LCA, SXM, MSR.
- **Quirk: multiple ADM0 entries** — BDI, NGA, TCD (also the `--test` 3-country subset).
- **Quirk: extraneous / non-standard pcodes** in the CODs — CHN, LBN, MOZ, PAK, SDN, SSD (e.g. Lebanon has an ADM1 named "Conflict").
- **`public.polygon` semantics** (for interpreting the coverage columns): `area` is km² computed on the Mollweide equal-area projection; `{dataset}_frac_raw_pixels` = n_upsampled_pixels / upsample_factor² (polygon size relative to raw pixel size); `{dataset}_n_intersect_raw_pixels` excludes pixels with very small overlap.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Outputs

**Dedicated Azure PostgreSQL** `chd-rasterstats-{dev|prod}.postgres.database.azure.com` (local mode → `chd-rasterstats-local.db` sqlite):

- `public.seas5` — `iso3, pcode, valid_date, issued_date, leadtime, adm_level, mean, median, min, max, count, sum, std`. Unique on `(valid_date, pcode, leadtime)` (nulls-not-distinct).
- `public.era5` / `public.imerg` — observational schema (no `issued_date`/`leadtime`). Unique on `(valid_date, pcode)`.
- `public.floodscan` — observational schema + `band` (SFED/MFED). Unique on `(valid_date, pcode, band)`.
- `public.qa` — error log: `date, iso3, adm_level, dataset, error, stack_trace`.
- `public.iso3` — country registry (rewritten only on `--update-metadata`).
- `public.polygon` — per-pcode metadata: `name, area, standard`, per-dataset pixel-coverage counts (built only on `--update-metadata`).

No blob outputs. No email outputs.

## Dependencies

| Dependency | Notes |
|---|---|
| `azure-storage-blob==12.20.0` | Direct Azure SDK — **not** ocha-stratus; SAS from env |
| `sqlalchemy==2.0.33` + `psycopg2_binary==2.9.9` | Direct DB engine; creds from env |
| `rioxarray==0.16.0`, `xarray==2024.3.0`, `dask==2024.7.0` | Raster I/O + lazy COG stacking |
| `rasterio==1.3.10`, `geopandas==1.0.1` | Admin rasterization / vector boundaries |
| `requests` | fieldmaps.io COD metadata (`--update-metadata` only) |

**Secrets / env** (NOTE: renamed vs README): blob = `DSCI_AZ_BLOB_{DEV|PROD}_SAS` and `DSCI_AZ_BLOB_{DEV|PROD}_SAS_WRITE`; DB = `DSCI_AZ_DB_{DEV|PROD}_UID_WRITE` and `DSCI_AZ_DB_{DEV|PROD}_PW_WRITE`. `PGSSLMODE=require` may be needed for Azure PostgreSQL — see [infrastructure/conventions.md](../infrastructure/conventions.md).

## Failure modes & debugging

**`No COGs found to process for dates: ...`** — blob listing returned nothing for the resolved date range. Check: (a) the `blob_prefix` in `src/config/{dataset}.yml` still matches blob layout; (b) the upstream [raster-pipelines](raster-pipelines.md) COG producer actually ran (a missed COG run starves this job); (c) the SAS token (`DSCI_AZ_BLOB_*_SAS*`) hasn't expired. `stack_cogs` also logs a warning when `len(cogs) != len(dates)` but proceeds.

**Per-country errors silently swallowed** — `process_chunk` catches per-iso3 exceptions, logs to `public.qa`, and continues; the run still exits `0`. If a country's stats are missing, `SELECT * FROM public.qa WHERE iso3 = 'XYZ'`.

**All-NaN combos skipped with no trace** — in `fast_zonal_stats_runner`, a leadtime/band+date slice that is entirely NaN is `continue`-skipped with **no qa entry** (expected for invalid SEAS5 forecast combos / FloodScan band gaps).

**Admin boundary not in blob** — `load_shp_from_azure` raises if `{iso3}_shp.zip` is absent in the `polygon` container; caught → qa. Fix: upload the zip or drop the iso3 from `public.iso3`.

**Constraint violations on upsert** — `create_dataset_table` adds check constraints (min≤max, mean/median∈[min,max], `leadtime BETWEEN 0 AND 6`, `valid_date >= issued_date`, etc.) and `validate_stats` re-checks in Python; a genuine bad stat row will raise and land in qa.

**DB / env issues** — verify the renamed env vars (`DSCI_AZ_DB_*_{UID|PW}_WRITE`) are set on the cluster; the README's old names will silently yield `None` creds. Set `PGSSLMODE=require` if the connection is refused.

**`--update-metadata` fails locally** — `create_iso3_df` reads `data/humanitarian-response-plans.csv` and `data/global-pcodes.csv` from the working dir; without them it errors. This step is effectively manual/local.

**Databricks logs** — workspace `adb-6009046713167663`; check job run logs in the UI (but see the attribution conflict above — the failing task may belong to `ds-raster-pipelines`).

## Downstream consumers

- **raster-stats-app** — the Dash explorer (`ds-raster-stats-app`) reads `public.era5/seas5/imerg` plus `public.iso3`/`public.polygon` (and `*_completeness`) from the prod rasterstats DB. See [apps/raster-stats-app](../apps/raster-stats-app.md).
- **Framework monitoring apps** — any AA framework monitor that reads ERA5/SEAS5/IMERG/FloodScan zonal stats from the rasterstats DB consumes this output.

> **Not a consumer:** `ds-floodexposure-monitoring` has its *own* internal raster-stats step (`pipelines/update_raster_stats.py` → `app.floodscan_exposure`) and a self-contained `repository_dispatch` chain. It does **not** read from this pipeline. See [pipelines/floodexposure-monitoring](floodexposure-monitoring.md).
