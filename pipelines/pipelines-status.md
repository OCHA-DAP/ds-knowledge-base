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
  - "Databricks workspace API (jobs tagged databricks=job) via databricks-sdk"
  - "Azure PostgreSQL prod DB (column defs, row counts, table sizes, timestamp ranges via ocha-stratus.get_engine)"
  - "Azure Blob Storage imb0chd0prod (blob size/count per configured container+prefix, via direct SAS-token call)"
outputs:
  - "data/pipelines.json (committed to main every 6h by GHA bot if changed)"
  - "Azure Static Web App: https://thankful-ground-0e9f52a0f.azurestaticapps.net (auto-deployed on push to main)"
dependencies:
  - "ocha-stratus>=0.1.7 (prod DB engine)"
  - "databricks-sdk>=0.20.0"
  - "azure-storage-blob (UNDECLARED in pyproject; imported directly, pulled transitively via ocha-stratus — in uv.lock)"
  - "cron-descriptor>=2.0.0, croniter>=2.0.0 (schedule display + next-run)"
  - "python-dotenv>=1.0.0"
  - "Secrets: DSCI_DATABRICKS_HOST, DSCI_DATABRICKS_TOKEN, DSCI_AZ_DB_PROD_PW, DSCI_AZ_DB_PROD_UID, DSCI_AZ_DB_PROD_HOST, DSCI_AZ_BLOB_PROD_SAS"
downstream:
  - "Team operational use — the dashboard surfaces Databricks job health and DB/blob output metadata to the whole DS team"
depends_on:
  []  # monitors the Databricks/GHA jobs in the registry; no modelled upstream node (reads job metadata, not a KB-modelled dataset)
source_repo: ocha-dap/ds-pipelines-status
source_branch: main
source_sha: "61296a7"
code_ref:
  - "scripts/fetch_pipelines.py"
  - ".github/workflows/update.yml"
  - ".github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml"
  - "data/pipelines.json"
  - "index.html + script.js + styles.css"
