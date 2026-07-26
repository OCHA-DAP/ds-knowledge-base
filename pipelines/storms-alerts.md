---
content_type: pipeline
name: storms-alerts
type: alert
status: live
deployment:
  platform: databricks-job
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - name: "Storm Alert"
      ref: "500881901438881"
      schedule: "0 30 3,9,15,21 * * ? (UTC) — 30 min after each NHC advisory"
      status: live
    - name: "Run Storm Alert (GHA)"
      ref: ".github/workflows/run_alert.yml"
      schedule: "cron '30 3,9,15,21 * * *' (UTC) still in the file, but workflow is disabled_manually at the repo level — effectively workflow_dispatch only"
      status: paused
    - name: "Build and deploy to chd-ds-storms-alerts (Azure)"
      ref: ".github/workflows/main_chd-ds-storms-alerts.yml"
      schedule: "push to main"
      status: live
    - name: "Build and deploy to chd-ds-storms-alerts (Azure, DUPLICATE)"
      ref: ".github/workflows/initial-pipeline_chd-ds-storms-alerts.yml"
      schedule: "push (to the initial-pipeline branch)"
      status: live
    - name: "GH Pages build (subscribe form)"
      ref: "pages-build-deployment (GitHub-managed)"
      schedule: "push to docs/ on the Pages branch"
      status: live
inputs:
  - "DB (dev stage): storms.nhc_tracks_fcastonly_exposure — track-based forecast exposure (adm0 + adm1)"
  - "DB (dev stage): storms.nhc_tracks_obsv_exposure — cumulative observed exposure (adm0 + adm1)"
  - "DB (dev stage): storms.nhc_wsp_fcastonly_exposure — WSP probabilistic forecast exposure (adm0)"
  - "DB (dev stage): storms.nhc_wsp_fcastonly_polygon — WSP probability polygons for maps"
  - "DB (dev stage): storms.nhc_tracks_geo — raw track points for storm maps"
  - "DB (dev stage): storms.nhc_tracks_fcastonly_buffers — deterministic wind radii polygons"
  - "DB (dev stage): storms.nhc_tracks_obsv_buffers — observed wind radii polygons"
  - "DB (dev stage): storms.gdacs_exposure — GDACS pop-exposure (adm0 + adm1)"
  - "DB (dev stage): storms.adam_exposure — ADAM pop-exposure (adm0 + adm1)"
  - "DB (dev stage): storms.storm_id_lookup — cross-source storm ID mapping (atcf_id ↔ gdacs_eventid ↔ adam_eventid)"
  - "DB (dev stage): storms.nhc_storms — storm name/season from NHC"
  - "DB (dev stage): storms.ibtracs_storms — storm name/season fallback from IBTrACS"
  - "DB (dev stage): storms.gdacs_fm_lookup — GDACS admin code → FieldMaps pcode crosswalk"
  - "DB (dev stage): storms.adam_fm_lookup — ADAM admin name → FieldMaps pcode crosswalk (case-insensitive)"
  - "DB (dev stage): storms.admin_population — country total population (adm0)"
  - "Blob (global container): fieldmaps/edge-matched/humanitarian/intl/adm1/{iso3}.parquet — FieldMaps adm1 boundaries"
  - "Blob (global container): fieldmaps/edge-matched/humanitarian/intl/adm0/{iso3}.parquet — FieldMaps adm0 boundaries (pre-dissolved)"
  - "Repo: data/ne110m_countries.parquet — Natural Earth 110m world countries for map background"
outputs:
  - "Listmonk: per-country subscriber lists (tagged ds-storms-alerts, iso3:<code>) — exposure alert emails"
  - "Listmonk: aggregate:all list — all advisories"
  - "Listmonk: aggregate:lac list — any LAC-country advisory"
  - "Listmonk: aggregate:monitoring list — no-exposure monitoring emails (active storms, no affected countries)"
  - "Email attachment: per-storm styled xlsx workbook (tabs README/adm0_exposure/adm1_exposure/caveats; was a flat CSV before ds-storms-alerts PR #20) — mirrors the ds-storm-impact-harmonisation archive workbook"
  - "GH Pages: subscribe/unsubscribe form at ocha-dap.github.io/ds-storms-alerts"
  - "Azure web app (chd-ds-storms-alerts): guide.html static page"
