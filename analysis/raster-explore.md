---
content_type: analysis
name: raster-explore
analysis_type: exploratory     # technical/infra spike comparing raster storage backends; not a country/hazard framework
status: dormant                # 4 self-contained notebooks, frozen extracts (2000-2008), no CI, no schedule; superseded operationally by ds-raster-pipelines
country_iso3: global           # generic storage-format/infra exploration; Haiti/Nicaragua appear only as convenient test AOIs, not the analytical subject
hazard: multi-hazard           # touches precipitation (IMERG), reanalysis (ERA5) and seasonal forecast (SEAS5) generically, not one hazard
summary: "Sample notebooks comparing cloud-native raster storage options (Zarr vs. individual COGs) for ERA5/IMERG, and validating CRS alignment between MARS- and AWS-derived SEAS5 ensemble-mean COGs. Infra/format spike, not a country or hazard analysis — no trigger, no schedule, nothing deployed."
data_sources: [ERA5, IMERG, SEAS5, CODAB]
feeds: [raster-pipelines]      # the MARS-vs-AWS CRS finding maps directly onto raster-pipelines.md's seas5_dual_source (MARS pre-2024 / AWS S3 2024+) transition
# --- source repo ---
source_repo: ocha-dap/ds-raster-explore
source_branch: main
source_sha: f13a0d6
code_ref:
  - "README.md — setup (venv + .env with PROD_BLOB_SAS/DEV_BLOB_SAS)"
  - "R/utils.R — load_proj_contatiners()/azure_endpoint_url() Azure blob container helpers (AzureStor, dev SAS)"
  - "notebooks/era5-zarr.ipynb — GCP ARCO-ERA5 Zarr vs. Microsoft Planetary Computer STAC+Zarr ERA5 access patterns"
  - "notebooks/imerg-zarr.ipynb — IMERG Zarr backend: full-store open cost vs. post-clip compute cost (Haiti AOI)"
  - "notebooks/imerg-cogs.ipynb — IMERG per-date COG backend: per-file loop+clip cost vs. post-concat compute cost (Haiti AOI)"
  - "notebooks/mars_processed_em_vs_aws.qmd — SEAS5 ensemble-mean COG CRS-alignment check, MARS-derived vs. WIP AWS-NRT-derived"
depends_on: []                 # reads external public cloud stores (GCP, Planetary Computer) and ad-hoc/frozen dev-blob extracts, not a KB-tracked pipeline's live output
discrepancies:
  - "[gap] era5-zarr.ipynb draws no written conclusion — it only prints the two dataset structures (GCP native-grid Zarr vs. Planetary Computer regular-grid Zarr) side by side; any preference is unrecorded."
  - "[stale] imerg-zarr.ipynb and imerg-cogs.ipynb read frozen extracts (2000-2005 Zarr; 2003-2008 COGs) from the `imb0chd0dev` storage account (`global/imerg.zarr`, `global/imerg/v6/`) — a different layout than the current production path (`raster/imerg/daily/{late|early}/v7/...`) written by pipelines/raster-pipelines.md. Nothing refreshes these extracts."
  - "[gap] mars_processed_em_vs_aws.qmd compares different calendar months (AWS-derived July 2024 vs. MARS-derived July 2000) because of MARS's long publishing delay, not a true same-date comparison — flagged as a caveat in the doc itself, not a hidden gap."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Raster storage exploration — analysis

> **Analysis, not a framework.** No published framework doc, no trigger logic, no country/hazard scope — this is a technical infra spike comparing raster storage backends, captured so the reasoning behind current raster-pipeline design choices is findable.

## What it is

Four self-contained sample notebooks (3 Jupyter, 1 Quarto `.qmd`) exploring how to store and query large, multi-dimensional gridded climate datasets (ERA5, IMERG, SEAS5) in the cloud, and comparing storage backends: cloud-hosted Zarr stores (both external, e.g. Google's ARCO-ERA5 and Microsoft Planetary Computer, and the team's own Azure-blob Zarr) vs. collections of individual Cloud-Optimized GeoTIFFs (COGs). It is not a country or hazard analysis — it is infrastructure R&D, done ahead of / alongside building the team's production raster ingestion pipeline (`ds-raster-pipelines`, now [raster-pipelines](../pipelines/raster-pipelines.md)), which settled on the COG-per-timestep approach these notebooks help validate.

## What was analyzed / findings

