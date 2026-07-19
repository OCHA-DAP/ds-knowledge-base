---
content_type: framework-external
framework: wfp-eth-drought
org: WFP
country_iso3: ETH
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  A Forecast-based Financing (FbF) system built with the Ethiopian Meteorological Institute
  (EMI) and Columbia University's International Research Institute for Climate and Society
  (IRI) — the "EMI/IRI Maproom" — monitors woreda-level seasonal rainfall forecasts for the
  Belg (MAM) and Deyr/Kiremt (OND) seasons across Somali, Oromia and SNNP regions. When
  forecasts point to a high chance of a failed rainy season in a woreda, WFP and the Somali
  Region Disaster Risk Management Bureau (DRMB) activate weeks ahead of the season; exact
  public probability/threshold values per woreda are not stated in the sources reviewed —
  see `extra.schema_strain`.
data_sources: []
prearranged_funding_usd: 6622242
funding_by_source: {}
target_people: 1670326
framework_doc: https://www.anticipation-hub.org/Documents/Framework_documents/WFP-Ethiopia-Drought-0000162909.pdf
framework_doc_date: 2024-09
sources:
  - https://www.anticipation-hub.org/download/file-5020
  - https://www.anticipation-hub.org/experience/global-map
  - https://www.wfp.org/publications/anticipatory-cash-transfers-and-early-warning-information-ahead-drought-ethiopia
  - https://www.wfp.org/publications/anticipatory-action-ethiopia-drought-activation-somali-region
  - https://www.wfp.org/publications/lessons-learnt-anticipatory-action-2022-activation-somali-region-ethiopia
  - https://ethiopia.un.org/en/294164-ethiopia%E2%80%99s-drought-prone-regions-early-action-saving-lives-and-building-resilient-future
  - https://fist.iri.columbia.edu/publications/docs/ethiopia_aa_index/
activations:
  - date: 2021-03
    url: https://www.wfp.org/publications/anticipatory-cash-transfers-and-early-warning-information-ahead-drought-ethiopia
    note: >-
      Ahead of a forecast-failed Belg/Gu (Mar-May) rainy season: anticipatory cash and
      early-warning messages to 14,600+ people in Somali region; 95% of assisted people
      reported using the warning to make protective decisions.
  - date: 2022-10
    url: https://www.wfp.org/publications/anticipatory-action-ethiopia-drought-activation-somali-region
    note: >-
      Ahead of a forecast-failed Deyr (Oct-Dec) rainy season: cash transfers, early-warning
      messaging, and rangeland enclosure/fodder production in Somali region (documented in a
      lessons-learnt report published March 2024).
  - date: 2024-09
    url: https://www.anticipation-hub.org/Documents/Framework_documents/WFP-Ethiopia-Drought-0000162909.pdf
    note: >-
      La Niña-driven OND drought forecast for Oct-Dec 2024: triggered across 15 Somali-region
      woredas, ~US$6.6M cost — early-warning messages to ~1M people in Oromia/Somali, cash
      assistance to 70,000 people, livestock-feed vouchers to 96,000 people. Ran alongside a
      broader, separately-funded UN CERF (US$10M) + Ethiopia Humanitarian Fund (US$7M)
      anticipatory allocation covering Afar, Oromia, Somali and SNNP.
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
    This is WFP's OWN operational trigger (the EMI/IRI Maproom, woreda-level, Somali-region-led)
    — not a component of the OCHA/CERF collective Ethiopia drought framework. The OCHA page
    (frameworks/eth-drought, in-development 2026-06-09 version) explicitly notes that the
    September-October 2024 OND drought AA in Ethiopia was NOT an activation of the OCHA
    framework and belongs to WFP's own system (per DS-team feedback, OCHA-DAP/ds-knowledge-base
    issue #107); the two systems' OND geographies overlap substantially and how they'd
    coordinate in a joint activation is unaddressed in either org's documentation. The
    retired OCHA-endorsed 2020 framework (frameworks/eth-drought/2020-12-07.md) and this WFP
    framework are also separate CERF-history threads (2020/2021 CERF activations vs WFP's own
    2021/2022/2024 activations).
  schema_strain: >-
    (1) No public document states exact per-woreda forecast probability thresholds or lead
    times for the EMI/IRI Maproom trigger — the Maproom/dashboard tooling (fist.iri.columbia.edu)
    is described only at index level in sources reviewed. (2) The Hub-listed target_people
    (1,670,326) and prearranged_funding_usd (6,622,242, matching the reported ~US$6.6M total
    cost of the Sept 2024 Somali-region activation per CERF/WFP reporting) don't cleanly
    reconcile with the ~1M-people/US$6.6M single-activation figures reported for 2024 — the
    Hub figure may be a cumulative or broader-region framework envelope rather than one
    activation; not resolved in sources reviewed. (3) funding_by_source left {} — the Sept
    2024 US$6.6M WFP activation cost and the separate US$17M CERF (US$10M) + EHF (US$7M)
    multi-agency allocation are reported alongside each other but their exact relationship
    (is the WFP $6.6M drawn from the $17M, or additional) is not stated in sources reviewed.
    (4) Hub lists a 2023 listing year but no dated 2023 activation report was found distinct
    from the 2022 Deyr activation's continued response reporting; not recorded under
    `activations` to avoid guessing.
