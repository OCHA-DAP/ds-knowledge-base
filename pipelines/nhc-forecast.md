---
content_type: pipeline
name: nhc-forecast
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Run NHC (Databricks)", ref: "266763033249426", schedule: "17 0 0/3 * * ?", status: paused }
    - { name: "[dev adm_tdowning] NHC Pipeline (Databricks)", ref: "583285176982712", schedule: "0 0,30 0/3 * * ?", status: live }
    - { name: "Run script (GHA)", ref: ".github/workflows/run-python-script.yaml", schedule: "0 */3 * * *", status: live }
    - { name: "Keep Repo Awake (GHA)", ref: ".github/workflows/keep_awake.yml", schedule: "0 12 * * 1", status: live }
inputs:
  - "https://www.nhc.noaa.gov/CurrentStorms.json (NHC active storms JSON — scraped every 3h)"
  - "NHC per-storm Forecast Advisory HTML (URL from CurrentStorms.json forecastAdvisory.url)"
  - "noaa/nhc/forecasted_tracks.csv (existing historical blob — read-then-append)"
  - "noaa/nhc/observed_tracks.csv (existing historical blob — read-then-append)"
outputs:
  - "noaa/nhc/forecasted_tracks.csv (cumulative; fields: id, name, issuance, basin, latitude, longitude, maxwind, validTime)"
  - "noaa/nhc/observed_tracks.csv (cumulative; fields: id, name, basin, intensity, pressure, latitude, longitude, lastUpdate)"
  - "noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/forecasted_tracks.csv (timestamped backup written each run)"
  - "noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/observed_tracks.csv (timestamped backup written each run)"
  - "GitHub Actions webhook trigger to ds-aa-hti-hurricanes (fired when new storm data is appended)"
dependencies:
  - "hdx-python-api==6.4.5 (HDX facade, config, Retrieve/Download wrappers)"
  - "azure-storage-blob==12.19.1 (direct raw SDK — NOT ocha-stratus)"
  - "beautifulsoup4~=4.12.3 (forecast advisory HTML parsing)"
  - "pandas==2.2.3"
  - "python-dateutil~=2.9.0"
  - "lat-lon-parser==1.3.0 (parse NE/SE lat-lon strings)"
  - "env: STORAGE_ACCOUNT, CONTAINER, KEY (Azure blob auth)"
  - "env: GHP (GitHub PAT for webhook trigger)"
  - "env: GH_ACTION_TRIGGER_URLS (comma-separated GHA dispatch URLs)"
  - "env: HDX_SITE, HDX_KEY, PREPREFIX, USER_AGENT (HDX facade)"
downstream:
  - "pipelines/hti-hurricanes-monitoring.md (ds-aa-hti-hurricanes — its run_check_trigger workflow is GHA-dispatched by this pipeline on each new track)"
depends_on: []
source_repo: ocha-dap/ds-nhc-forecast
source_branch: keep-awake
source_sha: "5295166"
code_ref:
  - "nhc_forecast.py — NHCHurricaneForecast.get_data() / upload_dataset()"
  - "run.py — main() entrypoint, AzureBlobDownload"
  - ".github/workflows/run-python-script.yaml — GHA schedule + secrets wiring"
extra:
  note: "The production Databricks job (266763033249426) is PAUSED; a dev job for adm_tdowning (583285176982712) is UNPAUSED and effectively running prod cadence. The GHA workflow on the repo also runs every 3h independently. It is unclear whether both are writing to the same blob simultaneously — a concurrency/race hazard."
  blob_storage_pattern: "Uses raw azure-storage-blob SDK rather than ocha-stratus — predates the team standard. Blob paths are flat under noaa/nhc/, not following the {PROJECT_PREFIX}/{raw|processed}/{datasource}/ convention."
  keep_awake_branch: "The most-recent branch is keep-awake (2025-10-09), which exists only to keep GHA alive via weekly empty commits. The pipeline logic is on main."
visibility: internal
last_synced: "2026-06-17"
---

