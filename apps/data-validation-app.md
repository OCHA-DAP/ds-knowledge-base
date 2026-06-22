---
content_type: app
name: data-validation-app
purpose: "Interactive sanity-checking of raster pipeline outputs (SEAS5, Floodscan) — time-series and COG pixel maps per admin unit."
status: live
tech: dash
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-data-validation
  url: "https://chd-ds-data-validation-fhfyfahyb7gaa6a7.eastus2-01.azurewebsites.net"
  resource_group: IMB-CHD-DataScience-EastUS2
  slot: development                          # [conflict] CI only deploys to the dev/sandbox SLOTS; no prod-slot automation. See discrepancies.
  ci_workflow: ".github/workflows/main_chd-ds-data-validation(development).yml — push to main + workflow_dispatch → slot 'development'"
  ci_workflow_sandbox: ".github/workflows/sandbox_chd-ds-data-validation(sandbox).yml — push to sandbox + workflow_dispatch → slot 'sandbox'"
  deployed_branch: main                      # dev slot built from main (== ingested branch). sandbox slot built from sandbox branch (17 commits ahead of main).
inputs:
  - "DB table: iso3 (country registry with max_adm_level, floodscan flag)"
  - "DB table: polygon (pcode / name / adm_level per iso3)"
  - "DB table: seas5 (raster stats — issued_date, leadtime, iso3, pcode, band stats)"
  - "DB table: floodscan (raster stats — valid_date, iso3, pcode, band, stats)"
  - "Blob raster: seas5/monthly/processed/precip_em_i{date}_lt{0-6}.tif (container: raster)"
  - "Blob raster: floodscan/daily/v5/processed/aer_area_300s_v{date}_v05r01.tif (container: raster)"
  - "Blob shapefile: {iso3}_shp.zip / {iso3}_adm{level}.shp (container: polygon)"
depends_on:
  - floodscan-ingest
source_repo: OCHA-DAP/ds-app-data-validation
source_branch: main
source_sha: 29bf965
code_ref:
  - app.py
  - callbacks/callbacks.py
  - src/datasources/seas5.py
  - src/datasources/floodscan.py
  - src/datasources/codab.py
extra:
  stage_env: "STAGE env var (read in constants.py and src/constants.py) selects dev vs prod DB/blob via stratus.get_engine(STAGE) / stage=STAGE; also toggles the dev banner in app.py (STAGE=='dev')."
  datasets_supported: ["seas5", "floodscan"]
  gunicorn_start: "gunicorn -w 4 -b 127.0.0.1:8000 app:server (per README; production entrypoint app:server)"
  seas5_source: "SEAS5 rasters + DB stats are produced by the Databricks 'Run SEAS5' job (job_id 710204563973283, UNPAUSED) — no dedicated KB pipeline page exists yet (see discrepancies [gap])."
discrepancies:
  - "[conflict] CI deploys to Azure SLOTS only, never a production slot. main → slot 'development', sandbox → slot 'sandbox'. No workflow targets a prod slot, so the prod surface (if any) is updated manually / by slot-swap. deployments.md lists only the base app row `chd-ds-data-validation` (Running) and does not distinguish slots."
  - "[conflict] The sandbox slot is built from the `sandbox` branch, which is 17 commits AHEAD of `main` (125fea5 vs 29bf965). So the sandbox slot runs newer code than the dev slot — 'development is the primary live surface' is not clearly true; verify which slot the base URL is swapped to before assuming."
  - "[conflict] floodscan.get_raster_stats() hardcodes stratus.get_engine(\"prod\"), ignoring STAGE — a dev/sandbox deployment still reads the production `floodscan` DB table. Every other DB call (iso3, polygon, seas5) respects STAGE."
  - "[gap] deployments.md maps the `chd-ds-data-validation` app row to repo `—` (unlinked); the real source repo is OCHA-DAP/ds-app-data-validation. Registry row should be linked."
  - "[gap] No KB pipeline page for SEAS5 ingest (the `Run SEAS5` Databricks job 710204563973283 that produces this app's SEAS5 rasters/stats). depends_on can only point to floodscan-ingest until a seas5 pipeline page exists — stub it."
  - "[stale] requirements.txt pins ocha-stratus==0.1.2 — may lag current stratus; auth/API changes would require a bump + redeploy."
  - "[stale] date_utils.get_date_range has a `# TODO: Modify for other datasets` marker; adding a dataset requires editing both this dict and dataset_options in layouts/body.py."
visibility: internal
last_synced: "2026-06-22"
---

# Data Validation App

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A Dash application for basic visualization and sanity-checking of outputs from the DS team's raster data pipelines. A user selects a dataset (SEAS5 or Floodscan), an issue/valid date, a country (ISO3), admin level, admin unit (pcode), and a summary statistic. The app renders two charts: a time-series of raster stats across historical dates at the same day-of-year (to spot anomalies vs prior years), and a COG pixel map showing the raw raster clipped to the selected admin boundary — optionally upsampled for visual clarity. The SEAS5 view facets the pixel map by leadtime (0–6 months). The Floodscan view exposes SFED/MFED band selection. The primary user is the DS team; the purpose is QA of pipeline outputs, not public reporting.

