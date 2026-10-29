---
content_type: pipeline
name: fji-storms-monitoring
type: monitoring
status: live
deployment:
  platform: databricks   # live since 2026-10-26 (FMS_TARGETS=dbx); the GitHub Actions poller hands each CSV to it, Check Trigger is the rollback
  resource_group:            # n/a
  jobs:
    - { name: "Power Automate flow fji_trigger_monitoring", ref: "personal flow on the maintainer's un.org mailbox (not in any repo; details in ds-knowledge-base-internal/infrastructure/fji-fms-relay.md)", schedule: "event — each FMS forecast email", status: live }
    - { name: "Poll FMS inbox (the relay watcher)", ref: ".github/workflows/poll_fms_inbox.yml", schedule: "*/10 * * * * (repo vars POLL_ENABLED=True, POLL_DRY_RUN=False)", status: live }
    - { name: "Check Trigger", ref: ".github/workflows/run_monitor_forecast_trigger.yml (checks out branch initial-2025-trigger)", schedule: "event — repository_dispatch fms_forecast / fms_forecast_test from the poller (+ workflow_dispatch)", status: paused }   # rollback since 2026-10-26: FMS_TARGETS=gha
    - { name: "Fiji Cyclone Monitoring (DAB fji_monitoring)", ref: "dbx:481931590521487", schedule: "event — jobs/run-now from the poller, one run per CSV (no schedule)", status: live }   # live since 2026-10-26 (shadow on the test list 2026-10-19..26)
    - { name: "Keep Repo Awake", ref: ".github/workflows/keep_awake.yml (pushes to branch keep-awake)", schedule: "0 12 * * 1 (Mondays 12:00 UTC)", status: live }
inputs:
  - "FMS (RSMC Nadi) Official Forecast Track CSVs, emailed to ocha-datascience@un.org about every 6 hours during a tropical cyclone event (sometimes also to data.science@humdata.org, which nothing here reads)"
  - "The humdata.org (Zoho) relay inbox, over IMAP (address in the internal KB)"
  - "WorldPop 2020 1 km UN-adjusted population — blob (dev) pa-aa-fji-storms/raw/worldpop/fji_ppp_2020_1km_Aggregated_UNadj.tif"
  - "Fiji COD-AB admin 3 — blob (dev), src/datasources/codab.py"
  - "Databricks path only: storms.fms_forecasts / storms.fms_tracks_geo (prod database; test events use dev), read back by the monitor (--from-db)"
outputs:
  - "Listmonk campaigns: information email for every forecast to lists 11 (Fiji framework info), 14 (CERF info) and 6 (DSCI); readiness / action emails to lists 10 (Fiji framework trigger), 15 (CERF trigger) and 6; test sends to list 5 only, subject prefixed [TEST]"
  - "OneDrive fji_fms_forecasts/ — every CSV the flow received (written by the Power Automate flow)"
  - "blob (dev) pa-aa-fji-storms/monitoring/fms_inbox_processed.csv — the poller's record of handled CSVs (sha256 + event + target)"
  - "blob (dev) pa-aa-fji-storms/raw/fms/inbox/ — CSVs staged for the Databricks job"
  - "blob (dev) pa-aa-fji-storms/monitoring/email_record.csv (test_email_record.csv for test sends) — the Databricks monitor's send-once record"
  - "Databricks path only: storms.fms_storms / storms.fms_forecasts / storms.fms_tracks_geo via the ds-storms-pipeline FMS ingest at tag fms-v1.0.0 (prod database since 2026-10-22; fms_forecast_test runs write to dev); raw CSV archived to the storm container, fms/raw/"
