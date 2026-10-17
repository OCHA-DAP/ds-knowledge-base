---
content_type: pipeline
name: pipelines-status
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Pipeline Status Refresh", ref: "dbx:314917446421609 (databricks.yml job pipeline_status_refresh)", schedule: "0 0 6 * * ? (daily 06:00 UTC, Job Compute policy 000C79D951EAF0D6; runs scripts/fetch_pipelines.py --to-blob)", status: live }
    - { name: "Update Pipeline Status", ref: ".github/workflows/update.yml", schedule: "15 6 * * * (daily 06:15 UTC) + workflow_dispatch; downloads pipelines.json from the dev blob and commits it", status: live }
inputs:
  - "Databricks Jobs/Runs/cluster-policies API (all jobs with expand_tasks; those tagged databricks=job are tabulated, other scheduled jobs are listed as warnings)"
  - "Azure PostgreSQL prod AND dev DBs (information_schema column defs + pg_description comments, pg_class reltuples row counts, table sizes, timestamp min/max) for tables named in each job's output_schema tag"
  - "Azure Blob prod AND dev accounts (blob count/size per output_blob container/prefix, via ocha-stratus get_container_client)"
outputs:
  - "dev blob projects/ds-pipelines-status/pipelines.json (written by the Databricks job via ocha-stratus upload_blob_data)"
  - "data/pipelines.json (committed to main daily by the GHA bot if changed)"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-pipelines-status/", kind: dashboard, title: "DSCI Pipeline Status dashboard (Databricks-only; superseded by infrastructure/pipeline-registry.md)"}
dependencies:
  - "ocha-stratus>=0.1.7 (DB engines, blob container client, blob upload; both stages)"
  - "databricks-sdk>=0.20.0 (ships with the Databricks runtime on the job)"
  - "cron-descriptor>=2.0.0 (schedule text)"
  - "python-dotenv>=1.0.0, sqlalchemy>=2.0, psycopg2-binary (job libraries)"
  - "Job Compute policy 000C79D951EAF0D6 injects DSCI_AZ_DB_{DEV,PROD}_{HOST,UID,PW} and DSCI_AZ_BLOB_{DEV,PROD}_SAS from the dsci secret scope"
  - "GHA secret DSCI_AZ_BLOB_DEV_SAS (update.yml download only)"
downstream:
  - "Team operational use: the dashboard surfaces Databricks job health and DB/blob output metadata to the whole DS team"
depends_on:
  []  # monitors the Databricks jobs in the registry; no modelled upstream node (reads job metadata, not a KB-modelled dataset)
source_repo: ocha-dap/ds-pipelines-status
source_branch: main
source_sha: "1d2f6f4"
code_ref:
  - "scripts/fetch_pipelines.py"
  - "databricks.yml"
  - ".github/workflows/update.yml"
  # data/pipelines.json deliberately NOT a code_ref: regenerated data, re-flags drift-STALE daily.
  - "index.html + script.js + styles.css"
extra:
  pyproject_name: "ds-pipelines-viz"
  job_discovery: "Databricks jobs are auto-discovered by filtering for the tag databricks=job; no hardcoded job list"
  tags_read: "type, hazard, kb (rendered as KB link), output_schema (schema.table list), output_blob (container/prefix list), data_mode (dev|prod; else inferred from job params data_stage/stage/mode or a --mode task arg; default prod)"
  retired_2026_09_30: "Azure Static Web Apps deploy (thankful-ground-0e9f52a0f) and the runner-side fetch; dashboard now on GitHub Pages"
  discrepancies:
    - "[stale] infrastructure/deployments.md still lists the retired SWA (dsci-monitor, thankful-ground-0e9f52a0f) in its Azure SWA table; the pipelines-status row in its GHA-pipelines table is current."
    - "[stale] pipeline-registry.md lists gha:ds-pipelines-status/update.yml as 'every 6h'; update.yml is now daily 15 6 * * *."
    - "[resolved] pause_status is now read: each pipeline carries a paused flag, and get_warnings() lists scheduled-but-untagged jobs and jobs not on a job-cluster policy."
    - "[resolved] blob sizes now go through ocha-stratus get_container_client; azure-storage-blob is no longer imported directly."
    - "[gap] on_failure email goes to a single person (hannah.ker@un.org); prod target run_as is a personal admin account."
