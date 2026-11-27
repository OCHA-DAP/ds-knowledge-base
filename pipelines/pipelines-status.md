---
content_type: pipeline
name: pipelines-status
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Update Pipeline Status", ref: ".github/workflows/update.yml", schedule: "15 6 * * * (daily 06:15 UTC since 2026-09-30 — downloads pipelines.json from the dev blob and commits it; was 15 */6 * * * running the fetch itself)", status: live }
    - { name: "Pipeline Status Refresh", ref: "dbx:314917446421609 (databricks.yml job pipeline_status_refresh)", schedule: "0 0 6 * * ? (daily 06:00 UTC, Job Compute; runs scripts/fetch_pipelines.py --to-blob)", status: live }
    - { name: "Azure Static Web Apps CI/CD", ref: ".github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml", schedule: "push/PR to main", status: "removed from the repo 2026-09-30 (the dashboard is served from GitHub Pages)" }
inputs:
  - "Databricks workspace API (jobs tagged databricks=job) via databricks-sdk"
  - "Azure PostgreSQL prod and dev DBs (column defs, row counts, table sizes, timestamp ranges via ocha-stratus.get_engine, plane-first lookup)"
  - "Azure Blob Storage imb0chd0prod / imb0chd0dev (blob size/count per configured container+prefix, via ocha-stratus.get_container_client)"
outputs:
  - "pipelines.json uploaded daily to the dev blob (projects/ds-pipelines-status/) by the Databricks job; update.yml commits it to main as data/pipelines.json at 06:15 UTC if changed"
  - "GitHub Pages site https://ocha-dap.github.io/ds-pipelines-status/ (rebuilt on push to main)"
dependencies:
  - "ocha-stratus>=0.1.7 (DB engines for both planes, blob listing, and the upload of pipelines.json)"
  - "databricks-sdk>=0.20.0"
  - "cron-descriptor>=2.0.0 (schedule display; croniter and the next-run calculation were removed 2026-09-30)"
  - "python-dotenv>=1.0.0"
  - "Secrets: on Databricks, injected by the Job Compute (single node) policy (DSCI_AZ_DB_{DEV,PROD}_* and DSCI_AZ_BLOB_{DEV,PROD}_SAS); the GHA workflow uses only DSCI_AZ_BLOB_DEV_SAS to download the file"
downstream:
  - "Team operational use — the dashboard surfaces Databricks job health and DB/blob output metadata to the whole DS team"
depends_on:
  []  # monitors the Databricks/GHA jobs in the registry; no modelled upstream node (reads job metadata, not a KB-modelled dataset)
surfaces:
  - {url: "https://ocha-dap.github.io/ds-pipelines-status/", kind: dashboard, title: "DSCI Pipeline Status dashboard (Databricks-only; superseded by infrastructure/pipeline-registry.md)"}
source_repo: ocha-dap/ds-pipelines-status
source_branch: main
source_sha: "d899064"
code_ref:
  - "scripts/fetch_pipelines.py"
  - ".github/workflows/update.yml"
  - "databricks.yml"
  # data/pipelines.json deliberately NOT a code_ref: it is regenerated data that changes
  # every run and was re-flagging this page as drift-STALE weekly (kb-drift noise).
  - "index.html + script.js + styles.css"
