---
content_type: dataset
name: GHSL
aliases: [GHSL, "Global Human Settlement Layer", GHS-POP, GHS-BUILT, GHS-SMOD]
provider: "European Commission Joint Research Centre (JRC)"
data_type: settlement-and-population-raster
access: public
api: "https://human-settlement.emergency.copernicus.eu/download.php  ·  catalogue: https://data.jrc.ec.europa.eu/collection/ghsl  ·  Google Earth Engine"
auth: "none (open)"
formats: [geotiff]
resolution: "GHS-BUILT to 10 m; GHS-POP 100 m / 1 km; multi-temporal 1975–2030 (5-yr epochs incl. 2025, 2030); Mollweide + WGS84"
update_cadence: "per JRC release (current package: R2023A)"
license: "open and free (European Commission)"
code_ref: "read as a COG from blob via ocha-stratus (open_blob_cog) where mirrored"
mirror: manual          # tiles mirrored to blob ad-hoc; JRC releases every few years
mirror_priority: low    # near-static (5-yr epochs); staleness rarely bites
used_by:
  - frameworks/cub-hurricanes/2026-06-17.md
  - frameworks/hti-hurricanes/2026-06-09.md
  - pipelines/flood-gfm.md
last_verified: 2026-07-01
---

# GHSL — Global Human Settlement Layer

JRC's global **built-up** and **population** grids — our alternative / cross-check to
[WorldPop](worldpop.md) for exposure, and the source when we need **built-up surface** or a
**degree-of-urbanisation** (urban/rural) split. Three main products:

- **GHS-POP** — residential population grid (100 m / 1 km).
- **GHS-BUILT** — built-up surface / height / volume (to 10 m).
- **GHS-SMOD** — settlement model (degree of urbanisation: urban centre / cluster / rural).

All **multi-temporal, 1975–2030** at 5-year epochs (including projected 2025/2030).

## How we access it

- **Direct download** (`human-settlement.emergency.copernicus.eu/download.php`) or the
  **JRC Data Catalogue**; also on **Google Earth Engine** for programmatic access.
- Where used in exposure pipelines we mirror the needed tiles to **blob** and read them as
  **COGs** via **[`ocha-stratus`](../libs/ocha-stratus.md)** (`open_blob_cog`), like any raster.

## How we use it

Exposure denominators and **urban/rural** stratification for storm/flood impact work — a
second opinion against WorldPop, and the go-to when built-up extent (not just headcount)
matters.

## Gotchas

- **Native CRS is Mollweide (equal-area)** for many products — reproject to EPSG:4326 before
  combining with our WGS84 hazard layers, and mind that resampling population changes counts.
- **Epoch ≠ observation year** for future epochs (2025/2030 are **modelled projections**).
- GHS-POP and [WorldPop](worldpop.md) use different methods and **won't match** — pick one per
  analysis and note which; don't average across them.
