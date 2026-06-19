---
content_type: analysis
analysis_type: regional-overview   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: [bfa-drought, ner-drought, mrt-drought, tcd-drought]   # framework(s) this analysis supports
framework: sahel-drought
version: "2022-09-29"
status: triggered
country_iso3: [BFA, NER, TCD]
hazard: drought
admin_level: 1
geographic_scope:
  - "BFA: Boucle de Mouhoun, Centre Nord, Sahel, Nord"
  - "NER: national (all south of 17°N)"
  - "TCD: Lac, Kanem, Barh-El-Gazel, Batha, Wadi Fira"
data_sources: [IRI, CHIRPS, ECMWF-SEAS5, ERA5, ASAP, SPI]
trigger_facets:
  basis: mixed
  calibration: percentile
  indicators: [IRI-tercile-prob, SPI, NDVI-biomass-anomaly]
  n_windows: 8
  window_axes: [time, space]
supersedes: null
# funding and scope

prearranged_funding_usd: 45000000
funding_by_source: {CERF: 45000000}
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: [FAO, UNDP, UNFPA, UNHCR, UNICEF, WFP, WHO]
target_people: null
# documents, authority-ranked
framework_doc: "https://www.unocha.org/attachments/5be0e3d1-6621-4cbc-96c7-e0fb7ccbcb5b/CERF_Pamphlet-AA-Sahel_20220929.pdf"
framework_doc_date: "2022-09-29"
framework_doc_annexes: []
languages: [en]
model_report: "https://centre.humdata.org/model-report-drought-anticipatory-action-trigger-in-burkina-faso/"
raw_extract:
  - /tmp/phase2-batch2/raw/sahel-drought_doc.txt
# live system
operated_by: "IRI (Niger monitoring only — activation protocol assigns IRI as the monitoring/alerting entity for NER; CHD does BFA and TCD)"
apps: []
# source repo and reconciliation
depends_on: []
source_repo: ocha-dap/ds-aa-sahel-drought
source_branch: ecmwf-historical
source_sha: e5ff27e
code_ref:
  - exploration/iri_historical.md
  - exploration/ecmwf_2024.md
  - exploration/historical_comparison.md
  - src/utils.py
trigger_source: framework_doc
repo_completeness:
  analysis: partial
  deployed_code: lost
