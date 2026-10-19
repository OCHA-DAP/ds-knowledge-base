---
content_type: pipeline
name: nhc-forecast
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Run script (GHA)", ref: ".github/workflows/run-python-script.yaml", schedule: "0 */3 * * * (workflow disabled since 2026-06-08)", status: "paused (disabled manually on GitHub 2026-06-08 after every scheduled run had failed since 2026-06-02; last success 2026-06-02; no runs since)" }
    - { name: "Keep Repo Awake (GHA)", ref: ".github/workflows/keep_awake.yml", schedule: "0 12 * * 1", status: live }
inputs:
  - "https://www.nhc.noaa.gov/CurrentStorms.json (NHC active storms JSON, scraped every 3h)"
  - "NHC per-storm Forecast Advisory HTML (URL from CurrentStorms.json forecastAdvisory.url)"
  - "noaa/nhc/forecasted_tracks.csv (existing cumulative blob, read-then-append)"
  - "noaa/nhc/observed_tracks.csv (existing cumulative blob, read-then-append)"
outputs:
  - "noaa/nhc/forecasted_tracks.csv (cumulative, ';'-delimited; id, name, issuance, basin, latitude, longitude, maxwind, validTime)"
  - "noaa/nhc/observed_tracks.csv (cumulative, ';'-delimited; id, name, basin, intensity, pressure, latitude, longitude, lastUpdate)"
  - "noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/forecasted_tracks.csv (pre-update backup each run)"
  - "noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/observed_tracks.csv (pre-update backup each run)"
  - "GitHub workflow_dispatch (ref main) to each URL in GH_ACTION_TRIGGER_URLS (downstream AA monitoring repos)"
surfaces: []
dependencies:
  - "hdx-python-api==6.4.5 (facade/config/Retrieve/Download wrappers only; nothing is uploaded to HDX)"
  - "azure-storage-blob==12.19.1 (raw SDK, NOT ocha-stratus)"
  - "beautifulsoup4~=4.12.3"
  - "pandas==2.2.3"
  - "python-dateutil~=2.9.0"
  - "lat-lon-parser==1.3.0"
  - "GHA secrets: STORAGE_ACCOUNT, CONTAINER, KEY, GHP, HDX_SITE, HDX_BOT_SCRAPERS_API_TOKEN (as HDX_KEY), PREPREFIX, USER_AGENT, EMAIL_SERVER/PORT/USERNAME/PASSWORD/LIST/FROM"
  - "GHA repo var: GH_ACTION_TRIGGER_URLS (comma-separated dispatch URLs)"
downstream:
  - "pipelines/hti-hurricanes-monitoring.md (GH_ACTION_TRIGGER_URLS targets ds-aa-hti-hurricanes run_check_trigger.yml, which no longer exists in that repo)"
  - "pipelines/cub-hurricanes-monitoring.md (GH_ACTION_TRIGGER_URLS targets ds-aa-cub-hurricanes 01_run_forecast_data_ingestion.yml, now disabled manually)"
depends_on: []
source_repo: ocha-dap/ds-nhc-forecast
source_branch: main
source_sha: "7857d9b"
code_ref:
  - "nhc_forecast.py: NHCHurricaneForecast.get_data() / upload_dataset(), AzureBlobUpload, trigger_for_active_storms()"
  - "run.py: main() entrypoint, AzureBlobDownload (hand-rolled SharedKey GET)"
  - ".github/workflows/run-python-script.yaml: schedule + secrets wiring + failure email"
  - ".github/workflows/keep_awake.yml: weekly empty commit to keep-awake"
  - "config/project_configuration.yaml, config/hdx_dataset_static.yaml (HDX facade boilerplate)"
extra:
  superseded_by: "pipelines/storms-pipeline.md. Its Databricks `nhc_pipeline` job (dbx:959161297191654, repo ds-storms-pipeline) is the live prod NHC writer into the Postgres storms.nhc_* tables. The Databricks jobs once listed here (Run NHC 266763033249426, [dev adm_tdowning] NHC Pipeline 583285176982712) were never defined in this repo; the first was deleted (#698), the second is paused."
  blob_storage_pattern: "Raw azure-storage-blob SDK, predates ocha-stratus. Flat noaa/nhc/ paths, not the {PROJECT_PREFIX}/{raw|processed}/{datasource}/ convention."
  keep_awake_branch: "The keep-awake branch only collects the weekly empty '[skip ci]' commits; its tree is identical to main, which this page is synced to (last pipeline-logic change: trigger-cub merge 2025-07-29; main's last commit merged keep_awake.yml on 2025-10-21)."
