---
content_type: pipeline
name: pipelines-status
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Pipeline Status Refresh", ref: "dbx:314917446421609 (databricks.yml job pipeline_status_refresh)", schedule: "0 0 6 * * ? (daily 06:00 UTC; runs scripts/fetch_pipelines.py --to-blob)", status: live }
    - { name: "Update Pipeline Status", ref: ".github/workflows/update.yml", schedule: "15 6 * * * (daily 06:15 UTC) + workflow_dispatch; downloads pipelines.json from the dev blob and commits it", status: live }
inputs:
  - "Databricks Jobs API (jobs tagged databricks=job, plus all jobs for the untagged/off-policy warnings) via databricks-sdk"
  - "Azure PostgreSQL dev AND prod DBs (column defs, row counts, table sizes, timestamp ranges for each job's output_schema tables, via ocha-stratus.get_engine)"
  - "Azure Blob dev AND prod accounts (blob size/count per job output_blob container/prefix, via ocha-stratus.get_container_client)"
  - "Databricks cluster policies (to label each job's compute)"
outputs:
  - "dev blob projects/ds-pipelines-status/pipelines.json (written by the Databricks job)"
  - "data/pipelines.json (committed to main by the GHA bot if changed; refreshes GitHub Pages)"
dependencies:
  - "ocha-stratus>=0.1.7 (DB engines, container client, upload_blob_data)"
  - "databricks-sdk>=0.20.0 (ships with the Databricks runtime)"
  - "cron-descriptor>=2.0.0, python-dotenv>=1.0.0, sqlalchemy>=2.0, psycopg2-binary (job libraries)"
  - "Job Compute (single node) cluster policy 0017962FF5D1E3B9 injects DSCI_AZ_DB_{DEV,PROD}_{HOST,UID,PW} and DSCI_AZ_BLOB_{DEV,PROD}_SAS from the dsci secret scope"
  - "GHA secret DSCI_AZ_BLOB_DEV_SAS (update.yml only)"
downstream:
  - "Team operational use — the dashboard surfaces Databricks job health and DB/blob output metadata to the whole DS team"
depends_on:
  - dbx-job-compute
surfaces:
  - {url: "https://ocha-dap.github.io/ds-pipelines-status/", kind: dashboard, title: "DSCI Pipeline Status dashboard (Databricks-only; superseded by infrastructure/pipeline-registry.md)"}
source_repo: ocha-dap/ds-pipelines-status
source_branch: main
source_sha: "5aa7646"
code_ref:
  - "scripts/fetch_pipelines.py"
  - "databricks.yml"
  - ".github/workflows/update.yml"
  # data/pipelines.json deliberately NOT a code_ref: regenerated data, would re-flag drift weekly.
  - "index.html + script.js + styles.css"
extra:
  pyproject_name: "ds-pipelines-viz"
  job_discovery: "Jobs are auto-discovered by tag databricks=job; no hardcoded list"
  job_tags: "type, hazard, kb (KB page stem, rendered as a link), output_schema (schema.table list; bare schemas ignored), output_blob (container/prefix list), data_mode (dev|prod; inferred from data_stage/stage/mode params or --mode arg, default prod). Tables/blobs are looked up in the job's plane first, then the other; dev outputs get a badge."
  discrepancies:
    - "[resolved] Dashboard moved to GitHub Pages; the Azure Static Web Apps deploy workflow was removed 2026-09-30."
    - "[resolved] fetch_pipelines.py now emits a per-job paused flag (rendered as a 'paused' status in script.js) and top-level warnings (untagged scheduled jobs, scheduled jobs not on a job-cluster policy); the old 'paused jobs are invisible' gap is closed."
    - "[resolved] Blob access now goes through ocha-stratus (get_container_client); azure-storage-blob is no longer imported directly."
    - "[resolved] README's old 'every 4 hours' and secret list are gone; README now matches the daily 06:00/06:15 flow and the single DSCI_AZ_BLOB_DEV_SAS secret."
    - "[stale] infrastructure/deployments.md still lists the dsci-monitor Azure SWA row (thankful-ground-0e9f52a0f) although the SWA deploy workflow is gone from the repo."
    - "[stale] pipeline-registry.md labels gha:ds-pipelines-status/update.yml cadence 'every 6h'; update.yml is now daily (15 6 * * *)."
visibility: internal
last_synced: "2026-10-19"
---

# pipelines-status

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Daily: a Databricks job reads every `databricks=job`-tagged job from the Jobs API, enriches with dev+prod DB table and blob metadata, uploads `pipelines.json` to the dev blob; 15 min later a GitHub Action downloads and commits it, and GitHub Pages serves the dashboard.

