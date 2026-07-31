---
content_type: framework-external
framework: ifrc-bdi-flood
org: IFRC
country_iso3: BDI
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Rising water level of Lake Tanganyika — historically ≥771.2m marks the "first level of
  danger" for overflow into the lakebed — combined with IGEBU (Burundi's meteorological
  agency) seasonal and short-range rainfall forecasts (e.g. 55-65% probability of
  above-normal March-May rains). IGEBU monitors and confirms the forecast in coordination
  with the Burundi Red Cross and WFP; a confirmed trigger releases pre-positioned stock and
  cash early actions in the most exposed western communes (Bujumbura Mairie, Bujumbura
  Rural, Rumonge, Makamba, Cibitoke, Bubanza).
data_sources: [IGEBU]
prearranged_funding_usd: 199072
funding_by_source: {DREF: 199072}
target_people: 9000
framework_doc: /download/file-4881
framework_doc_date: 2024-07-05
sources:
- /download/file-4881
- https://reliefweb.int/report/burundi/burundi-extreme-floods-simplified-early-action-protocol-seap-no-seap2023bu01-operation-no-mdrbi021
- https://reliefweb.int/report/burundi/burundi-extreme-floods-simplified-early-action-protocol-annual-report-seap-no-seap2023bu01-operation-no-mdrbi021-november-2025
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRBI021
- https://www.anticipation-hub.org/news/the-first-official-anticipatory-action-activation-in-burundi
- https://www.preventionweb.net/news/first-official-anticipatory-action-activation-burundi
- https://www.anticipation-hub.org/global-overview/countries/burundi
- https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-18'
extra:
  hub_captions:
  - '2024: Flood (IFRC) [Burundi Red Cross]'
  hub_years:
  - '2024'
  implementing:
  - Burundi Red Cross
  eap_no: sEAP2023BU01
  operation_no: MDRBI021
  funding_chf: >-
    The Nov 2025 annual report on MDRBI021 gives the DREF allocation as CHF 175,382
    (CHF 33,423 stock prepositioning + CHF 75,721 readiness + CHF 66,238 reserved for early
    actions on trigger — the last tranche appears unspent as of that report, i.e. no
    confirmed trigger fire). The Anticipation Hub's country overview states a $199,072
    budget for this framework; the two figures are not a straight currency conversion, so
    both are recorded here rather than reconciled. Underlying EAP development was also
    supported by Italian Government funding channelled via the Italian Red Cross
    (technical assistance, not part of the DREF figure above).
  coordination: >-
    Burundi has two separate, parallel flood anticipatory-action frameworks per the
    Anticipation Hub's country overview: WFP's (funded via its own ECHO project,
    targeting ~5,880 people) and this Burundi Red Cross/IFRC one (DREF-funded,
    targeting 9,000 people). The widely-reported "first official anticipatory action
    activation in Burundi" (forecast 31 Oct 2023, IGEBU confirmation 8 Nov, cash
    distributed 10-14 Nov 2023 to 1,780 households in Muhuta and Rumonge, ~$145,960 total)
    was implemented jointly by WFP and the Burundi Red Cross on the ground, but the funds
    disbursed came from WFP's ECHO allocation, not the Red Cross DREF/EAP mechanism, and
    the ~5,880-person scale matches WFP's framework rather than this one's 9,000-person
    target. Treat that Nov 2023 event as WFP's framework activation (with BRC as an
    operational partner), not a confirmed trigger of sEAP2023BU01/MDRBI021 — see
    `extra.schema_strain`.
  partners: WFP, IGEBU (Institut Géographique du Burundi), RCRC Climate Centre, Italian
    Red Cross (technical-assistance funding via the Italian Government)
  schema_strain: >-
    No confirmed independent trigger/activation of this specific DREF-funded EAP
    (sEAP2023BU01/MDRBI021) was found in public sources as of last_checked — the Nov 2025
    annual report's unspent "early action" tranche suggests it had not fired by then;
    `activations` left empty rather than counting the Nov 2023 WFP-led event (see
    `extra.coordination`). No fixed EAP validity end-date found; `valid_until` left null.