visibility: internal
last_synced: "2026-10-08"
---

# pipelines-status

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Daily: a Databricks job reads every job tagged `databricks=job` from the Jobs API, enriches each with output-table and blob metadata from both the dev and prod data planes, and uploads `pipelines.json` to the dev blob; 15 min later a GitHub Action downloads it, commits it to `main`, and GitHub Pages serves the static dashboard.

> **Slated to be superseded.** It is Databricks-only, tag-reliant and display-only. The job_id-keyed [pipeline-registry.md](../infrastructure/pipeline-registry.md) spans Databricks + GHA with last-success-vs-cadence health checks; see [databricks.md](../infrastructure/databricks.md#how-a-pipeline-gets-discovered-today-and-why-were-superseding-it). The dashboard has since grown `warnings` (untagged scheduled jobs, jobs off a job-cluster policy) and a `paused` flag, which narrows some blind spots, but it still cannot see GHA-cron pipelines.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Pipeline Status Refresh | `dbx:314917446421609` (`databricks.yml`, job `pipeline_status_refresh`, task `fetch`, `source: GIT` on `main`) | `0 0 6 * * ?` (daily 06:00 UTC), Job Compute policy `000C79D951EAF0D6`, 1 worker, `run_as` adm.hker1 (prod target), `on_failure` email to hannah.ker@un.org, `max_concurrent_runs: 1` | live (🟢 OK in the registry) |
| Update Pipeline Status | `.github/workflows/update.yml` (`gha:ds-pipelines-status/update.yml`) | `15 6 * * *` (daily 06:15 UTC) + `workflow_dispatch` | live |

The Azure Static Web Apps deploy workflow and the runner-side fetch were removed on 2026-09-30: both Postgres servers are private-endpoint only, so the fetch moved to Databricks. Code changes ship by pushing `main` (the job uses `source: GIT`); `databricks bundle deploy -t prod` is only needed when job config (schedule, libraries, tags) changes. The `dev` bundle target is `mode: development` and auto-pauses (use `--var git_branch=...` to test a branch).

## Inputs

- **Databricks workspace API** via a bare `WorkspaceClient()`: on the job it authenticates as the run_as identity (the `databricks.yml` header also mentions a `DSCI_DATABRICKS_TOKEN` fallback in the `dsci` scope, but `fetch_pipelines.py` has no code for one); locally via `DATABRICKS_HOST`/`DATABRICKS_TOKEN`. Lists all jobs (`expand_tasks`), policies, and recent runs per tagged job.
- **Postgres prod and dev** (`ocha_stratus.get_engine(stage=...)`): column definitions and comments, `reltuples` row counts, table sizes, timestamp ranges for tables in the `output_schema` tag. A table is looked up in the job's data plane first (`data_mode` tag, else inferred from job params, default prod), then the other.
- **Blob prod and dev** (`ocha_stratus.get_container_client`): blob count and size for each `output_blob` `container/prefix`, same plane-first lookup.

## Steps

1. Databricks job runs `scripts/fetch_pipelines.py --to-blob` (`main()` → `fetch_pipeline_data`).
2. Discovery: `jobs.list(expand_tasks=True)`; jobs tagged `databricks=job` become rows, with `jobs.get` per job for full detail.
3. Per job: tasks (with git URLs), schedule text (Quartz → plain English via `cron-descriptor`; unscheduled jobs show "Triggered by <upstream>" or "Manual"), `paused` flag from `pause_status`, `data_mode`, compute/policy names, last-run status (`success|failed|running|unknown`), a duration summary over recent runs (`RECENT_RUNS = 20`), then `output_schemas` and `blob_storage` enrichment.
4. `warnings`: scheduled, unpaused jobs lacking the `databricks=job` tag (`untagged_scheduled`) and jobs on compute that is not a job-cluster policy (`no_job_policy`); `untagged_jobs` counts untagged jobs.
5. Upload the JSON to dev blob `projects/ds-pipelines-status/pipelines.json`.
6. 06:15 UTC: `update.yml` curls the blob with `DSCI_AZ_BLOB_DEV_SAS`, prints `generated_at` and job count, and commits `data/pipelines.json` only if changed. The commit rebuilds GitHub Pages.
7. The browser (`index.html` + `script.js` + `styles.css`) reads the committed `data/pipelines.json`; rows with output tables open a modal of column definitions, row counts and timestamp ranges; dev outputs carry a badge.

Locally: `uv run scripts/fetch_pipelines.py` writes `data/pipelines.json` (needs `.env`; the DBs are only reachable from the VNet, so DB stats will be skipped), then `python -m http.server 8000`.

## Outputs

- **`pipelines.json`** in dev blob `projects/ds-pipelines-status/` (the hand-off) and the committed `data/pipelines.json`: top-level `generated_at`, `warnings`, `untagged_jobs`, `pipelines[]` (name, description, tasks, schedule, last_run, tags, hazard, kb, paused, data_mode, compute, duration, output_schemas, blob_storage).
- **Dashboard** at <https://ocha-dap.github.io/ds-pipelines-status/> (GitHub Pages).

## Dependencies

- `ocha-stratus>=0.1.7` (engines, container client, upload), `databricks-sdk>=0.20.0`, `cron-descriptor>=2.0.0`, `python-dotenv`, `sqlalchemy>=2.0`, `psycopg2-binary`. `databricks.yml` installs these as job libraries (databricks-sdk comes with the runtime).
- Job Compute policy `000C79D951EAF0D6` injects the `DSCI_AZ_DB_*` and `DSCI_AZ_BLOB_*` (dev + prod) credentials from the `dsci` secret scope; nothing is in the bundle file.
- GHA secret `DSCI_AZ_BLOB_DEV_SAS` only. The old Databricks/DB/prod-blob secrets and the SWA token are no longer used by the workflow.

## Failure modes & debugging

- **Dashboard stale:** two links in the chain. Check the Databricks run of `Pipeline Status Refresh` (`dbx:314917446421609`; failure emails go to one person) first, then the `Update Pipeline Status` run in Actions (`curl -f` fails on an expired `DSCI_AZ_BLOB_DEV_SAS` or a missing blob; the commit step is a no-op when unchanged). Only 15 minutes separate the 06:00 refresh and the 06:15 download: a slow run means the previous day's file is committed.
- **Missing table/blob stats do not fail the run.** An unreachable DB stage logs `<stage> database unavailable, skipping its table stats`; a missing SAS logs `No DSCI_AZ_BLOB_<STAGE>_SAS set, skipping ...`; a listing error logs `Could not list ... blob`. The affected tables simply lack stats; look in the Databricks run output. Running the script outside the VNet silently yields no DB stats (the reason the fetch moved to Databricks).
- **Row counts are `reltuples` estimates**, stale if `ANALYZE` has not run.
- **Tag-reliant:** a job not tagged `databricks=job` is not tabulated; if scheduled and unpaused it appears only under `warnings.untagged_scheduled`. To add a pipeline, tag the job in `databricks.yml` (`databricks: job`, plus `type`, `hazard`, `kb`, `output_schema` as `schema.table`, `output_blob` as `container/prefix`, `data_mode`); no code change.
- **Paused / failing jobs:** `paused` is now surfaced from `pause_status`, but a tagged job can still fail every run and render normally, so skim the status pills. Cross-check [pipeline-registry.md](../infrastructure/pipeline-registry.md), the authoritative health view (for example `Run NHC` is paused; the live NHC writer is the GHA [nhc-forecast](nhc-forecast.md) pipeline).
- **Dev slot / branch:** the `dev` bundle target auto-pauses and can point at another branch (`--var git_branch`); the live job is the prod target on `main`. No branch mismatch: this page reflects `main`.
- **Doc drift:** the registry says `update.yml` runs "every 6h" (now daily), and `deployments.md` still carries the retired SWA `dsci-monitor` row; see `extra.discrepancies`.

## Downstream consumers

Read-only operational monitor for the DS team; nothing reads `pipelines.json` programmatically. It shows the Databricks jobs tagged `databricks=job`, and each job's `kb` tag links to that pipeline's KB page, e.g. [nhc-forecast](nhc-forecast.md), [imerg](imerg.md). The set changes as jobs are tagged; read the live dashboard or [pipeline-registry.md](../infrastructure/pipeline-registry.md) for the current list.