dependencies:
  - "ocha-stratus>=0.1.7 — DB and blob access"
  - "ocha-relay (pinned git SHA 2d4870749faa4235e65164b731e0a574a2e209ab) — Listmonk client"
  - "matplotlib>=3.9, geopandas — maps and strip charts"
  - "Databricks cluster 0515-161935-i2w5mxhc — carries DSCI_AZ_* env vars for DB/blob auth"
  - "Databricks secret scope dsci: DSCI_LISTMONK_BASE_URL, DSCI_LISTMONK_API_USERNAME, DSCI_LISTMONK_API_KEY"
  - "Listmonk instance: https://listmonk-demo-afhcg8e2hde0fxca.eastus2-01.azurewebsites.net"
downstream:
  - "Human subscribers via Listmonk per-country and aggregate lists (terminal output)"
  - "apps/glb-tropicalcyclones-app — only indirectly: it reads the same storms DB schema, not this pipeline's email output"
depends_on: [storms-pipeline, listmonk]
source_repo: ocha-dap/ds-storms-alerts
source_branch: adm1-exposure-csv
source_sha: de38cb5
code_ref:
  - "pipelines/run_alert.py — main pipeline: fetch → render → email"
  - "src/data.py — all DB/blob fetches"
  - "src/plots.py — strip charts and storm maps"
  - "src/constants.py — list IDs, country sets"
  - "databricks/run_alert_job.py — DBX wrapper: injects listmonk creds, shells out"
  - "databricks/README.md — operational runbook (deploy/run commands, gotchas)"
  - "databricks.yml — Databricks Asset Bundle definition"
  - ".github/workflows/run_alert.yml — legacy GHA schedule (now disabled)"
  - ".github/workflows/main_chd-ds-storms-alerts.yml — GHA deploy to Azure web app"
extra:
  data_stage_note: "Pipeline reads from DEV database for all targets (prod Databricks job included). The databricks.yml stage variable defaults to 'dev'; a prod cutover requires deploying with --var stage=prod once the upstream storms-pipeline writes to prod."
  listmonk_test_list_id: 5
  advisory_offset_hours: 3
  wind_thresholds_kt: [34, 50, 64]
  exposure_combination_method: "MAX across CHD/ADAM/GDACS per (storm, country, wind speed) — bias to action"
  adm1_harmonization: "GDACS/ADAM admin units mapped to FieldMaps pcodes via storms.gdacs_fm_lookup / storms.adam_fm_lookup; source set held consistent across all adm1 units within a storm-country per wind speed"
  gha_schedule_note: "The GHA 'Run Storm Alert' workflow is disabled_manually at the repo level (workflow_dispatch only); the cron is still in the file but does not fire. Databricks (job 500881901438881) is the scheduler since GHA trigger latency degraded to ~1h late."
  azure_app_note: "chd-ds-storms-alerts Azure web app serves the static subscriber form + guide page only; the pipeline logic does not run on the web app."
discrepancies:
  - "[stale] A duplicate Azure-deploy workflow `initial-pipeline_chd-ds-storms-alerts.yml` is still active in GitHub Actions and still fires on pushes to the `initial-pipeline` branch (last deploy 2026-06-08), but the file is gone from main/adm1-exposure-csv. Both deploy to the same chd-ds-storms-alerts app. Leftover from the original Azure portal CI/CD setup — should be deleted."
  - "[conflict] Page is ingested from branch `adm1-exposure-csv` (de38cb5), but the live Databricks job pulls `${var.git_branch}` default `main`. Changes on adm1-exposure-csv will NOT run in prod until merged to main or the job is redeployed with --var git_branch=adm1-exposure-csv."
  - "[gap] The prod Databricks job reads the DEV database/blob stage (stage defaults to 'dev' end-to-end). No prod cutover until ds-storms-pipeline writes prod; until then a dev-data outage silently produces zero-exposure emails."