# NHC Forecast

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Every 3 hours: scrape NHC active-storm JSON + per-storm forecast advisory text → append to cumulative observed and forecasted track CSVs in Azure blob → webhook-trigger `ds-aa-hti-hurricanes` GHA if new data was written.

## Jobs & schedule

A pipeline repo is often several jobs/workflows with different schedules. List them (one row even if single):

| job | ref | schedule | status |
|---|---|---|---|
| Run NHC (Databricks) | job_id 266763033249426 | `17 0 0/3 * * ?` (every 3h) | paused |
| [dev adm_tdowning] NHC Pipeline (Databricks) | job_id 583285176982712 | `0 0,30 0/3 * * ?` (every 3h) | live |
| Run script (GHA) | `.github/workflows/run-python-script.yaml` | `0 */3 * * *` (every 3h) | live |
| Keep Repo Awake (GHA) | `.github/workflows/keep_awake.yml` | `0 12 * * 1` (Mondays) | live |

**Deployment anomaly:** The named production Databricks job "Run NHC" is PAUSED. A developer-namespaced job "[dev adm_tdowning] NHC Pipeline" is UNPAUSED and running on a similar cadence. The GHA workflow on the repo also runs every 3h. Whether both write to the same blob simultaneously is unknown — a potential concurrency hazard.

## Inputs

- **NHC CurrentStorms.json** — `https://www.nhc.noaa.gov/CurrentStorms.json` — scraped each run; contains `activeStorms[]` with current position, intensity, pressure, and a `forecastAdvisory.url` per storm.
- **NHC Forecast Advisory HTML** — one per active storm, fetched from the URL in `forecastAdvisory.url`; plain-text `<pre>` block parsed for `FORECAST VALID`, `OUTLOOK VALID`, and `REMNANTS OF CENTER LOCATED NEAR` lines.
- **`noaa/nhc/forecasted_tracks.csv`** — existing cumulative blob file, read at the start of each run so new rows can be deduped and appended.
- **`noaa/nhc/observed_tracks.csv`** — same pattern for observed tracks.

## Steps

1. **Fetch** `CurrentStorms.json`; if `activeStorms` is empty, exit early with no writes.
2. **Parse observed tracks** — extract id, name, basin (first two chars of id), intensity, pressure, lat, lon, lastUpdate for each active storm.
3. **Parse forecasted tracks** — for each storm, fetch the Forecast Advisory HTML, extract `FORECAST VALID` / `OUTLOOK VALID` / `REMNANTS OF CENTER LOCATED NEAR` lines, convert day/time tokens to a full `validTime` datetime (month-rollover handled), parse lat/lon strings, record maxwind. One row per forecast horizon per storm.
4. **Download existing blobs** — pull current `forecasted_tracks.csv` and `observed_tracks.csv` from blob.
5. **Deduplicate and append** — `pd.concat(...).drop_duplicates()` on each dataset.
6. **Write backups** — upload pre-update versions to `noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/`.
7. **Upload merged CSVs** — overwrite `noaa/nhc/forecasted_tracks.csv` and `observed_tracks.csv`.
8. **Webhook trigger** — POST to each URL in `GH_ACTION_TRIGGER_URLS` to dispatch a GHA in `ds-aa-hti-hurricanes`.

Code refs: `nhc_forecast.py` (`NHCHurricaneForecast.get_data`, `upload_dataset`, `AzureBlobUpload`), `run.py` (`main`, `AzureBlobDownload`).

## Outputs

| artifact | path / address | format | notes |
|---|---|---|---|
| Observed tracks (cumulative) | `noaa/nhc/observed_tracks.csv` | CSV (`;` delimiter) | fields: id, name, basin, intensity, pressure, latitude, longitude, lastUpdate |
| Forecasted tracks (cumulative) | `noaa/nhc/forecasted_tracks.csv` | CSV (`;` delimiter) | fields: id, name, issuance, basin, latitude, longitude, maxwind, validTime |
| Backup — observed | `noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/observed_tracks.csv` | CSV | written each successful run before overwrite |
| Backup — forecasted | `noaa/nhc/previous/{YYYYMMDD}_{HHMMSS}/forecasted_tracks.csv` | CSV | written each successful run before overwrite |
| GHA webhook | `GH_ACTION_TRIGGER_URLS` (comma-separated) | HTTP POST | triggers `ds-aa-hti-hurricanes` main branch |

