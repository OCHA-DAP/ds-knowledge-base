---
content_type: pipeline
name: raster-pipelines
type: dataset-ingest
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Run ERA5",      ref: "954457722530604",  schedule: "0 0 12 6 * ?",        status: live }
    - { name: "Run SEAS5",     ref: "710204563973283",  schedule: "19 30 12 5 * ?",       status: live }
    - { name: "Run IMERG",     ref: "666239885322861",  schedule: "56 40 14 * * ?",       status: live }
    - { name: "Run FloodScan", ref: "792911256578092",  schedule: "36 0 20 * * ?",        status: live }
inputs:
  - "ECMWF CDS API (ERA5 monthly total precipitation; reanalysis-era5-single-levels-monthly-means via cdsapi)"
  - "ECMWF MARS API (SEAS5 seasonal forecasts pre-2024; tprate, 0.4 deg global)"
  - "Private ECMWF AWS S3 bucket (SEAS5 >=2024 GRIB files; s3://AWS_BUCKET_NAME/ecmwf/)"
  - "NASA GES DISC HTTPS (IMERG daily v7 late/early run NC4; gpm1.gesdisc.eosdis.nasa.gov)"
  - "AER FloodScan HTTP endpoints (daily 90-day rolling SFED+MFED ZIPs for Africa, Asia-Australia, N/S America)"
  - "Azure blob raster container — historical FloodScan NetCDF archive (pre-2024 data already on blob)"
outputs:
  - "blob:raster/era5/monthly/raw/  — raw GRIB files (tp_reanalysis_monthly_YYYY_MM.grib)"
  - "blob:raster/era5/monthly/processed/  — monthly COG GeoTIFFs (precip_reanalysis_vYYYY-MM-DD.tif)"
  - "blob:raster/seas5/monthly/raw/  — raw GRIB files (tprate_YYYY.grib or T8L... filenames for >=2024)"
  - "blob:raster/seas5/monthly/processed/  — per-issued/leadtime COG GeoTIFFs (precip_em_iYYYY-MM-DD_ltN.tif)"
  - "blob:raster/floodscan/daily/v5/raw/  — raw ZIPs and historical NC4 files"
  - "blob:raster/floodscan/daily/v5/processed/  — daily COG GeoTIFFs per region + global merged (aer_area_300s_vDATE_v05r01.tif)"
  - "blob:raster/imerg/daily/{late|early}/v7/raw/  — raw NC4 files"
  - "blob:raster/imerg/daily/{late|early}/v7/processed/  — daily COG GeoTIFFs (imerg-daily-{run}-YYYY-MM-DD.tif)"
dependencies:
  - azure-storage-blob==12.20.0
  - xarray==2024.3.0
  - rioxarray==0.16.0
  - cfgrib==0.9.13.0
  - cdsapi==0.7.7
  - ecmwf-api-client==1.6.3
  - fsspec==2024.6.1
  - s3fs==2024.6.1
  - dask==2024.7.0
  - rasterio==1.4.1
  - "env: DSCI_AZ_BLOB_DEV_SAS_WRITE, DSCI_AZ_BLOB_PROD_SAS_WRITE, STORAGE_ACCOUNT_DEV, STORAGE_ACCOUNT_PROD"
  - "env: ECMWF_API_URL, ECMWF_API_EMAIL, ECMWF_API_KEY (MARS)"
  - "env: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME, AWS_DEFAULT_REGION (SEAS5 >=2024)"
  - "env: CDSAPI_URL, CDSAPI_KEY (ERA5)"
  - "env: IMERG_USERNAME, IMERG_PASSWORD (NASA Earthdata)"
  - "env: FLOODSCAN_SFED_URL_AF/SA/NA/AA, FLOODSCAN_MFED_URL_AF/SA/NA/AA"
  - "env: CONTAINER_RASTER (= 'raster')"
downstream:
  - "ds-seas5-skill (reads SEAS5 COGs from blob)"
  - "ds-seas5-viz (reads SEAS5 COGs from blob)"
  - "ds-floodexposure-monitoring (reads FloodScan COGs from blob to compute ADM exposure)"
  - "ds-imerg (separate GHA-driven IMERG pipeline also reads/writes same blob paths)"
  - "any AA framework pipeline that computes raster stats from blob (ERA5, SEAS5, IMERG, FloodScan)"
