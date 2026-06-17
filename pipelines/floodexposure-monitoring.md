---
content_type: pipeline
name: floodexposure-monitoring
type: exposure
status: live
deployment:
  platform: github-actions
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - { name: "Update exposure rasters", ref: ".github/workflows/run_update_exposure.yml", schedule: "15 23 * * *", status: live }
    - { name: "Update exposure raster stats", ref: ".github/workflows/run_update_raster_stats.yml", schedule: "repository_dispatch: trigger_exposure_raster_stats", status: live }
    - { name: "Update quantiles", ref: ".github/workflows/run_update_quantiles.yml", schedule: "repository_dispatch: trigger_compute_quantiles", status: live }
    - { name: "Init iso3s", ref: ".github/workflows/run_init_iso3.yml", schedule: "on-demand", status: live }
    - { name: "Keep Repo Awake", ref: ".github/workflows/keep_awake.yml", schedule: "0 12 * * 1", status: live }
inputs:
  - "blob raster/floodscan/daily/v5/processed/*.tif (Floodscan SFED COGs, from ds-floodscan-ingest)"
  - "blob projects/ds-floodexposure-monitoring/raw/worldpop/{iso3}_ppp_2020_1km_Aggregated_UNadj.tif (WorldPop 2020 1km UN-adjusted)"
  - "blob projects/ds-floodexposure-monitoring/raw/codab/{iso3}.shp.zip (CODABs from FieldMaps)"
  - "DB app.floodscan_exposure (read-back for existing dates and region stats aggregation)"
outputs:
  - "blob projects/ds-floodexposure-monitoring/processed/flood_exposure/{iso3}/{iso3}_exposure_{date}.tif (daily per-country exposure rasters)"
  - "DB app.floodscan_exposure (cols: iso3, adm_level, valid_date, pcode, sum — upsert, ADM0/1/2)"
  - "DB app.floodscan_exposure_regions (same schema, custom COD regions for DRC)"
  - "DB app.quantile (rolling-average quintile scores for latest date — replaced daily)"
  - "DB app.quantile_regions (same for DRC custom regions)"
  - "DB app.admin_lookup (pcode/name lookup table — replaced on init)"
  - "Azure web app chd-ds-floodexposure-monitoring (consumes DB tables above)"
dependencies:
  - "ocha-stratus==0.1.2"
  - "xarray==2024.7.0"
  - "rioxarray"
  - "geopandas==1.0.1"
  - "dask>2024.8.0"
  - "sqlalchemy==2.0.36"
  - "azure-storage-blob==12.22.0"
  - "python-dotenv==1.0.1"
  - secrets: DSCI_AZ_BLOB_DEV_SAS_WRITE, DSCI_AZ_BLOB_PROD_SAS_WRITE, DSCI_AZ_BLOB_DEV_SAS, DSCI_AZ_BLOB_PROD_SAS, DSCI_AZ_DB_DEV_PW_WRITE, DSCI_AZ_DB_PROD_PW_WRITE, DSCI_AZ_DB_PROD_UID_WRITE, DSCI_AZ_DB_DEV_UID_WRITE, DSCI_AZ_DB_DEV_HOST, DSCI_AZ_DB_PROD_HOST, PAT
  - vars: STAGE, ROLL_WINDOW (default 7)
  - "upstream pipeline: ds-floodscan-ingest (must run before 23:15 UTC)"
downstream:
  - "chd-ds-floodexposure-monitoring Azure web app (https://chd-ds-floodexposure-monitoring.azurewebsites.net)"
  - "Any AA framework monitoring flood exposure in covered countries"
depends_on: [floodscan-ingest]
source_repo: ocha-dap/ds-floodexposure-monitoring
source_branch: main
source_sha: 6319cb0
code_ref:
  - pipelines/update_exposure.py
  - pipelines/update_raster_stats.py
  - pipelines/update_exposure_quantile.py
  - pipelines/init_iso3.py
  - src/constants.py
  - src/datasources/floodscan.py
  - src/datasources/worldpop.py
  - src/datasources/codab.py
  - src/utils/database.py
extra:
  iso3s_covered: [ner, nga, cmr, tcd, bfa, eth, som, ssd, mli, cod, moz, mwi]
  cod_regions: "DRC (cod) has 3 custom sub-national regions built from ADM1 pcodes; region stats stored separately in floodscan_exposure_regions / quantile_regions"
  keep_awake: "keep_awake.yml pushes an empty commit to keep-awake branch weekly (Mondays 12:00 UTC) to prevent GHA from disabling scheduled workflows on inactive repos"
  workflow_chaining: "3-stage chain: update_exposure -> (repository_dispatch) -> update_raster_stats -> (repository_dispatch) -> update_quantiles. Only the first stage is cron-triggered."
