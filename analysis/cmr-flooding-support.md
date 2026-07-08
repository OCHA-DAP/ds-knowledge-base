---
content_type: analysis
name: cmr-flooding-support
analysis_type: exploratory   # situational-awareness / impact-estimation support; NOT ad-hoc-activation — no anticipatory action ever fired (the 2024 CERF money was a rapid-response, i.e. reactive, allocation)
status: dormant
country_iso3: CMR
hazard: flood
summary: "Repeated seasonal-forecast-driven flood-impact estimates for Cameroon (esp. Logone-et-Chari / Mayo-Danay, Extrême-Nord) through the 2024 flood response and into a Jan-2025 update — exploration notebooks only, no framework doc, no schedule, no deployment."
data_sources: [FloodScan, SEAS5, ERA5, IRI, EM-DAT, WorldPop, CODAB, "Copernicus EMS (CEMS rapid mapping)"]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-cmr-flooding-support
source_branch: jan-2025-analysis
source_sha: 6f0cddf
code_ref:
  - exploration/jan_2025.md
  - exploration/estimate_2024.md
  - exploration/estimate_2024_logonechari.md
  - exploration/oct_estimate.md
  - exploration/octnov_estimate.md
  - exploration/impact_2024.md
  - exploration/impact.md
  - exploration/emdat.md
  - exploration/emdat_all.md
  - exploration/seas5_era5.md
  - exploration/copernicus_mapping.md
  - exploration/raster_stats_validation.md
  - exploration/exp_from_db.md
  - exploration/watersheds.md
  - exploration/iri.md
  - src/datasources/floodscan.py
  - src/datasources/seas5.py
  - src/datasources/era5.py
  - src/datasources/emdat.py
  - src/datasources/impact.py
  - src/datasources/worldpop.py
  - src/datasources/copernicus.py
  - src/datasources/watersheds.py
  - src/constants.py
depends_on: [floodexposure-monitoring, raster-pipelines]
discrepancies:
  - "[gap] README describes a productionized entrypoint (`python src/main.py`) but no `src/main.py` exists anywhere in the repo — the only runnable code is `src/` helper modules (`datasources/`, `blob.py`, `db_utils.py`, `utils.py`) called ad hoc from the `exploration/` notebooks. The repo never grew past exploration despite the README's pipeline framing."
  - "[stale] `src/db_utils.py` (used by `exploration/exp_from_db.md`) duplicates connection logic already available via `ocha-stratus` (used elsewhere in the same repo, e.g. `emdat_all.md`, `seas5_era5.md`) — inconsistent DB-access pattern across notebooks, not a functional bug."
extra:
  type_note: "Classified exploratory, not ad-hoc-activation: the repo produced forecast-driven situational-awareness / impact-estimate products for the 2024 Far North flood response, but no anticipatory action framework or trigger exists and none fired. constants.py CERF_YEARS=[2012, 2024] refers to CERF flood allocations the analysis retrospectively references; the 2024 one (CERF-CMR-24-RR-1427, $4M) was a rapid-response allocation, not an AA trigger."
visibility: internal
last_synced: "2026-07-08"
---

# Cameroon flooding support — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-cmr-flooding-support` is a repository of one-off exploration notebooks built to support OCHA's response to recurrent seasonal flooding in Cameroon's Far North (Extrême-Nord) and North regions — centered on the Logone-et-Chari and Mayo-Danay departments, which sit on the Logone/Chari river basin (Lake Chad Basin). It is **not a framework**: there is no published trigger document, no endorsed mechanism, and no CERF pre-arranged financing envelope tied to this analysis — `CERF_YEARS = [2012, 2024]` in `src/constants.py` records that CERF flooding allocations happened in those years, but they are ad-hoc allocations the analysis retrospectively references, not something this repo's trigger fires. It is also **not a living pipeline**: nothing in the repo runs on a schedule, there is no deployment, and (per the discrepancy above) the entrypoint the README advertises (`src/main.py`) does not exist — every notebook is run by hand and calls helper functions in `src/datasources/` directly. The work is best read as a running series of manually-produced situational-awareness estimates, repeated at each new seasonal-forecast update through the 2024 flood season and once more in January 2025.

## What was analyzed / findings

The core method, repeated across most notebooks with small variations: take the latest ECMWF **SEAS5** seasonal rainfall forecast for the basin/departments of interest, rank the current year's forecast against the 1981–2023 historical distribution to get a **percentile**, then use that percentile (± a fixed spread, e.g. ±20 percentile points) to sample the same percentile range from the **historical FloodScan-derived flood-exposure distribution** (population exposed to flooding, FloodScan SFED × WorldPop, 1998–2023) for each admin unit. The resulting exposure range is then converted to an **estimated affected-population range** via a simple linear regression (`exposed_to_impact`, fit on `cmr_adm2_impact_exposed.csv`) between historical flood-exposed population and OCHA-reported affected population (from the 2022 and 2024 flood impact assessments).

This estimate was re-run at each forecast update through 2024, tracking the evolving lead time/valid-month window as the season progressed:
- `estimate_2024.md` — March-issued forecast for JJA (June–August), national ADM2-level estimate.
- `estimate_2024_logonechari.md` — July-issued forecast for JAS (July–September), Logone-et-Chari watershed only.
- `octnov_estimate.md` — October-issued forecast for ON (October–November).
- `oct_estimate.md` — September-issued forecast for SON (September–October–November).
- `jan_2025.md` — the most recent notebook (branch `jan-2025-analysis`), a January-issued SEAS5 forecast for June–July 2025 (`valid_months = [6, 7]`) — processes ranks/percentiles for the Logone-Chari basin but does not carry the analysis through to an impact estimate, i.e. it is a partial re-run of the same recipe for the next season, not a finished product.

