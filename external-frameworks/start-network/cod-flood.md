---
content_type: framework-external
framework: start-network-cod-flood
org: START
country_iso3: COD
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Global forecast data (Start Ready's flood model, referenced in Start Network materials
  as JBA-supported) indicates riverine flooding in the Congo/Maniema river system up to
  ~10 days ahead; district-level contingency plans under Start Network's "Start Ready"
  risk-pooling facility set locally-specific danger thresholds, and pre-agreed funding
  releases automatically to member NGOs for pre-designed anticipatory activities when a
  threshold is met. Operational in Maniema (Kindu) since 2022, expanded to Kinshasa in
  2024. The precise river gauge/percentile threshold and lead-time definition for the DRC
  system specifically were not found in public sources (see `extra.schema_strain`).
data_sources: [JBA]
prearranged_funding_usd: 1436782
funding_by_source: {Start Ready: 1436782}
target_people: 34477
framework_doc: https://reliefweb.int/report/world/start-ready-risk-pool-01-summary-report-may-2022-april-2023
framework_doc_date: 2023-10
sources:
- https://reliefweb.int/report/world/start-ready-risk-pool-01-summary-report-may-2022-april-2023
- https://startnetwork.org/network/hubs/democratic-republic-congo-hub
- https://startnetwork.org/funds/start-ready/activations/act-00000017
- https://startnetwork.org/learn-change/news-and-blogs/when-forecasts-failed-action-didnt-start-readys-experience-basis-risk
- https://www.anticipation-hub.org/global-overview/countries/democratic-republic-of-congo
- https://drc.actionaid.org/news/2025/start-ready-funded-flood-preparedness-project-kicks-kinshasa-actionaid-drc
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: '2022-09'
  url: https://startnetwork.org/funds/start-ready/activations/act-00000017
  note: >-
    RP1 DRC Floods — riverine flooding in Kindu, Maniema province, met the Start Ready
    Risk Pool 1 (May 2022-Apr 2023) threshold. £525,000 disbursed (18 Feb 2023) to two
    local members (MIDEFEHOPS, Caritas Kindu per Hub captions) reaching ~28,968 people,
    plus a separate £1,125,000 to an international member (Christian Aid) for the same
    response.
- date: '2023'
  url: https://www.anticipation-hub.org/global-overview/countries/democratic-republic-of-congo
  note: >-
    Hub-recorded activation year for the DRC flood framework — 76,936 people reached,
    $2,100,314 disbursed. Implementing partners per Hub listing: AFPDE, MIDEFEHOPS. No
    dedicated Start Network activation page found for this year specifically.
- date: '2024'
  url: https://www.anticipation-hub.org/global-overview/countries/democratic-republic-of-congo
  note: >-
    Hub-recorded activation year, coinciding with the system's stated expansion to
    Kinshasa. The Hub lists figures identical to 2023 (76,936 people / $2,100,314) —
    possibly a display duplication rather than a second distinct disbursement (see
    `extra.schema_strain`). Implementing partners per Hub listing: CAFOD, Caritas Kindu.
last_checked: '2026-07-24'
extra:
  hub_captions:
  - '2022: Flood (Start Network) [Christian Aid] [MIDEFEHOPS] [ALIMA] [Caritas Kindu]'
  - '2023: Flood (Start Network) [AFPDE] [MIDEFEHOPS]'
  - '2024: Flood (Start Network) [CAFOD] [Caritas Kindu]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - CAFOD
  - Caritas Kindu
  near_miss: >-
    April 2025: heavy rainfall and Congo river overflow flooded Kinshasa (~165 deaths,
    7,000+ displaced, 60,000+ affected). The flood-forecast model Start Ready uses did
    NOT predict the event — a basis-risk failure — so the automatic funding trigger never
    fired. Start Ready delivered funding through a stop-gap/manual mechanism instead,
    after missing the initial anticipatory window; Start Network published this as a
    basis-risk case study. Not counted in `activations` above since the forecast trigger
    itself did not activate.
  ongoing_programming: >-
    A Start Ready-funded flood-preparedness project led by ActionAid International DRC
    (with CBS, PADECO, AFPDE, and DRC Hub coordination support) launched community
    workshops in Kinshasa's Limete and Ngaliema communes in Nov 2025, part of the
    2024 Kinshasa expansion.
  funding_discrepancy: >-
    The Anticipation Hub's DRC country-page view (fetched 2026-07-24) shows a larger
    aggregate for the Start Network flood framework — 396,237 people targeted, $3,506,743
    total budget — than the map-API record used to create this page's original stub
    (34,477 / $1,436,782, fetched 2026-07-10). Likely different aggregation windows
    (single risk-pool record vs cumulative multi-year framework total); kept the original
    map-API figures as the frontmatter values since they match a single dated pull, but
    flagging rather than guessing which is "the" framework total.
  schema_strain: >-
    Could not confirm the DRC-specific river gauge/threshold/lead-time definition from a
    primary Start Network or ReliefWeb document — startnetwork.org and reliefweb.int both
    returned HTTP 403 to automated fetch (per README, Hub-hosted PDF mirrors fetch best,
    but no DRC-specific PDF mirror was located); trigger_summary is built from Start
    Ready's general mechanism description plus secondary reporting, not a DRC-specific
    published protocol. `valid_until` left null — Start Ready runs as successive named
    Risk Pools (RP1 2022-23, RP2 2023-24, RP3, RP4) rather than one fixed-validity
    framework, and no single end-date was found.
