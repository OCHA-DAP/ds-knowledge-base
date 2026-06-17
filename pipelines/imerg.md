---
content_type: pipeline
name: imerg
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Download IMERG (GHA)", ref: ".github/workflows/run_download_imerg.yml", schedule: "0 15 * * *", status: live }
    - { name: "Run IMERG (Databricks)", ref: "666239885322861", schedule: "56 40 14 * * ?", status: live }
inputs:
  - "NASA GES DISC IMERG Late Run v7 daily .nc4 files (GPM_3IMERGDL.07B)"
  - "URL pattern: https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDL.07B/<year>/<month>/3B-DAY-L.MS.MRG.3IMERG.<YYYYMMDD>-S000000-E235959.V07B.nc4"
  - "Earthdata credentials (IMERG_USERNAME / IMERG_PASSWORD)"
  - "Azure blob dev container imb0chd0dev/global — existing blobs listed to skip re-download"
outputs:
  - "Azure blob dev container imb0chd0dev/global — imerg/v7/imerg-daily-late-YYYY-MM-DD.tif (COG)"
dependencies:
  - "azure-storage-blob==12.20.0 (raw SDK — NOT ocha-stratus)"
  - "rioxarray==0.15.5"
  - "xarray==2024.6.0"
  - "pandas==2.2.2"
  - "requests==2.32.3"
  - "netcdf4==1.7.0"
  - "GitHub secrets: DEV_BLOB_SAS, IMERG_USERNAME, IMERG_PASSWORD, GH_TOKEN"
  - "NASA Earthdata account (urs.earthdata.nasa.gov)"
downstream:
  - "hti-hurricanes monitoring — observational trigger (run_check_obsv_trigger.yml) dispatched on OCHA-DAP/ds-aa-hti-hurricanes (ref main) after each run. See pipelines/hti-hurricanes-monitoring.md and frameworks/hti-hurricanes/2024-08-23.md"
source_repo: ocha-dap/ds-imerg
source_branch: add-download   # operational code lives ONLY on add-download; main has a stub main.py. The scheduled GHA (default branch main) pins `ref: add-download` in its checkout. See Discrepancies.
source_sha: a9a79ee
code_ref:
  - "src/datasources/imerg.py — download, process, upload"
  - "src/utils/blob.py — raw Azure container client (DEV only)"
  - "main.py — entrypoint: create_auth_files(); download_recent_imerg()"
  - ".github/workflows/run_download_imerg.yml — schedule + dispatch to hti-hurricanes"
discrepancies:
  - "[conflict] Operational code (src/datasources/imerg.py, src/utils/blob.py, populated requirements.txt, real main.py) exists ONLY on branch add-download. On main, main.py is a stub (print('test')), requirements.txt is empty, and src/datasources/imerg.py is absent. The scheduled GHA runs from the default branch (main), where the workflow's checkout step pins ref add-download to pull the real code. If add-download is deleted or diverges, the scheduled run breaks. This work was never merged to main."
  - "[gap] Databricks job 666239885322861 Run IMERG (UNPAUSED, cron 56 40 14 * * ?) in deployments.md has no source/repo listed. It likely ingests IMERG via a different (ocha-stratus-based) pipeline that writes raster STATS to Postgres -- which is what hti-hurricanes-monitoring actually reads (IMERG national-mean Postgres). This ds-imerg GHA writes only rasters to dev blob and does NOT compute Postgres stats, so the Databricks job is probably the real prod IMERG-stats pipeline, not a duplicate of this one."
  - "[stale] Page targets DEV storage account imb0chd0dev (not prod) and reads DEV_BLOB_SAS via raw azure-storage-blob (not ocha-stratus). Consistent with this being an early/standalone download job rather than the team-standard stratus pipeline."
extra:
  schema_strain: "Two jobs span two platforms/repos: this GHA download (ds-imerg) and Databricks Run IMERG (666239885322861, no repo in deployments.md). They may be unrelated systems sharing the IMERG name rather than one pipeline; deployment.jobs[] lists both but only the GHA is sourced from this repo."
  blob_container: "imb0chd0dev (DEV storage account — not prod)"
  coverage_start: "2024-06-01 (hardcoded in download_recent_imerg)"
  run_type: "IMERG Late Run (L), not Early (E)"
  version: "v7 (07B)"
  raster_format: "Cloud-Optimized GeoTIFF (.tif), variable precipitationCal or precipitation"
visibility: internal
last_synced: "2026-06-17"
---

# IMERG

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Daily (15:00 UTC): authenticate to NASA Earthdata, download IMERG Late Run v7 daily .nc4 for yesterday, convert to COG .tif, upload to Azure dev blob `imerg/v7/`, then dispatch the `ds-aa-hti-hurricanes` observational-trigger workflow.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Download IMERG (GHA) | `.github/workflows/run_download_imerg.yml` | `0 15 * * *` (daily 15:00 UTC) | live |
| Run IMERG (Databricks) | job_id `666239885322861` | `56 40 14 * * ?` (daily ~14:40 UTC) | live (UNPAUSED) — no source repo in deployments.md |