## Key features

- **Dataset picker**: SEAS5 (monthly precipitation forecasts) or Floodscan (daily flood fraction).
- **Cascading dropdowns**: dataset → issue/valid date → ISO3 → admin level → pcode → stat.
- **Time-series chart** (`chart-leadtime-series`): historical same-day-of-year raster stats for the selected pcode, current year highlighted in red, prior years in pink.
- **COG viewer** (`chart-cog`): pixelwise raster clipped to the selected admin boundary; SEAS5 shows one facet per leadtime (0–6); Floodscan shows a single date; an "upsampled" radio option nearest-neighbor resamples to 0.05° for visual inspection.
- **Dev bar**: yellow banner injected when `STAGE=dev`, so it's obvious which slot you're on.
- QA surface for the team's raster ecosystem: the app's own UI footer links the COG + raster-stats producers (`OCHA-DAP/ds-raster-pipelines`, `OCHA-DAP/ds-raster-stats`). The Floodscan arm it reads is [pipelines/floodscan-ingest](../pipelines/floodscan-ingest.md); the SEAS5 arm is the Databricks `Run SEAS5` job (no KB pipeline page yet — see discrepancies).

## Data

All data access goes through `ocha-stratus` (`stratus.get_engine(STAGE)` for DB, `stratus.open_blob_cog` / `stratus.load_shp_from_blob` for blob).

**DB tables (read on demand):**

| Table | Key columns | Used for |
|---|---|---|
| `iso3` | iso3, max_adm_level, floodscan | Country list; filters Floodscan-capable countries |
| `polygon` | iso3, pcode, name, adm_level | Pcode options per country + admin level |
| `seas5` | issued_date, leadtime, iso3, pcode, band stats (mean/median/min/max/count/sum/std) | Time-series chart for SEAS5 |
| `floodscan` | valid_date, iso3, pcode, band, band stats | Time-series chart for Floodscan |

**Blob data (read on user interaction):**

| Path pattern | Container | Used for |
|---|---|---|
| `seas5/monthly/processed/precip_em_i{YYYY-MM-DD}_lt{0-6}.tif` | `raster` | SEAS5 COG viewer (7 leadtimes per issue date) |
| `floodscan/daily/v5/processed/aer_area_300s_v{YYYY-MM-DD}_v05r01.tif` | `raster` | Floodscan COG viewer |
| `{iso3}_shp.zip` → `{iso3}_adm{level}.shp` | `polygon` | Admin boundary clip |

**Freshness:** SEAS5 date range covers 1981-01-01 to current month (clipped to prior month if before the 6th). Floodscan date range covers 1998-01-12 through yesterday. Both are driven by the upstream raster pipelines; no data is transformed or stored by this app.

## Deployment & access

The app runs on Azure Web App **`chd-ds-data-validation`** in resource group `IMB-CHD-DataScience-EastUS2`. See `infrastructure/deployments.md` for the full registry row.

**Deployment slots and GHA workflows:**

| Slot | Trigger branch | Workflow file |
|---|---|---|
| `development` | `main` | `main_chd-ds-data-validation(development).yml` |
| `sandbox` | `sandbox` | `sandbox_chd-ds-data-validation(sandbox).yml` |

There is **no GHA workflow targeting a production slot** — CI only ever pushes to the `development` and `sandbox` slots. Any true prod surface is updated manually (e.g. slot-swap), and `deployments.md` lists only the base app row (`chd-ds-data-validation`, Running) without distinguishing slots. Note the `sandbox` branch is currently **17 commits ahead of `main`**, so the sandbox slot runs newer code than the dev slot — don't assume "development" is authoritative without checking which slot the base URL points at. Access is internal to the DS team (no public auth layer in the code).

Runtime: Python 3.11, `gunicorn -w 4 -b 127.0.0.1:8000 app:server` (per the repo README). `STAGE` (`prod`/`dev`) gates DB/blob stage and the dev banner. Azure PostgreSQL also needs `PGSSLMODE=require` in the environment (general DS convention — see `infrastructure/database.md`; not set in this repo). For redeploy steps and env wiring, follow the repo README rather than restating here.

## Maintenance / known issues

The deployment/data gotchas (slot-only CI, no prod-slot automation, sandbox-ahead-of-main, Floodscan hardcoded to prod DB, stratus pin, the add-a-dataset two-edit footgun) are captured in the `discrepancies` frontmatter above — read that first. A few runtime notes:

- **Redeploy**: push to `main` (→ dev slot) or `sandbox` (→ sandbox slot). Workflows have no pre-deploy test step. There is no prod-slot workflow.
- **Floodscan reads prod regardless of STAGE**: `src/datasources/floodscan.get_raster_stats()` calls `stratus.get_engine("prod")` directly — even a dev/sandbox deployment hits the production `floodscan` table. (`[conflict]` in discrepancies.)
- **Missing COG → silent blank**: a missing blob raster is caught as `RasterioIOError` and rendered as a "No data available" placeholder, not surfaced as an error.

Deeper redeploy/env detail belongs in the repo README — don't restate it here.
