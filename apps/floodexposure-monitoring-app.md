---
content_type: app
name: floodexposure-monitoring-app
purpose: "Interactive map and chart showing near-real-time population exposure to flooding (Floodscan × WorldPop) across 12 countries, with return-period context."
status: live
tech: dash
related: ds-floodexposure-monitoring
deployment:
  platform: azure-webapp
  ref: chd-ds-floodexposure-monitoring
  url: https://chd-ds-floodexposure-monitoring.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
  slot: development                          # [conflict] only CI flow deploys to the DEV slot; see discrepancies
  ci_workflow: ".github/workflows/main_chd-ds-floodexposure-monitoring(development).yml — push to main + workflow_dispatch"
  deployed_branch: main                      # [conflict] deployed != ingested branch (update-bounds); see discrepancies
inputs:
  - "DB table app.floodscan_exposure — daily pcode-level flood exposure (sum column), adm 0/1/2"
  - "DB table app.floodscan_exposure_regions — same for COD custom sub-national regions"
  - "DB table app.quantile — current-date quantile (relative-to-historical) per pcode/adm_level"
  - "DB table app.quantile_regions — same for COD regions"
  - "DB table app.admin_lookup — admin name lookup (adm0/1/2 names + pcodes)"
  - "Static GeoJSON in assets/geo/ (adm0.json, adm1.json, adm2.json, adm0_outline.json) — committed to repo, sourced from FieldMaps edge-matched boundaries via download_geodata.py"
depends_on: [floodexposure-monitoring]
source_repo: ocha-dap/ds-floodexposure-monitoring-app
source_branch: update-bounds
source_sha: 888efdc
code_ref:
  - app.py
  - callbacks/callbacks.py
  - utils/data_utils.py
  - utils/chart_utils.py
  - constants.py
  - download_geodata.py
extra:
  rolling_window_days: 7
  rolling_window_env_var: ROLL_WINDOW
  countries_iso3: ["ner", "nga", "cmr", "tcd", "bfa", "eth", "ssd", "som", "mli", "cod", "moz", "mwi"]
  adm_levels: ["0", "1", "2", "region"]
  regions_note: "COD has 3 custom sub-national regions composed of specific ADM1 pcodes (Zone 1/2/3); served from separate DB tables."
  companion_pipeline: "ds-floodexposure-monitoring — computes daily exposure rasters and writes to DB; app is read-only."
  second_active_branch: "geoparquet-switch (2025-09-17, WIP) — explores loading boundaries from geoparquet at runtime rather than from committed GeoJSON."
  stage_env: "STAGE env var selects dev vs prod DB via stratus.get_engine(STAGE)"
  devbar: "Yellow 'THIS IS A DEV APP' banner injected into layout when STAGE=dev."
  disclaimer_modal: "On load, shows an internal-tool disclaimer modal with contact (tristan.downing@un.org)."
  methodology_note: "Exposure = WorldPop 1km 2020 × SFED_AREA rolling-average (≥5% threshold); return period is empirical annual-maximum rank."
  related_pipeline_page_status: "companion exposure pipeline documented at pipelines/floodexposure-monitoring.md (KB page names drop the ds- repo prefix)."
discrepancies:
  - "[conflict] CI deploys to the Azure DEV slot only. The single workflow (`main_chd-...(development).yml`) sets `slot-name: development` / `environment: development` and fires on push to `main`. There is no production-slot deploy automation in the repo; the production slot is updated manually (zip-deploy) if at all. The deployments.md registry lists only the base app `chd-ds-floodexposure-monitoring` (Running) and does not distinguish slots."
  - "[conflict] Deployed branch (`main`, 5eb3559, 2025-03-17) != ingested/checked-out branch (`update-bounds`, 888efdc, 2025-09-17). The map currently in prod is built from `main`; the edge-matched-boundaries work on `update-bounds` and the geoparquet runtime-loading work on `geoparquet-switch` are both unmerged."
  - "[stale] `geoparquet-switch` HEAD is `ef9fafe wip exploring switch to geoparquet` — explicitly WIP, not production-ready."
  - "[stale] `moz` and `mwi` are in `ISO3S` (constants.py) but absent from `iso3_to_pcode`/`pcode_to_iso3`; those dicts are legacy/incomplete (lookup happens via FieldMaps `adm{n}_src`)."
  - "[stale] `ocha-stratus==0.1.1` pinned in requirements.txt — may lag current stratus."
  - "[gap] Azure-app row in deployments.md maps `chd-ds-floodexposure-monitoring` to repo `ds-floodexposure-monitoring` (the pipeline), but this app's code lives in `ds-floodexposure-monitoring-app`. The app and its companion pipeline share the same chd-app name."
visibility: internal
last_synced: "2026-06-17"
---

# Flood Exposure Monitoring App

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A Dash web app ("Risk Monitoring Dashboard — Flood Exposure Module") that shows, for 12 sub-Saharan and Horn-of-Africa countries, how many people are currently exposed to flooding and how unusual that level is historically. A choropleth map (Leaflet, CARTO basemap) colours admin units by their current-day quantile relative to the historical record. Clicking a unit drills down to two charts: a multi-year daily timeseries (7-day rolling average) and a return-period scatter of annual-maximum exposure. The sidebar reports the number of people exposed as of the latest data date and whether it is above/below/normal for the time of year.