> **Slated to be superseded** by the job_id-keyed [pipeline-registry.md](../infrastructure/pipeline-registry.md) (Databricks + GHA, last-success-vs-cadence health). This dashboard is Databricks-only, tag-reliant and display-only, though it now also warns about untagged scheduled jobs. Background: [databricks.md](../infrastructure/databricks.md#how-a-pipeline-gets-discovered-today-and-why-were-superseding-it).

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Pipeline Status Refresh | `dbx:314917446421609` (`databricks.yml`, job `pipeline_status_refresh`, `source: GIT` on `main`) | `0 0 6 * * ?` daily 06:00 UTC; Job Compute (single node) policy `0017962FF5D1E3B9`; prod target `run_as` adm.hker1; `on_failure` email hannah.ker@un.org; `max_concurrent_runs: 1` | live (🟢 OK in the registry) |
| Update Pipeline Status | `.github/workflows/update.yml` (`gha:ds-pipelines-status/update.yml`) | `15 6 * * *` daily 06:15 UTC + `workflow_dispatch` | live |

The fetch runs on Databricks because both Postgres servers are private-endpoint only (GitHub runners cannot reach them). Code changes ship by pushing `main`; `databricks bundle deploy -t prod` is only needed when job config (schedule, libraries, tags, policy) changes. The `dev` bundle target is `mode: development` and auto-pauses the job — use it with `--var git_branch=...` to test a branch.

## Inputs

- **Databricks Jobs API** — `jobs.list(expand_tasks=True)`, per-job `jobs.get`, recent runs per tagged job, cluster policies. On Databricks it authenticates as the job's `run_as` identity; locally via `DATABRICKS_HOST`/`DATABRICKS_TOKEN`.
- **Postgres dev + prod** (`ocha-stratus.get_engine(stage=...)`) — `information_schema.columns` + `pg_description`, `pg_class.reltuples` (approximate row count), `pg_total_relation_size`, MIN/MAX of timestamp/date columns, for each `output_schema` table.
- **Blob dev + prod** (`get_container_client`) — total size and count under each `output_blob` `container/prefix`.

## Steps

1. `fetch_pipelines.py --to-blob` (Databricks task `fetch`): list all jobs; keep those tagged `databricks=job`.
2. Build top-level `warnings`: scheduled, unpaused jobs that are **untagged** (missed by the table) and scheduled jobs **not on a job-cluster policy**; plus an `untagged_jobs` count.
3. Per tagged job: resolve `data_mode`; fetch table schemas/stats and blob sizes (expected plane first, then the other); fetch recent runs → last-run status (`success|failed|running|unknown`) and median/IQR duration of recent successes; schedule in plain English (or "Triggered by <upstream job>" / "Manual"); `paused` flag; compute policy names; task git URLs.
4. Upload JSON to dev blob `projects/ds-pipelines-status/pipelines.json`.
5. `update.yml` curls that blob with `DSCI_AZ_BLOB_DEV_SAS`, prints `generated_at` and job count, commits `data/pipelines.json` if changed.
6. The commit rebuilds GitHub Pages; `index.html`/`script.js` render `data/pipelines.json` (modal with columns/row counts/ranges for jobs with `output_schema`).

Local: `uv run scripts/fetch_pipelines.py` writes `data/pipelines.json` directly (needs `.env`); `python -m http.server 8000` to view.

## Outputs

- Dev blob `projects/ds-pipelines-status/pipelines.json`.
- `data/pipelines.json` in the repo (per job: name, description, tasks, schedule, last_run, type/hazard/kb tags, paused, data_mode, compute, duration stats, output_schemas, blob_storage; top-level `generated_at`, `warnings`, `untagged_jobs`).
- Dashboard: <https://ocha-dap.github.io/ds-pipelines-status/>.

## Dependencies

- `ocha-stratus>=0.1.7`, `databricks-sdk`, `cron-descriptor`, `python-dotenv`, `sqlalchemy`, `psycopg2-binary` (job libraries in `databricks.yml`).
- Cluster policy `0017962FF5D1E3B9` injects the `DSCI_AZ_*` dev+prod DB and blob credentials from the `dsci` secret scope; fallback Jobs-API token `DSCI_DATABRICKS_TOKEN` in that scope.
- GHA secret `DSCI_AZ_BLOB_DEV_SAS` (the only one the workflow needs).

## Failure modes & debugging

- **Dashboard stale:** check both stages. If the Databricks job failed (email to hannah.ker@un.org; see the registry row), the blob is old and `update.yml` just finds no change and does not commit. If the blob is fine but the page is old, check the `update.yml` run (expired `DSCI_AZ_BLOB_DEV_SAS` makes `curl -f` fail).
- **Timing coupling:** the Action at 06:15 assumes the 06:00 job finished; a slow run means a day-old file is committed.
- **Missing table/blob stats fail soft:** unreachable DB logs `<stage> database unavailable, skipping its table stats`; missing SAS logs `No DSCI_AZ_BLOB_<STAGE>_SAS set`; unreadable blob/table is logged and skipped; `fetch_table_stats` swallows all exceptions. The run stays green with stats missing. Row counts are `reltuples` estimates (stale until `ANALYZE`).
- **Job not on the dashboard:** it needs tag `databricks=job`; untagged scheduled jobs appear only in the `warnings` block. Add tags (`type`, `hazard`, `kb`, `output_schema`, `output_blob`, `data_mode`) in `databricks.yml` — no code change.
- **Paused jobs** now carry `paused: true` and show a "paused" status on the dashboard (e.g. `Run NHC`, `dbx:266763033249426`, per the registry); the schedule text is still computed from the cron, so read the flag, not the schedule. Only cron-schedule pauses set the flag (a paused `trigger` does not). Dev-slot jobs are marked via `data_mode`.
- **Dev bundle target auto-pauses** the job (development mode); don't expect scheduled runs from `-t dev`.
- **Still blind to GHA-cron pipelines** — use [pipeline-registry.md](../infrastructure/pipeline-registry.md) for those.
- **Doc discrepancies:** [deployments.md](../infrastructure/deployments.md) still lists a `dsci-monitor` Azure SWA row, though the SWA deploy workflow no longer exists in the repo; the registry labels `update.yml` "every 6h" although it is now daily.

## Downstream consumers

Read-only operational monitor for the DS team; nothing consumes `pipelines.json` programmatically except the static dashboard. Each monitored job links to its KB page via its `kb` tag (e.g. [nhc-forecast](nhc-forecast.md), [imerg](imerg.md)).
