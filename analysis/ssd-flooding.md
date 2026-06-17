---
content_type: analysis
analysis_type: ad-hoc-activation   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: ssd-flooding
version: development
status: development
country_iso3: SSD
hazard: flood
admin_level: 0
geographic_scope: [SS]
data_sources: [SEAS5, ERA5, Floodscan, IRI, EM-DAT]
trigger_facets:
  basis: forecast
  calibration: return-period
  indicators: [SEAS5-precip-mean, ERA5-precip-mean, Floodscan-exposure, IRI-above-normal-prob]
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
raw_extract:
  - /tmp/phase2-batch2/raw/ssd-flooding_2022lessons.txt
  - /tmp/phase2-batch2/raw/ssd-flooding_early-action.txt
  - /tmp/phase2-batch2/raw/ssd-flooding_roadmap.txt
# --- live system ---
operated_by: null
apps: []
# --- source repo & reconciliation ---
depends_on: []
source_repo: ocha-dap/ds-aa-ssd-flooding
source_branch: subnational-impact
source_sha: 9f62481
code_ref:
  - exploration/seas5.md
  - exploration/seas5_skill.md
  - exploration/impact_comparison.md
  - exploration/iri.md
  - src/datasources/seas5.py
  - src/datasources/era5.py
  - src/datasources/iri.py
  - src/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No endorsed trigger threshold exists: the 2022 CERF allocation was explicitly NOT a formal AA framework (OCHA's own documentation states 'the predictive strength of forecasts was limited for South Sudan' and the action was a pilot without a pre-agreed quantitative trigger). No framework doc URL exists."
  - "[gap] Seasonal forecast (SEAS5 issued June, valid JAS) and IRI exploratory analyses in the repo are analytical candidates for a future trigger (1-in-3-year or 1-in-5-year RP thresholds explored), but no threshold has been agreed or endorsed."
  - "[gap] The IRI datasource module (src/datasources/iri.py) loads data from a local filesystem path (AA_DATA_DIR_NEW env variable) rather than the blob — may be stale or only functional on the original author's machine; the iri.nc it reads is not reproducibly fetched in-repo."
  - "[stale] The src/datasources and src/utils modules predate the ocha-stratus convention: seas5.py and era5.py use a hand-rolled src/utils/db_utils.get_engine() (raw psycopg2 + DSCI_AZ_DB_* SAS/password env vars), and blob_utils.py uses the raw azure-storage-blob SDK. Only codab.py imports ocha_stratus. The team standard is to use ocha-stratus for ALL DB/blob access — these are legacy local helpers, not the live pattern."
  - "[stale] codab.py writes/reads the CODAB from the DEV blob slot (stage=\"dev\"), and both db_utils.get_engine and blob_utils default to stage=\"dev\"/dev hosts. Analysis that mixes dev-slot CODAB with prod-slot raster stats is a local-convenience artifact, not a deployment config."
  - "[stale] CERF_YEARS = [2019, 2020, 2021, 2022, 2024] in src/constants.py encodes historical CERF flood response years for correlation analysis. These were all rapid-response or pilot early-action allocations, NOT formal AA framework activations — using this list as a trigger-fired indicator would be misleading."
  - "[gap] The subnational_impact.md notebook (branch: subnational-impact) attempts to load 2022 and 2024 county-level impact data but is unfinished: one cell is a bare isinstance() call with no arguments (raises TypeError at runtime) and the next, df_in = df_in[df_in[\"Affected People\"]], boolean-indexes on a non-boolean column (also broken) — clearly work-in-progress, so the 2022/2024 subnational impact join is not actually computed."
  - "[stale] A companion repo pa-ssd-flooding-blog exists locally but is an abandoned project scaffold (README badge STATUS: ON HOLD, constants.py only ISO3 = ssd, placeholder template notebooks). It contains NO South Sudan flood trigger analysis; do not mistake it for a second analysis home — all real analysis is in ds-aa-ssd-flooding."
  - "[stale] The ds-aa-ssd-flooding README still describes the project as 'Analysis for flooding in South Sudan in 2025', but the active subnational-impact branch reads 2024 impact data and the impact_comparison analysis runs through 2024 — the README header is a stale single-season framing, not the current scope."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "No framework doc exists; trigger_source=repo and framework_doc=null are the correct representation. The 2022 CERF 'early action' is documented but was explicitly non-trigger-based — it is NOT an activation of a formal AA framework and should not be counted as such. The national Roadmap 2025-2030 (published 2026-01-06) is a strategic planning document, not a technical trigger specification."
  cerf_early_action_2022: "CERF US$15M + SSHF US$4M = US$19M allocated May 2022 for Unity State flooding (Bentiu). This was a risk-analysis-based early allocation without a pre-agreed trigger mechanism. Six implementing agencies: FAO, IOM, UNFPA, UNHCR, UNICEF, WHO. Approx 320,000 people at risk in Unity State; Bentiu IDP camp (100,000+ IDPs) was the focus."
  cerf_rapid_response_2024: "CERF US$10M rapid response allocated 5 September 2024 for floods affecting ~1M people in 5 priority counties (Northern Bahr el Ghazal, Upper Nile, Unity, Jonglei). Post-event rapid response, not anticipatory."
  national_roadmap: "South Sudan Roadmap on Anticipatory Action 2025-2030 (SSRAA), published 2026-01-06 by Government of South Sudan/MHADM with WFP, FAO, SSRC, IGAD/ICPAC. Six strategic pillars including Trigger and Early Warning Systems. Establishes intent to develop formal AA frameworks; does not itself define a trigger."
  repo_analysis_focus: "SEAS5 issued June, valid JAS (July-Aug-Sep) is the primary candidate trigger window based on impact_comparison.md analysis. ERA5 detrended JAS correlation with Floodscan and EM-DAT impact explored. IRI above-normal probability (April forecast, leadtime 3 for JAS) also evaluated for watershed of White Nile at exit from South Sudan."
visibility: internal
last_synced: 2026-06-17
---

# South Sudan Flood — development

> **Analysis, not a framework** (reclassified 2026-06-17): ad-hoc anticipatory action, not a published framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> The canonical trigger (when one exists) will be the code at `code_ref`; this page explains the current analytical work, it does not define a trigger.

## Summary

South Sudan has faced five consecutive years of unprecedented flooding (2019–2024), with the White Nile basin and Sudd wetlands at the core. OCHA's Centre for Humanitarian Data has been building toward a formal flood anticipatory action framework since 2022, but no endorsed trigger exists. The 2022 CERF allocation (US$19M) was an explicitly non-framework "early action pilot" based on risk analysis rather than a quantitative forecast trigger. The repo (`ds-aa-ssd-flooding`) currently contains exploratory analysis evaluating SEAS5 and IRI seasonal precipitation forecasts, ERA5 observed precipitation, and Floodscan exposure as candidate trigger indicators — the analytical groundwork for a future endorsed framework. A national roadmap (SSRAA 2025-2030) published January 2026 establishes government intent to institutionalize AA including formal trigger mechanisms.

## Method

The repo evaluates whether seasonal precipitation forecasts can predict flood impact with sufficient skill to support a trigger-based AA framework. Analysis proceeds in three steps:

1. **Data**: SEAS5 seasonal forecast (DB `public.seas5`), ERA5 observed precipitation (DB `public.era5`), Floodscan flood exposure (DB `app.floodscan_exposure`), IRI seasonal forecast probability (`iri.nc`), and EM-DAT flood impact data.
2. **Skill assessment**: For each combination of issue month and valid month, compute SEAS5–ERA5 correlation and True Positive Rate at a return-period threshold (typically 1-in-5-year). The `exploration/seas5_skill.md` notebook generates skill heatmaps.
3. **Impact validation**: `exploration/impact_comparison.md` correlates SEAS5 forecasts, Floodscan exposure, and EM-DAT impact records (2000–2024), testing 2- and 5-year RP thresholds on detrended and raw series. CERF years (2019–2024) are used as a proxy for severe flood years in correlation analysis.

The most promising candidate window identified in the analysis is a **June-issued SEAS5 forecast valid for July–August–September (JAS)**, applied to the whole-country pcode `SS`. The IRI notebook evaluates above-normal rainfall probability for the Nile watershed exiting South Sudan (April-issued, leadtime 3 for JAS).

## Trigger logic

- **Keys off:** SEAS5 mean precipitation for `SS` (issued June, valid JAS), and/or IRI above-normal probability for the White Nile watershed
- **Decision rule (plain language):** No decision rule is currently endorsed. Exploratory thresholds tested include 1-in-3-year and 1-in-5-year return periods on detrended SEAS5 JAS precipitation. Would fire when the seasonal forecast exceeds the historical quantile threshold.
- **Activation structure:** Single window; no staged readiness/action split defined yet.
- **Calibration:** Return-period based (empirical rank), tested on 1981–2024 SEAS5 data. Detrending applied to remove trend signal from both SEAS5 and ERA5 series.
- **Authoritative source:** None — no published framework PDF. Analysis is in the repo.
- **Operated by:** OCHA/CHD (analysis); no live monitoring system deployed.

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| JAS seasonal (candidate) | forecast | SEAS5 precip mean (SS, issued Jun); IRI above-normal prob (Nile watershed) | Not yet defined — 1-in-3-yr or 1-in-5-yr RP explored | ~1–3 months | 1-in-3 yr or 1-in-5 yr (under evaluation) | Not yet defined |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no published framework document exists.
- **Repo completeness:** partial — exploratory analysis notebooks are present (SEAS5, ERA5, IRI, Floodscan, EM-DAT) but no trigger code, no threshold has been agreed, and the subnational impact notebook has an unfinished code cell.
- **Discrepancies:** See frontmatter `discrepancies` field for the full tagged list. Key issues: (1) [gap] no endorsed threshold; (2) [stale] the `src/datasources` + `src/utils` modules predate ocha-stratus — `seas5.py`/`era5.py` use a hand-rolled `db_utils.get_engine` and `blob_utils` uses the raw Azure SDK; only `codab.py` uses stratus, and it targets the dev blob slot; (3) [gap] `iri.py` reads from a local filesystem path; (4) [gap] `subnational_impact.md` has two broken WIP cells (`isinstance()` with no args; boolean-index on a non-boolean column); (5) [stale] companion repo `pa-ssd-flooding-blog` is an empty on-hold scaffold.

## Monitoring

No live monitoring pipeline is deployed. The exploratory notebooks require manual execution against the production database. The `exploration/seas5.md` notebook shows a "current vs. historical" plot for a given pcode, but is not automated.

## Historical activations

**No formal AA framework activations.** The framework does not yet have an endorsed trigger.

Two related CERF allocations occurred outside a formal AA framework:

- **2022 early action pilot**: CERF US$15M + SSHF US$4M (May 2022) for Unity State (Bentiu IDP camp focus). Six agencies: FAO, IOM, UNFPA, UNHCR, UNICEF, WHO. Approx 320,000 people at risk. Explicitly described by OCHA as "not a formal AA framework" — based on risk analysis (Floodscan historical levels, expert judgment) rather than a quantitative forecast trigger. Constructed/reinforced 55+ km of dykes; prevented evacuation of 100,000+ IDPs.
- **2024 rapid response**: CERF US$10M (5 September 2024) for flood-affected populations (~1M people in 5 counties). Post-event rapid response, not anticipatory.

## Key decisions & rationale

- **2022 "early action" approach**: OCHA concluded in March 2022 that forecast reliability for the Sudd wetlands was insufficient for a formal AA framework (complex water flow, absence of reliable hydrological data, limited weather observation network). Rather than not act, OCHA piloted a risk-analysis-based early allocation. The CERF portfolio update (Nov 2024) explicitly notes this "*was based on forecasts without a formalized framework in place*" and marks South Sudan as "*not currently active with CERF support*."
- **SEAS5 as primary candidate**: June-issued SEAS5 for JAS provides ~1–3 months lead time before peak flooding. The impact_comparison.md analysis finds meaningful correlation between SEAS5 JAS forecasts and both Floodscan exposure and EM-DAT impact — though evidence from a small number of years.
- **Detrending**: ERA5 and SEAS5 series are detrended to remove the upward precipitation trend in South Sudan, to avoid inflating RP estimates.
- **National roadmap 2025-2030**: The SSRAA (published Jan 2026) by the Government of South Sudan signals transition from pilot early actions to institutionalized trigger-based AA. It identifies limited forecasting accuracy and fragmented early warning as key barriers.

## Changes from previous version

First version; no predecessor.

## Open questions / known issues

- What quantitative threshold (RP, percentile, absolute) and which indicator(s) will the endorsed trigger use?
- How will the Sudd wetland baseline-flood problem be handled — multi-year standing water means "above-normal rainfall" has higher flood impact than historical averages suggest?
- Can the IRI module be migrated to ocha-stratus, and is the IRI data for the Nile watershed reliable enough to use alongside SEAS5?
- What geographic scope will be targeted — whole country (`SS`), Unity State, or specific high-flood-risk states?
- How will the SSRAA trigger and early warning pillar coordinate with OCHA/CHD's analytical work?
- Is there a 2025 trigger analysis planned, given the 2025 rainy season brought major floods (>1.3M people affected per SSRAA Jan 2026)?
