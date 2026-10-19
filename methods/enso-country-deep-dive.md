---
content_type: method
last_reviewed: "2026-09-17"   # bump when a human verifies the page is still accurate
---

# ENSO country deep dive — how bad, how confident, how much El Niño

A **country deep dive** answers, for one country and one rainy season, the three questions a
humanitarian reader actually has when an ENSO event is developing:

1. **How bad is the coming season likely to be?** — the current SEAS5 issuance (return period
   of the forecast anomaly, at what skill) and where food insecurity already sits (FEWS NET).
2. **How confident are we?** — SEAS5 skill for the windows that carry the season, and the
   historical record: what El Niño seasons did before, how many missed, and why.
3. **How much of it is El Niño?** — the current Niño3.4 state, the ERA5 correlation
   (explained variance), and whether the response is uniform across the country.

Reference implementation: `ds-teleconnections/enso_deep_dive.py` + `deep_dives/<slug>.toml`
(see [pipelines/teleconnections.md](../pipelines/teleconnections.md)); published pages for
Eritrea, Malawi and Zimbabwe at <https://ocha-dap.github.io/ds-teleconnections/enso/>. The
earlier two pages are catalogue-led ("is the survey's literature grade earned?"); Zimbabwe is
the question-led template to copy for an operational read.

## Where each number comes from

Read the team's precomputed products first; recompute only what no product holds
([reuse-published-stats.md](reuse-published-stats.md)). Say on the page which is which.

| Element | Source | Recomputed? |
|---|---|---|
| Seasonal cycle, pixel Niño3.4 correlations per window, ENSO-phase drought hit-rates, El Niño composites | The survey's ERA5 0.25° pixel cache (`cache/era5_pixel/`) + the **pinned** Niño3.4 series | Yes — the survey's `corr_px_display` product keeps one best season per pixel, so per-window maps and phase statistics have to be computed |
| Country-level correlations (ADM0 table) | Survey `out/corr_*_l3.parquet` | No |
| By-province correlations and hit-rates | `public.era5` admin-1 monthly means (prod DB) + CODAB polygons | Correlation of the stored series — no pixel work |
| SEAS5 skill by window and lead; forecast return period and percentile | seas5-skill `skill_stats_grid_detrended.nc` (DEV blob), sampled at the page's cells, median per zone/country | No |
| Food security | ds-fewsnet-mirror site JSON + unit geometry, drawn **at FEWS NET's own units** | Never aggregated to admin units or rasterised |
| CERF drought allocations and their timing | `aa.cerf_allocation` + `aa.cerf_supplement` (dev DB) | No |
| Current ENSO state | NOAA PSL live Niño3.4 (`nino34_latest.data`) | — |

## Conventions that matter

- **Season year.** A Nov–Mar season is labelled by the year its first month falls in
  (2023/24 → 2023). Its harvest feeds the **consumption year** Apr Y+1 – Mar Y+2, whose
  lean season is Jan–Mar Y+2.
- **Zones.** Latitude bands or climatology bands are *analysis* devices to show whether
  the response is uniform. If it is (Zimbabwe), keep zones only in the seasonal-cycle chart
  and run everything nationally (`zones_analysis = false`); if it is not (Malawi), the
  zones carry the story and a national number is misleading.
- **Provinces, not zones, are the operational unit** — every page carries a by-province
  section from the DB raster stats.
- **CERF attribution.** An allocation belongs to the rainy season named in the CERF
  drought-period supplement; when that period spans two failed seasons it sits under the
  later one, flagged. Without a dated period, fall back to the consumption year the approval
  date falls in and say "by date". Show the approval month as months after 1 December of the
  season — the pattern (Zimbabwe: +9 to +15 months until 2023/24, then 0 and +6) is the
  point.
- **FEWS NET readings per season, like for like.** Three readings, each as shares of
  classified units in Phase 3 / 4 / 5: the pre-season outlook (issued Jun–Sep for Oct–Jan —
  the same product as the one in hand now), the in-season outlook (issued Oct for the lean
  season) and the observed current situation at the lean-season peak (Jan–Apr). Draw a dash
  for "classified, nothing in Phase 3+" and a "?" for "no reading published" — the two must
  not look alike ([absent-data.md](absent-data.md)).
- **Forecast return periods at the hindcast ceiling** (≈ 46 years for a 45-year hindcast)
  mean "the most extreme forecast in the record", not a calibrated 1-in-46. The September
  2026 issuance sits in the dry tail far more often than calibration allows *globally*
  (14–16 % of rainy pixels at the 0th percentile for NDJ–JFM); say so.

## Gotchas found while building these (all fixed in the reference implementation)

- **Index vintage.** NOAA PSL's `nina34.anom.data` moved to ERSST v6 in 2026 (~+0.2 °C).
  Refreshing the cache silently changed every phase count (Eritrea La Niña JAS seasons
  12 → 7). Keep the *analysis* series pinned (NOAA CPC ERSST v5 reproduces the old PSL
  values to 0.01 °C) and refresh only a separate *latest* series for the current-state line.
  The seas5-skill ENSO slides cache is already on v6 — the survey and the slides are on
  different bases until the survey is rerun.
- **FEWS NET assistance flag.** FDW's `is_allowing_for_assistance` is the "!" marker on the
  one published row per unit × scenario × round (phase held down by assistance), *not* a
  parallel "without assistance" series. Filtering it out drops those units (Zimbabwe, Feb
  2020: 98 of 203 units, 100 % in Phase 3+ → the published 48 %). Count every row at its
  phase. Verified against the October 2016 package shapefiles (`HA0/HA1/HA2`).
- **FEWS NET population.** None by phase for areas; only a national Phase 3+ range (FDW
  `ipcpopulationsize`, coarse bins, FAOB monthly from 2019, Peak Needs from 2016). Don't
  draw it as if it were a number.
- **Historical FEWS NET packages** are downloadable per round
  (`/api/ipcpackage/?country_code=ZW&collection_date=2016-10-01`) and are the rendered map;
  use them to settle any doubt about what was published.
- **ERA5 cache horizon.** The survey's pixel cache stops at its `end_year`; the deep-dive
  build appends newer monthly COGs from the prod raster blob into a side file so the current
  season is included without touching the survey's cache. Adding a season shifts ranks and
  phase counts — diff every generated table against the previous build and reconcile the
  narrative.
- **Narrative ≠ tables.** The TOML narrative quotes numbers; after *every* rebuild, dump the
  tables and check each quoted number. The Malawi and Zimbabwe pages each needed two rounds
  of reconciliation.

## Adding a country

Run a diagnostic pass first (candidate windows × zones — a national mean can cancel a real
sub-national signal), verify literature and event sources by web search, copy the closest
TOML, write the narrative against the *generated* tables, rebuild all pages, diff, reconcile,
render with headless Chrome, push. Repo README has the TOML keys.
