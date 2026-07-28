---
content_type: framework-external
framework: start-network-mdg-drought
org: START
country_iso3: MDG
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  Welthungerhilfe's forecast-based drought model computes a Water Requirement Satisfaction
  Index (WRSI) for upland rice/agricultural drought from satellite rainfall, crop/planting-
  calendar and soil datasets, calibrated to flag events with roughly a 10-year average
  return period; when a covered district crosses the model's threshold, pre-agreed early
  actions (early cash, in-kind assistance, awareness-raising) release from the Start Finance
  Facility. Lead time and the precise numeric threshold are not published in a fetchable
  source (see `extra.schema_strain`). It is unconfirmed whether the same WRSI trigger, or a
  different Start Fund/Start Ready mechanism, governs the 2023/2024 activations the
  Anticipation Hub lists for this framework.
data_sources: [WRSI, DGM]
prearranged_funding_usd: 3045120
funding_by_source: {}
target_people: 70000
framework_doc: https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/madagascar/development-of-forecast-based-action-mechanism-addressing-drought-induced-food-insecurity-in-madagascar
framework_doc_date: 2021
sources:
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/madagascar/development-of-forecast-based-action-mechanism-addressing-drought-induced-food-insecurity-in-madagascar
- https://www.welthungerhilfe.org/news/publications/detail/drought-risk-financing-in-madagascar-model-threshold-rationale/
- https://www.anticipation-hub.org/news/forecast-based-action-intervention-early-cash-distribution-to-address-food-insecurity-in-the-north-east-of-madagascar
- https://www.anticipation-hub.org/global-overview/countries/madagascar
- https://reliefweb.int/report/madagascar/start-ready-madagascar-activations
- https://startnetwork.org/funds/disaster-risk-financing-support/forewarn/forewarn-madagascar
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2021-01
  url: https://www.anticipation-hub.org/news/forecast-based-action-intervention-early-cash-distribution-to-address-food-insecurity-in-the-north-east-of-madagascar
  note: >-
    The mechanism's only confirmed activation to date. WHH's WRSI model triggered for
    Ambatondrazaka district (Alaotra-Mangoro) during the upland-rice growing phase; EUR
    196,000 released from the Start Finance Facility; WHH delivered unconditional cash of
    US$10/household/month for 6 months to 1,500 households (~7,500 people).
- date: 2024-02
  url: https://reliefweb.int/report/madagascar/start-ready-madagascar-activations
  note: >-
    Start Ready (Start Network's separate multi-hazard pre-arranged financing pool, 2nd
    Risk Pool, May 2023-Apr 2024, 7 countries) activated for drought in Madagascar; Cyclone
    Gamane triggered a further Start Ready activation the following month. Disbursement/
    beneficiary figures for this specific drought activation were not available from a
    fetchable primary source (ReliefWeb and Start Network pages returned HTTP 403 to
    automated fetch); its relationship to the WRSI trigger above is unconfirmed.
last_checked: '2026-07-24'
extra:
  hub_captions:
  - '2023: Drought (Start Network) [Catholic Relief Services] [Welthungerhilfe]'
  - '2024: Drought (Start Network) [CARE International] [Catholic Relief Services] [Humanity
    & Inclusion] [Save the Children] [Action Against Hunger]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Welthungerhilfe
  - Catholic Relief Services
  - CARE International
  - Humanity & Inclusion
  - Save the Children
  - Action Against Hunger
  coordination: >-
    Not a component of an OCHA/CERF collective framework (no OCHA mdg-drought page exists
    under frameworks/). Operates alongside, but independently of, two other Madagascar
    drought AA mechanisms: WFP/Government of Madagascar (DGM)/FAO's Grand Sud composite-
    trigger plan (external-frameworks/wfp/mdg-drought.md) and a separate FAO-run drought
    framework (~243,000 people / ~US$2M per the Anticipation Hub country page). Start
    Network member organisations (Save the Children, Welthungerhilfe, World Vision)
    supported WFP's own September 2023 Southern Africa El Nino drought activation as
    implementing partners of WFP's framework, not of this one.
  funding_note: >-
    prearranged_funding_usd/target_people (3,045,120 / 70,000) are the Anticipation Hub
    Madagascar country page's current listing for "Start Network Drought Framework" (a
    portfolio-level aggregate; no dated breakdown by year or donor found). This differs
    both from the prior stub's Hub pull (2,298,851 / 24,000) and from the fully-documented
    2020-2022 Welthungerhilfe project at `framework_doc`, which targeted 365,449 people
    across 6 districts (Boeny: Mahajanga II, Marovoay; Atsimo-Atsinanana: Farafangana,
    Vangaindrano; Alaotra-Mangoro: Amparafaravola, Ambatondrazaka) funded by Germany's
    Federal Foreign Office (GFFO) via the Start Finance Facility. None of these figures are
    reconciled; treat all as Hub-inventory approximations of an evolving multi-year
    envelope, not a single audited total.
  schema_strain: >-
    Lead time and the exact WRSI numeric threshold are described only qualitatively in
    public sources (a "~10-year average return period"; full parameters are in a
    Welthungerhilfe "Model Threshold Rationale 2021" technical document not independently
    fetchable here). The Hub's 2023 caption (CRS, Welthungerhilfe) could not be tied to a
    specific dated, sourced activation distinct from WFP's Sept 2023 Southern Africa
    activation (see `extra.coordination`) — recorded as an unconfirmed activation year
    rather than guessed into `activations`. ReliefWeb and startnetwork.org pages describing
    the 2024 Start ready drought activation returned HTTP 403 to automated fetch, so
    numeric details for that activation are also missing.
