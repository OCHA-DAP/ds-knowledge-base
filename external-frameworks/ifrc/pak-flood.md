---
content_type: framework-external
framework: ifrc-pak-flood
org: IFRC
country_iso3: PAK
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Current (2025) nationwide protocol covers the Indus River and major tributaries in
  numbered sections; e.g. Section 4 (Chenab at Trimmu) triggers at ≥300,000 cusecs and
  Section 5 (Indus at Taunsa) at ≥550,000 cusecs, both confirmed by PMD/FFD bulletins.
  Its predecessor, Kabul-River-only EAP2023PK01, triggered on FFD Bulletin C / flood
  advisories forecasting >150,000 cusecs at Nowshera (Kabul River) 3-5 days out, confirmed
  within 24-48h by Bulletin A/B before cash was disbursed (a "stop mechanism" cancelled
  disbursement if the confirming bulletin didn't materialise).
data_sources: [Pakistan Flood Forecasting Division (FFD) bulletins A/B/C, FEWS, INDUS-IFAS]
prearranged_funding_usd: 449484
funding_by_source: {}
target_people: 104288
framework_doc: https://reliefweb.int/report/pakistan/pakistan-riverine-floods-early-action-protocol-summary-15-september-2025-eap2025pk02
framework_doc_date: 2025-09-15
sources:
- https://www.anticipation-hub.org/download/file-3777
- https://reliefweb.int/report/pakistan/pakistan-riverine-flood-simplified-early-action-protocol-eap2023pk01-dref-no-mdrpk024
- https://reliefweb.int/report/pakistan/pakistan-riverine-flood-early-action-protocol-annual-report-11062024-mdrpk024
- https://reliefweb.int/report/pakistan/pakistan-riverine-flood-simplified-early-action-protocol-operations-update-30-june-2025-mdrpk024
- https://reliefweb.int/report/pakistan/simplified-early-action-protocol-final-report-pakistan-riverine-flood-31012026
- https://reliefweb.int/report/pakistan/pakistan-riverine-floods-early-action-protocol-summary-15-september-2025-eap2025pk02
- https://reliefweb.int/report/pakistan/pakistan-riverine-floods-early-action-protocol-2025-annual-report-eap-no-eap2025pk02-operation-no-mdrpk029-5-march-2026
- https://www.anticipation-hub.org/news/the-pakistan-red-crescent-society-activates-early-actions-for-flooding-at-the-chenab-river
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/pakistan
- https://www.anticipation-hub.org/global-overview/countries/pakistan/forecast-based-financing-in-pakistan
activations:
- date: '2025-08-29'
  url: https://www.anticipation-hub.org/news/the-pakistan-red-crescent-society-activates-early-actions-for-flooding-at-the-chenab-river
  note: >-
    Chenab River (Section 4, ≥300,000 cusecs at Trimmu) and Indus River (Section 5,
    ≥550,000 cusecs at Taunsa) sections activated during the catastrophic Aug 2025
    Punjab floods — early warning reached 85,658 people, evacuation support to 26,061,
    coordination on 17 evacuation camps; funded by German Red Cross/German Federal
    Foreign Office. Activation ran ahead of the nationwide EAP2025PK02's formal
    publication (2025-09-15) — see `extra.schema_strain`.
last_checked: '2026-07-14'
extra:
  eap_no: EAP2025PK02
  operation_no: MDRPK029
  generations: >-
    EAP2023PK01 (approved 2023-07-24, operation MDRPK024, CHF 200,000 total — CHF 45,857
    readiness + 1,978 prepositioning + 152,165 early action, DREF-funded, Kabul River
    basin only [Nowshera/Charsadda/Peshawar, districts Charsadda & Nowshera], sEAP
    timeframe 2 years, targeting 37,315 people with early warning incl. 14,820 via
    unconditional multipurpose cash) → EAP2025PK02 (EAP summary published 2025-09-15,
    operation MDRPK029, CHF 829,824 total — CHF 272,263 stock prepositioning + 177,152
    readiness + 380,409 contingency for early action, funded via a 5-year PRCS/IFRC
    Project Funding Agreement, expanded nationwide to the Indus River and major
    tributaries incl. Chenab/Indus sections). Succession follows PRCS's stated 2023
    intent (in the EAP2023PK01 document) to "explore the possibility of a nationwide EAP
    covering the entire Indus River basin".
  hub_captions:
  - '2023: Flood (IFRC) [Pakistan Red Crescent]'
  - '2024: Flood (IFRC) [Pakistan Red Crescent]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Pakistan Red Crescent Society (PRCS)
  partners: German Red Cross (GRC), German Federal Foreign Office (GFFO), IFRC, RCRC
    Climate Centre, Pakistan Meteorological Department/Flood Forecasting Division,
    Federal Flood Commission
  coordination: No matching OCHA/CERF collective AA framework found for Pakistan flood
    under frameworks/ — this reads as PRCS/IFRC's own independent framework, not a
    component of an OCHA-coordinated one.
  schema_strain: >-
    (1) target_people/prearranged_funding_usd use the Anticipation Hub's live Pakistan
    country-page "Active Frameworks" figures (104,288 people / US$449,484), which don't
    cleanly reconcile with either generation's own CHF budget/target figures above —
    kept as the headline current numbers, generation detail kept separately. (2) Whether
    the original Kabul-only EAP2023PK01 was itself ever triggered on its own threshold
    before being succeeded is unconfirmed — ReliefWeb blocks default fetches (403) for
    its 2024 annual report and 31 Jan 2026 final report, and the 2025-06-30 operations
    update likewise wasn't fetchable full-text. (3) EAP2025PK02's own target-people
    figure, full trigger table (all sections/basins, not just Chenab/Indus), and precise
    valid_until date weren't extractable from the accessible excerpts — the 2025-09-15
    summary page returned empty content on fetch.
visibility: public
---

# IFRC — Pakistan flood

## Summary
The Pakistan Red Crescent Society (PRCS), with IFRC and German Red Cross support, runs
forecast-based anticipatory action against riverine flooding. What began in 2023 as a
simplified Early Action Protocol (EAP2023PK01) for the Kabul River basin alone (Khyber
Pakhtunkhwa; Peshawar, Nowshera, Charsadda) was superseded in September 2025 by a
nationwide protocol (EAP2025PK02) covering the Indus River and its major tributaries —
including the Chenab and lower Indus — in numbered river sections, backed by a 5-year
PRCS/IFRC funding agreement. The programme disburses unconditional multipurpose cash and
early-warning dissemination ahead of forecast flood peaks.

## Trigger
**EAP2023PK01 (Kabul River, 2023-07-24 to ~2025-07-24):** activation trigger reached when
FFD/PMD's Bulletin C (weekly catchment forecast) or a significant flood advisory predicted
very-high-to-exceptionally-high flooding — river flow above 150,000 cusecs at the Nowshera
gauge on the Kabul River — with a 3-5 day lead time. That triggered early-warning
dissemination and beneficiary registration; actual cash disbursement (24-48h before the
flood) required Bulletin A or B to *confirm* the same >150,000 cusec threshold, otherwise a
built-in "stop mechanism" cancelled the payout. Forecasts draw on Pakistan's Flood Early
Warning System (FEWS) and INDUS-IFAS hydrological models.

**EAP2025PK02 (nationwide Indus system, from 2025-09-15):** divides the Indus and its
tributaries into numbered sections, each with its own gauge and cusec threshold. Confirmed
so far: Section 4 (Chenab at Trimmu) triggers at ≥300,000 cusecs; Section 5 (Indus at
Taunsa) at ≥550,000 cusecs. The full section-by-section trigger table (including whether a
Kabul River section persists) wasn't accessible from public excerpts — see
`extra.schema_strain`.

## Funding & scope
EAP2023PK01: CHF 200,000 total (DREF), of which CHF 152,165 was earmarked for early
action (mainly PKR 15,000 one-off unconditional cash grants to 2,470 households/14,820
people via mobile wallets, plus early-warning dissemination to 37,315 people) in
Nowshera/Charsadda districts, KP province.

EAP2025PK02: CHF 829,824 total (CHF 272,263 prepositioning + CHF 177,152 readiness + CHF
380,409 early-action contingency), funded through a 5-year PRCS/IFRC Project Funding
Agreement plus German Red Cross/GFFO support, scaled up to cover the Indus basin
nationwide. The Anticipation Hub's live Pakistan listing gives current headline figures of
104,288 people targeted and ~US$449,484 budget (see `extra.schema_strain` on
reconciliation).

## Activations
- **29-31 August 2025** — Chenab (Section 4) and Indus (Section 5) sections activated
  during the catastrophic Aug-Sept 2025 Punjab floods: early-warning reached 85,658
  people, evacuation support to 26,061, coordination on 17 government evacuation camps.
  This ran ahead of EAP2025PK02's formal publication date, under what the Hub described as
  PRCS's "forthcoming" nationwide EAP.
- No confirmed activation of the original Kabul-only EAP2023PK01 was found in public
  sources ("not yet activated" as of its 2023 publication); its closure/final report
  (31 Jan 2026) wasn't accessible full-text to check.

## Sources
- **Authoritative (current):** [EAP2025PK02 summary, 15 Sep 2025](https://reliefweb.int/report/pakistan/pakistan-riverine-floods-early-action-protocol-summary-15-september-2025-eap2025pk02) · [2025 annual report (EAP2025PK02/MDRPK029), 5 Mar 2026](https://reliefweb.int/report/pakistan/pakistan-riverine-floods-early-action-protocol-2025-annual-report-eap-no-eap2025pk02-operation-no-mdrpk029-5-march-2026)
- **Predecessor (full text read):** [EAP2023PK01 / MDRPK024 PDF](https://www.anticipation-hub.org/download/file-3777) (approved 24 Jul 2023) · [ReliefWeb listing](https://reliefweb.int/report/pakistan/pakistan-riverine-flood-simplified-early-action-protocol-eap2023pk01-dref-no-mdrpk024) · [2024 annual report](https://reliefweb.int/report/pakistan/pakistan-riverine-flood-early-action-protocol-annual-report-11062024-mdrpk024) · [30 Jun 2025 operations update](https://reliefweb.int/report/pakistan/pakistan-riverine-flood-simplified-early-action-protocol-operations-update-30-june-2025-mdrpk024) · [final report, 31 Jan 2026](https://reliefweb.int/report/pakistan/simplified-early-action-protocol-final-report-pakistan-riverine-flood-31012026)
- [Anticipation Hub — Chenab River activation news](https://www.anticipation-hub.org/news/the-pakistan-red-crescent-society-activates-early-actions-for-flooding-at-the-chenab-river) (8 Sep 2025, updated from 3 Sep)
- [Anticipation Hub — Pakistan country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/pakistan) (fetched 2026-07-14; current active-framework figures)
- [Anticipation Hub — Forecast-based Financing in Pakistan](https://www.anticipation-hub.org/global-overview/countries/pakistan/forecast-based-financing-in-pakistan) (original FbF project overview, 2021-2023)
