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
    - { name: "Azure Static Web Apps CI/CD", ref: ".github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml", schedule: "push to main", status: live }
inputs:
  - "Databricks workspace API (jobs tagged databricks=job) via databricks-sdk"
  - "Azure PostgreSQL prod DB (table metadata, row counts, timestamp ranges via ocha-stratus)"
  - "Azure Blob Storage imb0chd0prod (blob size/count per configured container+prefix, via SAS token)"
outputs:
  - "data/pipelines.json (committed to main every 6h by GHA bot if changed)"
  - "Azure Static Web App: https://thankful-ground-0e9f52a0f.azurestaticapps.net (auto-deployed on push to main)"
dependencies:
  - "ocha-stratus>=0.1.7 (prod DB engine)"
  - "databricks-sdk>=0.20.0"
  - "azure-storage-blob (direct SAS-token access to imb0chd0prod)"
  - "cron-descriptor, croniter (schedule display)"
  - "python-dotenv"
  - "Secrets: DSCI_DATABRICKS_HOST, DSCI_DATABRICKS_TOKEN, DSCI_AZ_DB_PROD_PW, DSCI_AZ_DB_PROD_UID, DSCI_AZ_DB_PROD_HOST, DSCI_AZ_BLOB_PROD_SAS"
downstream:
  - "Team operational use — the dashboard surfaces Databricks job health and DB/blob output metadata to the whole DS team"
depends_on:
  - "infrastructure/deployments"
  - "infrastructure/database"
  - "infrastructure/storage"
source_repo: ocha-dap/ds-pipelines-status
source_branch: main
source_sha: "7895641"
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
  output_schema_tag: "Jobs annotated with output_schema tag (comma-separated table names, e.g. storms.nhc_tracks) get live column/row/size metadata fetched from prod DB and embedded in pipelines.json"
  blob_storage_tag: "Jobs annotated with blob_container (and optional blob_prefix) get total blob size and count embedded; uses direct Azure SDK SAS-token call, not ocha-stratus (diverges from team convention)"
  monitored_pipelines_as_of_2026_06_22:
    - "Run NHC (every 3h, ds-storms-pipeline)"
    - "Run ECMWF Storms (daily 22:00 UTC, ds-storms-pipeline)"
    - "Run IBTrACS (daily 16:00 UTC, ds-storms-pipeline)"
    - "Run FloodScan (daily 20:00 UTC, ds-raster-pipelines + ds-raster-stats)"
    - "Run ERA5 (monthly day 6, ds-raster-pipelines + ds-raster-stats)"
    - "Run IMERG (daily 14:40 UTC, ds-raster-pipelines + ds-raster-stats)"
    - "Run SEAS5 (monthly day 5, ds-raster-pipelines + ds-raster-stats)"
  not_in_deployments_md: true
  discrepancies:
    - "[gap] This pipeline (the GHA `update.yml` job + the `thankful-ground-0e9f52a0f` Azure Static Web App) is NOT in infrastructure/deployments.md — neither the GHA-pipelines table nor the Azure web-apps table (SWAs are a separate Azure resource from the App Service apps listed there). Add it on next deployments refresh."
    - "[stale] README.md says the update job 'runs every 4 hours'; the actual cron in update.yml is `15 */6 * * *` (every 6h). Code is authoritative — README is stale."
    - "[stale] README.md lists only DATABRICKS_HOST/DATABRICKS_TOKEN/DSCI_AZ_BLOB_PROD_SAS as required secrets; the live update.yml also injects DSCI_AZ_DB_PROD_PW/UID/HOST (needed for the prod-DB schema enrichment). README understates the secret set."
    - "[conflict] Blob size enrichment uses a direct azure-storage-blob SAS-token call to imb0chd0prod, not ocha-stratus — diverges from the team convention (all blob/DB access via stratus). DB access here does go through stratus.get_engine(stage='prod')."
    - "[stale] env-var naming: update.yml maps secrets DSCI_DATABRICKS_HOST/DSCI_DATABRICKS_TOKEN onto the runtime env vars DATABRICKS_HOST/DATABRICKS_TOKEN that the databricks-sdk WorkspaceClient reads; the DSCI_-prefixed names are the GHA secret names, not the names the script reads at runtime."
