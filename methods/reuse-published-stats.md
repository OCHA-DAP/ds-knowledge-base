---
content_type: method
last_reviewed: "2026-08-31"   # bump when a human verifies the page is still accurate
---

# Reuse published statistics — don't recalculate what a product already exports

When one of our products already publishes a statistic — a forecast percentile, a return
period, a severity category, a zonal mean — any derived view built on top of it (slides, a
country brief, an ad-hoc analysis, another app) should **read the product's export, not
recompute the number**. Recomputing forks the methodology: a different record, a different
spatial aggregation, detrended vs raw, log-normalised vs mm — and the derived view then
shows a number that disagrees with the authoritative product. The reader now has two
"official" values for the same thing and no way to know which to trust. Reusing the export
also inherits the product's vintage handling for free (see
[absent-data.md](absent-data.md) for the sibling failure class, and
`feedback_vintage_integrity` in project memories).

## The zonal-stats corollary: no bounding-box aggregates

Never approximate a country or admin-unit aggregate with a **simple bounding-box mean**
(or a bbox clip plus a coarse all-touched mask). At forecast-grid resolutions the bbox
drags in neighbouring countries, ocean cells, and edge pixels whose inclusion is
arbitrary — and the result quietly diverges from the team's zonal statistics. Aggregate
over the **actual admin geometry**: the DB zonal-stats tables (`public.seas5`,
`public.era5` — produced with proper polygon weighting), or if computing directly from
rasters, a real polygon-weighted aggregation over the COD boundary.

The point is consistency of method, not of file: raster statistics don't have to come from
one specific export — but they must be genuine zonal aggregations, and where an
authoritative product publishes the same quantity, the numbers must agree (or the
divergence must be deliberate and labelled).

## When recomputation is legitimate

- The product doesn't export the quantity, or not at the spatial unit needed. Then match
  the upstream methodology (same record, same transforms — e.g. detrending — same
  aggregation) so the new number is an *extension* of the product, not a rival to it.
- A deliberate methodological variant (e.g. raw vs detrended). Fine — but label it, and
  don't present it beside the product's number as if they were the same statistic.

## Where this bit us

Aug 2026, the PNG/Timor-Leste ENSO slide pages (`ds-seas5-skill` `pages/{png,tls}-enso/`,
built by `analysis/png_enso_slides.py`): the slide's country return periods were
recomputed from a raw bounding-box-mean SEAS5 series and its bar colours from a third
quantity (mean pixel percentile). PNG SON showed **1-in-15 dry** while the app's main page
— adm0 detrended zonal series — showed **1-in-46**, and a 15-yr-RP trimester wore a
3–10-yr colour. The review caught it immediately ("isn't SON more severe, based on the
app?"). Fix: the slides now read `docs/data/forecasts/<issued>.json`, the same export the
app renders, with the issuance vintage asserted.
