---
content_type: analysis
analysis_type: exploratory   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: nga-cholera
version: april24-new-data-python  # no published doc — branch name per template convention
status: development
country_iso3: NGA
hazard: cholera
admin_level: 2
geographic_scope: ["NG002", "NG008", "NG036"]
data_sources: [cholera-linelist]
trigger_facets:
  basis: observational
  calibration: percentile
  indicators: [weekly-suspected-cases, weekly-case-growth-rate]
  n_windows: 1
  window_axes: []
supersedes: null
# --- funding & scope ---

prearranged_funding_usd: null
funding_by_source: {}
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: []
target_people: null
# --- documents, authority-ranked ---
framework_doc: null
framework_doc_date: null
framework_doc_annexes: []
languages: [en]
model_report: null
raw_extract: []
# --- live system ---
operated_by: null
apps: []
# --- source repo & reconciliation ---
depends_on: []
source_repo: ocha-dap/pa-aa-nga-cholera
source_branch: april24-new-data-python
source_sha: c56bc8b
code_ref:
  - exploration/03b_explore_2024_data_python.md
  - exploration/03a_explore_2024_data.qmd
  - src/constants.py
trigger_source: repo
repo_completeness:
  analysis: partial
  deployed_code: lost
discrepancies:
  - "[gap] No published framework PDF found on ReliefWeb or unocha.org; trigger design exists only in exploratory notebooks - there is no endorsed document to cross-check against."
  - "[gap] The 2024 Python notebook (03b) applies fixed absolute thresholds (Borno=59, Adamawa=19 cases/week) derived from static percentile calculations, but does not document how these were calibrated or what return period they represent."
  - "[stale] The R-based exploration notebooks (01a, 01b, 03a) and R/technical_indicators.R contain DRC-style expanding-percentile and Sorbonne-classification code; this was early methodological exploration and is not the current trigger design."
  - "[stale] The CERF_YEARS constant in src/constants.py lists [2013, 2018, 2022] as calibration reference years; the notebook data however identifies 2018 and 2021 as the CERF RR allocation events (2022 had a Borno spike but no CERF allocation), suggesting a minor inconsistency between the constant and the exploratory analysis narrative."
  - "[stale] src/constants.py carries many exploration leftovers not used by the current priority-LGA trigger: WUROBOKI_LAT/WUROBOKI_LON point coords, and non-priority LGA pcodes (JAKUSKO, JERE, MONGUNO, MARTE, MAFA) plus the EXP_HRP_*_ADM2_PCODES sets. Only PRIORITYONE/PRIORITYTWO (Bama, Numan, Dikwa, Ngala) feed the Python notebook trigger."
  - "[stale] Two parallel implementations coexist on sibling branches: the R pipeline (branch april24-new-data; 03a qmd + R/technical_indicators.R) keeps the full 4-level Sorbonne weekly-rate classification and expanding-quarterly-percentile machinery, while the Python branch (april24-new-data-python; 03b notebook) collapses to a binary 99th-percentile-OR-4x-growth, 3-consecutive-week rule. The Python branch is the latest design; the richer R logic is superseded exploration, not the live trigger."
  - "[conflict] The two CERF Rapid Response anchor dates disagree on the second event within the source itself: the 03a qmd narrative (bullet) writes 2021-10-21, while the code constant actually used downstream (cerf_rr_allocations <- as_date(c('2018-10-31','2021-10-22'))) uses 2021-10-22. A one-day internal inconsistency in the calibration anchor."
  - "[gap] Timeliness of the cholera linelist data has not been confirmed; the 03a notebook explicitly notes this as a blocking concern ('if timeliness of the data cannot be confirmed there is little point in committing more work into hypothetical trigger design')."
  - "[gap] The Python notebook explores both a fraction-of-population threshold (FRAC_THRESH_99 = 0.01765/100 = 0.0001765) and an absolute-case threshold per ADM1 state, but does not document which was selected for the endorsed trigger - no endorsed trigger exists yet."
  - "[gap] The 2020 data gap is flagged as a known quality issue: confirmed outbreaks occurred across all 3 BAY states in 2020 but the linelist is nearly empty for that year, limiting calibration."
  - "[gap] No confirmed priority-LGA selection rationale documented in code; constants.py designates Bama and Numan as priority-1, Dikwa and Ngala as priority-2, but the decision logic is not explained in any notebook."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "No framework_doc exists; trigger_source=repo per INGESTION.md instructions for development-stage repos. No dated publication exists, so version is set to the source branch name (april24-new-data-python) per the template convention; status=development."
  cerf_rr_reference_events: "Two past CERF Rapid Response cholera allocations referenced as calibration anchors: 2018-10-31 and 2021-10-22 (both pre-date this framework and are not AA activations)."
  aoi_notes: "BAY states = Borno (NG008), Adamawa (NG002), Yobe (NG036). Priority LGAs from src/constants.py: priority-1 = Bama (NG008003), Numan (NG002016); priority-2 = Dikwa (NG008008), Ngala (NG008025). Broader analysis AOI covers 17 Borno + 16 Yobe + 16 Adamawa LGAs."
