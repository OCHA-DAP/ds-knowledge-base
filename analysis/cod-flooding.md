---
content_type: analysis
analysis_type: exploratory   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: cod-flooding
version: dec-seasonal  # no published doc — branch name per template convention
status: development
country_iso3: COD
hazard: flood
admin_level: 1
geographic_scope:
  - CD61  # Nord-Kivu
  - CD62  # Sud-Kivu
  - CD74  # Tanganyika
  - CD52  # Bas-Uele
  - CD53  # Haut-Uele
  - CD51  # Tshopo
data_sources:
  - SEAS5
  - ERA5
  - Floodscan
trigger_facets:
  basis: mixed
  calibration: return-period
  indicators: [SEAS5-precip-tercile, ERA5-precip-tercile]
  n_windows: 3
  window_axes: [space]
supersedes: null
# --- funding & scope ---

prearranged_funding_usd:
funding_by_source: {}
cofinancing_usd:
cofinancing_sources: []
implementing_agencies: []
target_people:
# --- documents, authority-ranked ---
framework_doc: null
framework_doc_date: null
framework_doc_annexes: []
languages: [fr]
model_report: null
raw_extract: []   # not persisted to repo — raw source is the framework_doc PDF(s) above (re-extract from there)
# --- live system ---
operated_by: null
apps: []
# --- source repo & reconciliation ---
depends_on: []
source_repo: ocha-dap/ds-aa-cod-flooding
source_branch: dec-seasonal
source_sha: 93aae59
code_ref:
  - exploration/seas5.md
  - exploration/era5.md
  - exploration/exposure.md
  - src/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No published framework PDF exists for DRC floods — OCHA's AA portal (unocha.org/anticipatory-action) lists DRC only under cholera. Both candidate pages supplied (2025-action-anticipatoire and anticipatory-action-democratic-republic-congo) attach cholera PDFs, not flood PDFs. trigger_source is therefore repo, not framework_doc."
  - "[gap] The 'dec-seasonal' branch name implies a December-issued seasonal forecast trigger, but the branch contains no formalized trigger logic — only exploratory notebooks. There is no threshold decision, return-period cutoff, or activation rule coded up."
  - "[gap] ERA5 analysis covers November (observational) and SEAS5 covers December-issued forecasts valid for Dec–Jan, but the two are not combined into a single trigger decision rule. The relationship between the observational and forecast signals is unresolved in the code."
  - "[gap] Floodscan exposure analysis (exploration/exposure.md) loads from app.floodscan_exposure and app.floodscan_exposure_regions using the dev DB — it appears to be assessing impact thresholds (Q1/Q2/Q3 population exposure) but these are not yet wired into a trigger decision."
  - "[gap] Province coverage in exposure analysis (exposure.md) is slightly wider than AOI: KINSHASA1 (CD10) and EQUATEUR1 (CD41) appear in individual plots but are not in AOI_ADM1_PCODES or ZONES. Their role in a potential trigger is undefined."
  - "[conflict] The three-zone structure (Zone 1: Bas-Uele/Haut-Uele/Tshopo; Zone 2: Nord-Kivu/Sud-Kivu; Zone 3: Tanganyika) is defined in constants and used in exposure analysis, but SEAS5 and ERA5 notebooks loop over individual provinces, not zones. Whether windows fire per-zone or per-province is not settled."
  - "[gap] No pipeline, GitHub Actions workflow, or deployed app exists. All work is in Jupyter/Marimo-style exploration notebooks on the dec-seasonal branch. Main branch contains only the initial scaffold (commit 3f85b23)."
  - "[conflict] DB connections in exploration/exposure.md use stage=\"dev\" (db_utils.get_engine(stage=\"dev\"), pointing at chd-rasterstats-dev), whereas the production default is stage=\"prod\" (chd-rasterstats-prod). The exposure analysis runs against the dev DB slot and has not been promoted to production data."
  - "[conflict] Window/zone granularity is contradicted within the repo: the page's 3-window table is built on the three ZONES in constants.py, but the SEAS5 and ERA5 notebooks (seas5.md, era5.md) loop over individual provinces (AOI_ADM1_PCODES), computing terciles and return periods per province — only exposure.md aggregates by ZONE. So the precip indicators that would drive a trigger are calibrated per-province, not per-zone, directly undercutting the per-zone window structure. n_windows=3 is an inference from the zone grouping, not a codified trigger."
  - "[conflict] Calibration granularity is inconsistent across indicators: the SEAS5 and ERA5 precipitation analyses use TERCILES (upper/middle/lower, 1/3 and 2/3 quantiles), while the Floodscan exposure analysis uses QUARTILES (Q1/Q2/Q3 at 1/4, 2/4, 3/4). The \"above-normal = upper tercile\" signal and the impact thresholds are therefore on different statistical footings, and no rule reconciles them."
  - "[stale] Hardcoded analysis year: seas5.md, era5.md, and exposure.md all hardcode the current year as 2024 (e.g. `.loc[2024, \"mean\"]`, `right_edge = 2024 + 0.99`). This is a stale constant — the notebooks would raise KeyError if re-run for any other year and do not roll forward automatically."
  - "[gap] Floodscan region coverage is incomplete/asymmetric: exposure.md queries app.floodscan_exposure_regions for region_number = 1 and region_number = 3 only; region_number = 2 is never queried, despite three ZONES being defined. The mapping between Floodscan \"regions\" and the three constants.py zones, and the omission of region 2, is unexplained."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "n_windows=3 is an estimate based on the 3 spatial zones in constants.py; no trigger logic explicitly defines 3 windows. window_axes=[space] because the primary differentiator is which zone fires, not a time dimension. status=development reflects that analysis is underway but no framework document has been published or endorsed."
