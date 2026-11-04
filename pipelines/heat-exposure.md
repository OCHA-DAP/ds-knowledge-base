---
content_type: pipeline
name: heat-exposure
type: exposure
status: live   # backfill running 2026-11-04; daily refresh enabled after the first deploy
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Heat exposure — ERA5 backfill and build", ref: "48618764487730", schedule: "on-demand (databricks.yml heat_exposure_backfill: era5_backfill -> build_all)", status: live }
    - { name: "Refresh data and deploy site", ref: ".github/workflows/refresh-deploy.yml", schedule: "daily 09:40 UTC (schedule commented out until the backfill is done) + push to site/** + workflow_dispatch", status: paused }
inputs:
  - "CDS derived-era5-single-levels-daily-statistics: 2m temperature daily max / min / mean, 2m dewpoint daily mean; 1-hourly input, UTC days, 0.25°, area 75N-60S; 1986-present"
  - "CDS reanalysis-era5-single-levels (land-sea mask) and reanalysis-era5-single-levels-monthly-means (surface pressure 2015-2024)"
  - "CDS multi-origin-c3s-atlas (Copernicus Interactive Climate Atlas): CMIP6 monthly Tmax/Tmin/Tmean/specific humidity (historical + SSP5-8.5), CMIP6 ISIMIP-adjusted hot-day counts (TX35, TX40), ERA5 monthly hot-day counts and mean temperature"
  - "IPCC AR6 Atlas warming-level table (SantanderMetGroup/ATLAS warming-levels/CMIP6_Atlas_WarmingLevels.csv)"
  - "Indicators of Global Climate Change (ClimateIndicator/data, anthropogenic warming headlines) - current warming level"
  - "WorldPop R2025A 2026 1 km constrained global mosaics: total + age bands"
  - "HNRP mirror public export (ocha-dap.github.io/ds-hnrp-mirror/data/: plans.json, pin/, needs/) - people in need"
  - "COD-AB via ocha-stratus (HDX cloud mirror; FieldMaps admin 0 fallback)"
outputs:
  - "SHARED (dev raster container): era5/daily/raw/{variable}_{statistic}/era5_daily_{variable}_{statistic}_{YYYY}.nc - untouched CDS NetCDF per year; current year overwritten monthly"
  - "SHARED (dev raster container): era5/static/raw/era5_land_sea_mask.nc; era5/monthly/raw/era5_surface_pressure_monthly_2015-2024.nc"
  - "SHARED (dev raster container): c3s_atlas/raw/{origin}_{variable}_{experiment}_{bias_adjustment}_75N-60S.zip - untouched C3S Atlas downloads"
  - "SHARED (dev raster container): worldpop/age_structures/global_t_{AA}_2026_CN_1km_R2025A_UA_v1.tif (0-1 yr and 65..90+ bands)"
  - "dev projects container ds-heat-exposure/: era5c/ (compact land/populated-cell store), metrics/, pop/, tables/, state/ (CDS job ids)"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-heat-exposure/", kind: landing, title: "Extreme heat and people in need"}
  - {url: "https://ocha-dap.github.io/ds-heat-exposure/dashboard/", kind: dashboard, title: "Extreme heat and people in need (password-protected while under review)"}
dependencies:
  - "ocha-stratus (blob, COD-AB)"
  - "ecmwf-datastores-client (CDS jobs); repo secret CDSAPI_KEY; CDS URL set in code"
  - "org secrets DSCI_AZ_BLOB_DEV_SAS / DSCI_AZ_BLOB_DEV_SAS_WRITE; repo secret PAGE_PASSWORD"
downstream: []
depends_on: [hnrp-mirror, worldpop]
source_repo: OCHA-DAP/ds-heat-exposure
source_branch: main
source_sha:
code_ref:
  - "src/heat/shared.py - shared blob paths (the team-reusable copies)"
  - "scripts/fetch_era5.py, scripts/fetch_atlas.py - CDS submit/collect, resumable"
  - "src/heat/metrics.py, src/heat/thermo.py - heat metrics, wet-bulb temperature"
  - "docs/DESIGN.md - method and decisions"
extra:
  report: "Extreme heat: Preparing for the heatwaves of the future (OCHA, IFRC, Climate Centre, Oct 2022; written by Greg Puley)"
visibility: public
last_synced: "2026-11-04"
---

# Heat exposure of people in need

## One-liner
Daily (once enabled): pull this year's ERA5 daily temperature and humidity from CDS → count dangerous-heat
days per 0.25° cell → weight by WorldPop and by people in need in the current GHO country plans →
encrypted Pages dashboard. A live update of the 2022 OCHA–IFRC *Extreme heat* report.

## Reusable data this pipeline puts on the shared blob

**Check here before downloading ERA5 daily temperature, C3S Atlas files or WorldPop age rasters.**
All copies are on the **dev** storage account, `raster` container, untouched as downloaded:

