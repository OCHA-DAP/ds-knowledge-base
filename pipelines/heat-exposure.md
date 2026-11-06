---
content_type: pipeline
name: heat-exposure
type: exposure
status: live   # backfill + build done 2026-11-06 (ARCO-ERA5); site published (password-protected); daily refresh on
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Heat exposure — ERA5 backfill and build", ref: "48618764487730", schedule: "on-demand (databricks.yml heat_exposure_backfill: era5_backfill -> build_all; job parameter build_from)", status: live }
    - { name: "Refresh data and deploy site", ref: ".github/workflows/refresh-deploy.yml", schedule: "daily 09:40 UTC + push to site/** + workflow_dispatch", status: live }
inputs:
  - "ARCO-ERA5 hourly (Google Cloud public dataset gcp-public-data-arco-era5, ar/full_37-1h-0p25deg-chunk-1.zarr-v3; public, no login): 2m temperature and 2m dewpoint, reduced here to UTC-day max / min / mean (= CDS derived-era5-single-levels-daily-statistics); 0.25°, area 75N-60S; 1986-present"
  - "CDS reanalysis-era5-single-levels (land-sea mask) and reanalysis-era5-single-levels-monthly-means (surface pressure 2015-2024)"
  - "CDS multi-origin-c3s-atlas (Copernicus Interactive Climate Atlas): CMIP6 monthly Tmax/Tmin/Tmean/specific humidity (historical + SSP5-8.5), CMIP6 ISIMIP-adjusted hot-day counts (TX35, TX40), ERA5 monthly hot-day counts and mean temperature"
  - "IPCC AR6 Atlas warming-level table (SantanderMetGroup/ATLAS warming-levels/CMIP6_Atlas_WarmingLevels.csv)"
  - "Indicators of Global Climate Change (ClimateIndicator/data, anthropogenic warming headlines) - current warming level"
  - "WorldPop R2025A 2026 1 km constrained global mosaics: total + age bands"
  - "HNRP mirror public export (ocha-dap.github.io/ds-hnrp-mirror/data/: plans.json, pin/, needs/) - people in need"
  - "COD-AB via ocha-stratus (HDX cloud mirror; FieldMaps admin 0 fallback)"
outputs:
  - "SHARED (dev raster container): era5/daily/processed/{variable}_{statistic}/era5_daily_{variable}_{statistic}_{YYYY}.nc - ERA5 UTC daily statistics computed from ARCO-ERA5 hourly, one NetCDF per year in the CDS daily-statistics layout; current year overwritten monthly"
  - "SHARED (dev raster container): era5/static/raw/era5_land_sea_mask.nc; era5/monthly/raw/era5_surface_pressure_monthly_2015-2024.nc"
  - "SHARED (dev raster container): c3s_atlas/raw/{origin}_{variable}_{experiment}_{bias_adjustment}_75N-60S.zip - untouched C3S Atlas downloads"
  - "SHARED (dev raster container): worldpop/age_structures/global_t_{AA}_2026_CN_1km_R2025A_UA_v1.tif (0-1 yr and 65..90+ bands)"
  - "dev projects container ds-heat-exposure/: era5c/ (compact land/populated-cell store), metrics/, pop/, tables/, state/ (plan fingerprint, CDS job ids of the one-off downloads)"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-heat-exposure/", kind: landing, title: "Extreme heat and people in need"}
  - {url: "https://ocha-dap.github.io/ds-heat-exposure/dashboard/", kind: dashboard, title: "Extreme heat and people in need (password-protected while under review)"}
dependencies:
  - "ocha-stratus (blob, COD-AB)"
  - "zarr + aiohttp (ARCO-ERA5 reads; no credentials)"
  - "ecmwf-datastores-client (one-off CDS downloads: C3S Atlas, ERA5 static fields; CDSAPI_KEY, CDS URL set in code)"
  - "org secrets DSCI_AZ_BLOB_DEV_SAS / DSCI_AZ_BLOB_DEV_SAS_WRITE; repo secret PAGE_PASSWORD"
downstream: []
depends_on: [hnrp-mirror, worldpop]
source_repo: OCHA-DAP/ds-heat-exposure
source_branch: main
source_sha:
code_ref:
  - "src/heat/shared.py - shared blob paths (the team-reusable copies)"
  - "src/heat/arco.py, scripts/fetch_arco.py - ERA5 daily statistics from ARCO-ERA5 hourly (backfill, monthly current year)"
  - "scripts/fetch_era5.py, scripts/fetch_atlas.py - one-off CDS downloads (static fields, Atlas), resumable"
  - "src/heat/metrics.py, src/heat/thermo.py - heat metrics, wet-bulb temperature"
  - "docs/DESIGN.md - method and decisions"
