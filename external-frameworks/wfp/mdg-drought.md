---
content_type: framework-external
framework: wfp-mdg-drought
org: WFP
country_iso3: MDG
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  A district-level composite trigger score (combining DGM/IRI seasonal rainfall forecasts,
  observed indicators and vulnerability data) is monitored for Madagascar's Grand Sud;
  crossing a threshold of roughly 55% activates the pre-agreed Anticipatory Action Plan for
  the affected district(s). In the 2023/24 activation, a July 2023 DGM forecast of moderate
  drought for October-December gave ~1-5 months' lead time before the harvest-impact window,
  with the AA Technical Working Group confirming activation in August 2023.
data_sources: [DGM, IRI]
prearranged_funding_usd: 6500000
funding_by_source: {}
target_people: 413501
framework_doc: https://www.anticipation-hub.org/Documents/Evaluations/Anticipating_the_impact_of_drought_in_Madagascar.pdf
framework_doc_date: 2025-01
sources:
- https://www.anticipation-hub.org/Documents/Evaluations/Anticipating_the_impact_of_drought_in_Madagascar.pdf
- https://reliefweb.int/report/madagascar/anticipating-impact-drought-madagascar-key-findings-anticipatory-action-activation-grand-sud-202324
- https://www.wfp.org/news/wfp-launches-initiative-bolster-peoples-resilience-food-shocks-southern-madagascar
- https://www.anticipation-hub.org/global-overview/countries/madagascar/risk-layering-using-forecast-based-financing-in-madagascar
- https://www.preventionweb.net/resource/case-study/anticipatory-action-drought-southern-madagascar-calibrating-trigger-systems
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2023-08
  url: https://www.anticipation-hub.org/Documents/Evaluations/Anticipating_the_impact_of_drought_in_Madagascar.pdf
  note: >-
    Grand Sud 2023/24 activation for Betroka, Betioky Atsimo and Tsihombe, triggered by a
    July 2023 DGM forecast of moderate Oct-Dec drought. US$4.26M disbursed: anticipatory
    cash and drought-tolerant inputs to ~100,000 people in Betioky/Betroka (Dec-Feb) and
    ~50,000 in Tsihombe (Feb-Jun, funding confirmed later); early-warning messages reached
    ~157,000; 11 boreholes and 21 water/irrigation assets built in Betroka. Delivered with
    the Government of Madagascar, FAO, NORAD, Association Tompy, Association Mahavotse and
    ADRA. An endline evaluation (Difference-in-Differences vs a control group) found AA
    assistance improved food consumption scores ~12% and cut the reduced coping strategies
    index ~34% versus the counterfactual.
- date: 2022-10
  url: https://www.wfp.org/news/wfp-launches-initiative-bolster-peoples-resilience-food-shocks-southern-madagascar
  note: >-
    Earlier Grand Sud activation (Oct 2022-Mar 2023): over US$1.2M anticipatory finance to
    60,000+ smallholder farmers in Amboasary and Betioky. Its after-action review (shorter
    readiness phase than ideal, inconsistent targeting criteria, unclear guidance on cash
    use) directly shaped the improved 2023/24 design.
last_checked: '2026-07-19'
extra:
  hub_captions:
  - '2022: Drought (WFP) [WFP]'
  - '2024: Drought (WFP) [WFP]'
  hub_years:
  - '2022'
  - '2024'
  implementing:
  - WFP
  coordination: >-
    Not an OCHA/CERF collective framework. WFP and FAO jointly operate Madagascar's
    national drought AA mechanism with the Government of Madagascar (shared DGM/IRI
    trigger model, joint WFP-FAO after-action reviews, a common AA Technical Working
    Group), but each publishes its own AA plan and funding envelope. FAO's separate
    Madagascar drought framework (~243,000 people / ~US$2M per the Anticipation Hub
    country page) is out of scope for this WFP-specific page.
  funding_note: >-
    prearranged_funding_usd/target_people (6.5M / 413,501) are the Anticipation Hub's
    current listing for "Risk layering using Forecast-based Financing in Madagascar"
    (framework_doc's original slug); an earlier pull of the same Hub data (this page's
    prior stub) recorded 5,000,000 / 313,501 — not reconciled, treat both as
    Hub-inventory approximations of the same multi-year envelope rather than the cash
    actually disbursed in a given year. The most recent (2023/24) activation itself
    disbursed US$4.26M to ~151,000-157,000 people (see `activations`). NORAD is named as
    a funding/implementing partner for the 2023/24 activation but its share of the
    envelope is not publicly broken out, hence `funding_by_source: {}`.
  schema_strain: >-
    The framework_doc URL given in the original stub
    (anticipation-hub.org/global-overview/.../risk-layering-using-forecast-based-financing-in-madagascar)
    describes a completed 2019-2022 project phase (partners WFP, BNGRC, DGM, WHH, GIZ;
    regions Androy/Anosy/Atsimo Andrefana/Atsimo Atsinanana) rather than the currently
    active Grand Sud mechanism documented by the Jan 2025 WFP evidence report used above;
    kept as a `source` rather than `framework_doc` for that reason. Precise numeric
    trigger thresholds (beyond the ~55% composite score reported by a PreventionWeb case
    study) were not found in a fetchable primary document.
