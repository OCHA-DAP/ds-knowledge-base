---
content_type: analysis
name: aa-drought-indicators
analysis_type: exploratory
status: one-off
country_iso3: [AFG, BFA, ETH, KEN, GTM, HND, SLV, MRT, NER, TCD]
hazard: drought
summary: "Cross-country backtest (2001-2024) of temperature, rainfall, water-balance and vegetation indicators against drought impact (FAOSTAT staple production, CERF-dated drought seasons, EM-DAT events) across the ten OCHA drought-AA countries; finds detrended growing-season temperature out-predicts the ASAP biomass anomaly Burkina Faso's observational trigger keys on (pooled leave-one-out R² 0.13 vs 0.02) and recommends adding it to the candidate set alongside FAO's ASI."
data_sources: [JRC-ASAP, CHIRPS, ERA5, FAO-ASI, FAO-VHI, FAOSTAT, CERF, EM-DAT]
feeds: [afg-drought, bfa-drought, eth-drought, ken-drought, lac-dry-corridor, mrt-drought, ner-drought, tcd-drought]
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-drought-indicators/", kind: landing, title: "Drought AA indicators"}
  - {url: "https://ocha-dap.github.io/ds-aa-drought-indicators/indicators-vs-impact/", kind: report, title: "Do temperature, rainfall and vegetation indicators predict drought impact?"}
  - {url: "https://ocha-dap.github.io/ds-aa-drought-indicators/robustness/", title: "Robustness of the temperature finding", auto: true, first_seen: 2026-09-19}
# --- source repo ---
source_repo: ocha-dap/ds-aa-drought-indicators
source_branch: main
source_sha: cafd399
code_ref:
  - "scripts/fetch_asap.sh, scripts/fetch_asis.sh — raw pulls (JRC ASAP per-admin export, FAO GIEWS ASIS)"
  - "scripts/build_tables.py — per-country season tables: indicators + production/CERF/EM-DAT impact targets"
  - "scripts/analyse.py — per-country and pooled OLS/leave-one-out-R²/AUC regressions"
  - "scripts/make_site.py — renders pages/ (landing + indicators-vs-impact report + one page per country)"
  - "data/config/countries.json — per-country seasons, AOI, staples, framework-documented bad years"
depends_on: [raster-stats, cerf-supplement, emdat, jrc-asap, fao-asi-vhi]
discrepancies:
  - "[conflict] The published report's caveats state that prod Postgres `public.era5_temp` was checked as a cross-reference for Ethiopia temperature and 'turned out to hold precipitation-like values', so it was dropped in favour of ASAP's own ECMWF-reanalysis temperature series. The table does exist (`infrastructure/db-schema.md`: 60.5k rows prod, 39.2k dev, same 11-column zonal-stats schema as `public.era5`), but `pipelines/raster-stats.md` documents only `public.era5`/`seas5`/`imerg`/`floodscan` as this pipeline's output tables and never mentions `era5_temp` — its writer, purpose and correctness are undocumented anywhere in the KB. NOTE: the finding is asserted only in the report prose; no `era5_temp` query or check survives in the repo's committed code (repo-wide grep at `cafd399` returns nothing), so the values themselves are not independently re-checkable from this repo."
  - "[conflict] The report describes ASAP's zFPARc biomass anomaly as 'the indicator Burkina Faso and Chad trigger on' / 'two of our frameworks trigger on'. That holds for Burkina Faso (`frameworks/bfa-drought/2026-04-17.md` Trigger 2 = JRC ASAP Level-3 crop-or-rangeland alert), but NOT for Chad: `frameworks/tcd-drought/2025-03-03.md` Window 3 keys on **ACF/GeoSahel DMP** cumulative biomass (trend-adjusted anomaly < 84.5% at dekad 24), a different product from a different provider. The report's own country table says 'GeoSahel biomass' for Chad, so the summary line contradicts its own body. The backtest result still bears on Chad's design, but the tested series is not Chad's trigger input."
  - "[conflict] The report states Ethiopia's binary target is saturated because 'CERF has responded to drought in 15 of 24 seasons'. The committed results give ETH `impact` (CERF allocation OR EM-DAT event) n_pos = 15 and `impact_cerf` n_pos = 12 (`data/processed/results.json`); 15 is the combined target, not CERF alone. The saturation conclusion is unaffected."
  - "[gap] FAOSTAT (bulk `Production_Crops_Livestock_E_All_Data_(Normalized)`, pulled Dec 2025) has no `infrastructure/datasets/` page — it is fetched directly by this repo with no team-owned loader. `frameworks/bfa-drought/2026-04-17.md` already leans on a FAOSTAT-based analysis, so the promote-on-second-duplication trigger in docs/INGESTION.md is arguably met; a stub is worth opening."
  - "[gap] `infrastructure/datasets/jrc-asap.md` and `fao-asi-vhi.md` do not list this page under `used_by` (out of scope for this page's own edit)."