visibility: internal
last_synced: 2026-06-17
---

# Nigeria Cholera — development

> **Analysis, not a framework** (reclassified 2026-06-17): repo-only exploration; no published framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> No published framework PDF exists as of June 2026. The trigger design is in exploratory analysis notebooks on branch `april24-new-data-python`. This page reflects the repo state only; it is not authoritative for an endorsed trigger.

## Summary

This framework is an anticipatory action design in development for cholera in northeast Nigeria's BAY states (Borno, Adamawa, Yobe). It targets LGA-level cholera outbreaks using weekly suspected case counts from the state epidemiological linelist. The trigger keys off a sustained signal — either case counts exceeding the historical 99th percentile or a week-on-week growth rate exceeding 4x — for 3 consecutive weeks in any priority LGA. No framework PDF has been published; the design exists only as exploratory analysis in the repo. Activation of pre-arranged funds has never occurred under this framework.

## Method

Data is weekly suspected cholera case counts aggregated to the LGA level, sourced from case-based linelists supplied by state Ministries of Health across the BAY states. The linelist data spans 2018–2023 (with a significant gap in 2020). Population denominators come from the 2023 LGA population estimates embedded in the CHOLERA_BAY shapefile.

The analysis pipeline (R and Python notebooks in `exploration/`) merges linelist data with population and administrative boundary files, calculates weekly case counts per LGA, and evaluates two trigger conditions:

1. **Percentile threshold**: cases in a given LGA exceed the 99th percentile of historical weekly caseloads for that state.
2. **Growth rate threshold**: cases in a given LGA increase by ≥ 4x relative to the prior week.

Both conditions are combined via OR logic, then a 3-consecutive-week rolling window is applied: a trigger fires when either condition is satisfied in 3 successive weeks. The Python notebook uses fixed absolute thresholds derived from this percentile calculation (Borno: 59 cases/week, Adamawa: 19 cases/week) in addition to the fractional-population threshold (0.01765% of population/week = FRAC_THRESH_99 constant).

The MACD (moving-average convergence/divergence) crossover approach was also explored as an alternative indicator but not selected.

## Trigger logic

- **Keys off:** Weekly suspected cholera case count per LGA (observational, from state Ministry of Health linelist)
- **Decision rule:** A trigger fires for a given LGA when either (a) weekly cases ≥ 99th-percentile historical threshold OR (b) week-on-week case growth ≥ 4x, AND this condition holds for 3 consecutive weeks.
- **Activation structure:** Single-window, observational only. No forecast component. Fires per LGA within the priority set; no spatial aggregation logic defined.
- **Calibration:** 99th percentile calculated from 2018–2023 BAY-states linelist data; zero-imputation approach used for missing weeks (the alternative — percentiles on active weeks only — produced thresholds considered too high). Historical absolute thresholds: Borno 59 cases/week, Adamawa 19 cases/week. The 4x growth rate threshold is borrowed from the DRC cholera AA framework.
- **Authoritative source:** `trigger_source: repo` — the latest framework PDF does not exist. The exploratory notebooks are the only documented design.
- **Operated by:** null — no operational system; analysis only.

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| in-season observational | observational | weekly-suspected-cases; weekly-case-growth-rate | Cases ≥ 99th percentile (~59/wk Borno, ~19/wk Adamawa) OR growth ≥ 4x, for 3 consecutive weeks | 0 weeks (real-time obs) | ~1-in-100 weeks per state (by construction) | not defined |

