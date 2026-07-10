---
content_type: dataset
name: GloFAS
aliases: [GloFAS, "Global Flood Awareness System", CEMS-flood]
provider: "Copernicus Emergency Management Service (CEMS) — JRC/ECMWF"
data_type: river-discharge-forecast
access: public
api: "Copernicus Data Store (cdsapi; GloFAS/CEMS-flood datasets — forecast, reforecast, historical/reanalysis)  ·  web map: https://global-flood.emergency.copernicus.eu"
auth: "free CDS account + API key"
formats: [grib, netcdf]
resolution: "gridded river discharge, global; daily; 30-day ensemble forecast + reanalysis from 1979 (v4 grid 0.05°)"
update_cadence: "daily forecast; reanalysis updated continuously"
license: "CC-BY-4.0 (Copernicus/CEMS attribution)"
code_ref: null
mirror: n/a             # queried per-analysis at single station pixels; storing global daily rasters was considered and rejected (~30 rasters/day, limited use)
mirror_priority: low
used_by:
  - frameworks/ner-flooding/2025-11-04.md
  - frameworks/nga-flooding/2025-08-11.md
  - frameworks/tcd-flooding/2025-07-31.md
  - frameworks/bgd-flooding/2025-04-25.md
  - frameworks/npl-flooding/2025-08-25.md
  - analysis/caf-flooding.md
visibility: public
last_verified: 2026-07-10
---

# GloFAS

The Copernicus **Global Flood Awareness System** — global gridded **river discharge**
reanalysis, forecasts, and reforecasts. The riverine-flood trigger data behind our
Niger, Nigeria, and Chad flooding frameworks (plus Bangladesh/Nepal work and ad-hoc
flood analyses).

## How we access it

- **Copernicus Data Store** via `cdsapi` (free account + key) — the GloFAS/CEMS-flood
  datasets: daily ensemble **forecast**, **reforecast**, and **historical** (reanalysis).
  The web map interface is at `global-flood.emergency.copernicus.eu`.
- No shared loader; per-analysis pulls in the framework repos. (Do **not** use
  `ocha-anticipy` for GloFAS access — deprecated.)

## How we use it

- GloFAS is a global raster but we typically analyze **single pixels corresponding to
  reporting stations** (the virtual/actual gauging stations the frameworks trigger on).
- **We DO use the forecast ensembles** — unlike SEAS5 (where we generally take the ensemble
  mean), GloFAS analysis keeps the members so probabilities match the **GloFAS web
  interface**, which only reports the forecast numerically as probabilities.
- **Skill assessment**: compare the **reanalysis** timeseries against the
  **reforecast/forecast** at the station pixel to assess forecast accuracy before setting
  a trigger.
- We deliberately do **not** mirror global daily GloFAS rasters (~30 global rasters/day,
  limited use beyond the station pixels).

## Gotchas

- **Historical forecast ≠ reforecast, even for the SAME dates.** The archived real-time
  forecasts and the reforecast for identical dates can differ, due to differences in model
  **initialization**. Globally this difference should be unbiased, but **local biases exist
  and must be investigated per analysis** — don't validate a trigger on reforecast skill and
  assume the real-time forecast behaves identically at your station. (ECMWF support ticket
  SD-113508.)

---

Source: digested from the retired DSCI Confluence space (full archive: `confluence/` in the
private companion repo `ds-knowledge-base-internal`). Original pages: "GloFAS" (+ usage notes
from "Core Data Sets").