visibility: internal
last_synced: 2026-06-15
---

# DRC Flood — dec-seasonal

> **Analysis, not a framework** (reclassified 2026-06-17): repo-only exploration; no published framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> No published framework document exists. Trigger taken from repo (dec-seasonal branch, SHA 93aae59). This page is explicitly not authoritative — it summarises the development-stage analysis, not an endorsed trigger.

## Summary

An anticipatory action framework for seasonal flooding in the Democratic Republic of Congo (DRC) is in early development. Analysis focuses on six eastern and north-central provinces (Nord-Kivu, Sud-Kivu, Tanganyika, Bas-Uele, Haut-Uele, Tshopo), grouped into three zones. The approach combines December-issued SEAS5 seasonal precipitation forecasts (valid December–January) with ERA5 November observations and Floodscan historical exposure data to assess whether a trigger could be feasibly constructed. No activation rule has been formalised, no framework PDF has been published, and no pipeline or app has been deployed.

## Method

Data flows through three parallel exploratory analyses, none yet combined into a single decision rule:

1. **SEAS5 forecast**: December-issued forecasts (from the `public.seas5` DB table) for December–January precipitation are extracted at ADM1 level for the six provinces. The ensemble mean daily precipitation (mm) is aggregated spatially per province and ranked against the historical record (2000–2024) to compute a return period. The upper tercile (67th percentile) is used as a reference level; the analysis plots return-period maps with breakpoints at 1, 2, 3, 5, 10, and 20 years.

2. **ERA5 observation**: November mean daily precipitation per province is extracted (from `public.era5`) and plotted against the historical distribution. The upper tercile serves as a visual threshold. This appears intended as a real-time observation cross-check for the seasonal forecast, but the two are not yet combined.

3. **Floodscan exposure**: Daily flood-exposed population (`app.floodscan_exposure`) is smoothed with a 7-day rolling mean. The annual maximum of the 7-day mean is computed per province and per zone. Historical quartile thresholds (Q1/Q2/Q3) are annotated. These are used to assess the population impact that would have occurred under past flood seasons, informing return-period calibration of any eventual trigger.

## Trigger logic

- **Keys off:** SEAS5 precipitation forecast (issued December, valid Dec–Jan) aggregated at ADM1 level; ERA5 November observations; Floodscan historical flood exposure.
- **Decision rule (plain language):** Not formalised. Exploratory analysis suggests the framework would activate when the December-issued SEAS5 forecast for December–January precipitation in one or more zones exceeds a threshold (likely upper tercile, return period ≥ some level — 3 or 5 years is typical but unconfirmed). An ERA5 November observation component may serve as a real-time cross-check. The Floodscan analysis informs impact thresholds but does not appear to be part of the trigger rule itself.
- **Activation structure:** Three spatial zones are defined (Zone 1: Bas-Uele/Haut-Uele/Tshopo; Zone 2: Nord-Kivu/Sud-Kivu; Zone 3: Tanganyika). A zone-by-zone trigger structure is implied but not yet coded.
- **Calibration:** Return-period ranking against 2000–2024 SEAS5 historical record. No return-period cutoff (e.g., 1-in-3 or 1-in-5) has been formally selected.
- **Authoritative source:** None — no framework PDF exists. This page summarises the repo analysis only.
- **Operated by:** Not applicable — no live trigger system exists.