extra:
  azure_swa_name: "thankful-ground-0e9f52a0f"
  pyproject_name: "ds-pipelines-viz"
  job_discovery: "Databricks jobs are auto-discovered by filtering for the tag databricks=job; no hardcoded job list"
  output_schema_tag: "Jobs annotated with output_schema tag (comma-separated table names, e.g. storms.nhc_storms) get live column/row/size/timestamp-range metadata fetched from prod DB and embedded in pipelines.json"
  blob_storage_tag: "Jobs annotated with blob_container (and optional blob_prefix) get total blob size and count embedded; uses direct Azure SDK SAS-token call, not ocha-stratus (diverges from team convention)"
  monitored_pipelines_as_of_2026_07_02:
    - "Run NHC (every 3h, ds-storms-pipeline) — PAUSED per pipeline-registry.md (dbx:266763033249426); last recorded run 2026-06-09 FAILED (not a success — deprecated Databricks path; live NHC writer is the GHA ds-nhc-forecast pipeline, itself currently failing per the registry)"
    - "Run ECMWF Storms (daily 22:00 UTC, ds-storms-pipeline) — last run 2026-07-01 FAILED; registry shows 🔴 DOWN, FAILING/NO-SUCCESS"
    - "Run IBTrACS (daily 16:00 UTC, ds-storms-pipeline) — last run 2026-07-02 FAILED; registry shows 🔴 DOWN, FAILING/NO-SUCCESS"
    - "Run FloodScan (daily 20:00 UTC, ds-raster-pipelines + ds-raster-stats) — last run 2026-07-01 FAILED (newly broken since the last sync; pipeline-registry.md's 2026-06-29 snapshot still shows it 🟢 OK — that snapshot predates this failure and is now stale)"
    - "Run ERA5 (monthly day 6 12:00 UTC, ds-raster-pipelines + ds-raster-stats) — last run 2026-06-06 success"
    - "Run IMERG (daily 14:40 UTC, ds-raster-pipelines + ds-raster-stats) — last run 2026-07-02 success"
    - "Run SEAS5 (monthly day 5 12:30 UTC, ds-raster-pipelines + ds-raster-stats) — last run 2026-06-05 success"
  not_in_deployments_md: false
  discrepancies:
    - "[resolved] Previously flagged as missing from infrastructure/deployments.md — it is now registered: deployments.md GHA-pipelines table (the `pipelines-status` row) and pipeline-registry.md (`gha:ds-pipelines-status/update.yml`, last seen 🟢 OK)."
    - "[stale] README.md says the update job 'runs every 4 hours'; the actual cron in update.yml is `15 */6 * * *` (every 6h). Code is authoritative — README is stale."
    - "[stale] README.md lists only DATABRICKS_HOST/DATABRICKS_TOKEN/DSCI_AZ_BLOB_PROD_SAS as required secrets; the live update.yml also injects DSCI_AZ_DB_PROD_PW/UID/HOST (needed for the prod-DB schema enrichment). README understates the secret set."
    - "[conflict] Blob size enrichment uses a direct azure-storage-blob SAS-token call to imb0chd0prod, not ocha-stratus — diverges from the team convention (all blob/DB access via stratus). DB access here does go through stratus.get_engine(stage='prod')."
    - "[gap] azure.storage.blob is imported in fetch_pipelines.py but azure-storage-blob is NOT a declared dependency in pyproject.toml — it resolves only transitively (via ocha-stratus; present in uv.lock). If ocha-stratus ever drops it, the blob-size step breaks at import."
    - "[stale] env-var naming: update.yml maps GHA secrets DSCI_DATABRICKS_HOST/DSCI_DATABRICKS_TOKEN onto the runtime env vars DATABRICKS_HOST/DATABRICKS_TOKEN that the databricks-sdk WorkspaceClient reads; the DSCI_-prefixed names are the GHA secret names, not the names the script reads at runtime."
    - "[gap] fetch_pipelines.py never reads job.settings.schedule.pause_status — get_job_schedule() and get_next_run() compute the cron description and next-run time purely from the quartz expression, blind to whether the job's schedule is actually PAUSED in Databricks. A paused job (e.g. Run NHC) still shows a plausible future 'Next Run' time on the dashboard; the only tell is a stale 'Last Run' timestamp. There is no explicit paused indicator anywhere in pipelines.json or the UI."
    - "[stale] pipeline-registry.md's 2026-06-29 snapshot lists Run FloodScan as 🟢 OK; the live pipelines.json (generated 2026-07-02) shows its 2026-07-01 run FAILED. The registry snapshot is a point-in-time dump and lags the dashboard's own 6h refresh — cross-check both, don't trust either alone as of-right-now."
visibility: internal
last_synced: "2026-07-02"
---

# pipelines-status

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Every 6 hours: query Databricks for all jobs tagged `databricks=job`, enrich with prod DB table metadata and Azure blob sizes, commit `data/pipelines.json` to main; Azure Static Web Apps auto-deploys the static dashboard on every push.

