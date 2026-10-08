---
content_type: pipeline
name: mdg-monitoring
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "MDG IMERG Monitoring", ref: "dbx:1002058609590918 (databricks.yml job key `mdg_imerg_monitoring`)", schedule: "0 16 * * * UTC (quartz `0 0 16 * * ?`) — deployed PAUSED by design", status: paused }
    - { name: "Monitor IMERG (GHA)", ref: ".github/workflows/run_monitor_imerg.yml", schedule: "on-demand (workflow_dispatch only — cron removed)", status: live }
inputs:
  - "DB table: public.imerg (IMERG v7 daily raster stats per ADM1 pcode, prod — always queried at stage=\"prod\" regardless of the job's `stage` parameter)"
  - "DB table: public.polygon (MDG ADM1 pcodes and names, prod — same hardcoded stage=\"prod\")"
outputs:
  - "Email: daily informational email (French) via Listmonk campaign (list 109 prod / 103 test default, overridable via LISTMONK_TEST_LIST_ID, e.g. 5 = a single-recipient test list)"
surfaces: []
dependencies:
  - "ocha-relay @ v0.2.0 (ListmonkClient — campaign create/send)"
  - ocha-stratus==0.1.7
  - pandas==2.2.3
  - sqlalchemy==2.0.36
  - psycopg2-binary==2.9.10
  - matplotlib==3.10.0
  - scipy==1.17.0
  - geopandas (undeclared in requirements.txt; imported by src/monitoring/plotting.py, added explicitly to the Databricks job libraries in databricks.yml)
  - azure-storage-blob==12.22.0
  - python-dotenv==1.2.2
  - "Listmonk (DSCI_LISTMONK_BASE_URL / API_USERNAME / API_KEY) — list 109 (prod), 103 (test default)"
  - "Azure DB PROD credentials (DSCI_AZ_DB_PROD_HOST / UID / PW) — on Databricks injected by the Job Compute policy (000C79D951EAF0D6) from the `dsci` secret scope; on GHA, repo secrets"
  - "Databricks Job Compute policy 000C79D951EAF0D6 (ephemeral single-worker cluster; injects DSCI_AZ_DB_*/DSCI_AZ_BLOB_* — Listmonk sender creds are added separately via spark_env_vars since the policy doesn't carry them)"
downstream:
  - "frameworks/mdg-storms — Madagascar cyclone AA framework (this is its rainfall observational-monitoring email; recipients are the framework's ops team / partners)"
depends_on: [imerg, listmonk, dbx-job-compute]
source_repo: ocha-dap/ds-aa-mdg-monitoring
source_branch: main
source_sha: 6742e95
code_ref:
  - pipelines/monitor_imerg.py
  - databricks.yml
  - databricks/run_task.py
  - .github/workflows/run_monitor_imerg.yml
  - src/constants.py
  - src/datasources/imerg.py
  - src/datasources/polygon.py
  - src/monitoring/emails.py
  - src/monitoring/plotting.py
  - src/utils/db_utils.py
