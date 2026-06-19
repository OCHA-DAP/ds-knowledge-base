---
content_type: analysis
analysis_type: exploratory   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: eth-flooding
version: development
status: development
country_iso3: ETH
hazard: flood
admin_level: 2
geographic_scope: []
data_sources: [SEAS5]
trigger_facets:
  basis: forecast
  calibration: return-period
  indicators: [SEAS5-JAS-rainfall-return-period]
  n_windows: 1
  window_axes: []
supersedes: null
prearranged_funding_usd: null
funding_by_source: {}
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: []
target_people: null
framework_doc: null
framework_doc_date: null
framework_doc_annexes: []
languages: [en]
model_report: null
raw_extract: [/tmp/phase2-batch2/raw/eth-flooding_doc.txt]
operated_by: null
apps: []
depends_on: []
source_repo: ocha-dap/ds-aa-eth-flooding
source_branch: main
source_sha: be88a7a
code_ref: [markdowns/rainfall_return_period.Rmd]
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No published flood framework document exists for Ethiopia. The UNOCHA candidate\
    \ page (https://www.unocha.org/publications/report/ethiopia/evaluation-report-ochas-anticipatory-action-trigger-ethiopia-26-april-2021)\
    \ leads to the April 2021 evaluation report of Ethiopia's DROUGHT AA trigger (ETH_FinalReport_OCHAClimateCentre_April2021.pdf),\
    \ NOT a flood framework. The repo is named eth-flooding but no authoritative flood\
    \ trigger document exists publicly."
  - "[gap] Trigger thresholds are not defined in the repo. The Rmd computes SEAS5\
    \ JAS rainfall return periods at ADM2 level and maps them, but sets no numeric\
    \ activation threshold (no stated return period, probability cutoff, or area fraction\
    \ that would release funds)."
  - "[gap] The repo helpers.R is empty (no helper functions implemented). The Rmd\
    \ depends on functions pg_load_seas5_historical() and seas5_aggregate_forecast()\
    \ from an unexported package (cumulus) — the trigger pipeline is not self-contained\
    \ in this repo."
  - "[gap] No stated geographic scope — the Rmd uses iso3=ETH at ADM2 level for all\
    \ of Ethiopia, but the target area(s) for flood AA are not documented."
  - "[stale] rainfall_return_period.Rmd computes a tercile classification (df_filtered,\
    \ group_by(pcode, leadtime), cut on terciles) that is never used in the return-period\
    \ mapping path (which keys off mean/return_period only) — leftover/dead code. library(shiny)\
    \ is also loaded but never used."
  - "[stale] rainfall_return_period.Rmd hardcodes the historical baseline as year(issued_date)\
    \ >= 2000 in the filter (line 66) while year_start is a parameter (default 2000)\
    \ used only in plot labels. Changing the year_start param would NOT change the actual\
    \ baseline used — a latent inconsistency / hardcoded constant, not the parameterised\
    \ value the labels imply."
  - "[gap] The repo is at the earliest development stage: only 2 commits (2025-06-10\
    \ initial, 2025-07-08 rainfall analysis), no endorsement process started, no monitoring\
    \ pipeline, no companion repo or deployment found. The Rmd is a standalone manual\
    \ notebook."
activations: []
extra:
  schema_strain: "No published framework document exists for this flood framework.\
    \ trigger_source=repo and framework_doc=null. The candidate PDF supplied in the\
    \ ingestion task (ETH_FinalReport_OCHAClimateCentre_April2021.pdf) is the evaluation\
    \ report of Ethiopia's DROUGHT AA trigger, not a flood framework — it was ingested\
    \ and extracted to raw_extract for reference but is NOT authoritative for this\
    \ page. The drought framework is a separate entry (eth-drought)."
  candidate_pdf_note: "ETH_FinalReport_OCHAClimateCentre_April2021.pdf describes\
    \ Ethiopia's 2020 drought AA trigger: two-step Food Insecurity + Drought indicator\
    \ (IPC thresholds + seasonal rainfall forecast). First activated December 2020.\
    \ CERF allocated $20M ($13M phase 1 Dec 2020 + $7M phase 2 Feb 2021), reaching\
    \ >900,000 people. Implementing agencies included FAO, UNICEF, WHO, UNHCR, UNFPA,\
    \ WFP. That drought framework is a SEPARATE framework from this flood repo."
visibility: internal
last_synced: 2026-06-17
---

# Ethiopia Flood — development

> **Analysis, not a framework** (reclassified 2026-06-17): repo-only exploration; no published framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.


> No published framework document exists for this flood framework. The canonical trigger analysis is in `code_ref`; this page summarises the repo and notes its status.

## Summary

The `ds-aa-eth-flooding` repo is an early-stage analytical project to develop an anticipatory action trigger for **flooding** in Ethiopia, using SEAS5 seasonal rainfall forecasts. As of July 2025 the repo contains a single analysis notebook that computes JAS (July–August–September) rainfall return periods and anomalies at ADM2 level from SEAS5 hindcast data. No trigger thresholds, geographic scope, or funding envelope have been defined yet. No published framework document exists; this is distinct from Ethiopia's drought AA framework (a separate initiative, first activated December 2020).

## Method

The method in `markdowns/rainfall_return_period.Rmd` proceeds as follows:

1. Load SEAS5 historical seasonal forecasts at ADM2 level for Ethiopia via `cumulus::pg_load_seas5_historical()`.
2. Aggregate over the JAS season (July, August, September) using the mean of ensemble member rainfall for each issued month.
3. Compute exceedance probabilities and return periods using the rank method (rank / (n+1)), grouping by ADM2 pcode.
4. Also compute rainfall anomalies relative to the 2000-present mean.
5. Map the results: return period bins (0–5, 5–10, 10–20, 20–30, 30–50, 50+) and rainfall anomaly bins by woreda.

The analysis is parameterised (iso3, adm_level, dataset, year, issue_month, months, year_start) to support re-runs for different seasons. No threshold value is currently set above which a trigger would fire.

## Trigger logic

- **Keys off:** SEAS5 JAS rainfall return period at ADM2 level (issued July)
- **Decision rule (plain language):** Not yet defined. The analysis computes return periods for each woreda but does not specify the threshold return period that would activate the framework (e.g. "≥1-in-5 year event in at least N woredas").
- **Activation structure:** Single window (no multi-stage or spatial disaggregation beyond ADM2 mapping). No AND/OR logic defined.
- **Calibration:** Return period calculated from SEAS5 hindcast 2000–present using the rank method. Threshold return period not yet calibrated against historical flood events.
- **Authoritative source:** None — no published framework document. The repo is the only source.
- **Operated by:** OCHA/CHD (this repo).

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| JAS seasonal | forecast | SEAS5 JAS mean rainfall return period (ADM2) | not defined | ~1 month (issued July) | not defined | not defined |

## Sources & repo completeness

- **Trigger taken from:** `repo` (no framework doc exists).
- **Repo completeness:** partial — the rainfall return period analysis is present and runnable (subject to `cumulus` package access), but trigger thresholds, geographic scope, funding envelope, and implementing agency roles are all absent.
- **Discrepancies:** See frontmatter `discrepancies`. Key gaps: no published flood framework document; the UNOCHA candidate page leads to the drought evaluation PDF; no threshold defined in code; `helpers.R` is empty; `cumulus` package dependency is unexported. Stale-code notes: the Rmd computes an unused tercile classification (dead code, plus an unused `library(shiny)`), and hardcodes the baseline `year >= 2000` in the filter while `year_start` is a parameter used only in plot labels (latent inconsistency).

## Monitoring

No monitoring pipeline or live system is deployed. The Rmd is a standalone analytical notebook re-run manually with a `year` parameter.

## Historical activations

Never activated. This framework has not been endorsed or triggered. Note: Ethiopia's **drought** AA framework was activated in December 2020 and March 2021 (CERF $20M), and again in September 2024 ($10M CERF + $7M EHF) — those are a separate framework.

## Key decisions & rationale

- SEAS5 JAS season chosen to align with the Kiremt (long rains) season, the primary flood risk season in Ethiopia (June–September, peak July–August).
- Return period framing chosen over probability tercile to communicate risk in terms familiar to AA practitioners.
- ADM2 level used to capture sub-regional heterogeneity within large Admin1 regions — a limitation of the earlier drought trigger noted explicitly in the 2021 evaluation report.

## Changes from previous version

First version — no prior published flood framework to supersede.

## Open questions / known issues

- What return period threshold would trigger activation? (1-in-3? 1-in-5?)
- Which woredas / Admin1 regions are in scope? (Gambella, Afar, Somali, others?)
- What is the area fraction required — must multiple woredas exceed the threshold?
- What is the pre-arranged funding envelope and which CERF mechanism?
- Which implementing agencies would act, and what are the pre-agreed actions?
- The `cumulus` package that provides `pg_load_seas5_historical()` and `seas5_aggregate_forecast()` is not part of this repo — is it ocha-stratus or a separate internal library? This must be resolved before the trigger can be operationalized.
- Is there a companion monitoring repo or dashboard under development?