visibility: internal
last_synced: "2026-10-08"
---

# NHC Forecast

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Every 3 hours (GHA): scrape NHC active-storm JSON plus per-storm forecast advisory text, append to cumulative observed/forecasted track CSVs in Azure blob, then dispatch downstream AA monitoring workflows. **Legacy writer: the prod NHC path is now [storms-pipeline](storms-pipeline.md); this repo's `Run script` workflow has been disabled on GitHub since 2026-06-08, so nothing here runs.**

## Jobs & schedule

This repo defines only two GHA workflows (no `databricks.yml`):

| job | ref | schedule | status |
|---|---|---|---|
| Run script (GHA) | `.github/workflows/run-python-script.yaml` | `0 */3 * * *` (every 3h) + manual dispatch | **paused**: workflow state `disabled_manually` since 2026-06-08, after every scheduled run had failed since 2026-06-02 (last success 2026-06-02 19:10 UTC); no runs since. [pipeline-registry](../infrastructure/pipeline-registry.md) shows it as 🔴 `FAILING, NO-SUCCESS` because it reads the last run, not the workflow state |
| Keep Repo Awake (GHA) | `.github/workflows/keep_awake.yml` | `0 12 * * 1` (Mondays) | live; empty commit to the `keep-awake` branch so GitHub doesn't disable the schedule |

**Not this repo's jobs (earlier versions of this page listed them):** the Databricks jobs `Run NHC` (`266763033249426`, deleted by 2026-09-29, #698) and `[dev adm_tdowning] NHC Pipeline` (`583285176982712`, PAUSED) are registered against `OCHA-DAP/ds-storms-pipeline`, as is the live prod `NHC Pipeline` (`dbx:959161297191654`, 4×/day, writes `storms.nhc_*`). See [storms-pipeline](storms-pipeline.md).

## Inputs

