---
content_type: pipeline
name: cma-datasharing
type: dataset-ingest
status: live
deployment:
  platform: azure-webapp
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - { name: "download-all-files (triggered WebJob)", ref: "DataScienceFTP", schedule: "0 0 * * * * (hourly NCRONTAB)", status: live }
    - { name: "chd-ftp-job (triggered WebJob)", ref: "DataScienceFTP", schedule: "on-demand (empty settings.job, no schedule)", status: live }
    - { name: "chd-ftp-debug (triggered WebJob)", ref: "DataScienceFTP", schedule: "on-demand (empty settings.job, no schedule)", status: live }
    - { name: "process_bob_tc.py (local script, NOT deployed)", ref: "branch process-bob-tc, not on DataScienceFTP", schedule: on-demand, status: dev }
    - { name: "process_cmme_history.py (local script, NOT deployed)", ref: "branch cmme-historical, not on DataScienceFTP", schedule: on-demand, status: dev }
inputs:
  - "CMA SFTP server (FTP_HOST env var, port 22 SFTP) -- full directory tree under /"
  - "blob: ds-cma-datasharing/cma_ftp/data_out/2022-2025_BoB_TC/**/*.dat (for process_bob_tc)"
  - "blob: ds-cma-datasharing/cma_ftp/data_out/CMME_History/CMME_history.zip (for process_cmme_history)"
outputs:
  - "blob: ds-cma-datasharing/cma_ftp/<remote-path> (projects container, dev account imb0chd0dev) -- all files mirrored from CMA SFTP"
  - "blob: ds-cma-datasharing/processed/2022-2025_BoB_TC.parquet -- tidy Bay of Bengal TC forecasts"
  - "blob: ds-cma-datasharing/processed/CMME_history.zarr -- CMME seasonal precipitation history 1991-2020"
dependencies:
  - paramiko==2.7.2
  - "azure-storage-blob==12.8.1 (raw SDK, not ocha-stratus, for the SFTP mirror job)"
  - ocha-stratus
  - adlfs
  - zarr
  - xarray
  - rioxarray
  - "env: FTP_HOST, FTP_USER, FTP_PASS, FTP_PORT"
  - "env: DSCI_AZ_BLOB_DEV_SAS_WRITE"
  - "Azure Web App: DataScienceFTP (IMB-CHD-DataScience-EastUS2)"
downstream:
  - "frameworks/afg-drought -- analysis consumer (not scheduled): exploration/cma_forecasts.py on ocha-dap/ds-aa-afg-drought (branch cma-forecasts) reads the CMME history zarr + realtime cmme/ files for the 2026 W1 SEAS5-vs-CMME retrospective."
  - "[gap] No scheduled/live consumer yet -- other candidates (for discoverability, not current edges): drought AA frameworks (frameworks/bfa-drought, eth-drought, ken-drought) that could use CMME as a SEAS5 alternative; bgd-cyclone framework / pipelines/bgd-cyclone-monitoring for Bay of Bengal TC tracks."
depends_on: []
source_repo: ocha-dap/ds-cma-datasharing
source_branch: main
source_sha: 1d723f0
code_ref:
  - "pipelines/download_all_files.py (main -- the deployed SFTP mirror)"
  - "App_Data/jobs/triggered/download-all-files/settings.job + run.cmd (main -- WebJob schedule 0 0 * * * *, deployed)"
  - "App_Data/jobs/triggered/chd-ftp-job/ + chd-ftp-debug/ (main -- legacy debug WebJobs, empty settings.job = manual)"
  - .github/workflows/test-ftp_datascienceftp.yml
  - "pipelines/process_bob_tc.py + src/datasources/cma_cyclones.py (branch process-bob-tc only -- NOT on main, NOT deployed)"
  - "pipelines/process_cmme_history.py (branch cmme-historical only -- NOT on main, NOT deployed)"
