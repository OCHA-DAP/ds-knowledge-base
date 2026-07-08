---
content_type: analysis
name: som-risk-analysis-support
analysis_type: exploratory
status: active
country_iso3: SOM
hazard: [drought, flood, cholera, conflict]
summary: "Recurring ad-hoc R analysis (ACLED conflict, cholera, FloodScan flood exposure, SEAS5 drought) that CHD reruns each cycle to support Somalia's annual HNO/HRP risk-analysis section; no published framework, no schedule, no deployment."
data_sources: [ACLED, SEAS5, FloodScan, WorldPop, CHIRPS, ECMWF, IRI-seasonal-forecast, PRMN]
feeds: []
source_repo: ocha-dap/ds-som-risk-analysis-support
source_branch: init-flood-drought
source_sha: 07cfa70
code_ref:
  - README.md
  - _targets.R
  - R/tar_flood_exposure.R
  - analysis/06_seas5_comparison.R
  - analysis/01c_Conflict_ACLED_slides_update2026_HNRP.Rmd
  - analysis/05_analysis_PRMN_Investigate.Rmd
  - exploration/FloodRiskMethodologyTar.qmd
depends_on: [public.seas5]
discrepancies:
  - "[gap] Cholera is listed in the README as one of four current risk themes, but the repo itself notes 'no cholera data received for 2026 update' and the only cholera code (02/02b) is frozen at the 2022-vs-2023 comparison built for the 2024 HNRP — the theme is stale in practice, not live."
  - "[stale] The flood-exposure `{targets}` pipeline (_targets.R / R/tar_flood_exposure.R) reads a frozen FloodScan flooded-fraction extract that ends 2022-12-31 and a 2020-vintage WorldPop raster; it was built for the 2024 HNRP cycle and has not been rerun with newer inputs since."
  - "[gap] README TBD: the pre-2025 ACLED scripts (01, 01b) broke when ACLED changed its API/auth; only the 2026 update script (01c, OAuth-based) is confirmed working, and it's unverified whether re-running it reproduces the older charts' numbers."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Somalia Risk Analysis Support — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-som-risk-analysis-support` is CHD's working repo of R scripts and R Markdown notebooks used to produce the risk-analysis inputs (charts, maps, tables, slide decks) for Somalia's annual OCHA Humanitarian Needs Overview / Humanitarian Response Plan (HNO/HRP, later HNRP) report. It has been re-run, by hand, once per reporting cycle since a late-2022 in-country risk-analysis workshop fed the 2023 HNO (p.50–57): 2023→2024 HNRP (late 2023), a "light" 2025 HNRP update (late 2024), and a 2026 HNRP update (November 2025, on this branch). There is no published AA framework behind any of this, no schedule/CI (everything is knit or sourced manually), and no deployed app or monitoring job — outputs are pasted into a Google Slides deck and the HNRP report text, which is why this stays `analysis` rather than a `framework` or `pipeline`.

## What was analyzed / findings

Four recurring themes, of very different currency as of the 2026 (Nov 2025) update:

- **Conflict (ACLED)** — `analysis/01_*`→`01c_*`. Compares fatalities and conflict type year-over-year (2022 vs 2023, then rolled forward to 2025/2026), and maps admin1 violence using the *report's own* groupings for two separate risk scores (non-international armed conflict/Al-Shabaab vs inter-clan violence) since neither grouping is a COD boundary. The 2026 script (`01c`) switches ACLED ingestion from the old API key to OAuth (`ACLED_USER_EMAIL`/`ACLED_PASSWORD`) after ACLED changed its authentication; `01`/`01b` are the pre-change versions and are not confirmed to still run.
- **Cholera** — `analysis/02_*`, `02b_*`. National and admin1 case-count comparisons (2022 vs 2023: dumbbell charts, bar charts, choropleth maps) built once for the 2024 HNRP. No new cholera line-list data has been received since, so the 2025 and 2026 updates carried this theme in name only.
- **Flood exposure** — `_targets.R` / `R/tar_flood_exposure.R`, explored in `exploration/05_exp_floodscan.Rmd`, `06_exp_floodscan_short.Rmd`, `FloodRiskMethodologyTar.qmd`. A `{targets}` pipeline intersects a FloodScan flooded-fraction raster (Africa-wide extract, 1998–2022) with a WorldPop 2020 population raster and OCHA population/PIN spreadsheets, at admin1/admin2. For each MAM/OND season it takes the seasonal-max flood fraction per pixel, masks it against a threshold (two methods implemented: a fixed low threshold of 0.005 flood-fraction, or a fixed/sweep of higher thresholds around 0.2), multiplies by population to get people exposed, and aggregates to admin1/2. Historical (1998–2022) percentiles of % population exposed are then used per admin1 as a "normal range" band (50th–95th percentile for MAM, 25th–75th for OND) to flag whether a given season's exposure looks anomalous. This was the core deliverable for the 2024 HNRP cycle; it has not been rerun since (the FloodScan extract stops at end-2022).
- **Flood displacement** — `analysis/05_analysis_PRMN_Investigate.Rmd`. Exploratory look at IOM PRMN (population/return movement) flood-displacement time series by admin1 and by the report's north/south regional groupings, plus a rainfall-anomaly-vs-displacement comparison and top-20-district ranking. Feeds narrative, not a defined indicator or threshold.
- **Drought / seasonal rainfall** — three successive approaches, most recent is the live one:
  - `analysis/03_analysis_IRI_seasonal.Rmd` — maps IRI's seasonal forecast dominant-tercile probability (OND, MAM, FMA), used in the earlier cycles.
  - `analysis/04_analysis_ECMWF.Rmd` — ranks admin1 units by Jan–Feb–Mar 2024 rainfall using manually downloaded ECMWF seasonal forecast rasters (a noted CDS-API-vs-manual-download product discrepancy had to be worked around).
  - `analysis/06_seas5_comparison.R` — the current approach (flagged in the README as a "key updated script (2025)"). Connects read-only to the **prod** Postgres DB (`cumulus::pg_con(stage="prod")`) and queries the `seas5` table for Somalia at admin1. For the Gu (Mar–May) season it sums forecast monthly rainfall by issue month, computes cumulative and per-month anomalies against the historical mean, and computes an empirical return period per admin1/month (`rp = 1 / (rank/(n+1))`, direction flipped for drought framing) to rank which regions have the rarest rainfall deficits. No formal go/no-go threshold is set — it's used to rank/flag the driest regions for the narrative, not to trigger anything. Its plots (`p_cumulative_individual_months`, `p_monthly_anomaly`, `map_rp_binned`) were used directly in the "Somalia Risk Analysis Support Update 2026 HNRP" slide deck (Nov 2025).

## Relation to frameworks

Standalone (`feeds: []`). The closest KB neighbour is [`frameworks/som-drought/2019`](../frameworks/som-drought/2019.md) — the retired 2019 CERF drought pilot for Somalia — but this repo is not that framework's supporting analysis: it implements no trigger, sets no threshold, and nothing in it is read by a deployed monitoring job. It exists solely to produce narrative and figures for the annual Somalia HNO/HRP risk-analysis section (covering conflict, cholera, flood, and drought together as a general risk overview), and its outputs land in a slide deck and the HNRP report text — both outside anything else this KB tracks. If Somalia's drought or flood risk work is ever formalised into a new CERF AA framework, this repo (particularly the flood-exposure percentile method and the SEAS5 return-period method) is the most likely pre-framework exploration to draw on.

## Sources & status

Repo `ocha-dap/ds-som-risk-analysis-support`, active branch **`init-flood-drought`** @ `07cfa70` (per this ingestion; the repo's default branch was not compared). R project managed with `renv`-free `box::use()` imports per script; the `{targets}` flood-exposure pipeline is invoked via `run.R`/`run.sh` (`targets::tar_make()`), everything else is a manually-knit Rmd or sourced `.R` script — there is no CI, no cron, and no Azure/GH Pages deployment. Status is **active** in the sense that CHD reruns parts of it every HNO/HRP cycle (most recently for the 2026 HNRP, Nov 2025) — but individual themes are frozen between cycles and two of the four (cholera, flood exposure) haven't had new source data since 2023/2024 respectively. Completeness is uneven: conflict (ACLED) and drought (SEAS5) have live, actively-maintained scripts as of the 2026 cycle; cholera and flood exposure are dormant sub-analyses carried for continuity. The repo's own README documents the timeline and a Python-only-for-one-off-IRI-download note (Python can otherwise be ignored).
