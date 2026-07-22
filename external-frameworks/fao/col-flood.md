---
content_type: framework-external
framework: fao-col-flood
org: FAO
country_iso3: COL
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Two-phase seasonal-forecast trigger (no single public numeric river/GloFAS threshold):
  Phase 1 activates on a high probability of above-average rainfall from ENSO/La Niña
  seasonal outlooks (2024 cycle: 65% probability of surplus rainfall by late July,
  operationalized in August); Phase 2 activates when La Niña forecasts are corroborated by
  IDEAM (Instituto de Hidrología, Meteorología y Estudios Ambientales) short-range reports
  — in 2024, a 60-80% likelihood of surplus rainfall by mid-September. Phase 2 releases
  funds for flood-prone departments. See `extra.schema_strain`.
data_sources: [IDEAM, ENSO]
prearranged_funding_usd: 600000
funding_by_source: {SFERA: 600000}
target_people: 25565
framework_doc: https://www.anticipation-hub.org/download/file-5003
framework_doc_date: 2025
sources:
- https://www.anticipation-hub.org/download/file-5003
- https://www.anticipation-hub.org/Documents/Framework_documents/FAO-SFERA-2024-cd5429en.pdf
- https://openknowledge.fao.org/items/d51e8cc0-67ab-463c-89d2-65a04a6c5ab7
- https://www.anticipation-hub.org/experience/global-map
- https://www.anticipation-hub.org/news/eighteen-organizations-call-for-coordinated-anticipatory-action-to-be-scaled-up-in-colombia
- https://www.acaps.org/fileadmin/Data_Product/Main_media/20240802_ACAPS_Colombia_analysis_hub_Flooding_in_La_Mojana.pdf
activations:
- date: 2024-09
  url: https://www.anticipation-hub.org/download/file-5003
  note: >-
    2024 La Niña flood cycle: Phase 1 (Aug, 65% probability of surplus rainfall)
    followed by Phase 2 (Sep, IDEAM/La Niña 60-80% likelihood of surplus rainfall)
    triggered anticipatory actions in Sucre (La Mojana region), Chocó, Nariño (Pacific
    region) and the San Andrés, Providencia and Santa Catalina archipelago — cash
    transfers, food/seed supply centres, elevated gardens, livestock shelters, drainage
    systems, and training for indigenous and Afro-Colombian groups, animal-health teams
    and municipal seed banks. US$600,000 (Belgium, via SFERA) reached ~6,730 farming
    families (reported as 25,565 people) and protected 15,000 livestock. Floods
    materialized in the Chocó region in Nov 2024, after the anticipatory phase.
last_checked: '2026-07-22'
extra:
  hub_captions:
  - '2024: Flood (FAO) [FAO]'
  hub_years:
  - '2024'
  implementing:
  - FAO
  coordination: >-
    Colombia has a broader national multi-hazard AA landscape — 12 frameworks (drought,
    flood, hurricane, dengue, complex crises) run by different organisations, per the
    Anticipation Hub's Sep 2024 "Eighteen organisations" coordination declaration, aligned
    with UNGRD Circular 070-2024 institutionalizing AA in national disaster-risk
    management. This KB holds no OCHA/CERF collective framework page for Colombia (no
    `frameworks/` entry exists), so this FAO flood protocol is FAO's own framework rather
    than a component of an OCHA-coordinated collective one.
  schema_strain: >-
    No public document gives a single quantitative threshold (e.g. a river-gauge level or
    GloFAS return-period value) or a fixed lead-time window; the trigger is described only
    as a two-phase ENSO/La Niña-forecast + IDEAM-corroboration mechanism, re-assessed each
    cycle. `trigger_summary` reflects that looseness rather than an unstated number.
  prior_flood_context: >-
    Independent of this AA protocol, the La Mojana dike/embankment system (Cara de Gato,
    Los Arrastres) failed in May 2024, flooding ~27,039 people across San Jacinto del
    Cauca, Guaranda, Sucre, Majagual, San Benito Abad and San Marcos — a reactive
    emergency (OCHA/FAO/UNICEF/PAHO/World Vision inter-agency mission) that predates and
    is separate from the Aug-Sep 2024 AA trigger cycle described above.
