---
content_type: pipeline
name: floodscan-ingest
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "floodscan-cogs", ref: ".github/workflows/floodscan-cog-blob.yml", schedule: "0 23 * * *", status: live }
    - { name: "slack-notification", ref: ".github/workflows/slack-notification-cogs.yml", schedule: "25 23 * * *", status: live }
    - { name: "floodscan-download (phase 1 gdrive)", ref: ".github/workflows/floodscan-ingest.yaml", schedule: "0 23 * * *", status: retired }
    - { name: "Run FloodScan (Databricks prod arm)", ref: "792911256578092", schedule: "36 0 20 * * ? (20:00 UTC)", status: live }
inputs:
  - "AER SFED 90-day rotating zip (URL via FLOODSCAN_SFED_URL secret)"
  - "AER MFED 90-day rotating zip (URL via FLOODSCAN_MFED_URL secret)"
  - "dev blob global container — raster/cogs/aer_area_300s* (gap-detection reads existing blobs)"
  - "historical .nc files: aer_sfed_area_300s_19980112_20231231_v05r01.nc and aer_mfed_area_300s_19980112_20231231_v05r01.nc (one-time run)"
outputs:
  - "dev blob global container — raster/cogs/aer_area_300s_{yyyymmdd}_v05r01.tif (daily 2-band COG: SFED band 1, MFED band 2)"
  - "Slack channel DS-Pipelines (via DS_PIPELINES_SLACK webhook secret) — daily status notification"
  - "prod blob raster container — raster/floodscan/daily/v5/processed/*.tif (SFED COGs) — written by the Databricks Run FloodScan job (792911256578092), the production arm of this pipeline; this is the path floodexposure-monitoring reads (per its depends_on: [floodscan-ingest])"
dependencies:
  - "R 4.x"
  - "terra (raster I/O + COG write)"
  - "AzureStor (blob upload)"
  - "box (R module system)"
  - "purrr, dplyr, stringr, logger, glue, readr"
  - "httr2, jsonlite (Slack + GitHub API)"
  - "DSCI_AZ_SAS_DEV (Azure blob SAS key, dev stage)"
  - "DSCI_AZ_ENDPOINT (Azure blob endpoint)"
  - "FLOODSCAN_SFED_URL (AER SFED zip download URL)"
  - "FLOODSCAN_MFED_URL (AER MFED zip download URL)"
  - "DS_PIPELINES_SLACK (Slack webhook, production channel)"
  - "DS_PIPELINES_TEST_SLACK (Slack webhook, test channel)"
  - "GH_TOKEN / GITHUB_PAT (GitHub Actions token for status queries)"
  - "GCP_CREDENTIALS (phase 1 gdrive only — no longer used in phase 2)"
downstream:
  - "pipelines/floodexposure-monitoring (reads prod SFED COGs raster/floodscan/daily/v5/processed/*.tif as input; declares depends_on: [floodscan-ingest])"
  - "apps/floodexposure-monitoring-app (chd-ds-floodexposure-monitoring Azure web app — indirectly, via the floodexposure-monitoring pipeline's DB tables)"
depends_on: []  # source pipeline — pulls the AER FloodScan feed (external), no upstream KB node
source_repo: ocha-dap/ds-floodscan-ingest
source_branch: hdx-rp-baseline
source_sha: b99cc77
code_ref:
  - src/upload_latest_cog.R
  - src/utils/blob.R
  - src/send_slack_notification.R
  - .github/workflows/floodscan-cog-blob.yml
  - .github/workflows/slack-notification-cogs.yml
  - data-raw/process_historical_nc_to_cogs.R
