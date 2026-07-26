---
content_type: framework-external
framework: ifrc-phl-tropical-cyclone
org: IFRC
country_iso3: PHL
hazard: tropical-cyclone
status: active
valid_until: 2029-09-30
trigger_summary: >-
  Current generation (EAP2024PH03, from 2024-09-23): wind-speed based, using ECMWF forecasts
  as the main trigger input and PAGASA bulletins for monitoring. Readiness/early-action
  trigger can fire up to 72h before landfall; if not met by then, an observational trigger
  (PAGASA-confirmed super typhoon, ≥185 km/h 10-min sustained winds) can still fire any time
  from 72h before landfall up to landfall itself. Superseded the original EAP2019PH01 design,
  which triggered on a 510-Initiative statistical model forecasting >10% of houses totally
  damaged in more than three municipalities, 72h lead time.
data_sources: [PAGASA, ECMWF]
prearranged_funding_usd: 607594
funding_by_source: {DREF-anticipatory: 607594}
target_people: 15000
framework_doc: https://reliefweb.int/report/philippines/philippines-typhoon-early-action-protocol-summary-eap-no-eap2024ph03-operation-no-mdrph055
framework_doc_date: 2024-09-23
sources:
  - https://reliefweb.int/report/philippines/philippines-typhoon-early-action-protocol-summary-eap-no-eap2024ph03-operation-no-mdrph055
  - https://www.anticipation-hub.org/global-overview/countries/philippines/forecast-based-financing-fbf-in-the-philippines
  - https://www.anticipation-hub.org/Documents/Briefing_Sheets_and_Fact_Sheets/Philippines_Typhoon_EAP_Fact_Sheet.pdf
  - https://www.anticipation-hub.org/news/the-philippine-red-cross-acts-to-protect-people-ahead-of-tropical-storm-fungwong
  - https://reliefweb.int/report/philippines/philippines-typhoon-paeng-early-action-protocol-activation-final-report-eap-no-eap2019ph01-operation-no-mdrph049-30-june-2023
  - https://reliefweb.int/report/philippines/eap-activation-notification-philippines-typhoon-operation-mdrph049
  - https://reliefweb.int/report/philippines/philippines-typhoon-early-action-protocol-activation-report-eap-no-eap2024ph03-operation-no-mdrph055-30-april-2026
  - https://go.ifrc.org/emergencies/7196
activations:
  - date: 2019-12
    url: https://www.anticipation-hub.org/global-overview/countries/philippines/forecast-based-financing-fbf-in-the-philippines
    note: >-
      Typhoon Tisoy (Kammuri) — first test of the newly-approved EAP2019PH01, limited scale
      (~200 households), DREF funded.
  - date: 2022-10-27
    url: https://reliefweb.int/report/philippines/philippines-typhoon-paeng-early-action-protocol-activation-final-report-eap-no-eap2019ph01-operation-no-mdrph049-30-june-2023
    note: >-
      Typhoon Paeng (Nalgae) — trigger reached 27 Oct 2022 (>10% shelter damage projected in
      priority municipalities); PRC requested activation at 56h lead (shorter than the
      stated 72h, granted exceptionally). CHF 16,981 released; SSK distribution began
      29 Oct 2022 (49 staff/volunteers). Final report 30 Jun 2023.
  - date: 2025-11-07
    url: https://www.anticipation-hub.org/news/the-philippine-red-cross-acts-to-protect-people-ahead-of-tropical-storm-fungwong
    note: >-
      Super Typhoon Fung-wong (Uwan) — first activation under the revised EAP2024PH03,
      triggered by a PAGASA advisory forecasting 195 km/h winds within 96h. CHF 20,725
      (~US$25,751) released; shelter-strengthening kits distributed/installed for 224
      households (1,120 people) in Quirino, Isabela, and Quezon-Lucena — a partial
      activation targeting the highest-risk areas only. Activation report due 2026-04-30.
last_checked: '2026-07-17'
extra:
  hub_captions:
  - '2022: Cyclone / Typhoon / Hurricane (IFRC) [Philippine Red Cross] [German Red Cross]
    [Finnish Red Cross]'
  - '2024: Cyclone / Typhoon / Hurricane (IFRC) [Philippine Red Cross]'
  hub_years:
  - '2022'
  - '2024'
  implementing:
  - Philippine Red Cross
  eap_no: EAP2024PH03
  operation_no: MDRPH055
  generations: >-
    EAP2019PH01 (approved Nov 2019, CHF 249,540, 19 provinces, 510-Initiative
    damage-model trigger) → EAP2024PH03 (MDRPH055, effective 2024-09-23 to 2029-09-30,
    CHF 535,290, 25 provinces / 5 regions — North Luzon, Central Luzon, Bicol, Visayas,
    Mindanao — wind-speed trigger).
  funding_chf: >-
    CHF 535,290 total for EAP2024PH03: 318,890 readiness/prepositioning + 216,399
    early-action tranche (USD figure in prearranged_funding_usd is an approximate
    conversion; original EAP2019PH01 budget was CHF 249,540: 131,985 + 117,555).
  partners: German Red Cross, IFRC, PAGASA, provincial/municipal DRRM offices,
    barangay committees (BARCOM); funded in part by the German Federal Foreign Office.
  near_activations: >-
    Typhoon Kalmaegi (Nov 2025, shortly before Fung-wong) — EAP NOT activated because
    the wind-speed trigger was not met.
  coordination: >-
    Distinct from, and not a component of, OCHA/CERF's collective Philippines AA
    framework for tropical cyclones ([frameworks/phl-storms](../../frameworks/phl-storms/README.md))
    — this EAP is PRC/IFRC's own framework, financed through the DREF anticipatory
    pillar, not CERF. Both frameworks use PAGASA super-typhoon wind-speed classification
    in their observational triggers and both activated for the same storm (Super
    Typhoon Fung-Wong/Uwan, Nov 2025), but independently and at different scales.
  schema_strain: >-
    target_people (15,000) is the Hub inventory's design-capacity figure for the
    framework across all scenarios/regions; actual per-activation reach has been far
    smaller (e.g. 1,120 people in the Nov 2025 partial activation) since PRC scales
    early action to the areas forecast highest-risk, not the full footprint.
