---
content_type: framework-external
framework: ifrc-nga-flood
org: IFRC
country_iso3: NGA
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Riverine-flood forecasts for prioritized states (Adamawa, Kaduna, Kwara, Akwa Ibom,
  Bayelsa, Benue, Nasarawa, Delta, Kano, Yobe, Taraba) triangulated from GloFAS, the
  Nigerian Meteorological Agency (NiMet) and the Nigeria Hydrological Services Agency
  (NiHSA); the sEAP activates in the specific state(s) where forecasts indicate a high
  probability of flooding. No single public threshold/lead-time figure (station,
  return period) was found — see `extra.schema_strain`.
data_sources: [GloFAS, NiMet, NiHSA]
prearranged_funding_usd: 249716
funding_by_source: {DREF-FbA: 220000}
target_people: 7500
framework_doc: /download/file-2985
framework_doc_date: "2022-08"
sources:
  - https://www.anticipation-hub.org/download/file-2985
  - https://reliefweb.int/report/nigeria/nigeria-floods-simplified-early-action-protocol-eap2022ng01
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNG035
  - https://www.anticipation-hub.org/download/file-4260
  - https://reliefweb.int/report/nigeria/nigeria-floods-simplified-early-action-protocol-annual-report-seap-no-eap2022ng01-operation-no-mdrng035
  - https://reliefweb.int/report/nigeria/nigeria-floods-simplified-early-action-protocol-final-narrative-report-seap-no-eap2022ng01-operation-no-mdrng035
activations:
  - date: 2024-09-12
    url: https://www.anticipation-hub.org/download/file-4260
    note: >-
      Activated the week of 9 September 2024 after GloFAS, NiMet and NiHSA forecasts
      (triangulated with other sources) pointed to a high flood probability; implemented
      in 3 of the sEAP's 4 candidate states for that season (Adamawa, Edo, Nasarawa —
      Akwa Ibom was the fourth candidate but not triggered). ~4,000 households received a
      one-off NGN 50,000 (~US$30) cash grant in Sep-Nov 2024, alongside community
      sensitization and early-warning message dissemination led by NRCS with community
      leaders.
last_checked: '2026-07-18'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [IFRC] [Red Cross Society of Niger]'
  - '2023: Flood (IFRC) [Nigerian Red Cross Society]'
  - '2024: Flood (IFRC) [Nigerian Red Cross Society]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - Nigerian Red Cross Society
  eap_no: EAP2022NG01
  operation_no: MDRNG035
  funding_chf: >-
    CHF 220,000 total DREF Forecast-based Action allocation (IFRC GO appeal MDRNG035:
    US$220,000 requested and fully funded, open 14 Oct 2022 - 31 Dec 2024, status
    closed). One design-stage source describes CHF 206,573 of this as earmarked for
    "prepositioning stock and annual readiness activities to implement early actions" —
    read here as the pre-positioned early-action tranche rather than pure readiness
    overhead, leaving a smaller residual readiness/prepositioning slice; the exact
    tranche-by-tranche split could not be confirmed from a single authoritative table.
    The USD figure in `prearranged_funding_usd` (249,716) is the Anticipation Hub
    global-map "investment" figure and does not exactly match the GO API's $220,000 —
    kept as-is pending reconciliation, per the pattern on other IFRC pages in this KB.
  scope_detail: >-
    "Simplified EAP" (sEAP) prioritizing 11 flood-prone states (Adamawa, Kaduna, Kwara,
    Akwa Ibom, Bayelsa, Benue, Nasarawa, Delta, Kano, Yobe, Taraba); in a given season a
    smaller subset of candidate states (e.g. Adamawa, Akwa Ibom, Edo, Nasarawa in 2024)
    is monitored, with the sEAP activating only in the state(s) where the trigger is
    actually met. Separately, NRCS ran non-EAP DREF flood response operations in other
    states/years (e.g. Cross River, Jigawa, Kebbi under a distinct DREF grant) — those
    are regular emergency response, not this EAP.
  partners: >-
    Nigerian Meteorological Agency (NiMet), Nigeria Hydrological Services Agency
    (NiHSA), and (per one source) the Upper River Benue Basin Development Authority
    provide the forecast/hydrological data underpinning trigger monitoring.
  coordination: >-
    NOT a component of a collective OCHA/CERF framework, despite overlapping ground in
    Adamawa State. A separate OCHA/CERF-owned Nigeria flood framework exists
    (frameworks/nga-flooding, endorsed version 2025-08-11, CERF $5M + NHF $2M, riverine
    Benue-river triggers in Adamawa's 7 LGAs plus a BAY-states flash-flood window,
    implemented by FAO/WFP/OCHA CHD). Its September 2025 activation ($7M, 350,000+
    reached via WFP-led multi-purpose cash within 72 hours, per the Anticipation Hub's
    Nov 2025 after-activation-review coverage) is that OCHA/CERF framework's activation,
    NOT this IFRC/NRCS EAP's — it is recorded on the OCHA page, not here. The two
    frameworks share Adamawa as ground and both reference GloFAS, but are independently
    designed, funded (DREF-FbA vs CERF/NHF) and operated (NRCS/IFRC vs FAO/WFP/OCHA CHD),
    with different trigger mechanics and target populations.
  schema_strain: >-
    The EAP2022NG01 design PDF (/download/file-2985) could not be extracted as text by
    available tooling (binary/compressed PDF stream); facts here are drawn from the
    Anticipation Hub/ReliefWeb landing-page summaries, the IFRC GO API, and search-indexed
    excerpts of the sEAP annual/final narrative reports (the ReliefWeb report pages
    themselves return HTTP 403 to automated fetches). No single source gave a precise
    station-level threshold or lead-time figure (contrast the Kenya/Niger EAPs, which
    have GloFAS return-period and lead-time numbers) — `trigger_summary` is left at the
    plain-language "forecasts triangulated across states" level found in the sources.
    `status`/`valid_until`: the GO appeal MDRNG035 shows as closed (31 Dec 2024) but a
    2024 activation occurred under it and the Hub inventory lists this framework through
    2024 with no lapse/non-renewal notice found, so `status: active` is kept (looser than
    OCHA's enum, per the schema) rather than asserted expired.
visibility: public
---

# IFRC — Nigeria flood

## Summary
The Nigerian Red Cross Society's Simplified Early Action Protocol for riverine floods
(EAP2022NG01, operation MDRNG035), financed through the IFRC DREF's Forecast-based
Action (FbA) pillar since October 2022. It prioritizes 11 flood-prone states, monitoring
a smaller candidate subset each season and activating early actions — community
sensitization, early-warning messaging and cash grants — only in the state(s) where
forecasts (GloFAS, NiMet, NiHSA) indicate high flood probability. Targets 7,500 people
overall; activated once to date, in September 2024.

## Trigger
Riverine-flood forecasts for the prioritized states are triangulated from GloFAS, the
Nigerian Meteorological Agency (NiMet) and the Nigeria Hydrological Services Agency
(NiHSA) (plus, per one source, the Upper River Benue Basin Development Authority). The
sEAP activates in whichever of that season's candidate states (drawn from the 11-state
priority list) the forecasts point to as facing a high probability of flooding —
described in sources as triggered by conditions such as dam releases and ocean surge as
well as riverine flooding. No public document surfaced a single station-level threshold
or lead-time figure comparable to the Kenya or Niger EAPs' GloFAS return-period design
(see `extra.schema_strain`).

