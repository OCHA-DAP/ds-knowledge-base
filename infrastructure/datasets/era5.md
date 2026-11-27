---
content_type: dataset
name: ERA5
aliases: [ERA5, era5, ERA5T, "ARCO-ERA5", "ERA5 daily statistics", "reanalysis-era5-single-levels"]
provider: "ECMWF / Copernicus Climate Change Service (C3S); analysis-ready copy by Google Research (ARCO-ERA5)"
data_type: climate-reanalysis
access: public
api: "ARCO-ERA5 zarr https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3  ·  CDS https://cds.climate.copernicus.eu (cdsapi / ecmwf-datastores-client)"
auth: "ARCO-ERA5: none. CDS: free account + API key (team key CDSAPI_KEY, shared)"
formats: [zarr, netcdf, grib]
resolution: "0.25° global, hourly, 1940 to ~1 week ago (ERA5T; final ERA5 ~2-4 months behind)"
update_cadence: "daily (ERA5T); final ERA5 replaces ERA5T months later"
license: "CC-BY-4.0 (Copernicus licence): cite the CDS catalogue DOI 10.24381/cds.f17050d7 and show Copernicus attribution; the ARCO copy carries the same terms"
code_ref: "OCHA-DAP/ds-heat-exposure src/heat/arco.py (ARCO-ERA5 hourly -> UTC daily max/min/mean, threaded, on Databricks)"
mirror: automated       # monthly precip (raster pipelines) and daily 2 m temperature/dewpoint (heat-exposure) on blob
mirror_priority: med
used_by:
  - pipelines/heat-exposure.md
  - pipelines/raster-pipelines.md
  - pipelines/glb-tropicalcyclones.md
last_verified: 2026-11-06
---

# ERA5: where to get it

ECMWF's global reanalysis: hourly weather on a 0.25° grid from 1940 to about a week ago. Three ways to get
it, in the order to try them.

## 1. Already on the team blob (dev, `raster` container)

| what | path | from | coverage |
|---|---|---|---|
| Monthly total precipitation | `era5/monthly/raw/` (GRIB), `era5/monthly/processed/` (COG) | [raster pipelines](../../pipelines/raster-pipelines.md) | 0.25°, 1981–present, monthly |
| Daily max / min / mean 2 m temperature, daily mean 2 m dewpoint | `era5/daily/processed/{variable}_{statistic}/era5_daily_{variable}_{statistic}_{YYYY}.nc` | [heat-exposure](../../pipelines/heat-exposure.md) | 0.25°, 75°N–60°S, UTC days, 1986–present, updated monthly |
| Land-sea mask; monthly surface pressure 2015–2024 | `era5/static/raw/era5_land_sea_mask.nc`, `era5/monthly/raw/era5_surface_pressure_monthly_2015-2024.nc` | heat-exposure | 0.25°, 75°N–60°S |

Read them with ocha-stratus (see the `blob-io` skill). The heat-exposure page has the file layout details.

## 2. Anything else: read ARCO-ERA5 directly (fast, no queue, no login)

Google's **ARCO-ERA5** ("analysis-ready, cloud-optimised") is the full ERA5 archive as a public zarr store on
Google Cloud: 273 variables (single levels and 37 pressure levels), hourly, 0.25°, 1940 to about a week ago.
It is the same data as the CDS: the daily maxima computed from it for all of 1986 match the CDS
`derived-era5-single-levels-daily-statistics` download to within 0.001 °C on every day and grid cell
(heat-exposure, 2026-11-05).

```python
import xarray as xr
ds = xr.open_zarr(
    "https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3",
    consolidated=True, chunks=None,
)
t2m = ds["2m_temperature"].sel(time=slice("2024-07-01T00", "2024-07-01T23"))  # 24 hourly global fields
daily_max = t2m.max("time")                                                    # one UTC day
```

- **How fast.** On a Databricks E8ads_v5 (16 threads) the heat-exposure backfill read 2 m temperature and
  dewpoint at about 3 days per second: one year of four daily statistics in ~2½ minutes, 1986–2026 in
  1 h 40 min. The same data through the CDS queue came at about one variable-year per day.
- **Size.** Each chunk is one hour of one variable for the whole globe (~2 MB), so even a small region reads
  the full field: a variable-year is ~16 GB. Run big reads on Databricks, not a laptop (a laptop manages
  ~35 MB/s, about 20 minutes per year for two variables).
- **How recent.** Attributes `valid_time_stop_era5t` (last complete day, ~6 days behind; ERA5T) and
  `valid_time_stop` (end of final ERA5, ~2–4 months behind). The time axis runs on past the record with
  empty chunks, so check those attributes rather than the axis. ERA5T months are later replaced by final
  ERA5 (usually identical, occasionally corrected), so rebuild anything derived from ERA5T once final ERA5
  covers it.
- **Daily statistics.** The CDS daily-statistics product is the max / min / mean of the 24 hourly values of
  the UTC day (00–23 UTC). Reproduce it from ARCO as above; `heat.arco` in
  [ds-heat-exposure](https://github.com/OCHA-DAP/ds-heat-exposure/blob/main/src/heat/arco.py) is a worked,
  threaded example that writes the CDS layout.
- **Grid.** Latitude 90 → −90, longitude 0 → 359.75 (the CDS downloads are usually −180 → 180).
- **Variables.** Names are long-form (`2m_temperature`, `total_precipitation`, …); `list(ds.data_vars)`
  shows them. ERA5-Land and the CDS's other derived datasets are not in this store.

## 3. The Copernicus CDS: only for what ARCO-ERA5 doesn't have

ERA5-Land, the C3S Atlas, seasonal forecasts, and other CDS datasets still come from the CDS API. ECMWF's data
store service protection measures (October 2026) ask for **sequential** requests and may suspend accounts
that submit large batches. Keep **at most two requests in flight**: the team key is shared with the flood
monitoring. A batch of 124 requests in November 2026 sat unstarted for 3 hours, and single requests then
queued for 8–20 hours ([heat-exposure](../../pipelines/heat-exposure.md) → *Why ARCO-ERA5*).

## Licence

ERA5 is CC-BY-4.0 under the Copernicus licence: derived products can be shared with attribution. Cite the
CDS catalogue DOI [10.24381/cds.f17050d7](https://doi.org/10.24381/cds.f17050d7) and credit Copernicus
visibly. The ARCO copy carries the same terms.
