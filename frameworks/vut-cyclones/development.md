---
content_type: framework
framework: vut-cyclones
version: development
status: development
country_iso3: VUT
hazard: tropical-cyclone
admin_level: 2
geographic_scope: [Sanma, Shefa, Tafea]   # pcodes VU02, VU05, VU06
data_sources: [IBTrACS, IMERG, FMS, WorldPop, EM-DAT]
trigger_facets:
  basis: observational
  calibration: return-period
  indicators: [IBTrACS-usaradii-wind-exposure-64kt, IMERG-2day-rainfall-mean]
  n_windows: 1
  window_axes: []
monitoring_period:
  months: [11, 12, 1, 2, 3, 4]
  source: inferred
  note: "South Pacific cyclone season (~Nov–Apr); inferred from basin seasonality. Page does not state explicit season months."
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
apps: [https://ocha-dap.github.io/ds-aa-vut-cyclones/]
depends_on: []
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-vut-cyclones
source_branch: 2026-workshop
source_sha: 7e5afb4
code_ref:
  - exploration/trigger_explorer.py
  - exploration/make_trigger_data.py
  - exploration/quick_trigger_aoi.md
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No endorsed framework PDF exists; trigger design is under active development on branch 2026-workshop. The interactive trigger explorer presents candidate thresholds but no threshold has been formally fixed."
  - "[stale] exploration/make_trigger_data.py and exploration/quick_trigger*.md filter seasons >= 2001, but the underlying wind-exposure parquet (sourced from pa-aa-fji-storms) starts from season 2003. The trigger_explorer.py was corrected (commit 1fa053e) to use 2003 as the start year (23 seasons); the older notebooks still contain 2001 (25 seasons), giving a slightly different implied return period (would-be 6 storms in 25+1 seasons = RP 4.3 vs 4.0 at 23+1). These are stale artefacts; the trigger_explorer is the live analysis."
  - "[conflict] GHA workflow run_update_info_emails.yml hardcodes ref: 'add-monitoring', but the main analysis branch is 2026-workshop. The monitoring pipeline therefore runs off an older branch that predates the trigger explorer work."
  - "[gap] No fixed trigger threshold has been agreed; trigger_explorer.py defaults to 100k people exposed to 64kt wind AND 100mm 2-day rainfall as exploratory starting values, not an endorsed decision."
  - "[gap] Cyclone LOLA (October 2023, season 2024) received a CERF allocation but has zero 64kt wind exposure in IBTrACS. The current 64kt-only trigger design would not have captured LOLA; this known gap is not yet resolved in the framework design."
  - "[conflict] Monitoring lead-time mismatch: pipelines/update_info_emails.py truncates the FMS forecast to 72h (leadtime <= 72) BEFORE calling calculate_distances, whereas src/datasources/fms.py:calculate_distances internally clips to 120h and interpolates to 30-min. The effective live horizon is therefore 72h, not the 120h the helper appears to support."
  - "[stale] src/datasources/fms.py:calculate_distances docstring says it computes distances to 'adm2 and adm3', but the code actually loops over admin levels [1, 2] (adm1 and adm2) and returns only the adm1 frame. The docstring is stale relative to the code."
  - "[gap] email_utils.TEST_LIST defaults to True (only the literal env string 'False' disables it), so the monitoring pipeline sends to the TEST distribution list (email/test_distribution_list.csv) by default rather than the live list — a dev/test-slot default that would need flipping for real operations."
  - "[stale] The add-monitoring branch (which the GHA workflow checks out) carries an older src/datasources/fms.py than 2026-workshop: it still references blob.PROJECT_PREFIX for the FMS blob path instead of the corrected src.constants.PROJECT_PREFIX. The live monitoring runs this older companion code."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  doc_status: "in-development framework; doc exists but is not public"
  aoi_provinces: "Shefa (VU05), Sanma (VU02), Tafea (VU06) — the three provinces used to restrict wind-exposure calculation"
  info_email_distance_threshold_km: 1000
  cerf_sids_tracked: [2015066S08170, 2020092S09155, 2023055S14184, 2023059S15149, 2023292S03172]
  schema_strain: "No framework_doc exists; trigger_source=repo and version=development used per INGESTION.md guidance for pre-endorsed work."
visibility: internal
last_synced: 2026-06-17
---

# Vanuatu Tropical Cyclones — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.
> No endorsed framework PDF exists. Trigger design is under active development on branch `2026-workshop`.

## Summary

This framework is under development for Vanuatu tropical cyclone anticipatory action. The design keys off historical wind exposure (population within IBTrACS USA-radii wind buffers at 34/50/64kt) and IMERG two-day rainfall, targeting a ~1-in-4-season return period (≈6 activations over the 2003–2025 record). Three AOI provinces — Shefa, Sanma, and Tafea — define the spatial scope for wind-exposure counting. A monitoring pipeline sends informational emails based on FMS forecasts when a tropical cyclone is within 1,000 km of Vanuatu. No trigger threshold has been formally endorsed; an interactive Marimo app (deployed on GitHub Pages) allows stakeholders to explore threshold combinations.

## Method

**Historical calibration (retrospective):** IBTrACS v4 USA-radii wind buffers (34/50/64kt) are intersected with WorldPop 2026 admin-2 population grids (expanded 500 m into coastal ocean) for all South Pacific storms since 2003 in the three AOI provinces. IMERG daily mean rainfall across Vanuatu (country-level pcode VU) is used to compute a 2-day rolling sum; the maximum value in a ±1-day window around each storm's track passage within 250 km is taken as the storm's rainfall indicator. EM-DAT Total Affected and CERF allocation history are overlaid to validate indicator choices.

**Interactive exploration:** The `trigger_explorer.py` Marimo notebook lets users set a wind-speed tier (34/50/64kt), a wind-exposure people threshold, a rainfall threshold (mm), and AND/OR logic. It displays return period and Total Affected captured for any combination, targeting 6 storms (≈ RP 4.0 over 23+1 seasons).

**Monitoring (operational):** The `pipelines/update_info_emails.py` script, triggered via GitHub Actions, ingests FMS tropical cyclone forecast CSVs (base64-encoded), computes the forecast track's minimum distance to each admin-1 and admin-2 province, and sends informational emails to a distribution list when the storm is within 1,000 km. This is an informational/monitoring pipeline, not a formal trigger.

## Trigger logic

- **Keys off:** IBTrACS USA-radii wind-exposure (population exposed to ≥64kt over AOI provinces) AND IMERG 2-day mean rainfall over Vanuatu (mm). Both indicators measured against historical record.
- **Decision rule (plain language):** Trigger fires if — in the historical record — a storm would have ranked in the top 6 over 23 seasons for the chosen combination of wind exposure and rainfall. The return period target is ~1-in-4 seasons. No formal threshold is fixed yet.
- **Activation structure:** Single window; AND logic is the working design assumption (both wind AND rainfall must exceed thresholds). The explorer also supports OR for comparison. No readiness/action split documented in the repo.
- **Calibration:** Return-period based. 23 seasons (2003–2025 inclusive) used as the reference period for the trigger explorer. Target is 6 storms at RP ≈ 4.0 seasons (formula: (23+1)/6 = 4.0). Default slider values in the explorer (100k people at 64kt AND 100mm rainfall) are exploratory, not endorsed.
- **Authoritative source:** Repo only (`trigger_source: repo`) — no published framework PDF. The `code_ref` is the canonical analysis.
- **Operated by:** OCHA Centre for Humanitarian Data (repo owner). No external operational system.

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| activation | observational (wind exposure + rainfall, both retrospective) | IBTrACS USA-radii pop. exposed to ≥64kt wind (AOI: Shefa, Sanma, Tafea) AND IMERG 2-day mean rainfall (country) | not fixed — explorer default 100k people AND 100mm | not defined | ~1-in-4 seasons (target 6 storms / 23 seasons) | not defined |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no published framework PDF exists.
- **Repo completeness:** `partial` — the exploratory analysis (IBTrACS wind-exposure calculation, IMERG aggregation, trigger explorer app) is present and well-developed on the `2026-workshop` branch. However, no fixed threshold has been agreed, no endorsement has occurred, and the monitoring pipeline runs off the `add-monitoring` branch (an older branch), creating a drift gap between the live monitoring system and the trigger analysis.
- **Discrepancies:** See frontmatter `discrepancies` field for full tagged list. Key items: (1) GHA workflow hardcodes `add-monitoring` branch rather than `2026-workshop`; (2) several exploration notebooks still carry `season >= 2001` (stale, corrected in the main explorer); (3) LOLA (zero 64kt exposure, CERF-allocated) is a known gap in the 64kt-only trigger design.

## Monitoring

- **What:** FMS tropical cyclone forecast CSV ingestion → minimum track distance to Vanuatu admin-1 and admin-2 → informational email to distribution list.
- **Cadence:** On-demand / workflow_dispatch via GitHub Actions (`run_update_info_emails.yml`). Emails sent only when cyclone is within 1,000 km.
- **Branch:** GHA workflow uses `ref: add-monitoring` (not `2026-workshop`). The pipeline (`update_info_emails.py`) truncates the FMS forecast to a **72-hour (3-day)** horizon before computing distances, so the effective monitoring lead time is 72h — even though the underlying `calculate_distances` helper internally clips to 120h and interpolates the track to 30-minute intervals.
- **Distribution list:** `email_utils.TEST_LIST` defaults to `True` unless the `TEST_LIST` env var is the literal string `"False"`, so by default the pipeline sends to the **test** distribution list (`email/test_distribution_list.csv`), not the live list — a dev/test-slot default.
- **App:** Interactive trigger explorer deployed as WASM Marimo notebook at `https://ocha-dap.github.io/ds-aa-vut-cyclones/` (2026-workshop branch, GH Pages). Data pre-computed to `exploration/public/trigger_data.csv`.

## Historical activations

Never activated as a formal AA trigger — the framework is under development and has not been endorsed. No CERF AA allocation exists for Vanuatu cyclones.

Five past cyclones with CERF **rapid-response** allocations (not AA) are tracked as calibration references: Pam (2015), Harold (2020), Judy (2023), Kevin (2023), Lola (October 2023/season 2024). These are encoded in `src/constants.py` as `CERF_SIDS` and overlaid on the trigger explorer as a validation signal.

## Key decisions & rationale

- **AOI restricted to three provinces:** Shefa (VU05), Sanma (VU02), and Tafea (VU06) were selected as the Area of Interest for wind-exposure counting because they contain the most exposed population and have historically experienced the greatest cyclone impacts. The country-wide wind-exposure calculation was found to correlate less well with CERF allocations.
- **USA radii over WMO:** IBTrACS USA-provider wind radii are used (over WMO) because they have better historical coverage and consistency for the South Pacific basin. The `wind_provider="usa"` choice is explicit in `src/datasources/ibtracs.py`.
- **64kt as the headline indicator:** 64kt (hurricane-force) wind exposure showed the strongest correlation with both EM-DAT Total Affected and CERF allocation in the exploratory analysis. The 34kt and 50kt tiers are retained in the explorer for comparison.
- **IMERG rainfall as a second indicator:** Added because some high-impact events (e.g. Cook 2017) had significant rainfall impacts without large 64kt wind footprints. The AND/OR exploration in the explorer is specifically designed to handle LOLA-type events (high impact, low 64kt wind).
- **Target RP of 4:** Chosen as a reasonable balance between coverage and false alarm rate, consistent with CERF anticipatory action norms. Generates a target of 6 storms over 23 seasons.
- **LOLA tension:** Lola (Oct 2023, season 2024) had zero 64kt wind exposure in IBTrACS but received a CERF rapid response allocation and caused 91,000 affected. Current 64kt-based trigger would not have captured Lola. This is a known unresolved design question.

## Changes from previous version

No prior version — this is the first iteration of the framework.

## Open questions / known issues

- No endorsed threshold: the trigger explorer's default values (100k people / 100mm) are starting points for stakeholder discussion, not an agreed trigger.
- LOLA coverage gap: how to handle extreme-rainfall / Category-1-2 events that cause significant impact but fall below 64kt thresholds? OR logic with a rainfall-only path is the most likely resolution.
- Monitoring pipeline branch drift: GHA workflow `run_update_info_emails.yml` checks out `add-monitoring`, not `2026-workshop`. This means the live monitoring pipeline does not reflect the current trigger design. Should be updated to track the active branch.
- Season range inconsistency: `make_trigger_data.py` and older exploration notebooks still filter `season >= 2001` despite the underlying wind-exposure data starting in season 2003. These should be harmonized. The trigger_explorer.py was corrected in commit `1fa053e` but `make_trigger_data.py` was not updated, meaning the WASM app's data (trigger_data.csv) was generated with the 2001 filter (data is unaffected since no storms exist in 2001/2002 in the wind buffer dataset, but the return-period calculation in the script is conceptually wrong).
- No formal lead-time design: the framework currently has no defined action timeline (readiness vs. action windows), budget envelope, or implementing agency assignments.
