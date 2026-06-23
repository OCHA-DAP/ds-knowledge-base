---
content_type: app
name: raster-stats-app
purpose: Interactive explorer for ERA5/SEAS5/IMERG raster zonal statistics per admin boundary — lets users browse, map, and check DB completeness for the rasterstats pipeline output.
status: live
tech: dash
related: pipelines/raster-stats
deployment:
  platform: azure-webapp
  ref: chd-ds-rasterstats
  url: https://chd-ds-rasterstats.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "DB table: public.era5 (rasterstats DB — zonal stats by iso3/pcode/valid_date/adm_level)"
  - "DB table: public.seas5 (rasterstats DB — zonal stats by iso3/pcode/valid_date/issued_date/leadtime/adm_level)"
  - "DB table: public.imerg (rasterstats DB — zonal stats by iso3/pcode/valid_date/adm_level)"
  - "DB table: public.iso3 (rasterstats DB — country registry: iso3, stats_last_updated, total-pcodes, max_adm_level)"
  - "DB table: public.{dataset}_completeness (rasterstats DB — per-iso3/year completeness summary)"
  - "local GeoJSON files in data/ — admin boundaries for AFG/ETH/MDV/BRA at adm0/1/2 (bundled with app)"
depends_on:
  - raster-stats
source_repo: ocha-dap/ds-raster-stats-app
source_branch: main
source_sha: "710c3ea"
code_ref:
  - "app.py — entrypoint: Dash app init, BasicAuth, layout + callbacks registration"
  - "layout/layout.py — sidebar (dataset/stat/leadtime/iso3/admin/date/pcode selectors) + three-tab main panel"
  - "callbacks/callbacks.py — all Dash callbacks: map, line chart, data grid, completeness tables"
  - "utils/data_processing.py — get_engine (dev/prod), fetch_data_from_db, load_geojson, calculate_centroid"
  - "utils/components.py — navbar, sidebar controls, chart_panel, database_completeness/details grids"
  - "utils/date_utils.py — display_date_range (monthly highlight band), to_first_of_month"
  - "constants.py — MODE, AZURE_DB_PW_DEV/PROD, APP_UID/PWD from env"
extra:
  auth: "HTTP Basic Auth via dash-auth (uid/pwd from APP_UID/APP_PWD env vars)."
  db_connection: "Uses raw SQLAlchemy engine (psycopg2) directly — NOT ocha-stratus. Connects to the dedicated rasterstats DB (chd-rasterstats-{dev|prod}.postgres.database.azure.com). MODE env var selects dev vs prod."
  local_mode: "MODE=local skips DB queries and loads data/demo-export.csv instead — useful for offline dev/demo."
  completeness_hardcodes: "The 'Database Summary' tab hard-codes expected-row factors (era5:525, seas5:526*7, imerg:8690) and last-updated dates (2024-10-10/09/11). These must be updated manually whenever the DB is refreshed — they are NOT pulled from the DB."
  iso3_coverage: "The ISO3 dropdown is hard-coded to [AFG, ETH, MDV, BRA] in utils/components.py. Expanding to more countries requires both adding GeoJSON files to data/ and updating the dropdown."
discrepancies:
  - "[gap] Deployed to Azure web app chd-ds-rasterstats (GHA main_chd-ds-rasterstats.yml, push-to-main → Production slot) but this app is NOT listed in infrastructure/deployments.md (registry shows 20 apps, chd-ds-rasterstats not among them). Registry needs a row added."
  - "[conflict] MODE defaults to 'dev' (constants.py: os.getenv('MODE','dev')). Unless MODE=prod is set in the Azure app's config, the deployed app reads the chd-rasterstats-DEV DB, not prod. Confirm the Azure app setting; otherwise the 'live' app is showing dev data."
  - "[stale] completeness expected-row factors (era5:525, seas5:526*7, imerg:8690) and stats_last_updated dates (Oct 2024) are hard-coded in callbacks/callbacks.py and not refreshed from the DB — they go stale as the pipeline writes more rows."
visibility: internal
last_synced: "2026-06-22"
---

# Raster Stats App

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A Dash-based visualizer over the output of the [raster-stats pipeline](../pipelines/raster-stats.md). A user selects a dataset (ERA5 / SEAS5 / IMERG), a statistic (mean/median/max/min/count/sum/std), a leadtime (SEAS5 only), an ISO3 country, an admin level (0/1/2), and a valid date. The app queries the dedicated rasterstats PostgreSQL DB and renders a choropleth map coloured by the chosen stat for that date, a time-series line chart for selected p-codes, and a tabular grid of the raw rows. A third "Database Summary" tab shows per-country DB completeness (actual vs expected row counts, colour-coded red/pink for gaps).

The question it answers: "What do the ERA5/SEAS5/IMERG zonal stats look like for a given country, admin level, and date — and is the DB fully populated?"

## Key features

