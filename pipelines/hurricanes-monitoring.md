---
content_type: pipeline
name: hurricanes-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor All", ref: ".github/workflows/run_monitor_all.yml", schedule: "15 */3 * * *", status: live }
    - { name: "Monitor Cuba", ref: ".github/workflows/run_monitor_cub.yml", schedule: "15 */3 * * *", status: live }
    - { name: "Keep Repo Awake", ref: ".github/workflows/keep_awake.yml", schedule: "0 12 * * 1", status: live }
inputs:
  - "blob (dev/global): noaa/nhc/forecasted_tracks.csv — NHC forecast tracks written by ds-storms-pipeline Run NHC job"
  - "blob (dev/global): noaa/nhc/observed_tracks.csv — NHC observed tracks written by ds-storms-pipeline"
  - "blob (dev/projects): ds-hurricanes-monitoring/raw/codab/<iso3>.shp.zip — CODAB boundaries per country, downloaded from FieldMaps"
  - "blob (dev/projects): ds-hurricanes-monitoring/processed/codab/combined_codab.shp.zip — combined ADM0/ADM1 boundaries for 20 Caribbean countries"
  - "blob (dev/projects): ds-hurricanes-monitoring/processed/ibtracs/all_adm_wind_stats.parquet — historical wind speed return periods per ADM pcode"
  - "blob (dev/projects): ds-hurricanes-monitoring/processed/ibtracs/sid_name.parquet — IBTrACS storm sid → name lookup"
  - "blob (dev/projects): ds-hurricanes-monitoring/processed/ibtracs/havana_wind_stats.parquet — historical wind vs distance stats for Cuba scatter plot"
  - "blob (dev/projects): ds-hurricanes-monitoring/email/distribution_list.csv — email recipients (to/cc columns per geography)"
  - "blob (dev/projects): ds-hurricanes-monitoring/email/test_distribution_list.csv — test distribution list (used when TEST_LIST != False)"
outputs:
  - "blob (dev/projects): ds-hurricanes-monitoring/monitoring/all_fcast_monitoring.parquet — per-forecast, per-ADM monitoring records for all Caribbean"
  - "blob (dev/projects): ds-hurricanes-monitoring/monitoring/cub_fcast_monitoring.parquet — per-forecast monitoring records for Cuba (Havana ADM1)"
  - "blob (dev/projects): ds-hurricanes-monitoring/plots/fcast/<monitor_id>_{all|cub}_{map|scatter}.png — map and scatter plots attached to emails"
  - "blob (dev/projects): ds-hurricanes-monitoring/email/email_record.csv — deduplication log of sent emails"
  - "email (AWS SMTP): informational alerts to distribution list when storm passes proximity threshold (Cuba: 1000 km; all Caribbean: 250 km)"
dependencies:
  - "azure-storage-blob (raw Azure SDK — NOT ocha-stratus; uses SAS tokens via DSCI_AZ_BLOB_DEV_SAS_WRITE secret)"
  - "geopandas, shapely, rioxarray, xarray"
  - "plotly + kaleido (map PNGs), matplotlib (scatter PNGs)"
  - "Jinja2 (email HTML templates in src/email/templates/)"
  - "AWS SMTP (not Listmonk/ocha-relay): secrets DSCI_AWS_EMAIL_HOST, DSCI_AWS_EMAIL_USERNAME, DSCI_AWS_EMAIL_PASSWORD, DSCI_AWS_EMAIL_ADDRESS"
  - "GHA repo vars: TEST_LIST, TEST_STORM, EMAIL_DISCLAIMER"
  - "upstream: ds-storms-pipeline NHC job populates the NHC CSVs in the dev global container — see discrepancies re: which job_id"
downstream:
  - "apps/hti-hurricanes-app.md (chd-ds-aa-hti-hurricanes-app, Azure webapp, repo ds-aa-hti-hurricanes-app) — consumes monitoring parquets and plots for display"
  - "frameworks/cub-hurricanes — Cuba proximity emails feed the readiness/action trigger workflow for the Cuba hurricane AA pilot"
related:
  - "pipelines/storms-pipeline.md — upstream; its NHC job writes the forecast/observed track CSVs this pipeline reads"
  - "frameworks/hti-hurricanes — Haiti hurricane AA framework (Caribbean 'all' scope context)"
