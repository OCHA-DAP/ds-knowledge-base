---
content_type: analysis
name: adhoc-aa-cuba
analysis_type: pre-framework
status: dormant
country_iso3: CUB
hazard: tropical-cyclone
summary: "Frozen 2024 exploration of historical cyclone windspeed/distance-to-landfall and CHIRPS rainfall for Cuba, ahead of the dedicated cub-hurricanes framework repo"
data_sources: [IBTrACS, CHIRPS, GAUL-ASAP]
feeds: [cub-hurricanes]
# --- source repo ---
source_repo: ocha-dap/ds-adhoc-aa-cuba
source_branch: main
source_sha: c6d074b
code_ref:
  - exploration/01_windspeed_dist_rainfall.R
  - data-raw/cuba_ibtracs_windspeed_distance.R
  - data-raw/cuba_adm0_chirps.R
  - R/utils.R
depends_on: []
discrepancies:
  - "[gap] exploration/01_windspeed_dist_rainfall.R ends mid-analysis: an unfinished ggplot call is followed by a dangling pipe into an undefined-purpose example function (`ex_func`) that just tags rows with a literal string — no plot, threshold, or conclusion is actually produced."
  - "[stale] data-raw/cuba_ibtracs_windspeed_distance.R has a typo (`AUL0_PATH` instead of `GAUL0_PATH`) that would raise an undefined-object error if re-run as-is — consistent with the repo being a frozen, never-cleaned-up scratch script rather than a maintained pipeline."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Cuba hurricanes — ad-hoc windspeed/rainfall exploration — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-adhoc-aa-cuba` is a small, single-purpose R scratch repo (no README, no package structure beyond an `.Rproj` and one `R/utils.R` helper) that pulls historical tropical-cyclone track data and CHIRPS rainfall for Cuba to eyeball the relationship between a storm's windspeed/distance-to-landfall and observed rainfall. It is not a framework because there is no published framework document behind it and no endorsed trigger — it is pre-analysis scratch work, done independently of (and earlier than) the dedicated `ocha-dap/ds-aa-cub-hurricanes` repo that now holds the endorsed [cub-hurricanes](../frameworks/cub-hurricanes/2025-08-26.md) framework and its [2026 wind-exposure redesign](../frameworks/cub-hurricanes/2026-06-17.md). It is not a living pipeline either: there is no scheduling, no `CLAUDE.md`, and the one data-staging script (`cuba_adm0_chirps.R`) writes a date-stamped CSV by hand rather than running on any cadence.

## What was analyzed / findings

The core script, `exploration/01_windspeed_dist_rainfall.R`, loads a frozen CHIRPS daily rainfall extract for Cuba (`20240524_chirps_daily_historical_cuba.csv`, admin-0 mean) and IBTrACS storm tracks + a precomputed all-country distance-to-admin0 table, filters to storms passing near Cuba (GAUL/ASAP `asap0_id` for "Cuba"), restricts to the CHIRPS extract's date range, and identifies storms that made landfall (`dist == 0`) to isolate their track history. A companion script, `data-raw/cuba_ibtracs_windspeed_distance.R`, does the same IBTrACS/GAUL join independently (filtering to distances `<300000` m and dates `>= 2000-01-01`), and was clearly meant to summarise minimum distance vs. maximum WMO windspeed per storm and scatter-plot the two (`geom_point()`), writing the joined table out to `cuba_ibtracs_windspeed_distance.csv`.

**No conclusion is reached in either script.** `01_windspeed_dist_rainfall.R` breaks off after computing a 2-day rolling rainfall sum (`rollsumr(..., k = 2)`, result discarded) and the landfall-storm filter — the intended `ggplot()` call is empty (`aes()`, no mapped variables) and the block below it is dead/exploratory code (a `dangling` pipe into an undefined-purpose `ex_func` that just stamps rows with a literal `"string"`). No threshold, correlation, or candidate trigger value is ever computed or stated. This is scratch/in-progress code, not a finished analysis — see `discrepancies`.

## Relation to frameworks

`feeds: [cub-hurricanes]`. This repo pre-figures the same country+hazard combination that became the endorsed [cub-hurricanes 2025-08-26](../frameworks/cub-hurricanes/2025-08-26.md) framework (NHC windspeed-in-ZMA-buffer + IMERG rainfall) and its [2026-06-17 wind-exposure redesign](../frameworks/cub-hurricanes/2026-06-17.md) (NHC wind buffers × GHSL population, OR'd with IMERG rainfall) — both combine a wind/track indicator with a rainfall indicator, the same pairing explored here with IBTrACS windspeed/distance and CHIRPS rainfall. There is no code-level evidence (commit messages, comments, shared functions) directly linking this repo to `ocha-dap/ds-aa-cub-hurricanes`; the connection is inferred from subject matter and timing (this repo's data was frozen 2024-05-30, before the 2025-08-26 framework doc). Treat it as an early, independent scratch exploration of the same question rather than a confirmed input to the framework's actual derivation.

## Sources & status

- **Repo**: `ocha-dap/ds-adhoc-aa-cuba`, branch `main` @ `c6d074b`. No commits/activity since the frozen CHIRPS extract date of 2024-05-30 (per `docs/repo-manifest.md`) — **dormant**.
- **Data staged, not refreshed**: `data-raw/cuba_adm0_chirps.R` pulls CHIRPS daily (UCSB-CHG/CHIRPS/DAILY via `rgee`/Google Earth Engine, admin-0 mean over a convex-hull-simplified Cuba boundary from GAUL/ASAP `gaul0_asap_v04`) and writes a date-stamped CSV (`20240524_chirps_daily_historical_cuba.csv`) — a one-time historical extract, not a scheduled refresh. `data-raw/cuba_ibtracs_windspeed_distance.R` and the exploration script read IBTrACS tracks (`ibtracs_with_wmo_wind.parquet`) and a precomputed global admin0-distance table (`all_adm0_distances.parquet`) from a blob path (`AA_DATA_DIR_NEW/public/processed/glb/ibtracs`) — these are shared, externally-produced extracts (not something this repo builds), read as static files rather than via the live `storms-pipeline` DB tables.
- **Code completeness**: partial/stub. `R/utils.R` is a single unfinished-roxygen helper (`load_proj_paths()`) hard-coding the CHIRPS extract filename; `exploration/01_windspeed_dist_rainfall.R` ends mid-analysis with dead code; `data-raw/cuba_ibtracs_windspeed_distance.R` contains a typo (`AUL0_PATH` vs `GAUL0_PATH`) that would break a re-run. No README documents intent or how to run these scripts.
- **Status**: dormant, one-off exploration superseded in practice by the dedicated `ds-aa-cub-hurricanes` framework repo, which independently carries the live Cuba hurricanes trigger design forward.
