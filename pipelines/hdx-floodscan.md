---
content_type: pipeline
visibility: internal
name: hdx-floodscan
type: publish
status: live
surfaces:
  - {url: "https://data.humdata.org/dataset/floodscan", kind: download, title: "HDX dataset: FloodScan — Near Real-Time and Historical Flood Mapping", origin: external}
source_repo: OCHA-DAP/hdx-floodscan
deployment:
  platform: github-actions   # + Databricks prepare job (DB half) — see body
  resource_group: null
  jobs:
    - { name: "HDX FloodScan Prepare", ref: "databricks.yml:hdx_floodscan_prepare", schedule: "daily 00:15 UTC (after Run FloodScan) — DB queries → dev blob → dispatches the workflow", status: "pending (hdx-floodscan#24)" }
    - { name: "run-python-script (publisher)", ref: ".github/workflows/run-python-script.yaml", schedule: "on dispatch (from the prepare job; also from Run FloodScan's last task ~23:20 UTC, which the freshness guard turns into a no-op)", status: live }
inputs:
  - "DB table: public.floodscan on chd-rasterstats-prod (SFED zonal stats, adm 1+2; via ds-raster-stats) — yearly maxima to 2023 (return periods), 10-year day-of-year 11-day rolling baseline, last 90 days; HRP countries only for the latter two (public.iso3.has_active_hrp)"
  - "blob (prod, raster): floodscan/daily/v5/processed/aer_area_300s_v{date}_v05r01.tif (last 90 days) + floodscan/daily/v5/raw/baseline_v2025-01-01_v05r01.nc4 (SFED_BASELINE grid)"
  - "blob (prod, polygon): admin_lookup.parquet (admin names for the xlsx)"
  - "blob (dev, projects): hdx-floodscan/intermediate/latest/*.parquet + manifest.json — the three DB frames, parked by the prepare job"
outputs:
  - "HDX dataset `floodscan` (org OCHA CHD, maintainer isatotun): hdx_floodscan_zonal_stats.xlsx (admin1 + admin2 sheets: SFED, empirical RP, SFED_BASELINE per day, last 90 days) + aer_floodscan_300s_SFED_90d.zip (90 daily 2-band COGs: SFED, SFED_BASELINE)"
  - "blob (dev, projects): hdx-floodscan/intermediate/{latest,YYYY-MM-DD}/ (dated copies pruned after 14 days)"
dependencies:
  - "raster-stats (public.floodscan must have the day's rows — Run FloodScan 23:00 UTC → Raster Stats FLOODSCAN → done ~23:20 UTC)"
  - "hdx-python-api 6.6.5 (facade; HDX_KEY / HDX_SITE / USER_AGENT / PREPREFIX env)"
  - "ocha-stratus (blob on both sides; DB on the Databricks side)"
  - "HDX org Actions secrets: HDX_BOT_SCRAPERS_API_TOKEN, HDX_PIPELINE_PREPREFIX, USER_AGENT, HDX_SITE, HDX_PIPELINE_EMAIL_* / HDX_EMAIL_LIST (failure mail) — owned by the HDX side, visible only to GitHub runners"
  - "org Actions secrets DSCI_AZ_BLOB_DEV_SAS + DSCI_AZ_BLOB_PROD_SAS (publisher's blob reads)"
  - "dsci secret GH_FLOODSCAN_TOKEN (PAT that dispatches the workflow; also used by ds-raster-pipelines' 'Trigger GitHub Action' notebook)"
  - "src/utils/return_periods.py: empirical RP via lmoments3 / scipy pearson3 (Zack, 2024-11..2025-01)"
depends_on:
  - raster-stats
  - dbx-job-compute
last_verified: 2026-09-25
---

# HDX FloodScan publish

