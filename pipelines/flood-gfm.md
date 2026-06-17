---
content_type: pipeline
name: flood-gfm
type: exposure
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Get GFM Plots", ref: "127810131501319", schedule: manual, status: live }   # Databricks job_id (workspace adb-6009046713167663, profile default); deployments.md: schedule=manual, not PAUSED. No automated trigger — runs on manual click only.
inputs:
  - "GFM STAC API — https://stac.eodc.eu/api/v1, collection GFM (ensemble_flood_extent band)"
  - "blob projects/ghsl/pop/GHS_POP_E2025_GLOBE_R2023A_4326_3ss_V1_0.tif (container: raster)"
  - "blob projects/ds-flood-gfm/raw/codab/{iso3}/*.parquet (COD-AB admin boundaries; container: projects)"
  - "FieldMaps HTTP fallback — https://data.fieldmaps.io/edge-matched/humanitarian/intl/adm{N}_polygons.parquet"
  - "blob projects/ds-flood-gfm/raw/geom/songkhla_province_adm{N}.parquet (custom AOI)"
  - "blob projects/ds-flood-gfm/raw/geom/gaza_strip_adm{N}.parquet (custom AOI)"
outputs:
  - "blob projects/ds-flood-gfm/processed/polygon/{cache_key}.shp.zip (flood extent polygons with provenance)"
  - "blob projects/ds-flood-gfm/processed/provenance_raster/{cache_key}_provenance.tif (COG; container: projects, stage: dev)"
  - "local outputs/plots/{ISO3}_population_provenance_{YYYYMMDD}.png"
  - "local outputs/plots/{ISO3}_population_latest_adm3_{YYYYMMDD}.png"
  - "local outputs/plots/{ISO3}_population_cumulative_adm3_{YYYYMMDD}.png"
  - "local outputs/plots/{ISO3}_choropleth_flooded_area_latest_{YYYYMMDD}.png"
  - "local outputs/plots/{ISO3}_choropleth_flooded_area_cumulative_{YYYYMMDD}.png"
  - "local data/cache/{ISO3}_{cache_key}/ (flood_points.parquet + provenance.tif + metadata.json)"
dependencies:
  - ocha-stratus
  - pystac-client
  - stackstac
  - xarray
  - rioxarray
  - geopandas
  - exactextract
  - rasterio
  - matplotlib
  - adjusttext
  - scipy
downstream:
  - "flood_exposure.py marimo notebook in this repo (reads ds-flood-gfm/processed/polygon/ blobs)"
  - "Ad-hoc: analysts download PNG plot outputs for situation reports"
depends_on:
  - "infrastructure/datasets/ghsl"
  - "infrastructure/datasets/gfm-stac"
source_repo: ocha-dap/ds-flood-gfm
source_branch: arbitrary-admin
source_sha: 1b1ee56
code_ref:
  - scripts/04_generate_flood_polygons.py
  - scripts/02_generate_affected_population_choropleths.py
  - src/ds_flood_gfm/datasources/gfm.py
  - flood_exposure.py
extra:
  databricks_job_id: "127810131501319"
  databricks_job_note: "Databricks 'Get GFM Plots' job_id 127810131501319 (manual schedule, not PAUSED) listed in deployments.md — likely wraps scripts/02 or 04 on a cluster; full job config not committed to the repo, registry is source of truth."
  countries_supported: ["JAM", "HTI", "CUB", "PHL (tiled)", "arbitrary AOI via blob geoparquet"]
  flood_modes: ["latest", "cumulative"]
  population_scale_factor: 25
  stac_api: "https://stac.eodc.eu/api/v1"
  schema_strain: "outputs split between blob (polygon, provenance raster) and local (PNG plots); no scheduled job in repo — platform is effectively manual/on-demand"
visibility: internal
last_synced: "2026-06-17"
---

# GFM Flood Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On-demand: query GFM STAC API → build flood composite (latest or cumulative) → extract flood extent polygons + population exposure → upload to blob + generate PNG choropleths.*

## Jobs & schedule

**Platform: Databricks job (manual trigger).** There is no scheduled GHA workflow and no Databricks cron — the one registered job runs on a manual click. The repo itself has no `.github/workflows/`.