visibility: internal
last_synced: "2026-06-18"
---

# Storm Alerts

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Four times daily: check the NHC advisory hour → query DB for forecast + observed exposure across CHD/ADAM/GDACS → render per-country strip charts and storm maps → email a consolidated HTML alert + a per-storm styled xlsx exposure workbook via Listmonk.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Storm Alert (Databricks) | `500881901438881` | `0 30 3,9,15,21 * * ?` UTC — 30 min after each NHC advisory | live (UNPAUSED; firing PERIODIC, last confirmed 2026-06-18 09:30 UTC) |
| Run Storm Alert (GHA) | `.github/workflows/run_alert.yml` | file still has `30 3,9,15,21 * * *` UTC cron | paused — workflow is `disabled_manually` at the repo level (last scheduled run 2026-06-08); `workflow_dispatch` only |
| Azure web app deploy | `.github/workflows/main_chd-ds-storms-alerts.yml` | push to `main` | live |
| Azure web app deploy (DUPLICATE) | `.github/workflows/initial-pipeline_chd-ds-storms-alerts.yml` | push (to the `initial-pipeline` branch) | live — stale duplicate, see below |
| GH Pages build | `pages-build-deployment` (GitHub-managed) | push to `docs/` on the Pages branch | live |

The Databricks job (`500881901438881`) is the canonical scheduler — UNPAUSED and confirmed firing 4x/day (PERIODIC trigger, runs verified through 2026-06-18). It clones the repo at `${var.git_branch}` (default: `main`) at run time via `source: GIT`, so pushing main updates the next run without a redeploy. The GHA `run_alert.yml` schedule was disabled (`disabled_manually`) after latency degraded to ~1 hour late — the `30 3,9,15,21 * * *` cron is still present in the workflow file but does NOT fire while the workflow is disabled; re-enable via `gh workflow enable "Run Storm Alert"`.

The Azure deploy workflow pushes the static `docs/` subscriber form to `chd-ds-storms-alerts` on each `main` push — it does NOT run the pipeline. **Gotcha:** a second, near-identical Azure deploy workflow (`initial-pipeline_chd-ds-storms-alerts.yml`) is still **active in GitHub Actions and still firing** on pushes to the `initial-pipeline` branch (last deploy 2026-06-08), even though the file is no longer present in the `main`/`adm1-exposure-csv` working trees. Both deploy to the same `chd-ds-storms-alerts` Azure app — a leftover from the original Azure portal CI/CD setup that should be deleted.

## Inputs

**DB reads (dev stage):** All queries go to the `storms` schema via `ocha-stratus`. Key tables:

- `storms.nhc_tracks_fcastonly_exposure` — deterministic track forecast exposure, adm0 and adm1, keyed by `issued_time`
- `storms.nhc_tracks_obsv_exposure` — cumulative observed exposure up to advisory time
- `storms.nhc_wsp_fcastonly_exposure` — WSP probabilistic bands (percentage × pop_exposed) keyed by `issued_time`
- `storms.nhc_wsp_fcastonly_polygon` — WSP probability polygons for the probabilistic map panel
- `storms.nhc_tracks_geo` — track point geometries (observed + forecast), for storm maps
- `storms.nhc_tracks_fcastonly_buffers` / `nhc_tracks_obsv_buffers` — wind radii polygons (34/50/64 kt)
- `storms.gdacs_exposure` — GDACS pop-exposure (adm0 + adm1, matched via `valid_time` to advisory window ±3h)
- `storms.adam_exposure` — ADAM pop-exposure (same advisory-window match)
- `storms.storm_id_lookup` — cross-source ATCF ↔ GDACS ↔ ADAM ID mapping
- `storms.gdacs_fm_lookup` / `storms.adam_fm_lookup` — adm1 code/name → FieldMaps pcode crosswalks
- `storms.admin_population` — country-level population denominators
- `storms.nhc_storms`, `storms.ibtracs_storms` — storm name/season metadata

**Blob reads:**
- `global/fieldmaps/edge-matched/humanitarian/intl/adm1/{iso3}.parquet` and `adm0/{iso3}.parquet` — FieldMaps boundaries for maps
- Local fallback: `data/ne110m_countries.parquet` (Natural Earth 110m, bundled in repo)