visibility: public
---

# WFP — Madagascar drought

## Summary
WFP, the Government of Madagascar (notably the General Direction of Meteorology, DGM)
and FAO have run a joint Anticipatory Action (AA) mechanism for drought in the Grand Sud
since 2020, activated in both the 2022/23 and 2023/24 seasons. The 2023/24 activation
(the most recent and best documented) covered the districts of Betroka, Betioky Atsimo
and Tsihombe, disbursing US$4.26M in anticipatory cash and drought-tolerant agricultural
inputs to roughly 151,000 people, alongside early-warning messaging and water-point
rehabilitation. A January 2025 WFP evidence report found the assistance measurably
protected food consumption and reduced negative coping strategies relative to a control
group.

## Trigger
A forecast trigger model — developed by the DGM, the International Research Institute
for Climate and Society (IRI) and WFP — combines seasonal rainfall forecasts, observed
climate indicators and vulnerability data into a district-level composite trigger score;
per a PreventionWeb case study on the system's calibration, crossing a threshold of
roughly 55% activates the pre-agreed AA plan for that district. In July 2023 the DGM
issued a forecast of moderate drought for October-December in Betroka, Betioky and
Tsihombe (coinciding with the October-March lean season); the national AA Technical
Working Group confirmed activation the following month, giving roughly 1-5 months of
lead time before the reduced-harvest impact window. Exact numeric thresholds beyond the
~55% composite score were not found in a directly fetchable primary document.

## Funding & scope
The Anticipation Hub lists the framework's (WFP-specific) multi-year envelope at
approximately US$6.5M targeting 413,501 people — figures that have shifted slightly
across Hub data pulls (see `extra.funding_note`) and should be read as an approximation
of scale rather than an exact, reconciled total. Actual disbursement in the most recent
(2023/24) activation was US$4.26M, reaching ~151,000 people with transfers and ~157,000
with early-warning messages, delivered with the Government of Madagascar, FAO, NORAD,
Association Tompy, Association Mahavotse and ADRA. A separate, FAO-run drought AA
framework in Madagascar (~243,000 people / ~US$2M) is coordinated through the same
national mechanism but is out of scope for this page — see `extra.coordination`.

## Activations
- **Aug 2023 (2023/24 Grand Sud activation)** — triggered by the July 2023 DGM drought
  forecast; US$4.26M disbursed for cash transfers, drought-tolerant inputs, early-warning
  messaging and water infrastructure (11 boreholes, 21 water/irrigation assets) across
  Betroka, Betioky Atsimo and Tsihombe. An endline evaluation found ~12% better food
  consumption scores and ~34% lower reduced-coping-strategy scores than a control group.
- **Oct 2022-Mar 2023 (2022/23 Grand Sud activation)** — over US$1.2M anticipatory
  finance to 60,000+ smallholder farmers in Amboasary and Betioky; its after-action
  review shaped several design changes carried into 2023/24 (longer readiness phase,
  consistent targeting criteria, clearer guidance on cash use).

## Sources
- **Authoritative:** [Anticipating the impact of drought in Madagascar — key findings from the Grand Sud 2023/24 activation](https://www.anticipation-hub.org/Documents/Evaluations/Anticipating_the_impact_of_drought_in_Madagascar.pdf) (WFP, Jan 2025) · [ReliefWeb mirror](https://reliefweb.int/report/madagascar/anticipating-impact-drought-madagascar-key-findings-anticipatory-action-activation-grand-sud-202324)
- [WFP launches initiative to bolster people's resilience to food shocks in Southern Madagascar](https://www.wfp.org/news/wfp-launches-initiative-bolster-peoples-resilience-food-shocks-southern-madagascar) (Oct 2022, the 2022/23 activation)
- [Anticipation Hub — Madagascar, "Risk layering using Forecast-based Financing"](https://www.anticipation-hub.org/global-overview/countries/madagascar/risk-layering-using-forecast-based-financing-in-madagascar) (2019-2022 project phase; also source of the framework-level people/funding figures)
- [Anticipatory action for drought in Southern Madagascar: calibrating trigger systems with historical impact data](https://www.preventionweb.net/resource/case-study/anticipatory-action-drought-southern-madagascar-calibrating-trigger-systems) (PreventionWeb, trigger-model detail)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory listing)