> **Slated to be superseded.** This is a Databricks-only, tag-reliant, display-only meta-pipeline. Its blind spots (it watches the tagged-but-PAUSED `Run NHC` and misses the live untagged GHA NHC pipeline; it can't see any GHA-cron pipeline) are documented in [databricks.md](../infrastructure/databricks.md#how-a-pipeline-gets-discovered-today-and-why-were-superseding-it). The intended replacement is the job_id-keyed [pipeline-registry.md](../infrastructure/pipeline-registry.md) spanning **Databricks + GHA**, with last-success-vs-cadence health checks.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Update Pipeline Status | `.github/workflows/update.yml` | `15 */6 * * *` (every 6h at :15) | live |
| Azure Static Web Apps CI/CD | `.github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml` | push/PR to main | live |

Both workflows run on `main`. The `update.yml` job commits `data/pipelines.json` to main; that commit then triggers the SWA deploy workflow to push the updated static site. (Registered in [pipeline-registry.md](../infrastructure/pipeline-registry.md) as `gha:ds-pipelines-status/update.yml`.)

## Inputs

- **Databricks workspace API** (GHA secrets `DSCI_DATABRICKS_HOST`/`DSCI_DATABRICKS_TOKEN`, injected into the runtime env vars `DATABRICKS_HOST`/`DATABRICKS_TOKEN` that the `databricks-sdk` `WorkspaceClient` reads): all jobs with tag `databricks=job`. Job discovery is dynamic — no hardcoded list. 7 pipelines visible as of 2026-07-02 (workspace `adb-6009046713167663` — see [infrastructure/deployments](../infrastructure/deployments.md)).
- **Azure PostgreSQL prod DB** (via `ocha-stratus.get_engine(stage="prod")`): column definitions (`information_schema.columns` + `pg_description` comments), row counts (`pg_class.reltuples`), table sizes (`pg_total_relation_size`), and timestamp min/max for tables listed in each job's `output_schema` tag.
- **Azure Blob Storage** (`imb0chd0prod`, direct SAS-token call via `azure-storage-blob`): total blob count and size for jobs that carry a `blob_container` tag (and optional `blob_prefix`). Note: this is a direct SDK call, not `ocha-stratus` — a divergence from team convention (see Failure modes).

## Steps

1. `fetch_pipelines.py` is invoked by `update.yml` with credentials injected as env vars.
2. **Job discovery**: `client.jobs.list()` filtered to `tags["databricks"] == "job"`; `client.jobs.get(job_id)` fetches full details per job.
3. **Schema enrichment**: for each job with an `output_schema` tag, queries `information_schema.columns` (+ `pg_description` for column comments) and `pg_class` for row counts (via `reltuples`), table size, and timestamp ranges. Writes results into `output_schemas` array.
4. **Blob enrichment**: for each job with a `blob_container` tag, lists all blobs under the prefix and sums sizes. Writes into `blob_storage` dict.
5. **Last/next run**: fetches latest run via `client.jobs.list_runs(job_id, limit=1)`, maps lifecycle/result state to `success|failed|running|unknown`. Next run computed from the Quartz cron (converted to 5-field standard cron) via `croniter`.
6. Output written to `data/pipelines.json` (single JSON dump, `generated_at` timestamp always refreshed).
7. GHA bot runs `git add data/pipelines.json && git diff --staged --quiet || git commit && git push`. Commit only if changed.
8. On push to main, Azure Static Web Apps CI/CD deploys the updated static files (HTML + JS + JSON) to the SWA endpoint.

## Outputs

- **`data/pipelines.json`** — structured JSON committed to repo; served statically. Contains per-job: name, description, tasks (with git URLs), schedule, last run timing/status, next run, type tags, `job_status`, output DB table schemas, blob storage stats.
- **Static dashboard** at `https://thankful-ground-0e9f52a0f.azurestaticapps.net` — a plain HTML/JS table (`index.html` + `script.js` + `styles.css`) showing each monitored Databricks pipeline's last run status, schedule, next run, and tags. Clicking a job name with `output_schema` opens a modal with full column definitions, row counts, and timestamp ranges.

## Dependencies

- `ocha-stratus>=0.1.7` — prod DB engine only (no blob access here; blob uses raw SDK)
- `databricks-sdk>=0.20.0` — workspace client
- `azure-storage-blob` — direct SAS-token blob size enumeration. **Imported but not declared in `pyproject.toml`** — only resolves transitively via `ocha-stratus` (present in `uv.lock`).
- `cron-descriptor>=2.0.0`, `croniter>=2.0.0` — schedule parsing (Quartz→standard cron) and next-run calculation
- `python-dotenv>=1.0.0` — local `.env` loading (production uses GHA secrets)
- **GHA secrets required**: `DSCI_DATABRICKS_HOST`, `DSCI_DATABRICKS_TOKEN`, `DSCI_AZ_DB_PROD_PW`, `DSCI_AZ_DB_PROD_UID`, `DSCI_AZ_DB_PROD_HOST`, `DSCI_AZ_BLOB_PROD_SAS`
- **Azure Static Web Apps token**: `AZURE_STATIC_WEB_APPS_API_TOKEN_THANKFUL_GROUND_0E9F52A0F`

## Failure modes & debugging

**GHA update job fails silently:** If `fetch_pipelines.py` raises, the commit step never fires, so `data/pipelines.json` is not updated. The dashboard will show stale data but won't error visibly — check the Actions tab for the "Update Pipeline Status" workflow.

**DB credential misconfiguration (`PGSSLMODE`):** Azure PostgreSQL requires SSL. `ocha-stratus.get_engine()` handles this, but locally the `.env` must set `PGSSLMODE=require` — otherwise `get_engine()` raises an SSL error. See [infrastructure/conventions.md](../infrastructure/conventions.md).

**Blob size enumeration fails silently:** `calculate_blob_storage_size()` catches all exceptions and returns `None`. If `DSCI_AZ_BLOB_PROD_SAS` is expired or missing, blob stats will be absent from `pipelines.json` without a hard failure. Look for `Error calculating blob storage size` in the GHA step log. Likewise `fetch_table_stats()` swallows all exceptions (`except Exception: pass`) — bad table stats just go missing.

**Row counts from `reltuples` are approximate:** `pg_class.reltuples` is the PostgreSQL stats-based estimate, not an exact `COUNT(*)`. Can be stale if `ANALYZE` has not run recently on large tables.

**`Run NHC` shows no recent runs:** The Databricks `Run NHC` job (`266763033249426`) is **PAUSED** per [pipeline-registry.md](../infrastructure/pipeline-registry.md) (`dbx:266763033249426`); its last recorded run (2026-06-09) **failed** — it is the deprecated Databricks path, and the intended live NHC writer is the GHA `ds-nhc-forecast` pipeline (see [pipelines/nhc-forecast](nhc-forecast.md)), which per the registry is itself currently failing. **The dashboard does not surface "paused" at all** — `get_job_schedule()`/`get_next_run()` in `fetch_pipelines.py` read only the quartz cron expression, never `job.settings.schedule.pause_status`, so a paused job still shows a plausible future "Next Run" time. The only visible tell on the page is a stale "Last Run" timestamp/status.

**A pipeline can be tagged `databricks=job` and still be failing every run** without any special dashboard treatment: `Run ECMWF Storms` and `Run IBTrACS` are both discovered and rendered normally, but their `last_run.status` is `failed` on every recent run (registry: 🔴 DOWN, FAILING/NO-SUCCESS). As of the 2026-07-02 refresh, `Run FloodScan` joined them — its 2026-07-01 run also shows `failed`, a regression from the 🟢 OK it carried in the 2026-06-29 `pipeline-registry.md` snapshot. The dashboard shows all of these correctly via the red "failed" status pill — it's not a blind spot, but it's easy to skim past in a table of otherwise-green rows, and the two sources (this live dashboard vs. the point-in-time registry snapshot) can disagree on any given day.

**Adding a new pipeline to the dashboard:** Tag the Databricks job with `databricks=job` in the Databricks UI or `databricks.yml`. Optionally add `type`, `output_schema`, `blob_container`, `blob_prefix`, and `status=development` tags. No code changes needed.

**Local development:** Serve with `python -m http.server 8000` from repo root. Run `uv run scripts/fetch_pipelines.py` to refresh `data/pipelines.json` (requires a `.env` with credentials).

> Tagged gotchas (`[stale]`/`[conflict]`/`[gap]`/`[resolved]`) live in `extra.discrepancies` in the frontmatter: now registered in `deployments.md`/`pipeline-registry.md` `[resolved]`; the README's "every 4 hours" is stale (real cron every 6h) `[stale]`; blob enrichment bypasses `ocha-stratus` `[conflict]`; `azure-storage-blob` is imported but undeclared in `pyproject.toml` `[gap]`; `pause_status` is never read, so paused jobs get no explicit indicator `[gap]`; the `pipeline-registry.md` 2026-06-29 snapshot vs. this dashboard's 2026-07-02 refresh disagree on `Run FloodScan`'s health `[stale]`.

## Downstream consumers

The dashboard is a **read-only operational monitor** for the DS team — no other pipeline or app reads `pipelines.json` programmatically. It gives visibility into the health of the 7 monitored Databricks jobs:

- [pipelines/nhc-forecast](nhc-forecast.md) (`Run NHC`)
- `Run ECMWF Storms` — ds-storms-pipeline (no separate KB page yet)
- [pipelines/imerg](imerg.md) (`Run IMERG`)
- `Run FloodScan`, `Run ERA5`, `Run SEAS5` — ds-raster-pipelines + ds-raster-stats (KB pages TBD)
- `Run IBTrACS` — ds-storms-pipeline (no separate KB page yet)
