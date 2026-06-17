---
content_type: pipeline
name: glb-tropicalcyclones
type: exposure
status: live
deployment:
  platform: manual
  resource_group: null
  jobs:
    - { name: "manual analysis / ad-hoc notebooks", ref: "exploration/", schedule: "on-demand", status: live }
inputs:
  - "IBTrACS v04r00 NetCDF (NCEI download, full ALL dataset + last3years)"
  - "storms.ibtracs_tracks_geo (DB table, prod, via ocha-stratus)"
  - "storms.ibtracs_storms (DB table, prod, via ocha-stratus)"
  - "IMERG daily late v7 COGs (blob: raster container, imerg/daily/late/v7/processed/imerg-daily-late-{date}.tif)"
  - "public.imerg (DB table, prod, by pcode, via ocha-stratus)"
  - "EM-DAT tropical cyclone 2000-2022 (private blob: emdat/processed/emdat_all.parquet via ocha-stratus + legacy local XLSX)"
  - "pa-aa-phl-storms blob: processed/emdat-tropicalcyclone-2000-2022-processed-sids.csv (cross-repo reference)"
  - "GAUL ADM0 shapefile (local AA_DATA_DIR, ASAP reference data)"
  - "CERF allocations XLSX (local AA_DATA_DIR, public/raw/glb/cerf)"
  - "HumanitarianAction operations list (humanitarianaction.info download)"
  - "ECMWF cyclone hindcast XMLs (local AA_DATA_DIR_NEW, SLB processed)"
  - "ERA5 hourly precipitation GRIB via CDS API (MOZ bbox)"
  - "CODAB MOZ shapefiles (local AA_DATA_DIR, public/raw/moz/cod_ab)"
  - "CODAB via FieldMaps (stratus.datasources.codab.load_codab_from_fieldmaps)"
outputs:
  - "ds-glb-tropicalcyclones/processed/ibtracs_imerg_stats_{iso3}.parquet (blob)"
  - "ds-glb-tropicalcyclones/processed/emdat_sid_{iso3s}.parquet (blob)"
  - "IBTrACS processed parquets (local AA_DATA_DIR_NEW, public/processed/glb/ibtracs/): ibtracs_with_{wind}_wind.parquet, all_adm0_distances_*.parquet, all_adm0_thresholds_*.parquet"
  - "EM-DAT with SIDs CSV (local AA_DATA_DIR_NEW, private/processed/glb/emdat/)"
  - "CERF with ISO CSV (local AA_DATA_DIR, public/processed/glb/cerf/)"
  - "ECMWF besttrack_forecasts.csv (local, SLB processed)"
  - "Figures / scatter plots (interactive notebook outputs — not persisted to blob)"
dependencies:
  - ocha-stratus
  - ocha-lens (not currently used; stratus.datasources.codab used directly)
  - IBTrACS v04r00 (NCEI public download)
  - cdsapi (ERA5 download)
  - geopandas
  - xarray
  - rioxarray
  - dask
  - duckdb
  - pycountry
  - climada (ibtracs.ipynb exploration only)
  - jupytext
  - "AA_DATA_DIR env var (legacy local filesystem)"
  - "AA_DATA_DIR_NEW env var (current local filesystem)"
  - PGSSLMODE=require
downstream:
  - "ds-glb-tropicalcyclones-app (Azure web app chd-ds-glb-tropicalcyclones-app) — the app consumes processed IBTrACS/threshold outputs"
depends_on:
  - pipelines/ibtracs
  - pipelines/imerg
source_repo: ocha-dap/ds-glb-tropicalcyclones
source_branch: ni-2025-cyclones
source_sha: d3ec251
code_ref:
  - src/datasources/ibtracs.py
  - src/datasources/imerg.py
  - src/datasources/ecmwf.py
  - src/datasources/emdat.py
  - src/datasources/cerf.py
  - src/datasources/gaul.py
  - src/datasources/humanitarianinfo.py
  - src/datasources/codab.py
  - src/utils/rp_calc.py
  - exploration/north_indian_2025_analysis/
  - exploration/ibtracs.md
  - exploration/emdat.md
  - exploration/cerf.md
  - exploration/ecmwf.md
  - exploration/moz.md