extra:
  pre_formalization_note: "README explicitly states this repo writes to DEV blob storage only. A formal production pipeline was planned under ds-raster-pipelines; that repo does not yet contain FloodScan. The Databricks Run FloodScan job (792911256578092, UNPAUSED, 20:00 UTC) is the presumed production path but its source repo is unknown — listed as '—' in deployments.md."
  blob_path_mismatch: "This GHA pipeline writes to dev blob raster/cogs/aer_area_300s_*. The downstream floodexposure-monitoring reads raster/floodscan/daily/v5/processed/*.tif — a different path and likely a different (production) blob. The Databricks job is the likely writer of that prod path."
  band_order_warning: "Band order (SFED/MFED) is not consistent between historical and NRT pipelines — a known bug. Downstream consumers should reference bands by name, not index."
  gap_fill: "upload_latest_cog.R implements gap detection: on each run it checks the last 90 days of blobs and backfills any missing dates from the current zip before uploading."
  active_branch_note: "Most recent commit activity is on hdx-rp-baseline (2024-11-29) which contains RP exploration notebooks; the production GHA pipeline code is on main (2024-07-23). Both branches have the same src/ pipeline code."
  SCHEMA_STRAIN: "Databricks Run FloodScan job (792911256578092) listed in deployments.md with no source repo attribution — unclear if it reads from the same AER URLs or a different source. Included in jobs[] with best available info."
visibility: internal
last_synced: "2026-06-17"
---

# floodscan-ingest

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Daily: pull AER FloodScan SFED+MFED 90-day rotating zips → extract latest date(s) → merge into 2-band COG → upload to dev Azure blob; Slack notification 25 minutes later with pass/fail status.

## Jobs & schedule

This repo runs on GitHub Actions. There is also a separate Databricks job for FloodScan that writes to the production blob path consumed by floodexposure-monitoring (source repo unknown).

| job | ref | schedule | status |
|---|---|---|---|
| floodscan-cogs | `.github/workflows/floodscan-cog-blob.yml` | `0 23 * * *` (daily 23:00 UTC) | live |
| slack-notification | `.github/workflows/slack-notification-cogs.yml` | `25 23 * * *` (daily 23:25 UTC) | live |
| floodscan-download (phase 1) | `.github/workflows/floodscan-ingest.yaml` | `0 23 * * *` | retired (gdrive-only, superseded by phase 2) |
| Run FloodScan (Databricks) | job_id `792911256578092` | `36 0 20 * * ?` (20:00 UTC) | live, UNPAUSED |

The Databricks `Run FloodScan` job is not attributed to this repo in deployments.md. It is the upstream dependency for `floodexposure-monitoring`, which reads `raster/floodscan/daily/v5/processed/*.tif` — a path this GHA pipeline does **not** write.

## Inputs

- **AER SFED zip** — 90-day rotating zip of Africa SFED GeoTIFs, one file per day. URL provided via `FLOODSCAN_SFED_URL` secret.
- **AER MFED zip** — same format for MFED. URL via `FLOODSCAN_MFED_URL`.
- **Existing blobs** — `blob.blob_date_gaps()` queries `raster/cogs/aer_area_300s*` in the dev global container to determine which dates are missing or gapped over the last 90 days. Only missing dates are downloaded/processed.
- **Historical .nc files** (one-time): `aer_sfed_area_300s_19980112_20231231_v05r01.nc` and matching MFED file, loaded from the local filesystem path in `AA_DATA_DIR_NEW`. Processed by `data-raw/process_historical_nc_to_cogs.R` — not a scheduled pipeline.

## Steps

1. **Gap detection** (`src/utils/blob.R:blob_date_gaps`): list blobs in dev global container under `raster/cogs/aer_area_300s`; identify dates missing from the last 90-day window. Logs old gaps (>90d) separately — those require manual pipeline review.
2. **Download zips**: loop over SFED and MFED; download 90-day zip to `tempdir()` using the secret URL.
3. **Selective unzip**: peek at zip contents without full extraction; unzip only files matching the needed dates.
4. **Merge bands**: read each SFED and MFED TIF as a `SpatRaster`, set band name; then per-date, stack the two rasters into a single 2-band object (`SFED` / `MFED`).
5. **Write COG**: write 2-band raster as Cloud-Optimized GeoTIFF with DEFLATE compression, sparse OK, average overview resampling.
6. **Upload**: push COG to dev blob global container at `raster/cogs/{filename}` via `AzureStor::upload_blob`. Skipped if `DRY_RUN=TRUE`.
7. **Slack notification** (separate workflow, 25 min later): query GHA API for today's scheduled run of `floodscan-cog-blob`; post success/failure + logs link to DS-Pipelines Slack channel. On failure, pings `<!channel>`.