visibility: public
---

# START — Madagascar drought

## Summary
Welthungerhilfe (WHH), with Start Network and Madagascar's disaster-management authority
(BNGRC) and meteorological service (DGM), built a forecast-based drought mechanism for
Madagascar, operational since 2019/2020 and funded by Germany's Federal Foreign Office
(GFFO) via the Start Finance Facility. The 2020-2022 project phase targeted 365,449 people
in 6 districts and triggered once, in January-February 2021, releasing EUR 196,000 for
cash assistance in Ambatondrazaka. The Anticipation Hub's current country listing carries
a broader, ongoing "Start Network Drought Framework" (70,000 people / ~US$3.05M) with
different Start Network member organisations implementing in different years — Catholic
Relief Services and Welthungerhilfe in 2023; CARE International, Catholic Relief Services,
Humanity & Inclusion, Save the Children and Action Against Hunger in 2024 — consistent with
Start Network's Start Fund/Start Ready model of rotating "EAP custodian" member NGOs rather
than one fixed operator. Start Ready (a separate Start Network pre-arranged financing pool)
also activated for Madagascar drought in February 2024.

## Trigger
The documented mechanism (WHH's forecast-based action project) computes a Water
Requirement Satisfaction Index (WRSI) — an agricultural-drought indicator built from
satellite-based rainfall data, crop and planting-calendar information, and soil datasets —
to detect drought events with roughly a 10-year average return period. When a covered
district's WRSI crosses the model's threshold, pre-agreed early actions (early cash,
in-kind assistance, awareness-raising) release, with the specific action depending on the
timing of the trigger and severity reached. Numeric threshold values and lead time are laid
out in a 2021 Welthungerhilfe/Start Network technical document ("Model Threshold
Rationale") that was not independently fetchable for this page. It is not confirmed
whether this same WRSI model, or a different trigger under Start Network's separate Start
Ready pool, governs the 2023 and 2024 activation years the Anticipation Hub lists for this
framework — see `extra.schema_strain`.

## Funding & scope
The 2020-2022 WHH project (this page's `framework_doc`) covered 365,449 people across 6
districts in 3 regions — Boeny (Mahajanga II, Marovoay), Atsimo-Atsinanana (Farafangana,
Vangaindrano) and Alaotra-Mangoro (Amparafaravola, Ambatondrazaka) — funded by Germany's
GFFO through the Start Finance Facility. The Anticipation Hub's current country-page
listing for the ongoing "Start Network Drought Framework" gives a broader envelope of
roughly US$3.05M targeting 70,000 people; the two figures are not reconciled (see
`extra.funding_note`), and no per-donor or per-year funding breakdown was found. A separate
Start Ready risk-financing pool (2nd Risk Pool, 7 countries, May 2023-April 2024) provides
additional pre-arranged, multi-hazard financing that also covers Madagascar drought.

## Activations
- **January-February 2021 (Ambatondrazaka)** — the mechanism's only confirmed activation.
  WHH's WRSI model detected agricultural drought in the upland-rice growing phase; EUR
  196,000 released from the Start Finance Facility; WHH delivered unconditional cash of
  US$10/household/month for 6 months to 1,500 households (~7,500 people).
- **February 2024** — Start Ready, Start Network's separate pre-arranged multi-hazard
  financing pool, activated for drought in Madagascar (followed by a Cyclone Gamane
  activation in March 2024). Disbursement and beneficiary figures were not available from
  a fetchable primary source.
- The Hub's 2023 caption (Catholic Relief Services, Welthungerhilfe) could not be tied to
  a specific, independently-sourced Start Network drought activation distinct from Start
  Network members' support role in WFP's own September 2023 Southern Africa El Nino
  activation — see `extra.coordination`. Not recorded as a dated activation here for lack
  of a distinct primary source.

## Sources
- **Authoritative:** [Development of Forecast-based Action mechanism addressing drought induced food insecurity in Madagascar](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/madagascar/development-of-forecast-based-action-mechanism-addressing-drought-induced-food-insecurity-in-madagascar) (Anticipation Hub project page)
- [Drought Risk Financing in Madagascar: Model Threshold Rationale](https://www.welthungerhilfe.org/news/publications/detail/drought-risk-financing-in-madagascar-model-threshold-rationale/) (Welthungerhilfe/Start Network, 2021 concept paper; full technical thresholds not independently fetchable)
- [Forecast-based Action Intervention: Early Cash Distribution to address Food Insecurity in the North-East of Madagascar](https://www.anticipation-hub.org/news/forecast-based-action-intervention-early-cash-distribution-to-address-food-insecurity-in-the-north-east-of-madagascar) (Anticipation Hub, 16 June 2021 — the 2021 activation)
- [Anticipatory action in Madagascar — country page](https://www.anticipation-hub.org/global-overview/countries/madagascar) (Anticipation Hub; current "Start Network Drought Framework" figures)
- [Start Ready: Madagascar Activations](https://reliefweb.int/report/madagascar/start-ready-madagascar-activations) (ReliefWeb; Feb 2024 drought + Mar 2024 Cyclone Gamane activations — body text not independently fetchable, HTTP 403)
- [FOREWARN Madagascar](https://startnetwork.org/funds/disaster-risk-financing-support/forewarn/forewarn-madagascar) (Start Network; multi-hazard national coordination structure, not independently fetchable, HTTP 403)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory listing)