discrepancies:
  - "[stale] The ecmwf-historical branch explores ECMWF SEAS5 as an alternative to IRI for BFA and TCD triggers (files: exploration/ecmwf_2024.md, exploration/ecmwf.md, exploration/historical_comparison.md). The endorsed 2022 framework uses IRI as the authoritative forecast source for BFA and TCD, not ECMWF. ECMWF analysis appears to be exploratory work toward a future update, not the live trigger."
  - "[conflict] The iri_historical.md notebook encodes BFA trigger threshold as prob=40, frac=0.1 (40% below-average probability in ≥10% of monitored area). The framework PDF states: 'at least 10% of the monitored area meets: (1) forecast reaches 40% or more probability of below average rainfall AND (2) the probability of below average rainfall is 5 percentage points higher than that of above average rainfall.' The second criterion (5pp differential) is NOT present in the repo code — only the 40%/10% criteria are implemented."
  - "[gap] The iri_historical.md notebook encodes TCD T1/T2 threshold as prob=42.5, frac=0.2 (42.5% probability in ≥20% of area), which MATCHES the PDF (not a conflict). The gap is that the TCD biomass trigger (T3: ≥80% anomaly from September observation) has no corresponding code in the repo — only the IRI T1/T2 windows are implemented for TCD. (T3 gap also noted in the dedicated entry below.)"
  - "[gap] Niger's actual trigger logic is absent from the repo. The framework PDF specifies NER T1/T2 as IRI forecast of driest 35% years since 1991, and NER T3 as SPI negative AND in lowest 35% since 1991 (June–July, observed in August, only if T2 not met). IRI monitoring for Niger is assigned to IRI (Columbia) in the activation protocol. The repo has NO IRI-forecast NER evaluation (the iri_historical.md countries list contains only BFA and TCD — Niger is entirely omitted) and NO SPI computation. The only Niger-adjacent code is exploration/bad_years.md, which loads ner_bad_years.csv and ranks it against ECMWF reanalysis (`v{n}_rank < 32`) — this is exploratory bad-year identification, NOT the IRI/SPI NER trigger, and uses ECMWF rather than the endorsed IRI source."
  - "[gap] Chad T3 (September biomass observation, ≥80% anomaly threshold) is described in the PDF but has no implementation in the repo. The repo does not contain NDVI or biomass processing code for Chad."
  - "[stale] exploration/lac_support.md and exploration/lac_2024_support.md contain analysis for Central America (LAC dry corridor) reusing this repo's ECMWF utilities — unrelated to the Sahel drought trigger."
  - "[stale] exploration/mdg_iri_support.md contains Madagascar IRI analysis reusing this repo's infrastructure — unrelated to the Sahel drought trigger."
  - "[stale] The HEAD commit on the live branch (ecmwf-historical, e5ff27e, 'july 2024 monitoring', 2024-07-16) includes exploration/ecmwf_2024.md, which monitors BFA's 2024 ECMWF forecast against a 1/3-quantile (≈3-year return period) threshold — a DIFFERENT indicator and calibration than the endorsed IRI 40%/≥10%-area rule. This is dev/monitoring work toward an unendorsed ECMWF-based successor, not the live 2022 trigger; the 2022 framework PDF remains authoritative."
  - "[conflict] PDF-internal date inconsistency: the framework_doc filename encodes 2022-09-29 (used as this page's version), but the PDF body states 'Creation date: 17 October 2022'. The two dates disagree by ~3 weeks. version/framework_doc_date follow the filename (2022-09-29); the 17 Oct date is the document's stated creation date. Neither changes the trigger content."
  - "[stale] iri_historical.md backtests the IRI triggers over years 2017–2025, whereas the PDF defines NER thresholds relative to 'driest 35% of years since 1991'. The repo's BFA/TCD backtest window (2017+) is the available-IRI-data range, not the framework's 1991-baseline reference period; the two are different time bases and the repo does not reproduce the 1991-baseline percentile calculation."
# activation history
activations:
  - date: "2022-08"
    window: "NER T3 (SPI observational)"
    note: "Niger SPI for June–July 2022 placed southwest Niger within driest 35% of years since 1991 (lowest in ~30 years). CERF released USD 9.5 million via Rapid Response window. Reached 160,000+ people. Triggered before T2 seasonal forecast was met."
# escape hatch
extra:
  schema_strain: "This is a three-country multi-hazard framework (BFA + NER + TCD share one PDF) but each country has independent trigger windows, thresholds, and activation protocols. The single framework_doc covers all three — per-country PDFs do not exist. country_iso3 is a list; n_windows (8) counts all windows across the three countries. Funding of $45M is a ceiling across the full two-year commitment for all three countries combined; per-country breakdown not stated in the framework PDF."
  cerf_note: "CERF pre-arranged commitment is 'up to $45 million' for two years from each country's endorsement. BFA and NER endorsed 2022; TCD endorsement was pending as of the PDF date. No single per-country breakdown is provided in the overview doc."
  niger_monitoring_note: "For Niger, the activation protocol assigns IRI (Columbia University) as the primary monitor and alerter (steps 1–4). CHD plays that role for BFA and TCD. This is a structural feature of the multi-operator design."
  bfa_adm1_pcodes: [BF46, BF49, BF54, BF56]
  tcd_adm1_pcodes: [TD01, TD06, TD07, TD17, TD19]
visibility: internal
last_synced: "2026-06-17"
---

# Sahel (BFA/NER/TCD) Drought — 2022-09-29

> **Analysis, not a framework** (reclassified 2026-06-17): a regional pilots *overview* — the country components are the real frameworks. Feeds: bfa-drought, ner-drought, mrt-drought, tcd-drought. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> The canonical trigger is the code at `code_ref`; this page explains it — it does not redefine it. Note: the repo is partial; the authoritative trigger for Niger is operated by IRI (Columbia University), not this repo.

