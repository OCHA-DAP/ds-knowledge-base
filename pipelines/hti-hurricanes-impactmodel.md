---
content_type: pipeline
name: hti-hurricanes-impactmodel
type: exposure
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Predictions on affected population from grid-based 2STG-XGB model", ref: ".github/workflows/main.yml", schedule: "on push to fede-implementation + workflow_dispatch (daily cron commented out)", status: live }
inputs:
  - "ECMWF HRES TC forecast tracks via climada-petals TCForecast.fetch_ecmwf()"
  - "GEFS precipitation forecast (NOMADS: nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/gefs.<date>/prcp_bc_gb2/)"
  - "blob dev container (imb0chd0dev / isi): ds-aa-hti-hurricanes/features_combined/stationary_data_hti.csv"
  - "blob dev container: ds-aa-hti-hurricanes/grid/output_dir/hti_0.1_degree_grid_land_overlap.gpkg"
  - "blob dev container: ds-aa-hti-hurricanes/grid/input_dir/grid_municipality_info.csv"
  - "blob dev container: ds-aa-hti-hurricanes/model/weather_constraints/xgb.pkl (+ xgb_class.pkl, xgbR.pkl)"
outputs:
  - "blob dev container: ds-aa-hti-hurricanes/windfield/ECMWF/<YYYYMMDD>/wind_data.csv (per-grid windspeed + track fields)"
  - "blob dev container: ds-aa-hti-hurricanes/windfield/ECMWF/<YYYYMMDD>/track_data.csv"
  - "blob dev container: ds-aa-hti-hurricanes/rainfall/GEFS/<YYYYMMDD>/rainfall_data_rw_mean.csv"
  - "blob dev container: ds-aa-hti-hurricanes/model/predictions/impact_predictions_<YYYYMMDD>.csv (ADM1-level, conditional on trigger)"
  - "GHA artifact: output_<YYYYMMDD>.txt + output_<YYYYMMDD>.zip (trigger status message)"
dependencies:
  - "climada==4.0.1 + climada-petals==4.0.2 (ECMWF TC track fetch + windfield modelling)"
  - "xgboost==2.0.1 + scikit-learn==1.3.2 (2-stage impact model inference)"
  - "geopandas + rasterio + rasterstats (spatial operations on GEFS rasters)"
  - "azure-storage-blob==12.20.0 (raw SDK; NOT ocha-stratus)"
  - "beautifulsoup4 (NOMADS HTML scrape for GEFS files)"
  - "joblib (model serialisation)"
  - "Secret: ISI_BLOB_SAS -> DEV_BLOB_SAS env var (GitHub Actions secret)"
downstream: []   # no verified consumer — impact_predictions CSV is written to dev blob and read by no known KB page. The hti-hurricanes-app reads the framework MONITORING trigger data, NOT this model (see discrepancies).
related:
  - "pipelines/hti-hurricanes-monitoring (sibling in repo ds-aa-hti-hurricanes — the framework NHC+CHIRPS-GEFS trigger eval; DISTINCT from this XGBoost impact model)"
  - "frameworks/hti-hurricanes/2024-08-23 (the AA framework this model supports)"
  - "pipelines/glb-cyclones-impactmodel (sibling EM-DAT/IBTrACS impact-model approach)"
depends_on:
  - "infrastructure/storage"
source_repo: ocha-dap/ds-aa-hti-hurricanes-impactmodel
source_branch: fede-implementation
source_sha: 9fbc25c
code_ref:
  - "main.py — entrypoint: trigger check, inference, blob write"
  - "src/datasources/ECMWF/realtime_wind_data.py — ECMWF fetch + ROI trigger"
  - "src/datasources/GEFS/realtime_rainfall_data.py — NOMADS download + zonal stats"
  - "src/model_training.py — offline training script (run manually)"
  - "src/utils/blob.py — raw Azure SDK blob helpers (prod + dev containers)"
  - ".github/workflows/main.yml — GHA workflow definition"