Publishes the team's FloodScan zonal statistics to HDX as the dataset
[**FloodScan: Near Real-Time and Historical Flood Mapping**](https://data.humdata.org/dataset/floodscan):
a daily xlsx of admin-1/2 SFED flood fraction with an empirical return period
and a 10-year day-of-year baseline, plus a zip of the last 90 days of SFED +
SFED_BASELINE GeoTIFFs. Built by Zack (return periods, baseline) and Isa (HDX
publishing, GitHub Action), Nov 2024 – Feb 2025; HDX team (mcarans) touches the
packaging.

> **Split across Databricks and GitHub since the private-endpoint cutover ([hdx-floodscan#24](https://github.com/OCHA-DAP/hdx-floodscan/pull/24), 2026-09-25, pending review by Isa/Zack).**
> The rasterstats DB is reachable only through its private endpoint, but the HDX
> bot token is an OCHA-DAP **org** secret that only GitHub runners can see and
> nobody on the DS side holds — so the publish cannot simply move to Databricks.
> Instead:
>
> 1. **Databricks job `HDX FloodScan Prepare`** (00:15 UTC, Job Compute policy,
>    generic `databricks/run_task.py` wrapper) runs the three `public.floodscan`
>    queries (`src/utils/pg.py` `query_*`) against **prod**, writes them as
>    parquet to the **dev** blob under `projects/hdx-floodscan/intermediate/`
>    (`latest/` + dated copy + `manifest.json` with `generated_at`, `db_stage`,
>    `floodscan_max_date`, row counts), then dispatches the GitHub workflow with
>    `GH_FLOODSCAN_TOKEN` (`--secret`, resolved from the dsci scope at run time).
> 2. **GitHub workflow `run-python-script.yaml`** publishes: `pg.fs_*` read the
>    parquet from blob with the same names/arguments/frames as the old DB
>    queries (verified frame-for-frame identical, adm 1+2, including the
>    downstream `fs_add_rp` + baseline merge), rasters and the admin lookup come
>    from the prod blob via stratus, `run.py`/`floodscan.py` are unchanged.
> 3. **Freshness guard** `scripts/check_intermediates.py`: the upstream
>    `Run FloodScan` job's last task still dispatches this workflow (~23:20 UTC,
>    owner adm.itot6, before the prepare job has run); a manifest older than 6 h
>    or a missing `latest/` skips the publish (green, logged). `workflow_dispatch`
>    with `force=true` publishes whatever is in `latest/`.
>
> Before #24 the workflow ran the queries itself against the hard-coded prod
> FQDN as `chdadmin`, and read blob with a storage-account key.

## How it runs

- **Trigger chain:** ds-raster-pipelines `Run FloodScan` (23:00 UTC) → download
  → `Raster Stats FLOODSCAN` (ds-raster-stats) → notebook `Trigger GitHub Action`
  (dispatches this repo's workflow; legacy, now a no-op via the guard). Then
  `HDX FloodScan Prepare` at 00:15 UTC → dispatch → real publish. Ideal end
  state: the owner of `Run FloodScan` replaces its last task with a
  `run_job_task` pointing at the prepare job, and the bundle is redeployed with
  `--var pause_status=PAUSED`.
- **Data plane:** DB read = prod (`STAGE`, default `prod`); intermediates = dev
  blob (`pg.INTERMEDIATE_*` constants); rasters/admin lookup = prod blob.
- **Deploy:** `databricks bundle validate|deploy -t prod -p DEFAULT` in the repo;
  code ships by pushing `main` (`git_source`). Failure e-mail: job → Tristan;
  workflow → `HDX_EMAIL_LIST` (unchanged).
- **Runbook:** publish skipped? Read the guard line in the workflow log
  (`publish=false: stale …`) — the prepare job has not run for this cycle; check
  the Databricks job, or re-dispatch with `force=true` after it has. Empty
  `last_90_days` makes the prepare job refuse (raises) rather than publish an
  empty dataset.
- **Local:** `python scripts/prepare_intermediates.py --no-dispatch` (needs prod
  DB read creds + dev blob write SAS) parks intermediates; the publish half
  needs the HDX env vars nobody local has — so the HDX upload itself can only
  be exercised by the workflow.

## Gotchas

- `mode="prod"` in `floodscan.get_data` is now `self.stage` (default `prod`);
  `pg.fs_*` assert the manifest's `db_stage` matches, so a dev-prepared set
  cannot be published as prod by accident.
- The xlsx is written by appending sheets to the checked-in
  `files/floodscan_readme.xlsx` (`mode="a"`, `if_sheet_exists="replace"`).
- `fs_year_max` is fixed at `valid_date <= '2023-12-31'` (the RP reference
  period); the baseline window is the last 10 full years relative to `NOW()`.
- HDX `Retrieve.download_file` passes `path=` plus the pipeline's extra kwargs
  (`container`, `blob`, `stage`) straight to the custom `AzureBlobDownload`
  in `run.py`; keep that signature if you touch it.