extra:
  comms_channel: "Listmonk via ocha-relay ListmonkClient.from_env() (create_campaign + send_campaign skip_confirmation). Same as the prior ingest — comms channel itself hasn't changed since the AWS SES → Listmonk migration; what changed this round is the compute platform (see discrepancies)."
  listmonk_lists: "LISTMONK_LIST_ID = 109 (prod), LISTMONK_LIST_ID_TEST = int(os.getenv('LISTMONK_TEST_LIST_ID', 103)) (src/constants.py) — the test list is now overridable at run time, not just prod/test. The Databricks job exposes this as the `test_list_id` parameter (103 default, 5 = a single-recipient list for a solo test send). On main since ds-aa-mdg-monitoring#17 (merged 2026-09-28)."
  email_language: French
  trigger_threshold: "RAIN_THRESH = 300 mm (src/constants.py): per-region 3-day sum of region-averaged precip, max across ADM1 regions. Code fires on strictly > 300 mm; README still says >= 300 (see discrepancies) — unresolved since the last ingest."
  test_toggle: "Two independent mechanisms now, one per platform. GHA: the --test CLI flag (workflow_dispatch boolean `test`; default no-flag sends to the real list 109). Databricks: the `test_email` job parameter (STRING \"true\"/\"false\", read via the TEST_EMAIL env fallback in monitor_imerg.py's parse_args — the `dev` bundle target defaults it \"true\", `prod` sets \"false\") plus the separate `test_list_id` parameter (LISTMONK_TEST_LIST_ID) for choosing *which* test list."
  email_body: "Email HTML is built inline as an f-string in src/monitoring/emails.py (_build_body); chart embedded as base64 PNG. The email_assets/templates/*.html (Jinja2) and email_assets/static/ are legacy and NOT used by the current code path."
  blob_unused_in_pipeline: "src/utils/blob_utils.py (raw azure-storage-blob SDK) is still present but NOT used by the scheduled pipeline — no distribution-list CSV is read from blob anymore. azure-storage-blob remains a declared dependency (databricks.yml libs) but is otherwise dead weight on this job."
  analyst_tooling: "notebooks/wind_exposure.ipynb + bubbles_template.ipynb and src/datasources/meteofr.py + src/utils/exposure.py + the plotting.py bullseye/bubble/wind-buffer plotters are manual analyst tools for cyclone events (Meteo France RSMC La Réunion tracks → wind exposure plots). NOT part of the scheduled Monitor IMERG job."
  stage_param_cosmetic: "The Databricks job's `stage` parameter (STAGE env var) only selects the wrapper's declared data plane for parity with the other AA bundles — src/datasources/imerg.py and polygon.py both call get_engine(stage=\"prod\") hardcoded, so the pipeline reads the PROD DB regardless of `stage`. Same is true for the pre-existing GHA path, which only ever had prod DB secrets."
  run_task_wrapper: "databricks/run_task.py is new: a thin Databricks-only entry point that copies src/ + pipelines/ off the wsfs git-checkout mount onto local disk (importing straight off the FUSE mount was unreliable) before shelling out to the unmodified pipelines/monitor_imerg.py with PYTHONPATH set. It also translates job parameters into the env vars the script already understood (STAGE, TEST_EMAIL, MONITORING_DATE, LISTMONK_TEST_LIST_ID) — pipelines/monitor_imerg.py itself is byte-for-byte the same script both platforms run."
  discrepancies:
    - "[change] Platform migration: this repo's scheduled monitor moved from GitHub Actions (`run_monitor_imerg.yml`, daily cron) to a Databricks job (`mdg_imerg_monitoring` in databricks.yml). Per databricks.yml's header comment, the reason is GitHub-hosted runners losing network access to the Postgres DB — not a code/logic change. pipelines/monitor_imerg.py is unchanged; only the run wrapper (databricks/run_task.py) is new. The GHA workflow's cron trigger has been removed; it remains only as a workflow_dispatch manual fallback."
    - "[resolved] Pause state: `ops/mdg-test-list` merged as ds-aa-mdg-monitoring#17 (2026-09-28), so `main` now deploys the job with `pause_status: PAUSED` on purpose — the GHA schedule had been off since 2026-04-11 and the move to Databricks was not meant to switch monitoring back on. The registry confirms it (dbx:1002058609590918, prod, PAUSED, no runs). Unpausing is a runbook step (README \"Switching the daily send on\": optional test send with test_email=true,test_list_id=5, then Resume in the workspace or set pause_status: UNPAUSED and redeploy the prod target), to be done when Madagascar cyclone-season monitoring should resume."
    - "[stale] infrastructure/pipeline-registry.md (snapshot 2026-10-08) carries the Databricks job (`dbx:1002058609590918`, 🟡 WARN PAUSED) but still also lists the retired GHA cron (`gha:ds-aa-mdg-monitoring/run_monitor_imerg.yml`, 🔴 DOWN/OVERDUE) as a prod pipeline — the workflow is dispatch-only now, so that row is noise, not an outage. infrastructure/deployments.md's GHA table still describes mdg-monitoring as GHA-only with a live 16:00 UTC cron; both are generator/inventory fixes outside this page."
    - "[stale] README.md's \"Mailing lists\" section still describes the old AWS-SES-era blob-CSV distribution list (`TEST_LIST` repo variable, distribution_list.csv) as the current mechanism; that changed to Listmonk lists 109/103 at least one ingest ago and the section was never updated. Its \"Schedule\" and \"Switching the daily send on\" sections (added 2026-09-28) are current, so the file is internally inconsistent (Listmonk section stale, schedule sections current)."
    - "[conflict] Threshold operator: code uses strict greater-than (`df_grouped['mean'].max() > RAIN_THRESH`, src/monitoring/emails.py) so the trigger fires above 300 mm, but README states '>= 300 mm in any region'. Exactly 300.0 mm would NOT activate per the code. Unresolved since the last ingest."
    - "[stale] email_assets/ Jinja2 templates + static banner/logo are legacy; the current email body is inline HTML in emails.py."
    - "[gap] databricks.yml's `prod` target runs `run_as` a named personal admin account (not a service principal) with a `# TODO: replace with a service principal once one is provisioned` — a bus-factor/ownership risk typical of early DAB migrations."
  deployment_registry: "infrastructure/deployments.md's GitHub Actions pipelines table still lists mdg-monitoring as \"GHA-only\" — stale (see discrepancies); the authoritative live-health view is infrastructure/pipeline-registry.md, which shows the Databricks job dbx:1002058609590918 as PAUSED."
