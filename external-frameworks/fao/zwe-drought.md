---
content_type: framework-external
framework: fao-zwe-drought
org: FAO
country_iso3: ZWE
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  FAO's own Zimbabwe drought anticipatory action work runs on the same national
  early-warning architecture (Meteorological Services Department seasonal/dry-spell
  forecasts, disseminated via the Climate Change Management Department and district-level
  Technical Working Groups, plus local-language community radio) that underlies Zimbabwe's
  wider AA system, but triggers FAO's own agriculture/livestock early actions (drought-
  tolerant seed and input distribution, fertilizer-timing advisories, livestock feed and
  vaccination support) rather than WFP's separate cash/water response (see
  external-frameworks/wfp/zwe-drought.md). No public source found states a specific
  numeric indicator, threshold or lead time for FAO's own protocol — see
  `extra.schema_strain`.
data_sources: [MSD]
prearranged_funding_usd: 500000
funding_by_source: {}
target_people: 34000
framework_doc: null
framework_doc_date: null
sources:
  - https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/zimbabwe
  - https://www.anticipation-hub.org/experience/global-map
  - https://www.fao.org/newsroom/detail/threat-of-el-nino-looms-fao-prepares-anticipatory-actions-with-members-and-partners/en
  - https://reliefweb.int/report/madagascar/scaling-anticipatory-action-zimbabwe-madagascar-and-malawi
  - https://www.preventionweb.net/collections/using-el-nino-impact-analysis-inform-policy-early-action-and-risk-informed-planning-0
  - https://www.fao.org/africa/news-stories/news-detail/zimbabwe-makes-strides-in-el-nino-response-and-recovery/en
  - https://www.fao.org/africa/news-stories/news-detail/fao-and-partners-enhance-zimbabwe-s-resilience-through-eu-funded-anticipatory-action-project/en
  - https://www.fao.org/africa/news-stories/news-detail/zimbabwe-farmers-thrive-through-climate-smart-anticipatory-action-project/en
  - https://reliefweb.int/report/world/el-nino-2023-2024-evidence-faos-anticipatory-action-interventions
activations:
  - date: '2022-02'
    url: https://reliefweb.int/report/madagascar/scaling-anticipatory-action-zimbabwe-madagascar-and-malawi
    note: >-
      Dry-spell early warning issued in two (unnamed) FAO pilot districts ahead of the
      Jan-Feb 2022 drought episode: FAO used local-language community radio to advise
      farmers against applying fertilizer ahead of the predicted dry spell, part of the
      broader early-warning-to-early-action chain FAO was scaling up in Zimbabwe,
      Madagascar and Malawi at the time.
  - date: '2023-10'
    url: https://www.fao.org/africa/news-stories/news-detail/zimbabwe-makes-strides-in-el-nino-response-and-recovery/en
    note: >-
      FAO's established Zimbabwe drought trigger mechanisms/protocols underpinned the
      first inter-agency El Niño CERF anticipatory action framework OCHA built with FAO,
      WFP, UNICEF and government counterparts for the Oct 2023-Mar 2024 El Niño season
      (`extra.coordination`). FAO reports securing USD 2.6 million through CERF — combined
      across Zimbabwe AND Madagascar, exact Zimbabwe-only share not published — to protect
      agricultural livelihoods in highly exposed/vulnerable districts, implemented as the
      "Mitigating the Impact of El Niño-induced Drought" (MIEND) project: survival stock
      feed access, improved livestock water access, and community drought-mitigation
      awareness. A July 2024 FAO field mission covered Bikita district (Masvingo province).