visibility: internal
last_synced: "2026-06-22"
---

# pipelines-status

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Every 6 hours: query Databricks for all jobs tagged `databricks=job`, enrich with prod DB table metadata and Azure blob sizes, commit `data/pipelines.json` to main; Azure Static Web Apps auto-deploys the static dashboard on every push.

> **Slated to be superseded.** This is a Databricks-only, tag-reliant, display-only meta-pipeline. Its blind spots (it watches the tagged-but-PAUSED `Run NHC` and misses the live untagged `NHC Pipeline`; it can't see any GHA-cron pipeline) are documented in [databricks.md](../infrastructure/databricks.md#how-a-pipeline-gets-discovered-today-and-why-were-superseding-it). The intended replacement is the job_id-keyed [prod-pipeline registry](../infrastructure/deployments.md#databricks-jobs--prod-pipeline-registry) spanning **Databricks + GHA**, with cadence/freshness health checks.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Update Pipeline Status | `.github/workflows/update.yml` | `15 */6 * * *` (every 6h at :15) | live |
| Azure Static Web Apps CI/CD | `.github/workflows/azure-static-web-apps-thankful-ground-0e9f52a0f.yml` | push/PR to main | live |

Both workflows run on `main`. The `update.yml` job commits `data/pipelines.json` to main; that commit then triggers the SWA deploy workflow to push the updated static site.

## Inputs

- **Databricks workspace API** (GHA secrets `DSCI_DATABRICKS_HOST`/`DSCI_DATABRICKS_TOKEN`, injected into the runtime env vars `DATABRICKS_HOST`/`DATABRICKS_TOKEN` that the `databricks-sdk` `WorkspaceClient` reads): all jobs with tag `databricks=job`. Job discovery is dynamic — no hardcoded list. 7 pipelines visible as of 2026-06-22 (workspace `adb-6009046713167663`, profile `default` — see [infrastructure/deployments](../infrastructure/deployments.md)).
- **Azure PostgreSQL prod DB** (via `ocha-stratus.get_engine(stage="prod")`): column definitions, row counts, table sizes, and timestamp min/max for tables listed in each job's `output_schema` tag.
- **Azure Blob Storage** (`imb0chd0prod`, direct SAS-token call via `azure-storage-blob`): total blob count and size for jobs that carry a `blob_container` tag (and optional `blob_prefix`). Note: this is a direct SDK call, not `ocha-stratus` — a divergence from team convention (see Failure modes).

## Steps

1. `fetch_pipelines.py` is invoked by `update.yml` with credentials injected as env vars.
2. **Job discovery**: `client.jobs.list()` filtered to `tags["databricks"] == "job"`. Full job details fetched per job.
3. **Schema enrichment**: for each job with an `output_schema` tag, queries `information_schema.columns` and `pg_class` for column types, row counts (via `reltuples`), and timestamp ranges. Writes results into `output_schemas` array.
4. **Blob enrichment**: for each job with a `blob_container` tag, lists all blobs under the prefix and sums sizes. Writes into `blob_storage` dict.
5. **Last/next run**: fetches latest run via `client.jobs.list_runs(limit=1)`, maps lifecycle state to `success|failed|running|unknown`. Next run computed from cron.
6. Output written atomically to `data/pipelines.json`.
7. GHA bot runs `git add data/pipelines.json && git diff --staged --quiet || git commit && git push`. Commit only if changed.
8. On push to main, Azure Static Web Apps CI/CD deploys the updated static files (HTML + JS + JSON) to the SWA endpoint.

## Outputs

- **`data/pipelines.json`** — structured JSON committed to repo; served statically. Contains per-job: name, description, tasks (with git URLs), schedule, last run timing/status, next run, tags, output DB table schemas, blob storage stats.
- **Static dashboard** at `https://thankful-ground-0e9f52a0f.azurestaticapps.net` — a plain HTML/JS table showing each monitored Databricks pipeline's last run status, schedule, next run, and tags. Clicking a job name with `output_schema` opens a modal with full column definitions, row counts, and timestamp ranges.

## Dependencies

- `ocha-stratus>=0.1.7` — prod DB engine only (no blob access here; blob uses raw SDK)
- `databricks-sdk>=0.20.0` — workspace client
- `azure-storage-blob` — direct SAS-token blob size enumeration
- `cron-descriptor`, `croniter` — schedule parsing and next-run calculation
- `python-dotenv` — local `.env` loading (production uses GHA secrets)
- **GHA secrets required**: `DSCI_DATABRICKS_HOST`, `DSCI_DATABRICKS_TOKEN`, `DSCI_AZ_DB_PROD_PW`, `DSCI_AZ_DB_PROD_UID`, `DSCI_AZ_DB_PROD_HOST`, `DSCI_AZ_BLOB_PROD_SAS`
- **Azure Static Web Apps token**: `AZURE_STATIC_WEB_APPS_API_TOKEN_THANKFUL_GROUND_0E9F52A0F`

## Failure modes & debugging

**GHA update job fails silently:** If `fetch_pipelines.py` raises, the commit step never fires, so `data/pipelines.json` is not updated. The dashboard will show stale data but won't error visibly — check the Actions tab for the "Update Pipeline Status" workflow.

**DB credential misconfiguration (`PGSSLMODE`):** Azure PostgreSQL requires SSL. `ocha-stratus.get_engine()` handles this, but locally the `.env` must set `PGSSLMODE=require` — otherwise `get_engine()` raises an SSL error. See [infrastructure/conventions.md](../infrastructure/conventions.md).

**Blob size enumeration fails silently:** `calculate_blob_storage_size()` catches all exceptions and returns `None`. If `DSCI_AZ_BLOB_PROD_SAS` is expired or missing, blob stats will be absent from `pipelines.json` without a hard failure. Look for `Error calculating blob storage size` in the GHA step log.

**Row counts from `reltuples` are approximate:** `pg_class.reltuples` is the PostgreSQL stats-based estimate, not an exact `COUNT(*)`. Can be stale if `ANALYZE` has not run recently on large tables.

**Dashboard shows stale `generated_at`:** The GHA job only commits if `pipelines.json` changes (diff guard). If no Databricks data changes, the file won't update even on a successful run — `generated_at` will still move (timestamp always changes), so in practice the diff will almost always fire.

**`Run NHC` shows repeated failures:** As of 2026-06-22, the last successful run of `Run NHC` was 2026-06-09; it has been failing since. The Databricks job `266763033249426` is listed as `PAUSED` in `deployments.md` — the GHA-based NHC pipeline is the live path (see [pipelines/nhc-forecast](nhc-forecast.md)). The status dashboard correctly reflects the Databricks job state (failing/paused) because it queries Databricks directly.

**Adding a new pipeline to the dashboard:** Tag the Databricks job with `databricks=job` in the Databricks UI or `databricks.yml`. Optionally add `type`, `output_schema`, `blob_container`, `blob_prefix`, and `status=development` tags. No code changes needed.

**Local development:** Serve with `python -m http.server 8000` from repo root. Run `uv run scripts/fetch_pipelines.py` to refresh `data/pipelines.json` (requires a `.env` with credentials).

> Tagged gotchas (`[stale]`/`[conflict]`/`[gap]`) live in `extra.discrepancies` in the frontmatter: this pipeline is **not yet in `infrastructure/deployments.md`** `[gap]`; the README's "every 4 hours" is stale (real cron is every 6h) `[stale]`; blob enrichment bypasses `ocha-stratus` `[conflict]`.

## Downstream consumers

The dashboard is a **read-only operational monitor** for the DS team — no other pipeline or app reads `pipelines.json` programmatically. It gives visibility into the health of the 7 monitored Databricks jobs:

- [pipelines/nhc-forecast](nhc-forecast.md) (`Run NHC`)
- `Run ECMWF Storms` — ds-storms-pipeline (no separate KB page yet)
- [pipelines/imerg](imerg.md) (`Run IMERG`)
- `Run FloodScan`, `Run ERA5`, `Run SEAS5` — ds-raster-pipelines + ds-raster-stats (KB pages TBD)
- `Run IBTrACS` — ds-storms-pipeline (no separate KB page yet)