extra:
  note: "No Databricks bundle, no GHA workflows, no scheduled entrypoint. This is an analysis/exploration repo driven entirely by Jupyter notebooks and ad-hoc Python calls. The 'pipeline' is the notebook sequence; there is no automation. The related Azure app (chd-ds-glb-tropicalcyclones-app) is a separate repo."
  local_data_dirs: "AA_DATA_DIR and AA_DATA_DIR_NEW — two legacy env vars pointing to local filesystem trees; not blob. Only the newer ni-2025-cyclones notebooks use ocha-stratus blob paths."
  active_branch_note: "ni-2025-cyclones is the most recently committed branch (2026-01-21). main is at tag c7f645e (2026-01-02). The active analysis work is entirely on ni-2025-cyclones."
  countries: "Analyses exist for: global ADM0 (IBTrACS thresholds), Mozambique (MOZ), Solomon Islands (SLB, ECMWF hindcasts), Philippines (PHL, CERF/EM-DAT), Sri Lanka (LKA, NI basin 2025), Indonesia (IDN, NI basin 2025)"
  schema_strain: "type=exposure is closest fit — this repo does both return-period exposure analysis (global IBTrACS thresholds) and impact analysis (EM-DAT joins, CERF allocations, IMERG rainfall aggregation). No single type fully captures it."
visibility: internal
last_synced: "2026-06-17"
---

# Global Tropical Cyclones

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Ad-hoc analysis library and notebook suite: download IBTrACS + IMERG + EM-DAT → compute ADM0 return-period thresholds and storm rainfall exposure → produce scatter plots for TC trigger design.*

## Jobs & schedule

This is a **notebook-driven analysis repo**, not an automated pipeline. There is no scheduler, no Databricks bundle, no GitHub Actions workflow. All execution is ad-hoc by a human running notebooks or calling `src/` functions.

| job | ref | schedule | status |
|---|---|---|---|
| IBTrACS download + threshold computation | `src/datasources/ibtracs.py` + `exploration/ibtracs.md` | on-demand | live |
| IMERG aggregation per country | `exploration/north_indian_2025_analysis/ibtracs_imerg_agg_{iso3}.ipynb` | on-demand | live |
| EM-DAT matching + upload | `exploration/north_indian_2025_analysis/emdat.ipynb` | on-demand | live |
| Scatter plots / return-period vis | `exploration/north_indian_2025_analysis/scatter_plot_{iso3}.ipynb` | on-demand | live |
| ECMWF hindcast processing (SLB) | `src/datasources/ecmwf.py` + `exploration/ecmwf.md` | on-demand | live (legacy) |
| ERA5 MOZ download | `src/datasources/era5.py` + `exploration/moz_rainfall.md` | on-demand | live (legacy) |

The associated **Azure web app** (`chd-ds-glb-tropicalcyclones-app`, repo `ds-glb-tropicalcyclones-app`) is a separate deployment that consumes outputs produced by this analysis.

## Inputs

**IBTrACS (primary)**
- Direct HTTP download from NCEI: `IBTrACS.{ALL|last3years}.v04r00.nc`
- DB tables `storms.ibtracs_tracks_geo` and `storms.ibtracs_storms` via `stratus.get_engine(stage="prod")` (used in ni-2025-cyclones notebooks)

**IMERG**
- COG rasters from blob: `imerg/daily/late/v7/processed/imerg-daily-late-{date}.tif` (container: `raster`, stage: `prod`)
- DB table `public.imerg` (by pcode, e.g. `pcode = 'LK'`) via `stratus.get_engine(stage="prod")`

