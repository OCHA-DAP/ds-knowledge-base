---
content_type: framework-external
framework: ifrc-mli-flood
org: IFRC
country_iso3: MLI
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Mali's National Directorate of Hydraulics (DNH) monitors river levels at 26 hydrometric
  stations nationwide; the EAP activates once a station's downstream water level exceeds
  the local 5-year return period (derived from the historical upstream/downstream
  relationship for August-September), triggering a 96-hour (4-day) lead time. In practice
  the confirmed 2022 activation fired at the Sofara gauge on the Bani River reaching the
  "orange alert" level of 633 cm.
data_sources: [DNH]
prearranged_funding_usd: 219610
funding_by_source: {DREF-FbA: 209532}
target_people: 5000
framework_doc: https://adore.ifrc.org/Download.aspx?FileId=369555
framework_doc_date: 2020-09-17
sources:
- https://adore.ifrc.org/Download.aspx?FileId=369555
- https://adore.ifrc.org/Download.aspx?FileId=570944
- https://www.anticipation-hub.org/Documents/Reports/flood-early-action-protocol-trigger-report-mali.pdf
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRML017
- https://reliefweb.int/report/mali/mali-riverine-floods-early-action-protocol-summary-eap-no-eap2023ml002-operation-no-mdrml021
- https://www.anticipation-hub.org/global-overview/countries/mali
- https://www.anticipation-hub.org/global-overview/countries/mali/forecast-based-financing-in-mali
- https://www.anticipation-hub.org/news/acting-in-anticipation-of-severe-floods-in-mali
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2022-09-04
  url: https://www.anticipation-hub.org/Documents/Reports/flood-early-action-protocol-trigger-report-mali.pdf
  note: >-
    Only confirmed activation, under first-generation EAP2020ML01 (operation MDRML017).
    DNH observed the Bani River at Sofara exceed the 633 cm orange alert level around
    1 September 2022, with a sharp upstream (Bagoè/Baoulé) rise and the opening of the
    Djenné threshold valves adding to the risk; the automatic CHF 62,890 early-action
    tranche was released and a 4-8 September intervention followed in Kaka, Bellokim and
    Sofara's 3ème quartier (Djenné circle, Mopti region) — 271 households (~3,045 people)
    assisted: 23 households evacuated, shelter/kitchen kits and mosquito nets/aquatabs/
    bleach distributed, sandbag/banco protection of houses, a mosque and the Sofara
    cattle market. IFRC GO records the MDRML017 appeal (started 2 Sept 2022) as fully
    funded (CHF/USD 62,890) and closed.
last_checked: '2026-07-18'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Mali Red Cross] [The Netherlands Red Cross] [Danish Red Cross]'
  hub_years:
  - '2022'
  implementing:
  - Mali Red Cross
  - The Netherlands Red Cross
  - Danish Red Cross
  - Belgian Red Cross
  eap_no: EAP2020ML01
  operation_no: MDRML017
  funding_detail: >-
    CHF 209,532 total from the IFRC DREF Forecast-based Action (FbA) mechanism: CHF 87,983
    readiness, CHF 58,658 pre-positioned stock (shelter/WASH items), CHF 62,890 released
    automatically once the trigger is met. `prearranged_funding_usd` (219,610) is the
    Anticipation Hub's own USD conversion, current as of its live country page.
  eap_timeframe: >-
    5-year EAP timeframe from the 17 September 2020 approval (nominally through ~2025).
    ReliefWeb lists a further "Mali | Riverine Floods: Early Action Protocol Summary
    (EAP No: EAP2023ML002, Operation No: MDRML021)" — a likely second generation/renewal
    — but the page returned HTTP 403 to direct and archived fetch and no mirror was found,
    so its trigger, budget and target figures are unconfirmed (see `schema_strain`). The
    Anticipation Hub's live country page still lists this framework as active with the
    same $219,610/5,000-people figures as the original stub, so `status: active` is kept
    rather than marking it expired.
  trigger_detail: >-
    Alert bands: green/yellow (Feb-Jun, preparation/training/surveillance) - orange
    (Jul-Nov, stepped-up monitoring) - red (activation, resource positioning within the
    96-hour lead time). The 633 cm figure is the Sofara station's own orange-alert
    threshold on the Bani River; the EAP's underlying rule (downstream level vs. the local
    5-year return period) is applied independently at each of DNH's 26 monitoring stations,
    so other stations/regions would have different absolute thresholds.
  coordination: >-
    No OCHA/CERF collective AA framework for Mali floods was found in this KB's
    `frameworks/` directory — this is a standalone Mali Red Cross (Croix-Rouge Malienne,
    CRM) instrument funded through the IFRC DREF, not a component of a collective
    framework.
  partners: >-
    Belgian Red Cross, Danish Red Cross and Netherlands Red Cross (technical/financial
    support to CRM); 510 (data collection/analysis); RCRC Climate Centre (trigger design);
    government technical services — National Directorate of Hydraulics (DNH), Mali Météo,
    General Directorate of Civil Protection (DGPC), National Directorate of Social
    Development (DNDS/DNDSES), National Directorate of Health (DNS), National Centre for
    Early Warning Coordination (CNAP); WFP, World Vision, IEDA-RELIEF, CRS, ACF, Care
    International, Wetlands International, OCHA, IOM and WHO consulted during EAP design.
  schema_strain: >-
    The IFRC GO API query for operation code MDRML021 (the presumed EAP2023ML002 operation
    number) returned internally inconsistent data — disaster type "Cyclone" for landlocked
    Mali, a Niger/Côte d'Ivoire/Burkina Faso/Mali multi-country cluster, and 2025-2030
    dates — which does not match a Mali flood EAP and looks like a garbled/wrong record
    (possibly a fetch-tool artifact); it was not used here. ReliefWeb's EAP2023ML002
    summary page 403'd on both direct and web.archive.org fetch attempts, and no
    Hub-hosted PDF mirror was located, so beyond its existence (confirmed by the ReliefWeb
    page title) nothing about a second-generation EAP's trigger, budget or target
    population could be sourced. All trigger/funding/target detail above is drawn from the
    original EAP2020ML01 documents and the confirmed 2022 activation.