visibility: public
---

# START — Congo flood

## Summary
Start Network's Democratic Republic of Congo Hub runs a riverine flood anticipatory
action system financed through **Start Ready**, Start Network's pooled disaster risk
financing facility (distinct from IFRC's DREF/EAP or WFP's AA mechanisms). Operational
in Maniema province (Kindu, on the Congo river system) since 2022 and expanded to
Kinshasa in 2024, it uses global flood-forecast data to trigger pre-agreed funding to
member NGOs — among them Christian Aid, MIDEFEHOPS, ALIMA, Caritas Kindu, AFPDE, CAFOD,
and (from the 2024 Kinshasa expansion) ActionAid International DRC.

## Trigger
Start Ready's flood system uses global forecasting data (reported in Start Network
materials in connection with JBA's flood modelling) to indicate riverine flooding up to
roughly 10 days ahead; district-level contingency plans define the specific danger
thresholds for each covered area, and funding releases automatically to pre-agreed member
NGOs once a threshold is met. The exact river gauge, forecast percentile, and lead-time
definition specific to the DRC system were not found in the public sources reachable for
this page (both startnetwork.org and reliefweb.int returned HTTP 403 to automated
fetch) — see `extra.schema_strain`. Basis risk is material: in April 2025 the model
failed to forecast severe Kinshasa flooding (see Activations).

## Funding & scope
Financed through Start Ready (not DREF/SFERA/WFP). The Anticipation Hub's map-API record
for this framework shows $1,436,782 prearranged, targeting 34,477 people; the Hub's DRC
country-page view shows a larger aggregate (396,237 people / $3,506,743) that likely
reflects a different, cumulative aggregation window (see `extra.funding_discrepancy`).
Individual disbursements have been denominated in GBP (e.g. £525,000 and £1,125,000 for
the 2022 Kindu response).

## Activations
- **Sept-Oct 2022** (RP1 DRC Floods) — riverine flooding in Kindu, Maniema, met the Start
  Ready Risk Pool 1 threshold; £525,000 disbursed (18 Feb 2023) to two local members
  (MIDEFEHOPS, Caritas Kindu) reaching ~28,968 people, plus £1,125,000 to an
  international member (Christian Aid) for the same response.
- **2023** — Hub-recorded activation year: 76,936 people reached, $2,100,314 disbursed
  (AFPDE, MIDEFEHOPS).
- **2024** — Hub-recorded activation year, coinciding with the system's expansion to
  Kinshasa: figures identical to 2023 per the Hub (76,936 people / $2,100,314; CAFOD,
  Caritas Kindu) — possibly a display duplication rather than a confirmed second
  disbursement.
- **April 2025 (near-miss, not counted above)** — Kinshasa flooding (~165 deaths, 7,000+
  displaced, 60,000+ affected) was not forecast by Start Ready's flood model (a basis-risk
  failure); the automatic trigger did not fire, and funding was instead released through a
  stop-gap manual mechanism, missing the initial anticipatory window. Start Network
  published this as a basis-risk case study.

## Sources
- **Authoritative:** [Start Ready — Risk Pool 01 Summary Report, May 2022-April 2023 (Oct 2023)](https://reliefweb.int/report/world/start-ready-risk-pool-01-summary-report-may-2022-april-2023)
- [Democratic Republic of the Congo Hub](https://startnetwork.org/network/hubs/democratic-republic-congo-hub) (Start Network)
- [RP1 DRC Floods — activation record](https://startnetwork.org/funds/start-ready/activations/act-00000017) (Start Network)
- [When forecasts failed, but action didn't — Start Ready's experience with basis risk](https://startnetwork.org/learn-change/news-and-blogs/when-forecasts-failed-action-didnt-start-readys-experience-basis-risk) (Start Network, on the Apr 2025 Kinshasa event)
- [Anticipatory action in Democratic Republic of Congo](https://www.anticipation-hub.org/global-overview/countries/democratic-republic-of-congo) (Anticipation Hub country page, fetched 2026-07-24)
- [Start Ready-Funded Flood Preparedness Project Kicks Off in Kinshasa](https://drc.actionaid.org/news/2025/start-ready-funded-flood-preparedness-project-kicks-kinshasa-actionaid-drc) (ActionAid DRC, Nov 2025)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record, fetched 2026-07-10)