visibility: internal
last_synced: "2026-10-08"
---

# MDG Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Daily at 16:00 UTC (Databricks job `dbx:1002058609590918`, deployed **paused** on purpose — nothing is sending until it is resumed): pull IMERG ADM1 raster stats for Madagascar → check the 3-day rainfall total against the 300 mm threshold → send a French-language informational email with a bar chart to the Listmonk distribution list.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| MDG IMERG Monitoring (Databricks) | `databricks.yml` job `mdg_imerg_monitoring`, task `monitor_imerg` via `databricks/run_task.py` | `0 16 * * *` UTC (quartz `0 0 16 * * ?`) | **paused** by design (`dbx:1002058609590918`; resume per the README runbook) |
| Monitor IMERG (GHA) | `.github/workflows/run_monitor_imerg.yml` | none — `workflow_dispatch` only (cron removed) | live (manual fallback) |

The Databricks job is the intended replacement for the GHA cron: GitHub-hosted runners were losing network access to the Postgres DB, so the schedule moved to a Databricks Job Compute cluster that runs the *unmodified* `pipelines/monitor_imerg.py` through a small wrapper (`databricks/run_task.py`). It is deployed **paused** on purpose (`pause_status: PAUSED` on `main` since ds-aa-mdg-monitoring#17, 2026-09-28) — the GHA cron had already been silently dead since 2026-04-11, and the migration was not meant to auto-resume monitoring. To switch the daily send on, follow the README's "Switching the daily send on": an optional test send to a single-recipient list (`databricks bundle run mdg_imerg_monitoring -t prod -p DEFAULT --params test_email=true,test_list_id=5`), then Resume the schedule in the workspace or set `pause_status: UNPAUSED` and redeploy the `prod` target. Failures notify the job owner by email (`email_notifications.on_failure`). The GHA workflow still exists with a `keep-alive` ping job and a `workflow_dispatch` trigger (`date`, `test` inputs) as a manual fallback; its own cron trigger has been deleted from the YAML.

Job parameters (Databricks): `stage` (dev/prod — cosmetic, see below), `test_email` (true/false — Listmonk test vs real list), `monitoring_date` (empty = T-2 default), `test_list_id` (which Listmonk list to use when `test_email=true`).

## Inputs

- **`public.imerg`** (prod DB): daily IMERG v7 raster stats per MDG ADM1 pcode, queried for the 3-day window (`src/datasources/imerg.py`).
- **`public.polygon`** (prod DB): ADM1 polygon metadata (pcode, name) for MDG, filtered `iso3='MDG'` and `adm_level=1` (`src/datasources/polygon.py`).

Both queries hardcode `stage="prod"` — the job's `stage` parameter does **not** switch the data plane for this pipeline (see `extra.stage_param_cosmetic`); it exists only for parity with the other AA Databricks bundles.

Default center `date` = `today − 2 days` (T-2), ensuring raster stats exist (the upstream Databricks "Run IMERG" job in `ds-raster-pipelines` — see [pipelines/imerg](imerg.md) — writes `public.imerg` at ~14:40 UTC; this job's email fires at 16:00 UTC). There is **no backfilling** of missed past dates on the schedule; `MONITORING_DATE` / `--date` can be used for a manual backfill run.

## Steps

1. **Parse args** (`pipelines/monitor_imerg.py`): determine `run_date` (default T-2, overridable by `--date` or the `MONITORING_DATE` env fallback) and compute `dates` = 3-day window ending at `run_date + 1 day`. `--test` / `TEST_EMAIL=true` selects the test send.
2. **Fetch polygon data**: query `public.polygon` for MDG ADM1 pcodes.
3. **Fetch IMERG data**: query `public.imerg` for those pcodes over the 3-day range.
4. **Validate**: raise `ValueError` if any of the 3 dates is missing from the result.
5. **Plot** (`src/monitoring/plotting.py → plot_rainfall`): stacked bar chart of 3-day precipitation per ADM1 region, crimson dashed threshold line at 300 mm, totals labelled above bars.
6. **Send email** (`src/monitoring/emails.py → send_info_email`): group by pcode and sum the 3 days; `obsv_trigger` = "ACTIVÉ" if `df_grouped["mean"].max() > RAIN_THRESH` else "PAS ACTIVÉ" (strict greater-than). Build inline HTML body (base64-embedded chart) and create + send a **Listmonk campaign** via `ListmonkClient.from_env()` (`create_campaign` then `send_campaign(skip_confirmation=True)`). Returns the campaign ID.

On Databricks, `databricks/run_task.py` wraps steps 1–6: it copies `src/` + `pipelines/` off the git-checkout FUSE mount to local disk, sets `STAGE`/`TEST_EMAIL`/`MONITORING_DATE`/`LISTMONK_TEST_LIST_ID` env vars from the job parameters, and runs `pipelines/monitor_imerg.py` unchanged as a subprocess.

## Outputs

- **Email / Listmonk campaign**: French-language informational email, subject `"[test] Action anticipatoire Madagascar – précipitations autour de {middle_date}"`, campaign name `mdg-cyclone-rainfall-{middle_date}-{EAT timestamp}`, sent to list **109** (prod) or the test list (**103** default, or `LISTMONK_TEST_LIST_ID`, e.g. **5** = a single-recipient list), with a `[test]` subject prefix when testing. Body embeds the 3-day rainfall bar chart and the trigger status.
- **No DB writes, no blob writes** from the scheduled pipeline.

## Dependencies

| dependency | detail |
|---|---|
| Listmonk (`ocha-relay` v0.2.0) | `ListmonkClient.from_env()` reads `DSCI_LISTMONK_BASE_URL` / `DSCI_LISTMONK_API_USERNAME` / `DSCI_LISTMONK_API_KEY`. Lists `109` (prod) / `103` default test / overridable via `LISTMONK_TEST_LIST_ID` (`src/constants.py`). |
| Azure DB PROD | `DSCI_AZ_DB_PROD_HOST/UID/PW` — `public.imerg` and `public.polygon`. SQLAlchemy + psycopg2 (`src/utils/db_utils.py`). On Databricks, injected by the Job Compute policy `000C79D951EAF0D6` from the `dsci` secret scope; on GHA, repo secrets. |
| Databricks Job Compute policy `000C79D951EAF0D6` | Ephemeral single-worker cluster. Injects `DSCI_AZ_DB_*`/`DSCI_AZ_BLOB_*`; the Listmonk sender creds are **not** in the policy, so `databricks.yml` adds them via `spark_env_vars` from the same `dsci` scope. |
| `test_email`/`test_list_id` params (Databricks) or `--test` flag (GHA) | Toggle test vs real send and which test list. Default (`test_email=false` on the `prod` target) sends to the **real** list `109`. |
| matplotlib / pandas / geopandas | chart rendering and data shaping. `geopandas` is undeclared in `requirements.txt` (arrived transitively on GHA) but is declared explicitly in `databricks.yml`'s job libraries. |
| ocha-stratus 0.1.7, scipy, azure-storage-blob | installed; used by analyst notebooks / legacy helpers, not the scheduled email path. |

## Failure modes & debugging

- **Nothing is scheduled to fire**: the Databricks job `mdg_imerg_monitoring` (`dbx:1002058609590918`) is deployed **PAUSED** by design, and the GHA cron has been removed entirely (manual `workflow_dispatch` only; GitHub-hosted runners cannot reach the Postgres private endpoints since 2026-09-30, so the GHA fallback only works for the email path if the DB is reachable — expect it to fail on the DB read). If Madagascar cyclone-season monitoring needs to resume, unpause the Databricks job (workspace UI, or `pause_status: UNPAUSED` in `databricks.yml` and redeploy the `prod` target) — don't assume either platform is sending emails without checking.
- **Registry reads it as 🟡 WARN / PAUSED**: that is the intended state, not a fault. The old GHA row (🔴 DOWN/OVERDUE) in `infrastructure/pipeline-registry.md` and the GHA-only row in `infrastructure/deployments.md` are stale inventory, not outages. The `prod` target `run_as` is a named user, not a service principal (TODO in `databricks.yml`).
- **Missing IMERG dates**: script raises `ValueError` with the missing dates. Root cause: the upstream IMERG pipeline ([pipelines/imerg](imerg.md), Databricks "Run IMERG" `666239885322861` in `ds-raster-pipelines`) ran late or failed. Check that job's logs first.
- **DB connection / SSL failure**: `db_utils.get_engine` builds a raw `postgresql+psycopg2://…/postgres` URL and does **not** set `sslmode`. Azure PostgreSQL needs `PGSSLMODE=require` — set it as an env var (GHA) or in `databricks/run_task.py`'s env dict if you see SSL handshake errors.
- **Listmonk send failure**: bad/missing `DSCI_LISTMONK_*` secrets, unreachable base URL, or wrong list id. The campaign is created then sent with `skip_confirmation=True`; a failure at either step aborts the run. Check the campaign in the Listmonk UI.
- **Accidental real-list send**: on Databricks, the safety toggle is the `test_email` job parameter (string `"true"`/`"false"`) plus `test_list_id` — confirm both before a manual `databricks bundle run`. On GHA, it's the `test` workflow_dispatch input; omitting it sends to the real list `109`.
- **Import errors when running straight off the wsfs mount**: `databricks/run_task.py` exists specifically because importing packages directly off the Databricks git-checkout FUSE mount was intermittently unreliable; it copies `src/`+`pipelines/` to local disk first. If a Databricks run fails with odd filesystem/import errors, check that copy step rather than assuming a code bug.
- **Logs**: GHA — Actions tab on `ocha-dap/ds-aa-mdg-monitoring`, workflow "Monitor IMERG". Databricks — the `mdg_imerg_monitoring` job's run history in the workspace (`dbx:1002058609590918`).

## Downstream consumers

- **Madagascar cyclone AA framework operations** ([frameworks/mdg-storms](../frameworks/mdg-storms/README.md)): the Listmonk list recipients (humanitarian partners, national authorities). This is the framework's rainfall observational-monitoring channel — a terminal notification step; no downstream pipeline consumes it.
- The analyst exposure notebooks (`notebooks/wind_exposure.ipynb`, `bubbles_template.ipynb`) feed ad-hoc wind-exposure reports to the same stakeholders during active cyclone events, using Meteo France RSMC La Réunion track forecasts (`src/datasources/meteofr.py`). These are manual, not part of the scheduled job.
