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
    - { name: "HTI DGPC Rainfall Analysis (Databricks)", ref: "700734159677972", schedule: "manual (no cron) - analysis backfill, not a monitor", status: live }
discrepancies:
  - "[gap] The Databricks job `HTI Hurricane Monitoring` (dbx:586426884912849) first appeared in the estate on 2026-08-11 (infra-drift #540). Its config is now sourced from `databricks.yml` on `main`, but whether it duplicates or replaces the event-driven GHA path (run_check_trigger / run_check_obsv_trigger, dispatched by ds-nhc-forecast) is still NOT confirmed - the two arms are described separately in the repo and nothing marks the GHA workflows as retired."
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

**New since 2026-08-11 — a Databricks arm.** A job `HTI Hurricane Monitoring` (`dbx:586426884912849`, `git_source` `OCHA-DAP/ds-aa-hti-hurricanes`) runs unpaused on Quartz `0 50 3,9,15,21 * * ?` — **03:50 / 09:50 / 15:50 / 21:50 UTC**, i.e. after each cycle's `ds-storms-pipeline` `:00`/`:30` run has landed the advisory's tracks/exposure/WSP (advisories not yet in the DB are deferred to the next run). It is a **DAB job** defined in `databricks.yml` on `main` (bundle `ds-aa-hti-hurricanes`, resource `hti_monitoring`): task `run_monitoring` → `databricks/run_monitor_job.py` → `pipelines/monitor.py`, cloned from the repo at `${var.git_branch}` (default `main`). Job parameters `test_email` / `dry_run`; the `prod` target sets `test_email=False`, i.e. **live to the AA Haïti Listmonk lists (116 info / 117 déclencheurs) since 2026-08-11**. Exposure/WSP inputs come from the **dev** storms DB, rain from CHIRPS-GEFS (blob) + IMERG (prod DB). `adm.zarno1` holds `CAN_MANAGE` (job-level, covering Aug 2026 leave). **How this relates to the event-driven GHA checks above is still unconfirmed** — nothing in the repo marks `run_check_trigger` / `run_check_obsv_trigger` as retired. See [pipeline-registry.md](../infrastructure/pipeline-registry.md) for its live health.

**Compute: ephemeral Job Compute, not the personal cluster** (corrected 2026-08-27). Both jobs use a `job_clusters` block under the team **Job Compute policy `000C79D951EAF0D6`** (`Standard_DS4_v2`, `num_workers: 1`, spot-with-fallback) — the policy injects the `DSCI_AZ_*` / `IMERG_*` creds, so anyone with `CAN_MANAGE` can operate the job without permissions on someone's personal cluster. The monitor was briefly pinned to the durable interactive cluster `0515-161935-i2w5mxhc` and flagged `PERSONAL-CLUSTER` ([why that's fragile](../infrastructure/databricks.md#clusters)); the estate fingerprint shows it moved to Job Compute between **2026-08-12 and 2026-08-15**, and the flag no longer fires.

**Manual sibling — `HTI DGPC Rainfall Analysis`** (`dbx:700734159677972`, bundle resource `dgpc_rain`, new in the estate on **2026-08-27**, [infra-drift #573](https://github.com/OCHA-DAP/ds-knowledge-base/issues/573)). **Not a monitor** — a one-off/manual analysis backfill that evaluates the **DGPC rainfall criteria against IMERG half-hourly for every storm in the Haiti set** (task `run_dgpc_rain` → `databricks/run_dgpc_rain_job.py` → `pipelines/run_dgpc_rain.py`; `src/dgpc/rain_analysis.py`). Scoped by the `dgpc_storms` parameter (`""` = all 42 storms, else e.g. `AL142016 AL132025`); `timeout_seconds: 21600`. It exists as a Databricks job **only because the Earthdata credentials live in the `dsci` secret scope** and are injected by the compute policy as `IMERG_USERNAME` / `IMERG_PASSWORD` (the same pair `Run IMERG` uses) — ~14 000 OPeNDAP granule fetches, and nobody has to hold the password locally. Feeds the DGPC-validation strand of the [in-development redesign](../frameworks/hti-hurricanes/2026-06-09.md), not the live trigger path.

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
