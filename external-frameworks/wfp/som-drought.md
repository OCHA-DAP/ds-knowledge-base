---
content_type: framework-external
framework: wfp-som-drought
org: WFP
country_iso3: SOM
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  Seasonal (Gu/Deyr) rainfall forecasts of a below-average season, cross-checked against
  IPC/FSNAU food-security deterioration, trigger cash transfers delivered through Somalia's
  government-owned Baxnaano social safety net ahead of the projected dry season. No public
  document states a single quantified threshold (e.g. an exact rainfall percentile or IPC
  population share) — see `extra.schema_strain`.
data_sources: [FSNAU, IPC, FEWSNET]
prearranged_funding_usd: 8000000
funding_by_source: {}
target_people: 1300000
framework_doc: https://docs.wfp.org/api/documents/WFP-0000153419/download/
framework_doc_date: 2023-11-28
sources:
- https://docs.wfp.org/api/documents/WFP-0000153419/download/
- https://www.anticipation-hub.org/global-overview/countries/somalia
- https://www.anticipation-hub.org/experience/global-map
- https://www.wfp.org/anticipatory-actions
- https://reliefweb.int/report/somalia/wfp-somalia-country-brief-march-2022
- https://reliefweb.int/report/somalia/wfp-somalia-country-brief-april-2022
- https://reliefweb.int/report/somalia/somalia-annual-country-report-2022-country-strategic-plan-2022-2025
activations:
- date: "2022-03"
  url: https://reliefweb.int/report/somalia/wfp-somalia-country-brief-march-2022
  note: >-
    Gu-2022 drought activation — a forecast fourth consecutive failed rainy season triggered
    cash transfers (USD 120/household/quarter) plus radio early-warning messages in Xudur and
    Wajiid districts, Bakool region; ~117,000 people reported reached in the March brief,
    ~112,000 in the April brief (per WFP's monthly country briefs). By year end WFP's 2022
    Somalia annual country report describes the cumulative activation as its "largest drought
    anticipatory action intervention in Eastern Africa" to date: USD 6.7M in cash-based
    transfers (delivered via the Baxnaano safety net) reaching 201,534 people.
last_checked: '2026-07-19'
extra:
  hub_captions:
  - '2022: Drought (WFP) [WFP]'
  hub_years:
  - '2022'
  implementing:
  - WFP
  baxnaano: >-
    WFP delivers the drought AA cash transfer through Baxnaano, Somalia's government-owned,
    World Bank-financed national safety-net programme — WFP's factsheet describes
    anticipatory action as an instrument layered onto this existing delivery platform rather
    than a standalone payment system.
  coordination: >-
    Distinct from OCHA/CERF's earlier collective Somalia drought pilot (`frameworks/som-drought`,
    version 2019, retired) — that framework was designed under the Humanitarian Coordinator
    with the Federal Government of Somalia, OCHA and the World Bank, keyed off FSNAU/IPC
    food-security projections, and activated twice via CERF (June 2020, USD 15M; Feb 2021,
    USD 20M to seven UN agencies including WFP as one implementing partner among FAO, IOM,
    UNFPA, UNHCR, UNICEF and WHO), then lapsed with no located successor. This WFP page
    describes a separate, WFP-branded instrument — first publicly reported activating in
    2022, after the collective framework's last activation — funded and operated by WFP
    itself via Baxnaano, not a CERF-financed collective allocation. No source found
    describing the two as the same instrument or as formally coordinated with each other.
  schema_strain: >-
    No public document gives a single quantified drought trigger (rainfall percentile, IPC
    population-share threshold, or lead time in days) comparable to the detail available for
    WFP's Somalia FLOOD anticipatory action (which does state a forecast model and lead
    time). The WFP factsheet (framework_doc) and country briefs describe the trigger only as
    a seasonal forecast of below-average Gu/Deyr rains combined with deteriorating food
    security, without publishing the exact numeric threshold; trigger_summary reflects that
    limit. `prearranged_funding_usd`/`target_people` are taken from the Anticipation Hub
    Somalia country page's current listing for WFP's drought framework, distinct from the
    USD 6.7M actually released and 201,534 people reached in the 2022 activation.