Supporting/validating exploration:
- **`impact_2024.md`** compares daily FloodScan-derived exposure (from the live `ds-floodexposure-monitoring` pipeline's per-country exposure rasters) against the actual OCHA-reported 2024 affected-population figures by commune/department, to sanity-check the exposure→impact relationship used elsewhere.
- **`emdat.md`** / **`emdat_all.md`** reconstruct a 2000–2024 "people affected by flooding" time series for Cameroon, splicing EM-DAT (2000–2021) with OCHA impact-assessment figures for 2022 and 2024, and back-filling a few known department-level events (2010, 2012, 2013, 2020) from EM-DAT/ReliefWeb DREF reports where EM-DAT itself isn't department-resolved.
- **`copernicus_mapping.md`** validates the team's FloodScan/WorldPop exposure estimate against **Copernicus Emergency Management Service (CEMS)** rapid-mapping products (activation EMSR772, two observation dates in Oct/Nov 2024) for three AOIs (Yagoua, Makari, Waza) — found the CHD estimate differs from CEMS's own published exposure figures by a substantial "factor error" (computed inline, not summarized as a single number in the notebook).
- **`seas5_era5.md`** checks SEAS5 forecast skill against ERA5 reanalysis (detrended) for Extrême-Nord, overlays EM-DAT/impact totals and CERF years, and plots the 2025 SEAS5 forecast against the historical scatter — an informal skill/plausibility check rather than a formal verification score.
- **`raster_stats_validation.md`** and **`exp_from_db.md`** cross-check raster-derived stats computed directly from blob COGs against the equivalent values already sitting in the prod Postgres DB (`public.seas5`, `app.floodscan_exposure`), to confirm the DB-side aggregation matches a from-scratch raster computation.
- **`watersheds.md`** stages Lake Chad Basin (LCB) river-basin shapefiles (Logone, Chari upstream, Logone-et-Chari) to blob so basin-level (rather than admin-level) clipping can be used for the SEAS5/ERA5/IRI rainfall analyses.
- **`iri.md`** is a secondary/exploratory seasonal outlook check using IRI's seasonal precipitation probability forecast, plotted for the basin — not used downstream by the impact-estimate notebooks.

No formal trigger or threshold was ever proposed — the percentile-matching approach is a rough analogue-year technique for producing a plausible impact range at each forecast update, not a candidate trigger design.

## Relation to frameworks

Standalone. Cameroon has no OCHA/CERF AA framework in the KB (`catalog.md` has no `cmr` entry), and nothing in this repo proposes one — it is direct situational/impact-estimation support for an active response, closer in kind to the other regional flood-exploration analyses (`caf-flooding`, `cod-flooding`, `eth-flooding`, `ssd-flooding`) than to a pre-framework design exercise.

## Sources & status

- **Repo**: `ocha-dap/ds-cmr-flooding-support`, active branch `jan-2025-analysis` @ `6f0cddf`. All substantive work lives under `exploration/` (jupytext `.md` notebooks) plus reusable data-loading helpers in `src/datasources/`.
- **Data**: SEAS5 (ECMWF seasonal forecast, read both from local GRIB/blob COGs and from the prod DB `public.seas5` table), ERA5 reanalysis (prod DB), FloodScan SFED flood extent (historical NetCDF extract 1998–2023, plus live daily exposure rasters/DB rows from the `floodexposure-monitoring` pipeline), WorldPop 2020 1km population, IRI seasonal outlook, EM-DAT (project-local Cameroon extract + the team's global EM-DAT parquet), OCHA impact assessments for the 2022 (`cmr_exno_data_inondationlc_md_mt_v1.0_20221206.xlsx`) and 2024 (`cmr_ocha_data_Inondation_2024_20240915.xlsx`) floods, CODAB admin boundaries, LCB watershed shapefiles, and Copernicus EMS (CEMS) rapid-mapping shapefiles for activation EMSR772. Most of these (SEAS5 GRIB, EM-DAT excerpt, OCHA impact files, WorldPop raster) are **frozen local extracts** under `AA_DATA_DIR_NEW` with no refresh mechanism; only the FloodScan exposure inputs and the DB-hosted SEAS5/ERA5 stats stay current because they're fed by other live pipelines (`floodexposure-monitoring`, `raster-pipelines`).
- **Completeness**: exploration-complete for 2024 (four seasonal re-estimates through the flood season plus an EM-DAT/CEMS/skill validation pass), but nothing was packaged into a reusable script, dashboard, or monitoring job. The `jan_2025.md` notebook (last commit on the checked-out branch) is a half-finished start on the 2025 season — it computes ranks/percentiles but stops before the impact-estimate step the earlier notebooks completed.
- **Status**: `dormant`. No commits or notebook updates since the `jan_2025.md` work (branch `jan-2025-analysis`); no schedule, no deployment, no entry in `infrastructure/deployments.md` or `infrastructure/pipeline-registry.md`. Revive by continuing `jan_2025.md` through the impact-estimate step if a similar ad-hoc estimate is needed again, or by pointing at `floodexposure-monitoring`'s live exposure/quantile tables directly instead of re-deriving them from scratch.