| what | path (raster container, dev) | coverage |
|---|---|---|
| ERA5 daily max 2 m temperature | `era5/daily/raw/2m_temperature_daily_maximum/era5_daily_2m_temperature_daily_maximum_{YYYY}.nc` | 1986–present, 0.25°, 75°N–60°S, UTC days from hourly data |
| ERA5 daily min 2 m temperature | `era5/daily/raw/2m_temperature_daily_minimum/…_{YYYY}.nc` | same |
| ERA5 daily mean 2 m dewpoint | `era5/daily/raw/2m_dewpoint_temperature_daily_mean/…_{YYYY}.nc` | same |
| ERA5 daily mean 2 m temperature | `era5/daily/raw/2m_temperature_daily_mean/…_{YYYY}.nc` | current year only (earlier years: C3S Atlas ERA5 monthly mean) |
| ERA5 land-sea mask | `era5/static/raw/era5_land_sea_mask.nc` | 0.25°, 75°N–60°S |
| ERA5 monthly surface pressure 2015–2024 | `era5/monthly/raw/era5_surface_pressure_monthly_2015-2024.nc` | 0.25°, 75°N–60°S |
| C3S Atlas CMIP6 / ERA5 monthly | `c3s_atlas/raw/{origin}_{variable}_{experiment}_{bias_adjustment}_75N-60S.zip` | CMIP6 1°, historical 1850–2014 + SSP5-8.5 2015–2100, ~20–24 models; ERA5 0.25° 1940–2025 |
| WorldPop 2026 age bands | `worldpop/age_structures/global_t_{00,65,70,75,80,85,90}_2026_CN_1km_R2025A_UA_v1.tif` | 1 km global (next to `worldpop/pop_count/`) |

- The ERA5 files are one NetCDF per variable-year (~1 GB, float32, `valid_time` × latitude × longitude).
  The **current year is overwritten** each month as new months complete (ERA5 runs ~6 days behind).
- Each blob carries metadata `producer` and `source` (the exact CDS request), so you can see the
  statistic, frequency and area without opening it.
- Atlas zips hold several NetCDFs split along time; open them together
  (`heat.projections.open_atlas` in the repo does this lazily).
- The WorldPop total for 2026 already on blob (`worldpop/pop_count/…`, deflate) is identical in values to
  WorldPop's LZW download (checked 2026-11-04).
- Prod copies don't exist (prod writes run on Databricks); copy with a DBX job if a prod pipeline needs them.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Heat exposure — ERA5 backfill and build | Databricks job `48618764487730` (`databricks.yml` → `heat_exposure_backfill`: `era5_backfill` on E4ads_v5, then `build_all` on E8ads_v5) | on-demand; first run started 2026-11-04 (days: sequential CDS requests) | running |
| Refresh data and deploy site | `.github/workflows/refresh-deploy.yml` | daily 09:40 UTC (commented out until the backfill is done) | paused |

**Copernicus requests go one or two at a time.** ECMWF's data-store service protection measures (Oct 2026)
ask for sequential submission and may suspend accounts that submit large batches; a 124-request batch on
2026-11-04 sat unstarted for 3 hours and drew a 429. The Databricks job uses the team `CDSAPI_KEY` from the
Job Compute policy, keeps at most 2 requests open, and saves state + compacted years on the project blob so a
retry resumes.

## Steps
1. `backfill_sequential.py` (via `fetch_era5.py`): CDS requests one variable-year at a time (≤ 2 in flight;
   job ids in `state/era5_jobs.json` on blob), download, copy untouched to the shared container, compact to
   land/populated cells (int16). A year already in the shared container is taken from there instead of CDS.
2. `build_observed.py`: 1986–2005 95th percentiles (Lancet heatwave definition), per-year day counts per cell:
   Tmax > 35 / 40 °C, WBGT (shade) ≥ 30 / 32 °C, wet-bulb ≥ 29 / 31 °C, heatwave days, yearly mean temperature.
3. `build_projections.py`: CMIP6 monthly changes at 1.5 / 2 / 3 °C (C3S Atlas, IPCC warming-level windows,
   SSP5-8.5, model median) added to ERA5 1995–2014 days, recounted.
4. `build_population.py`: WorldPop 2026 on the ERA5 grid; PiN units (HNRP mirror admin PiN rescaled to the
   official national figure) matched to COD-AB; population per unit × cell.
5. `build_tables.py` → exposure tables; `build_site.py --encrypt` → Pages artifact.

## Failure modes & debugging
- **CDS queue**: derived ERA5 daily statistics can sit in "accepted" for hours. Nothing is lost: rerun the
  Databricks job (it resumes from blob state). Never raise the in-flight limit to speed it up.
- **`CDSAPI_URL` on team machines points at EWDS** (flood data); the code sets the CDS URL itself and uses
  `CDSAPI_KEY` only (the key is the same across the Copernicus stores).
- **Licence**: the CDS CMIP6 heat-stress indicators (`sis-extreme-indices-cmip6`, CICERO licence:
  non-commercial research only, results to be submitted for open publication) are deliberately **not** used.
- **p-codes**: COD JIAF health zones match COD-AB admin 3 by name within the parent only; MLI "PDI land"
  (IDPs with no location) is spread over the whole country.

## Downstream consumers
The dashboard only, so far. The shared ERA5 daily / Atlas / WorldPop-age copies above are meant for reuse.