extra:
  pyproject_name: "ds-pipelines-viz"
  job_discovery: "Databricks jobs are auto-discovered by filtering for the tag databricks=job; no hardcoded job list"
  tag_schema: "Since 2026-09-28 jobs carry type / hazard / kb / output_schema / output_blob / data_mode tags using the KB vocabularies — the canonical table is infrastructure/databricks.md → Job tags"
  output_schema_tag: "Jobs annotated with output_schema (comma-separated schema.table; bare schema names are ignored) get live column/row/size/timestamp-range metadata, looked up in the job's data plane first (data_mode tag, else inferred from job parameters) and the other plane second; each entry records its stage"
  blob_storage_tag: "Jobs annotated with output_blob (comma-separated container/prefix) get total blob size and count per path, same plane-first lookup, via ocha-stratus.get_container_client (since 2026-09-30; was a direct azure-storage-blob SAS call)"
  monitored_pipelines_as_of_2026_11_04: "40 tagged jobs in pipelines.json (generated 2026-11-04 06:07 UTC); the other 27 workspace jobs are untagged and only counted (untagged_jobs). The per-job list is the in_status_dashboard column of infrastructure/pipeline-registry.md; the July 2026 snapshot that used to live here predated the tag convention and the 2026-09-28 deletion of Run NHC."
  not_in_deployments_md: false
  discrepancies:
    - "[resolved] Registered in deployments.md (GHA-pipelines table) and pipeline-registry.md (gha:ds-pipelines-status/update.yml and dbx:314917446421609)."
    - "[resolved 2026-09-30] README.md now describes the daily Databricks job + 06:15 UTC commit; the old 'every 4 hours' / 'every 6 hours' mismatch is gone."
    - "[resolved 2026-09-30] The GHA workflow no longer runs the fetch, so the README's secret list is no longer the runtime secret set; the Databricks job gets its credentials from the compute policy."
    - "[resolved 2026-09-30, fb0a003] Blob sizing moved to ocha-stratus.get_container_client; no direct azure-storage-blob call remains."
    - "[resolved 2026-09-30] azure.storage.blob is no longer imported, so the undeclared-dependency gap is closed."
    - "[resolved 2026-09-30] The DSCI_DATABRICKS_HOST/TOKEN secret mapping only applied while update.yml ran the fetch on the runner."
    - "[resolved 2026-10-01, 896b002] fetch_pipelines.py reads schedule.pause_status; pipelines.json carries a paused flag and the dashboard shows a paused status. The Next Run column it used to mislead was removed 2026-09-30."
    - "[note] pipeline-registry.md and pipelines.json are both daily snapshots (06:49 and 06:07 UTC); for the state right now read the workspace, not either file."
visibility: internal
last_synced: "2026-11-04"
---

# pipelines-status

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Daily: the Databricks job `Pipeline Status Refresh` (06:00 UTC) queries the Jobs API for every job tagged `databricks=job`, enriches each with DB table metadata and blob sizes on both planes, and uploads `pipelines.json` to the dev blob; `update.yml` (06:15 UTC) commits it to `main`, which rebuilds the GitHub Pages dashboard.