## Sources & repo completeness

- **Trigger taken from:** `repo` (no published framework PDF exists).
- **Repo completeness:** `{analysis: partial, deployed_code: lost}` — exploratory notebooks capture the trigger concept and threshold derivation, but the design is not finalized, timeliness of data has not been confirmed, and no production pipeline or deployed monitoring system exists.
- **Discrepancies:** See frontmatter `discrepancies` field. Key issues: (1) no endorsed document; (2) data timeliness unconfirmed; (3) 2020 data gap limits calibration; (4) CERF_YEARS constant lists [2013, 2018, 2022] but the notebook analysis identifies 2018 & 2021 as the actual CERF events (stale constant); (5) threshold selection between absolute and fractional approaches is not finalized; (6) the source itself disagrees on the second CERF anchor date (qmd narrative 2021-10-21 vs code constant 2021-10-22); (7) R (Sorbonne/expanding-percentile) and Python (binary 99th-pct + 4x growth) implementations coexist on sibling branches, the Python branch being the latest design.

## Monitoring

No operational monitoring system or pipeline exists. The analysis is run manually from exploratory notebooks. No apps are deployed. The `exploration/03b_explore_2024_data_python.md` notebook was the most recent analysis run (branch `april24-new-data-python`, last commit 2024-10-22).

## Historical activations

This AA framework has never been activated. No pre-arranged funding has been released under it. Two historical CERF Rapid Response allocations for cholera in Nigeria serve as calibration reference events but predate the framework:
- 2018-10-31: CERF RR allocation (response to 2018 Borno outbreak)
- 2021-10-22: CERF RR allocation (response to 2021 BAY outbreak)

The exploratory analysis found that the proposed trigger design would have fired approximately 3–9 weeks ahead of these CERF allocation dates, had data been available and the framework operational.

## Key decisions & rationale

- **BAY states scope:** The framework focuses on northeast Nigeria's Borno, Adamawa, and Yobe (BAY) states, which account for the vast majority of Nigeria's cholera burden and have received CERF Rapid Response funding repeatedly.
- **LGA level:** Ward-level data exists but population denominators were unavailable at ward level; LGA was the chosen spatial unit.
- **99th percentile + 4x growth, 3-week window:** The 99th percentile is a common threshold in cholera AA frameworks (used in DRC). The 4x growth rate threshold is adapted from DRC. The 3-consecutive-week requirement filters false positives and confirms sustained outbreak trajectory rather than a single spike.
- **Zero-imputation for missing weeks:** Including zero-case weeks in percentile calculation yields lower, more actionable thresholds. Using only active weeks produces thresholds that are too high to be useful.
- **Priority LGAs:** Bama and Numan designated priority-1; Dikwa and Ngala priority-2. Rationale not documented in the repo; likely reflects prior CERF-allocated LGAs and burden data.
- **Timeliness as blocking concern:** The analysis explicitly identified data timeliness as a prerequisite for framework development. Without confirmation that linelist data arrives within the required lead time, the framework cannot proceed to endorsement.

## Changes from previous version

No prior version. This is the initial development-stage design.

## Open questions / known issues

1. **Data timeliness:** Can the state Ministry of Health linelist data be received with sufficient regularity and speed (ideally within days of case registration) to support anticipatory action? This is flagged as the primary blocker to framework advancement.
2. **2020 data gap:** How should the missing 2020 data be handled for calibration? Confirmed outbreaks occurred across all BAY states in 2020.
3. **Threshold finalization:** Which threshold approach is preferred — absolute (59/week Borno, 19/week Adamawa) or fraction-of-population (0.01765% per week)? The Adamawa absolute threshold of 19 cases/week was noted as potentially too low.
4. **Priority LGA selection:** What is the documented rationale for the Bama/Numan (priority-1) and Dikwa/Ngala (priority-2) designations?
5. **Framework status:** As of 2026, has the NGA cholera AA framework been endorsed or published? No OCHA/ReliefWeb publication was found during ingestion (June 2026).
6. **Funding mechanism:** Would pre-arranged funds come from CERF, NHF, or another source? No funding envelope has been defined.
