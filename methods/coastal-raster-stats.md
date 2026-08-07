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

1. **Buffer each admin polygon seaward only**: buffer by the distance chosen
   below (starting point: half the pixel *diagonal* — ~700 m for 1 km
   pixels), intersect the added ring with the ocean (buffer ∸ land), and
   merge it back into the polygon. Land-side boundaries are untouched, so
   admins never grow into each other.
2. **De-overlap**: where two admins' ocean extensions overlap, assign the
   overlap to one of them. After this the polygons are strictly
   non-overlapping (union area == sum of areas). Note the extension can
   never claim another admin's *land* (step 1 subtracts all land from every
   ring) — but rings **do** contest wherever two coasts sit within 2×buffer
   of each other, including islands the admin never touched. A fixed-order
   sequential difference (sorted p-code) is simplest but settles those
   contests by sort order: at 500 m in Vanuatu, 2,412 people sit on pixels
   a fixed order hands to the non-nearest admin — Port Vila's ring claims
   Ifira islet's and Erakor lagoon's near-shore pixels because it sorts
   first. If per-admin numbers matter, de-overlap by **nearest admin**
   instead; fixed order only shuffles population between neighbours, so
   higher-level aggregates are unaffected either way.
3. **Run zonal stats on the extended polygons** — see the pairing table
   below for which stat engine.

With the extended polygons, even the plain **pixel-center rule captures
338,648 of 338,868 (99.94%)** — and because the polygons are non-overlapping,
a pixel center falls in at most one admin, so per-admin results **partition
exactly**: no double counting is possible by construction. The two failure
modes cancel each other's fix.

## Choosing the extension distance — sweep it, don't assume it

Half a pixel is a floor, not the answer. Two separate effects hide in the
"missed" population, and a cheap sweep (dissolved land union buffered by *d*,
center-rule capture at each *d*) tells them apart:

| buffer (Vanuatu, 1 km pixels) | captured | missed |
|--:|--:|--:|
| 0 m | 302,524 | 36,344 |
| 250 m | 331,282 | 7,586 |
| 500 m | 338,648 | 220 |
| **707 m (half pixel diagonal)** | 338,815 | 53 |
| 2 km | 338,840 | 28 |
| 5 km | 338,868 | 0 |

- **Pixel discretization** is fully exhausted at half the pixel *diagonal*
  (0.71 px): that is the farthest a land-touching pixel's center can sit
  from the coastline, so the curve must plateau there **if boundaries and
  raster agree on where the coast is**.
- **A tail beyond ~1 px is real misalignment**: coastline generalized away,
  a different land mask in the raster, or populated islets absent from the
  boundary file entirely (the 48 people above). If the curve keeps climbing
  well past a pixel, the boundary file — not the buffer — is the problem;
  a large buffer will still capture that population, but it assigns it to
  whichever admin's extension reaches first, so check those pixels land
  where they should.
- **Over-buffering is nearly free over open ocean** (the added ring holds no
  people by definition) — but cap the distance below ~half the narrowest
  strait between *different* admins, or the fixed-order de-overlap starts
  settling cross-channel disputes arbitrarily. If you genuinely need a large
  distance, de-overlap the extension ring by **nearest admin** (Voronoi
  of the coastline) instead of fixed order.

## Pairing with the stats engine

For count rasters on the extended, de-overlapped polygons, **either engine is
sound** — the geometry does the heavy lifting, and *totals* come out
near-identical:

- **`exactextract` coverage-weighted `sum`** — the team's direction for
  exposure work. Coastal pixels get ≈ full weight (the extension covers their
  ocean part), and interior boundary pixels are additionally split by exact
  area fraction between admins, which sharpens *per-admin* numbers at the
  margins. Totals still partition, since the polygons don't overlap.
- **Pixel-center rule** (`rio.clip` default) — equally valid, and handy where
  exactextract isn't (Pyodide, quick scripts). Boundary pixels are assigned
  whole to whichever admin holds their center rather than split, so per-admin
  figures differ slightly at the margins; the partition property is the same.
  An equivalent formulation is a rasterized pixel→admin assignment with
  first-come priority (`ds-aa-vut-cyclones/exploration/recalc_adm2_exposure.py`).
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
- **Check the leftover**: after choosing a distance from the sweep above,
  compare the extended-polygon capture against the raster's own near-shore
  total — the residual is what you are knowingly leaving out, and should be
  a number you can name (53 people at 707 m in Vanuatu), not a surprise.
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
