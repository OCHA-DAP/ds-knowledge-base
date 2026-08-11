---
content_type: pipeline
name: hti-hurricanes-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: n/a
  jobs:
    - { name: run_check_trigger, ref: .github/workflows/run_check_trigger.yml, schedule: "event (dispatched by ds-nhc-forecast on each new track)", status: live }
    - { name: run_check_obsv_trigger, ref: .github/workflows/run_check_obsv_trigger.yml, schedule: "event (dispatched by the IMERG pipeline)", status: live }
    - { name: run_update_chirps_gefs, ref: .github/workflows/run_update_chirps_gefs.yml, schedule: "50 8 * * *", status: live }
    - { name: "HTI Hurricane Monitoring (Databricks)", ref: "586426884912849", schedule: "0 50 3,9,15,21 * * ? (03:50/09:50/15:50/21:50 UTC)", status: live }
discrepancies:
  - "[gap] A Databricks job `HTI Hurricane Monitoring` (dbx:586426884912849, unpaused, 4x/day at :50 past 03/09/15/21 UTC, git_source OCHA-DAP/ds-aa-hti-hurricanes) first appeared in the estate on 2026-08-11 (infra-drift #540; absent from the 2026-08-10 baseline). Which entrypoint it runs, on which branch, and whether it duplicates or replaces the event-driven GHA path (run_check_trigger / run_check_obsv_trigger, dispatched by ds-nhc-forecast) is NOT confirmed from the repo - needs a look at the job config in workspace adb-6009046713167663. It runs on the durable personal cluster 0515-161935-i2w5mxhc, so the registry flags it PERSONAL-CLUSTER (see infrastructure/databricks.md - Clusters)."
inputs:
  - NHC forecasts + observed tracks (basin "al")
  - CHIRPS-GEFS national-mean daily (blob)
  - IMERG national-mean (Postgres)
  - CODAB ADM0
outputs:
  - blob monitoring records (hti_fcast_monitoring.parquet, hti_obsv_monitoring.parquet)
  - email_record.csv, plots
  - emails (info/readiness/action/obsv) via AWS SES SMTP
dependencies: [Azure Blob, Azure Postgres (IMERG), AWS SES SMTP, ds-nhc-forecast (upstream), IMERG/raster-stats pipeline (upstream)]
downstream: [hti-hurricanes framework; chd-ds-aa-hti-hurricanes-app]
depends_on: [storms-pipeline, imerg]
source_repo: ocha-dap/ds-aa-hti-hurricanes   # pipeline folded into the framework repo
source_branch: melissa-exposure   # NOT main
source_sha: 731776c
code_ref:
  - pipelines/check_fcast_trigger.py
  - pipelines/check_obsv_trigger.py
  - pipelines/update_chirps_gefs.py
  - src/monitoring/monitoring_utils.py
  - src/email/
visibility: internal
last_synced: 2026-06-12
---

# Haiti hurricanes monitoring

## One-liner
Event-driven: when `ds-nhc-forecast` issues a new NHC track, check the forecast trigger (wind AND CHIRPS-GEFS rain within 230 km); the IMERG pipeline dispatches the observational check; CHIRPS-GEFS data refreshes daily. Sends staged emails (info/readiness/action/obsv). **Folded into the [hti-hurricanes framework repo](../frameworks/hti-hurricanes/2024-08-23.md)** — not a separate repo.

## Schedule / trigger
`run_check_trigger.yml` (forecast) and `run_check_obsv_trigger.yml` (obsv) are `workflow_dispatch`-only, dispatched by upstream repos (NHC ~every 6h during storms; IMERG pipeline for obs). `run_update_chirps_gefs.yml` cron `50 8 * * *` (10 min before the next NHC forecast).

**New since 2026-08-11 — a Databricks arm.** A job `HTI Hurricane Monitoring` (`dbx:586426884912849`, `git_source` `OCHA-DAP/ds-aa-hti-hurricanes`) now runs unpaused on Quartz `0 50 3,9,15,21 * * ?` — **03:50 / 09:50 / 15:50 / 21:50 UTC**, i.e. ~10 min before each NHC advisory cycle, the same offset the CHIRPS-GEFS workflow uses. It runs on the durable interactive cluster `0515-161935-i2w5mxhc`, so the registry flags it `PERSONAL-CLUSTER` ([why that's fragile](../infrastructure/databricks.md#clusters)). **What it executes, off which branch, and how it relates to the event-driven GHA checks above is unconfirmed** — the estate fingerprint sees the job, not its tasks; check the job config in workspace `adb-6009046713167663`. See [pipeline-registry.md](../infrastructure/pipeline-registry.md) for its live health.

## Inputs
NHC forecasts/observed tracks; CHIRPS-GEFS national-mean (blob); IMERG national-mean (Postgres); CODAB ADM0.

## Steps
Per new track/issue-time, evaluate readiness/action (forecast) and obsv (observed) against `THRESHS` within the 230 km gate; dedupe by `monitor_id`; write monitoring parquet; send the appropriate email.

## Outputs
`hti_fcast_monitoring.parquet` / `hti_obsv_monitoring.parquet` (one row per storm × issue-time), `email_record.csv`, plots, emails via AWS SES.

## Dependencies
Azure Blob (SAS), Azure Postgres (IMERG), AWS SES SMTP; upstream `ds-nhc-forecast` and the IMERG/raster-stats pipeline.

## Failure modes & debugging
- Idempotent back-fill: a failed step is retried next run so every forecast/obsv point is checked exactly once (`monitor_id` dedup).
- `TEST_STORM=True` fabricates a triggering row to force test emails.
- `rainfall_relevant=False` once a storm leaves the 230 km zone suppresses info emails.
- **Risk:** obsv check still depends on the "old IMERG pipeline" trigger (TODO: move to `ds-raster-stats`).

## Downstream consumers
Trigger emails → OCHA Haiti, RC/HC, CERF, WFP, UNICEF, IOM; CHD activation messages; the historical-trigger Dash app (`chd-ds-aa-hti-hurricanes-app`). Monitoring parquets consumed by exploration notebooks.