discrepancies:
  - "[conflict] run_monitor_cub.yml passes env secrets DEV_BLOB_SAS and CHD_DS_HOST/PORT/EMAIL_USERNAME/PASSWORD/ADDRESS, but the code (src/utils/blob.py, src/email/utils.py) reads DSCI_AZ_BLOB_DEV_SAS_WRITE and DSCI_AWS_EMAIL_HOST/USERNAME/PASSWORD/ADDRESS. The Cuba workflow's secret names do not match what the code consumes, so its blob/email env would resolve to None at runtime unless those secrets are also defined. Monitor All passes the correct names. Needs reconciliation."
  - "[gap] Upstream NHC job ambiguity: deployments.md has TWO NHC jobs — 266763033249426 'Run NHC' (PAUSED) and 583285176982712 '[dev adm_tdowning] NHC Pipeline' (UNPAUSED). This pipeline reads the DEV global container, which the UNPAUSED dev-slot job most plausibly feeds; the paused 'Run NHC' is likely the prod-slot job. The 'no new storms because upstream is paused' failure note assumes the paused job is the live feeder — verify which job actually writes noaa/nhc/*.csv to imb0chd0dev before acting on it."
  - "[stale] source_branch is melissa-analysis (last commit 2025-11-04), ahead of main (2025-10-28). The GHA workflows checkout the default branch (no ref: pin on monitoring workflows), so the deployed monitoring code runs from main, NOT the checked-out melissa-analysis branch this page reflects."
source_repo: OCHA-DAP/ds-hurricanes-monitoring
source_branch: melissa-analysis
source_sha: eefb9bf
code_ref:
  - pipelines/monitor_all.py
  - pipelines/monitor_cub.py
  - src/monitoring/monitoring_utils.py
  - src/email/send_emails.py
  - src/email/update_emails.py
  - src/email/plotting.py
  - src/utils/blob.py
  - src/datasources/nhc.py
  - src/datasources/ibtracs.py
  - src/datasources/codab.py
extra:
  geographies: "Two monitoring scopes run in parallel: 'all' (20 Caribbean countries, ADM0/ADM1 mix, 250 km email threshold) and 'cub' (Havana ADM1 only, 1000 km threshold, also generates scatter plot)"
  email_mechanism: "Direct AWS SMTP via smtplib — NOT ocha-relay/Listmonk. Distribution list is a CSV on blob, not a Listmonk list."
  blob_auth: "Uses raw Azure SDK ContainerClient with SAS tokens (DSCI_AZ_BLOB_DEV_SAS_WRITE). Does NOT use ocha-stratus — this is a known deviation from team convention."
  blob_stage: "All writes go to the 'dev' stage blob (imb0chd0dev). No prod-stage writes. The 'global' container is read-only (nhc/ and ibtracs/)."
  deduplication: "Both monitoring and email sending are idempotent — monitor_id and email_record.csv prevent re-processing and re-sending for the same forecast issuance."
  wind_model: "Uses Vickery & Wadhera (2008) parametric wind model to estimate wind at ADM centroid distance from storm track. Return periods estimated from IBTrACS 2010+ NA basin."
  keep_awake: "keep_awake.yml makes empty weekly commits to the keep-awake branch — GitHub Actions free tier disables scheduled workflows on inactive repos after 60 days."
visibility: internal
last_synced: 2026-06-17
---

# Hurricanes Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Every 3 hours: pull NHC forecast tracks from blob → compute closest approach and estimated wind for each Caribbean ADM → email distribution list when a storm passes proximity threshold.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor All | `.github/workflows/run_monitor_all.yml` | every 3 hours at :15 (`15 */3 * * *`) | live |
| Monitor Cuba | `.github/workflows/run_monitor_cub.yml` | every 3 hours at :15 (`15 */3 * * *`) | live |
| Keep Repo Awake | `.github/workflows/keep_awake.yml` | Mondays 12:00 UTC | live |

Both monitoring workflows trigger on schedule and `workflow_dispatch`. They are independent and run concurrently. The "all" workflow covers all 20 Caribbean countries (ADM0/ADM1 mix); the "cub" workflow covers Havana ADM1 only with a wider proximity threshold and an additional scatter plot.

**Not in deployments.md** — this pipeline runs entirely on GitHub Actions; there is no Databricks job or Azure webapp for the pipeline itself. The downstream app `chd-ds-aa-hti-hurricanes-app` (repo `ds-aa-hti-hurricanes-app`) is in deployments.md (Running).

**Deployed branch ≠ this page's branch.** This page reflects `melissa-analysis` (latest commit, 2025-11-04). The monitoring workflows do **not** pin a `ref:`, so `actions/checkout` takes the repo default branch (`main`, 2025-10-28) at runtime — the live monitoring code is whatever is on `main`, not `melissa-analysis`. (Only `keep_awake.yml` pins `ref: keep-awake`.)