discrepancies:
  - "[conflict] DEPLOYED ref != checked-out: local main (6319cb0) is 1 commit ahead of origin/main (095c3d7, 'Merge PR #32 from keep-awake'). GHA workflows run from the pushed origin/main = 095c3d7, NOT the checked-out 6319cb0. The local-only commit ('backfill recent raw files from last 90 days; robust YYYY-MM-DD parsing') is NOT deployed until pushed."
  - "[stale] The update_exposure.yml inline comment says the 23:15 UTC cron is '15 minutes after ds-floodscan-ingest'. The real Run FloodScan Databricks job (792911256578092) runs at 20:00 UTC (Quartz 36 0 20 * * ?), so the true buffer is ~3h15m. Page text claimed '20:36 UTC' (a misread of the cron seconds field) — corrected."
  - "[gap] None of these 5 GHA workflows are listed in infrastructure/deployments.md (the registry only inventories Azure web apps + Databricks jobs + GH Pages). GHA-scheduled pipelines are not yet tracked there; the only registry-confirmed entry for this repo is the Azure app chd-ds-floodexposure-monitoring (Running) and the upstream Databricks Run FloodScan job."
visibility: internal
last_synced: "2026-06-17"
---

# Flood Exposure Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Daily: multiply Floodscan SFED flood-extent rasters by WorldPop population grids → per-ADM0/1/2 exposure sums → rolling-average quintile scores → DB tables consumed by the Azure monitoring app.*

## Jobs & schedule

Three GHA workflows form a chained pipeline (each triggers the next via `repository_dispatch`). Two additional utility workflows exist.

| job | ref | schedule | status |
|---|---|---|---|
| Update exposure rasters | `.github/workflows/run_update_exposure.yml` | cron `15 23 * * *` (23:15 UTC) | live |
| Update exposure raster stats | `.github/workflows/run_update_raster_stats.yml` | `repository_dispatch: trigger_exposure_raster_stats` | live |
| Update quantiles | `.github/workflows/run_update_quantiles.yml` | `repository_dispatch: trigger_compute_quantiles` | live |
| Init iso3s | `.github/workflows/run_init_iso3.yml` | on-demand (`workflow_dispatch`, iso3 input) | live |
| Keep Repo Awake | `.github/workflows/keep_awake.yml` | cron `0 12 * * 1` (Mondays) | live |

The 23:15 UTC cron is meant to run after `ds-floodscan-ingest` completes; there is no explicit dependency check, just timing. NOTE: the workflow's inline comment claims "15 minutes after ds-floodscan-ingest", but the actual `Run FloodScan` Databricks job (job_id `792911256578092`) is scheduled at **20:00 UTC** (Quartz `36 0 20 * * ?` = 20:00:36), so the real buffer is ~3h15m, not 15 min. See `[stale]` discrepancy.

## Inputs

- **Floodscan SFED COGs** — blob container `raster`, path `floodscan/daily/v5/processed/*.tif`. Written by `ds-floodscan-ingest`. The pipeline selects the SFED band (Surface Flood Extent), filters to pixels ≥ 0.05 flood extent to reduce noise, and processes only the most recent 90 days on daily runs (full history on `init_iso3`).
- **WorldPop 2020** — blob container `projects`, path `ds-floodexposure-monitoring/raw/worldpop/{iso3}_ppp_2020_1km_Aggregated_UNadj.tif`. UN-adjusted 1km resolution, 2020 vintage. Sourced from WorldPop API on init.
- **CODABs** — blob container `projects`, path `ds-floodexposure-monitoring/raw/codab/{iso3}.shp.zip`. Downloaded from FieldMaps on init. ADM2 boundaries used for clipping and pcode joins.
- **DB `app.floodscan_exposure`** — read back by `update_raster_stats.py` to skip already-processed dates (clobber=False mode), and by `update_exposure_quantile.py` to calculate rolling quantiles.

12 countries covered: `ner, nga, cmr, tcd, bfa, eth, som, ssd, mli, cod, moz, mwi` (all Africa).

## Steps

1. **`update_exposure.py`** — for each ISO3: load WorldPop raster from blob, list Floodscan COGs from blob (last 90 days), skip already-processed exposure rasters, interpolate SFED to WorldPop grid (nearest), multiply → exposure raster, upload COG to blob as `ds-floodexposure-monitoring/processed/flood_exposure/{iso3}/{iso3}_exposure_{date}.tif`. Processed in batches of 100 to limit memory.
2. **`update_raster_stats.py`** — for each ISO3: load ADM2 CODAB from blob, list processed exposure rasters, skip dates already in DB, clip each raster to each ADM2 polygon, sum exposed population, aggregate to ADM0/ADM1/ADM2, upsert to `app.floodscan_exposure`. Then handles DRC custom regions (aggregates ADM1 stats by region definition in `constants.REGIONS`) and upserts to `app.floodscan_exposure_regions`.
3. **`update_exposure_quantile.py`** — reads the latest `valid_date` from `app.floodscan_exposure`, computes a `ROLL_WINDOW`-day rolling average per pcode for the same calendar day across all years, assigns quintile scores (-2 to +2) using 20/40/60/80th percentile boundaries, writes today's row to `app.quantile` (full replace) and `app.quantile_regions`.
4. **`init_iso3.py`** (on-demand) — downloads CODAB + WorldPop to blob, runs full-history exposure raster calculation, updates `app.admin_lookup` table.