## Summary

Three-country OCHA-facilitated anticipatory action framework for drought in Burkina Faso (BFA), Niger (NER), and Chad (TCD), endorsed by the Emergency Relief Coordinator in 2022. Each country has its own geographic scope (specific admin-1 regions for BFA and TCD; all of southern Niger for NER) and 2–3 phased trigger windows. BFA and TCD use IRI seasonal rainfall forecasts; Niger uses both IRI forecast and an observational SPI fallback. Chad also includes a biomass observational trigger. The framework is backed by up to USD 45 million in pre-arranged CERF funding. The Niger framework was activated in August 2022 based on the SPI observational trigger.

## Method

Data flows through three distinct pathways:

1. **IRI seasonal forecast (BFA T1/T2, TCD T1/T2, NER T1/T2):** IRI seasonal forecast probability of below-average rainfall (low tercile) is computed over the in-season crop area (masked using ASAP crop calendar). The fraction of the monitored area exceeding the probability threshold is compared against a spatial coverage threshold. For BFA, a second condition requires the below-average probability to exceed the above-average probability by at least 5 percentage points. For NER, the trigger is expressed as forecast rainfall totals being in the driest 35% of years since 1991.

2. **SPI observational fallback (NER T3 only):** When NER T2 is not met, August SPI computed over June–July cumulative rainfall is checked. If SPI is negative AND in the lowest 35% of values since 1991, T3 activates. This observational trigger reduces the risk of inaction when a drought occurs but was not forecast.

3. **Biomass observation (TCD T3 only):** Analysis of September satellite biomass data. If the biomass anomaly reaches ≥80% anomaly threshold, TCD T3 activates.

Each trigger window is evaluated independently; only the funds for the triggered component are released.

## Trigger logic

- **Keys off:** IRI seasonal forecast (low tercile probability), CHIRPS/ERA5-based SPI (NER T3), NDVI/biomass anomaly (TCD T3)
- **Decision rule (plain language):** For BFA, if the March IRI forecast shows ≥40% probability of below-average rainfall AND that probability exceeds the above-average probability by ≥5pp, in ≥10% of the monitored crop area (BFA T1) → trigger. Same conditions on July forecast (BFA T2). For TCD, if March/April IRI forecast shows ≥42.5% probability in ≥20% of monitored area (TCD T1) or May/June shows same (TCD T2) → trigger. If September biomass anomaly ≥80% (TCD T3) → trigger. For NER, if January–March forecast places national rainfall totals in driest 35% since 1991 (NER T1) or April–June forecast does the same (NER T2) → trigger. If neither T1 nor T2 is met and August SPI is negative and in lowest 35% since 1991 → NER T3.
- **Activation structure:** Independent evaluation of each window; partial activation possible. BFA: 2 windows (T1 March forecast, T2 July forecast). TCD: 3 windows (T1 March/April forecast, T2 May/June forecast, T3 September biomass obs). NER: 3 windows (T1 Jan–March forecast, T2 April–June forecast, T3 August SPI obs — T3 conditional on T2 not met).
- **Calibration:** Return-period / percentile. BFA/TCD use absolute probability thresholds (40% / 42.5%) plus spatial coverage fractions (10% / 20%). NER uses a percentile rank approach (driest 35% since 1991). TCD T3 uses a biomass anomaly absolute threshold (80%). The BFA threshold implies roughly a 1-in-3 event when combined with the spatial coverage requirement.
- **Authoritative source:** The framework PDF (`framework_doc`). The repo (`code_ref`) implements the IRI-based analysis for BFA and TCD only.
- **Operated by:** IRI (Columbia University) operates the monitoring and alerting for Niger (steps 1–4 of the NER activation protocol). CHD operates BFA and TCD monitoring. This is formally stated in the activation protocol table in the framework doc.

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| BFA T1 (readiness) | forecast | IRI low-tercile probability | ≥40% prob AND prob(below) > prob(above) + 5pp, in ≥10% of monitored area | March forecast → JJA | ~1-in-3 | Trigger 1 activities (agriculture, livestock, WASH) |
| BFA T2 (action) | forecast | IRI low-tercile probability | same criteria as T1 | July forecast → ASO | ~1-in-3 | Trigger 2 activities (off-season, pastoral, nutrition) |
| TCD T1 (readiness) | forecast | IRI low-tercile probability | ≥42.5% prob in ≥20% of monitored area | March+April forecast → JAS | ~1-in-3 | Trigger 1 activities |
| TCD T2 (action) | forecast | IRI low-tercile probability | ≥42.5% prob in ≥20% of monitored area | May+June forecast → JAS | ~1-in-3 | Trigger 2 activities |
| TCD T3 (observational) | observational | NDVI/biomass anomaly | ≥80% anomaly in September biomass observation | n/a (observed) | ~1-in-3 | Trigger 3 activities |
| NER T1 (readiness) | forecast | IRI seasonal forecast (national rainfall total percentile) | Forecast rainfall in driest 35% of years since 1991 | Jan–March forecast → JAS | ~1-in-3 | Trigger 1 activities |
| NER T2 (action) | forecast | IRI seasonal forecast (national rainfall total percentile) | Forecast rainfall in driest 35% of years since 1991 | April–June forecast → JAS | ~1-in-3 | Trigger 2 activities |
| NER T3 (observational fallback) | observational | SPI (June–July cumulative, observed in August) | SPI negative AND in lowest 35% of values since 1991; only evaluated if T2 not met | Observed August | ~1-in-3 | Trigger 3 activities |