**Cuba workflow secret mismatch.** `run_monitor_cub.yml` exports `DEV_BLOB_SAS` and `CHD_DS_HOST/PORT/EMAIL_*` as env, but the code reads `DSCI_AZ_BLOB_DEV_SAS_WRITE` and `DSCI_AWS_EMAIL_*` (same as Monitor All). The Cuba job's env names don't match what the code consumes — see Discrepancies/Failure modes.

## Inputs

- **NHC forecast tracks** (`global` container dev, `noaa/nhc/forecasted_tracks.csv`): semicolon-delimited CSV written by an `ds-storms-pipeline` NHC Databricks job. **Which job is ambiguous** — deployments.md lists both `266763033249426` "Run NHC" (PAUSED) and `583285176982712` "[dev adm_tdowning] NHC Pipeline" (UNPAUSED); since this pipeline reads the *dev* blob, the UNPAUSED dev-slot job is the likely feeder (see Discrepancies). Fields include `issuance`, `validTime`, `id` (ATCF ID), `basin`, `latitude`, `longitude`, `maxwind`.
- **NHC observed tracks** (`global` container dev, `noaa/nhc/observed_tracks.csv`): same pipeline, observed track variant.
- **CODAB boundaries** (`projects` container dev, `ds-hurricanes-monitoring/raw/codab/<iso3>.shp.zip`): per-country admin boundaries downloaded from FieldMaps. 20 countries in `ISO3S`; Cuba, Bahamas, Honduras, Guatemala, Nicaragua, Costa Rica, and Panama use ADM1; the rest use ADM0.
- **Combined CODAB** (`projects` dev, `ds-hurricanes-monitoring/processed/codab/combined_codab.shp.zip`): pre-merged GeoDataFrame with unified `ADM_PCODE` and `ADM_NAME` columns.
- **IBTrACS wind stats** (`projects` dev, `ds-hurricanes-monitoring/processed/ibtracs/all_adm_wind_stats.parquet`): historical max wind per storm per pcode, used to estimate return period for forecast winds.
- **IBTrACS sid/name lookup** and **Havana wind stats**: supporting blobs for email content generation.
- **Distribution list** (`projects` dev, `ds-hurricanes-monitoring/email/distribution_list.csv`): columns `name`, `email`, `all` (to/cc/null), `cub` (to/cc/null).
- **Email record** (`projects` dev, `ds-hurricanes-monitoring/email/email_record.csv`): existing sent-email log for deduplication.

## Steps

1. **`monitoring_utils.update_fcast_monitoring`** — loads NHC forecast CSV; for each forecast issuance × ATCF ID combination not already in the existing monitoring parquet, resamples the track to 30-minute intervals, computes distance from each ADM centroid (EPSG:3857), and estimates wind at that distance using the Vickery & Wadhera parametric model. Records `min_dist`, `closest_s`, `time_to_closest`, `max_adm_wind`, `time_to_maxwind`. Appends new rows and uploads the parquet.
2. **`plotting.update_plots`** — for each monitoring record (or grouped `email_monitor_id` for "all"), generates PNG plots if not already on blob:
   - *Cuba*: map (Plotly/OpenStreetMap) + scatter (matplotlib wind-vs-distance comparison against historical storms)
   - *All*: map only
3. **`update_emails.update_fcast_info_emails`** — filters monitoring records by distance threshold (Cuba: 1000 km, all: 250 km); skips monitor IDs already in the email record; calls `send_info_email` which renders a Jinja2 HTML template and sends via AWS SMTP. Appends sent entries to `email_record.csv`.

## Outputs

- **Monitoring parquets**: `ds-hurricanes-monitoring/monitoring/{all,cub}_fcast_monitoring.parquet` — append-only records of every forecast issuance × ADM combination processed. Core columns: `monitor_id`, `atcf_id`, `ADM_PCODE`, `name`, `issue_time`, `min_dist`, `closest_s`, `max_adm_wind`, `adm_wind_rp`.
- **Plot PNGs**: `ds-hurricanes-monitoring/plots/fcast/<monitor_id>_{all,cub}_{map,scatter}.png` — embedded in emails and consumed by the HTI app.
- **Email record**: `ds-hurricanes-monitoring/email/email_record.csv` — deduplication log.
- **Emails**: HTML/text multipart messages sent via AWS SMTP to the distribution list. Subject lines: `Hurricane Monitoring [Caribbean]: <name> forecast issued <time>` (all) and `Hurricane Monitoring [Havana]: <name> ...` (Cuba).

## Dependencies

