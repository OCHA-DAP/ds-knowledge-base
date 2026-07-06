---
content_type: app
name: hti-hurricanes-app
purpose: "Dash map + timeline for exploring how each historical Haiti hurricane forecast performed against the AA framework's readiness/action trigger thresholds"
status: live
tech: dash
related: hti-hurricanes
deployment:
  platform: azure-webapp
  ref: chd-ds-aa-hti-hurricanes-app
  url: https://chd-ds-aa-hti-hurricanes-app.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "blob: ds-aa-hti-hurricanes/processed/monitors.parquet (dev container)"
  - "blob: ds-aa-hti-hurricanes/processed/noaa/nhc/historical_forecasts/hti_distances_2000_2023.parquet (dev container)"
  - "blob: ds-aa-hti-hurricanes/processed/triggers_r_p{..}_s{..}_a_p{..}_s{..}.csv (dev container, threshold-encoded filename)"
  - "blob: ds-aa-hti-hurricanes/raw/codab/hti.shp.zip (dev container, CODAB ADM0)"
  - "blob: ds-aa-hti-hurricanes/processed/codab/hti_buffer_230km.shp.zip (dev container, precomputed 230km buffer)"
depends_on: [hti-hurricanes-monitoring]
source_repo: ocha-dap/ds-aa-hti-hurricanes-app
source_branch: historical-forecasts
source_sha: d549f23
code_ref:
  - app.py
  - index.py
  - data/load_data.py
  - callbacks/callbacks.py
  - components/map_plot.py
  - components/time_plot.py
extra: {}
visibility: internal
last_synced: 2026-07-02
---

# Haiti Hurricanes AA Framework — historical triggers app

> The canonical logic is the code at `code_ref` in `ocha-dap/ds-aa-hti-hurricanes-app` (branch `historical-forecasts`); this page explains what it shows and how it's fed.

## What it shows
A single-page Dash app ("Cadre action anticipatoire ouragans Haïti : déclencheurs historiques") that lets a user pick a historical storm and one of its NHC forecast issue-times, then see (1) a map of Haiti with the storm track plotted for that issue-time, the 230km trigger buffer, and markers flagging whether the readiness/action wind and rolling-2-day-rainfall thresholds were crossed, and (2) a collapsible time-series panel plotting wind speed, 2-day rainfall, and minimum distance to Haiti across all issue-times for that storm, with vertical lines marking when the readiness/action triggers actually fired and when the storm made its closest pass. It answers: "for this historical storm, would/did the Haiti hurricanes AA framework's mobilisation and action triggers have fired, and when?" French-language UI; carries an "internal, in development" banner (contact: tristan.downing@un.org).

## Key features
- **Storm dropdown** — every storm in the historical NHC record (2000–2023), including the framework's named reference storms (Matthew 2016 default, plus Laura/Ivan/Sandy/Jeanne/Hanna/Gustav/Ike — see `src/constants.py`).
- **Issue-time dropdown** — every forecast issue-time available for the selected storm.
- **Map plot** — ADM0 outline, 230km buffer, forecast track points sized/labelled by windspeed, colored red where a threshold was crossed, plus a rainfall-level marker; separate readiness (blue/grey, dotted) and action (orange/black, solid) leadtime windows per `data/load_data.py`'s `lts` dict.
- **Time-series panel** (toggle button) — 3-row subplot (wind / 2-day rainfall / min distance) vs. forecast issue-time, with threshold dashed lines and annotated trigger/closest-pass markers.
- Serves the [hti-hurricanes](../frameworks/hti-hurricanes/2024-08-23.md) framework as a companion visualization for reviewing/calibrating the trigger against the historical record (distinct from live monitoring).

## Data
Reads pre-processed parquet/CSV/shapefile artifacts from the **dev** Azure Blob container (`imb0chd0dev`, `projects` container, `ds-aa-hti-hurricanes` prefix) via `src/utils/blob.py` (SAS-token `ContainerClient`, `DEV_BLOB_SAS` env var) — no live API calls or DB reads at request time; all data is loaded once into `app.data` at process startup (`load_data()` in `data/load_data.py`). Inputs: `monitors.parquet` (historical forecast/obsv monitoring records — the same family of data the [hti-hurricanes-monitoring](../pipelines/hti-hurricanes-monitoring.md) pipeline produces), `hti_distances_2000_2023.parquet` (per-track distance-to-Haiti reanalysis, 2000–2023), a threshold-encoded `triggers_*.csv` (precomputed trigger fire times per storm for the specific readiness/action thresholds baked into `lts`), and CODAB ADM0 + a precomputed 230km buffer shapefile. Freshness is tied to whenever these dev-blob artifacts were last regenerated upstream (batch/notebook, not scheduled) — the app itself does not refresh data on a cadence; a redeploy or process restart is needed to pick up new blob contents.

## Deployment & access
Azure Linux web app `chd-ds-aa-hti-hurricanes-app` (Python 3.11.4, `gunicorn` serving the Dash `server` WSGI object from `app.py`), resource group `IMB-CHD-DataScience-EastUS2`, state Running — see the row in [infrastructure/deployments.md](../infrastructure/deployments.md). No dev/prod deployment slot in the app itself, but it reads exclusively from the **dev** blob container (`prod_dev="dev"` hardcoded throughout `src/utils/blob.py` and `src/datasources/codab.py`) — there is no prod-data path. Access is via the public URL; the in-app banner marks it an internal, in-development tool. Requires **both** `DEV_BLOB_SAS` and `PROD_BLOB_SAS` as app-service environment variables — `PROD_BLOB_SAS` never reads any data, but `src/utils/blob.py` builds the prod `ContainerClient` at module import (`PROD_BLOB_AA_URL = … + "?" + PROD_BLOB_SAS`), so a missing value raises `TypeError` and the app fails to start.

## Maintenance / known issues
- Redeploy via the Azure web app's normal Python/gunicorn deployment (push to the deployed branch; `runtime.txt` pins `python-3.11.4`, `requirements.txt` pins `dash==2.17.0`, `geopandas==0.14.4`, etc.).
- **Active branch is `historical-forecasts`, not `main`** — verify which branch Azure is actually configured to deploy from before assuming a `main` push updates the live app.
- All blob reads are hardcoded to the **dev** container; if the underlying dev artifacts are moved/renamed (e.g. the threshold-encoded `triggers_*.csv` filename, which is derived from the exact `lts` threshold values in `data/load_data.py`), the app will fail to load data at startup with no fallback.
- `load_gdf_from_blob` extracts shapefiles to a relative `temp/` directory — repeated loads/restarts on the same instance overwrite it rather than cleaning up.
- No automated tests, CI, or scheduled data-refresh workflow in this repo; it is a thin viz layer over artifacts produced elsewhere (framework repo `ocha-dap/ds-aa-hti-hurricanes` / the monitoring pipeline).