visibility: public
---

# IFRC — Philippines tropical cyclone

## Summary
The Philippine Red Cross's typhoon Early Action Protocol, developed with German Red Cross
and IFRC support and pre-financed through the IFRC Disaster Response Emergency Fund (DREF)
anticipatory pillar. Now in its second generation (EAP2024PH03/MDRPH055, effective
2024-09-23 to 2029-09-30), it covers 25 provinces across five regions (North Luzon, Central
Luzon, Bicol, Visayas, Mindanao) and funds shelter-strengthening, livestock evacuation, and
early-harvest actions ahead of landfall.

## Trigger
The original EAP (EAP2019PH01, approved Nov 2019) triggered on a 510-Initiative statistical
model: forecast winds implying >10% of houses totally damaged across more than three
municipalities, 72h lead time. The 2024 revision (EAP2024PH03) moved to a wind-speed based
design: ECMWF forecasts are the main trigger input, with PAGASA bulletins used for
monitoring; the readiness/early-action trigger can fire up to 72h before landfall, and if
not met by then, an observational trigger — a PAGASA-confirmed super typhoon (≥185 km/h
10-minute sustained winds) — can still fire any time from 72h before landfall through
landfall itself.

## Funding & scope
CHF 535,290 pre-arranged under EAP2024PH03 (≈US$0.608M): CHF 318,890 for
readiness/prepositioning, CHF 216,399 released automatically once the trigger is met. Prior
generation (EAP2019PH01) was CHF 249,540. Early actions: shelter-strengthening kits,
livestock/asset evacuation, early crop harvesting, implemented via cash-for-work with
barangay disaster committees (BARCOM) and provincial/municipal DRRM offices.

## Activations
- **Dec 2019, Typhoon Tisoy (Kammuri)** — first test of EAP2019PH01, ~200 households.
- **Oct 2022, Typhoon Paeng (Nalgae)** — full activation at a shortened 56h lead time
  (exceptionally granted); CHF 16,981 released; SSK distribution to affected barangays.
- **Nov 2025, Super Typhoon Fung-wong (Uwan)** — first activation of the revised
  EAP2024PH03, triggered by a PAGASA forecast of 195 km/h winds within 96h; partial
  activation (CHF 20,725) reaching 224 households (1,120 people) in Quirino, Isabela, and
  Quezon-Lucena.
- **Not activated:** Typhoon Kalmaegi (Nov 2025, just before Fung-wong) — wind-speed
  trigger not met.

Note: OCHA/CERF also runs a separate, larger collective AA framework for Philippine
tropical cyclones ([`phl-storms`](../../frameworks/phl-storms/README.md)), which activated
independently for the same Fung-Wong/Uwan event in Nov 2025 — see `extra.coordination`.

## Sources
- **Authoritative:** [EAP Summary, EAP2024PH03/MDRPH055](https://reliefweb.int/report/philippines/philippines-typhoon-early-action-protocol-summary-eap-no-eap2024ph03-operation-no-mdrph055) (approved 2024-09-23)
- [Anticipation Hub — Philippines FbF](https://www.anticipation-hub.org/global-overview/countries/philippines/forecast-based-financing-fbf-in-the-philippines)
- [Original EAP fact sheet (EAP2019PH01)](https://www.anticipation-hub.org/Documents/Briefing_Sheets_and_Fact_Sheets/Philippines_Typhoon_EAP_Fact_Sheet.pdf)
- [Anticipation Hub — Fung-wong activation news](https://www.anticipation-hub.org/news/the-philippine-red-cross-acts-to-protect-people-ahead-of-tropical-storm-fungwong)
- [Typhoon Paeng EAP activation final report](https://reliefweb.int/report/philippines/philippines-typhoon-paeng-early-action-protocol-activation-final-report-eap-no-eap2019ph01-operation-no-mdrph049-30-june-2023) (30 Jun 2023) · [activation notification](https://reliefweb.int/report/philippines/eap-activation-notification-philippines-typhoon-operation-mdrph049)
- [EAP2024PH03 activation report](https://reliefweb.int/report/philippines/philippines-typhoon-early-action-protocol-activation-report-eap-no-eap2024ph03-operation-no-mdrph055-30-april-2026) (due 30 Apr 2026)
- [IFRC GO — Philippines Typhoons and Floods emergency](https://go.ifrc.org/emergencies/7196)
