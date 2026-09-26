---
content_type: pipeline
name: mdg-monitoring
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "MDG IMERG Monitoring", ref: "databricks.yml job key `mdg_imerg_monitoring` (job_id not yet visible in infrastructure/pipeline-registry.md)", schedule: "0 16 * * * UTC (quartz `0 0 16 * * ?`)", status: paused }   # PAUSED only on branch ops/mdg-test-list (7398a9c); on main (c2b56f6) the prod target runs it unpaused — see discrepancies
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
source_branch: ops/mdg-test-list
source_sha: 7398a9c
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
  listmonk_lists: "LISTMONK_LIST_ID = 109 (prod), LISTMONK_LIST_ID_TEST = int(os.getenv('LISTMONK_TEST_LIST_ID', 103)) (src/constants.py) — the test list is now overridable at run time, not just prod/test. The Databricks job exposes this as the `test_list_id` parameter (103 default, 5 = a single-recipient list for a solo test send). NB: this override exists only on branch ops/mdg-test-list — on main LISTMONK_LIST_ID_TEST is a hardcoded 103."
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
    - "[conflict] Branch vs main on the pause state: this page reflects branch `ops/mdg-test-list` @ 7398a9c (one commit ahead of main, unmerged at ingest), whose databricks.yml sets `pause_status: PAUSED` — per its inline comment, because the GHA schedule had been off since 2026-04-11 and the move to Databricks was not meant to switch it back on. On `main` (c2b56f6, PR #16 merged) the schedule has **no** pause_status, i.e. a `prod`-target deploy from main would run it daily and send to the real list 109. The GHA cron removal is already on main. Which one is actually deployed is unknown (the job isn't in the registry yet) — confirm in the workspace; unpause when Madagascar cyclone-season monitoring should resume."
    - "[gap] infrastructure/pipeline-registry.md and infrastructure/deployments.md have not caught up to this migration: both still show only the old GHA row (`gha:ds-aa-mdg-monitoring/run_monitor_imerg.yml`, flagged 🔴 DOWN/OVERDUE as of the 2026-06-22 snapshot) and no `dbx:<job_id>` row for `mdg_imerg_monitoring` at all — consistent with the job being deployed paused (paused jobs still usually appear, e.g. `Run NHC` `dbx:266763033249426`, so it may also mean the `prod` target bundle hasn't actually been deployed yet, only authored). Re-run `gen_pipeline_registry.py` and confirm the job exists in the workspace before treating this page's Databricks row as fully live."
    - "[stale] README.md still describes the old AWS-SES-era blob-CSV distribution list (`TEST_LIST` repo variable, distribution_list.csv) as the current mechanism; that changed to Listmonk lists 109/103 at least one ingest ago and the README was never updated. It does correctly describe the new Databricks schedule in its own \"Schedule\" section, so the file is now internally inconsistent (Listmonk section stale, Schedule section current)."
    - "[conflict] Threshold operator: code uses strict greater-than (`df_grouped['mean'].max() > RAIN_THRESH`, src/monitoring/emails.py) so the trigger fires above 300 mm, but README states '>= 300 mm in any region'. Exactly 300.0 mm would NOT activate per the code. Unresolved since the last ingest."
    - "[stale] email_assets/ Jinja2 templates + static banner/logo are legacy; the current email body is inline HTML in emails.py."
    - "[gap] databricks.yml's `prod` target runs `run_as` a named personal admin account (not a service principal) with a `# TODO: replace with a service principal once one is provisioned` — a bus-factor/ownership risk typical of early DAB migrations."
  deployment_registry: "infrastructure/deployments.md's GitHub Actions pipelines table still lists mdg-monitoring as \"GHA-only\" — stale as of this ingest (see discrepancies); the authoritative live-health view is infrastructure/pipeline-registry.md, which is itself not yet showing the Databricks job."
visibility: internal
last_synced: "2026-09-26"
---

# MDG Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Daily at 16:00 UTC (Databricks job; deployed paused on branch `ops/mdg-test-list`): pull IMERG ADM1 raster stats for Madagascar → check the 3-day rainfall total against the 300 mm threshold → send a French-language informational email with a bar chart to the Listmonk distribution list.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| MDG IMERG Monitoring (Databricks) | `databricks.yml` job `mdg_imerg_monitoring`, task `monitor_imerg` via `databricks/run_task.py` | `0 16 * * *` UTC (quartz `0 0 16 * * ?`) | **paused** (branch `ops/mdg-test-list`; unpaused on `main`) |
| Monitor IMERG (GHA) | `.github/workflows/run_monitor_imerg.yml` | none — `workflow_dispatch` only (cron removed) | live (manual fallback) |

