---
content_type: framework-external
framework: wfp-zwe-drought
org: WFP
country_iso3: ZWE
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  District-level seasonal drought forecast: rainfall anomaly measured by the Standardized
  Precipitation Index (SPI), derived from ECMWF's 7-month seasonal rainfall ensemble
  forecast, classified into mild/moderate/severe drought categories for the Oct-Jan rainy
  season, with forecast skill/lead time reported at 1-6 months. First piloted in Mudzi
  district (activated at the "moderate" threshold for the Nov 2021-Jan 2022 season); since
  expanded to Mbire, Binga and Matobo districts, with further expansion planned.
data_sources: [SPI, ECMWF]
prearranged_funding_usd: 12000000
funding_by_source: {}
target_people: 1804060
framework_doc: https://www.wfp.org/publications/system-anticipate-and-address-impacts-drought-zimbabwe
framework_doc_date: 2022-09-16
sources:
  - https://www.wfp.org/publications/system-anticipate-and-address-impacts-drought-zimbabwe
  - https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/zimbabwe
  - https://www.wfp.org/publications/2023-building-systems-anticipate-drought-southern-africa
  - https://www.wfp.org/anticipatory-actions
  - https://www.wfp.org/stories/el-nino-intensifies-floods-and-droughts-early-action-pays
  - https://www.wfp.org/news/wfp-races-cushion-people-looming-drought-southern-africa-largest-cash-payout-date
  - https://nhess.copernicus.org/articles/24/4661/2024/
  - https://www.fao.org/newsroom/detail/bracing-for-el-ni%C3%B1o--fao-and-wfp-launch-joint-appeal-to-protect-8.8-million-people-from-extreme-weather-events/en
  - https://www.unocha.org/publications/report/zimbabwe/zimbabwe-el-nino-anticipatory-action-plan-oct-2023-mar-2024-issued-november-2023
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2021-09
    url: https://www.wfp.org/anticipatory-actions
    note: >-
      First WFP AA activation in Southern Africa. District-level forecast showed the
      "moderate" drought trigger reached for the Nov 2021-Jan 2022 rainy season in Mudzi
      district; over US$360,000 released for ~32,500 people, mainly solar-powered
      borehole installation to secure water access ahead of the forecast drought.
  - date: 2023-07
    url: https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/zimbabwe
    note: >-
      Activation ahead of the 2023/2024 El Niño-induced drought (part of a joint
      Southern Africa activation with Mozambique, Lesotho and Madagascar reaching
      ~1.2 million people with early-warning messages and ~US$14M in pre-arranged
      financing region-wide). Zimbabwe-specific figures per the Anticipation Hub:
      ~US$5,000,000 disbursed reaching ~75,000 people; interventions included
      drought-tolerant seed distribution and borehole drilling (Binga district) plus
      last-mile early-warning messaging.
last_checked: '2026-07-19'
extra:
  hub_captions:
  - '2022: Drought (WFP) [WFP]'
  - '2023: Drought (WFP) [WFP]'
  - '2024: Drought (WFP) [WFP]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - WFP
  coordination: >-
    Distinct from a separate OCHA-coordinated inter-agency framework: per FAO reporting,
    OCHA worked with FAO, WFP, UNICEF and government counterparts to build "the first
    inter-agency El Niño CERF anticipatory action framework" for Zimbabwe (and Madagascar),
    published as "Zimbabwe: El Niño Anticipatory Action Plan, Oct 2023-Mar 2024" (issued
    Nov 2023; ~505,600 people targeted, ~US$28.7M requirement, 21 districts, per search
    results — full document could not be fetched, ReliefWeb/OCHA both returned HTTP 403 to
    automated fetches). This KB has no `frameworks/zwe-drought/` page for that collective
    plan yet (gap — not created here since this page's scope is WFP's own framework only).
    WFP's SPI/ECMWF drought AA system described on this page predates that CERF plan
    (piloted from 2019, first activated 2021) and has its own budget/targets separate from
    it; WFP's 2023 activation coincided with and fed into the same El Niño response window
    but is reported by WFP/the Hub under its own figures, not the CERF plan's.
  schema_strain: >-
    Figures are inconsistent across sources/time and could not be fully reconciled from
    public sources: this page previously (stub, checked 2026-07-10) carried
    prearranged_funding_usd: 5,000,000 and target_people: 902,030, apparently pulled from
    a specific year's Hub global-map API record. On 2026-07-19 the Hub's Zimbabwe country
    page instead showed a current framework card of target 1,804,060 people / $12,000,000
    budget, plus a *separate* "2023 activation" record of 75,000 people / $5,000,000 (used
    above under activations). No single authoritative WFP document giving one consistent
    framework-wide budget/target figure was found; the $12M/1.8M figures (used in the
    frontmatter) are the freshest available but may themselves be a point-in-time Hub
    snapshot rather than a fixed programme ceiling. Funding source breakdown (e.g.
    NORAD/DANIDA, cited as funders of the original FbF pilot) not confirmed against a
    current breakdown, so `funding_by_source` is left empty. No formal EAP/protocol PDF
    (in the IFRC sense) was found; `framework_doc` points to WFP's most authoritative
    public overview publication instead.
