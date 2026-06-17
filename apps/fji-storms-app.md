---
content_type: app
name: fji-storms-app
purpose: Interactive map of historical tropical cyclone tracks and hindcast forecasts for the Fiji Anticipatory Action framework, used to review how past triggers fired.
status: live
tech: dash
related: fji-storms
deployment:
  platform: azure-webapp
  ref: chd-pa-aa-fji-storms-app
  url: https://chd-pa-aa-fji-storms-app.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
  slot: development          # GHA deploys to the 'development' slot, not prod (see workflow)
  trigger: push-to-main + workflow_dispatch
inputs:
  - "data/public/processed/fji/fms_tracks_processed.csv — processed FMS observed cyclone tracks"
  - "data/public/processed/fji/fms_historical_forecasts.csv — RSMC/FMS 72-hour hindcast forecasts"
  - "data/public/exploration/fji/ecmwf/cyclone_hindcasts/besttrack_forecasts.csv — ECMWF 120-hour best-track hindcasts"
  - "data/public/processed/fji/historical_triggers.csv — per-storm trigger outcomes (readiness + action dates)"
  - "data/public/raw/fji/cod_ab/fji_polbnda_adm2_province — Fiji ADM2 (province) CODAB shapefile"
  - "data/public/processed/fji/buffer/fji_250km_buffer — 250 km buffer around Fiji ADM0"
source_repo: ocha-dap/pa-aa-fji-storms-app
source_branch: main
source_sha: b7582b9
code_ref:
  - app.py
  - datasources.py
  - update_datasources.py
extra:
  data_origin: "All data is bundled in the repo under data/ (committed static files). update_datasources.py copies data from a local AA_DATA_DIR (Google Drive mount) into data/ — there is no live DB or blob connection at runtime."
  update_workflow: "Data refresh is manual: developer runs update_datasources.py with AA_DATA_DIR set, then commits and redeploys."
  heroku_history: "A heroku/master branch exists from an earlier deployment on Heroku; app was migrated to Azure."
  analysis_repo: "pa-aa-fji-storms (separate repo) contains the framework analysis that produced the trigger CSVs consumed here."
  deploy_slot: "[conflict] GHA workflow `.github/workflows/main_chd-pa-aa-fji-storms-app(development).yml` deploys to slot-name 'development', not prod — the deployments.md row tracks the app, but the live surface is the dev slot."
visibility: internal
last_synced: "2026-06-17"
---

# Fiji Storms Historical Forecasts App

> Interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

This app lets a user explore historical tropical cyclone events near Fiji and review how the Fiji AA framework trigger would have fired. For each named cyclone season (e.g. "Yasa 2020/2021"), it shows the actual observed track alongside all available RSMC/FMS 72-hour hindcast forecasts and ECMWF 120-hour best-track hindcasts on a Mapbox map. Forecast tracks that triggered the Readiness (R) or Action (A) phases are highlighted in the legend. The question it answers: "For this past storm, which forecast first crossed the trigger threshold, and how did that compare to the actual track?"

## Key features

- **Storm selector dropdown** — sorted newest-first by datetime; one storm per selection.
- **Actual track** — observed path in black with Australian-scale category labels.
- **50/100/200 km track buffers** — shaded rings around the actual and each forecast track.
- **250 km Fiji trigger zone** — blue outline of the area within 250 km of Fiji ADM0.
- **FMS 72-hour forecasts** — colour-coded forecast tracks (hidden by default, toggled in legend); forecast that triggered Action is prefixed "A:".
- **ECMWF 120-hour forecasts** — shown in grey when FMS data is present (colour when FMS absent); forecast that triggered Readiness is prefixed "R:"; Action trigger prefixed "A:".
- **Legend title** summarises which forecast type triggered what phase.

For the framework analysis (trigger thresholds, calibration), see the [fji-storms framework page](../frameworks/fji-storms/2025-12-17.md) and the `pa-aa-fji-storms` repo.

## Data

All data is **static and bundled in the repo** under `data/`. There is no live database or blob connection at runtime. The files are:

| File | Content |
|---|---|
| `data/public/processed/fji/fms_tracks_processed.csv` | Observed FMS cyclone tracks (all historical storms) |
| `data/public/processed/fji/fms_historical_forecasts.csv` | RSMC/FMS 72-hour hindcast forecasts per storm |
| `data/public/exploration/fji/ecmwf/cyclone_hindcasts/besttrack_forecasts.csv` | ECMWF 120-hour best-track hindcasts |
| `data/public/processed/fji/historical_triggers.csv` | Per-storm trigger dates and flags (readiness/action) |
| `data/public/raw/fji/cod_ab/fji_polbnda_adm2_province/` | Fiji ADM2 CODAB shapefile |
| `data/public/processed/fji/buffer/fji_250km_buffer/` | 250 km buffer shapefile |

Data freshness is determined by when a developer last ran `update_datasources.py` and committed the result. The script copies from a local `AA_DATA_DIR` (Google Drive mount) — there is no automated refresh pipeline connected to this app.

## Deployment & access

Deployed as Azure web app `chd-pa-aa-fji-storms-app` in resource group `IMB-CHD-DataScience-EastUS2`. URL: https://chd-pa-aa-fji-storms-app.azurewebsites.net. State: Running (per `deployments.md`).

**Deploys to the `development` slot, not prod.** The GitHub Actions workflow `.github/workflows/main_chd-pa-aa-fji-storms-app(development).yml` runs on every push to `main` (and on manual `workflow_dispatch`), builds the repo, and publishes to `slot-name: development`. The `deployments.md` registry row tracks the app object (Running); the actual served surface is the dev slot. The app is served via Gunicorn with `server = app.server` as the WSGI entry point. Access is internal (no authentication layer visible in the code).

Cross-ref: `infrastructure/deployments.md` — Azure web apps table, row `chd-pa-aa-fji-storms-app`.

## Maintenance / known issues

- **Data updates are manual; code deploy is automated.** Refreshing data is a manual developer step (sync `AA_DATA_DIR`, run `update_datasources.py`, commit) — see the repo for the exact commands. But the *deploy itself is not manual*: pushing the resulting commit to `main` triggers the GHA workflow, which redeploys to the **development** slot. There is no automated pipeline that refreshes the data, but there is CI that redeploys on push.
- **[conflict] Deployed slot is `development`, not prod.** The live surface is the dev slot per the workflow; the registry tracks only the app object. Treat the dev slot as the operational deployment.
- **Static data in git** — the `data/` directory contains committed binary shapefiles and CSVs. Large commits or stale data are the main drift risk.
- **Heroku legacy branch** — `heroku/master` branch (last commit 2023-12-08) predates the Azure deployment; ignore for operational purposes.
- **No ocha-stratus** — this app does not use ocha-stratus/blob/DB. All reads are local file I/O from the bundled `data/` directory.
- **EPSG:4326 wrapping** — Fiji straddles the antimeridian; `datasources.py` uses a custom lon_wrap CRS (`FJI_CRS`) for display. Map is centred at lon=179.
- **ADM2 note in code** — comment in `load_codab` says "there seems to be a problem with level=2 (province)" — the app uses level 2 but this may warrant investigation if provinces render incorrectly.