## Outputs

| destination | description |
|---|---|
| blob `ds-floodexposure-monitoring/processed/flood_exposure/{iso3}/{iso3}_exposure_{date}.tif` | Daily COG: population × flood fraction, per country |
| DB `app.floodscan_exposure` | Daily population-exposed sums by pcode + adm_level (0/1/2) |
| DB `app.floodscan_exposure_regions` | Same, for DRC's 3 custom sub-national regions |
| DB `app.quantile` | Today's rolling-average quintile score per pcode (full replace each run) |
| DB `app.quantile_regions` | Same for DRC regions |
| DB `app.admin_lookup` | Pcode → name lookup table for all covered countries + DRC regions |

The Azure web app `chd-ds-floodexposure-monitoring` reads directly from the DB tables.

## Dependencies

- **`ocha-stratus==0.1.2`** — blob list, COG open/upload, DB engine, upsert helper (`stratus.postgres_upsert`)
- **`xarray` / `rioxarray` / `dask`** — raster processing and clipping
- **`geopandas`** — CODAB loading and ADM2 polygon iteration
- **`sqlalchemy==2.0.36`** — DB writes (schema creation, upserts, replacements)
- **GitHub secrets** — `DSCI_AZ_BLOB_{DEV,PROD}_SAS_WRITE`, `DSCI_AZ_BLOB_{DEV,PROD}_SAS`, `DSCI_AZ_DB_{DEV,PROD}_PW_WRITE`, `DSCI_AZ_DB_{DEV,PROD}_UID_WRITE`, `DSCI_AZ_DB_{DEV,PROD}_HOST`, `PAT` (used by workflow chaining curl calls)
- **GitHub vars** — `STAGE` (dev/prod), `ROLL_WINDOW` (default 7 days)
- **Upstream** — `ds-floodscan-ingest` (Databricks job_id `792911256578092`, `Run FloodScan`, Quartz `36 0 20 * * ?` = **20:00 UTC** daily, UNPAUSED) must complete before the 23:15 UTC `update_exposure` run

## Failure modes & debugging

- **Timing race with ds-floodscan-ingest** — `update_exposure` fires at 23:15 UTC; the `Run FloodScan` Databricks job runs at 20:00 UTC, so there is a ~3h15m buffer (NOT the "15 minutes" the workflow comment claims). Usually safe, but a slow or delayed ingest will mean today's Floodscan data is missing. The pipeline will skip the date and catch up on the next run (clobber=False). Check GHA run times and the `Run FloodScan` Databricks job status first.
- **Workflow chain breaks** — if `update_exposure` succeeds but `update_raster_stats` never triggers, check whether the `PAT` secret is valid (it's used for the `repository_dispatch` curl call). GHA logs for the parent job will show the curl exit code.
- **Missing Floodscan SFED band** — the code inspects `da.attrs["long_name"]` and skips any file where the band label is unrecognized. If Floodscan changes its band ordering or naming, exposure rasters will silently stop being produced. Watch for runs that complete with no uploaded files.
- **DB schema drift** — `create_flood_exposure_table` uses `CREATE TABLE IF NOT EXISTS` semantics via SQLAlchemy `metadata.create_all`. Column changes require manual DDL; the upsert constraint is on `(pcode, valid_date)`.
- **`app.quantile` full-replace** — `update_exposure_quantile.py` uses `if_exists="replace"`, dropping and recreating the table each run. If this job fails mid-run, the table may be absent. The app will break until the next successful run or a manual re-run.
- **Keep-awake workflow** — pushes an empty commit to the `keep-awake` branch weekly. If GHA disables scheduled workflows due to inactivity (60-day rule), re-enable via the GHA UI and confirm `keep_awake.yml` is running.
- **Logs** — all run logs in GHA Actions tab of the repo. No Slack/email alerting configured; failures are silent unless monitored externally.
- **Local main ahead of origin (deployed ref != checked-out)** — at ingestion, local `main` (`6319cb0`, a Floodscan 90-day backfill / robust-date-parse commit) was 1 commit ahead of `origin/main` (`095c3d7`). GHA runs from the pushed `origin/main`, so that local commit is NOT live until pushed. If recent-date handling looks wrong in production, confirm whether `6319cb0` was ever pushed. See `discrepancies`.

## Downstream consumers

- **`chd-ds-floodexposure-monitoring`** Azure web app (https://chd-ds-floodexposure-monitoring.azurewebsites.net) — the primary consumer; reads `app.floodscan_exposure`, `app.quantile`, `app.admin_lookup`, and region equivalents.
- Any AA framework monitoring tools that incorporate flood exposure for covered countries should link here for the DB table schema.
