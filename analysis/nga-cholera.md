---
content_type: analysis
analysis_type: exploratory   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: nga-cholera
version: explore/cholera-2018-2023-analysis  # no published doc — branch name per template convention
status: development
country_iso3: NGA
hazard: cholera
admin_level: 2
geographic_scope: ["NG002", "NG008", "NG036"]
data_sources: [cholera-linelist, CERF-allocations, CODAB]
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
# --- source repo & reconciliation ---
depends_on: []
source_repo: ocha-dap/pa-aa-nga-cholera
source_branch: explore/cholera-2018-2023-analysis   # PR #6 to main, opened 2026-11-04
source_sha: 482658b
code_ref:
  - exploration/cholera_analysis/   # the Quarto book (rendered _book/ served by apps/chd-pa-aa-nga-cholera)
  - exploration/cholera_analysis/drc_trigger.py
  - exploration/cholera_analysis/drc_book.py
  - exploration/cholera_analysis/analysis_utils.py
  - exploration/cholera_analysis/methods.qmd
  - exploration/cholera_analysis/tests/test_drc_trigger.py
  - exploration/03b_explore_2024_data_python.md   # 2024 candidate design (superseded)
  - src/constants.py
trigger_source: repo
repo_completeness:
  analysis: full
  deployed_code: lost
discrepancies:
  - "[gap] No published framework PDF on ReliefWeb or unocha.org; no BAY cholera AA framework exists. The book applies the DRC framework's 2026 trigger to see what it would have done; nothing in it is a proposed BAY trigger."
  - "[gap] The line-list has no laboratory results (no RDT, culture or PCR field), so the DRC 2026 framework's condition of a laboratory-confirmed case in the 30 days before activation cannot be tested."
  - "[gap] Cases are dated by onset (date seen at a health facility for 79%: median 0 days later, 95% within 4 days); the date cases reached state or national surveillance is not in the line-list, so the reporting delay is unknown. A separate IDSR completeness/timeliness file (2023 and 2024 weeks 1-15) shows BAY LGAs' weekly reports arrived on time in 86-98% of weeks, but not their cholera counts."
  - "[gap] The line-list ends in December 2023; no 2024+ case data on the dev blob (checked 2026-11-04). The May 2026 CERF cholera allocation for Borno cannot be tested."
  - "[gap] The 2020 data gap: outbreaks were reported in all three BAY states in 2020 (WHO/PMC sources on the blob) but the line-list has 3 cases that year. Excluded from every baseline."
  - "[resolved 2026-11-04] The two CERF anchor dates in the 2024 notebooks (2021-10-21 in the 03a narrative, 2021-10-22 in code) are both wrong as endorsement dates: OneGMS gives ERC endorsement 2021-09-27 for 21-RR-NGA-49477 (2021-10-21/22 are the first/last project approvals). The book now uses ERC endorsement dates, as the DRC and Haiti analyses do."
  - "[stale] The CERF_YEARS constant in src/constants.py lists [2013, 2018, 2022]; OneGMS has no cholera allocation to Nigeria in 2013 or 2022. Cholera allocations: 2018, 2021, 2026."
  - "[stale] The 2024 candidate designs (R branch april24-new-data: Sorbonne classification + expanding quarterly percentiles; Python branch april24-new-data-python, notebook 03b: per-capita 99th percentile or fixed Borno 59 / Adamawa 19 cases a week, OR >=4x growth, 3 weeks, priority LGAs Bama/Numan/Dikwa/Ngala) are superseded by the book's DRC-rule analysis. The priority-LGA rationale was never documented."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "No framework_doc exists; trigger_source=repo per INGESTION.md for development-stage repos. No dated publication, so version is the source branch name; status=development."
  method_source: "Trigger from OCHA-DAP/pa-aa-cod-infectious-disease main@a44d9a3 (the DRC 2026 revision's L3 configuration: p98.8 of non-zero weekly suspected cases, >4x week-on-week rate rule with a previous 0 counted as 1, 3 consecutive alert weeks, 6-month same-unit mute, 6-month per-province spatial mute of the province and its neighbours), via the Python port in ds-aa-hti-cholera (src/hti_cholera/trigger.py @0bc54ba), copied with the code unchanged as drc_trigger.py. The Haiti repo checks the port against outputs of the DRC code; that check had no excluded years, which tests/test_drc_trigger.py here adds."
  cerf_rr_reference_events: "CERF Rapid Response cholera allocations to Nigeria (OneGMS, ERC endorsement dates): 18-RR-NGA-32765, 2018-10-31, US$2.25M (BAY + eight north-west/north-central states); 21-RR-NGA-49477, 2021-09-27, US$6.0M (national; CERF's report names Borno and Yobe among nine states); CERF-NGA-26-RR-1546, 2026-05-23, US$4.0M (Borno outbreak; also Adamawa, Yobe, Sokoto, Zamfara). None was anticipatory. The 2022 Borno outbreak, the largest in the line-list, drew no CERF cholera allocation."
  aoi_notes: "BAY states = Borno (NG008), Adamawa (NG002), Yobe (NG036). The book's panel is the 55 LGAs in the 2023 population file (26 Borno, 16 Yobe, 13 Adamawa); BAY has 65 in the COD-AB, and the other ten have no line-list cases. Borno borders both other states; Adamawa and Yobe do not touch."
