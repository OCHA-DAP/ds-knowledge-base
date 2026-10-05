---
content_type: pipeline
name: cub-hurricanes-monitoring
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group:   # n/a — Databricks workspace adb-6009046713167663; creds from the Job Compute policy + `dsci` secret scope
  jobs:
    - { name: "Cuba Hurricane Forecast Monitor (DAB fcast_monitor)", ref: "dbx:527252598381643", schedule: "event — run_job_task from storms-pipeline nhc_pipeline (no own cron)", status: live }
    - { name: "Cuba Hurricane Observational Monitor (DAB obsv_monitor)", ref: "dbx:759011249647664", schedule: "0 15 17 * * ? (UTC, daily)", status: live }
    - { name: "Daily Hurricane Report (GHA)", ref: ".github/workflows/daily-hurricane-report.yml", schedule: "cron 0 6 * * * (+ dispatch, push to main)", status: live }
    - { name: "Keep Repo Awake (GHA)", ref: ".github/workflows/keep_awake.yml", schedule: "cron 0 12 * * 1", status: live }
    - { name: "chirps-gefs-test", ref: "dbx:402939227068071", schedule: "on-demand (not in databricks.yml)", status: paused }
    - { name: "Forecast Monitor (GHA, retired)", ref: ".github/workflows/01_run_forecast_data_ingestion.yml", schedule: "cron 30 3,9,15,21 * * * — workflow disabled", status: retired }
    - { name: "Observational Monitor (GHA, retired)", ref: ".github/workflows/02_run_observational_data_ingestion.yml", schedule: "cron 15 17 * * * — workflow disabled", status: retired }
    - { name: "Download recent CHIRPS-GEFS (GHA)", ref: ".github/workflows/run_update_chirps_gefs.yml", schedule: "cron 50 8 * * * — workflow disabled", status: retired }
    - { name: "Check forecast / observational trigger (GHA)", ref: ".github/workflows/run_check_trigger.yml, run_check_obsv_trigger.yml", schedule: "workflow_dispatch (never run; target scripts absent)", status: retired }
inputs:
  - "NHC forecast + observed tracks — Postgres prod `storms.nhc_tracks_geo` joined to `storms.nhc_storms` (current Atlantic season; leadtime>0 = fcast, leadtime=0 = obsv), written by storms-pipeline"
  - "IMERG rainfall — prod DB `public.imerg` (pcode CU) and IMERG rasters in blob container `raster` (prod stage)"
  - "Cuba COD-AB ADM0 — blob ds-aa-cub-hurricanes/raw/codab/cub.shp.zip (dev stage; originally data.fieldmaps.io)"
  - "ZMA (coastal zone) polygons — src/datasources/zma.py"
  - "Listmonk lists tagged ds-aa-cub-hurricanes: `cub:info` (Cuba Hurricanes - Info), `cub:trigger` (Cuba Hurricanes - Trigger), `cub:test` ([TEST] Cuba Hurricanes)"
  - "Sent-email record — blob ds-aa-cub-hurricanes/email/email_record.csv (test_email_record.csv when TEST_EMAIL=true)"
  - "Daily report: distribution list blob ds-aa-cub-hurricanes/email/distribution_list.csv (rows with `daily_summary`); NHC Tropical Weather Outlook image scraped from nhc.noaa.gov/gtwo.php"
outputs:
  - "blob ds-aa-cub-hurricanes/monitoring/<season>/cub_fcast_monitoring.parquet"
  - "blob ds-aa-cub-hurricanes/monitoring/<season>/cub_obsv_monitoring.parquet"
  - "blob ds-aa-cub-hurricanes/plots/<year>/<fcast|obsv>/<monitor_id>_<map|scatter>.png (uploaded to the Listmonk media library for emails)"
  - "blob ds-aa-cub-hurricanes/email/email_record.csv (appended on send)"
  - "Listmonk campaigns (bilingual ES/EN; informational / readiness / action / observational) to the Cuba info + trigger lists"
  - "Daily Hurricane Report email (Quarto-rendered Report.qmd, sent by SMTP / AWS SES)"
surfaces: []   # the analysis book + trigger app are declared on frameworks/cub-hurricanes/2026-06-17.md
dependencies:
  - "ocha-stratus==0.1.2 (blob + Postgres access)"
  - "ocha-relay v0.3.0 (Listmonk campaigns; git tag)"
  - "Listmonk sender creds DSCI_LISTMONK_BASE_URL / _API_USERNAME / _API_KEY (dsci secret scope, set in databricks.yml spark_env_vars)"
  - "Databricks 'Job Compute' cluster policy 000C79D951EAF0D6 — injects DSCI_AZ_* DB/blob + IMERG_* creds; ephemeral driver+1 worker, DBR 18.2"
  - "runtime flags: DRY_RUN, TEST_EMAIL, FORCE_ALERT, EMAIL_BACKEND (listmonk default | humdata_email SMTP escape hatch)"
  - "Daily report (GHA): DSCI_AZ_BLOB_*_SAS + DSCI_AWS_EMAIL_* secrets, Quarto, Python 3.11"