visibility: public
---

# WFP — Ethiopia drought

## Summary
WFP Ethiopia runs a Forecast-based Financing (FbF) anticipatory action system for drought,
built with the Ethiopian Meteorological Institute (EMI) and Columbia University's IRI
(the "EMI/IRI Maproom"), operating at woreda level in partnership with the Somali Region
Disaster Risk Management Bureau (DRMB) and extending into Oromia and SNNP. It is WFP's own
operational framework — distinct from, and running in parallel with, OCHA/CERF's Ethiopia
drought framework (see Coordination below). It has activated at least three times since
2021, most recently for the Oct-Dec 2024 La Niña drought.

## Trigger
Seasonal rainfall forecasts (Belg/MAM and Deyr-Kiremt/OND) are monitored per woreda through
the EMI/IRI Maproom decision-support tool; when forecasts point to a high chance of a failed
rainy season, WFP and the Somali Region DRMB (or Oromia/SNNP counterparts) activate weeks
ahead of the season — early enough to disburse cash and messaging before rains would have
arrived. Public sources describe the mechanism and lead-time logic in general terms but do
not publish the specific probability thresholds per woreda/season (see `extra.schema_strain`).

## Funding & scope
Anticipation Hub lists a framework envelope of ~US$6.6M and 1,670,326 people (see
`extra.schema_strain` on how these reconcile with individual activations). The Sept 2024
activation alone cost ~US$6.6M and targeted ~1M people with early-warning messaging, 70,000
with cash, and 96,000 with livestock-feed vouchers, in 15 Somali-region woredas. That
activation ran alongside a separate, broader UN allocation of US$17M (US$10M CERF + US$7M
Ethiopia Humanitarian Fund) covering Afar, Oromia, Somali and SNNP — the split between this
and WFP's own funding is not stated in sources reviewed.

## Activations
- **Mar 2021 (Belg/Gu)** — cash and early-warning messages to 14,600+ people in Somali
  region ahead of a forecast-failed rainy season; 95% of recipients reported acting on the
  warning.
- **Oct 2022 (Deyr)** — cash transfers, early-warning messaging, and rangeland
  enclosure/fodder production in Somali region ahead of a forecast-failed rainy season
  (lessons-learnt report published March 2024).
- **Sep 2024 (OND, for Oct-Dec 2024)** — La Niña-driven drought forecast: 15 Somali-region
  woredas, ~US$6.6M; early-warning messages to ~1M people in Oromia/Somali, cash to 70,000
  people, livestock-feed vouchers to 96,000 people.

## Coordination
This is WFP's own trigger system, not a WFP component of the OCHA/CERF collective Ethiopia
drought framework in [`frameworks/eth-drought/`](../../frameworks/eth-drought/). The OCHA
page's in-development version explicitly records that the Sept-Oct 2024 OND activation was
**not** an activation of the OCHA framework and belongs to this WFP system instead (OCHA-DAP
issue #107) — the two systems' geographies overlap in Somali/Oromia/SNNP and their
coordination in a joint activation is undocumented on either side.

## Sources
- **Authoritative:** [WFP Ethiopia drought anticipatory action activation document](https://www.anticipation-hub.org/Documents/Framework_documents/WFP-Ethiopia-Drought-0000162909.pdf) (Sep 2024, via Anticipation Hub)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- [Anticipatory cash transfers and early-warning information ahead of drought in Ethiopia](https://www.wfp.org/publications/anticipatory-cash-transfers-and-early-warning-information-ahead-drought-ethiopia) (WFP, Dec 2022 — covers Mar 2021 activation)
- [Anticipatory Action in Ethiopia: Drought Activation for Somali Region](https://www.wfp.org/publications/anticipatory-action-ethiopia-drought-activation-somali-region) (WFP, Mar 2024 — covers Oct 2022 activation)
- [Lessons learnt from Anticipatory Action 2022 Activation in Somali region, Ethiopia](https://www.wfp.org/publications/lessons-learnt-anticipatory-action-2022-activation-somali-region-ethiopia) (WFP)
- [In Ethiopia's drought-prone regions, early action is saving lives](https://ethiopia.un.org/en/294164-ethiopia%E2%80%99s-drought-prone-regions-early-action-saving-lives-and-building-resilient-future) (UN Ethiopia — 2024 activation detail)
- [WFP Ethiopia AA / EMI-IRI Maproom index](https://fist.iri.columbia.edu/publications/docs/ethiopia_aa_index/) (IRI Columbia — trigger tooling)
- Cross-reference: [OCHA Ethiopia drought framework](../../frameworks/eth-drought/) (separate CERF-history framework; see Coordination)