## Key features

- **Admin level selector**: Admin 0 / 1 / 2 / Region (COD only) switchable from a map overlay dropdown.
- **Choropleth**: 5-class categorical colour (well below → well above normal) driven by `app.quantile`.
- **Timeseries chart**: Each year plotted as a faint line; current year highlighted; historical median overlaid; vertical dashed line at latest data date.
- **Return-period chart**: Empirical RP from annual maximum exposure; current year annotated; ≥3-yr RP years highlighted.
- **COD custom regions**: Three composite zones (Zone 1/2/3) built from specific ADM1 pcodes, served from separate DB tables.
- **Dev banner**: Yellow bar when `STAGE=dev` so it's impossible to confuse dev and prod deployments.

## Data

All live data is read from the Azure PostgreSQL database via `stratus.get_engine(STAGE)`:

| Table | Contents | Freshness |
|---|---|---|
| `app.floodscan_exposure` | Daily pcode-level population exposed (sum), adm 0/1/2 | Updated by `ds-floodexposure-monitoring` pipeline (Databricks job `Run FloodScan`, scheduled `~20:00 UTC daily`) |
| `app.floodscan_exposure_regions` | Same, COD custom regions | Same |
| `app.quantile` | Current-date quantile category (−2 to 2) per pcode/adm_level | Same |
| `app.quantile_regions` | Same, COD regions | Same |
| `app.admin_lookup` | Admin name / pcode hierarchy | Static; updated when countries added |

Admin boundary GeoJSON (`assets/geo/adm{0,1,2}.json`, `adm0_outline.json`) is committed to the repo, generated by `download_geodata.py` from [FieldMaps](https://data.fieldmaps.io) edge-matched humanitarian boundaries. These must be regenerated and recommitted when new countries are added (see runbook below).

Source rasters: Floodscan SFED_AREA (~10 km resolution) × WorldPop 2020 UN-adjusted 1 km grid. Processing is in the companion repo `ds-floodexposure-monitoring`, not in this app.

## Deployment & access

- **Azure web app**: `chd-ds-floodexposure-monitoring` in `IMB-CHD-DataScience-EastUS2`, state Running (deployments.md Azure web apps table).
- **URL**: https://chd-ds-floodexposure-monitoring.azurewebsites.net
- **CI targets the DEV slot, not prod.** [conflict] The only deploy workflow — `.github/workflows/main_chd-ds-floodexposure-monitoring(development).yml` — fires on push to `main` (or `workflow_dispatch`) and deploys with `slot-name: development` / `environment: development`. There is **no production-slot automation** in the repo; the prod slot is updated manually (zip-deploy) if at all. Don't assume a merge to `main` reaches the production URL.
- **Deployed branch ≠ ingested branch.** [conflict] Prod/dev are built from `main` (last merge `switch-rolling-window`, 2025-03-17); this page is anchored to `update-bounds` (888efdc, 2025-09-17). `update-bounds` (edge-matched boundaries) and `geoparquet-switch` (WIP) are unmerged.
- **Runtime**: Gunicorn (`gunicorn -w 4 -b 127.0.0.1:8000 app:server`) in production; `python app.py` for debug.
- **Auth**: No in-app auth layer; access is gated at the Azure web app level (internal only — disclaimer modal confirms this is an internal tool).
- **STAGE env var** selects the database connection via `stratus.get_engine(STAGE)`: `dev` → dev DB, `prod` → prod DB.

Cross-ref: `infrastructure/deployments.md` Azure web apps table, row `chd-ds-floodexposure-monitoring` (registry lists the base app only; it does not distinguish the dev slot the CI actually deploys to).

## Maintenance / known issues

**Adding a new country**: edit `ISO3S` in `constants.py`, regenerate `assets/geo/*.json` via `python download_geodata.py`, ensure the companion pipeline has populated the `app.*` tables (dev + prod), commit and PR. Canonical step-by-step is in the repo README ("To add a new ISO3 code") — not restated here.

**Redeployment**: Push to `main` triggers the GHA workflow, which deploys to the Azure **development slot** (see Deployment & access). Production is updated manually. `STAGE`, `ROLL_WINDOW`, and DB credential env vars must be set in the Azure app configuration.

**Rolling window**: configurable via `ROLL_WINDOW` env var (default 7). Changing it requires redeployment; the value is read at startup (`constants.ROLLING_WINDOW`) and baked into chart labels and query logic.

**Known issues / gotchas** (full list in `discrepancies` frontmatter):
- CI deploys to the **dev slot only**; deployed branch (`main`) ≠ this page's anchor (`update-bounds`). Two unmerged ahead-of-main branches (`update-bounds`, `geoparquet-switch` WIP).
- The app is read-only over `app.*` tables written by the companion pipeline. If the `Run FloodScan` Databricks job (job_id 792911256578092, `36 0 20 * * ?`, UNPAUSED) misses a run, the latest `valid_date` on the map stalls.