surfaces: []   # the Quarto site is declared on frameworks/fji-storms/2025-12-17.md
dependencies:
  - "Power Automate (standard connectors only: Outlook, OneDrive) on the maintainer's un.org account"
  - "Zoho mailbox on humdata.org — repo secrets FMS_IMAP_USER, FMS_IMAP_PASSWORD (Zoho app password), FMS_RELAY_SENDERS"
  - "GitHub repository_dispatch (GITHUB_TOKEN with contents: write)"
  - "ds-storms-pipeline at a pinned tag (storms_pipeline_ref, fms-v*): the ingest task clones it per run"
  - "Databricks service principal fji-fms-relay — CAN_MANAGE_RUN on the job; OAuth secret DATABRICKS_CLIENT_SECRET (jobs scope only, expires 2028-10-18); repo vars DATABRICKS_HOST, DATABRICKS_CLIENT_ID, FMS_DBX_JOB_ID"
  - "repo var FMS_TARGETS: gha | gha,dbx-shadow | dbx"
  - "Listmonk sender credentials (GHA secrets; dsci secret scope on Databricks)"
  - "Databricks Job Compute (single node) policy 0017962FF5D1E3B9, DBR 15.4 LTS, pinned requirements-dbx.txt"
  - "ocha-stratus (blob + Postgres)"
downstream:
  - "Fiji tropical cyclone AA framework — the live readiness / action trigger monitoring (frameworks/fji-storms/2025-12-17.md)"
depends_on:
  - listmonk
  - storms-pipeline
  - storms.fms_forecasts
  - storms.fms_tracks_geo
source_repo: ocha-dap/pa-aa-fji-storms
source_branch: main   # Check Trigger runs the monitor from branch initial-2025-trigger: merged into main 2026-10-19, diverged both ways since (main has the Databricks additions, the branch has slide-deck commits)
source_sha: a87109f
code_ref:
  - pa-aa-fji-storms/pipelines/poll_fms_inbox.py
  - pa-aa-fji-storms/.github/workflows/poll_fms_inbox.yml
  - pa-aa-fji-storms/.github/workflows/run_monitor_forecast_trigger.yml
  - pa-aa-fji-storms/pipelines/monitor_forecast_trigger.py
  - pa-aa-fji-storms/databricks.yml
  - pa-aa-fji-storms/databricks/run_ingest.py
  - pa-aa-fji-storms/databricks/run_monitor.py
  - pa-aa-fji-storms/src/datasources/fms_db.py
  - ds-storms-pipeline/src/pipelines/fms.py   # run at tag fms-v1.0.0 (storms_pipeline_ref)
extra:
  relay_reason: "Until 2026-10 the flow POSTed the CSV straight to Check Trigger. The HTTP connector is premium (licence lapsed: 403 when the flow is turned on) and the GitHub connector is blocked by the UN data policy, so since 2026-10-18 the flow emails the CSV to a relay inbox that the poller reads."
  migration: "GHA → Databricks: shadow on 2026-10-19 (FMS_TARGETS=gha,dbx-shadow). Since 2026-10-22 the job ingests to the prod database (ds-storms-pipeline#61 merged, prod tables created and backfilled, ingest pinned to tag fms-v1.0.0, ingest_mode prod by default). Live since 2026-10-26 (FMS_TARGETS=dbx), after a test run of the deployed job and a check that the monitor's read-only prod login reads storms.fms_*. Rollback = FMS_TARGETS=gha."
visibility: public
last_synced: "2026-10-26"
---

# Fiji tropical cyclone monitoring

> Runbook. How an FMS forecast email becomes a trigger check and a Listmonk email, and what to do when one doesn't arrive.

## One-liner

Every FMS forecast email: the team mailbox forwards it to a personal un.org mailbox → a Power Automate flow emails the CSV on to a humdata.org relay inbox → a GitHub Actions poller (every 10 min) hands it to the Databricks job → population exposed to ≥ 64-knot winds → Listmonk information, readiness and action emails.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Power Automate flow `fji_trigger_monitoring` | the maintainer's personal Power Automate (not in a repo) | each FMS email | live |
| Poll FMS inbox | `.github/workflows/poll_fms_inbox.yml` | `*/10 * * * *` | live |
| Check Trigger | `.github/workflows/run_monitor_forecast_trigger.yml`, runs branch `initial-2025-trigger` | `repository_dispatch` from the poller | paused: the rollback (`FMS_TARGETS=gha`) since 26 Oct 2026 |
| Fiji Cyclone Monitoring | `dbx:481931590521487` (`databricks.yml`) | `jobs/run-now` from the poller | live since 26 Oct 2026 (`FMS_TARGETS=dbx`) |
| Keep Repo Awake | `.github/workflows/keep_awake.yml` | Mondays 12:00 UTC | live |

