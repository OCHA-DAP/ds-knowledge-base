---
content_type: analysis
analysis_type: pre-framework   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: syr-drought
version: pre-development
status: pre-development
country_iso3: SYR
hazard: drought
admin_level: 1
geographic_scope: []
data_sources: [ASI, ERA5]
trigger_facets:
  basis: observational
  calibration: return-period
  indicators: [ASI, ERA5-seasonal-rainfall]
  n_windows: 0
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
apps: ["https://book-aa-syria-drought.netlify.app"]
depends_on: []
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-syr-drought
source_branch: main
source_sha: e359524
code_ref:
  - book_syr_drought/01_asi.qmd
  - book_syr_drought/02_era5.qmd
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No formal trigger thresholds defined — the repo computes empirical return periods for ASI and ERA5 rainfall but sets no activation threshold or decision rule."
  - "[gap] No framework document exists (no published PDF, no CERF endorsement, not in the CERF AA Portfolio as of November 2024)."
  - "[gap] No action plan, financing arrangement, or implementing agency documented anywhere in the repo."
  - "[conflict] 02_era5.qmd on main hard-codes 'iso3 <- c(\"SYR\",\"SOM\")[2]', which selects SOM — so the committed ERA5 chapter actually runs the Somalia analysis (Gu season Mar-Jun, Somali ADM1 regions Awdal/Woqooyi Galbeed/etc.), NOT Syria. The merged main state of the Syria ERA5 chapter renders Somalia output; the iso3 index must be set to [1] to produce the Syria (Nov-Apr) analysis the framework scope intends."
  - "[stale] get_cogs_to_process in 02_era5.qmd carries an unused SEAS5 branch (dataset == 'seas5' leadtime logic) that is never exercised — only the era5 branch runs. Forward-looking scaffolding for a possible forecast-based trigger, not part of the current observational analysis."
  - "[stale] 01_asi_somalia.qmd exists in book_syr_drought/ but is NOT registered in _quarto.yml chapters (only index, intro, 01_asi, 02_era5 are listed), so it is not rendered in the book — companion Somalia ASI analysis left in the repo but out of the build."
  - "[stale] 02_era5.qmd writes/reads the projects blob via cumulus::blob_containers(\"dev\") (dev storage slot) while pulling rasters from the prod raster container — dev-slot deployment, not a prod pipeline."
  - "[stale] _quarto.yml intro and summary chapters contain placeholder text ('This is a book created from markdown and executable code', 'this book has no content whatsoever'), indicating the analysis book scaffold was never fully written out."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "n_windows is 0 because no formal activation windows or trigger thresholds exist — this is exploratory indicator analysis, not an operational framework."
  netlify_app: "https://book-aa-syria-drought.netlify.app (Quarto book, id 6448b267-03d9-4a23-bded-631925132d09)"
  context: "Repo created June 2025 in response to FAO alert that 2024/25 winter drought was worst in 36 years. Analysis uses cumulus R package for ASI (FAO GIEWS) and ocha-stratus DB for ERA5 tabular stats. Somalia analysis was later added as a companion analysis on the era5-somalia branch (merged Sep 2025)."
visibility: internal
last_synced: "2026-06-17"
---

# Syria Drought — pre-development

> **Analysis, not a framework** (reclassified 2026-06-17): early analysis; no published framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary

This framework is in pre-development: there is no published framework document, no CERF endorsement, and no formal trigger threshold. The repository (`ds-aa-syr-drought`) is an exploratory Quarto analysis book computing empirical return periods for two candidate indicators — FAO GIEWS Agricultural Stress Index (ASI) and ERA5 seasonal precipitation — across Syrian governorates (ADM1) for the 2024/25 winter cropping season (November–April). The analysis was motivated by the 2024/25 drought being the most severe in 36 years according to FAO. No action plan or pre-arranged funding is in place. Syria does not appear in the CERF AA Portfolio (as of the November 2024 portfolio update).

## Method

The analysis uses two observational data sources:

1. **ASI (Agricultural Stress Index)** — retrieved via the `cumulus` R package from FAO GIEWS, at ADM1 level, filtered to dekad 3 of each month across the winter season (Nov, Dec, Jan, Feb, Mar, Apr). Empirical return periods are calculated per governorate per month using the formula `RP = 1 / (rank / (n+1))`, with direction = −1 (higher ASI = more stress = rarer event).

2. **ERA5 seasonal precipitation** — loaded from the OCHA stratus database (tabular ADM1 stats). Monthly mm/day values are converted to mm/month, summed to a seasonal total, and ranked to compute empirical return periods (direction = +1 for rainfall deficit). The same return-period function is applied. Additionally, raster COGs are loaded directly from Azure blob storage to produce spatial anomaly maps.