- **`era5-zarr.ipynb`** — compares two externally-hosted, analysis-ready ERA5 Zarr sources: (1) Google Cloud's ARCO-ERA5, a 31TB store on the native reduced Gaussian grid (`values` dim, not lat/lon); (2) Microsoft Planetary Computer's `era5-pds` STAC collection, a regular lat/lon grid (0.25°) queried per-month via `pystac_client` + `planetary_computer` signing, returning ~28GB/month datasets. The notebook only opens and prints each dataset's structure and plots one variable (`sea_surface_temperature`) — it draws no written conclusion about which is preferable.
- **`imerg-zarr.ipynb`** — opens the team's own IMERG Zarr store on the dev blob (`az://global/imerg.zarr`, 2000-06-01 to 2005-12-22, 2033 daily obs, 52.7GB, 0.1° global). Opening the full store's metadata takes an unexpectedly long **3-5 min** (candidate causes noted but not conclusively tested: too many chunks — rechunking to 160 chunks didn't help — Dask overhead, network speed, or an `adlfs` mapper issue). Clipping to a Haiti bounding box (using a CODAB shapefile pulled from `ds-aa-hti-hurricanes/raw/codab/hti.shp.zip` on blob) reduces the working set to ~5MB; `.compute()` on the clipped box then takes ~40s-1min, and downstream time-mean/plot operations are all <2s.
- **`imerg-cogs.ipynb`** — same IMERG data and same Haiti AOI, but sourced from individually-stored COGs (`global/imerg/v6/*.tif` on the dev blob) instead of Zarr, filtered to 2003-06-01 to 2008-12-31 (2041 files, a comparable volume to the Zarr example's 2033). Looping over each COG with `rioxarray.open_rasterio`, clipping to the Haiti bbox, and `persist()`-ing before `xr.concat`-ing along a `date` dim takes **5-8 min** for all 2041 files — slower up front than the Zarr store's single 3-5 min open, but the AOI clip happens inline per-file, so once concatenated, computing the time-mean and plotting are again <2s. Net effect: COGs front-load the clip cost per file; Zarr front-loads a single (slow) store-open then a bulk clip — the notebooks show, but don't state, this trade-off explicitly.
- **`mars_processed_em_vs_aws.qmd`** — compares SEAS5 seasonal-forecast ensemble-mean COGs from two sources: the long-standing ad-hoc MARS-catalogue pipeline (previously run per-project for Dry Corridor, Afghanistan, Ethiopia) vs. the then-WIP global AWS-NRT GRIB→COG pipeline (ECMWF pushing 0.4° NRT seasonal forecast gribs to the team's AWS bucket since 2024). Stacking a MARS-derived band with an AWS-derived band throws a `[rast] CRS do not match` warning, but pixel-centroid plotting (cropped to Nicaragua for legibility) shows the two grids are in fact spatially aligned. Root cause, confirmed via reprojection experiments: the AWS-derived COG's CRS is auto-imported from the raw GRIB and comes out mis-registered even though the underlying coordinates are correct WGS84 — reprojecting it (rather than just overwriting/setting its CRS) actively breaks the alignment. **Conclusion (stated in-repo):** MARS-derived and AWS-derived COGs are geometrically compatible once the AWS COG's CRS is explicitly *set* (not reprojected) — the same post-processing step MARS-derived COGs already apply. The doc recommends the new AWS NRT Global GRIB→COG pipeline adopt this same explicit CRS-setting step.

## Relation to frameworks

Standalone technical exploration, not tied to a specific AA framework. It functionally pre-figures and validates design choices later productionized in [raster-pipelines](../pipelines/raster-pipelines.md) — the Databricks-scheduled ERA5/SEAS5/IMERG/FloodScan → COG pipeline that is the team's current raster ingestion backbone. In particular, the MARS-vs-AWS CRS finding here maps directly onto that pipeline's documented `seas5_dual_source` split (MARS API pre-2024, private ECMWF AWS S3 2024+, different GRIB structure/filename convention) — this notebook is the evidence that the two sources' outputs are spatially compatible once CRS handling is aligned. Haiti (via `ds-aa-hti-hurricanes`'s CODAB) and Nicaragua appear only as convenient bounding-box/crop test fixtures for timing and CRS checks, not as the analytical subject — neither the [hti-hurricanes](../frameworks/hti-hurricanes/README.md) framework nor any Nicaragua-specific work is otherwise engaged by this repo.

## Sources & status

Repo: `ocha-dap/ds-raster-explore` (`main`, `f13a0d6`) — four notebooks, an R blob-access helper (`R/utils.R`), and a `README.md` with setup instructions (Python venv + `.env` holding `PROD_BLOB_SAS`/`DEV_BLOB_SAS`). No `.github/workflows/`, no scheduled job, no deployment, no persisted output beyond the notebooks' own cell state and inline plots — this is analyst scratch work, not a pipeline. All four notebooks are complete (none are empty stubs), but each is a single narrow, one-off comparison run against either external public cloud stores (GCP, Planetary Computer — live, not frozen) or frozen dev-blob extracts (IMERG: 2000-2008; SEAS5: a single MARS month vs. a single AWS month, both from 2024/2000 respectively). Nothing refreshes the frozen extracts. Status is **dormant**: no evidence of activity beyond the initial exploration, and the lessons it captures (COG-per-timestep over Zarr for the team's raster store; explicit CRS-setting for AWS-derived SEAS5 COGs) are now embodied in the live [raster-pipelines](../pipelines/raster-pipelines.md) production pipeline rather than in this repo.
