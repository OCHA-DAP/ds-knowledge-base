---
content_type: pipeline
name: glb-cyclones-impactmodel
type: exposure
status: live
deployment:
  platform: manual
  resource_group: null
  jobs:
    - { name: "model-training (manual)", ref: "src_global/model_training_example.py", schedule: on-demand, status: live }
inputs:
  - "EM-DAT tropical cyclone dataset (CSV, 2000-2022, with IBTrACS SIDs)"
  - "IBTrACS NetCDF (via CLIMADA TCTracks.from_ibtracs_netcdf)"
  - "IMERG daily late rainfall rasters (v6 2003+, v7 2000-2003) — blob: global container imerg/{v6|v7}/imerg-daily-late-{date}.tif"
  - "WorldPop 2020 global 1km population raster (worldpop.org)"
  - "GADM ADM2 shapefile (gadm.org download_world)"
  - "JRC CEMS-GLOFAS flood hazard rasters (RP10, depth_reclass.tif tiles)"
  - "World Bank landslide susceptibility raster (LS_RF_Median_1980-2018_COG.tif)"
  - "4TU storm surges netCDF"
  - "JRC GHS-SMOD urban/rural degree-of-urbanisation raster"
  - "GDL Sub-national Human Development Index (SHDI) v8.0 CSV + shapefile"
  - "blob: global_model/IBTRACKS/wind_data_part_{1..183}.csv (pre-computed windfield features)"
  - "blob: global_model/PPS/rainfall_data_part_{1..173}.csv (pre-computed rainfall features)"
  - "blob: global_model/EMDAT/impact_data_part_{1..8}.csv"
  - "blob: global_model/EMDAT/grid_based/impact_data_grid_global_part_{1..183}.csv"
  - "blob: global_model/WORLDPOP/processed_pop/pop_grid_global_part_{1..8}.csv"
  - "blob: global_model/GRID/grid_municipality_info_part_{1..8}.csv"
outputs:
  - "Trained XGBoost regressor (local .npz files of y_test / y_pred per country)"
  - "blob: global_model/model_input/model_input_data_part_{n}.csv (merged feature table)"
  - "blob: global_model/model_input/model_input_data_weather_constraints_part_{n}.csv"
  - "Intermediate per-country CSVs written to local /data/big/fmoss/data/ (researcher workstation)"
dependencies:
  - "CLIMADA 4.0.1 / climada-petals 4.0.2 (wind field modelling)"
  - "XGBoost 2.0.1 (model training)"
  - "scikit-learn 1.3.2"
  - "azure-storage-blob 12.20.0 (direct raw SDK — not ocha-stratus)"
  - "rioxarray / rasterio (raster I/O)"
  - "geopandas / shapely (vector processing)"
  - "imbalanced-learn / SHAP"
  - "DEV_BLOB_SAS_GLOBAL env var (SAS token for imb0chd0dev `global` container, hardcoded fallback in blob.py)"
  - "DEV_BLOB_SAS env var (SAS token for imb0chd0dev `isi` container)"
downstream:
  - "ds-glb-tropicalcyclones-app (likely consumer of model output — chd-ds-glb-tropicalcyclones-app Azure web app)"
depends_on:
  - "pipelines/imerg"
source_repo: ocha-dap/ds-glb-cyclones-impactmodel
source_branch: fede-implementation
source_sha: 9514c20
code_ref:
  - "src_global/datasources/00-GADM/ — GADM boundary download + grid creation"
  - "src_global/datasources/01-EMDAT/ — EM-DAT cleaning, geolocating, grid disaggregation, past-event count"
  - "src_global/datasources/02-WorldPop/ — WorldPop download + grid aggregation"
  - "src_global/datasources/03-SRTM/ — SRTM DEM download + coastline features"
  - "src_global/datasources/04-IbTracks/ — IBTrACS wind field modelling (CLIMADA)"
  - "src_global/datasources/05-PPS/ — IMERG rainfall to grid"
  - "src_global/datasources/06-FloodRisk/ — JRC CEMS-GLOFAS flood risk rasters"
  - "src_global/datasources/07-LandslideRisk/ — World Bank landslide raster"
  - "src_global/datasources/08-StormSurgesRisk/ — 4TU storm surges data"
  - "src_global/datasources/09-UrbanRuralAreas/ — JRC GHS-SMOD urban/rural"
  - "src_global/datasources/10-SHDI/ — GDL SHDI to grid"
  - "src_global/datasources/merge_features.py — merge all features into model input table"
  - "src_global/model_training_example.py — XGBoost/linear regressor training + LOOCV"
  - "src_global/utils/blob.py — raw Azure SDK blob access (dev + prod containers)"
  - "src_global/utils/grid.py — 0.1-degree grid creation per country"
  - "src_global/utils/impact_to_grid.py — impact disaggregation to grid cells"