> **Slated to be superseded.** This is a Databricks-only, tag-reliant, display-only meta-pipeline. Its blind spots (it only sees jobs tagged `databricks=job`, so any new untagged job is invisible; it can't see any GHA-cron pipeline; it doesn't surface freshness) are documented in [databricks.md](../infrastructure/databricks.md#how-a-pipeline-gets-discovered-today-and-why-were-superseding-it). The intended replacement is the job_id-keyed [pipeline-registry.md](../infrastructure/pipeline-registry.md) spanning **Databricks + GHA**, with last-success-vs-cadence health checks.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Update Pipeline Status | `.github/workflows/update.yml` | `15 6 * * *` (daily 06:15 UTC) + `workflow_dispatch` — since 2026-09-30 a download-and-commit step only (was `15 */6 * * *` running the fetch on the runner) | live |
| Pipeline Status Refresh (Databricks) | `dbx:314917446421609` (`databricks.yml`, job `pipeline_status_refresh`, `source: GIT` on `main`) | `0 0 6 * * ?` (daily 06:00 UTC), Job Compute (single node) policy `0017962FF5D1E3B9` since 2026-10-19 ([ds-pipelines-status#1](https://github.com/OCHA-DAP/ds-pipelines-status/pull/1); was `000C79D951EAF0D6`), `run_as` adm.hker1 (owner adm.tdowning since that deploy), `on_failure` → hannah.ker@un.org | live — new 2026-09-30, 🟢 OK in the registry |
| Azure Static Web Apps CI/CD | `.github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml` | push/PR to main | **removed from the repo 2026-09-30** — the dashboard is served from GitHub Pages (`surfaces`) |

**Databricks → blob since 2026-09-30.** Both Postgres servers are private-endpoint only, so the fetch moved off the GitHub runner: the Databricks job `Pipeline Status Refresh` (`dbx:314917446421609`, `databricks.yml`; spotted by `check_infra_drift.py`, [#711](https://github.com/OCHA-DAP/ds-knowledge-base/issues/711)) runs `scripts/fetch_pipelines.py --to-blob` daily at 06:00 UTC — Jobs API plus the dev **and** prod DBs/blob accounts (creds injected by the Job Compute policy) — and uploads `pipelines.json` to the dev blob at `projects/ds-pipelines-status/pipelines.json`. `update.yml` (06:15 UTC) only downloads that file with `DSCI_AZ_BLOB_DEV_SAS` and commits it. Code changes ship by pushing `main` (`source: GIT`); `bundle deploy` is needed only when the job config changes.

Both run on `main`. The `update.yml` commit of `data/pipelines.json` is what refreshes the GitHub Pages site (the Azure SWA deploy workflow was removed from the repo on 2026-09-30). (Registered in [pipeline-registry.md](../infrastructure/pipeline-registry.md) as `gha:ds-pipelines-status/update.yml`; the Databricks job as `dbx:314917446421609`.)

## Inputs

- **Databricks workspace API** (`databricks-sdk` `WorkspaceClient`; locally from `DATABRICKS_HOST`/`DATABRICKS_TOKEN` in `.env`): all jobs with tag `databricks=job`. Job discovery is dynamic — no hardcoded list. 40 jobs in the 2026-11-04 `pipelines.json`. The other 27 workspace jobs are untagged: `untagged_jobs` holds only their count, and any that are scheduled are listed in `warnings.untagged_scheduled` (none on 2026-11-04). Workspace `adb-6009046713167663` — see [infrastructure/deployments](../infrastructure/deployments.md).
- **Azure PostgreSQL prod AND dev DBs** (via `ocha-stratus.get_engine(stage=...)`, one engine per plane, opened lazily; a plane that fails to connect is skipped with a warning rather than failing the run): column definitions (`information_schema.columns` + `pg_description` comments), row counts (`pg_class.reltuples`), table sizes (`pg_total_relation_size`), and timestamp min/max for tables listed in each job's `output_schema` tag. Each table is looked up in the job's data plane first, then the other.
- **Azure Blob Storage** (`imb0chd0prod` / `imb0chd0dev`, via `ocha-stratus.get_container_client(container, stage=...)`): total blob count and size for each `container/prefix` in a job's `output_blob` tag, same plane-first lookup.

## Steps

1. `fetch_pipelines.py --to-blob` runs as the Databricks job `Pipeline Status Refresh`; the compute policy injects the DB and blob credentials. Locally, `uv run scripts/fetch_pipelines.py` writes `data/pipelines.json` instead.
2. **Job discovery**: `client.jobs.list()` filtered to `tags["databricks"] == "job"`; `client.jobs.get(job_id)` fetches full details per job.
3. **Data plane**: `data_mode` tag, else inferred from job parameters (`data_stage` › `stage` › `mode`, then task `--mode` args), default `prod`. Written as `data_mode`; the page shows a `dev` chip when a job's outputs resolve to dev.
4. **Schema enrichment**: for each `schema.table` in `output_schema`, queries `information_schema.columns` (+ `pg_description`) and `pg_class` for row counts (`reltuples`), table size, and timestamp ranges — in the expected plane first, then the other. Writes results (with `stage`) into the `output_schemas` array.
5. **Blob enrichment**: for each `container/prefix` in `output_blob`, lists blobs and sums sizes, plane-first. Writes a list of entries (with `stage`) into `blob_storage`.
6. **Last run and pause state**: fetches the latest run via `client.jobs.list_runs(job_id, limit=1)` and maps lifecycle/result state to `success|failed|running|unknown`; `paused` comes from `schedule.pause_status` (since 2026-10-01). The next-run calculation was removed on 2026-09-30.
7. Output uploaded to the dev blob at `projects/ds-pipelines-status/pipelines.json` (single JSON dump, `generated_at` always refreshed).
8. `update.yml` downloads that file with `DSCI_AZ_BLOB_DEV_SAS` and runs `git add data/pipelines.json && git diff --staged --quiet || git commit && git push`. Commit only if changed.
9. The push to `main` rebuilds the GitHub Pages site (HTML + JS + JSON).

## Outputs

- **`data/pipelines.json`** — structured JSON committed to the repo; served statically. Contains per-job: name, description, tasks (with git URLs), schedule, last run timing/status, `paused`, compute policy, median duration, type/hazard/kb tags, `data_mode`, output DB table schemas, blob storage stats.
- **Static dashboard** at `https://ocha-dap.github.io/ds-pipelines-status/` — a plain HTML/JS table (`index.html` + `script.js` + `styles.css`) showing each monitored Databricks pipeline's status (failed, running, paused, unknown or success), schedule, duration, compute policy and tags, with a warnings panel for failing jobs, untagged scheduled jobs and scheduled jobs off the job policies. Clicking a job name with `output_schema` opens a modal with full column definitions, row counts, and timestamp ranges.

## Dependencies

- `ocha-stratus>=0.1.7` — DB engines for both planes, blob listing (`get_container_client`) and the upload (`upload_blob_data`)
- `databricks-sdk>=0.20.0` — workspace client
- `cron-descriptor>=2.0.0` — human-readable schedule text (`croniter` and the next-run calculation were removed 2026-09-30)
- `python-dotenv>=1.0.0` — local `.env` loading (production uses GHA secrets)
- **Credentials**: on Databricks, injected by the Job Compute (single node) policy; the only GHA secret is `DSCI_AZ_BLOB_DEV_SAS`, used by `update.yml` to download the file

## Failure modes & debugging

**A failed refresh looks like stale data, not an error:** if the Databricks job fails, the blob file is not replaced and `update.yml` finds nothing new to commit, so the dashboard keeps showing the previous `generated_at`. Check the `Pipeline Status Refresh` run first (`on_failure` emails hannah.ker@un.org), then the "Update Pipeline Status" workflow in the Actions tab for the download step.

**DB access from a laptop:** both servers are private-endpoint only, so a local run needs the SSH tunnel described in [database.md](../infrastructure/database.md) → Network access. No `PGSSLMODE` is needed; `ocha-stratus` negotiates SSL itself (verified 2026-09-30, same page).

**Blob size enumeration fails silently:** `calculate_blob_storage_size()` catches all exceptions and returns `None`. If the plane's blob SAS is expired or missing, blob stats will be absent from `pipelines.json` without a hard failure. Look for `Could not list <stage> blob …` (the listing failed, e.g. an expired SAS) or `No DSCI_AZ_BLOB_<STAGE>_SAS set` in the job run output. Likewise `fetch_table_stats()` swallows all exceptions (`except Exception: pass`) — bad table stats just go missing.

**Row counts from `reltuples` are approximate:** `pg_class.reltuples` is the PostgreSQL stats-based estimate, not an exact `COUNT(*)`. Can be stale if `ANALYZE` has not run recently on large tables.

**A pipeline can be tagged `databricks=job` and still be failing every run** without any alert: the warnings panel lists failing jobs and a click on the Status header sorts them first, but nothing notifies anyone. Each job's own `on_failure` email is the alert path. (The July 2026 examples, `Run ECMWF Storms`, `Run IBTrACS` and `Run FloodScan`, were all 🟢 OK in the 2026-11-04 registry.)

**Adding a new pipeline to the dashboard:** give the job the standard tag block in its `databricks.yml` — `databricks: job` plus `type`, `hazard`, `kb`, `output_schema` (`schema.table`), `output_blob` (`container/prefix`) and a one-line linked `description`; see [infrastructure/databricks.md → Job tags](../infrastructure/databricks.md#job-tags--required-on-every-scheduled-job) for the vocabularies. UI edits only for bundle-less jobs (a deploy resets them). No dashboard code changes needed. The page filters by name / type / hazard / status.

**Local development:** Serve with `python -m http.server 8000` from repo root. Run `uv run scripts/fetch_pipelines.py` to refresh `data/pipelines.json` (requires a `.env` with credentials).

> Tagged gotchas (`[resolved]`/`[note]`) live in `extra.discrepancies` in the frontmatter. Every July 2026 finding on this page is resolved: the page is registered; the fetch runs on Databricks with policy-injected credentials; blob sizing goes through `ocha-stratus`; `azure-storage-blob` is no longer imported; `pause_status` is read and shown. What remains is a note that both the registry and `pipelines.json` are daily snapshots.

## Downstream consumers

The dashboard is a **read-only operational monitor** for the DS team — no other pipeline or app reads `pipelines.json` programmatically. It shows every tagged Databricks job (40 on 2026-11-04); for the per-job list, with KB pages where they exist, use the `in_status_dashboard` column of [pipeline-registry.md](../infrastructure/pipeline-registry.md).