**EM-DAT**
- Current: `emdat/processed/emdat_all.parquet` (blob: `global` container) via DuckDB + `stratus.get_container_client`
- Legacy: local XLSX under `AA_DATA_DIR_NEW/private/raw/glb/emdat/`
- Cross-repo processed CSV: `pa-aa-phl-storms/processed/emdat-tropicalcyclone-2000-2022-processed-sids.csv` (loaded via `stratus.load_csv_from_blob`)

**Administrative boundaries**
- GAUL ADM0 shapefile (local `AA_DATA_DIR`, ASAP reference data) — used for older IBTrACS threshold computations
- CODAB via FieldMaps: `stratus.datasources.codab.load_codab_from_fieldmaps(iso3=...)` — used in newer ni-2025-cyclones analysis

**Auxiliary**
- CERF allocations XLSX (local `AA_DATA_DIR`, 2024-02-27 snapshot)
- HumanitarianAction operations list (HTTP download from `humanitarianaction.info`)
- ECMWF cyclone hindcast XMLs (local `AA_DATA_DIR_NEW`, SLB, SLB-specific)
- ERA5 hourly precipitation via CDS API (MOZ bounding box only)
- Mozambique CODAB shapefiles (local `AA_DATA_DIR`, MOZ-specific)

## Steps

**Core IBTrACS pipeline (global, main branch)**

1. `ibtracs.download_ibtracs()` — fetch NetCDF from NCEI → `AA_DATA_DIR_NEW/public/raw/glb/ibtracs/`
2. `ibtracs.process_all_ibtracs(wind_provider)` — flatten NetCDF to parquet with lat/lon/wind/sid columns
3. `ibtracs.calculate_adm0_distances()` — for each GAUL ADM0 country, compute storm-track point distances to country boundary → per-country parquets
4. `ibtracs.concat_adm0_distances()` — merge per-country parquets into one global file
5. `ibtracs.calculate_thresholds()` — grid search over distance thresholds (0–400 km, 10 km steps) × wind speed thresholds (30+ kt, 5 kt steps) to count unique storm hits per ADM0 → threshold parquet

**North Indian basin 2025 analysis (ni-2025-cyclones branch)**

1. Load IBTrACS tracks from DB (`storms.ibtracs_tracks_geo` filtered to NI basin)
2. Filter by distance to ADM0 boundary (e.g. 230 km for LKA)
3. Aggregate storm-track records to per-storm max wind speed + time range
4. Load IMERG daily from DB (`public.imerg`) and compute 2-day rolling sum during storm window
5. Load EM-DAT (new blob + legacy CSV), join by storm SID, upload merged parquet to blob under `ds-glb-tropicalcyclones/processed/`
6. Scatter plots: wind speed vs IMERG rainfall, annotated with EM-DAT impact, with return-period ranking via `rp_calc.calculate_one_group_rp()`

**Legacy country analyses** (`exploration/moz.md`, `exploration/ecmwf.md`, `exploration/cerf.md`)
- ECMWF XML → CSV → best-track hindcasts (SLB-specific, uses local filesystem only)
- ERA5 hourly GRIB download via CDS API (MOZ-specific)
- CERF allocation matching to IBTrACS SIDs + GAUL ADM0

## Outputs