depends_on:
  - "infrastructure/storage"
source_repo: ocha-dap/ds-raster-pipelines
source_branch: HDXPIPE-102_floodscan-extended-historical
source_sha: "4178527"
code_ref:
  - "run_pipeline.py — CLI entrypoint dispatching to era5/seas5/imerg/floodscan"
  - "src/pipelines/pipeline.py — abstract base: blob upload/download, coverage check, backfill"
  - "src/pipelines/era5_pipeline.py — ERA5 query → GRIB → monthly COG"
  - "src/pipelines/seas5_pipeline.py — SEAS5 MARS/AWS query → GRIB → per-leadtime COG"
  - "src/pipelines/imerg_pipeline.py — NASA HTTPS download → NC4 → daily COG"
  - "src/pipelines/floodscan_pipeline.py — AER API / NC4 archive → daily COG; global merge; baseline calc"
  - "src/config/{era5,seas5,imerg,floodscan}_config.yml — blob paths, coverage dates, metadata"
  - "src/utils/validation_utils.py — pre-upload COG validation (CRS, dtype, attrs, leadtime)"
extra:
  floodscan_global_merge: "On daily update, four regional COGs (Africa, Asia-Australia, N/S America) are separately downloaded then merged into a single global COG saved under processed/global/"
  floodscan_baseline: "Separate --baseline-update mode computes 10-year rolling mean (11-day centred) by day-of-year and saves as NC4 to raw; used by floodexposure-monitoring for anomaly detection"
  seas5_dual_source: "Pre-2024 data fetched from ECMWF MARS API (25 or 51 ensemble members depending on year); 2024+ fetched from private ECMWF AWS S3 bucket (different GRIB structure, different filename convention)"
  imerg_version_letter: "IMERG v7 uses suffix 'B' before 2026-03-03, 'C' from that date onwards — hardcoded in imerg_pipeline.py:52"
  no_db_writes: "This repo writes COG rasters to blob only — no DB tables are written. Raster-stats computation is downstream (floodexposure-monitoring and per-framework pipelines)."
discrepancies:
  - "[gap] deployments.md lists Run ERA5/SEAS5/IMERG/FloodScan Databricks job IDs with source/repo as '—'; attribution to THIS repo is inferred from job names, not confirmed via Databricks git_source config. The deployed job may run a different branch than the checked-out HDXPIPE-102 feature branch."
  - "[conflict] Page reflects the feature branch HDXPIPE-102_floodscan-extended-historical (source_sha 4178527), NOT main. The FloodScan extended-historical archive filenames in floodscan_config.yml (…20260331…_no_ndt.nc for AA/NA/SA) only exist on this branch; main is behind. What the Databricks Run FloodScan job actually runs is unconfirmed (see gap above)."
  - "[stale] ds-imerg (separate repo) runs a parallel GHA ingest (run_download_imerg.yml) writing the SAME imerg/daily blob paths as the Databricks Run IMERG job here — two independent ingests to one path, not sequential; risk of clobber/duplication is unmanaged."
visibility: internal
last_synced: "2026-06-22"
---

# raster-pipelines

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Four Databricks jobs (daily/monthly): pull ERA5, SEAS5, IMERG, and FloodScan from external APIs, convert to Cloud-Optimized GeoTIFFs (COGs), and write to the Azure `raster` blob container — the shared raster store consumed by all downstream AA framework pipelines and apps.

## Jobs & schedule

All four pipelines run as Databricks jobs in the `adb-6009046713167663` workspace. Schedules are Quartz cron strings.

| job | ref (job_id) | schedule | status |
|---|---|---|---|
| Run ERA5 | 954457722530604 | `0 0 12 6 * ?` (6th of month at 12:00 UTC) | live / UNPAUSED |
| Run SEAS5 | 710204563973283 | `19 30 12 5 * ?` (5th of month at 12:30 UTC) | live / UNPAUSED |
| Run IMERG | 666239885322861 | `56 40 14 * * ?` (daily at 14:40 UTC) | live / UNPAUSED |
| Run FloodScan | 792911256578092 | `36 0 20 * * ?` (daily at 20:00 UTC) | live / UNPAUSED |