| job | ref | schedule | status |
|---|---|---|---|
| Get GFM Plots | `127810131501319` (Databricks job_id) | manual | live (not PAUSED) |

The Databricks job `127810131501319` (deployments.md → workspace `adb-6009046713167663`, profile `default`) is manual with no schedule. It is **not** PAUSED, but there is no automated trigger — it only runs when a human clicks Run. Full job config (which script/cluster it wraps) is not committed to the repo; the registry is the source of truth.

**Code entry points (not deployment-registry jobs — run locally / inside the Databricks job):**
- `scripts/02_generate_affected_population_choropleths.py` — affected-population choropleths (CLI)
- `scripts/03_generate_flooded_area_choropleths.py` — flooded-area choropleths (CLI; reads cache from script 02)
- `scripts/04_generate_flood_polygons.py` — flood polygon extraction + blob export (CLI)
- `scripts/01_download_codab_to_blob.py` — one-time COD-AB cache setup (CLI)
- `flood_exposure.py` — marimo notebook for interactive exposure recompute

## Inputs

- **GFM STAC API** (`https://stac.eodc.eu/api/v1`, collection `GFM`): queried with a bbox and 15-day backward (or forward) search window to find ensemble flood extent tiles. The STAC footprint is larger than the actual Sentinel tile — items are returned if the footprint *intersects* the AOI, but not all returned items contain flood data over the AOI (known gotcha).
- **GHSL 2025 population raster** (`ghsl/pop/GHS_POP_E2025_GLOBE_R2023A_4326_3ss_V1_0.tif`, container `raster`): 100m resolution; sampled at flood pixel locations and divided by 25 (pixel area ratio: 100m/20m² = 25) to estimate per-flood-pixel population.
- **COD-AB admin boundaries**: loaded from blob (`ds-flood-gfm/raw/codab/{iso3}/`) or via FieldMaps HTTP fallback. Script `01_download_codab_to_blob.py` is a one-time setup that caches them.
- **Custom AOI geoparquets** on blob (`ds-flood-gfm/raw/geom/`): e.g. Songkhla province, Gaza Strip — used via `--aoi-geom-blob` flag to process non-ISO3 areas.

Supported ISO3 codes in `country_config.py`: JAM, HTI, CUB. PHL and other large countries are handled via automatic spatial tiling (2° tiles by default).

## Steps

1. **STAC query** (`query_gfm_stac`): search GFM collection over country bbox, last 15 days (configurable via `--n-search`).
2. **Stack build** (`create_flood_composite`): load `ensemble_flood_extent` band via stackstac (chunksize=2048, rescale=False); create daily max composites; rechunk to `time:-1, y:4096, x:4096`.
3. **Compositing**:
   - *Latest mode*: forward-fill then take last time slice (pixels show their most recent observation).
   - *Cumulative mode*: vectorized `.any(dim='time')` union of all flood observations.
4. **Polygon extraction** (`raster_to_polygons`): `flood_array == 1` → `rasterio.features.shapes` with 8-connectivity.
5. **Provenance** (`create_provenance_raster`): lazy argmax on reversed time axis → 2D integer raster where each pixel's value = index of its last observation date.
6. **Population sampling** (script 02 only): `stratus.open_blob_cog` on GHSL raster; nearest-neighbour sample at each flood point; scale by ÷25 and `math.ceil`.
7. **Export**: `export_polygons` uploads `{cache_key}.shp.zip` to blob; provenance COG uploaded separately. PNG plots written locally to `outputs/plots/`.
8. **Marimo notebook** (`flood_exposure.py`): interactive UI for loading saved polygon blobs and recomputing population exposure with `exactextract`.

For large countries (PHL etc.), step 1–5 is tiled; provenance raster is computed full-country post-tile (it stays lazy until the final compute, so memory is manageable).

## Outputs

**Blob storage (persistent, shared):**
- `ds-flood-gfm/processed/polygon/{cache_key}.shp.zip` — flood extent polygons with provenance date attribute
- `ds-flood-gfm/processed/provenance_raster/{cache_key}_provenance.tif` — COG, int16, value = date index; GeoTIFF tags carry `date_mapping` JSON (uploaded to `projects` container, stage `dev`)

