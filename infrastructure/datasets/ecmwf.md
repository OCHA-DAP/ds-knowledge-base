---
content_type: dataset
name: ECMWF (SEAS5 / ERA5)
aliases: [ECMWF, SEAS5, ERA5, ERA5-Land, C3S, CDS, "seasonal forecast", reanalysis]
provider: "ECMWF / Copernicus Climate Change Service (C3S)"
data_type: precipitation-forecast-and-reanalysis
access: public
api: "CDS: https://cds.climate.copernicus.eu (cdsapi)  ·  MARS API (archival)  ·  team AWS bucket for the 0.4° SEAS5 push"
auth: "free CDS account + API key (CDSAPI_URL/CDSAPI_KEY); ECMWF_API_* for MARS; AWS_* for the SEAS5 bucket"
formats: [grib, netcdf]
resolution: "SEAS5: 1° on CDS, 0.4° via MARS/AWS (our ingest), monthly issue, ~7-month leadtime; ERA5: 0.25° global, hourly + monthly, 1940–present"
update_cadence: "SEAS5: monthly, published the 6th of each month; ERA5: monthly (ERA5T early release ~5-day latency)"
license: "CC-BY-4.0 — but see the Official-Duties caveat under Licence & sharing"
code_ref: "ingested to COGs by ds-raster-pipelines (see pipelines/raster-pipelines.md); zonal stats read from public.seas5 / public.era5 via ocha-stratus"
mirror: automated        # ds-raster-pipelines keeps SEAS5 + ERA5 COGs and raster stats fresh
mirror_priority: low
used_by:
  - pipelines/raster-pipelines.md
  - pipelines/raster-stats.md
  - pipelines/seasonal-bulletin.md
  - pipelines/eth-drought-monitoring.md
  - pipelines/teleconnections.md
  - frameworks/eth-drought/2026-06-09.md
  - frameworks/afg-drought/2026-04-04.md
  - frameworks/bfa-drought/2026-04-17.md
  - frameworks/tcd-drought/2025-03-03.md
  - frameworks/lac-dry-corridor/2026-03-13.md
  - apps/c3s-viz.md
  - apps/seas5-skill.md
  - apps/seas5-viz.md
visibility: public
last_verified: 2026-07-10
---

# ECMWF — SEAS5 seasonal forecasts & ERA5 reanalysis

The ECMWF data family as we consume it: **SEAS5** seasonal precipitation forecasts (the
backbone of our drought triggers) and **ERA5** reanalysis (our default historical
precipitation record). **Ingest mechanics live in
[pipelines/raster-pipelines.md](../../pipelines/raster-pipelines.md)** — this page is the
dataset reference and the gotchas.

## SEAS5 seasonal forecasts

- Each forecast covers **215 days (~7 months)** ahead and is **published on the 6th of the
  month** (e.g. the January forecast is published Jan 6, covering Jan 1 – Aug 3).
- **What the team ingests is NOT the public CDS product.** Our COGs are the higher-res
  **0.4°** data: archival 1981–2023 from the **MARS API**, 2024-onward from ECMWF's monthly
  GRIB push to the team AWS bucket — chosen for higher resolution and more timely delivery
  of the full 7-month leadtime than CDS provides. See
  [raster-pipelines](../../pipelines/raster-pipelines.md) for sources, paths, and naming.
- The **public CDS products** are **1°** and shorter-leadtime; use them only when the blob
  COGs / `public.seas5` stats don't cover the need:
  - *Seasonal forecast daily and subdaily data on single levels*
    (`seasonal-original-single-levels`) — since 1981, 215-day coverage, daily precip.
  - *Seasonal forecast monthly statistics on single levels*
    (`seasonal-monthly-single-levels`) — since 1981, 6 months, monthly.
- Reference docs: C3S Seasonal Forecasts on the ECMWF Confluence
  (`confluence.ecmwf.int/display/CKB/C3S+Seasonal+Forecasts`); current-trimester precip chart
  at `charts.ecmwf.int/products/seasonal_system5_standard_rain`.

## ERA5 reanalysis