visibility: public
---

# IFRC — Mali flood

## Summary
The Mali Red Cross's (Croix-Rouge Malienne, CRM) flood Early Action Protocol (EAP2020ML01,
approved 17 September 2020), funded through the IFRC Disaster Relief Emergency Fund's
Forecast-based Action (FbA) mechanism with technical/financial support from the Belgian,
Danish and Netherlands Red Cross societies. It targets 1,000 vulnerable households
(~5,000 people) countrywide with evacuation support, shelter/WASH item distribution and
sandbag-based house protection, triggered by river-level monitoring from Mali's National
Directorate of Hydraulics (DNH). Its one confirmed activation, in September 2022, protected
communities around Sofara (Mopti region) as the Bani River crossed its orange alert level. A
second-generation EAP (EAP2023ML002/MDRML021) is referenced on ReliefWeb but its details could
not be sourced (see `extra.schema_strain`).

## Trigger
DNH monitors river levels at 26 hydrometric stations across Mali. The EAP activates once a
station's downstream water level exceeds the local 5-year return period — calculated from the
historical relationship between upstream and downstream maximum daily levels during
August-September — giving a 96-hour (4-day) lead time for early actions. The system runs on a
four-band alert scale: green/yellow (Feb-Jun, preparation), orange (Jul-Nov, heightened
monitoring), and red (activation). The confirmed 2022 activation fired when the Bani River at
the Sofara gauge (Djenné circle, Mopti region) exceeded the 633 cm orange alert level, following
a sharp upstream rise and the opening of the Djenné threshold's valves.

## Funding & scope
CHF 209,532 (~USD 219,610 per the Anticipation Hub) from the IFRC DREF's Forecast-based Action
mechanism: CHF 87,983 for readiness, CHF 58,658 for pre-positioned shelter/WASH stock, and CHF
62,890 released automatically once the trigger is met. Targets 1,000 households (~5,000 people,
split roughly 400 male-/600 female-headed) nationwide, implemented by the Mali Red Cross with
Belgian, Danish and Netherlands Red Cross support and Mali government technical services (DNH,
Mali Météo, DGPC, DNDS, DNS, CNAP).

## Activations
- **4-8 September 2022** (EAP2020ML01, operation MDRML017) — the only confirmed activation.
  DNH observed the Bani River at Sofara cross the 633 cm orange alert level around 1 September,
  amid a sharp rise upstream and the opening of the Djenné threshold valves. The CHF 62,890
  automatic early-action tranche was released; over four days the Mali Red Cross evacuated 23
  households, distributed shelter kits, mosquito nets, aquatabs and bleach, and built
  sandbag/banco flood defences (protecting a mosque and the Sofara cattle market) across Kaka,
  Bellokim and Sofara's 3ème quartier — 271 households (~3,045 people) assisted in total. The
  IFRC GO appeal (MDRML017) records the operation as fully funded and closed.
- No sourced record of a distinct activation in 2023 or later was found, despite ReliefWeb
  listing a further EAP generation (EAP2023ML002/MDRML021) — see `extra.schema_strain`.

## Sources
- **Authoritative:** [EAP summary, EAP2020ML01, approved 17 September 2020](https://adore.ifrc.org/Download.aspx?FileId=369555)
- [Early Action Notification — Mali Floods, EAP2020ML01 (Sept 2022 trigger)](https://adore.ifrc.org/Download.aspx?FileId=570944)
- [Mali Red Cross — Flood EAP Trigger Report, Sofara/Kaka activation, 4-8 Sept 2022](https://www.anticipation-hub.org/Documents/Reports/flood-early-action-protocol-trigger-report-mali.pdf)
- [IFRC GO API — MDRML017](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRML017) (machine-readable budget/status)
- [ReliefWeb — Mali Riverine Floods EAP Summary, EAP2023ML002/MDRML021](https://reliefweb.int/report/mali/mali-riverine-floods-early-action-protocol-summary-eap-no-eap2023ml002-operation-no-mdrml021) (403 on fetch; existence only, content unconfirmed)
- [Anticipation Hub — Mali](https://www.anticipation-hub.org/global-overview/countries/mali) (current inventory figures)
- [Anticipation Hub — Forecast-based Financing in Mali](https://www.anticipation-hub.org/global-overview/countries/mali/forecast-based-financing-in-mali)
- [Anticipation Hub — Acting in anticipation of severe floods in Mali](https://www.anticipation-hub.org/news/acting-in-anticipation-of-severe-floods-in-mali) (2022 activation detail)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