Both are UNPAUSED in `deployments.md`. The Databricks job (`Run IMERG`, job_id `666239885322861`) has no linked repo/branch and is **not** part of this ds-imerg repo. It most likely produces the IMERG raster **stats** in Postgres that `hti-hurricanes-monitoring` reads — a distinct system from this GHA blob-download. Listed here for completeness; `[gap]` in Discrepancies.

## Inputs

- **NASA GES DISC IMERG Late Run v7** daily global precipitation, accessed over HTTPS using NASA Earthdata credentials (`.netrc` / `.urs_cookies` / `.dodsrc` written at runtime from `IMERG_USERNAME` / `IMERG_PASSWORD`).
- URL template: `https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDL.07B/{YYYY}/{MM}/3B-DAY-L.MS.MRG.3IMERG.{YYYYMMDD}-S000000-E235959.V07B.nc4`
- Existing blob listing for `imerg/v7` in the dev container to skip already-downloaded files (idempotent resume).

## Steps

`main.py` calls `create_auth_files()` (writes `~/.netrc` / `~/.urs_cookies` / `~/.dodsrc` from env) then `download_recent_imerg()`, which iterates `2024-06-01`→yesterday, skips blobs already in `imerg/v7/`, and for each missing date downloads the `.nc4`, extracts the precip variable to a COG `.tif`, and uploads it. After the script, the GHA dispatches `run_check_obsv_trigger.yml` on `OCHA-DAP/ds-aa-hti-hurricanes` (ref `main`).

Full implementation (download/process/upload functions, dim handling) lives in `src/datasources/imerg.py` on branch `add-download` — see `code_ref`. Not restated here.

## Outputs

- Azure blob dev container **`imb0chd0dev/global`**, path pattern `imerg/v7/imerg-daily-late-YYYY-MM-DD.tif`
- Format: Cloud-Optimized GeoTIFF (COG), variable = daily accumulated precipitation (`precipitationCal` or `precipitation`), EPSG:4326.

## Dependencies

- `azure-storage-blob==12.20.0` — used directly (raw SDK), **not `ocha-stratus`**. The blob client is built from `DEV_BLOB_SAS` (SAS token for the dev storage account). This is a known non-standard pattern.
- `rioxarray`, `xarray`, `pandas`, `netcdf4`, `requests` — see `requirements.txt`.
- GitHub secrets: `DEV_BLOB_SAS`, `IMERG_USERNAME`, `IMERG_PASSWORD`, `GH_TOKEN`.
- NASA Earthdata account at `urs.earthdata.nasa.gov`.

## Failure modes & debugging

- **Auth failure** — NASA Earthdata rejects credentials. `requests.get(...).raise_for_status()` will throw. Check `IMERG_USERNAME`/`IMERG_PASSWORD` secrets; NASA sometimes requires re-accepting licence agreements.
- **File already late/unavailable** — IMERG Late Run is typically available 2–3 days after the observation date. Downloading "yesterday" may occasionally fail; the exception is caught and logged, and the loop continues.
- **Blob SAS expiry** — `DEV_BLOB_SAS` is a SAS token; when it expires, all blob reads/writes fail silently (container client returns 403). Rotate the secret in GitHub repo settings.
- **Deployed branch ≠ default branch** — the scheduled GHA runs from the default branch `main`, but `main` only has a stub `main.py` (`print("test")`), an empty `requirements.txt`, and NO `src/datasources/imerg.py`. The workflow's checkout step on `main` pins `ref: add-download` to pull the real download code. **All operational code lives on `add-download` and was never merged.** If `add-download` is deleted or diverges, the scheduled run breaks. `[conflict]` — see Discrepancies.
- **Logs** — GitHub Actions run logs under `OCHA-DAP/ds-imerg` Actions tab. No Databricks logs for this repo's GHA job.
- **Idempotent resume** — reruns are safe; existing blobs are skipped.

## Downstream consumers

- **[hti-hurricanes monitoring](hti-hurricanes-monitoring.md)** (framework: [hti-hurricanes](../frameworks/hti-hurricanes/2024-08-23.md)) — this GHA dispatches `run_check_obsv_trigger.yml` on `OCHA-DAP/ds-aa-hti-hurricanes` (ref `main`) after each run, kicking off the Haiti hurricane **observational** trigger check.
  - **Caveat:** the monitoring pipeline reads "IMERG national-mean (Postgres)", i.e. raster **stats** from the DB. This ds-imerg GHA writes only **rasters** to dev blob `imerg/v7/` — it does NOT compute or store Postgres raster stats. The stats almost certainly come from the separate Databricks "Run IMERG" job (job_id `666239885322861`), not from this repo. So this GHA's blob output is not directly the input the monitoring trigger reads; the dispatch is the real coupling. `[gap]` — see Discrepancies.
- The blob output `imerg/v7/` is available to any pipeline reading `imb0chd0dev/global` (dev storage). No known KB-page consumer beyond the above.