visibility: public
---

# WFP — Zimbabwe drought

## Summary
WFP's forecast-based/anticipatory action (AA) system for drought in Zimbabwe, developed
with the Meteorological Services Department, the Climate Change Management Department and
district-level Technical Working Groups since 2019. It triggers on a seasonal rainfall
forecast (SPI derived from the ECMWF 7-month ensemble) classified into mild/moderate/severe
drought categories, releasing cash and water/livelihood support ahead of the Oct-Jan rainy
season. Piloted in Mudzi district (first activated 2021), it has since expanded to Mbire,
Binga and Matobo, and was a component of WFP's wider 2023/2024 Southern Africa El Niño
anticipatory action response.

## Trigger
Drought risk is monitored through the Standardized Precipitation Index (SPI), computed
from ECMWF's 7-month seasonal rainfall ensemble forecast, at district level for the
Oct-Jan/Nov-Jan rainy season. Forecasts are classified into mild, moderate and severe
drought categories, with reported forecast skill/lead time of roughly 1 to 6 months ahead
of the season. The system was first piloted in Mudzi district; the September 2021
activation was triggered when the district-level forecast reached the "moderate" drought
threshold for the Nov 2021-Jan 2022 rainy season. Coverage has since expanded to Mbire,
Binga and Matobo districts, with further district expansion planned. Exact numeric SPI
thresholds per severity category, and the current full list of covered districts, are not
stated in the public sources found (see `extra.schema_strain`).

## Funding & scope
Reported current framework scope (Anticipation Hub, checked 2026-07-19): ~US$12,000,000
budget, targeting ~1,804,060 people. Funding source breakdown is not confirmed publicly;
the original forecast-based-financing pilot (from 2019) is reported elsewhere as having
been supported by NORAD and DANIDA. See `extra.schema_strain` for why these figures don't
fully reconcile with an earlier Hub snapshot of this page.

## Activations
- **September 2021 — Mudzi district (first AA activation in Southern Africa).**
  District-level forecast reached the "moderate" drought trigger for the Nov 2021-Jan
  2022 rainy season; over US$360,000 released for ~32,500 people, mainly solar-powered
  borehole installation for water access.
- **From July 2023 — 2023/2024 El Niño-induced drought.** Activated jointly with
  Mozambique, Lesotho and Madagascar — WFP's largest AA activation in Southern Africa to
  date, reaching ~1.2 million people region-wide with early-warning messages and
  disbursing ~US$14 million in pre-arranged financing. Zimbabwe-specific figures per the
  Anticipation Hub: ~US$5,000,000 disbursed, ~75,000 people reached, with
  drought-tolerant seed distribution and borehole drilling (Binga district) alongside
  last-mile early-warning messaging.

No non-activation (trigger-not-met) events were found in public reporting for the years
covered by the Hub listing (2022-2024).

## Sources
- **Authoritative overview:** [A System to Anticipate and Address the Impacts of Drought in Zimbabwe (WFP, 16 Sept 2022)](https://www.wfp.org/publications/system-anticipate-and-address-impacts-drought-zimbabwe)
- [2023 - Building Systems to Anticipate Drought in Southern Africa (WFP, incl. Zimbabwe case study)](https://www.wfp.org/publications/2023-building-systems-anticipate-drought-southern-africa)
- [Anticipatory Action for climate shocks (WFP programme page — Mudzi 2021 activation detail)](https://www.wfp.org/anticipatory-actions)
- [Anticipation Hub — Anticipatory actions in Zimbabwe (framework/activation figures, fetched 2026-07-19)](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/zimbabwe)
- [As El Niño intensifies floods and droughts, early action pays off (WFP)](https://www.wfp.org/stories/el-nino-intensifies-floods-and-droughts-early-action-pays)
- [WFP races to cushion people from looming drought in Southern Africa in largest cash payout to date](https://www.wfp.org/news/wfp-races-cushion-people-looming-drought-southern-africa-largest-cash-payout-date)
- [NHESS — Ready, Set & Go! An anticipatory action system against droughts (technical/methodology background, Mozambique-focused, references shared Zimbabwe methodology)](https://nhess.copernicus.org/articles/24/4661/2024/)
- [FAO — Bracing for El Niño: FAO and WFP launch joint appeal (context on the separate OCHA/CERF inter-agency plan)](https://www.fao.org/newsroom/detail/bracing-for-el-ni%C3%B1o--fao-and-wfp-launch-joint-appeal-to-protect-8.8-million-people-from-extreme-weather-events/en)
- [Zimbabwe: El Niño Anticipatory Action Plan, Oct 2023-Mar 2024 (OCHA, issued Nov 2023) — the separate inter-agency CERF plan, see `extra.coordination`; page returned HTTP 403 to automated fetch, details via search snippets only](https://www.unocha.org/publications/report/zimbabwe/zimbabwe-el-nino-anticipatory-action-plan-oct-2023-mar-2024-issued-november-2023)
- [Anticipation Hub global map (original inventory record)](https://www.anticipation-hub.org/experience/global-map)