## Funding & scope
CHF 220,000 (IFRC GO appeal MDRNG035: US$220,000, fully funded, open 14 October 2022 to
31 December 2024) from the DREF Forecast-based Action mechanism. One design-stage
source describes CHF 206,573 of this as earmarked to "preposition stock and undertake
annual readiness activities to implement early actions" once triggered — read here as
the pre-positioned early-action tranche, though the precise tranche breakdown could not
be confirmed from one authoritative table. Targets 7,500 people; the sEAP prioritizes 11
states (Adamawa, Kaduna, Kwara, Akwa Ibom, Bayelsa, Benue, Nasarawa, Delta, Kano, Yobe,
Taraba), monitoring a smaller candidate subset each season.

## Activations
- **12 September 2024 activation notification (early actions the week of 9 September
  2024)** — GloFAS, NiMet and NiHSA forecasts, triangulated with other sources, pointed
  to high flood probability; the sEAP activated in 3 of that season's 4 candidate states
  (Adamawa, Edo, Nasarawa — Akwa Ibom was monitored but not triggered). Around 4,000
  households received a one-off NGN 50,000 (~US$30) cash grant in September-November
  2024, alongside community sensitization and early-warning message dissemination led by
  NRCS with local community leaders.
- No other activations known; the Anticipation Hub inventory lists this framework as
  active 2022-2024 without further activation-specific detail for 2022/2023.

## Sources
- **Authoritative:** [Simplified Early Action Protocol for floods in Nigeria, EAP2022NG01](/download/file-2985) (Anticipation Hub / Nigerian Red Cross Society, approved ~August 2022; PDF text not extractable by available tooling, facts drawn from linked landing page and secondary reporting)
- [ReliefWeb — Nigeria: Floods, Simplified Early Action Protocol (EAP2022NG01)](https://reliefweb.int/report/nigeria/nigeria-floods-simplified-early-action-protocol-eap2022ng01) (landing page; 403 to direct fetch)
- [IFRC GO API — appeal MDRNG035](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNG035) (budget, dates, beneficiaries; machine-readable)
- [Anticipation Hub — Activation notification for Nigeria floods EAP](https://www.anticipation-hub.org/download/file-4260) (12 Sep 2024)
- [ReliefWeb — sEAP Annual Report (EAP2022NG01 / MDRNG035)](https://reliefweb.int/report/nigeria/nigeria-floods-simplified-early-action-protocol-annual-report-seap-no-eap2022ng01-operation-no-mdrng035) (landing page; 403 to direct fetch)
- [ReliefWeb — sEAP Final Narrative Report (EAP2022NG01 / MDRNG035)](https://reliefweb.int/report/nigeria/nigeria-floods-simplified-early-action-protocol-final-narrative-report-seap-no-eap2022ng01-operation-no-mdrng035) (landing page; 403 to direct fetch; 2024 activation detail drawn from search-indexed excerpts)
- Cross-reference (not this framework): [Anticipation Hub — Nigeria's National After-Activation Review: advancing anticipatory action for floods in Adamawa State](https://www.anticipation-hub.org/news/nigerias-national-after-activation-review-advancing-anticipatory-action-for-floods-in-adamawa-state) — describes the September 2025 OCHA/CERF+NHF framework activation (`frameworks/nga-flooding`), not this IFRC/NRCS EAP