- **Raw Azure SDK** (`azure-storage-blob`): all blob I/O uses `ContainerClient` with SAS tokens — **not ocha-stratus**. Code (`src/utils/blob.py`) reads `DSCI_AZ_BLOB_DEV_SAS_WRITE`. NOTE: `run_monitor_cub.yml` instead passes `DEV_BLOB_SAS` — a name the code does not read (see Discrepancies).
- **AWS SMTP**: direct `smtplib.SMTP_SSL` on port 465 — **not ocha-relay/Listmonk**. Code (`src/email/utils.py`) reads `DSCI_AWS_EMAIL_HOST/USERNAME/PASSWORD/ADDRESS`. NOTE: `run_monitor_cub.yml` passes `CHD_DS_HOST/PORT/EMAIL_*` instead — names the code does not read (see Discrepancies).
- **GHA repo vars**: `TEST_LIST` (bool, default True = use test list), `TEST_STORM` (bool, default True = inject test row), `EMAIL_DISCLAIMER`.
- **Plotting**: `plotly` + `kaleido` for map PNGs; `matplotlib` for scatter PNGs.
- **Upstream dependency**: an `ds-storms-pipeline` NHC Databricks job must populate `noaa/nhc/forecasted_tracks.csv` before this pipeline runs. deployments.md has two NHC jobs (`266763033249426` "Run NHC" PAUSED; `583285176982712` "[dev adm_tdowning] NHC Pipeline" UNPAUSED). This pipeline reads the **dev** blob, so the UNPAUSED dev-slot job is the likely feeder. Confirm which one actually writes the dev `noaa/nhc/*.csv` before concluding the feed is stale (see Discrepancies).

## Failure modes & debugging

**No emails sent / stale monitoring**: most likely cause is the upstream NHC Databricks job not writing fresh CSVs. Check the `forecasted_tracks.csv` last-modified timestamp on the dev blob. First confirm *which* NHC job feeds the dev blob — `266763033249426` "Run NHC" is PAUSED but `583285176982712` "[dev adm_tdowning] NHC Pipeline" is UNPAUSED. Re-enable the relevant one in Databricks workspace `adb-6009046713167663`.

**Cuba emails / blob silently failing**: `run_monitor_cub.yml` passes env names (`DEV_BLOB_SAS`, `CHD_DS_EMAIL_*`) that the code does not read; the code expects `DSCI_AZ_BLOB_DEV_SAS_WRITE` and `DSCI_AWS_EMAIL_*`. If those `DSCI_*` secrets aren't also present in the repo, the Cuba job's blob/SMTP credentials resolve to `None`. Reconcile the workflow env block with `src/utils/blob.py` and `src/email/utils.py`.

**Email sent repeatedly / duplicates**: check `email_record.csv` on blob — if it can't be loaded (e.g. malformed or missing), `update_emails` falls back to an empty DataFrame and re-sends everything in range. The exception is caught and printed, not raised; watch GHA logs for "could not load email record".

**Plot PNG missing in email**: `send_all_info_email` catches `ResourceNotFoundError` for map blobs and skips them. The email still sends but without the map image. Check blob for `plots/fcast/<monitor_id>_all_map.png`; run `plotting.create_plot` manually.

**GHA workflow disabled**: GitHub disables scheduled workflows after 60 days of repo inactivity. The `keep_awake.yml` workflow (weekly empty commit to `keep-awake` branch) prevents this, but if it also stops running the monitoring workflows will silently cease.

**TEST_STORM/TEST_LIST defaults**: unless explicitly set to `"False"` in GHA repo vars, `TEST_STORM` and `TEST_LIST` default to `True`. In production, both must be set to `"False"` in the repo's Variables settings.

**Blob auth**: uses SAS token `DSCI_AZ_BLOB_DEV_SAS_WRITE`. If the token expires or is rotated, all blob reads and writes fail. This is a single token for both read and write to the `dev` stage.

**Logs**: GHA run logs at `https://github.com/OCHA-DAP/ds-hurricanes-monitoring/actions` — the "Run script" step output contains per-monitor_id progress prints.

## Downstream consumers

- **[hti-hurricanes-app](../apps/hti-hurricanes-app.md)** — Azure webapp `chd-ds-aa-hti-hurricanes-app` (repo `ds-aa-hti-hurricanes-app`, Running in deployments.md), [live](https://chd-ds-aa-hti-hurricanes-app.azurewebsites.net). Reads the monitoring parquets and plot PNGs from blob to power the interactive display.
- **[cub-hurricanes framework](../frameworks/cub-hurricanes/)** — the Cuba proximity email feeds the readiness/action trigger monitoring workflow for the Cuba hurricane AA pilot.

**Upstream / related:** [storms-pipeline](storms-pipeline.md) (NHC track CSVs), [hti-hurricanes framework](../frameworks/hti-hurricanes/) (Caribbean "all" scope context).