extra:
  note_ocha_stratus: "Does NOT use ocha-stratus. All blob access is via raw azure-storage-blob SDK with SAS tokens. DEV_BLOB_SAS_GLOBAL is hardcoded in blob.py as a fallback (valid until 2026-02-18) — a security/rotation concern."
  note_no_deployment: "No Databricks jobs, no GHA workflows, no Azure web app. All processing was run on researcher's local workstation (/data/big/fmoss/data/) and outputs pushed to blob. Not in deployments.md."
  note_branch: "main has only an init commit (654ffa6, 2024-07-22). All real code is on fede-implementation branch (9514c20, 2024-07-22) — never merged."
  note_countries: "64 countries in iso3_list (constant.py). Model training example targets PHL / HTI by default."
  note_imerg_versions: "IMERG v7 covers 2000-06-01 to 2003-12-31; IMERG v6 covers 2003-03-11 onwards."
  schema_strain: "platform=manual chosen because there is no scheduler of any kind. outputs_or_data_count counts distinct blob path patterns + local output files."
visibility: internal
last_synced: "2026-06-17"
---

# Global Tropical Cyclones Impact Model

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Research pipeline: ingest EM-DAT historical cyclone impacts + IBTrACS wind tracks + IMERG rainfall + seven static risk layers → build 0.1-degree global grid features → train XGBoost regressor to predict % population affected per grid cell per cyclone event.

## Jobs & schedule

There are no scheduled jobs, no Databricks bundles, and no GitHub Actions workflows. All processing was run manually on a researcher workstation (`/data/big/fmoss/data/`) with results pushed to Azure Blob Storage.

| job | ref | schedule | status |
|---|---|---|---|
| model-training (manual) | `src_global/model_training_example.py` | on-demand | live |
| feature-pipeline (manual) | `src_global/datasources/*/` scripts run sequentially | on-demand | live |

## Inputs

**EM-DAT (historical impact records)**
- Source CSV: `emdat-tropicalcyclone-2000-2022-processed-sids.csv` (loaded locally by researcher)
- `src_global/datasources/01-EMDAT/create_impact_dataset.py` cleans, geolocates (GADM ADM2 spatial join), disaggregates to ADM0/1/2, and pairs each event with an IBTrACS SID
- Outputs land in `global_model/EMDAT/` on blob

**IBTrACS wind tracks**
- Loaded via CLIMADA `TCTracks.from_ibtracs_netcdf(storm_id=sid)` per event
- Tracks are interpolated to 30-min intervals, then wind fields computed at 0.1-degree grid centroids using CLIMADA `TropCyclone.from_tracks`
- Pre-computed results on blob: `global_model/IBTRACKS/wind_data_part_{1..183}.csv`

**IMERG rainfall**
- Daily late IMERG rasters read directly from blob COG URLs: `imerg/{v6|v7}/imerg-daily-late-{date}.tif`
- Aggregated to max 24h rainfall in ±2-day window around landfall per storm/grid cell
- Pre-computed results: `global_model/PPS/rainfall_data_part_{1..173}.csv`

**Static risk layers (all processed to 0.1-degree grid)**
- WorldPop 2020 (1 km population raster from worldpop.org)
- GADM ADM2 boundaries (gadm.org)
- JRC CEMS-GLOFAS RP10 flood hazard tiles (`_depth_reclass.tif`)
- World Bank landslide susceptibility (`LS_RF_Median_1980-2018_COG.tif`)
- 4TU storm surges NetCDF
- JRC GHS-SMOD urban/rural classification
- GDL SHDI v8.0 (sub-national HDI, 2020 vintage)

## Steps

1. **Grid creation** (`utils/grid.py`): for each of 64 countries, create 0.1-degree polygon grid clipped to GADM land boundaries; assign municipality (GID_0/1/2) to each cell by largest intersection area.
2. **Impact geolocating** (`datasources/01-EMDAT/create_impact_dataset.py`): clean EM-DAT, match admin regions to GADM (ADM1/ADM2/ADM0), assign IBTrACS SID, then disaggregate to grid level proportionally by population.
3. **Wind features** (`datasources/04-IbTracks/wind_to_grid.py`): per event per country, download IBTrACS track via CLIMADA, interpolate, compute gridded wind speed + track distance.
4. **Rainfall features** (`datasources/05-PPS/rain_to_grid.py`): for each event, extract IMERG daily rasters for ±2 days around landfall, aggregate to max rainfall per grid cell.
5. **Static risk aggregation** (datasources 02–10): download/process each risk layer, aggregate to 0.1-degree grid.
6. **Feature merge** (`datasources/merge_features.py`): join wind, rain, impact, population, flood risk, landslide risk, and vulnerability metadata into a single flat table; upload to blob in chunks.
7. **Model training** (`model_training_example.py`): load merged feature table; train XGBoost regressor with LOOCV (leave-one-event-out) scheme, asymmetric track-distance-weighted loss, save predictions to `.npz`.