Note: `ds-imerg` also has a separate GHA-triggered ingest that shares the same blob paths (see downstream). The GHA `run_tests.yml` is CI-only (push/PR to `main`), not a scheduled pipeline.

## Inputs

| pipeline | source | detail |
|---|---|---|
| ERA5 | ECMWF CDS API | Monthly total precipitation, 0.25° global, from 1981-01-01. `cdsapi` library, `CDSAPI_URL`/`CDSAPI_KEY`. |
| SEAS5 | ECMWF MARS API (pre-2024) | All months in a year, 0.4° global, 1981–2023. 25 ensemble members ≤2016, 51 thereafter. Env: `ECMWF_API_*`. |
| SEAS5 | Private ECMWF AWS S3 (2024+) | Per (issued_month, fc_month) GRIB files from `s3://AWS_BUCKET_NAME/ecmwf/`. Env: `AWS_*`. |
| IMERG | NASA GES DISC HTTPS | Daily v7 (late run default), 0.1° global, coverage from 1998-01-01 (`imerg_config.yml`). Auth via Earthdata `.netrc`. Env: `IMERG_USERNAME`/`IMERG_PASSWORD`. |
| FloodScan | AER API (2024+) | Daily 90-day rolling ZIP files (SFED + MFED) for 4 regions. Env: `FLOODSCAN_SFED_URL_*/MFED_URL_*`. |
| FloodScan | Azure blob NC4 archive (pre-2024) | Historical files already on blob: `raster/floodscan/daily/v5/raw/aer_sfed_area_300s_*.nc`. |

## Steps

Each pipeline follows the same abstract base flow (`src/pipelines/pipeline.py`):

1. **Parse args / load config** — CLI dispatches to `run_era5/seas5/imerg/floodscan_pipeline.py`; YAML config (`src/config/<name>_config.yml`) supplies blob paths, coverage dates, and metadata defaults.
2. **Fetch raw data** — `query_api()` downloads from the external source to a temporary local dir; optionally checks blob cache first (`--use-cache`).
3. **Save raw to blob** — raw file uploaded to `raster/<source>/<freq>/raw/`.
4. **Process to COG** — xarray opens the raw file, reshapes/renames dimensions, converts units, embeds 15-field standard metadata (`valid_time`, `issued_time`, leadtime, source, product, etc.), validates with `validate_dataset()`, writes via `rioxarray.to_raster(driver="COG")`.
5. **Upload COG to blob** — processed file uploaded to `raster/<source>/<freq>/processed/` (hot tier for FloodScan/IMERG, cool tier for ERA5/SEAS5).
6. **Backfill mode** (`--backfill`) — `check_coverage()` lists blobs under `processed/`, diffs against expected date range, re-runs steps 2–5 for any gaps.

FloodScan has two extra modes:
- **Global merge**: after processing all four regions, `rioxarray.merge.merge_datasets()` combines them into a single global COG saved under `processed/global/`.
- **Baseline update** (`--baseline-update YEAR`): loads 10 years of SFED processed COGs from blob, computes 11-day centred rolling mean, then `groupby dayofyear` to get daily climatology, saves as NC4 to `raw/`.

## Outputs

All outputs are Azure blob storage (`raster` container), no DB writes from this repo.

| pipeline | blob path pattern | format | freq |
|---|---|---|---|
| ERA5 raw | `era5/monthly/raw/tp_reanalysis_monthly_YYYY_MM.grib` | GRIB | monthly |
| ERA5 processed | `era5/monthly/processed/precip_reanalysis_vYYYY-MM-DD.tif` | COG GeoTIFF | monthly |
| SEAS5 raw | `seas5/monthly/raw/tprate_YYYY.grib` (pre-2024) or `T8LMM010000FC______.grib` (2024+) | GRIB | per-issued-month |
| SEAS5 processed | `seas5/monthly/processed/precip_em_iYYYY-MM-DD_ltN.tif` | COG GeoTIFF | per (issued, leadtime) pair |
| IMERG raw | `imerg/daily/{late\|early}/v7/raw/imerg-daily-{run}-YYYY-MM-DD.nc4` | NC4 | daily |
| IMERG processed | `imerg/daily/{late\|early}/v7/processed/imerg-daily-{run}-YYYY-MM-DD.tif` | COG GeoTIFF | daily |
| FloodScan raw | `floodscan/daily/v5/raw/aer_floodscan_sfed/mfed_…_{region}_90days_DATE.zip` | ZIP | daily |
| FloodScan processed (Africa) | `floodscan/daily/v5/processed/aer_area_300s_vDATE_v05r01.tif` | COG GeoTIFF | daily |
| FloodScan processed (global) | `floodscan/daily/v5/processed/global/aer_area_300s_vDATE_v05r01.tif` | COG GeoTIFF | daily |
| FloodScan baseline | `floodscan/daily/v5/raw/baseline_vDATE_v05r01.nc4` | NC4 | annual (on-demand) |