visibility: public
---

# FAO — Colombia flood

## Summary
FAO Colombia runs a La Niña/ENSO-triggered flood anticipatory action protocol protecting
agropastoral livelihoods in flood-prone departments — the La Mojana subregion (Sucre),
Chocó and Nariño on the Pacific coast, and the San Andrés, Providencia and Santa Catalina
archipelago. The 2024 cycle was financed by the Government of Belgium (US$600,000)
through FAO's SFERA Anticipatory Action window, reaching roughly 6,730 farming families
(~25,565 people) and protecting 15,000 livestock. It sits alongside FAO's separate
El Niño-triggered drought AA programme in Colombia ([`col-drought.md`](col-drought.md))
and within a wider, multi-organisation national AA landscape (see `extra.coordination`).

## Trigger
A two-phase seasonal-forecast mechanism rather than a single published numeric threshold.
In the 2024 cycle: Phase 1 activated in August on a 65% probability of above-average
rainfall forecast for late July; Phase 2 activated when La Niña forecasts were
corroborated by IDEAM (Colombia's national hydrology/meteorology institute) reporting a
60-80% likelihood of surplus rainfall by mid-September. Phase 2 releases pre-arranged
funds for implementation in the identified flood-prone areas. No GloFAS threshold, river
level, or fixed lead-time window is documented publicly; see `extra.schema_strain`.

## Funding & scope
US$600,000 pre-arranged, financed by the Government of Belgium through FAO's SFERA
(Special Fund for Emergency and Resilience Activities) Anticipatory Action window,
targeting an estimated 25,565 people (~6,730 vulnerable farming families) and 15,000
livestock across Sucre (La Mojana), Chocó, Nariño and the San Andrés archipelago.
Interventions: cash transfers, food and seed supply centres, elevated/raised gardens,
livestock shelters, drainage systems, and training for indigenous and Afro-Colombian
groups, animal-health teams and municipal seed banks.

## Activations
- **Aug-Sep 2024** — Phase 1 (Aug, 65% surplus-rainfall probability) then Phase 2 (Sep,
  IDEAM/La Niña 60-80% likelihood) triggered the anticipatory package described above in
  Sucre, Chocó, Nariño and the San Andrés archipelago. Floods subsequently materialized in
  the Chocó region in November 2024.

No FAO-attributed activation is documented before the 2024 cycle. The severe May 2024
La Mojana dike-failure flooding (~27,039 people affected) predates this AA trigger cycle
and was addressed as a reactive inter-agency emergency response, not an FAO AA activation
— see `extra.prior_flood_context`.

## Sources
- **Authoritative:** [FAO SFERA Annual report 2024](https://www.anticipation-hub.org/download/file-5003) (Anticipation Hub-hosted PDF, also at [the direct FAO mirror](https://www.anticipation-hub.org/Documents/Framework_documents/FAO-SFERA-2024-cd5429en.pdf); Rome, 2025) — Annex 5 "Colombia" entry and AA-window funding table
- [FAO/openknowledge — Colombia: Belgium's contribution through the Special Fund for Emergency and Rehabilitation Activities (SFERA) – Anticipatory Action window](https://openknowledge.fao.org/items/d51e8cc0-67ab-463c-89d2-65a04a6c5ab7) (19 Sep 2024; funding and target-people/livestock figures; full text returned 403 to automated fetch, details confirmed via search index)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory listing)
- [Anticipation Hub — Eighteen organizations call for coordinated anticipatory action to be scaled up in Colombia](https://www.anticipation-hub.org/news/eighteen-organizations-call-for-coordinated-anticipatory-action-to-be-scaled-up-in-colombia) (national AA coordination context, UNGRD Circular 070-2024)
- [ACAPS Briefing note — Colombia: Flooding in La Mojana (8 Aug 2024)](https://www.acaps.org/fileadmin/Data_Product/Main_media/20240802_ACAPS_Colombia_analysis_hub_Flooding_in_La_Mojana.pdf) (context for the May 2024 La Mojana dike-failure flooding, prior to this AA cycle)