extra: {}
visibility: public
last_synced: "2026-09-18"
---

# Drought AA indicators — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

A cross-country backtest asking whether the observable indicators behind OCHA's drought
anticipatory-action triggers — and a few they don't use — actually predict drought **impact**.
For each of the ten countries with an endorsed or in-development OCHA drought framework
(Afghanistan, Burkina Faso, Chad, El Salvador, Ethiopia, Guatemala, Honduras, Kenya, Mauritania,
Niger — the KB's three other drought frameworks, Malawi, Nicaragua and Somalia, are `retired` and
out of scope), it regresses eight indicators (detrended growing-season temperature, ASAP's
cumulative-FPAR biomass anomaly zFPARc, ASAP/CHIRPS rainfall, ERA5 rainfall, water-satisfaction
index, SPI-3, FAO's Agricultural Stress Index, FAO mean VHI) against national staple production
and against drought-impact seasons (CERF drought allocations dated to their rainfall-deficit
period, EM-DAT events), 2001-2024. It is not a framework — there is no published framework doc,
no trigger, no monitoring window — and not a living pipeline: it is a one-time, cross-country
methods study built to inform trigger design **across the portfolio** rather than deliver an
operational output for any one country. It grew directly out of a country-level finding in
`ds-aa-bfa-drought` (Sept 2026) that growing-season temperature explained Burkina Faso's
cereal-production shortfalls and CERF seasons better than the ASAP biomass anomaly Burkina Faso's
Trigger 2 actually keys on (recorded on
[`bfa-drought/2026-04-17`](../frameworks/bfa-drought/2026-04-17.md)); this repo generalises that
question to the whole drought portfolio.

## What was analyzed / findings

**Method.** Per country and main growing season: indicator means over the season (biomass, WSI
and SPI-3 over the last 60% of the window, where trigger checks sit), aggregated over both the
framework area of interest and the national mean of ASAP units; temperature detrended per ASAP
unit with a Theil-Sen slope (1991-2025), biomass per unit (2001-2025), so "hot"/"low-biomass"
means relative to that year's expected value, not a raw level. Targets: national staple
production as a % departure from a 2001-2024 linear trend (continuous), and growing seasons with
a CERF drought allocation (dated to the season by `ds-cerf-supplement`'s rainfall-deficit period)
or an EM-DAT drought event (binary; the two are OR-ed into one `impact` target, with CERF-only and
EM-DAT-only variants kept alongside). Statistics: OLS on standardised predictors with
leave-one-out R² (the honest number at n=24 seasons/country), AUC for the binary target, and a
pooled regression across all ten countries — **national scope only** — with every series
standardised within-country (240 country-seasons) so only year-to-year variation is compared.

**Cross-country findings** (pooled, leave-one-out R² against production, out of a possible 1.0):

| Indicator | pooled LOO R² | notes |
|---|--:|---|
| FAO Agricultural Stress Index (% cropland stressed) | 0.14 | best single indicator |
| Detrended temperature | 0.13 | not used by any framework as a trigger input |
| FAO mean VHI | 0.13 | |
| ERA5 rainfall | 0.09 | |
| SPI-3 | 0.09 | |
| Water balance (WSI) | 0.09 | |
| CHIRPS/ASAP rainfall | 0.06 | |
| ASAP zFPARc biomass anomaly | 0.02 | **the biomass family Burkina Faso's observational trigger keys on** (ASAP Level-3 alert); LOO-negative in 8 of 10 countries |

Temperature + ASI together reach a pooled LOO R² of 0.19 with both coefficients staying
significant — they carry different information rather than proxying the same signal.

- **Where the weather explains the harvest at all, temperature is at or near the top** (national
  LOO R² against production): Mauritania 0.54 (second only to ERA5 rainfall at 0.55), Afghanistan
  0.38 (but FAO ASI 0.54, mean VHI 0.51 and SPI-3 0.45 all beat it there), Burkina Faso 0.23 and
  Niger 0.11 — its own best indicator in the last two. In these four, hot seasons are the poor
  harvests and, where the impact record is sparse enough to test, the CERF/EM-DAT seasons too
  (temperature AUC 0.72-0.80 in Burkina Faso, Niger, Chad, Afghanistan).
- **ASAP's biomass anomaly is the weakest indicator almost everywhere** — pooled LOO R² 0.02,
  LOO-negative in 8/10 countries (positive only in Mauritania, 0.39, and marginally Honduras,
  0.01). Its FAO cousin, ASI, does much better on the pooled view, plausibly because ASI counts
  the *share of cropland under stress* rather than averaging a z-score with a strong greening
  trend baked in — though ASI is itself badly unstable in a few countries (Mauritania LOO −1.03,
  El Salvador −2.66).
- **Rainfall underperforms both heat and vegetation health** except in Kenya, where ERA5 rainfall
  over the long rains is the best indicator and temperature adds little — Kenya's maize is grown
  in the highlands, not the arid counties the framework AOI targets.
- **Nothing works in Ethiopia or the Central American Dry Corridor.** Ethiopia's national cereal
  production is a smooth growth curve dominated by highland Meher policy and area expansion, with
  no relation to any indicator (every LOO R² negative); 15 of 24 Ethiopian seasons also carry a
  drought impact record (12 a CERF drought allocation, 9 an EM-DAT event), saturating the binary
  target. Guatemala/Honduras/El Salvador produce most of their maize outside
  the Dry Corridor departments the framework targets, so framework-area indicators show no
  relation to national production — a scale-mismatch problem the study flags as needing
  subnational production data to resolve, not a finding that the indicators themselves fail there.

**Recommendation for trigger design**: add a detrended growing-season temperature anomaly to the
candidate set for every drought framework's observational window, alongside ASI/VHI — it updates
on the same cadence as the vegetation indices (ASAP, every dekad), needs no new data agreement,
and in the Sahel is the single indicator most tied to outcomes. Where a framework's observational
window rests on a biomass anomaly alone — Burkina Faso (ASAP Level-3) and Chad (ACF/GeoSahel DMP,
a different product but the same indicator family) — the backtest against real outcomes should be
re-run with temperature and ASI as alternatives before the next revision. Temperature does not
*lead* in-season (it coincides with dry spells rather than preceding them, per the Burkina Faso
dekadal analysis), so this is an observational-window indicator, not a forecast-window one — a
separate test of seasonal temperature *forecasts* is flagged as worth doing.

**Caveats** (the KB-relevant ones are in `discrepancies`): national production vs.
framework-area indicators is a scale mismatch, worst where the framework area is a small share of
national production (Ethiopia, Kenya, Central America); FAOSTAT production carries reporting
noise and in places is itself partly weather-estimated; single-country p-values are indicative
only at n=24, the pooled regression and leave-one-out R² are what to trust; impact-season dating
rules (CERF-period overlap vs. last-season-before-EM-DAT-event) move a few seasons by one year
under a different convention.

## Relation to frameworks

Feeds trigger-design reconsideration for all eight OCHA drought frameworks whose countries it
covers: [`afg-drought`](../frameworks/afg-drought/2026-04-04.md),
[`bfa-drought`](../frameworks/bfa-drought/2026-04-17.md),
[`eth-drought`](../frameworks/eth-drought/2026-06-09.md) (in development),
[`ken-drought`](../frameworks/ken-drought/2023-02-19.md) (in development — OCHA's trigger; the
*operational* Kenya framework is IFRC/KRCS's EAP2022KE02, not ours),
[`lac-dry-corridor`](../frameworks/lac-dry-corridor/2026-03-13.md) (covers GTM/HND/SLV),
[`mrt-drought`](../frameworks/mrt-drought/2026-04-17.md),
[`ner-drought`](../frameworks/ner-drought/2026-06-03.md) (in development), and
[`tcd-drought`](../frameworks/tcd-drought/2025-03-03.md). It does not pre-figure a new framework
and is not itself a candidate framework — it is a comparative methods layer sitting above the
existing portfolio, explicitly "built to inform trigger design across the portfolio rather than
one country at a time." Its closest KB neighbour is
[`asap-indicator-trends`](asap-indicator-trends.md) (same JRC ASAP export, same
"is the indicator behind our triggers actually reliable" question, but about temporal drift in
the warning threshold rather than cross-sectional predictive power against impact); the two are
complementary reads on ASAP's biomass indicator, from opposite angles. The Burkina Faso
country-level analysis that started this (`ds-aa-bfa-drought`, `heat-and-impact/`) is linked from
this repo's landing page but lives outside it as a repo-level finding on the `bfa-drought`
framework's own site.

## Sources & status

**Repo**: [`OCHA-DAP/ds-aa-drought-indicators`](https://github.com/OCHA-DAP/ds-aa-drought-indicators),
branch `main` @ `cafd399`. **Completeness: full** — this is not a stub; `build_tables.py` →
`analyse.py` → `make_site.py` is a complete, runnable pipeline from raw pulls to a published
report, with results committed (`data/processed/results.json`, `summary_table.csv`) and a live
GitHub Pages site (`.github/workflows/deploy-pages.yml`) covering a landing page, the
cross-country report, and one page per country with its impact-dating table.

**Status: one-off.** Published 18 September 2026 as a completed cross-country study, not a
refreshed pipeline — there is no schedule beyond the GH Pages deploy-on-push, and every input is
a frozen extract: JRC ASAP pulled September 2026, FAOSTAT bulk file from December 2025, CERF/
EM-DAT as of the repo's one build. Re-running it with new seasons requires re-pulling the raw
sources by hand (`scripts/fetch_asap.sh` / `fetch_asis.sh`) — nothing here refreshes on its own.

**Data**: [JRC ASAP](../infrastructure/datasets/jrc-asap.md) per-admin indicator export —
temperature (ECMWF reanalysis, cropland), rainfall (CHIRPS), SPI-3, WSI, and zFPARc taken as the
mean of the cropland and rangeland series — via `scripts/fetch_asap.sh` (gotcha: ASAP's
`country_id` is the country's rank in ASAP's full GAUL0 list, not its `asap0_id`, recorded in
`data/config/asap_ids.json`); team prod Postgres
`public.era5` monthly precipitation zonal stats ([`raster-stats`](../pipelines/raster-stats.md));
[FAO GIEWS ASIS](../infrastructure/datasets/fao-asi-vhi.md) country CSV endpoints (ASI, mean VHI —
`scripts/fetch_asis.sh`, admin-1); FAOSTAT bulk
production file (staples per country, no team loader); CERF drought allocations from the dev
Postgres `aa.cerf_allocation` ⋈ `aa.cerf_supplement` mirror
([`cerf-supplement`](../pipelines/cerf-supplement.md)); EM-DAT drought events via the team blob
snapshot ([`emdat`](../infrastructure/datasets/emdat.md), `ocha_stratus.emdat`). Framework areas
and seasons for all ten countries are hand-curated in `data/config/countries.json`, sourced from
this KB.
