---
content_type: method
last_reviewed: "2026-08-07"   # bump when a human verifies the page is still accurate
---

# Coastal admin boundaries × coarse rasters — the seaward-extension recipe

Admin polygons are drawn to the coastline; population rasters put people in
coarse pixels that straddle it. On small-island and coastline-heavy
geographies this mismatch silently loses (or double counts) a large share of
the population, and the three obvious clip rules each fail differently. The
fix that works is geometric: **extend the admin polygons a few hundred metres
seaward, de-overlap them, and only then run zonal stats**. Developed for
`ds-aa-vut-cyclones` (WorldPop 1 km × Vanuatu adm2); the numbers below are
that case.

## The failure modes, quantified (Vanuatu, WorldPop 1 km, 66 adm2)

| clip rule on the *original* polygons | national pop captured | problem |
|---|--:|---|
| pixel-center (`rio.clip` default, `rasterstats` default) | 302,524 | **loses 36k people — 10.7%** — coastal pixels whose centers fall in the sea |
| `all_touched=True` per admin | 338,735 | captures ~all, but a boundary pixel lands in **every** admin it touches — summing across admins double counts (**+23%** on the Vanuatu AOI aggregate, because the densest population sits on the densest adm2 mesh) |
| `exactextract` coverage-weighted | between the two | interior boundary pixels are split exactly (good), but a coastal pixel that is 80% ocean contributes only 20% of its people — even though all of them live on the land sliver. Systematic coastal undercount for **count** rasters |

The reference total (any pixel touching land): 338,868.

## The recipe

1. **Buffer each admin polygon seaward only**: buffer by ~half a pixel
   (500 m for 1 km pixels), intersect the added ring with the ocean
   (buffer ∸ land), and merge it back into the polygon. Land-side boundaries
   are untouched, so admins never grow into each other.
2. **De-overlap**: where two admins' ocean extensions overlap, assign the
   overlap to one of them (sequential difference in a fixed order — sorted
   p-code works). After this the polygons are strictly non-overlapping
   (union area == sum of areas).
3. **Run zonal stats on the extended polygons** — see the pairing table
   below for which stat engine.

With the extended polygons, even the plain **pixel-center rule captures
338,648 of 338,868 (99.94%)** — and because the polygons are non-overlapping,
a pixel center falls in at most one admin, so per-admin results **partition
exactly**: no double counting is possible by construction. The two failure
modes cancel each other's fix.

## Pairing with the stats engine

- **`exactextract` (the team's direction for exposure work) — count rasters:**
  run coverage-weighted `sum` on the **extended, de-overlapped** polygons.
  Coastal pixels get ≈ full weight (the extension covers their ocean part);
  interior boundary pixels are split by exact area fraction between admins —
  strictly better than any whole-pixel assignment — and totals still
  partition, since the polygons don't overlap.
- **No exactextract available** (Pyodide, quick scripts): pixel-center rule on
  the extended polygons, as above. Or, equivalently, rasterize a pixel→admin
  assignment with first-come priority (`ds-aa-vut-cyclones/exploration/recalc_adm2_exposure.py`).
- **Intensive variables (means: rainfall, NDVI, wind) — do *not* extend.**
  The extension exists because count rasters allocate people to the land part
  of a mixed pixel; a mean would instead be diluted with ocean-pixel values.
  Coverage weighting (or the upsampling proxy in
  [pipelines/raster-stats](../pipelines/raster-stats.md)) on the original
  polygons is already right for means.

## Pitfalls

- **Never `all_touched=True` per admin and then sum across admins.** This was
  the actual bug in the original Vanuatu exposure numbers: the vector-level
  de-overlap was done carefully, but `all_touched` re-introduces the overlap
  at the pixel level (in Vanuatu: 1,005 pixels claimed by 2+ adm2 → +23% on
  AOI totals). Vector non-overlap does not imply pixel-assignment uniqueness.
- **Check the invariant**: any admin aggregate must be ≤ the population of
  the same polygons' dissolved clip. The Vanuatu bug sat in a published
  parquet for months with one storm's "exposed" exceeding the AOI's entire
  population.
- **Check the leftover**: `all_touched` on the dissolved union minus the
  extended-polygon capture = what your extension distance still misses
  (87 people at 500 m in Vanuatu; widen the buffer if it's material). A
  residual against the raster's own total can also reveal populated pixels
  outside the boundaries entirely (48 people here — offshore islets absent
  from CODAB).
- Buffer in a **metric CRS**, and on dateline-straddling geographies do all
  lon/lat conversion in a lon-wrapped frame (`+lon_wrap=180`) — plain
  EPSG:4326 tears cross-meridian polygons into a map-wide smear (the other
  Vanuatu exposure bug; see `antimeridian` usage in
  [pipelines/storms-pipeline](../pipelines/storms-pipeline.md)).

## Reference implementation

`ds-aa-vut-cyclones`: construction in
`exploration/make_forecast_check_data.py::build_adm2_expanded` (originally
`exploration/hist_exp.md`); pixel-unique per-admin stats in
`exploration/recalc_adm2_exposure.py`. Related:
[pipelines/raster-stats](../pipelines/raster-stats.md) (whole-pixel vs
pixel-weighting trade-off for the general stats pipeline),
[pipelines/storms-pipeline](../pipelines/storms-pipeline.md) (exactextract
exposure path).