visibility: internal
last_synced: 2026-11-04
---

# Nigeria Cholera — development

> **Analysis, not a framework** (reclassified 2026-06-17): repo-only exploration; no published framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> No BAY cholera AA framework exists as of November 2026. Since 2026-11-04 the analysis applies the DRC cholera framework's 2026 trigger to the BAY line-list, as was done for Haiti ([hti-cholera](hti-cholera.md)). Nothing here is an endorsed or proposed trigger.

## 2026-11 revision — the DRC 2026 trigger applied to BAY

The Quarto book in `exploration/cholera_analysis/` (branch `explore/cholera-2018-2023-analysis`,
[PR #6](https://github.com/OCHA-DAP/pa-aa-nga-cholera/pull/6)) was revised on 2026-11-04. Chapters
1–3 (data, data quality, epidemiology) are unchanged. Chapters 4–6 now apply the trigger of the
[DRC cholera framework's 2026 revision](../frameworks/cod-infectious-disease/2026-06-24.md) — its
L3 configuration, through the Python port written for Haiti — to the line-list
(`CHOLERA_BAY 2018_2023.xlsx`, dev blob `pa-aa-nga-cholera/raw/healthsector/`), and compare the
result with CERF's cholera allocations to Nigeria. A method-notes chapter records the port and the
BAY-specific choices. The 2024 candidate design is kept in chapter 4 as a comparison.

Findings, all retrospective and dated by onset:

- **Threshold.** The DRC procedure in January 2024 (98.8th percentile of LGA-weeks with at least
  one case, five prior years skipping 2020) gives **251 suspected cases per LGA-week**, above the
  DRC's own 2026 endemic value (174). Taking each year's threshold from earlier years only gives
  113 to 269.
- **Would-have-activated history.** With 251, the rule would have activated **twice** in the five
  usable years (Weibull return period 3 years): Gwoza (Borno), week ending 5 September 2021, and
  Jere (Borno), week ending 2 October 2022. The expanding baseline or the DRC's 174 add Mubi North
  (Adamawa), May 2018; the DRC's 63 gives five.
- **The L3 spatial mute.** Borno borders both other states, so one activation in Borno mutes all of
  BAY for six months. The same-state mute (the DRC team's L2.5 alternative) is the closer
  equivalent of the DRC's 26 provinces.
- **Timing.** Three alert weeks are needed and BAY outbreaks rise fast: most activations come in the
  LGA's peak week or the week after, when 45–62% of its outbreak cases have happened.
- **CERF.** The rule activates 3–5 weeks before the September 2021 allocation under every baseline.
  In the August–October 2018 wave the 2018 allocation responded to, only the 63 threshold activates
  (Damaturu, Yobe); lower thresholds also activate on a separate Adamawa outbreak in May, which under
  L3 mutes Adamawa and Borno for the autumn wave. 2022, the largest outbreak, drew no CERF cholera
  allocation. The May 2026 allocation is after the line-list ends.
- **Not testable**: the laboratory condition (no lab results) and the reporting delay (onset dates
  only).

The earlier (2024) candidate design gave 27 LGA-year activations; most of the difference is the
DRC rule's same-LGA and spatial mutes, which count one activation per outbreak area instead of one
per LGA-year.

**Deployment:** the rendered book is at <https://chd-pa-aa-nga-cholera.azurewebsites.net>
(redeployed 2026-11-04) — see [apps/chd-pa-aa-nga-cholera](../apps/chd-pa-aa-nga-cholera.md).

## Summary

Exploratory analysis of cholera in north-east Nigeria's BAY states (Borno, Adamawa, Yobe) for a
possible LGA-level anticipatory action trigger on weekly suspected cases from the state line-list.
The current analysis tests the DRC framework's 2026 trigger on 2018–2023 data. No framework PDF
has been published, no funding is pre-arranged, and no activation has ever happened.

## Method

Data: the consolidated BAY suspected-cholera line-list, 2018–2023 (32,826 suspected cases,
836 deaths; one row per case with onset date, date seen at a health facility, LGA, ward, outcome,
age, sex, OCV; no laboratory results). Aggregated to LGA × ISO week, 55 LGAs. 2020 is a reporting
gap (3 cases) and is excluded from every baseline.

The trigger tested is the DRC 2026 L3 rule: a week is at alert if suspected cases exceed the 98.8th
percentile of non-zero LGA-weeks in the baseline, or are more than four times the previous week's
(a previous 0 counts as 1); an onset is the third consecutive alert week; onsets are muted within
six months of a kept activation in the same LGA (L2) and in the same or a neighbouring state (L3).
Four baselines: pooled 2018–2023 without 2020 (reference; equal to the January 2024 recompute),
expanding, and the DRC's fixed 2026 values (174 and 63). One pool for the three states (no
endemic/non-endemic list exists for BAY LGAs). The book also shows L2.5 (same-state mute only), a
percentile sweep (p95–p99.5), the rule without the rate component, and each activation's timing
against its LGA's and state's peak.

## Trigger logic

- **Keys off:** weekly suspected cholera cases per LGA (observational, state line-list).
- **Decision rule (as tested):** the DRC 2026 L3 rule above; reference threshold 251 suspected cases
  per LGA-week. The framework's laboratory condition is not applied (no lab data).
- **Activation structure:** single observational window; one pool; per-state spatial mute.
- **Calibration:** in-sample on 2018–2023 (2020 excluded); five usable years.
- **Authoritative source:** `trigger_source: repo` — no framework document exists.
- **Operated by:** null — analysis only, no monitoring.

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| in-season observational (as tested) | observational | weekly suspected cases; weekly growth | > 251 cases/LGA-week (p98.8 of non-zero LGA-weeks) OR > 4× the previous week, 3 consecutive weeks; L3 mute | 0 weeks on onset dates; activations land at the LGA's outbreak peak; reporting delay unknown | 3 years (2 activations, 5 usable years; Weibull) | not defined |

## Sources & repo completeness

- **Trigger taken from:** `repo` (no published framework PDF).
- **Repo completeness:** `{analysis: full, deployed_code: lost}` — the book is complete and
  reproducible (`quarto render --execute` with blob credentials; 19 unit tests); there is no
  monitoring code.
- **Discrepancies:** see frontmatter. In short: no framework; no lab results; reporting delay
  unknown; data end in 2023; 2020 gap; the 2024 notebooks' CERF dates and `CERF_YEARS` are wrong
  as endorsement dates; the 2024 designs are superseded.

## Monitoring

None. The book is a one-off render of 2018–2023 data, not a monitoring system.

## Historical activations

Never activated; no pre-arranged funding. The three CERF Rapid Response cholera allocations to
Nigeria (2018-10-31, 2021-09-27, 2026-05-23; details in `extra.cerf_rr_reference_events`) are the
reference events the book compares against. None was anticipatory, and none was for BAY alone.

## Key decisions & rationale

- **BAY scope:** the north-eastern states covered by the humanitarian response plan. All three CERF
  cholera allocations to Nigeria included BAY states (2018: all three; 2021: Borno and Yobe; 2026:
  all three), though most of Nigeria's cholera cases in 2018 and 2021 were elsewhere.
- **LGA level:** the line-list has wards, but population and boundaries are at LGA level, and the
  LGA is the analogue of the DRC's health zone.
- **The DRC 2026 rule (2026-11):** the endorsed framework closest in design, already ported to
  Python and checked for Haiti. Using it as written shows what an existing CERF-endorsed trigger
  would have done, rather than tuning a new one to six years of data.
- **Non-zero-week percentiles:** the DRC method; it reverses the 2024 design's zero-filled
  per-capita percentiles. The rate rule and three-week persistence catch the start of an outbreak.
- **2020 excluded:** a reporting gap, not a quiet year.

## Changes from previous version

- **2026-11-04:** chapters 4–6 rewritten to apply the DRC 2026 L3 trigger (was: per-capita
  99th percentile or ≥4× growth, 3 weeks, no mute; 27 LGA-year activations). CERF dates corrected to
  ERC endorsement (2021: 27 September, not 22 October); May 2026 allocation added. Method-notes
  chapter and unit tests added.
- **2026-07:** consolidated 2018–2023 line-list book (branch `explore/cholera-2018-2023-analysis`),
  deployed to App Service.

## Open questions / known issues

1. **Weekly LGA counts for 2024–2026** (ideally IDSR, what an operational trigger would use): would
   add the May 2026 CERF allocation and allow the threshold to be computed on current data.
2. **Laboratory results** by LGA and week, to test the framework's confirmation condition.
3. **Reporting dates**, to measure the delay between onset and when a trigger could see a case.
4. **A hotspot-LGA list** (NCDC or the states), the equivalent of the DRC's endemic provinces.
5. **What a BAY trigger should catch:** outbreaks of the 2022 size (no CERF money) or only those
   that drew CERF funding; and L3 versus L2.5 for three states.
6. **Framework status:** no NGA cholera AA framework has been published (checked November 2026).