Both analyses produce per-governorate return period maps and time-series charts. There is no combined indicator, no defined threshold, and no triggering decision rule.

## Trigger logic

- **Keys off:** ASI from FAO GIEWS (via `cumulus`) and ERA5 seasonal rainfall from the OCHA DB/blob.
- **Decision rule (plain language):** None defined. The analysis characterises the severity of the 2024/25 season by computing empirical return periods for both indicators. No activation threshold has been set.
- **Activation structure:** Not defined.
- **Calibration:** Empirical return periods using historical record length available in FAO GIEWS ASI data and the ERA5 DB table. No target return period (e.g. 1-in-5 year) has been specified for framework activation.
- **Authoritative source:** No framework PDF exists. Trigger source is the repo analysis only.
- **Operated by:** n/a (no live trigger system).

## Trigger windows

No formal activation windows have been defined (`n_windows: 0`). The analysis covers the full winter cropping season (November–April at ADM1 level) but defines no activation window, threshold, or decision rule, so the table below has no rows.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| _(none — no activation window defined)_ |  |  |  |  |  |  |

## Sources & repo completeness

- **Trigger taken from:** repo (no framework PDF exists).
- **Repo completeness:** partial — the indicator analysis (return period computation for ASI and ERA5) is present for the 2024/25 season, but there is no formal trigger design, no threshold, no action plan documentation, and several chapters of the Quarto book contain placeholder text.
- **Discrepancies:** see frontmatter `discrepancies` list. Key gaps: no formal trigger thresholds, no framework doc, no action plan/financing. Key conflict: `02_era5.qmd` on `main` hard-codes `iso3 <- c("SYR","SOM")[2]`, which selects **SOM** — so the committed ERA5 chapter actually renders the **Somalia** analysis (Gu season, Somali ADM1 regions), not Syria; the index must be `[1]` to produce the intended Syria output. Stale/scaffolding: an unused SEAS5 branch in `get_cogs_to_process`, the `01_asi_somalia.qmd` companion file not registered in `_quarto.yml` chapters, the dev blob slot for the projects container, and placeholder text in the intro/summary chapters.

## Monitoring

No operational monitoring pipeline exists. The Quarto book is deployed to Netlify (`https://book-aa-syria-drought.netlify.app`) and rendered from R code pulling live data from FAO GIEWS (ASI) and the OCHA stratus database (ERA5). Re-running the book re-executes the analysis but there is no scheduled pipeline or alert system.

## Historical activations

Never activated. No AA framework has been formally endorsed for Syria drought, and no pre-arranged funds have been released.

## Key decisions & rationale

The choice of ASI (Agricultural Stress Index from FAO GIEWS) as the primary indicator reflects the agricultural focus of drought impacts in Syria — ASI captures crop stress across the growing season rather than just precipitation deficit. ERA5 is used as a complementary precipitation-based indicator to contextualise ASI anomalies with observed rainfall deficits. Both are observational indicators (not forecasts), which is appropriate for a retrospective severity assessment but limits anticipatory lead time if carried forward to a formal framework. The spatial unit is ADM1 (governorate), matching the available ASI tabular data granularity.

The 2024/25 season was characterised as the worst drought in 36 years by FAO, providing the immediate motivation for this analysis. No formal framework design decisions (trigger return period, geographic scope restriction, financing) have been documented.

## Changes from previous version

First version; no prior framework exists for Syria drought.

## Open questions / known issues

- Is this analysis intended to develop into a formal CERF-endorsed AA framework, or was it a one-off situational analysis for the 2024/25 crisis response?
- Which governorates would be in scope for an AA framework trigger (all 14 ADM1 units, or a subset focused on the main wheat-growing areas)?
- What target return period would be appropriate for an AA threshold (the standard CERF/OCHA 1-in-3 to 1-in-5 years)?
- Would the framework use ASI alone, ERA5 alone, or a combined indicator? And would it shift to a forecast-based trigger (e.g. SEAS5) for anticipatory lead time?
- The Somalia ASI/ERA5 analysis co-located in the same repo (`01_asi_somalia.qmd`, and the `[2]`→SOM toggle in `02_era5.qmd`) — is this the seed of a separate Somalia framework, or a comparison exercise? Note the committed ERA5 chapter currently renders Somalia, not Syria, because of the hard-coded `[2]` index.
- The Quarto book's intro and summary chapters still contain placeholder text, suggesting the analytical narrative is incomplete.