**Local (ephemeral, analyst's machine):**
- `outputs/plots/{ISO3}_population_provenance_{YYYYMMDD}.png` — density heatmap
- `outputs/plots/{ISO3}_population_latest_adm3_{YYYYMMDD}.png` — affected-pop choropleth, latest mode
- `outputs/plots/{ISO3}_population_cumulative_adm3_{YYYYMMDD}.png` — affected-pop choropleth, cumulative mode
- `outputs/plots/{ISO3}_choropleth_flooded_area_{latest|cumulative}_{YYYYMMDD}.png` — flooded area km² choropleths
- `data/cache/{ISO3}_{cache_key}/` — local cache: `flood_points.parquet`, `provenance.tif`, `metadata.json`

Cache key is computed from ISO3 + actual STAC observation dates (not query end-date) + population raster path + flood mode. This means the cache invalidates only when new satellite data arrives.

## Dependencies

| Library | Purpose |
|---|---|
| ocha-stratus | blob I/O (`open_blob_cog`, `load_parquet_from_blob`, `upload_shp_to_blob`, `upload_cog_to_blob`, `codab.load_codab_from_fieldmaps`) |
| pystac-client | STAC search |
| stackstac | xarray stack from STAC items |
| xarray / rioxarray | raster processing |
| exactextract | fast zonal stats (modal provenance per polygon) |
| rasterio | raster I/O, polygon extraction |
| geopandas / shapely | vector data |
| matplotlib / adjustText | map rendering, non-overlapping labels |
| scipy | Gaussian smoothing for density heatmaps |
| marimo | interactive notebook UI |

**Secrets/env:** Azure blob credentials (via `ocha-stratus` / `.env`). `PGSSLMODE=require` is not needed here — this pipeline reads/writes blob only, no DB.

## Failure modes & debugging

**STAC returns items but no flood data over AOI:**
The STAC footprint for a Sentinel tile is larger than the tile itself. A search result with 3 dates may only have actual flood pixels on 2 of them. Symptom: cache key is built with N dates, but the actual xarray stack has fewer non-null time steps. Fix: use `--n-latest` larger than expected, or inspect "All dates found" in logs.

**Out of memory (Cuba, PHL):**
Cuba requires ~16GB RAM. Philippines requires `--use-tiling` (auto-enabled). Reduce `--n-latest` to 2 if still failing. Chunks are 2048×2048 (or 4096×4096 after rechunk).

**Blob upload fails (provenance raster):**
`stratus.upload_cog_to_blob` is called with `container_name="projects"`, `stage="dev"`. Verify credentials and that the `projects` container is accessible. The polygon zip upload uses `stratus.upload_shp_to_blob` — same container.

**Script 03 fails with cache not found:**
Script 03 reads the cache written by script 02. Must run script 02 in BOTH `latest` AND `cumulative` modes before running 03. Cache path: `data/cache/{ISO3}_{mode}_{hash}/`.

**Choropleth all white:**
Population sampling failed silently (check for "WARNING: Could not sample population raster"). Or `vmin/vmax` collapsed if all values are 0. Check logs for "Total affected population."

**Admin boundaries not loading from blob:**
Run script 01 first to upload COD-AB for the target ISO3. Blob path: `projects/ds-flood-gfm/raw/codab/{iso3_lower}/`. Script falls back to FieldMaps HTTP (~91s vs ~2.5s from blob).

**Logs:** console only — no centralised logging. Run with `PYTHONUNBUFFERED=1` to see progress in real time.

## Downstream consumers

- `flood_exposure.py` (marimo notebook in this repo) reads `ds-flood-gfm/processed/polygon/` blobs to recompute population exposure interactively.
- Ad-hoc: analysts download PNG outputs for situation reports.

> [conflict→resolved] An earlier draft listed `ds-floodexposure-monitoring` (`chd-ds-floodexposure-monitoring` on Azure) as a possible downstream consumer. Checked [pipelines/floodexposure-monitoring](floodexposure-monitoring.md): that pipeline reads Floodscan SFED COGs + WorldPop, **not** any flood-gfm output. The two are unrelated flood-exposure systems (GFM = Sentinel-1 SAR flood extent on-demand; floodexposure-monitoring = daily Floodscan). Removed the false link.