extra:
  report: "Extreme heat: Preparing for the heatwaves of the future (OCHA, IFRC, Climate Centre, Oct 2022; written by Greg Puley)"
visibility: public
last_synced: "2026-11-06"
---

# Heat exposure of people in need

## One-liner
Daily: compute this year's ERA5 daily temperature and humidity from ARCO-ERA5 → count dangerous-heat
days per 0.25° cell → weight by WorldPop and by people in need in the current GHO country plans →
encrypted Pages dashboard. A live update of the 2022 OCHA–IFRC *Extreme heat* report.

## Reusable data this pipeline puts on the shared blob

**Check here before downloading ERA5 daily temperature, C3S Atlas files or WorldPop age rasters.**
All copies are on the **dev** storage account, `raster` container. The ERA5 daily files are computed here
from ARCO-ERA5 hourly data; everything else is untouched as downloaded:

| what | path (raster container, dev) | coverage |
|---|---|---|
| ERA5 daily max 2 m temperature | `era5/daily/processed/2m_temperature_daily_maximum/era5_daily_2m_temperature_daily_maximum_{YYYY}.nc` | 1986–present, 0.25°, 75°N–60°S, UTC days (00–23 UTC) from hourly data |
| ERA5 daily min 2 m temperature | `era5/daily/processed/2m_temperature_daily_minimum/…_{YYYY}.nc` | same |
| ERA5 daily mean 2 m temperature | `era5/daily/processed/2m_temperature_daily_mean/…_{YYYY}.nc` | same |
| ERA5 daily mean 2 m dewpoint | `era5/daily/processed/2m_dewpoint_temperature_daily_mean/…_{YYYY}.nc` | same |
| ERA5 land-sea mask | `era5/static/raw/era5_land_sea_mask.nc` | 0.25°, 75°N–60°S |
| ERA5 monthly surface pressure 2015–2024 | `era5/monthly/raw/era5_surface_pressure_monthly_2015-2024.nc` | 0.25°, 75°N–60°S |
| C3S Atlas CMIP6 / ERA5 monthly | `c3s_atlas/raw/{origin}_{variable}_{experiment}_{bias_adjustment}_75N-60S.zip` | CMIP6 1°, historical 1850–2014 + SSP5-8.5 2015–2100, ~20–24 models; ERA5 0.25° 1940–2025 |
| WorldPop 2026 age bands | `worldpop/age_structures/global_t_{00,65,70,75,80,85,90}_2026_CN_1km_R2025A_UA_v1.tif` | 1 km global (next to `worldpop/pop_count/`) |

- The ERA5 daily files are one NetCDF per variable-year (~0.6 GB, float32 K, `valid_time` × latitude ×
  longitude, variable `t2m` / `d2m`), in the same grid and layout as the CDS
  `derived-era5-single-levels-daily-statistics` downloads (checked: the 1986 daily maxima match the CDS
  product to within 0.001 °C on every day and cell). The **current year is overwritten** each month as new months
  complete (ERA5T runs ~6 days behind).
- **Need ERA5 hourly or another variable?** Read ARCO-ERA5 directly instead of queueing CDS requests: see
  [ERA5: where to get it](../infrastructure/datasets/era5.md) (recipe, speed, latency, licence).
- Each blob carries metadata `producer` and `source` (for downloads, the exact CDS request), so you can see
  where it came from without opening it.
- `era5/daily/raw/2m_temperature_daily_maximum/…_1986.nc` is the one untouched CDS daily-statistics file
  from before the switch to ARCO-ERA5 (used for the check above).
- Atlas zips hold several NetCDFs split along time; open them together
  (`heat.projections.open_atlas` in the repo does this lazily).
- The WorldPop total for 2026 already on blob (`worldpop/pop_count/…`, deflate) is identical in values to
  WorldPop's LZW download (checked 2026-11-04).
- Prod copies don't exist (prod writes run on Databricks); copy with a DBX job if a prod pipeline needs them.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Heat exposure — ERA5 backfill and build | Databricks job `48618764487730` (`databricks.yml` → `heat_exposure_backfill`: `era5_backfill` then `build_all`, both on E8ads_v5) | on-demand; ARCO-ERA5 backfill (~1.4 TB read, 1 h 40 min) then the build (~2 h 30 min) | done 2026-11-06 (run 750501654300250) |
| Refresh data and deploy site | `.github/workflows/refresh-deploy.yml` | daily 09:40 UTC (enabled 2026-11-06); re-reads this year's ERA5 only when ARCO-ERA5 has a new complete month, rebuilds PiN weights only when the plans change | live |