extra:
  model_approach: "Grid-based XGBoost, 3 serialised models (xgb.pkl regressor + xgb_class.pkl classifier + xgbR.pkl regressor on the damage-positive subset); grid resolution 0.1 degree; per-grid predictions aggregated to ADM1. (Repo names it the '2STG' / 2-stage model in the workflow title even though 3 .pkl artifacts are loaded.)"
  trigger_logic: "Internal trigger fires when at least one ECMWF TC track intersects a bounding box ±3 deg around Haiti — ROI = lon (-75-deg) to (-71+deg), lat (17-deg) to (21+deg) = lon -78..-68, lat 14..24 at deg=3 — within a 120-HOUR forecast look-ahead horizon (create_windfield_dataset(thres=120, deg=3); thres is hours, NOT a windspeed). There is NO windspeed threshold in the trigger: any track whose line intersects the ROI (with >4 datapoints inside the 120h window) fires it. No prediction is written if no track is in ROI."
  blob_container: "dev (imb0chd0dev/isi) — not prod. The workflow injects ISI_BLOB_SAS as DEV_BLOB_SAS; PROD_BLOB_SAS is optional and unused in the GHA path."
  training_data: "EMDAT historical impact data (24 hurricane events Haiti 2002-2021); stationary features pre-built from IbTrACS, NASA PPS, Meta Data for Good (population), DWTKNS SRTM (topography), GlobalDataLab IWI, Google Open Buildings. Training run separately via src/model_training.py; trained models stored on blob."
  schedule_note: "Daily cron ('0 0 * * *') is commented out in main.yml. The workflow currently fires on push to fede-implementation and via workflow_dispatch only — effectively on-demand / during active hurricane season."
  ocha_stratus_not_used: "Uses raw azure-storage-blob SDK via src/utils/blob.py rather than ocha-stratus. Convention deviation vs team standard."
discrepancies:
  - "[gap] Not in infrastructure/deployments.md GHA-pipelines table. The registry has no row for ds-aa-hti-hurricanes-impactmodel (no Databricks job, no Azure web app) — it should be added there."
  - "[conflict] Deployed branch is fede-implementation (workflow pushes/checks out fede-implementation), NOT main. main is stale for this pipeline. The page reflects fede-implementation."
  - "[conflict] This is a DEV deployment: every write goes to the dev blob (imb0chd0dev/isi) via DEV_BLOB_SAS (mapped from secret ISI_BLOB_SAS). The prod container is coded but never wired in the GHA path. status: live overstates maturity — it is a development/prototype deployment that fires on push, not a scheduled prod pipeline."
  - "[stale] Daily cron '0 0 * * *' is commented out in main.yml. Effective trigger is push-to-fede-implementation + workflow_dispatch only (on-demand). To run on schedule the cron must be uncommented on fede-implementation."
  - "[gap] No verified downstream consumer of impact_predictions_<date>.csv. The originally-recorded link (hti-hurricanes-app reads the model output) is WRONG: ds-aa-hti-hurricanes-app reads the framework MONITORING outputs (processed/<trig>.csv, processed/monitors.parquet, NHC historical_forecasts parquet under ds-aa-hti-hurricanes/), not this model's model/predictions/ CSV. The app depends_on hurricanes-monitoring, not this impact model."
  - "[stale] Workflow title calls it the '2STG-XGB' (2-stage) model, but main.py loads 3 .pkl artifacts (xgb, xgb_class, xgbR)."
visibility: internal
last_synced: "2026-06-22"
---

# HTI Hurricanes Impact Model

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

On-demand (or push-triggered): fetch ECMWF TC forecast + GEFS rainfall → check ROI trigger → if a storm threatens Haiti, run 2-stage XGBoost to predict % population affected per ADM1 → write CSV to blob.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Predictions on affected population from grid-based 2STG-XGB model | `.github/workflows/main.yml` | push to `fede-implementation` + `workflow_dispatch` (daily cron commented out) | live |