- **Choropleth map** — Plotly `choropleth_map` at configurable admin level, date, and statistic. Reads GeoJSON boundaries bundled in `data/` for AFG, ETH, MDV, BRA.
- **Line chart** — time series for up to 5 selected p-codes, with a red vertical band highlighting the currently selected date range (month-wide for ERA5/SEAS5; point for IMERG).
- **Data grid** — AG Grid table of all DB rows for the current country/level/dataset/leadtime filter; filterable/sortable.
- **Database Summary tab** — two AG Grids: (1) per-iso3 summary with expected vs actual row counts (red = under-populated, pink = over-populated); (2) per-iso3/year detail for the selected row. Completeness expected-row factors are hard-coded (see `extra.completeness_hardcodes`).
- **Basic Auth** — dash-auth HTTP Basic Auth gate; credentials from `APP_UID`/`APP_PWD` env vars.
- **Dev/prod mode** — `MODE` env var (`dev`|`prod`|`local`) selects which rasterstats DB to hit. `local` mode reads a bundled CSV (`data/demo-export.csv`) with no DB needed.

Serves the [raster-stats pipeline](../pipelines/raster-stats.md) as its primary exploration and QA surface.

## Data

**Database (dedicated Azure PostgreSQL — `chd-rasterstats-{dev|prod}.postgres.database.azure.com`):**

| table | content | freshness |
|---|---|---|
| `public.era5` | Monthly precip zonal stats per iso3/pcode/adm_level/valid_date | Updated ~6th of month by Run ERA5 Databricks job |
| `public.seas5` | Monthly precip zonal stats per iso3/pcode/adm_level/valid_date/issued_date/leadtime | Updated ~5th of month by Run SEAS5 Databricks job |
| `public.imerg` | Daily precip zonal stats per iso3/pcode/adm_level/valid_date | Updated daily by Run IMERG Databricks job |
| `public.iso3` | Country registry (iso3, max_adm_level, stats_last_updated, total-pcodes) | Manual bootstrap; updated infrequently |
| `public.{dataset}_completeness` | Per-iso3/year row counts | Derived; written by raster-stats pipeline |

This is the **same dedicated DB** written by the `ds-raster-stats` pipeline (not the shared stratus DB). Connection via raw SQLAlchemy — NOT ocha-stratus.

**Bundled GeoJSON boundaries (`data/`):** pre-downloaded admin boundary files for AFG (adm0/1/2), ETH (adm0/1/2), MDV (adm0/1/2/3), BRA (adm0/1). These are static files bundled in the repo; they do not update automatically.

## Deployment & access

Azure web app **`chd-ds-rasterstats`** (resource group `IMB-CHD-DataScience-EastUS2`), deployed by GitHub Actions on every push to `main` (`.github/workflows/main_chd-ds-rasterstats.yml` → `azure/webapps-deploy`, **Production** slot). `server = app.server` is the WSGI entrypoint.

**Gotcha — dev DB by default.** `MODE` defaults to `dev` (`constants.py`), so unless the Azure app config sets `MODE=prod`, the deployed app queries the `chd-rasterstats-DEV` DB. Verify the app-setting before trusting the data shown. Required env vars: `MODE`, `AZURE_DB_PW_DEV`/`AZURE_DB_PW_PROD`, `APP_UID`, `APP_PWD`.

**Registry gap:** this app is **not yet listed** in `infrastructure/deployments.md` (the Azure web-apps table). Add a `chd-ds-rasterstats` row. See `discrepancies` `[gap]`.

Access is gated by HTTP Basic Auth (`dash-auth`). Internal use only.

## Maintenance / known issues

**Completeness factors are hard-coded.** The "Database Summary" tab computes expected row counts using fixed factors (`era5:525`, `seas5:526*7`, `imerg:8690`) and fixed `stats_last_updated` dates (Oct 2024). These go stale automatically as the DB grows. Update `callbacks/callbacks.py` → `update_completeness_table` when the pipeline has processed more data.

**ISO3 and GeoJSON coverage is hard-coded.** The app only shows AFG/ETH/MDV/BRA because those are the only GeoJSON files in `data/` and the only values in the ISO3 dropdown. Adding a new country requires adding a `{iso3}_adm{n}.geojson` file and updating `utils/components.py`.

**Raw SQLAlchemy, not ocha-stratus.** DB connection strings are assembled directly in `utils/data_processing.py` using `AZURE_DB_PW_DEV/PROD` env vars. The `PGSSLMODE=require` env var may be needed for Azure PostgreSQL connections (see `infrastructure/conventions.md`). Engine is disposed after each query to avoid connection leaks.

**Local mode for dev.** Set `MODE=local` to skip all DB calls and load `data/demo-export.csv`. This is the safest way to develop/test without a live DB connection.

**MODE defaults to `dev`.** The deployed Azure app reads the dev DB unless `MODE=prod` is set in app config — easy to miss when the app is presented as "live". See `discrepancies` `[conflict]`.

**Add to deployment registry.** `chd-ds-rasterstats` is deployed but missing from `infrastructure/deployments.md`. Add a row (app `chd-ds-rasterstats`, repo `ds-raster-stats-app`, url `https://chd-ds-rasterstats.azurewebsites.net`).