**Rerunning the build from a later step.** `build_all` saves each step's outputs to the project blob as it
finishes. After a failure, repair the run with job parameter `build_from` set to the failed step (`p95`,
`years`, `deltas`, `shift`, `check`, `tables`), e.g.
`databricks jobs repair-run --json '{"run_id": <run>, "latest_repair_id": <id>, "rerun_tasks": ["build_all"], "job_parameters": {"build_from": "deltas"}}'`.
Databricks refuses `python_params` on a job with job parameters.

**Why ARCO-ERA5 and not the CDS for the daily data.** ECMWF's data-store service protection measures
(Oct 2026) ask for sequential submission and may suspend accounts that submit large batches (a 124-request
batch on 2026-11-04 sat unstarted for 3 hours and drew a 429). Submitting one or two at a time, the CDS queue
then held single `derived-era5-single-levels-daily-statistics` requests 8–20 hours: one variable-year a day,
weeks for the backfill. ARCO-ERA5 has the same hourly data with no queue. The remaining CDS downloads (Atlas,
static fields) are one-off and still go at most two at a time; the key is shared with the team's flood
monitoring.

## Steps
1. `fetch_arco.py backfill`: for each year, read the 24 hourly 2 m temperature and dewpoint fields of every
   UTC day from ARCO-ERA5 (days in parallel), reduce to daily max / min / mean, write the full-grid files to
   the shared container and the land/populated-cell store (int16) to the project blob. A year already on blob
   is skipped, so a retry resumes. `fetch_arco.py current` (daily refresh) rebuilds the current year once a new
   month is complete.
2. `build_observed.py`: 1986–2005 95th percentiles (Lancet heatwave definition), per-year day counts per cell:
   Tmax > 35 / 40 °C, WBGT (shade) ≥ 30 / 32 °C, wet-bulb ≥ 29 / 31 °C, heatwave days, yearly mean temperature.
3. `build_projections.py`: CMIP6 monthly changes at 1.5 / 2 / 3 °C (C3S Atlas, IPCC warming-level windows,
   SSP5-8.5, model median) added to ERA5 1995–2014 days, recounted.
4. `build_population.py`: WorldPop 2026 on the ERA5 grid; PiN units (HNRP mirror admin PiN rescaled to the
   official national figure) matched to COD-AB; population per unit × cell.
5. `build_tables.py` → exposure tables; `build_site.py --encrypt` → Pages artifact.

## Validation (2026-11-06)
- **ERA5 daily from ARCO vs the CDS product:** 1986 daily maxima identical to within 0.001 °C, every day and cell.
- **Lancet Countdown** (over-65s and infants, 3.7 billion more heatwave person-days in 2020 than 1986–2005):
  5.5 billion here, with 2026 population held fixed (more over-65s than in 2020). Within the 2× target.
- **Lenton et al. 2023** (~60 million people where the yearly mean is ≥ 29 °C): 173 million here for
  2016–2025 at 2026 population. Lenton uses 2010 population and 2000–2020 climate; like for like (2006–2015,
  Sahel populations scaled back to 2010) it is ~70 million. Very threshold-sensitive: ±0.5 °C halves or
  doubles the count, and single years swing 108–282 million, so quote a 10-year mean.
- **Shift method vs the Atlas ISIMIP bias-adjusted hot-day counts** (change from 1995–2014, population-weighted):
  days over 40 °C agree within 10% at 1.5 / 2 / 3 °C; days over 35 °C come out 10 / 19 / 24% lower, so the
  projections probably understate that measure. Cause not established (not tail widening: TX40 agrees).

## Failure modes & debugging
- **ARCO-ERA5 read errors** are retried per day (5 tries); a day past the end of the record raises
  ("missing values"), which means `valid_time_stop_era5t` in the store's attributes moved backwards. Rerun
  the Databricks job: finished years are skipped.
- **Blob sync** stamps files with the blob's last-modified time: our netCDF outputs keep the same byte size
  when their values change, so a size-only comparison silently skipped re-uploads (fixed 2026-11-06).
- **netCDF says "Permission denied" when the output folder does not exist** (first build on a fresh cluster).
- **`CDSAPI_URL` on team machines points at EWDS** (flood data); the code sets the CDS URL itself and uses
  `CDSAPI_KEY` only (the key is the same across the Copernicus stores).
- **Licence**: the CDS CMIP6 heat-stress indicators (`sis-extreme-indices-cmip6`, CICERO licence:
  non-commercial research only, results to be submitted for open publication) are deliberately **not** used.
- **p-codes**: COD JIAF health zones match COD-AB admin 3 by name within the parent only; MLI "PDI land"
  (IDPs with no location) is spread over the whole country.

## Downstream consumers
The dashboard only, so far. The shared ERA5 daily / Atlas / WorldPop-age copies above are meant for reuse.