## Dependencies

- `hdx-python-api` — HDX facade used for config/retriever boilerplate; not uploading to HDX in the current flow.
- `azure-storage-blob` (raw SDK) — blob reads use a hand-rolled HMAC SharedKey auth; writes use `BlobServiceClient.from_connection_string`. This predates the team's `ocha-stratus` standard.
- `beautifulsoup4` — HTML parsing of NHC advisory pages.
- `lat-lon-parser` — converts NHC lat/lon strings (e.g. `22.9N`, `68.1W`) to numeric.
- **Secrets (GHA):** `STORAGE_ACCOUNT`, `CONTAINER`, `KEY`, `GHP`, `GH_ACTION_TRIGGER_URLS` (repo var), `HDX_SITE`, `HDX_KEY`, `PREPREFIX`, `USER_AGENT`, plus email server creds for failure notifications.

## Failure modes & debugging

- **No active storms** — exits cleanly with "No datasets were uploaded." This is expected behaviour outside hurricane season (roughly June–November Atlantic, May–November East Pacific).
- **Forecast Advisory download fails** — `DownloadError` is caught and logged as `ERROR` but the loop continues; that storm's forecast rows are silently skipped. Check logs for `"Could not download from url"`.
- **Blob upload fails** — exception is caught inside `AzureBlobUpload.upload_file` and logged as `ERROR` but not re-raised; data is silently lost. No retry logic.
- **Webhook trigger fails** — exception is caught and logged as `ERROR`; `ds-aa-hti-hurricanes` will not be triggered.
- **Concurrency hazard** — both the dev Databricks job and the GHA workflow run every 3h. If they overlap, both will read the same blob, append independently, and one overwrite will clobber the other's new rows.
- **GHA failure emails** — on job failure the workflow sends email via `dawidd6/action-send-mail`; recipients in `EMAIL_LIST` secret.
- **Logs** — GHA: Actions tab on the repo. Databricks: job run history in workspace `adb-6009046713167663`.
- **`keep-awake` branch** — exists to prevent GHA from disabling scheduled workflows on inactive repos; weekly empty commit to `keep-awake` branch tagged `[skip ci]`.

## Downstream consumers

- **`ds-aa-hti-hurricanes`** — Haiti hurricane AA framework; see KB page [`pipelines/hti-hurricanes-monitoring.md`](hti-hurricanes-monitoring.md). Its `run_check_trigger` GHA workflow is dispatched by this pipeline (one of the URLs in `GH_ACTION_TRIGGER_URLS`) on each new track. The NHC forecast blob CSVs (`noaa/nhc/forecasted_tracks.csv`, basin `al`) are the data source for its exposure/trigger analysis.

## Discrepancies

- **[conflict]** Frontmatter `source_branch: keep-awake` / `source_sha: 5295166` — the page reflects the `keep-awake` branch (the checked-out branch), which exists only to keep GHA alive via weekly empty commits; the pipeline logic lives on `main`. The deployed cadence is real but the documented branch is not where the operational code is maintained.
- **[stale]** Raw `azure-storage-blob` SDK with hand-rolled HMAC SharedKey auth instead of `ocha-stratus`; flat `noaa/nhc/` blob paths instead of the `{PROJECT_PREFIX}/{raw|processed}/{datasource}/` convention. Predates the team standard; informational, not a live error.
- **[conflict]** Named production Databricks job `Run NHC` (266763033249426) is PAUSED, while dev-namespaced `[dev adm_tdowning] NHC Pipeline` (583285176982712) is UNPAUSED and running prod cadence. The repo GHA `Run script` also runs every 3h. Two unpaused writers (dev Databricks + GHA) against the same flat blob = read-append-overwrite race; whoever writes last wins.