visibility: public
---

# WFP — Somalia drought

## Summary
WFP runs its own anticipatory action (AA) programme for drought in Somalia, delivering
cash transfers ahead of a forecast poor Gu or Deyr rainy season through Baxnaano, the
government-owned, World Bank-financed national social safety net. It is separate from the
earlier OCHA/CERF collective Somalia drought pilot (2019 design, retired after activating
in 2020 and 2021 — see `frameworks/som-drought`), in which WFP participated only as one of
seven implementing UN agencies. WFP's own drought AA first activated publicly in 2022,
reaching over 200,000 people with USD 6.7 million in cash transfers — described by WFP as
its largest drought anticipatory action intervention in Eastern Africa that year. The
Anticipation Hub currently lists the programme at a USD 8,000,000 pre-arranged envelope
against a target of 1,300,000 people.

## Trigger
Plain language, per WFP's public materials: seasonal rainfall forecasts (Gu, March-May, or
Deyr, October-December) signalling a below-average or failed rainy season, cross-checked
against FSNAU/IPC food-security deterioration, trigger release of pre-arranged cash through
Baxnaano ahead of the season. No public source states a single quantified threshold (a
rainfall percentile, IPC population-share cut-off, or lead time in days) — contrast WFP's
Somalia flood AA, which does publish a named forecast model (IGAD's Geospatial Streamflow
Forecast Model). See `extra.schema_strain`.

## Funding & scope
Anticipation Hub's current country listing gives a pre-arranged envelope of USD 8,000,000
against 1,300,000 target people for WFP's Somalia drought framework. The one activation
reported in detail — 2022 — released USD 6.7 million in cash-based transfers via Baxnaano,
reaching 201,534 people by year end (initial rounds of ~112,000-117,000 people in Xudur and
Wajiid districts, Bakool region, at USD 120/household/quarter, expanded over the year).
Funding source/donor breakdown was not stated in the sources reviewed.

## Activations
- **2022 (Gu season)** — a forecast fourth consecutive failed rainy season triggered cash
  transfers plus radio early-warning messaging in Bakool region (Xudur, Wajiid); WFP's 2022
  annual country report for Somalia calls the year's cumulative activation (USD 6.7M,
  201,534 people) its largest drought AA intervention in Eastern Africa to date.
- No other WFP-branded Somalia drought AA activation was found in the sources reviewed
  (WFP's 2023-2024 Somalia AA reporting found in this research covers **flood**, not
  drought, activations — see `external-frameworks/wfp/som-flood.md` if enriched).

## Sources
- **Authoritative:** [WFP Somalia — anticipatory action and integrated climate risk, updated 28 Nov 2023](https://docs.wfp.org/api/documents/WFP-0000153419/download/) (factsheet PDF; not machine-text-extractable via available tools, see `extra.schema_strain`)
- [Anticipation Hub — Somalia country page](https://www.anticipation-hub.org/global-overview/countries/somalia) (current funding/target-people figures for the WFP drought framework)
- [WFP — Anticipatory Action for climate shocks](https://www.wfp.org/anticipatory-actions) (2022 activation narrative: forecast fourth dry season, Bakool)
- [WFP Somalia Country Brief, March 2022](https://reliefweb.int/report/somalia/wfp-somalia-country-brief-march-2022) · [April 2022](https://reliefweb.int/report/somalia/wfp-somalia-country-brief-april-2022) (activation figures, Xudur/Wajiid)
- [Somalia Annual Country Report 2022 — CSP 2022-2025](https://reliefweb.int/report/somalia/somalia-annual-country-report-2022-country-strategic-plan-2022-2025) (USD 6.7M / 201,534 people, "largest... in Eastern Africa")
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Related: [`frameworks/som-drought`](../../frameworks/som-drought) — the earlier, now-retired OCHA/CERF collective pilot in which WFP was an implementing partner (see `extra.coordination`)
