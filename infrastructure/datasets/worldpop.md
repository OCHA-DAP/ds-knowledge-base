---
content_type: dataset
name: WorldPop
aliases: [WorldPop, "WorldPop-2025", worldpop]
provider: "WorldPop, University of Southampton"
data_type: population-raster
access: public
api: "https://hub.worldpop.org  ·  REST: https://www.worldpop.org/sdi/introapi/  ·  ArcGIS ImageServer for 1km density"
auth: "none (open)"
formats: [geotiff]
resolution: "100 m and 1 km grids; per-country and global mosaics; annual 2015–2030 (Global2); EPSG:4326"
update_cadence: "per WorldPop release (Global2 = annual estimates 2015–2030)"
license: "CC-BY 4.0"
code_ref: "read as a COG from our blob raster container via ocha-stratus (open_blob_cog)"
mirror: manual          # tiles on blob, uploaded ad-hoc; no automated refresh (updates annually)
mirror_priority: low    # slow-moving; staleness rarely bites
used_by:
  - pipelines/storms-pipeline.md
  - pipelines/storm-impact-harmonisation.md
  - pipelines/floodexposure-monitoring.md
  - pipelines/flood-gfm.md
  - pipelines/glb-cyclones-impactmodel.md
  - frameworks/nga-flooding/2026-06-18.md
  - frameworks/fji-storms/2025-12-17.md
  - frameworks/moz-cholera/2026-05-22.md
  - frameworks/vut-cyclones/development.md
  - apps/floodexposure-monitoring-app.md
last_verified: 2026-07-01
---

# WorldPop

Gridded **population counts** — our default population denominator for **exposure**
(people in a flood extent / cyclone wind field / cholera catchment). We standardise on the
**1 km global mosaic**; 100 m is available where finer grain is needed.

## How we access it

- We keep a copy on our **blob raster container** (e.g.
  `worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif`) and read it as a **COG** via
  **[`ocha-stratus`](../libs/ocha-stratus.md)** (`open_blob_cog` / `stack_cogs`), same as any
  raster in the exposure pipelines.
- Upstream: the **WorldPop hub** (`hub.worldpop.org`) for GeoTIFF downloads (country + global
  mosaics), a **REST API** (`worldpop.org/sdi/introapi/`), an **ArcGIS ImageServer** for 1 km
  density, and mirrors on [HDX (`worldpop`)](https://data.humdata.org/organization/worldpop).

## How we use it

Zonal sums under a hazard mask → **population exposed**, feeding the flood-exposure monitor,
the storm impact model, and framework exposure estimates.

## Gotchas

- **Constrained vs unconstrained**: constrained models confine population to built settlements
  (more realistic where settlement layers are good); unconstrained spread it across admin
  areas. Know which product a number came from — they differ materially in sparse areas.
- **Year matters** — pick the estimate year that matches the analysis; don't mix vintages
  across a comparison.
- Counts are **modelled estimates**, not a census; uncertainty is highest in low-density and
  rapidly-changing areas. Cross-check against [GHSL](ghsl.md) when population is the crux.