extra:
  data_agreement: "CMA data is under a data sharing agreement -- no actual data may be committed to the repo or notebooks. Metadata is fine."
  azure_blob_account: imb0chd0dev (dev stage only)
  cmme_dataset: "CMME monthly mean precipitation forecasts, 1991-2020, 1-degree global, 6-month lead, zarr v3 format"
  cmme_lead_convention: "target month = init month + lead (leads 1-6; an init never covers its own month). PREC is monthly-mean mm/day. Verified 2026-07-22."
  cmme_history_lat_bug: "[open bug] CMME_history.zarr latitude labels are inverted (script assigned linspace(90,-90) to rows running -90..90); consumers must apply ds.assign_coords(lat=-ds.lat).sortby('lat') until the zarr is rewritten. History product is land-only; realtime files are global."
  cmme_realtime_timing: "Realtime cmme/ files arrive ~end of init month or later (Feb 2026 init landed 2026-03-10) -- check blob last_modified before assuming availability at a past decision date; ignore .tmp siblings."
  bob_tc_dataset: "CMA BABJ diamond-7 TC track format; Bay of Bengal historical forecasts 2022-2025"
  webjob_jobs_note: "[conflict-resolved] App_Data/jobs/triggered/ IS on main (verified git ls-tree main): download-all-files/settings.job carries the hourly schedule {\"schedule\": \"0 0 * * * *\"} and run.cmd, plus two legacy debug WebJobs chd-ftp-job and chd-ftp-debug with empty settings.job ({} = manual/triggered, no schedule). So the deployed-from-main app DOES get the hourly schedule. (An earlier note claiming App_Data only lived on cmme-historical was wrong.)"
  processing_pipelines_status: "[gap] process_bob_tc and process_cmme_history are local scripts on unmerged feature branches (process-bob-tc @ dc9e95e, cmme-historical @ ebfc3b7) -- they are NOT WebJobs and are NOT deployed on DataScienceFTP. They are run manually/locally. The production Azure app (main) runs ONLY the SFTP mirror WebJob."
  sftp_use_not_ftp: "Despite the app name DataScienceFTP and early FTP test scripts, the live download pipeline uses SFTP (paramiko, port 22)."
  download_dedup: "download_all_files.py skips blobs that already exist (blob_client.exists() check) -- incremental/idempotent mirror."
visibility: internal
last_synced: "2026-07-22"
deployment_verified_against: "infrastructure/deployments.md -- DataScienceFTP (Running); git ls-tree main for WebJob settings.job"
---

# CMA Data Sharing

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Hourly SFTP mirror from the Chinese Meteorological Administration (CMA) server to Azure blob storage (`projects/ds-cma-datasharing/cma_ftp/`), plus on-demand processing pipelines to convert raw CMA files into tidy parquet (Bay of Bengal TC tracks) and zarr (CMME seasonal forecast history).

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| download-all-files (triggered WebJob) | DataScienceFTP Azure Web App | hourly (`0 0 * * * *` NCRONTAB) | live (deployed) |
| chd-ftp-job (triggered WebJob) | DataScienceFTP Azure Web App | on-demand (empty `settings.job`) | live (legacy debug) |
| chd-ftp-debug (triggered WebJob) | DataScienceFTP Azure Web App | on-demand (empty `settings.job`) | live (legacy debug) |
| process_bob_tc.py | local script (branch `process-bob-tc`) | manual / on-demand | dev -- NOT deployed |
| process_cmme_history.py | local script (branch `cmme-historical`) | manual / on-demand | dev -- NOT deployed |