COG metadata always embeds 15 standard attrs: `averaging_period`, `date_issued`, `date_valid`, `download_date`, `grid_resolution`, `leadtime`, `leadtime_units`, `month_issued`, `month_valid`, `product`, `source`, `units`, `version`, `year_issued`, `year_valid`.

## Dependencies

- **Python 3.12.4**; managed with pip + venv (no `uv` in this repo — predates the convention).
- **Key libs**: `azure-storage-blob`, `cdsapi`, `ecmwf-api-client`, `fsspec`/`s3fs`, `xarray`, `rioxarray`, `cfgrib`, `rasterio`, `dask`, `netCDF4`, `h5netcdf`.
- **External API credentials**: see env var list in frontmatter `dependencies`. All stored as Databricks secrets and injected at runtime.
- **ecCodes system dep**: required for GRIB parsing via `cfgrib` — must be installed on the compute node (`apt-get install libeccodes-dev`).
- No `ocha-stratus`, `ocha-lens`, or `ocha-relay` — this repo uses raw Azure SDK calls directly (predates stratus adoption).

## Failure modes & debugging

| symptom | likely cause | action |
|---|---|---|
| SEAS5 job fails on year >=2024 | AWS S3 credential expiry or GRIB file not yet published | Check env vars `AWS_*`; verify file exists in S3 with `fsspec` |
| ERA5 job fails | CDS API key expired or request quota hit | Check `CDSAPI_KEY`; CDS has a queue — check job status in CDS portal |
| FloodScan update returns `None` for a region | AER endpoint down or 90-day ZIP doesn't contain yesterday's date | Check `FLOODSCAN_*_URL_*` env vars; AER SLA is typically next-day; re-run with `--backfill` |
| IMERG download returns 404 | NASA GES DISC publication lag (late run typically available ~2 days after observation) | Run with `--start-date` one day earlier; check `version_letter` logic (B vs C cutoff 2026-03-03) |
| Coverage gaps | Databricks job skipped or network failure | Run `python run_pipeline.py <pipeline> --mode prod --update --backfill` to detect and fill |
| `validate_dataset` ValueError | Metadata mismatch (leadtime vs dates, wrong CRS, dtype not float32) | Check pipeline's `_set_metadata` / `process_data` output; validation is strict |
| Blob auth failure | SAS token expired | Rotate `DSCI_AZ_BLOB_PROD_SAS_WRITE` in Databricks secret scope |

Logs: Databricks job run logs are in the workspace UI under each job's run history. The `--log-level DEBUG` flag produces verbose output including blob paths.

**Coverage check**: The base pipeline's `check_coverage()` lists blobs at the processed path and diffs against expected dates. Run `--backfill` to fill gaps for any pipeline. Note it currently drops the last 2 expected dates to avoid false alarms for in-progress periods.

## Downstream consumers

- **[ds-floodexposure-monitoring](floodexposure-monitoring.md)** — reads FloodScan daily COGs from `raster/floodscan/` to compute flood exposure per admin boundary; the global merge COG is the primary input.
- **`ds-seas5-skill`** and **`ds-seas5-viz`** (Azure web apps) — read SEAS5 processed COGs from `raster/seas5/monthly/processed/`.
- **AA framework pipelines** (e.g. drought monitoring for SHF, BFA, etc.) — read ERA5 and SEAS5 COGs for tercile/anomaly computation; read IMERG for near-real-time rainfall monitoring.
- **`ds-imerg`** — a separate GHA-scheduled pipeline (`run_download_imerg.yml`) that also writes to the same IMERG blob paths; the two are parallel ingests, not sequential.
