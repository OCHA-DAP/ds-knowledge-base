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
