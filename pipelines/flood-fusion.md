---
content_type: pipeline
name: flood-fusion
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "[dev adm_zarno1] Flood Fusion Daily", ref: "718536903707906", schedule: "0 0 7 * * ? UTC (PAUSED until the prod deploy)", status: paused }   # DAB dev target; prod target pulls main after the ds-flood-gfm PR merges
    - { name: "[dev adm_zarno1] Flood Fusion Static Build", ref: "186374068781759", schedule: on-demand, status: live }
inputs:
  - "GFM STAC https://stac.eodc.eu/api/v1 collection GFM (ensemble_flood_extent, exclusion_mask, advisory_flags; 80 m overview)"
  - "blob prod raster/floodscan/daily/v5/processed/aer_area_300s_v{date}_v05r01.tif (Africa SFED, current)"
  - "blob dev raster/floodscan/daily/v5/raw/aer_sfed_area_300s_19980112_20260331_v05r01_{aa,na,sa}_no_ndt.nc (Asia-Australia, Americas, to 2026-03-31)"
  - "GDACS GFDS https://www.gdacs.org/flooddetection/DATA/ALL/SignalTiffs/ (daily signal; feed ended 2026-09-14)"
  - "NOAA VIIRS flood maps s3://noaa-jpss/JPSS_Blended_Products/VFM_1day_GLB/TIF/ (v2r0)"
  - "GLO-30 HAND (s3://glo-30-hand), ESA WorldCover 2021 v200, JRC GSW v1.4 occurrence, ERA5-Land monthly snow cover (CDS)"
  - "blob dev global/copernicus_ems/flood/gold/ and global/unosat/gold/ (gold labels for training/validation)"
outputs:
  - "blob dev projects/ds-flood-gfm/processed/flood_fusion_v1/daily/{window}/{window}_{YYYY-MM-DD}.tif (COG: p_flood, abs_logodds, n_sources_observed, days_since_obs)"
  - "blob dev projects/ds-flood-gfm/processed/flood_fusion_v1/{static,static_cache,state,runs,cubes,results}/ + MANIFEST.json"
  - "blob dev projects/ds-flood-gfm/raw/{era5_land,gfds,hydrobasins,koppen,natural_earth,tile_index}/"
surfaces: []
dependencies:
  - ocha-stratus
  - pystac-client
  - rasterio
  - xarray
depends_on:
  - flood-gfm
  - floodscan-ingest
  - cems-flood-archive
  - dbx-job-compute
source_repo: ocha-dap/ds-flood-gfm
source_branch: feat/flood-fusion-v1
source_sha: 5ceab0b
code_ref:
  - src/ds_flood_gfm/fusion/
  - scripts/fusion/
  - configs/fusion.yaml
  - databricks.yml
extra:
  licence_note: "FloodScan (AER) is an input: derived outputs are internal until AER approves sharing."
visibility: internal
last_synced: "2026-10-12"
---

# Flood fusion (daily P(flooded), 0.01°)

> Runbook: what feeds it, what it emits, and what to do when it breaks.

## One-liner

daily: GFM (SAR) + FloodScan|GFDS (microwave) + VIIRS (optical) → per-stratum naive Bayes in log-odds with 0.9 carry-over → P(flooded), |log-odds| + sources observed, days since observation on a 0.01° grid over the floodable domain → COGs on dev blob.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Flood Fusion Daily (`scripts/fusion/daily_job.py`) | `718536903707906` | 07:00 UTC for UTC yesterday | dev target only, schedule paused; the prod target (pulls `main`) is deployed after the repo PR merges |
| Flood Fusion Static Build (`scripts/fusion/static_build.py --bbox`) | `186374068781759` | on demand | extends daily coverage tile by tile |

v1 scope: AOIs in `configs/fusion.yaml` (`operational.aois`: Nigeria Niger–Benue, Chad Logone–Chari) plus every held-out validation event window. Global coverage needs the static build over all land tiles (about 15,000), which has not been run.

## Inputs

See frontmatter. Model tables (`results/accuracy_table.csv`, `results/prior_v1.csv`) ship in the repo and are copied by `databricks/run_task.py`.

## Steps

Per 1° tile, per day:
1. Pull yesterday's state and the static cache from blob.
2. GFM scenes of the day: 80 m overview binned into 0.01° cells, flood if ≥ 30% of observed pixels are flood. `exclusion_mask` and `advisory_flags` 1/3 → NoData.
3. FloodScan SFED ≥ 0.30, OR GFDS R1 fraction ≥ 0.30 → microwave vote.
4. VIIRS codes → flood fraction ≥ 0.30. Cloud, snow and shadow → NoData.
5. Log-odds update by stratum (land cover × snow season).
6. Write the COG and state, and push both to blob.

## Outputs

See frontmatter. The dataset card is `processed/flood_fusion_v1/MANIFEST.json`.

## Dependencies

ocha-stratus (`DSCI_AZ_BLOB_*` via Job Compute policy); no other secrets. CDS key only for re-fetching the snow climatology (already on blob raw).

## Failure modes & debugging

- **GFDS returns HTTP 403 for missing days.** The feed stopped after 2026-09-14. The job records GFDS absence in `runs/{date}.json`, and the microwave vote is then FloodScan alone where FloodScan covers. If even the known-good file 403s, the job raises: we are blocked, not absent.
- **FloodScan outside Africa ends 2026-03-31** (dev raw NetCDFs). Those regions have no microwave vote after that date until the global FloodScan merge on prod is populated.
- **No state for yesterday.** The job raises unless `--cold-start` is passed (first run, or after a gap).
- **GFM STAC returns out-of-bbox items** (filtered). An asset file that 404s drops that scene (recorded). A missing advisory layer is read without the flag (recorded).
- **Logs:** Databricks run output. Locally, `data/fusion/logs/`.

## Validation summary (v1, 49 held-out gold events)

The full write-up is `docs/final_report.md` in the repo. Held-out CSI across all strata: fusion 0.285, VIIRS 0.319, microwave 0.280, GFM 0.184.

The product does **not** beat the best single source in any stratum, and its probabilities are strongly over-confident (reliability slope about 0.01). A per-stratum recalibration fitted on training events fixes calibration in open/no-snow (slope 0.87), where fusion then beats every single source (CSI 0.37 vs 0.33).

## Downstream consumers

None yet (v1). Candidate: flood monitoring for the Nigeria and Chad frameworks.

<!-- TODO: dataset page — the KB has no registry for team-produced datasets; this page plus MANIFEST.json is the registration for now. -->
