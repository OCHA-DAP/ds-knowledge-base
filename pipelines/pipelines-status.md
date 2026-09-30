---
content_type: pipeline
name: pipelines-status
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Update Pipeline Status", ref: ".github/workflows/update.yml", schedule: "15 */6 * * *", status: live }
    - { name: "Azure Static Web Apps CI/CD", ref: ".github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml", schedule: "push/PR to main", status: live }
inputs:
  - "Databricks workspace API (all jobs tagged databricks=job, latest run per job) via databricks-sdk"
  - "Azure PostgreSQL prod AND dev DBs (column defs + comments, reltuples row counts, table sizes, timestamp ranges via ocha-stratus.get_engine), for tables named in each job's output_schema tag"
  - "Azure Blob Storage imb0chd0prod and imb0chd0dev (blob count/size per output_blob container/prefix, direct SAS-token call)"
outputs:
  - "data/pipelines.json (committed to main every 6h by the GHA bot if changed)"
  - "Azure Static Web App https://thankful-ground-0e9f52a0f.7.azurestaticapps.net (auto-deployed on push to main)"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-pipelines-status/", kind: dashboard, title: "DSCI Pipeline Status dashboard (Databricks-only; superseded by infrastructure/pipeline-registry.md)"}
dependencies:
  - "ocha-stratus>=0.1.7 (prod/dev DB engines)"
  - "databricks-sdk>=0.20.0"
  - "azure-storage-blob (UNDECLARED in pyproject; imported directly, pulled transitively via ocha-stratus)"
  - "cron-descriptor>=2.0.0, croniter>=2.0.0 (schedule display + next-run)"
  - "python-dotenv>=1.0.0"
  - "GHA secrets: DSCI_DATABRICKS_HOST, DSCI_DATABRICKS_TOKEN, DSCI_AZ_DB_{PROD,DEV}_{PW,UID,HOST}, DSCI_AZ_BLOB_{PROD,DEV}_SAS, AZURE_STATIC_WEB_APPS_API_TOKEN_THANKFUL_GROUND_0E9F52A0F"
downstream:
  - "Team operational use only: the dashboard shows Databricks job health and DB/blob output metadata to the DS team; nothing reads pipelines.json programmatically"
depends_on: []  # reads Databricks job metadata, not a KB-modelled dataset
source_repo: ocha-dap/ds-pipelines-status
source_branch: main
source_sha: "2cf14cf"
code_ref:
  - "scripts/fetch_pipelines.py"
  - ".github/workflows/update.yml"
  - ".github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml"
  # data/pipelines.json deliberately NOT a code_ref: regenerated every run (kb-drift noise).
  - "index.html + script.js + styles.css"
extra:
  azure_swa_name: "thankful-ground-0e9f52a0f"
  pyproject_name: "ds-pipelines-viz"
  job_tags: "databricks=job (discovery); type, hazard, kb (KB page stem, rendered as link), status=development, output_schema (schema.table list), output_blob (container/prefix list), data_mode (dev|prod, else inferred from job params data_stage/stage/mode)"
  monitored_jobs_as_of_2026_09_29: 27
  discrepancies:
    - "[stale] README.md says the update job runs every 4 hours; update.yml cron is `15 */6 * * *` (6h). Code is authoritative."
    - "[stale] README lists secrets DATABRICKS_HOST/DATABRICKS_TOKEN; the workflow's secret names are DSCI_DATABRICKS_HOST/DSCI_DATABRICKS_TOKEN, mapped onto the env vars the SDK reads."
    - "[conflict] Blob sizing uses a direct azure-storage-blob SAS call (prod + dev accounts), not ocha-stratus, diverging from the team convention. DB access does go through stratus."
    - "[gap] azure-storage-blob is imported but not declared in pyproject.toml; resolves only transitively via ocha-stratus."
    - "[gap] pause_status is never read (no 'paused' handling in fetch_pipelines.py or script.js): a PAUSED job still shows a plausible future Next Run; the only tell is a stale Last Run."
    - "[gap] Discovery relies on the databricks=job tag and covers Databricks only; GHA-cron pipelines are invisible (pipeline-registry.md covers both)."
visibility: internal
last_synced: "2026-09-29"
---

# pipelines-status

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Every 6 hours: list all Databricks jobs tagged `databricks=job`, enrich with prod/dev DB table metadata and Azure blob sizes, commit `data/pipelines.json` to main; Azure Static Web Apps redeploys the static dashboard on every push.

