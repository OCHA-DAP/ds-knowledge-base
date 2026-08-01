---
content_type: framework-external
framework: echo-bgd-flood
org: ECHO
country_iso3: BGD
hazard: flood
status: unknown
valid_until: "2025-06"
trigger_summary: >-
  The "SUFAL trigger matrix" (aligned with Bangladesh's government-endorsed National Early
  Action Protocol, NEAP, for monsoon riverine flood) uses GloFAS ensemble discharge
  forecasts and the FFWC 15-day forecast model at the Bahadurabad gauging station on the
  Jamuna. A readiness trigger (NEAP scenario 2) fires at ~10-day lead time when forecasts
  show >50% likelihood of discharge exceeding 100,000 m3/s over 3 days, prompting last-mile
  warning dissemination; an action trigger (NEAP scenario 5), closer to the event (~3-4 day
  lead time, water level approaching/crossing danger level), releases cash grants and
  evacuation support to targeted households.
data_sources:
  - GloFAS
  - FFWC
  - RIMES
prearranged_funding_usd: null
funding_by_source: {}
target_people: 100000
framework_doc: /global-overview/countries/bangladesh/supporting-flood-forecast-based-action-and-learning-in-bangladesh-sufal-phase-i-and-phase-ii
framework_doc_date: "2022-03-03"
sources:
  - https://www.anticipation-hub.org/global-overview/countries/bangladesh/supporting-flood-forecast-based-action-and-learning-in-bangladesh-sufal-phase-i-and-phase-ii
  - https://www.concern.net/knowledge-hub/supporting-flood-forecast-based-action-learning-bangladesh
  - https://legacy.rimes.int/node/848
  - https://www.carebangladesh.org/project-details/54
  - https://www.anticipation-hub.org/Documents/Case_Studies/CARE-Bangladesh_Case_Study_final.pdf
  - https://www.anticipation-hub.org/Documents/Evaluations/Post_Distribution_Monitoring__PDM__Report__Findings_of_PDM_Phase_3.pdf
  - https://www.care.org/news-and-stories/before-the-floods-how-an-early-warning-is-saving-lives-in-bangladesh/
  - https://www.anticipation-hub.org/download/file-3484
activations:
  - date: "2020-07"
    url: https://www.anticipation-hub.org/Documents/Case_Studies/CARE-Bangladesh_Case_Study_final.pdf
    note: >-
      First (Phase I) activation, Jamuna monsoon floods. ~100,000 people supported with
      community-based early actions; cash grants (reported at the household level, e.g.
      BDT 4,500 to help a family evacuate) alongside livestock and asset protection.
      Post-activation assessment found average household savings of BDT 19,161 (assets),
      36,552 (livestock) and 23,451 (fisheries).
  - date: "2024-07"
    url: https://www.anticipation-hub.org/Documents/Evaluations/Post_Distribution_Monitoring__PDM__Report__Findings_of_PDM_Phase_3.pdf
    note: >-
      SUFAL II tested the newly-approved (Jun 2024) NEAP for the first time: readiness
      (scenario 2) fired 1 Jul 2024, action (scenario 5) followed as Brahmaputra-Jamuna
      water levels crossed danger level in north-western Char areas. Multipurpose cash
      grants totaling BDT 3,535,000 (~EUR 28,280) disbursed to 700 households, plus
      evacuation assistance.
last_checked: "2026-08-01"
extra:
  hub_captions:
    - '2024: Flood (ECHO) [CARE International]'
  hub_years:
    - '2024'
  implementing:
    - CARE Bangladesh
    - CARE Deutschland e.V.
    - Concern Worldwide
    - Islamic Relief Bangladesh
    - RIMES
  funders:
    - ECHO
    - Aktion Deutschland Hilft (ADH)
  phases:
    - {phase: I, start: "2019-08", end: "2021-06", districts: [Kurigram, Gaibandha, Jamalpur]}
    - {phase: II, start: "2021-07", end: "2025-06", districts: [Kurigram, Gaibandha, Jamalpur, Bogura, Sylhet, Sunamganj, Netrokona]}
  coordination: >-
    NOT a component of the OCHA/CERF collective Bangladesh flood framework
    (frameworks/bgd-flooding — GloFAS/FFWC trigger at the same Bahadurabad station,
    CERF funding to FAO/WFP/UNICEF/UNFPA). SUFAL is a separately-funded (ECHO/ADH),
    CARE-led mechanism that happens to reference the same forecast station/threshold
    (100,000 m3/s at Bahadurabad) and, since 2024, the same government-owned National
    Early Action Protocol (NEAP) that the OCHA-coordinated framework also feeds into —
    the two ran in parallel during the July 2024 flood rather than as one integrated
    trigger. Treat as coordinated-but-independent, not a piece of the OCHA page.
  schema_strain: >-
    No public source reviewed states a total SUFAL project budget or ECHO's specific
    contribution (searched Hub, CARE, Concern, RIMES, ReliefWeb, PreventionWeb pages/PDFs);
    `prearranged_funding_usd`/`funding_by_source` left null/{} rather than guessed — the
    Hub-inventory stub's prior figure (81000) could not be corroborated in any source found
    and may reflect a partial/miscategorized figure, so it was dropped. `target_people`
    (100000) is the stated reach of the 2020 activation, not a formally stated programme
    target. `status` set to `unknown`: Phase II's stated end date (Jun 2025) has passed as
    of this review and no Phase III / continuation was found in public sources.