All exposure data is produced upstream by `ds-storms-pipeline` (NHC/IBTrACS track processing, WSP computation, GDACS/ADAM ingestion).

## Steps

1. **Determine advisory time** — defaults to most recent NHC advisory hour (03/09/15/21 UTC) at or before now; backfill via `--issued-time`.
2. **Fetch forecast exposure** — `nhc_tracks_fcastonly_exposure` + `nhc_wsp_fcastonly_exposure` to identify active (storm, country) pairs. A 3-hour advisory-window offset handles GDACS/ADAM/WSP publication lags.
3. **Fetch previous advisory pairs** — detect final-update pairs (had exposure last advisory, have none now).
4. **Fetch observed, GDACS, ADAM exposures** — for rendering and cross-source comparison.
5. **Combine sources** — `MAX(CHD, ADAM, GDACS)` per (storm, country, wind speed) — bias to action. At adm1, GDACS/ADAM units are harmonized to FieldMaps pcodes; source set held consistent across all units within a storm-country.
6. **Render HTML** — per-storm strip charts (population exposure vs. historical storms since 2002, return period coloring) and probabilistic/deterministic track maps (matplotlib + geopandas). Images embedded as base64 in HTML, then uploaded to Listmonk media before send.
7. **Generate xlsx** — per-storm styled Excel workbook (tabs `README`, `adm0_exposure`, `adm1_exposure`, `caveats`), mirroring the ds-storm-impact-harmonisation archive workbook and sharing its identity columns (`atcf_id` storm key, `admin_pcode`, `sources` joined with `|`). Was a flat CSV before PR #20. Differences by design: forecast-based (not final observed), per-storm per-`issued_time`, laid out wide by wind threshold (34/50/64 kt) with the MAX-across-sources value in each cell. Styling comes from `src/xlsx_style.py`, vendored code-identical from the harmonisation repo's `src/source_exposure/style.py`.
8. **Branch on result** — if any (storm, country) pairs: send exposure alert to per-country lists + aggregate lists + monitoring list. If active storms but no country exposure: send monitoring-only email (maps only) to monitoring list. If no active storms: exit silently.
9. **Send via Listmonk** — create campaign + upload images + attach the per-storm xlsx workbook(s) + send. Listmonk credentials are pulled from the `dsci` Databricks secret scope at runtime.

## Outputs