> **Slated to be superseded.** Databricks-only, tag-reliant, display-only. It cannot see GHA-cron pipelines or whether a job is paused. The replacement is the job_id-keyed [pipeline-registry.md](../infrastructure/pipeline-registry.md) (Databricks + GHA, last-success-vs-cadence health); see [databricks.md](../infrastructure/databricks.md#how-a-pipeline-gets-discovered-today-and-why-were-superseding-it).

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Update Pipeline Status | `.github/workflows/update.yml` | `15 */6 * * *` + manual `workflow_dispatch` | live |
| Azure Static Web Apps CI/CD | `.github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml` | push/PR to main | live |

Both run on `main`. `update.yml` commits `data/pipelines.json`; that push triggers the SWA deploy. Registry handle: `gha:ds-pipelines-status/update.yml` (🟢 OK in [pipeline-registry.md](../infrastructure/pipeline-registry.md)). The deployments row is `dsci-monitor` in [deployments.md](../infrastructure/deployments.md). Repo path is `ocha-dap/ds-pipelines-status`, branch `main`; no mismatch.

## Inputs

- **Databricks workspace API** (`DATABRICKS_HOST`/`DATABRICKS_TOKEN`, fed from GHA secrets `DSCI_DATABRICKS_*`): jobs with tag `databricks=job`, full job settings, latest run. Discovery is dynamic. 27 jobs in the 2026-09-29 snapshot at `2cf14cf` (the mirrors, `Run *` raster/storms jobs, NGA/TCD/Cuba/HTI monitors, `CERF Supplement Daily`, etc.).
- **Postgres prod and dev** (`ocha_stratus.get_engine(stage=...)`): for tables in the `output_schema` tag (`schema.table` only; bare schema names ignored): `information_schema.columns` + comments, `reltuples` row counts, size, timestamp min/max.
- **Azure Blob** (`imb0chd0prod` / `imb0chd0dev`, one SAS per stage): count and total size under each `output_blob` `container/prefix`.
- **Data-plane resolution**: `data_mode` tag, else inferred from job params `data_stage`/`stage`/`mode`. Tables and blobs are looked up in that plane first, then the other. A stage that fails to connect is skipped for the rest of the run.

## Steps

1. `update.yml` runs `uv run scripts/fetch_pipelines.py` with secrets as env vars.
2. Discover jobs (`client.jobs.list()` filtered on the tag), then `jobs.get` for each.
3. Resolve `data_mode`; fetch table schemas/stats and blob stats, each stamped with the `stage` where it was found.
4. Latest run via `jobs.list_runs(limit=1)`, mapped to `success|failed|running|unknown`. Schedule text and next run come from the Quartz cron (or periodic trigger) via `cron-descriptor`/`croniter`.
5. Write `data/pipelines.json` (`generated_at` is always refreshed, so it commits every run).
6. The bot commits and pushes if changed. The SWA workflow then deploys `index.html`/`script.js`/`styles.css`/data.

## Outputs

- **`data/pipelines.json`**: per job: name, description, tasks (git URLs), schedule, last run, next run, `tags` (type), `hazard`, `kb`, `job_status`, `data_mode`, `output_schemas`, `blob_storage`.
- **Dashboard** at <https://thankful-ground-0e9f52a0f.7.azurestaticapps.net>: table with search and type/hazard filters, KB-page links, a `dev` badge for jobs/outputs on the dev plane, and a modal with column definitions, row counts and timestamp ranges.

## Dependencies

- `ocha-stratus>=0.1.7` (DB engines only), `databricks-sdk>=0.20.0`, `cron-descriptor`, `croniter`, `python-dotenv`. `azure-storage-blob` is used but undeclared.
- GHA secrets: `DSCI_DATABRICKS_HOST/TOKEN`, `DSCI_AZ_DB_{PROD,DEV}_{PW,UID,HOST}`, `DSCI_AZ_BLOB_{PROD,DEV}_SAS`, `AZURE_STATIC_WEB_APPS_API_TOKEN_THANKFUL_GROUND_0E9F52A0F`.

## Failure modes & debugging

- **Update job fails**: the commit step never runs, so the dashboard silently goes stale. Check the "Update Pipeline Status" run in Actions (or its row in the registry).
- **Missing DB stats**: table stats and schema fetches swallow exceptions, and an unreachable stage is skipped with a "database unavailable" log line. Missing tables usually mean a bad `output_schema` tag, wrong `data_mode`, or bad DB secrets. Locally set `PGSSLMODE=require` ([conventions](../infrastructure/conventions.md)).
- **Missing blob stats**: a missing SAS logs "No DSCI_AZ_BLOB_<STAGE>_SAS set"; other errors return `None` silently.
- **Row counts are approximate**: `reltuples` is a planner estimate, stale without `ANALYZE`.
- **Paused jobs are not flagged**: `pause_status` is never read, so a paused job still shows a future Next Run. Only a stale Last Run gives it away. Cross-check paused state in [pipeline-registry.md](../infrastructure/pipeline-registry.md).
- **Failing jobs look normal**: any tagged job renders with a red `failed` pill (e.g. `MOZ Cyclone Monitoring` in the 2026-09-29 snapshot). The dashboard and registry are point-in-time and can disagree, so check both.
- **Untagged jobs are invisible**: add `databricks=job` (plus `type`, `hazard`, `kb`, `output_schema`, `output_blob`, `data_mode`) in `databricks.yml`. No code change needed.
- **README is stale** (4h cadence, secret names). The workflow is authoritative.
- **Local**: `uv run scripts/fetch_pipelines.py` (needs `.env`), then `python -m http.server 8000`.

## Downstream consumers

Read-only operational monitor for the DS team; no pipeline or app consumes `pipelines.json`. Jobs with a `kb` tag link to their KB pages, e.g. [hdx-floodscan](hdx-floodscan.md), [population-mirror](population-mirror.md), [ipc-mirror](ipc-mirror.md), [fewsnet-mirror](fewsnet-mirror.md), [hnrp-mirror](hnrp-mirror.md), [mdg-monitoring](mdg-monitoring.md). Superseded in intent by [pipeline-registry.md](../infrastructure/pipeline-registry.md).