## Outputs

- **Dev blob** `global` container: `raster/cogs/aer_area_300s_{yyyymmdd}_v05r01.tif` — one file per day, 2 bands (SFED band 1, MFED band 2). Storage account `imb0chd0dev`.
- **Slack** DS-Pipelines channel: daily status message with green/red circle + link to logs on failure.

**Important:** `floodexposure-monitoring` reads from `raster/floodscan/daily/v5/processed/*.tif`, which is a different blob path (presumably on prod storage). This GHA pipeline writes to dev storage at a different prefix. The Databricks `Run FloodScan` job (792911256578092) is the most likely writer of the production path.

## Dependencies

R 4.x runtime on `ubuntu-latest`. Key R packages: `terra`, `AzureStor`, `box`, `purrr`, `dplyr`, `stringr`, `logger`, `glue`, `httr2`, `jsonlite`. Dependency list in `.github/depends.R`.

Secrets required (GitHub Actions):
- `DSCI_AZ_SAS_DEV` — SAS key for dev blob storage
- `DSCI_AZ_ENDPOINT` — blob endpoint URL
- `FLOODSCAN_SFED_URL` / `FLOODSCAN_MFED_URL` — AER download URLs (proprietary; request from AER)
- `DS_PIPELINES_SLACK` / `DS_PIPELINES_TEST_SLACK` — Slack incoming webhook URLs
- `GH_TOKEN` / `GITHUB_PAT` — GitHub token (for Slack workflow status query)

Note: `utils_slack.R` hardcodes `DS_PIPELINES_TEST_SLACK` for both dry and live runs (a TODO comment in the code) — the production webhook may not currently be used.

## Failure modes & debugging

- **AER URL stale / rotated**: the 90-day zip URL is provided by AER and can change. If `download.file()` fails or returns an empty/unexpected zip, the GHA run fails silently or produces 0 files. Check `FLOODSCAN_SFED_URL`/`FLOODSCAN_MFED_URL` secrets are current.
- **No update available**: if `blob_date_gaps()` returns `NULL`, the script exits cleanly with "No Updates Available" — this is expected when the blob is current.
- **Old gaps logged but not filled**: dates more than 90 days old that are missing from the blob are logged as `old_gap` type but NOT backfilled (they're outside the current 90-day zip window). Manual intervention required.
- **Band order inconsistency**: the historical vs NRT pipelines iterated files differently, producing inconsistent SFED/MFED band ordering. Always reference bands by name not index when consuming these COGs.
- **Slack notification always uses test webhook**: `utils_slack.R` sends to `DS_PIPELINES_TEST_SLACK` regardless of `dry_run` flag — a known bug. Check the test channel, not the production channel, for actual status messages.
- **Logs**: GitHub Actions run logs at `https://github.com/ocha-dap/ds-floodscan-ingest/actions` — failure Slack messages include a direct link.
- **Databricks Run FloodScan (792911256578092)**: if this job fails, `floodexposure-monitoring` will not receive updated COGs at the prod path. Check Databricks workspace `adb-6009046713167663` job logs.

## Downstream consumers

- **[floodexposure-monitoring](floodexposure-monitoring.md)**: reads FloodScan COGs from blob daily at 23:15 UTC to compute population exposure. Depends on the Databricks Run FloodScan job writing to the production blob path; this GHA pipeline writes to dev.
- **[chd-ds-floodexposure-monitoring](../apps/)**: Azure web app consuming the DB tables written by floodexposure-monitoring, which in turn depends on COGs from the FloodScan ingest path.
