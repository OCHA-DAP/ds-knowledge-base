---
content_type: framework-external
framework: ifrc-gtm-flood
org: IFRC
country_iso3: GTM
hazard: flood
status: active
valid_until: '2029-05-31'
trigger_summary: >-
  Either-or, two hazard paths. (1) INSIVUMEH or the US National Hurricane Center forecasts
  ≥60% probability that a tropical storm (≥61 km/h) track will enter Guatemala's cyclone
  warning zone, 3-5 day lead time. (2) GloFAS forecasts ≥50% probability of a flood
  exceeding the 10-year return period in high-flood-risk areas, 3-day lead time.
data_sources: [GloFAS, INSIVUMEH, NHC]
prearranged_funding_usd: 621119
funding_by_source: {DREF: 621119}
target_people: 14000
framework_doc: https://www.anticipation-hub.org/download/file-4113
framework_doc_date: 2024-06-04
sources:
  - https://www.anticipation-hub.org/download/file-4113
  - https://reliefweb.int/report/guatemala/guatemala-floods-associated-tropical-cyclones-early-action-protocol-summary-eap-no-eap2024gt02-operation-no-mdrgt024
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRGT024
  - https://www.anticipation-hub.org/news/a-new-eap-for-floods-associated-with-tropical-cyclones-will-benefit-up-to-15000-people-in-guatemala
  - https://www.anticipation-hub.org/news/early-action-protocols-activated-in-guatemala-and-honduras-as-hurricane-julia-hits-central-america
  - https://reliefweb.int/report/guatemala/guatemala-floods-associated-tropical-cyclones-early-action-protocol-notification-7-october-2022-eap2022gt01
  - https://reliefweb.int/report/guatemala/early-action-protocol-activation-final-report-guatemala-floods-caused-cyclones-eap-no-eap2022gt01-operation-no-mdrgt018-22052023
  - https://www.climatecentre.org/14860/2024-atlantic-hurricane-season-officially-ends-ts-sara-may-be-parting-shot/
activations:
  - date: 2022-10-07
    url: https://www.anticipation-hub.org/news/early-action-protocols-activated-in-guatemala-and-honduras-as-hurricane-julia-hits-central-america
    note: >-
      Hurricane Julia — both triggers met (storm-track confirmation 6 Oct, GloFAS >50%
      probability of >10-year-return-period flooding 7 Oct); CHF 478,789 released ahead of
      the flood peak (13 Oct) for cash assistance and WASH support (water purification
      kits, treatment plants, storage tanks) in Puerto Barrios, Izabal, targeting 3,000
      families (1,000 via cash). Final report puts actual reach at 10,300 people (2,060
      families). Implemented by Guatemalan Red Cross with German Red Cross support, under
      the predecessor EAP2022GT01/MDRGT018 (this activation predates the current
      EAP2024GT02 generation).
last_checked: '2026-07-17'
extra:
  hub_captions:
  - '2024: Flood (IFRC) [Guatemalan Red Cross]'
  hub_years:
  - '2024'
  implementing:
  - Guatemalan Red Cross
  eap_no: EAP2024GT02
  operation_no: MDRGT024
  generations: >-
    EAP2022GT01 (approved 2022-08-18, operation MDRGT018, CHF 478,796 total ≈US$488,560/
    €489,818, valid to 2027-08-18, same 5-department scope and 15,000-person target,
    same DREF mechanism) → EAP2024GT02 (Hub-published 2024-06-04, operation MDRGT024,
    approved/appeal opened 2024-05-29, CHF 547,206 total — CHF 242,234
    readiness/prepositioning + CHF 304,972 early-action tranche, fully funded by
    2025-02-11 per the GO appeal record). Same either-or trigger design carried forward
    across both generations per public Hub reporting.
  scope_detail: >-
    Five departments: Alta Verapaz, Izabal, Quetzaltenango, Retalhuleu, Suchitepéquez.
  partners: Guatemalan Red Cross (implementing); German Red Cross supported the 2022
    Hurricane Julia activation; IFRC (DREF mechanism).
  coordination: No matching OCHA/CERF collective AA framework found for Guatemala flood
    under frameworks/ (the OCHA-adjacent GTM entries there — lac-dry-corridor, and GTM is
    not in nic-drought — cover drought, a different hazard). Reads as IFRC/Guatemalan Red
    Cross's own independent framework, not a component of an OCHA-coordinated one.
  schema_strain: >-
    (1) prearranged_funding_usd/target_people are the Hub/GO API's current headline
    figures for EAP2024GT02 (CHF 547,206 ≈ US$621,119 conversion; 14,000 people) — these
    sit slightly below the EAP text's own "up to 15,000 people" language, similar to the
    predecessor's 15,000-target vs 10,300-actual-reached gap; kept the GO/Hub figure as
    the machine-comparable headline. (2) No confirmed activation of EAP2024GT02 (the
    current generation) was found in public sources — search results describing a
    mid-November 2024 Tropical Storm Sara "EAP activation" affecting Guatemala trace back,
    on closer reading of the RCRC Climate Centre's own reporting, to the *Honduran* Red
    Cross's EAP, not Guatemala's; no Guatemala-specific EAP2024GT02 activation notice was
    found, so only the 2022 Julia activation (predecessor EAP2022GT01) is recorded above.
    (3) Full text of the EAP2024GT02 PDF (file-4113) and its ReliefWeb mirror both returned
    thin/blocked content to automated fetch (ReliefWeb 403s by default) — trigger and
    funding detail for the current generation are drawn from Hub/news secondary reporting
    that explicitly attributes them to EAP2024GT02/MDRGT024, not from the primary PDF text
    directly.