There is no seasonal switch: the chain runs whenever FMS sends a forecast. The 2025 framework's 1 October–31 May monitoring season is kept by FMS sending forecasts, not by code.

## Steps

1. **FMS** emails each Official Forecast Track CSV to `ocha-datascience@un.org`, which forwards it to the maintainer's un.org mailbox. FMS sometimes also sends to `data.science@humdata.org`; nothing in this chain reads that address, so a forecast sent only there is not monitored.
2. **The flow** (`fji_trigger_monitoring`) starts on "When a new email arrives (V3)". It carries on only if the sender's address ends with `met.gov.fj` or the subject is exactly `fji_test`, and a CSV is attached. For each CSV it saves the file to OneDrive `fji_fms_forecasts/`, replies to the sender, and sends the CSV on to the relay inbox with the Outlook "Send an email (V2)" action, subject `[fji-relay] fms_forecast` (`[fji-relay] fms_forecast_test` for `fji_test`).
3. **The poller** (`pipelines/poll_fms_inbox.py`) reads the relay inbox over IMAP, read-only, looking back 3 days. It accepts an email only from an allowlisted sender, with one of the two subjects, and a `dmarc=pass` in the topmost `Authentication-Results` header (authserv `mx.zohomail.com`). Each CSV is keyed by the sha256 of its bytes plus the event, and recorded in `fms_inbox_processed.csv` once sent, so a CSV is handled once.
4. **`FMS_TARGETS`** picks where it goes; it is `dbx` since 26 October 2026. `gha` sends a `repository_dispatch` to Check Trigger (run titled `FMS <sha12> <event>`). `dbx` stages the CSV in `raw/fms/inbox/` and starts the Databricks job as the `fji-fms-relay` service principal. `gha,dbx-shadow` does both, with the Databricks run on the test list. The shadow keeps its own record, so a CSV the live target already handled still goes to the shadow once.
5. **The monitor** (`pipelines/monitor_forecast_trigger.py`) builds the wind-field buffers, counts the WorldPop population in the 64-knot buffer within 120 h (readiness) and 72 h (action), and sends the Listmonk emails. On Databricks, an `ingest` task first writes the forecast to `storms.fms_*` through ds-storms-pipeline's FMS ingest, and the `monitor` task reads it back (`--from-db`); if the ingest fails, the monitor runs on the staged CSV. The Databricks monitor only evaluates an Official Forecast Track: any other forecast track type (the FMS archive holds two "GP Forecast Track" files) fails the run without emailing.

`fji_test` emails become `fms_forecast_test` runs, which only ever email list 5.

## Outputs

Listmonk information emails for every forecast (lists 11, 14, 6), and readiness and action emails when the trigger is met (lists 10, 15, 6). Every received CSV is kept in OneDrive `fji_fms_forecasts/`. The poller's state, the staged CSVs and the Databricks send-once record are on the dev blob under `pa-aa-fji-storms/`. On the Databricks path, the forecast is also written to `storms.fms_forecasts` / `storms.fms_tracks_geo` in the prod database (test events: dev), and the raw CSV is archived to the `storm` container under `fms/raw/`.

## Dependencies

See the frontmatter. The secrets that expire or can be revoked: the Zoho app password (`FMS_IMAP_PASSWORD`) and the service principal's OAuth secret (`DATABRICKS_CLIENT_SECRET`, `jobs` scope only, expires 18 October 2028). Addresses, the flow's environment and IDs, and who owns what are in the internal KB: `ds-knowledge-base-internal/infrastructure/fji-fms-relay.md`.

## Failure modes & debugging

Follow the chain: the flow's run history in Power Automate and the file in OneDrive `fji_fms_forecasts/` → the relay inbox → the "Poll FMS inbox" run log (it says why it skipped an email) → the Check Trigger run `FMS <sha12> <event>` or the Databricks run → the Listmonk campaign.

