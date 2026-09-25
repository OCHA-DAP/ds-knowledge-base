---
content_type: pipeline
name: tcd-flooding-monitoring
type: monitoring
status: live
deployment:
  platform: databricks
  resource_group: null
  jobs:
    - { name: "TCD Flood Monitoring (bundle tcd_flood_monitoring)", ref: "dbx:496653473007283", schedule: "0 0 20 * * ? (daily 20:00 UTC)", status: live }
    - { name: "Monitor flooding (legacy GHA)", ref: ".github/workflows/monitoring.yml", schedule: "workflow_dispatch only since 2026-09-24 (cron removed by #20)", status: retired }
inputs:
  - "CDS/EWDS cems-glofas-forecast (operational ensemble perturbed forecasts, leads 1-14 d) at the N'Djamena station on the Chari"
outputs:
  - "DB projects.pa_aa_tcd_flooding_monitoring (DEV — data_stage=dev; per-run ensemble-mean forecast rows)"
  - "blob projects/pa-aa-tcd-flooding/monitoring/{date}_{activated}.png (DEV; the chart embedded in the informational email)"
  - "Emails — TEMPORARY since 2026-09-25: direct SES/SMTP (EMAIL_BACKEND=ses, src/ses_mail.py) to Tristan, Zack, Leonardo, Hannah (test_email=true -> Tristan only), informational email EVERY DAY (ALWAYS_EMAIL=true); readiness/action emails on activation. Listmonk (code default) is down with the dev DB: lists info 111 / trigger 112 / test 5"
dependencies:
  - "ocha-stratus, cfgrib/eccodes (GRIB decoding), ocha-relay (Listmonk client, unused while EMAIL_BACKEND=ses)"
  - "job params (bundle prod target): stage=prod (real recipients), data_stage=dev (DB/blob plane over the dev private endpoint; dsci secret DSCI_AZ_DB_DEV_HOST = private IP), email_backend=ses, always_email=true, test_email=false; SES creds DSCI_AWS_EMAIL_* via spark_env_vars; CDSAPI_URL overridden to EWDS in the wrapper (the compute policy fixes it to plain CDS)"
downstream:
  - "The four named recipients (SES); Listmonk info/trigger lists once Listmonk is back"
depends_on: [listmonk]
source_repo: ocha-dap/pa-aa-tcd-flooding
source_branch: main
source_sha: main@2026-09-25 (post #21)
code_ref:
  - databricks.yml
  - databricks/run_task.py
  - pipelines/check_forecasts.py
  - pipelines/save_plots.py
  - pipelines/send_emails.py
  - src/monitoring/etl.py
  - src/monitoring/plot.py
  - src/constants.py
  - src/ses_mail.py
extra:
  framework: "frameworks/tcd-flooding/2025-07-31.md — trigger definitions and provenance live there; this page is the ops runbook"
  cutover_2026_09: "2026-09-24: the daily GHA cron moved to a Databricks bundle job (#20, repos-02). 2026-09-25: DATA_STAGE split from STAGE (#19/#21) — the job keeps STAGE=prod for live recipients but reads/writes the DEV DB+blob (the dev server lost public access on 2026-09-22 but Databricks reaches it over its private endpoint; prod has no `projects` schema and only chdadmin / an Entra admin can create one), and emails go out via SES daily while Listmonk is down. Undo = email_backend listmonk, always_email false in the bundle. Test run 1047675586434155 green (SES to Tristan)."
visibility: internal
last_synced: "2026-09-25"
---

# Chad Flooding Monitoring (2025 framework)

> Runbook. Trigger design and provenance: [frameworks/tcd-flooding/2025-07-31](../frameworks/tcd-flooding/2025-07-31.md). Sibling of [nga-flooding-monitoring](nga-flooding-monitoring.md) (same code shape; the NGA repo was templated from this one).

## One-liner

*One daily Databricks job evaluates the Chad AA riverine trigger — GloFAS ensemble-mean discharge at N'Djamena against the readiness (≤14 d lead) and action (≤10 d lead) thresholds — and emails a French-language status update.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| TCD Flood Monitoring (Databricks bundle `tcd_flood_monitoring`) | `dbx:496653473007283` | `0 0 20 * * ?` UTC | live since 2026-09-24 — tasks check_forecasts → save_plots → send_emails via `databricks/run_task.py`; `on_failure` → tristan.downing@un.org |
| Monitor flooding (GHA) | `.github/workflows/monitoring.yml` | `workflow_dispatch` only | retired 2026-09-24 (cron removed by #20); GHA runners cannot reach the dev DB any more anyway |

**Since 2026-09-25 (PRs #19/#21):** the bundle's prod target runs with `stage=prod` (real recipients) **and `data_stage=dev`** — the DB/blob plane stays on the dev server, reachable from Databricks over its private endpoint. Emails go out by direct SES/SMTP to Tristan, Zack, Leonardo and Hannah, and the informational email is sent **every day** (`ALWAYS_EMAIL=true`) as a heartbeat while Listmonk is down. Ad-hoc: `databricks bundle run tcd_flood_monitoring -t prod -p DEFAULT --params test_email=true` (Tristan only). Undo when Listmonk is back: `email_backend: listmonk`, `always_email: "false"` in `databricks.yml`.

## Steps

1. `check_forecasts.py` — download the day's GloFAS operational ensemble forecast (leads 1–14 d, EWDS) for the N'Djamena point into the DEV `projects` blob (skipped if already there), decode with cfgrib, write the ensemble-mean rows to `projects.pa_aa_tcd_flooding_monitoring` (DEV).
2. `save_plots.py` — HDX-styled forecast chart to `projects/pa-aa-tcd-flooding/monitoring/{date}_{activated}.png` (DEV blob).
3. `send_emails.py` — `etl.check_results`: **action** = ensemble mean ≥ 4 542 m³/s at lead 0–10 d; **readiness** = ≥ 4 542 at lead 0–14 d; **warning** = ≥ 3 500 (advisory only). Sends: one email per activation type (readiness/action templates) plus the informational email (with the chart). Normal cadence = activations, warnings, Mondays, or test mode; **currently every day** (`ALWAYS_EMAIL`).

## Failure modes & debugging

- **CDS/EWDS 400 "invalid combination"** = the GloFAS issue is not published yet; the run crashes (no wait-and-retry like SOM). Re-run later with `--params monitoring_date=YYYY-MM-DD`.
- **`relation projects.pa_aa_tcd_flooding_monitoring does not exist` / connection timeout**: the job is not on the dev data plane — check `data_stage` in the deployed job and the `dsci` secret `DSCI_AZ_DB_DEV_HOST` (must be the dev private IP), see [database.md](../infrastructure/database.md).
- **No email although the run is green**: `ALWAYS_EMAIL` unset and no activation/warning/Monday — expected; or `EMAIL_BACKEND=listmonk` while Listmonk is down (the send task fails, not silently).