visibility: public
---

# IFRC — Guatemala flood

## Summary
The Guatemalan Red Cross runs a national Early Action Protocol for floods associated with
tropical cyclones, pre-financed through the IFRC DREF. The current generation,
EAP2024GT02 (operation MDRGT024, Hub-published 2024-06-04), succeeds EAP2022GT01
(operation MDRGT018, approved 2022-08-18), carrying forward the same trigger design,
five-department footprint, and roughly 14,000-15,000 person target. It has been activated
once to date, in October 2022, under the predecessor generation.

## Trigger
Either-or, two independent hazard paths. **Cyclone path**: INSIVUMEH (Guatemala's national
seismology/vulcanology/meteorology/hydrology institute) or the US National Hurricane Center
forecasts ≥60% probability that a tropical storm track (≥61 km/h sustained winds) will
enter Guatemala's cyclone warning zone, 3-5 days out. **Flood path**: GloFAS forecasts
≥50% probability of a flood exceeding the 10-year return period in areas of high flood
risk, 3 days out. Either path independently triggers the EAP. Public reporting describes
this same design for both EAP2022GT01 and its EAP2024GT02 successor.

## Funding & scope
**EAP2022GT01** (2022-08-18 to 2027-08-18): CHF 478,796 (≈US$488,560/€489,818) from the
DREF, covering Alta Verapaz, Izabal, Quetzaltenango, Retalhuleu and Suchitepéquez
departments, targeting up to 15,000 people per activation. **EAP2024GT02** (from
2024-05-29/06-04): CHF 547,206 total — CHF 242,234 for readiness/prepositioning and CHF
304,972 for the early-action tranche — same five departments, fully funded per the IFRC GO
appeal record by 2025-02-11. Early actions include multipurpose cash assistance and
WASH support (water purification kits, treatment plants, storage tanks, safe-water
distribution).

## Activations
- **7 October 2022** — Hurricane Julia. Both triggers confirmed (storm track 6 Oct; GloFAS
  >50% probability of >10-year-return-period flooding 7 Oct). CHF 478,789 released ahead
  of the flood peak (13 Oct) for cash assistance and WASH support in Puerto Barrios,
  Izabal; initially targeted 3,000 families (1,000 via cash transfers), with the EAP
  activation final report recording an actual reach of 10,300 people (2,060 families).
  Implemented by the Guatemalan Red Cross with German Red Cross support, under the
  predecessor EAP2022GT01/MDRGT018.
- No confirmed activation of the current EAP2024GT02 generation found in public sources —
  see `extra.schema_strain` on the Tropical Storm Sara (Nov 2024) reporting, which traces
  to Honduras's own EAP rather than Guatemala's.

## Sources
- **Authoritative (current):** [EAP summary: Guatemala — Floods associated with Tropical Cyclones, EAP2024GT02/MDRGT024](https://www.anticipation-hub.org/download/file-4113) (published 2024-06-04) · [ReliefWeb mirror](https://reliefweb.int/report/guatemala/guatemala-floods-associated-tropical-cyclones-early-action-protocol-summary-eap-no-eap2024gt02-operation-no-mdrgt024) (403 to automated fetch)
- [IFRC GO — appeal MDRGT024](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRGT024) (budget/status/beneficiaries; last updated 2025-02-11)
- [Anticipation Hub news — "A new EAP for Floods associated with Tropical Cyclones will benefit up to 15,000 people in Guatemala"](https://www.anticipation-hub.org/news/a-new-eap-for-floods-associated-with-tropical-cyclones-will-benefit-up-to-15000-people-in-guatemala) (predecessor EAP2022GT01 launch)
- **Predecessor (full text read via secondary reporting):** [ReliefWeb — EAP2022GT01 notification, 7 Oct 2022](https://reliefweb.int/report/guatemala/guatemala-floods-associated-tropical-cyclones-early-action-protocol-notification-7-october-2022-eap2022gt01) · [Anticipation Hub news — EAPs activated in Guatemala and Honduras for Hurricane Julia](https://www.anticipation-hub.org/news/early-action-protocols-activated-in-guatemala-and-honduras-as-hurricane-julia-hits-central-america) · [ReliefWeb — EAP2022GT01/MDRGT018 activation final report, 22 May 2023](https://reliefweb.int/report/guatemala/early-action-protocol-activation-final-report-guatemala-floods-caused-cyclones-eap-no-eap2022gt01-operation-no-mdrgt018-22052023) (403 to automated fetch; final beneficiary figures via search excerpt)
- [RCRC Climate Centre — "2024 Atlantic hurricane season officially ends – TS Sara may be parting shot"](https://www.climatecentre.org/14860/2024-atlantic-hurricane-season-officially-ends-ts-sara-may-be-parting-shot/) (clarifies the Nov 2024 Sara EAP activation was Honduras's, not Guatemala's)