| artifact | location | notes |
|---|---|---|
| `ibtracs_imerg_stats_{iso3}.parquet` | blob `ds-glb-tropicalcyclones/processed/` | per-storm wind + IMERG stats, per country |
| `emdat_sid_{iso3s}.parquet` | blob `ds-glb-tropicalcyclones/processed/` | EM-DAT events joined to IBTrACS SIDs |
| `ibtracs_with_{wind}_wind.parquet` | local `AA_DATA_DIR_NEW/public/processed/glb/ibtracs/` | flattened IBTrACS track points |
| `all_adm0_distances_*.parquet` | local `AA_DATA_DIR_NEW/public/processed/glb/ibtracs/` | storm-point to ADM0 distances, global |
| `all_adm0_thresholds_*.parquet` | local `AA_DATA_DIR_NEW/public/processed/glb/ibtracs/` | hit counts per ADM0 × (d_thresh, s_thresh) grid |
| `emdat-tropicalcyclone-2000-2022-processed-sids.csv` | local `AA_DATA_DIR_NEW/private/processed/glb/emdat/` | legacy EM-DAT × IBTrACS match |
| `besttrack_forecasts.csv` | local `AA_DATA_DIR_NEW/public/processed/slb/ecmwf/cyclone_hindcasts/` | SLB ECMWF hindcasts only |
| Scatter plots / figures | notebook outputs, not persisted | LKA and IDN NI-basin analyses |

## Dependencies

- `ocha-stratus` — blob reads/writes (COG, parquet, CSV), DB engine (`storms.*`, `public.imerg`, `emdat/processed/emdat_all.parquet`), FieldMaps CODAB
- `geopandas`, `xarray`, `rioxarray`, `dask` — spatial/raster processing
- `duckdb` — remote parquet queries over blob URLs
- `pycountry` — ISO code resolution for EM-DAT and CERF country matching
- `cdsapi` — ERA5 download (MOZ only)
- `climada` — used in `exploration/ibtracs.ipynb` for `TCTracks` (exploration only)
- `jupytext` — notebook format (.ipynb ↔ .md)
- `PGSSLMODE=require` — required for Azure PostgreSQL connections
- `AA_DATA_DIR` and `AA_DATA_DIR_NEW` — local environment variables pointing to on-disk data directories; most older functions use these rather than blob

## Failure modes & debugging

**No automation = no automated failure.** Breakage manifests when a human runs a notebook and it errors.

- **NCEI IBTrACS download fails**: NCEI URL is public; check https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/ for dataset availability. The v04r00 dataset updates irregularly.
- **DB table `storms.ibtracs_tracks_geo` or `storms.ibtracs_storms` missing/stale**: these are populated by the separate `ds-glb-tropicalcyclones` (or `ds-storms-pipeline`) Databricks job `Run IBTrACS` (job_id `638351145729392`). If the DB query returns nothing or stale data, check that job's run history in Databricks.
- **IMERG blob or DB table not found**: IMERG rasters are written by the `Run IMERG` Databricks job (job_id `666239885322861`). Check that job. DB table `public.imerg` is populated by the IMERG pipeline.
- **EM-DAT blob `emdat/processed/emdat_all.parquet` not found**: This is an external dependency — find who populates this blob. Not clearly owned by this repo.
- **`AA_DATA_DIR` / `AA_DATA_DIR_NEW` not set**: Most `src/datasources/` functions will throw `TypeError: argument of type 'NoneType' is not iterable` or similar on `Path(os.getenv(...))`. Set both env vars to valid local data directories.
- **PGSSLMODE not set**: Azure PostgreSQL connections will fail with SSL errors. Always set `PGSSLMODE=require` before running notebooks that call `stratus.get_engine()`.
- **`pa-aa-phl-storms` blob reference**: `exploration/north_indian_2025_analysis/emdat.ipynb` reads `pa-aa-phl-storms/processed/emdat-tropicalcyclone-2000-2022-processed-sids.csv` from blob. This is a cross-repo dependency; if that blob is deleted or moved, the notebook fails silently with a missing file error.

## Downstream consumers

- **`ds-glb-tropicalcyclones-app`** (Azure web app `chd-ds-glb-tropicalcyclones-app`, listed in `infrastructure/deployments.md`) — interactive visualization app that consumes the processed IBTrACS threshold parquets produced by this analysis repo. See the app's own page for details.
- Framework trigger design work (e.g. `pa-aa-fji-storms`, `pa-aa-phl-storms`, `ds-aa-hti-hurricanes`) may reference the global threshold methodology from this repo, but those repos carry their own code.
