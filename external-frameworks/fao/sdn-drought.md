---
content_type: framework-external
framework: fao-sdn-drought
org: FAO
country_iso3: SDN
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  FAO's Early Warning Early Action (EWEA) system for Sudan, established in 2017, monitors
  climate, seasonal-forecast and vulnerability indicators for signs of impending drought/dry
  spells affecting agropastoralist livelihoods in Kassala, Red Sea and North Darfur states.
  When indicators point to a failing season, pre-identified early actions (livestock feed,
  animal health treatment, destocking support) are released via FAO's SFERA Early Action
  Fund. Public sources describe the monitoring approach in general terms but do not publish
  the specific numeric thresholds or lead time — see `extra.schema_strain`.
data_sources: []
prearranged_funding_usd: 1000000
funding_by_source: {}
target_people: 59000
framework_doc: https://www.fao.org/in-action/kore/publications/publications-details/en/c/1194977/
framework_doc_date: 2019-05-20
sources:
  - https://www.anticipation-hub.org/experience/global-map
  - https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/sudan
  - https://www.anticipation-hub.org/global-overview/countries/sudan
  - https://reliefweb.int/report/sudan/acting-early-mitigate-drought-sudan
  - https://reliefweb.int/report/sudan/sudan-impact-early-warning-early-action
  - https://www.preventionweb.net/publication/sudan-impact-early-warning-early-action-protecting-agropastoralist-livelihoods-ahead
  - https://www.preventionweb.net/news/acting-early-mitigate-drought-sudan
activations:
  - date: 2017-12
    url: https://reliefweb.int/report/sudan/acting-early-mitigate-drought-sudan
    note: >-
      Following a rapid assessment rolled out in October 2017 that confirmed limited pasture,
      low water supplies and a below-average sorghum harvest in Kassala, FAO drew on its
      SFERA Early Action Fund to support ~5,000 households (~30,000 livestock) in
      Hameshkoreb, Tulkouk and Aroma localities: 600 tonnes of concentrated animal feed, 30
      tonnes of mineral licks, and health treatment for ~30,000 animals. A 2019 FAO impact
      evaluation put the return at ~US$6.7 in avoided losses/added benefits per US$1 spent.
last_checked: '2026-07-21'
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
  schema_strain: >-
    (1) The Anticipation Hub's global-map framework record (used for the original stub) gives
    prearranged_funding_usd=1,000,000 / target_people=59,000, but the Hub's Sudan country
    overview page (fetched 2026-07-21) instead shows budget=US$2,000,000 / people
    targeted=118,000 for the same FAO-drought entry — almost exactly double. The two haven't
    been reconciled from public sources; the country-page figure may be a cumulative rollup
    across the 2022-2024 listing years rather than a single-year framework envelope. Recorded
    the original global-map figures here as primary. (2) No public report of an actual
    activation during the Hub's listed 2022, 2023 or 2024 years was found — the only
    documented activation is the Sept-Dec 2017 Kassala dry-spell response, which predates the
    listed years (the EWEA system itself has run continuously since 2017, so 2022-2024 likely
    reflects continued active status/funding rather than a lapse, but this is not confirmed).
    (3) No named forecast/monitoring data product (e.g. NDVI, WRSI, seasonal rainfall
    forecast) is specified for the Sudan system in sources reviewed, despite FAO's comparable
    EWEA systems elsewhere naming specific indicators — left `data_sources` empty rather than
    guessing. (4) Exact SFERA disbursement amount for the 2017 activation is not stated in
    sources found (only the in-kind/treatment quantities); `funding_by_source` left {}.
visibility: public
---

# FAO — Sudan drought

## Summary
FAO has run an Early Warning Early Action (EWEA) system for drought and dry-spell risk in
Sudan since 2017, covering agropastoralist communities dependent on rainfed farming and
small-scale herding in Kassala, Red Sea and North Darfur states. It monitors climate,
seasonality and vulnerability data and releases pre-identified early actions — chiefly
livestock feed, animal health support and destocking assistance — through FAO's SFERA Early
Action Fund ahead of confirmed drought impact. The Anticipation Hub lists it as an active
framework for 2022, 2023 and 2024, though the only publicly documented activation found dates
to late 2017.

## Trigger
The EWEA system "systematically monitor[s], through a set of indicators and thresholds, the
likely impact of drought on the livelihoods and food security situation" of target groups in
Kassala, Red Sea and North Darfur, linking climate, seasonality and vulnerability data to
specific pre-agreed early actions. Public sources describe the approach at this level of
generality; the exact numeric thresholds (e.g. rainfall deficit, vegetation index values) and
lead time are not published in the documents reviewed (see `extra.schema_strain`).

## Funding & scope
The Anticipation Hub's global-map framework record lists ~US$1,000,000 pre-arranged funding
and 59,000 target people; its Sudan country-overview page instead shows ~US$2,000,000 and
118,000 people for the same entry — the discrepancy is unresolved (see `extra.schema_strain`).
The one documented activation (2017) was funded through FAO's SFERA Early Action Fund and
reached ~5,000 households (~30,000 livestock); no breakdown of current funding by source is
available.

## Activations
- **Dec 2017 (Kassala dry spell).** An October 2017 rapid assessment found limited pasture,
  low water supplies and a below-average sorghum harvest; FAO's SFERA Early Action Fund
  financed feed, mineral licks and animal-health treatment for ~30,000 livestock in
  Hameshkoreb, Tulkouk and Aroma localities, benefiting ~5,000 households. A subsequent FAO
  impact evaluation (2019) estimated a return of ~US$6.7 per US$1 spent in avoided losses and
  added benefits.

No activation during the Hub's listed 2022-2024 years was found in the public sources
reviewed; whether the framework was triggered in those years, or is simply recorded as
actively funded/available, is not stated.

## Sources
- **Authoritative:** [The Sudan: Impact of Early Warning Early Action — Protecting agropastoralist livelihoods ahead of drought](https://www.fao.org/in-action/kore/publications/publications-details/en/c/1194977/) (FAO/KORE, 20 May 2019; also mirrored on [PreventionWeb](https://www.preventionweb.net/publication/sudan-impact-early-warning-early-action-protecting-agropastoralist-livelihoods-ahead) and [ReliefWeb](https://reliefweb.int/report/sudan/sudan-impact-early-warning-early-action))
- [Acting early to mitigate drought in Sudan](https://reliefweb.int/report/sudan/acting-early-mitigate-drought-sudan) (FAO story, via ReliefWeb, 9 Jul 2019; also on [PreventionWeb](https://www.preventionweb.net/news/acting-early-mitigate-drought-sudan)) — source of the 2017 activation detail
- [Anticipatory action in Sudan](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/sudan) (Anticipation Hub country page)
- [Anticipatory action in Sudan — global overview](https://www.anticipation-hub.org/global-overview/countries/sudan) (Anticipation Hub; budget/target-people figures that disagree with the global-map record — see `extra.schema_strain`)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record; source of the frontmatter funding/target-people figures used here)