## Per-country variants

Three countries share the overall framework design but have separate calibration, geographic scope, and monitoring responsibilities.

| country | AOI | forecast source | threshold | monitoring entity |
|---|---|---|---|---|
| Burkina Faso | Boucle de Mouhoun, Centre Nord, Sahel, Nord (ADM1 pcodes BF46, BF49, BF54, BF56) | IRI (CHD monitors) | 40% prob, ≥10% area; +5pp differential condition | CHD |
| Niger | All of Niger south of 17°N | IRI (IRI/Columbia monitors) | Driest 35% since 1991 (T1/T2); SPI lowest 35% (T3) | IRI (Columbia University) |
| Chad | Lac, Kanem, Barh-El-Gazel, Batha, Wadi Fira (ADM1 pcodes TD01, TD06, TD07, TD17, TD19) | IRI T1/T2 (CHD monitors); biomass observation T3 | 42.5% prob, ≥20% area (T1/T2); ≥80% biomass anomaly (T3) | CHD |

## Sources & repo completeness

- **Trigger taken from:** `framework_doc` — the October 2022 CERF overview PDF is the authoritative source. Repo code implements partial analysis only.
- **Repo completeness:**
  - BFA IRI trigger: **partial** — the repo (`exploration/iri_historical.md`) implements the 40%/10% threshold and time windows correctly, but omits the ≥5pp differential condition stated in the PDF.
  - TCD IRI trigger: **partial** — the 42.5%/20% threshold and windows are implemented; TCD T3 (biomass) is absent.
  - NER trigger: **lost** — no Niger-specific trigger evaluation code exists. IRI operates this; the repo has no SPI or Niger-specific NER analysis.
  - ECMWF analysis: the `ecmwf-historical` branch is exploratory (ECMWF SEAS5 as a potential alternative to IRI); not the live endorsed trigger.
- **Discrepancies:** See `discrepancies` in frontmatter. Key issues: (a) BFA 5pp differential condition in PDF but absent from repo code; (b) NER and TCD T3 triggers have no repo implementation; (c) ECMWF branch likely preparatory for a future version not yet endorsed.

## Monitoring

The monitoring cadence follows the forecast release calendar:
- **BFA T1:** March IRI forecast release → monitored by CHD
- **BFA T2:** July IRI forecast release → monitored by CHD
- **TCD T1:** March and April IRI forecast releases → monitored by CHD
- **TCD T2:** May and June IRI forecast releases → monitored by CHD
- **TCD T3:** September biomass observation (ASAP or equivalent) → monitored by CHD
- **NER T1:** January, February, March IRI forecast releases → monitored by IRI (Columbia)
- **NER T2:** April, May, June IRI forecast releases → monitored by IRI (Columbia)
- **NER T3:** August SPI (observed June–July) → monitored by IRI (Columbia)