visibility: public
---

# IFRC — Burundi flood

## Summary
The Burundi Red Cross's (BRC) Simplified Early Action Protocol for extreme floods
(sEAP2023BU01, IFRC DREF operation MDRBI021, published 5 July 2024) targets roughly 9,000
people in flood-prone western Burundi — the Lake Tanganyika basin and its tributary
catchments (Bujumbura Mairie, Bujumbura Rural, Rumonge, Makamba, Cibitoke, Bubanza). It
triggers on rising Lake Tanganyika water levels combined with IGEBU rainfall forecasts, and
runs alongside — but separately from — WFP's own flood anticipatory-action framework in the
same country (see `extra.coordination`).

## Trigger
Monitored by IGEBU (Burundi's meteorological/hydrological agency) in coordination with BRC
and WFP. The core indicator is the water level of Lake Tanganyika, whose historical overflow
threshold is documented at approximately 771.2m — described as the "first level of danger"
for extreme-rainfall flooding of the minor lakebed — layered with IGEBU's seasonal rainfall
outlook (e.g. the March-May 2024 season was forecast at 55-65% probability of above-normal
rainfall) and shorter-range forecast confirmation ahead of peak rains. A confirmed trigger
releases pre-positioned relief stock and cash-based early actions in the most exposed
communes.

## Funding & scope
IFRC DREF, operation MDRBI021: per the Nov 2025 annual report, CHF 175,382 allocated (CHF
33,423 stock prepositioning, CHF 75,721 readiness, CHF 66,238 reserved for early actions on
trigger — apparently still unspent at that point). The Anticipation Hub's country overview
separately states a $199,072 budget for this framework (see `extra.funding_chf` for the
reconciliation caveat). Target: ~9,000 people. EAP development received technical and
financial support from the Italian Red Cross (Italian Government funding).

## Activations
None confirmed for this EAP (sEAP2023BU01/MDRBI021) as of last_checked. The widely-covered
"first official anticipatory action activation in Burundi" (Oct-Nov 2023, Muhuta and
Rumonge communes, 1,780 households, ~$145,960 in cash) was a joint WFP/Burundi Red Cross
operation funded through WFP's own ECHO-financed anticipatory action framework, not this
EAP's DREF mechanism — see `extra.coordination` for why it isn't counted here.

## Sources
- **Authoritative:** [Simplified EAP: Burundi — Extreme Floods](/download/file-4881) (Anticipation Hub, published 5 Jul 2024) — also indexed on [ReliefWeb](https://reliefweb.int/report/burundi/burundi-extreme-floods-simplified-early-action-protocol-seap-no-seap2023bu01-operation-no-mdrbi021)
- [Annual report, sEAP2023BU01/MDRBI021 (Nov 2025)](https://reliefweb.int/report/burundi/burundi-extreme-floods-simplified-early-action-protocol-annual-report-seap-no-seap2023bu01-operation-no-mdrbi021-november-2025) — funding breakdown, implementation status
- [IFRC GO — appeal MDRBI021](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRBI021) (machine-readable budget/status)
- [Anticipation Hub — "The first official anticipatory action activation in Burundi"](https://www.anticipation-hub.org/news/the-first-official-anticipatory-action-activation-in-burundi) / [PreventionWeb mirror](https://www.preventionweb.net/news/first-official-anticipatory-action-activation-burundi) — Nov 2023 WFP/BRC joint activation (see `extra.coordination`)
- [Anticipation Hub — Burundi country overview](https://www.anticipation-hub.org/global-overview/countries/burundi) — two-framework (WFP + IFRC) breakdown, aggregate funding/target figures
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record, fetched 2026-07-10)