The Databricks job is the intended replacement for the GHA cron: GitHub-hosted runners were losing network access to the Postgres DB, so the schedule moved to a Databricks Job Compute cluster that runs the *unmodified* `pipelines/monitor_imerg.py` through a small wrapper (`databricks/run_task.py`). On branch `ops/mdg-test-list` (the branch this page reflects, unmerged at ingest) it is deployed **paused** on purpose — the GHA cron had already been silently dead since 2026-04-11, and the migration was not meant to auto-resume monitoring. On `main` the schedule carries no `pause_status`, so a `prod` deploy from main would run daily. The GHA workflow still exists with a `keep-alive` ping job and a `workflow_dispatch` trigger (`date`, `test` inputs) as a manual fallback; its own cron trigger has been deleted from the YAML.

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

- **Email / Listmonk campaign**: French-language informational email, subject `"[test] Action anticipatoire Madagascar – précipitations autour de {middle_date}"`, campaign name `mdg-cyclone-rainfall-{middle_date}-{EAT timestamp}`, sent to list **109** (prod) or the test list (**103** default, or `LISTMONK_TEST_LIST_ID` on branch `ops/mdg-test-list`, e.g. **5** = a single-recipient list), with a `[test]` subject prefix when testing. Body embeds the 3-day rainfall bar chart and the trigger status.
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

- **Nothing may be scheduled to fire**: on branch `ops/mdg-test-list` the Databricks job `mdg_imerg_monitoring` is deployed **PAUSED** by design (on `main` it is not paused — check which was deployed), and the GHA cron has been removed entirely (manual `workflow_dispatch` only). If Madagascar cyclone-season monitoring needs to resume, unpause the Databricks job (workspace UI, or flip `pause_status` in `databricks.yml` and redeploy) — don't assume either platform is sending emails without checking.
- **Not yet visible in the KB's live registries**: `infrastructure/pipeline-registry.md` has no `dbx:<job_id>` row for this job and still only shows the old GHA row flagged DOWN/OVERDUE; `infrastructure/deployments.md`'s GHA table also hasn't been updated. Re-run `scripts/gen_pipeline_registry.py` and check the Databricks workspace directly to confirm the `prod` target bundle is actually deployed (the `run_as` is a named user, not a service principal, pending a TODO in `databricks.yml`).
- **Missing IMERG dates**: script raises `ValueError` with the missing dates. Root cause: the upstream IMERG pipeline ([pipelines/imerg](imerg.md), Databricks "Run IMERG" `666239885322861` in `ds-raster-pipelines`) ran late or failed. Check that job's logs first.
- **DB connection / SSL failure**: `db_utils.get_engine` builds a raw `postgresql+psycopg2://…/postgres` URL and does **not** set `sslmode`. Azure PostgreSQL needs `PGSSLMODE=require` — set it as an env var (GHA) or in `databricks/run_task.py`'s env dict if you see SSL handshake errors.
- **Listmonk send failure**: bad/missing `DSCI_LISTMONK_*` secrets, unreachable base URL, or wrong list id. The campaign is created then sent with `skip_confirmation=True`; a failure at either step aborts the run. Check the campaign in the Listmonk UI.
- **Accidental real-list send**: on Databricks, the safety toggle is the `test_email` job parameter (string `"true"`/`"false"`) plus `test_list_id` — confirm both before a manual `databricks bundle run`. On GHA, it's the `test` workflow_dispatch input; omitting it sends to the real list `109`.
- **Import errors when running straight off the wsfs mount**: `databricks/run_task.py` exists specifically because importing packages directly off the Databricks git-checkout FUSE mount was intermittently unreliable; it copies `src/`+`pipelines/` to local disk first. If a Databricks run fails with odd filesystem/import errors, check that copy step rather than assuming a code bug.
- **Logs**: GHA — Actions tab on `ocha-dap/ds-aa-mdg-monitoring`, workflow "Monitor IMERG". Databricks — the `mdg_imerg_monitoring` job's run history in the workspace (job id not yet confirmed in the KB registry, see above).

## Downstream consumers

- **Madagascar cyclone AA framework operations** ([frameworks/mdg-storms](../frameworks/mdg-storms/README.md)): the Listmonk list recipients (humanitarian partners, national authorities). This is the framework's rainfall observational-monitoring channel — a terminal notification step; no downstream pipeline consumes it.
- The analyst exposure notebooks (`notebooks/wind_exposure.ipynb`, `bubbles_template.ipynb`) feed ad-hoc wind-exposure reports to the same stakeholders during active cyclone events, using Meteo France RSMC La Réunion track forecasts (`src/datasources/meteofr.py`). These are manual, not part of the scheduled job.