No live monitoring app is deployed for this framework in this repo. IRI operates live monitoring for Niger via the IRI Maproom.

## Historical activations

**Niger, August 2022 (NER T3 — SPI observational):** Cumulative rainfall for June–July 2022 placed southwest Niger in the driest 35% of years since 1991 (reported as the lowest rainfall in approximately 30 years). The SPI trigger (T3) was met in August 2022, after the T2 seasonal forecast had not been reached. CERF released USD 9.5 million via its Rapid Response window months earlier than a traditional rapid response allocation would have occurred. Over 160,000 people were targeted. This is confirmed as a real activation (funds released, implementation commenced). Status: **triggered**.

**Burkina Faso and Chad:** No confirmed CERF activations identified for the BFA or TCD drought triggers as of the PDF date (October 2022). The PDF notes that Chad's framework was pending endorsement at time of publication. Web searches did not surface confirmed BFA or TCD drought trigger activations through 2024 (the 2024 Chad CERF allocation was for flooding, not drought).

## Key decisions & rationale

- **Multi-stage approach:** Phased triggers allow action at each window of opportunity as lead times shorten and data certainty increases. Earlier windows (T1) use longer-range forecasts with higher uncertainty; later windows (T2) use shorter-range forecasts with more certainty. The observational T3 is a safety net for scenarios where forecasts failed to predict an actual drought.
- **IRI vs ECMWF:** The endorsed 2022 framework uses IRI seasonal forecasts because IRI was operationally available and well-validated for the Sahel. The repo's `ecmwf-historical` branch suggests exploratory work to compare or transition to ECMWF SEAS5, but this has not been endorsed.
- **BFA 5pp differential condition:** Beyond the 40% absolute threshold, BFA requires that below-average probability exceeds above-average by ≥5pp. This additional condition reduces false positives by ensuring a directional signal in the forecast, not just a floor on the tercile probability.
- **NER percentile vs absolute threshold:** Niger uses a percentile-based threshold (driest 35% since 1991) rather than a fixed probability, which adjusts for Niger's national-scale aggregation and different forecast calibration. The observational T3 is unique to Niger and Chad and reflects concern about missed events.
- **Spatial coverage requirement:** Requiring 10%–20% of monitored area to exceed the threshold prevents activation from small, localized signals that would not warrant a national-scale response.
- **IRI as NER operator:** The activation protocol formally assigns IRI/Columbia as the monitoring entity for Niger (steps 1–4), while OCHA/CHD is the primary monitor for BFA and TCD. This was negotiated given IRI's pre-existing operational role in Niger's national early warning system.

## Changes from previous version

This is the first published version of the Sahel multi-country overview (`supersedes: null`). Individual country frameworks for BFA and NER were endorsed in early 2022; this October 2022 document is the overview pamphlet covering all three. No prior version of this exact multi-country document has been identified.

## Open questions / known issues

- The TCD framework was "pending endorsement" as of the PDF date (October 2022). It is unclear whether TCD was subsequently endorsed and whether any TCD drought trigger activation has occurred.
- The BFA framework has a two-year validity from endorsement (2022). Its renewal/extension status is unknown.
- The 5pp differential condition for BFA (PDF) is absent from the repo implementation — this should be clarified before relying on repo code for threshold compliance.
- Per-country CERF allocations (of the USD 45M ceiling) are not stated in this overview document; individual country framework PDFs may have this detail.
- The `ecmwf-historical` branch activity (last committed July 2024) suggests ongoing work toward an ECMWF-based version. Whether a new endorsed version has been published should be checked against aa.unocha.org and ReliefWeb.
- Target population per country is not stated in the overview PDF (BFA ~800,000 is cited in other sources; NER and TCD figures not confirmed from this document).