- **The flow is personal.** It runs on the maintainer's un.org account. If that account or mailbox goes away, or the forward from the team mailbox changes, no forecast reaches the poller and nothing fails visibly. A new owner needs their own copy of the flow and the relay inbox. The long-term fix is to read the team mailbox directly (Microsoft Graph `Mail.Read`, needs OCHA IT).
- **Poll runs fail at the IMAP login:** the Zoho app password was revoked or changed; set `FMS_IMAP_PASSWORD` again.
- **The poller skips relay emails:** the log names the reason. An `authserv-id` warning means Zoho's header changed: set the repo var `FMS_AUTHSERV_ID` to the id the log shows.
- **Databricks runs don't start** (`Databricks hand-off failed: token request: HTTP 401` in the poll log): the service principal's secret expired or was deleted. Generate a new one with the `jobs` scope and set `DATABRICKS_CLIENT_SECRET`.
- **Never delete branch `initial-2025-trigger`.** Check Trigger, the rollback, runs its code, and GitHub Pages is served from its `docs/`. A change to the GitHub Actions monitor only takes effect on that branch. That monitor is older than `main`'s: it has no send-once record and no 48-hour age guard, so a forecast re-sent through Check Trigger is emailed again.
- **Deploying the Databricks job:** a plain `databricks bundle deploy -t prod -p DEFAULT` from a clean checkout of `main`. The ingest clones ds-storms-pipeline at the tag in `storms_pipeline_ref` (`fms-v1.0.0`), not its `main`: a change to its `src/pipelines/fms.py` reaches this job only after a new `fms-v*` tag, a bump of that default and a redeploy.
- **The ingest fails on an unreadable value:** a value that can't be read as a number in a column the trigger reads (position, wind, category, uncertainty, 34/50/64 kt radii) fails the ingest, so the monitor runs on the staged CSV and the run ends FAILED. The same value in any other column is stored as NULL with a warning in the ingest log. A file with no points, or a point without a readable time or position, also fails.
- **A run fails with "not an 'Official Forecast Track': not monitored":** the ingest wrote another forecast track type. The trigger is defined on the Official forecast, so nothing was emailed; look at the file and decide by hand.
- **Package pins:** the GitHub Actions monitor pins `pyarrow==25.0.0` because pyarrow 26 needs NumPy ≥ 2 and the monitor pins `numpy==1.25.1`. The Databricks job installs the full lock `requirements-dbx.txt` in one go: installing libraries one by one let pip upgrade NumPy and broke shapely.
- **A forecast was missed, or a Databricks run failed after the poller recorded it:** send it by hand with Check Trigger's `workflow_dispatch` (base64 of the CSV) or `databricks bundle run fji_monitoring` (see `databricks.yml`). The poller won't resend a CSV it has recorded. Set Check Trigger's `test_email` explicitly: left blank it falls back to the repo variable `TEST_EMAIL=False` and emails the real lists.
- **Switching back to GitHub Actions:** `gh variable set FMS_TARGETS --body gha --repo OCHA-DAP/pa-aa-fji-storms`. The poller won't resend a CSV a failed Databricks run already took (see above): re-send it through Check Trigger by hand.
- **Turning the shadow on** sends every CSV still in the 3-day window to the Databricks job once, on the test list (the shadow keeps its own record). Switching the live target between `gha` and `dbx` does not re-send: both count as one live record. Before switching a new poller on, run it once with `seed_state: True`.
- **End-to-end test:** email the maintainer's un.org mailbox with the subject exactly `fji_test` and a real FMS CSV the poller hasn't seen. Within about 10 minutes you get the `[TEST]` emails on list 5 (one from each monitor when the shadow is on).

Logs: GitHub Actions runs of `OCHA-DAP/pa-aa-fji-storms` (Poll FMS inbox, Check Trigger); Databricks job 481931590521487; failed Databricks runs email the maintainer's un.org address (`email_notifications` in `databricks.yml`; the team mailbox until 2026-10-26).

## South Pacific pipeline trigger — in review (2026-10-29)

pa-aa-fji-storms#35 adds a third task, `trigger_sp_pipeline`: after a live ingest it starts ds-storms-pipeline's South Pacific FMS Pipeline (fire-and-forget; never fails this job). It does nothing until `sp_pipeline_job_id` is set at deploy, and nothing for test events. See [storms-pipeline](storms-pipeline.md) → South Pacific.

## Downstream consumers

The Fiji tropical cyclone AA framework ([2025-12-17](../frameworks/fji-storms/2025-12-17.md)): this is its live forecast trigger monitoring. The observational (IMERG rainfall) trigger is not automated.