visibility: public
---

# ECHO — Bangladesh flood

## Summary
SUFAL ("Supporting Flood Forecast-based Action and Learning in Bangladesh") is an
ECHO/ADH-funded, CARE Bangladesh-led anticipatory action programme for monsoon (and, in
Phase II, flash) flooding, running in two phases since August 2019. It is implemented by a
consortium (CARE, Concern Worldwide, Islamic Relief Bangladesh, RIMES, plus local partners)
and works through community-based early-action plans and cash grants triggered by a
two-step forecast-based "trigger matrix" for the Brahmaputra-Jamuna basin. Phase I (2019-
2021) covered three north-western districts; Phase II (2021-2025) added a north-eastern
flash-flood/lightning component across four more districts. SUFAL's trigger matrix has,
since 2024, fed into Bangladesh's government-endorsed National Early Action Protocol
(NEAP) for monsoon riverine flood — a separate mechanism from, but running alongside, the
OCHA/CERF collective flood framework (see Coordination below).

## Trigger
A two-step "SUFAL trigger matrix", aligned with the NEAP: a **readiness trigger** (NEAP
scenario 2) fires at roughly 10-day lead time when GloFAS ensemble forecasts and/or the
FFWC 15-day model show more than 50% probability that discharge at the Bahadurabad gauging
station (Jamuna) will exceed 100,000 m3/s over a 3-day period — this is the same station
and threshold used by the OCHA/CERF framework's Jamuna readiness trigger. This prompts
last-mile dissemination of the flood warning. An **action trigger** (NEAP scenario 5)
follows at roughly 3-4 day lead time, closer to the point where water levels approach or
cross the government danger level, and releases cash transfers and evacuation support to
targeted households. Public sources describe the mechanism at this level of detail but do
not publish a single consolidated protocol document with a full threshold table (cf. the
OCHA framework's PDF); see `extra.schema_strain`.

## Funding & scope
No public source reviewed states SUFAL's total budget or ECHO's specific contribution
(funded jointly by ECHO and Aktion Deutschland Hilft, ADH). Concrete, sourced figures are
activation-level: the 2020 activation supported ~100,000 people; the July 2024 activation
disbursed multipurpose cash grants totaling BDT 3,535,000 (~EUR 28,280) to 700 households.
Phase I (Aug 2019-Jun 2021) covered Kurigram, Gaibandha and Jamalpur districts; Phase II
(Jul 2021-Jun 2025) added Bogura plus the north-eastern districts of Sylhet, Sunamganj and
Netrokona. Implementation is led by CARE Bangladesh (CARE Deutschland e.V. managing),
with Concern Worldwide, Islamic Relief Bangladesh and technical partner RIMES.

## Activations
- **Jul 2020** — first (Phase I) activation for Jamuna monsoon floods: ~100,000 people
  supported with community-based early actions and household cash grants; post-activation
  assessment found average household savings in the tens of thousands of BDT across
  assets, livestock and fisheries.
- **Jul 2024** — SUFAL II tested the newly-approved (Jun 2024) NEAP for the first time:
  readiness triggered 1 Jul 2024, action followed as Brahmaputra-Jamuna water levels
  crossed danger level in north-western Char areas; cash grants (BDT 3,535,000 / ~EUR
  28,280) reached 700 households alongside evacuation assistance.

## Coordination
SUFAL is **not** a component of the OCHA/CERF collective Bangladesh flood framework
(`frameworks/bgd-flooding`) — that framework is separately funded (CERF, to FAO/WFP/
UNICEF/UNFPA) and OCHA-coordinated. The two do, however, reference the same forecast
station and threshold (GloFAS discharge >100,000 m3/s at Bahadurabad) and, since the June
2024 NEAP approval, both feed into the same government-owned National Early Action
Protocol — they ran in parallel, not as one integrated trigger, during the July 2024
flood.

## Sources
- **Authoritative:** [Anticipation Hub — SUFAL Phase I and Phase II](https://www.anticipation-hub.org/global-overview/countries/bangladesh/supporting-flood-forecast-based-action-and-learning-in-bangladesh-sufal-phase-i-and-phase-ii) (published 3 Mar 2022, updated with later activation data)
- [Concern Worldwide — Supporting Flood Forecast-based Action and Learning](https://www.concern.net/knowledge-hub/supporting-flood-forecast-based-action-learning-bangladesh)
- [RIMES — SUFAL II project page](https://legacy.rimes.int/node/848)
- [CARE Bangladesh — project details](https://www.carebangladesh.org/project-details/54)
- [CARE Bangladesh case study (Anticipation Hub PDF mirror)](https://www.anticipation-hub.org/Documents/Case_Studies/CARE-Bangladesh_Case_Study_final.pdf)
- [Post-Distribution Monitoring (PDM) Phase 3 findings — SUFAL II](https://www.anticipation-hub.org/Documents/Evaluations/Post_Distribution_Monitoring__PDM__Report__Findings_of_PDM_Phase_3.pdf) (2024 activation figures)
- [CARE — "Before the floods" story](https://www.care.org/news-and-stories/before-the-floods-how-an-early-warning-is-saving-lives-in-bangladesh/)
- [Anticipation Hub — Flood 2020: Trigger Analysis, Bangladesh](https://www.anticipation-hub.org/download/file-3484) (11 Mar 2021, Ahmadul Hassan)