downstream:
  - "Cuba hurricanes AA framework — live trigger monitoring + trigger emails (frameworks/cub-hurricanes)"
  - "Daily Hurricane Report email recipients"
depends_on:
  - storms-pipeline
  - storms.nhc_tracks_geo
  - storms.nhc_storms
  - imerg
  - public.imerg
  - listmonk
  - dbx-job-compute
source_repo: ocha-dap/ds-aa-cub-hurricanes
source_branch: main
source_sha: 7ce61f5
code_ref:
  - databricks.yml
  - databricks/run_monitor_job.py
  - databricks/README.md
  - pipelines/01_update_fcast_monitor.py
  - pipelines/02_update_obsv_monitor.py
  - pipelines/email_with_embedded_images.py
  - pipelines/setup_cub_listmonk_lists.py
  - src/monitoring/monitoring_utils.py
  - src/datasources/nhc.py
  - src/email/backends.py
  - src/email/listmonk_emails.py
  - src/email/update_emails.py
  - src/constants.py
  - docs/decisions/
  - .github/workflows/
extra: {}
visibility: public
last_synced: 2026-10-05
---

# Cuba Hurricanes Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner
Event-driven (forecast, after each new NHC advisory lands) + daily 17:15 UTC (observed): read NHC tracks from `storms.*` and IMERG rainfall → test each storm against the Cuba hurricane AA triggers → upsert the season's monitoring parquet, render map/scatter plots → send bilingual informational / readiness / action / observational campaigns via Listmonk. A separate GHA job emails a daily Quarto status report at 06:00 UTC.

## Jobs & schedule
Production is the Databricks Asset Bundle `ds-aa-cub-hurricanes` (`databricks.yml`, prod target, run-as `adm.zarno1`), **live since 2026-06-30** per `databricks/README.md`. The jobs run from `source: GIT` at `main`, so pushing to `main` changes the next run; only config changes need `bundle deploy`. The `dev` target is deployed only on demand for feature branches; it auto-pauses the schedule and uses the test list.

| job | ref | schedule | status |
|---|---|---|---|
| Cuba Hurricane Forecast Monitor (`fcast_monitor`) | `dbx:527252598381643` | no cron: kicked by the `trigger_cuba_forecast` task of [storms-pipeline](storms-pipeline.md)'s `nhc_pipeline`, once per new advisory (registry shows "manual") | live |
| Cuba Hurricane Observational Monitor (`obsv_monitor`) | `dbx:759011249647664` | `0 15 17 * * ?` UTC | live |
| Daily Hurricane Report (GHA) | `daily-hurricane-report.yml` | cron `0 6 * * *` + dispatch + push to `main` | live (succeeding daily, Oct 2026) |
| Keep Repo Awake (GHA) | `keep_awake.yml` | Mon 12:00 UTC | live. Pushes an empty commit to the `keep-awake` branch so GitHub doesn't disable the scheduled workflows |
| chirps-gefs-test | `dbx:402939227068071` | manual | not in the bundle; never run in the registry window |
| Forecast / Observational Monitor (GHA) | `01_…`, `02_…_data_ingestion.yml` | crons still in the YAML | **retired**: workflows `disabled_manually`. Not a fallback: GitHub has no Listmonk creds, so re-enabling them would fail rather than send |
| Download recent CHIRPS-GEFS (GHA) | `run_update_chirps_gefs.yml` | cron `50 8 * * *` | retired: disabled; `pipelines/update_chirps_gefs.py` no longer exists |
| Check forecast / obsv trigger (GHA) | `run_check_trigger.yml`, `run_check_obsv_trigger.yml` | dispatch | dead: still "active" in GitHub but never run, and their scripts are absent |

## Inputs
See `inputs`. NHC tracks come from Postgres **prod** `storms.nhc_tracks_geo` + `storms.nhc_storms`, written by [storms-pipeline](storms-pipeline.md). These are no longer the blob CSVs from [nhc-forecast](nhc-forecast.md). Rainfall comes from [imerg](imerg.md) (`public.imerg`, pcode `CU`, plus prod rasters). Cuba ADM0 is from COD-AB. Recipients are the Listmonk lists; the send record is a CSV in blob.