last_checked: '2026-07-22'
extra:
  hub_captions:
  - '2022: Drought (FAO) [FAO]'
  - '2023: Drought (FAO) [FAO]'
  - '2024: Drought (FAO) [FAO]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - FAO
  echo_project_2023_2025: >-
    Separate from FAO's own standing drought AA framework above: a 2023-2025 EU
    (ECHO)-funded joint project, "Building capacity in Southern Africa to enable effective
    disaster risk management through regional systems for inter-agency anticipatory action
    using a multi-hazard, multi-sectoral approach", run by FAO, WFP and IFRC with the
    Government of Zimbabwe. It built institutional AA systems (a National Anticipatory
    Action Roadmap, an AA Community of Practice, impact-based forecasting triggers, flood
    simulation/SIMEX exercises) in Chiredzi, Tsholotsho, Matobo and Beitbridge districts,
    prioritizing elderly, disabled, child-headed and chronically ill households, and
    supported livestock keepers through the 2023/24 drought (e.g. Beitbridge, where 435
    cattle died region-wide). No separate budget/target-people figures for this project
    were found distinct from the Hub's standing FAO drought-framework figures above.
  coordination: >-
    FAO's Oct 2023-Mar 2024 CERF-funded activation (see `activations`) was FAO's component
    of a separate OCHA-coordinated collective framework — "Zimbabwe: El Niño Anticipatory
    Action Plan, Oct 2023-Mar 2024" (issued Nov 2023) — not an independent FAO plan for
    that season. This KB has no `frameworks/zwe-drought/` page for that collective plan
    (same gap already flagged on external-frameworks/wfp/zwe-drought.md and
    external-frameworks/ifrc/zwe-drought.md — ReliefWeb/OCHA both return HTTP 403 to
    automated fetches of the plan itself, so detail here is via search-snippet citations
    only). FAO's standing drought AA framework (the `trigger_summary`/`prearranged_funding_usd`/
    `target_people` above) predates and is broader than that one CERF season, and is
    reported separately by the Hub from WFP's own SPI/ECMWF-based Zimbabwe drought
    framework (external-frameworks/wfp/zwe-drought.md) and IFRC/ZRCS's EAP
    (external-frameworks/ifrc/zwe-drought.md) — three distinct, non-identical frameworks
    for the same country+hazard.
  schema_strain: >-
    (1) No single citable FAO-authored protocol/EAP document with a specific indicator,
    numeric threshold or lead time was found; the closest public description is
    process-level (early-warning dissemination, fertilizer-timing/input-distribution
    advisories), so `framework_doc` is left null and `data_sources` kept to the general
    met-authority tag [MSD] rather than a named index. (2) The two pilot districts named in
    the Feb 2022 activation are not identified in the source found. (3) The USD 2.6 million
    CERF figure covers Zimbabwe AND Madagascar combined — no Zimbabwe-only breakdown was
    located, so it is reported in `activations` narrative only, not folded into
    `prearranged_funding_usd`/`funding_by_source` (which retain the Hub's per-country
    $500,000/34,000 standing-framework figures, unchanged from the prior stub and
    consistent across the 2023 and 2024 Hub inventory records). (4) `funding_by_source` is
    left {} — no source itemizes the $500,000 figure against a specific funding instrument
    (e.g. FAO SFERA vs. a bilateral donor).
visibility: public
---

# FAO — Zimbabwe drought

## Summary
FAO runs its own drought anticipatory action framework in Zimbabwe — one of the earliest
in FAO's global AA portfolio (alongside Burkina Faso, Chad, Niger, southern Madagascar,
Malawi, the Philippines, Pakistan and Central America) — listed active on the Anticipation
Hub across 2022-2024 with a ~US$500,000 envelope targeting ~34,000 people. It shares
Zimbabwe's national early-warning infrastructure (Meteorological Services Department,
Climate Change Management Department, district Technical Working Groups) with WFP's
separate SPI/ECMWF-based drought framework and the Zimbabwe Red Cross Society's EAP, but
delivers its own agriculture- and livestock-focused early actions. In Oct 2023-Mar 2024,
FAO's established triggers underpinned Zimbabwe's first inter-agency El Niño CERF
anticipatory action framework (built with OCHA, WFP, UNICEF and government), through which
FAO (with Madagascar) secured USD 2.6 million.

## Trigger
Public sources describe FAO's Zimbabwe drought AA trigger only at the process level: MSD
seasonal and dry-spell forecasts are disseminated through the Climate Change Management
Department, district Technical Working Groups and local-language community radio, cueing
FAO's own early actions — advisories on delaying fertilizer application, drought-tolerant
seed and input distribution, and livestock feed/vaccination support — ahead of a forecast
dry spell or drought season. No source found states a specific indicator, numeric
threshold (e.g. an SPI value) or lead time for FAO's own protocol, unlike WFP's SPI-based
Zimbabwe system or IFRC's EAP (see `extra.schema_strain`).