No Databricks job, no Azure web app. **Not yet listed in `infrastructure/deployments.md`** (GHA-pipelines table) — should be added. Deployment is a **dev slot**: runs on `fede-implementation` (not `main`), fires on push + `workflow_dispatch` (daily cron commented out), writes to the **dev** blob via `ISI_BLOB_SAS`→`DEV_BLOB_SAS`. `status: live` here means "the workflow runs on push", not "scheduled prod".

## Inputs

**Real-time (per run):**
- ECMWF HRES TC forecast tracks — fetched live via `climada_petals.hazard.TCForecast.fetch_ecmwf()`. Up to 120h look-ahead.
- GEFS precipitation forecast — scraped from NOMADS (`nomads.ncep.noaa.gov/pub/data/nccf/com/naefs/prod/gefs.<YYYYMMDD>/<HH>/prcp_bc_gb2/`). Falls back through 18h, 12h, 06h, 00h run folders.

**Static / pre-built (blob dev container `isi`):**
- `ds-aa-hti-hurricanes/features_combined/stationary_data_hti.csv` — merged stationary features (population, topography, IWI, buildings, coastline) per grid cell
- `ds-aa-hti-hurricanes/grid/output_dir/hti_0.1_degree_grid_land_overlap.gpkg` — Haiti 0.1° grid (land cells only)
- `ds-aa-hti-hurricanes/grid/input_dir/grid_municipality_info.csv` — grid → ADM1 crosswalk
- `ds-aa-hti-hurricanes/model/weather_constraints/xgb.pkl` + `xgb_class.pkl` + `xgbR.pkl` — serialised trained models

## Steps

1. **ROI trigger check** (`ECMWF/realtime_wind_data.py → create_windfield_dataset`): fetch all current ECMWF TC ensemble tracks, filter to 120h horizon, compute CLIMADA windfields on the Haiti 0.1° grid, flag tracks intersecting Haiti bounding box (±3 deg). Returns `True` if any tracks are in ROI.
2. **If trigger = False**: write a `output_<date>.txt` noting "Trigger condition not met" and stop.
3. **Build input dataset** (`main.py → create_input_dataset`): load stationary features from blob; load today's windfield CSV (written in step 1); download and process GEFS rainfall for each triggered event (zonal stats → 6h/24h max); merge all features.
4. **Inference** (`main.py → predict_new_data`): load three serialised XGBoost models from blob; run 2-stage prediction at grid level (regressor → classifier → regressor on damage-positive cells).
5. **ADM1 aggregation** (`main.py → aggregate_predictions_adm1`): join grid predictions to ADM1 via municipality crosswalk; sum affected population; add pre-calibrated bootstrapping error bins.
6. **Write output**: save ADM1 prediction CSV to `ds-aa-hti-hurricanes/model/predictions/impact_predictions_<date>.csv` on blob; upload GHA artifact (`output_<date>.txt` + optional zip).

**Training** (separate, manual): `src/model_training.py` trains on EMDAT historical impact (24 HTI hurricane events 2002–2021) merged with stationary features; serialises three `.pkl` models to blob.

## Outputs

| output | location | condition |
|---|---|---|
| Per-grid windfield CSV | `ds-aa-hti-hurricanes/windfield/ECMWF/<YYYYMMDD>/wind_data.csv` (blob dev) | trigger fires |
| Per-grid track CSV | `ds-aa-hti-hurricanes/windfield/ECMWF/<YYYYMMDD>/track_data.csv` (blob dev) | trigger fires |
| Per-grid rainfall CSV | `ds-aa-hti-hurricanes/rainfall/GEFS/<YYYYMMDD>/rainfall_data_rw_mean.csv` (blob dev) | trigger fires |
| ADM1 impact predictions CSV | `ds-aa-hti-hurricanes/model/predictions/impact_predictions_<YYYYMMDD>.csv` (blob dev) | trigger fires |
| Status text + zip artifact | GHA run artifacts | every run |

All blob writes go to the **dev container** (`imb0chd0dev/isi`). Prod container is supported in `blob.py` but the GHA injects only `ISI_BLOB_SAS` → `DEV_BLOB_SAS`.