## Outputs

| output | path / location | format |
|---|---|---|
| Merged model input (no weather constraints) | `global_model/model_input/model_input_data_part_{n}.csv` | blob CSV (chunked) |
| Merged model input (with weather constraints) | `global_model/model_input/model_input_data_weather_constraints_part_{n}.csv` | blob CSV (chunked) |
| Grid impact data (global, by cell) | `global_model/EMDAT/grid_based/impact_data_grid_global_part_{n}.csv` | blob CSV |
| Windfield features (per country) | `global_model/IBTRACKS/wind_data_part_{n}.csv` | blob CSV |
| Rainfall features (per country) | `global_model/PPS/rainfall_data_part_{n}.csv` | blob CSV |
| Municipality–grid mapping | `global_model/GRID/grid_municipality_info_part_{n}.csv` | blob CSV |
| Population grid | `global_model/WORLDPOP/processed_pop/pop_grid_global_part_{n}.csv` | blob CSV |
| Model predictions | `{country}_xgb_*.npz` | local `.npz` |

No DB writes. No email sending.

## Dependencies

- **CLIMADA 4.0.1 + climada-petals 4.0.2** — physics-based wind field modelling (TCTracks, TropCyclone). Core dependency; version-pinned.
- **XGBoost 2.0.1** — gradient boosted tree regressor
- **azure-storage-blob 12.20.0** — direct raw SDK (NOT ocha-stratus). Two containers on `imb0chd0dev`:
  - `global` container: accessed with `DEV_BLOB_SAS_GLOBAL` (hardcoded fallback SAS in `blob.py`, valid until 2026-02-18)
  - `isi` container: accessed with `DEV_BLOB_SAS` env var
- **rioxarray / rasterio** — raster I/O and clipping
- **geopandas / shapely** — vector operations, grid creation, spatial joins

**Secrets / env vars:**
- `DEV_BLOB_SAS_GLOBAL` — SAS token for `global` container; **hardcoded fallback in blob.py expires 2026-02-18**
- `DEV_BLOB_SAS` — SAS token for `isi` container; from `.env`

## Failure modes & debugging

**Not a scheduled system.** There are no logs to check — all runs were interactive (Jupyter notebooks or `__main__` blocks on a researcher workstation). Failures leave partial CSV files locally.

- **IBTrACS SID not found**: `TCTracks.from_ibtracs_netcdf` silently appended to `problematic_sid` list; corresponding country's storm appears in `nodata_storms_{iso3}.csv`. Check `all_events.sid` values against IBTrACS.
- **IMERG raster read failure**: `rain_to_grid.py` logs errors to `rainfall_processing.log` and writes `nodata_rainfall_{iso3}.csv`. Check COG URL accessibility on blob.
- **SAS token expiry (DEV_BLOB_SAS_GLOBAL)**: hardcoded SAS in `blob.py` expired 2026-02-18. Blob reads/writes will fail with HTTP 403. Rotate and update `blob.py` line 21, or set `DEV_BLOB_SAS_GLOBAL` env var.
- **CLIMADA version incompatibility**: code uses `tc.intensity`, `tracks.get_track()`, `Centroids.from_geodataframe` — check against CLIMADA 4.x API if upgrading.
- **Local-path hardcodes**: several `__main__` blocks use absolute paths like `/data/big/fmoss/data/` and `/home/fmoss/GLOBAL MODEL/` — will fail on any other machine without adjustment.
- **Blob chunking**: large datasets split into up to 193 chunks (e.g. `impact_data_grid_global_weather_constraints_part_{1..193}`). A missing chunk causes silent data loss in the concat.

## Downstream consumers

- **`ds-glb-tropicalcyclones-app`** (`chd-ds-glb-tropicalcyclones-app` Azure web app, Running) — likely the primary consumer of model outputs; consult that repo to confirm which blob paths it reads.
- Country-level AA frameworks (e.g. `ds-aa-hti-hurricanes`, referenced in commented-out code) — the model was originally developed for Haiti and extended globally; these repos may use model predictions.