**Listmonk campaigns** (real sends when `test_email=False, dry_run=False`):
- Exposure alert: full HTML email with summary table, per-country strip charts, storm maps; a styled xlsx workbook attachment per active storm (was a flat CSV before PR #20)
- Monitoring email: storm maps only, to `aggregate:monitoring` list, when active storms have no country exposure

**Subscriber lists** (per-country + aggregates, tagged `ds-storms-alerts`):
- `iso3:<code>` lists — one per monitored country (provisioned by `pipelines/setup_country_lists.py`)
- `aggregate:all` — all exposure advisories
- `aggregate:lac` — any LAC country (LAC_ISO3S set in `src/constants.py`)
- `aggregate:monitoring` — DSci team, monitoring-only and exposure emails

**Static site** (`docs/`): subscriber form at `ocha-dap.github.io/ds-storms-alerts`, guide page at `/guide.html`. Deployed to Azure app `chd-ds-storms-alerts` on push to `main`.

## Dependencies

| Dependency | Notes |
|---|---|
| `ocha-stratus>=0.1.7` | DB engine (`stratus.get_engine(stage="dev")`) and blob access |
| `ocha-relay` (pinned SHA) | `ListmonkClient` — create campaign, upload media/attachments, send |
| `matplotlib>=3.9`, `geopandas` | Strip charts, storm maps |
| Databricks cluster `0515-161935-i2w5mxhc` | Personal/interactive compute cluster (not ephemeral Job Compute) — pinning this prod job to it is fragile; see [databricks.md → Clusters](../infrastructure/databricks.md#clusters). Carries `DSCI_AZ_*` DB/blob creds as env vars |
| Databricks secret scope `dsci` | `DSCI_LISTMONK_BASE_URL`, `DSCI_LISTMONK_API_USERNAME`, `DSCI_LISTMONK_API_KEY` |
| `PGSSLMODE=require` | Required for Azure PostgreSQL; set in stratus/env — see `infrastructure/conventions.md` |
| Listmonk instance | `https://listmonk-demo-afhcg8e2hde0fxca.eastus2-01.azurewebsites.net` |

## Failure modes & debugging

**No email sent, job exits 0:** Normal — no active storms at the advisory time, or active storms with no country exposure and no monitoring list configured. Check job logs for `No active storms this advisory` or `No aggregate:monitoring list`.

**Job exits non-zero:** The `run_alert_job.py` wrapper raises `RuntimeError` on non-zero child exit. Check Databricks task run output (not just CLI exit code — `databricks jobs get-run-output <task_run_id>`). Look for `Sent campaign …` or `DRY_RUN=True` to confirm success.

**Missing Listmonk credentials:** Logs `[run_alert_job] WARNING: dsci/<KEY> unavailable`. A dry run will still exercise DB/blob/plotting. Set secrets via `databricks secrets put-secret dsci <KEY>`.

**GDACS/ADAM exposure absent or late:** The pipeline logs a warning when a source has no exposure for the current advisory time window (`±3h`). The consolidated MAX falls back to whichever sources responded. Not an error, but watch for patterns of persistent absence.

**`matplotlib` errors on cluster:** Set `MPLCONFIGDIR=/tmp/mplconfig` — the `run_alert_job.py` wrapper does this, but it's the fix if you see config-dir permission errors.

**Per-country list missing:** `RuntimeError: No listmonk list found for iso3(s): [...]`. Run `pipelines/setup_country_lists.py` to provision missing lists.

**GDACS adm1 orphan rows:** Logged as `WARNING: Dropping N GDACS adm1 unit(s) with no FieldMaps match`. Investigate via `storms.gdacs_fm_lookup` — the unit may need a new crosswalk entry.

**All data reads from DEV stage:** The prod Databricks job reads the dev database. Stage is a parameter, not hardcoded: `run_alert.py --stage` defaults to `"dev"` (argparse default) and the `databricks.yml` `stage` variable also defaults to `"dev"`, so the live prod job passes `stage=dev` to `stratus.get_engine(stage=...)`. `setup_country_lists.py` is the one place with a literal `stage="dev"`. If the upstream `ds-storms-pipeline` stops writing to dev, the alert will generate zero-exposure emails. To cut over: `databricks bundle deploy -p default --var stage=prod`.

**Branch mismatch:** The live DBX job's `git_branch` variable defaults to `main`. Active development is on `adm1-exposure-csv`. If you push to `adm1-exposure-csv` and the prod job is still pulling `main`, you will NOT see your changes at runtime. Redeploy with `--var git_branch=adm1-exposure-csv` or merge to main.

**GHA schedule is disabled:** The `run_alert.yml` workflow is `workflow_dispatch` only. Re-enable with `gh workflow enable "Run Storm Alert"` as a rollback option.

**Logs:** Databricks task run output in the workspace UI (Jobs → Storm Alert → latest run). GHA run logs under Actions tab in the repo.

## Downstream consumers

Human subscribers via Listmonk per-country and aggregate lists. The static subscriber form (`docs/`) serves new signups. No other internal pipeline consumes this email output directly — it is the terminal step of the storms exposure chain. [apps/glb-tropicalcyclones-app](../apps/glb-tropicalcyclones-app.md) is a sibling consumer of the same `storms` DB schema, not of this pipeline's output.

Upstream: [pipelines/storms-pipeline](./storms-pipeline.md) produces all `storms.*` DB tables this pipeline reads (exposure computation, GDACS/ADAM ingestion, WSP). [pipelines/nhc-forecast](./nhc-forecast.md) is the NHC track ingest that feeds storms-pipeline (one hop upstream, not read directly here). Email transport conventions: [infrastructure/comms-listmonk.md](../infrastructure/comms-listmonk.md).