## Dependencies

- **climada 4.0.1 + climada-petals 4.0.2** — ECMWF TC track retrieval (`TCForecast.fetch_ecmwf`) and windfield modelling (`TropCyclone.from_tracks`)
- **xgboost 2.0.1** — 2-stage model inference and training
- **scikit-learn 1.3.2, joblib 1.3.2** — model persistence
- **geopandas 0.14.0, rasterio 1.3.9, rasterstats 0.19.0** — spatial processing of GEFS rasters
- **azure-storage-blob 12.20.0** — raw SDK blob access (NOT ocha-stratus — convention deviation)
- **beautifulsoup4 4.12.2** — HTML scraping of NOMADS directory listing
- **Secret:** `ISI_BLOB_SAS` in GitHub Actions secrets, exposed as `DEV_BLOB_SAS` env var; `PROD_BLOB_SAS` optional (not injected in GHA)
- **eccodes** — installed separately in CI (ECMWF GRIB handling for climada)

## Failure modes & debugging

**ECMWF not responding**: `TCForecast.fetch_ecmwf()` raises an exception, caught in `main.py` as `ValueError("ECMWF not responding")`. The GHA step fails with exit non-zero; check GHA run logs for the traceback. This is the most common failure point — ECMWF service is sometimes unavailable.

**GEFS not available**: `download_gefs_data` silently returns (no files downloaded) if all four NOMADS folder variants (18h, 12h, 06h, 00h) return non-200. The pipeline then crashes on missing files when processing the rainfall dataset. No explicit error message.

**Missing blob data**: Any blob read fails with an Azure SDK exception if pre-built features or model files are absent. Check that `stationary_data_hti.csv`, grid files, and model `.pkl` files exist in the dev container under `ds-aa-hti-hurricanes/`.

**DEV_BLOB_SAS absent or expired**: `ContainerClient.from_container_url` fails or all blob operations return 403. The secret `ISI_BLOB_SAS` must be valid in the repo's GitHub Actions secrets.

**No trigger** (not a failure): When no TC track intersects the ROI, the pipeline writes `output_<date>.txt` with "Trigger condition not met" and exits 0. The GHA reports success; check the artifact to confirm.

**Logs**: GitHub Actions run logs at `https://github.com/ocha-dap/ds-aa-hti-hurricanes-impactmodel/actions`. Blob-side intermediate files (`windfield/`, `rainfall/`) can be inspected via Azure Storage Explorer pointed at `imb0chd0dev`.

**Schedule is effectively off**: The daily cron is commented out. Runs only on push or manual dispatch. To activate during hurricane season, uncomment the cron in `.github/workflows/main.yml` on `fede-implementation`.

## Downstream consumers

**None verified.** The `impact_predictions_<date>.csv` is written to the dev blob and no known KB page reads it.

Do **not** confuse this with the framework monitoring stack:
- [`pipelines/hti-hurricanes-monitoring`](hti-hurricanes-monitoring.md) — the framework's NHC + CHIRPS-GEFS / IMERG **trigger evaluation** (repo `ds-aa-hti-hurricanes`). A different system; this impact model is a separate XGBoost prediction repo (`ds-aa-hti-hurricanes-impactmodel`).
- [`apps/hti-hurricanes-app`](../apps/hti-hurricanes-app.md) (`chd-ds-aa-hti-hurricanes-app`) reads the **monitoring** outputs (`processed/<trig>.csv`, `processed/monitors.parquet`, NHC historical-forecasts parquet) — verified in the app repo's `data/load_data.py` / `src/datasources/`. It does **not** read this model's `model/predictions/` CSV.

Related: [`frameworks/hti-hurricanes/2024-08-23`](../frameworks/hti-hurricanes/2024-08-23.md) (the AA framework this model was built to support); [`pipelines/glb-cyclones-impactmodel`](glb-cyclones-impactmodel.md) (sibling impact-model approach).