## Trigger windows

The three windows below are inferred from the zone structure in `src/constants.py`. They have not been codified as distinct windows in any trigger document.

**Counting rule:** One row per zone (spatial differentiator); `n_windows = 3`. Caveat: this zone-based row structure is inferred from `ZONES` in `src/constants.py` and from the zone aggregation in `exposure.md`. The SEAS5 and ERA5 notebooks actually loop over individual **provinces** (`AOI_ADM1_PCODES`), not zones, so whether a future trigger fires per-zone or per-province is unsettled (see `discrepancies`).

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| Zone 1 (Bas-Uele / Haut-Uele / Tshopo) | mixed (forecast + obs) | SEAS5 Dec-issued precip (Dec–Jan) + ERA5 Nov precip | upper tercile (return period TBD) | ~1–2 months | TBD | TBD |
| Zone 2 (Nord-Kivu / Sud-Kivu) | mixed (forecast + obs) | SEAS5 Dec-issued precip (Dec–Jan) + ERA5 Nov precip | upper tercile (return period TBD) | ~1–2 months | TBD | TBD |
| Zone 3 (Tanganyika) | mixed (forecast + obs) | SEAS5 Dec-issued precip (Dec–Jan) + ERA5 Nov precip | upper tercile (return period TBD) | ~1–2 months | TBD | TBD |

## Sources & repo completeness

- **Trigger taken from:** repo (no framework PDF exists; `trigger_source: repo`).
- **Repo completeness:** partial — the analysis notebooks (exploration/) explore the data sources and visualise distributions but do not contain a codified trigger rule. No pipeline, app, or deployment exists.
- **Discrepancies:** See frontmatter `discrepancies` list. Key items: (1) no published PDF; (2) the two indicators (SEAS5 forecast, ERA5 observation) are not combined into a decision rule; (3) zone vs. province aggregation is unresolved — the precip notebooks calibrate per-province while the window table is built per-zone; (4) calibration granularity is inconsistent (precip uses terciles, Floodscan uses quartiles); (5) Floodscan exposure thresholds are descriptive only and not wired into the trigger; (6) KINSHASA1 and EQUATEUR1 appear in exposure plots but are outside the defined AOI; (7) the analysis year 2024 is hardcoded throughout the notebooks; (8) Floodscan regions 1 and 3 are queried but region 2 is not, despite three zones; (9) DB access runs against the dev slot, not prod.

## Monitoring

No monitoring system exists. There is no pipeline, no scheduled data pull, and no app. The exploration notebooks are run manually.

## Historical activations

Never activated. The framework has not reached endorsement, so no CERF or other allocation has been made under this mechanism.

## Key decisions & rationale

- **December issuance window:** The `dec-seasonal` branch name and `issued_month = 12` in seas5.md imply the chosen trigger window is December-issued SEAS5 forecasts valid for December–January — the short rainy season peak in parts of eastern DRC. This is consistent with the flood seasons observed in Nord-Kivu, Sud-Kivu, and Tanganyika.
- **Upper tercile as reference:** Consistent with standard CERF AA practice for seasonal precipitation frameworks (above-normal rainfall as the trigger signal).
- **Six provinces in three zones:** The geographical scope targets the provinces most severely affected by the January 2024 floods (DRC's worst floods in 60 years affected 18 provinces, of which these eastern provinces were among the hardest hit). The zone grouping likely reflects operational response zoning.
- **KINSHASA1 / EQUATEUR1 outside AOI:** These appear only in the exposure notebook's individual plots, suggesting they were explored for context but excluded from the trigger scope, possibly because their flood dynamics differ (Congo River vs. eastern highland rains).

## Changes from previous version

No prior version — this is the initial development analysis (repo created December 2024).

## Open questions / known issues

- What return-period threshold triggers? (1-in-3? 1-in-5? Different per zone?)
- How are SEAS5 and ERA5 combined — AND logic, OR logic, or a weighted index?
- Does Floodscan exposure inform the trigger threshold directly, or is it used only for calibration/validation?
- Is there a budget envelope and response plan that would govern what is released per zone?
- When is endorsement / framework publication expected?
- Will a CERF Anticipatory Action allocation be pursued, and if so, on what timeline?
- The `dec-seasonal` branch targets December issuance for Dec–Jan, but DRC also has a second rainy season (around April–May in the east). Is a second trigger window planned?