- **NHC `CurrentStorms.json`**: `activeStorms[]` with position, intensity, pressure and `forecastAdvisory.url` per storm.
- **NHC Forecast Advisory HTML**: one per active storm; the `<pre>` text is parsed for `FORECAST VALID`, `OUTLOOK VALID` and `REMNANTS OF CENTER LOCATED NEAR` lines.
- **`noaa/nhc/forecasted_tracks.csv` / `observed_tracks.csv`**: the existing cumulative blobs, downloaded so new rows can be deduped and appended.
- **Licence**: NWS/NOAA content is US public domain; see the [shareability matrix](../infrastructure/datasets/README.md#can-we-share-derived-products).

## Steps

1. `run.py: main()` reads config through the HDX facade, builds `NHCHurricaneForecast`, calls `get_data()`.
2. Fetch `CurrentStorms.json`; if `activeStorms` is empty, log "No datasets were uploaded." and exit with no writes.
3. Observed rows: id, name, basin (first two chars of id), intensity, pressure, lat, lon, lastUpdate.
4. Forecast rows: per storm fetch the advisory HTML, parse each forecast/outlook/remnants line, convert day/time to a full `validTime` (month rollover handled), parse lat/lon, record maxwind. One row per horizon.
5. `upload_dataset()`: download both existing CSVs, `pd.concat(...).drop_duplicates()`, write the pre-update CSVs to `noaa/nhc/previous/{date}_{time}/`, then overwrite the cumulative CSVs (sorted newest first).
6. POST `{"ref": "main"}` to every URL in `GH_ACTION_TRIGGER_URLS` using the `GHP` token to dispatch downstream workflows.
7. On success the workflow runs a git-auto-commit step for `dataset_dates.txt` (a file this code does not appear to create; probably a harmless no-op left over from the HDX scraper template). On failure it emails `EMAIL_LIST`.

## Outputs

| artifact | path / address | format | notes |
|---|---|---|---|
| Observed tracks (cumulative) | `noaa/nhc/observed_tracks.csv` | CSV (`;`) | id, name, basin, intensity, pressure, latitude, longitude, lastUpdate |
| Forecasted tracks (cumulative) | `noaa/nhc/forecasted_tracks.csv` | CSV (`;`) | id, name, issuance, basin, latitude, longitude, maxwind, validTime |
| Backups | `noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/{observed,forecasted}_tracks.csv` | CSV | pre-update copy each run |
| Workflow dispatch | URLs in `GH_ACTION_TRIGGER_URLS` | HTTP POST | `ref: main` |

## Dependencies

- Raw `azure-storage-blob` for writes (`BlobServiceClient.from_connection_string`) and a hand-rolled HMAC SharedKey GET in `run.py` for reads. No `ocha-stratus`, no Postgres, no Listmonk.
- `hdx-python-api` is used for config/retriever scaffolding only.
- `beautifulsoup4` (advisory HTML), `lat-lon-parser` (`22.9N` / `68.1W`).
- Secrets and vars as in the frontmatter; the HDX token comes from the `HDX_BOT_SCRAPERS_API_TOKEN` secret.

## Failure modes & debugging

- **Not running (since 2026-06-08).** `Run script` was disabled manually on GitHub on 2026-06-08 after every scheduled run had failed since 2026-06-02 (last success 2026-06-02 19:10 UTC); the cron does not fire. The logs of those runs have expired, so the cause is unknown. Check with `gh workflow list -R OCHA-DAP/ds-nhc-forecast --all`. Decide whether to retire this repo in favour of [storms-pipeline](storms-pipeline.md); until then the blob CSVs are stale.
- **No active storms:** clean early exit outside the season (Atlantic ~Jun-Nov, E. Pacific ~May-Nov).
- **Advisory download fails:** `DownloadError` is logged (`"Could not download from url"`) and that storm's forecast rows are skipped; the run still succeeds.
- **Blob upload fails:** `AzureBlobUpload.upload_file` catches and logs (`"Failed to upload dataset"`) without re-raising, so a failed write can look like a green run. No retry.
- **Webhook fails:** `trigger_for_active_storms` returns the response without checking status, so a 401/404 from GitHub is not detected; only a raised exception is logged.
- **Write race:** read-append-overwrite on a shared blob. Safe only while this GHA is the sole writer; do not run a second writer against `noaa/nhc/`.
- **Branch:** the `keep-awake` branch only holds the keep-awake empty commits; edit logic on `main`.
- **Logs:** Actions tab of `OCHA-DAP/ds-nhc-forecast`.

## Downstream consumers

- **[hti-hurricanes-monitoring](hti-hurricanes-monitoring.md)** and **[cub-hurricanes-monitoring](cub-hurricanes-monitoring.md)**: historically read these blob CSVs (basin `al`) and were dispatched on new tracks. Both now also get NHC data from the storms Postgres tables written by [storms-pipeline](storms-pipeline.md) (its `nhc_pipeline` triggers the Cuba and HTI Databricks monitors directly), so the dependency on this repo is likely vestigial. Confirm before retiring.

## Discrepancies

- **[conflict]** [pipeline-registry](../infrastructure/pipeline-registry.md) annotates this GHA row as `storms.nhc_*` "(intended prod NHC writer)", and DESIGN D43 (2026-06-22) calls it "the real prod NHC writer". The code at `7857d9b` writes only the `noaa/nhc/*.csv` blobs and never touches Postgres. The `storms.nhc_*` tables are written by [storms-pipeline](storms-pipeline.md) (`mode=prod` since 2026-09-22). The registry's curated annotation needs correcting.
- **[stale]** Earlier versions of this page listed Databricks jobs `266763033249426` and `583285176982712`. Neither is defined in this repo; both belong to `ds-storms-pipeline` (the first was deleted, #698; the second is paused). They have been removed from `deployment.jobs`.
- **[stale]** `pipeline/NHC_forecast_pipeline.json` (2024-06-27) is an empty Azure-Data-Factory-style stub (name and annotations only), not a job definition.
- **[stale]** The registry's `FAILING, NO-SUCCESS` for this workflow and D43's "failing since 8 Jun" describe the last runs (they actually failed from 2026-06-02); the workflow has been disabled since 2026-06-08 and does not run, so the blob outputs are stale. The cause of the 2026-06-02..08 failures cannot be recovered (run logs expired).
- **[stale]** `GH_ACTION_TRIGGER_URLS` (repo variable, last set 2025-07-25) dispatches `ds-aa-cub-hurricanes` `01_run_forecast_data_ingestion.yml` (now disabled manually) and `ds-aa-hti-hurricanes` `run_check_trigger.yml` (no longer in that repo). Both targets are dead, so the dispatch step would do nothing useful even if this workflow ran.