## Steps
1. `databricks/run_monitor_job.py` (the DBX wrapper) sets `EMAIL_BACKEND=listmonk`, `DRY_RUN`/`TEST_EMAIL`/`FORCE_ALERT` from job params, and `LISTMONK_SKIP_CONFIRMATION=true`. It copies `src/` and `pipelines/` to `/local_disk0` (imports off the wsfs mount are unreliable) and shells out to the monitor script.
2. `pipelines/01_update_fcast_monitor.py`: `create_cuba_hurricane_monitor(rainfall_source="raster")` → `update_monitoring("fcast")`. This interpolates the forecast tracks, filters them by distance to Cuba / ZMA and by lead time, evaluates the wind and rainfall triggers, and writes `monitoring/<season>/cub_fcast_monitoring.parquet`. Next comes trigger emails → `plotting.update_plots("fcast")` → info emails.
3. `pipelines/02_update_obsv_monitor.py` does the same for observed tracks (`obsv`) and sends the observational trigger emails.
4. Dispatch: `src/email/backends.py` selects `listmonk_emails` (an ocha-relay campaign to the list resolved by tag, with plots uploaded to the Listmonk media library) or the legacy `send_emails` (humdata.org via AWS SES). The switch is manual; there is no failover.
5. Dedup: an email is skipped if it's already in `email_record.csv`. `MONITORING_START_DATE` = 2025-01-01 (Cuba tz).
6. Daily report (GHA): renders `Report.qmd` with Quarto, then `pipelines/email_with_embedded_images.py` sends it by SMTP to the `daily_summary` rows of the distribution CSV.

## Outputs
See `outputs`. This repo writes nothing to Postgres. Monitoring parquets and plots are partitioned by season/year.

## Dependencies
See `dependencies`. ADRs in `docs/decisions/`: 0001 (DBX on ephemeral clusters), 0002 (fcast triggered by the upstream job), 0003 (Listmonk as the default backend) and 0004 (unsubscribe suppressed via a subscriber attribute). Mixed data plane: tracks and IMERG come from **prod** (DB/rasters); COD-AB and the project blobs use the stratus default (dev) stage.

## Failure modes & debugging
- **A bare `bundle run` sends for real.** Prod is the default target with `test_email=False`. For a safe check, use `--params dry_run=True,test_email=True`.
- **Verify from task logs, not the CLI exit code.** `bundle run` can exit 0 while the task failed. The wrapper prints a `[run_monitor_job] …` header and `OK`, and raises on a non-zero child exit (a top-level `sys.exit` would be treated as a task failure).
- **Forecast monitor didn't run.** It has no schedule. Check that storms-pipeline `nhc_pipeline` ran and that its `trigger_cuba_forecast` task fired. That task is fire-and-forget, so an upstream failure never shows on the NHC run. The trigger identity needs `CAN_MANAGE_RUN` on the job (granted to the `dsci` group).
- **Slow start is normal.** Expect ~15–20 min per run before monitor logic starts (library install on a fresh policy cluster).
- **Listmonk down.** Between 2026-09-22 and 09-25 the wrapper was switched to `humdata_email` with `HUMDATA_RECIPIENTS_OVERRIDE`. To fall back, run with `EMAIL_BACKEND=humdata_email` where the `DSCI_AWS_EMAIL_*` creds exist. Don't re-enable the GHA monitors.
- **Audience changes.** Re-populate Listmonk lists via `pipelines/setup_cub_listmonk_lists.py`. The import is additive, so clear the lists first to replace the audience.
- **Registry history.** The Observational Monitor was failing every run in the 2026-06-22 snapshot (`deployments.md`). Both monitors are 🟢 in the 2026-10-05 [pipeline registry](../infrastructure/pipeline-registry.md).
- **Missing blobs.** A missing monitoring parquet is treated as empty, so everything for the season is re-processed. A missing email record starts empty, which could cause resends.
- <!-- TODO: [gap] daily-hurricane-report.yml passes no DSCI_AZ_DB_* secrets, yet Report.qmd loads NHC tracks via nhc.load_recent_glb_nhc() from Postgres prod; the workflow still reports success — confirm the emailed report's storm section isn't silently empty/erroring. -->
- **[stale] docstrings.** In `src/datasources/nhc.py`, `load_recent_glb_forecasts`/`_obsv` say "dev database", but the code queries `stratus.get_engine("prod")`.

## Downstream consumers
[frameworks/cub-hurricanes](../frameworks/cub-hurricanes/README.md). This is the framework's live trigger monitor and notification channel. Per `databricks/README.md` the real audience is ~50 info and ~29 trigger recipients.