## Funding & scope
The Anticipation Hub lists FAO's Zimbabwe drought framework as active with a ~US$500,000
budget targeting ~34,000 people (consistent across the 2023 and 2024 inventory records).
Funding-source breakdown is not published. Separately, FAO's Oct 2023-Mar 2024 CERF-funded
activation (part of the inter-agency El Niño plan, not this standing framework figure)
secured USD 2.6 million combined for Zimbabwe and Madagascar; and a distinct 2023-2025
EU(ECHO)-funded institutional-strengthening project ran alongside WFP and IFRC in
Chiredzi, Tsholotsho, Matobo and Beitbridge districts (see `extra.echo_project_2023_2025`).

## Activations
- **February 2022** — dry-spell early warning in two (unnamed) FAO pilot districts ahead
  of the Jan-Feb 2022 drought: farmers advised via community radio to delay fertilizer
  application, part of FAO's early-warning-to-early-action chain being scaled up across
  Zimbabwe, Madagascar and Malawi.
- **October 2023 - March 2024** — FAO's trigger mechanisms underpinned its component of
  the OCHA-coordinated inter-agency El Niño CERF anticipatory action framework; FAO
  reports securing USD 2.6 million (Zimbabwe + Madagascar combined) implemented as the
  MIEND project (livestock stock feed, water access, community awareness); field mission
  to Bikita district (Masvingo), July 2024.
- A further 2023-2025 EU-ECHO joint project (FAO/WFP/IFRC/Government) built AA
  institutional systems in four districts but is not itself a dated trigger activation
  (`extra.echo_project_2023_2025`).

## Sources
- **Best available (no single FAO protocol document found — see `extra.schema_strain`):**
  [Anticipation Hub — Zimbabwe country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/zimbabwe) (framework figures)
- [FAO newsroom — "Threat of El Niño looms, FAO prepares anticipatory actions with Members and partners"](https://www.fao.org/newsroom/detail/threat-of-el-nino-looms-fao-prepares-anticipatory-actions-with-members-and-partners/en) (Zimbabwe listed among FAO's drought-protocol countries)
- [ReliefWeb — "Scaling up anticipatory action in Zimbabwe, Madagascar and Malawi"](https://reliefweb.int/report/madagascar/scaling-anticipatory-action-zimbabwe-madagascar-and-malawi) (2023-02-21; trigger process detail, Feb 2022 activation)
- [PreventionWeb — "Using El Niño Impact Analysis to Inform Policy, Early Action and Risk-Informed Planning in Southern Africa"](https://www.preventionweb.net/collections/using-el-nino-impact-analysis-inform-policy-early-action-and-risk-informed-planning-0) (USD 2.6M CERF figure, inter-agency framework detail)
- [FAO Africa — "Zimbabwe makes strides in El Nino response and recovery"](https://www.fao.org/africa/news-stories/news-detail/zimbabwe-makes-strides-in-el-nino-response-and-recovery/en) (MIEND project, Bikita field mission)
- [FAO Africa — "FAO and Partners enhance Zimbabwe's resilience through EU-Funded Anticipatory Action project"](https://www.fao.org/africa/news-stories/news-detail/fao-and-partners-enhance-zimbabwe-s-resilience-through-eu-funded-anticipatory-action-project/en) (2023-2025 ECHO project, districts)
- [FAO Africa — "Zimbabwe farmers thrive through climate-smart anticipatory action project"](https://www.fao.org/africa/news-stories/news-detail/zimbabwe-farmers-thrive-through-climate-smart-anticipatory-action-project/en) (full ECHO project name, farmer case studies)
- [ReliefWeb — "El Niño 2023-2024: Evidence from FAO's anticipatory action interventions"](https://reliefweb.int/report/world/el-nino-2023-2024-evidence-faos-anticipatory-action-interventions) (broader FAO AA evidence synthesis, 24 countries)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Cross-reference: [external-frameworks/wfp/zwe-drought.md](../wfp/zwe-drought.md) and [external-frameworks/ifrc/zwe-drought.md](../ifrc/zwe-drought.md) — sibling Zimbabwe drought frameworks; none of the three is the OCHA/CERF collective plan (`extra.coordination`)