- Two CDS products, both **0.25°**, global, since 1940: *ERA5 monthly averaged data on
  single levels* (what we ingest — monthly total precipitation) and *ERA5 hourly data on
  single levels* (ensemble mean 3-hourly / individual members hourly).
- Recent months are actually **ERA5T** (early release, ~5-day latency), replaced by final
  ERA5 2–3 months later and occasionally revised — see the `expver` note in
  [raster-pipelines](../../pipelines/raster-pipelines.md).

## Gotchas

- **`valid_date` = the END of the aggregation window, not the start.** SEAS5's `valid_date`
  attribute marks the end of the monthly time-aggregation window, while our own code
  convention treats `valid_time` as the **start** of the month — the two conventions differ
  by exactly one month and are easy to misread. See
  [OCHA-DAP/ds-raster-pipelines issue #9](https://github.com/OCHA-DAP/ds-raster-pipelines/issues/9)
  and `ds-raster-pipelines/examples/ecmwf_temporal_vars.md` (also ecmwf/cfgrib issue #97 and
  the C3S sf-anomalies training on converting leadtime months into dates). Whenever you touch
  raw SEAS5 GRIB/NetCDF, confirm which convention the timestamps follow before aggregating.
- **ERA5-Land ≠ ERA5 for accumulations.** ERA5-Land uses a **different convention for
  defining accumulated variables** (e.g. total precipitation) than ERA5 — see the ECMWF CKB
  "ERA5-Land data documentation", *Accumulations* heading, before mixing the two.

## C3S "Seasonal Forecast Anomalies on Single Levels" (postprocessed)

A separate upstream **anomaly** product on CDS (`seasonal-postprocessed-single-levels`) —
**distinct from our own `public.seas5` raster stats**, which are ensemble-mean precipitation
by pcode computed from the 0.4° COGs. Key methodology:

- **Grid**: all contributing centres regridded to a global regular **1°×1°** lat-lon grid
  (exception: JMA at 1.25°×1.25°).
- **Anomaly** = real-time forecast value minus the model **hindcast climatological mean** for
  the same lead month and start time; reference hindcast period **1993–2016**, uniform across
  all systems; computed per system and per ensemble member.
- **Single-system ensemble mean** = equal-weights average over the *qualifying* members
  (the subset used in C3S graphical products — for lagged-start systems this can be a subset
  of the full ensemble).
- **Multi-system combination** uses **variance-standardisation weights** so each system
  contributes equally to combined variance over 1993–2016:
  wₛ = √(mean variance across systems) / √(variance of system s).
- **Probabilistic products** (tercile lower/middle/upper, lowest/highest 20%, median):
  thresholds from the hindcast climatology per grid cell; per-system probability = fraction
  of qualifying members in the category; multi-system probability = **unweighted** mean of
  the individual system probabilities.

The [c3s-viz app](../../apps/c3s-viz.md) is our surface for comparing per-system C3S skill
and forecasts.

## Licence & sharing

- **SEAS5 / ECMWF open data: CC-BY-4.0** (redistribution + commercial use with attribution,
  per the ECMWF Terms of Use + Product Distribution Rules) — **but** ECMWF clarified that our
  *free access* is tied to **Official Duties only**, not competitive/market-distorting use.
  So derived products are shareable **sometimes**: fine for humanitarian outputs, not for
  anything that competes in the marketplace.
- **ERA5: yes** — CC-BY-4.0, plus you **must** cite the CDS catalogue entry
  (DOI [10.24381/cds.f17050d7](https://doi.org/10.24381/cds.f17050d7)) and give visible
  Copernicus attribution ("Generated using / contains modified Copernicus Climate Change
  Service information <year>. Neither the European Commission nor ECMWF is responsible for
  any use of this information.").

See the shareability matrix in the [datasets README](README.md#can-we-share-derived-products).

---

Source: digested from the retired DSCI Confluence space (full archive: `confluence/` in the
private companion repo `ds-knowledge-base-internal`). Original pages: "ECMWF", "Help! How do
I interpret the valid_date attribute?", "ECMWF SEAS5 Seasonal Forecasts - Anomalous
Precipitation".