The Azure Web App `DataScienceFTP` (resource group `IMB-CHD-DataScience-EastUS2`, state **Running** per the [deployments registry](../infrastructure/deployments.md#azure-web-apps)) deploys from `main` on push (GHA workflow `.github/workflows/test-ftp_datascienceftp.yml`). The WebJob schedule (`App_Data/jobs/triggered/download-all-files/settings.job`, holding `{"schedule": "0 0 * * * *"}`) **is on `main`** -- so the deployed app gets the hourly schedule. Two sibling WebJobs (`chd-ftp-job`, `chd-ftp-debug`) are also on `main` but have empty `settings.job` (`{}`), i.e. no schedule -- legacy manual debug jobs. The `process_bob_tc` / `process_cmme_history` rows are **local scripts on unmerged feature branches**, not WebJobs and not deployed.

## Inputs

- **CMA SFTP server**: credentials via env vars `FTP_HOST`, `FTP_USER`, `FTP_PASS`, `FTP_PORT` (default 22). The full remote directory tree under `/` is mirrored.
- **Blob (process_bob_tc)**: `ds-cma-datasharing/cma_ftp/data_out/2022-2025_BoB_TC/**/*.dat` -- CMA BABJ diamond-7 format TC forecast files.
- **Blob (process_cmme_history)**: `ds-cma-datasharing/cma_ftp/data_out/CMME_History/CMME_history.zip` -- zipped archive of 360 monthly `.nc` files, one per init month 1991-01 to 2020-12.

## Steps

**SFTP mirror (`download_all_files.py`)**:
1. Connect to CMA SFTP server via `paramiko`.
2. Recursively walk the remote directory tree.
3. For each file, check if blob `ds-cma-datasharing/cma_ftp/<remote-path>` already exists; skip if so (idempotent).
4. Download to a local temp file, upload to blob (`projects` container, `imb0chd0dev` dev account), delete temp file.
5. Logs counts of downloaded vs skipped; logs public IP at start for CMA IP-allowlist debugging.

> The two processing flows below are local scripts on **unmerged** branches (`process-bob-tc`, `cmme-historical`); they are not part of the deployed app. Exact parsing/column detail lives in the spoke (`code_ref`); this is the summary.

**BoB TC processing (`process_bob_tc.py` / `src/datasources/cma_cyclones.py`, branch `process-bob-tc`)**:
1. List all `.dat` blobs under the BoB prefix.
2. Parse each CMA BABJ diamond-7 file: header gives storm name/ID; data rows give analysis datetime, forecast hour, lon/lat, wind speed (m/s), pressure (hPa), gale/storm radii (km), motion dir/speed.
3. Concatenate into a tidy DataFrame, sort by storm/time/lead, upload as parquet to `ds-cma-datasharing/processed/2022-2025_BoB_TC.parquet`.

**CMME history processing (`process_cmme_history.py`, branch `cmme-historical`)**:
1. Load `CMME_history.zip` from blob into memory.
2. Iterate over 360 `.nc` files matching `PREC.6m.CMME.YYYYMM.1x1.ens.nc`.
3. For each: open with `xr.open_dataset`, replace CMA missing value (`-1e10`), rename dims to `lead`/`lat`/`lon`, set coordinates.
4. Concatenate along `init_time` dimension → shape `(360, 6, 181, 360)`.
5. Write as zarr v3 to `ds-cma-datasharing/processed/CMME_history.zarr` (chunked `init_time=12, lead=6`) using `adlfs.AzureBlobFileSystem` + `zarr.storage.FsspecStore`.

## Outputs

| output | path | format | notes |
|---|---|---|---|
| SFTP mirror | `projects/ds-cma-datasharing/cma_ftp/<remote-path>` | original file formats | hourly incremental; dev blob account |
| BoB TC forecasts | `ds-cma-datasharing/processed/2022-2025_BoB_TC.parquet` | parquet | tidy; cols: storm_id, storm_name, analysis_datetime, forecast_hour, valid_datetime, lon, lat, wind_speed_ms, pressure_hpa, radius_gale_km, radius_storm_km, motion_direction_deg, motion_speed_kmh |
| CMME history | `ds-cma-datasharing/processed/CMME_history.zarr` | zarr v3 | var: PREC (mm/day); dims: init_time (360), lead (6), lat (181), lon (360); 1991-01 to 2020-12 |

All outputs are in the **dev** blob account (`imb0chd0dev`). No prod account is used.

## Reading the CMME seasonal forecast data

Everything below verified 2026-07-22 during the AFG drought W1 comparison
(`exploration/cma_forecasts.py` on `ocha-dap/ds-aa-afg-drought`, branch `cma-forecasts`).

**Lead convention (both realtime and history): target month = init month + lead.**
The realtime files' time axis is `months since YYYY-MM-15` with values 1–6, so an
init **never covers its own month**: a February init covers Mar–Aug (MAM at leads
1–3); a March init covers Apr–Sep and never sees March. Confirmed in the historical
archive (whose time dim carries no units) via the Indian-monsoon seasonality
diagonal. `PREC` is **monthly-mean mm/day** — multiply by days-in-month for totals.

**Realtime files** (`cma_ftp/data_out/cmme/PREC.6m.CMME.YYYYMM.1x1.ens.nc`) are
**netCDF4** (the history archive members are netCDF3 — `engine="scipy"` works for
those but NOT for realtime), global coverage (no land mask), lat ascending −90…90,
lon 0…359. They arrive on the SFTP mirror around the **end of the init month or
later** — e.g. the Feb 2026 init landed 2026-03-10, *after* the AFG drought W1
decision date of 5 Mar. Check blob `last_modified` before assuming a forecast was
available at a past decision date. Ignore the `.tmp` siblings (partial mirror
artifacts).

```python
import adlfs, os, xarray as xr
fs = adlfs.AzureBlobFileSystem(
    account_name="imb0chd0dev", sas_token=os.environ["DSCI_AZ_BLOB_DEV_SAS"])
fs.get("projects/ds-cma-datasharing/cma_ftp/data_out/cmme/"
       "PREC.6m.CMME.202602.1x1.ens.nc", "local.nc")
ds = xr.open_dataset("local.nc", decode_times=False)  # netCDF4; time = lead 1-6
```

**History zarr** (`processed/CMME_history.zarr`, 1991–2020): zarr v3, so open with
`zarr.storage.FsspecStore` + `consolidated=False`, and pass an
`asynchronous=True` filesystem (a sync one breaks inside a running event loop,
e.g. marimo/jupyter). ⚠️ **Its latitude labels are INVERTED**: the processing
script assigned `lat = linspace(90, −90)` but the raw rows run −90…90 (verified
against the land/sea NaN mask — the history product is **land-only**, unlike the
realtime files). Selecting Afghanistan by its true coordinates silently returns
Southern-Hemisphere ocean (all NaN). Until the zarr is rewritten, always apply:

```python
import adlfs, os, xarray as xr, zarr
fs = adlfs.AzureBlobFileSystem(
    account_name="imb0chd0dev", sas_token=os.environ["DSCI_AZ_BLOB_DEV_SAS"],
    asynchronous=True)
store = zarr.storage.FsspecStore(
    fs, path="projects/ds-cma-datasharing/processed/CMME_history.zarr")
ds = xr.open_zarr(store, consolidated=False)
ds = ds.assign_coords(lat=-ds.lat).sortby("lat")  # fix inverted labels
```

Note the zarr is chunked `(init_time=12, lead=6)` with lat/lon unchunked, so any
spatial subset still downloads the full ~560 MB array — pull once and cache
derived series locally. And per the data agreement: derived stats only, no raw
data in repos or notebook outputs.

## Dependencies

- **`paramiko==2.7.2`** -- SFTP transport for the mirror job (raw, not via ocha-stratus)
- **`azure-storage-blob==12.8.1`** -- blob upload for the mirror job (raw SDK, not ocha-stratus)
- **`ocha-stratus`** -- blob I/O for the processing pipelines
- **`adlfs`** + **`zarr`** -- zarr v3 write for CMME history
- **`xarray`**, **`rioxarray`**, **`numpy`**, **`pandas`**, **`scipy`** -- data processing
- **Env vars**: `FTP_HOST`, `FTP_USER`, `FTP_PASS`, `FTP_PORT` (SFTP creds), `DSCI_AZ_BLOB_DEV_SAS_WRITE` (blob write SAS)
- **Azure Web App**: `DataScienceFTP` in resource group `IMB-CHD-DataScience-EastUS2`

## Failure modes & debugging

**SFTP connection failures** -- The CMA server is IP-allowlisted. The pipeline logs the public IP of the Azure Web App at startup (`https://api.ipify.org`). If the IP changed (e.g. after an app restart/scale event), the CMA side will need updating. Check logs for "Connected to sftp server" vs SSH errors.

**[conflict-resolved] WebJob schedule IS on main** -- The `App_Data/jobs/triggered/download-all-files/settings.job` file (which holds `{"schedule": "0 0 * * * *"}` and the `run.cmd` that pip-installs `pipeline_requirements.txt` and runs `download_all_files.py`) is present on `main` (verified via `git ls-tree main`). The GHA deploy workflow (`test-ftp_datascienceftp.yml`) zips the repo and deploys to `DataScienceFTP` from `main` on push, so the hourly WebJob ships with it. If the schedule ever appears not to fire, verify via the Azure Portal Kudu console > WebJobs view -- but the settings are in `main`, not stranded on a feature branch as an earlier note claimed.

**Blob already exists -- skipped** -- The mirror is idempotent by design. If a file from CMA needs to be re-fetched (e.g. CMA updated it in place), you must manually delete the blob first.

**Zarr v3 open errors** -- The CMME history zarr is written in v3 format (`zarr.storage.FsspecStore` + `consolidated=False`, `asynchronous=True` filesystem). See [Reading the CMME seasonal forecast data](#reading-the-cmme-seasonal-forecast-data) above for the working snippet; older snippets also live on the **`cmme-historical`** branch (`exploration/cmme_history_zarr.md`), but they predate the lat-inversion discovery.

**CMME history zarr latitudes inverted (open bug)** -- `process_cmme_history.py` (branch `cmme-historical`) assigns `lat=np.linspace(90, -90, 181)` to rows that actually run −90…90, so every consumer must flip the labels (`ds.assign_coords(lat=-ds.lat).sortby("lat")`) until the script is fixed and the zarr rewritten. Symptom of forgetting: your AOI is all-NaN (you're reading mirrored ocean — the history product is land-only).

**Data sharing restriction** -- CMA data is under a data sharing agreement. No raw data files may be committed to the repo or appear in notebook outputs. Only metadata, code, and derived stats are safe.

**Logs**: Azure Web App logs via the Kudu console (`https://datascienceftp-dvf6gdfbcggaf7b5.eastus2-01.azurewebsites.net/api/logstream`) or Application Insights. Set `LOG_LEVEL=DEBUG` env var for verbose SFTP directory listing output.

## Downstream consumers

**No scheduled consumer yet; one analysis consumer.** The [afg-drought](../frameworks/afg-drought/) framework repo (`ocha-dap/ds-aa-afg-drought`, branch `cma-forecasts`) uses both the CMME history zarr and the realtime `cmme/` files in `exploration/cma_forecasts.py` — a 2026 W1 retrospective comparing SEAS5 against CMME for the trigger AOI (renders a local HTML report; not scheduled). Other candidate consumers, for discoverability only:

- Drought AA frameworks that could use **CMME seasonal precipitation** as a SEAS5 alternative: [frameworks/bfa-drought](../frameworks/bfa-drought/), [afg-drought](../frameworks/afg-drought/), [eth-drought](../frameworks/eth-drought/), [ken-drought](../frameworks/ken-drought/). (SEAS5 itself is served via [apps/seas5-skill](../apps/seas5-skill.md) / [seas5-viz](../apps/seas5-viz.md).)
- Work needing **CMA Bay of Bengal TC track data**: [frameworks/bgd-cyclone](../frameworks/bgd-cyclone/), [pipelines/bgd-cyclone-monitoring](bgd-cyclone-monitoring.md).
- The raw SFTP mirror (`cma_ftp/`) is the upstream source for both processing scripts above, so it must stay current.
