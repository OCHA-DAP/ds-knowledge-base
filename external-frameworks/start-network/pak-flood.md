---
content_type: framework-external
framework: start-network-pak-flood
org: START
country_iso3: PAK
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Parametric trigger for the Indus River basin (Start Ready Risk Pool 1, dedicated to
  Pakistan flood): GloFAS discharge forecasts are translated into district-level impact
  forecasts via JBA's Flood Foresight model, covering the ~132 districts that fall within
  Pakistan's share of the Indus basin. When forecast discharge exceeds a return-period
  threshold at a given gauge for a sustained period, the district is flagged as "breached";
  in the confirmed August 2024 trigger this was a 20-year return-period discharge sustained
  over ~10 continuous days, with lead times of 0-3 days once confirmed at district level.
  Breached districts become eligible for prepositioned Risk Pool 1 funding; READY Pakistan
  hub members then submit activation proposals for a subset of the breached districts.
data_sources: [GloFAS, JBA Flood Foresight]
prearranged_funding_usd: 2634407
funding_by_source: {}
target_people: 635923
framework_doc: https://startnetwork.org/disaster-risk-financing-pakistan
framework_doc_date: null
sources:
- https://startnetwork.org/disaster-risk-financing-pakistan
- https://startnetwork.org/funds/start-ready/disaster-risk-financing-pakistan
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/pakistan
- https://www.anticipation-hub.org/experience/global-map
- https://startnetwork.org/funds/start-ready/activations/act-00000013
- https://reliefweb.int/report/pakistan/floods-pakistan-subside-locally-led-action-subverts-traditional-aid-myths
- https://startnetwork.org/learn-change/news-and-blogs/when-forecasts-failed-action-didnt-start-readys-experience-basis-risk
- https://startnetwork.org/learn-change/news-and-blogs/start-ready-reaches-new-milestone-fourth-risk-pool
- https://www.jbaconsulting.com/projects/flood-risk-and-forecast-modelling-solutions-supporting-humanitarian-and-financial-early-action-in-pakistan/
- https://jbagr.com/digital-tools/flood-foresight/
- https://startnetwork.org/about/current-vacancies/Pakistan-StartReady-Flood-Programme-Evaluation
- https://startnetwork.org/network/hubs/ready-pakistan
activations:
- date: '2022-07'
  url: https://reliefweb.int/report/pakistan/floods-pakistan-subside-locally-led-action-subverts-traditional-aid-myths
  note: >-
    Risk Pool 1 (act-00000013) fired ahead of the catastrophic 2022 monsoon floods; members
    raised Start Fund Alert 619 (12 Jul 2022, £400,000 GBP) for Quetta, Pishin and Killa
    Saif Ullah districts (Balochistan), plus a further £129,000 GBP from READY Pakistan's
    own reserves for 1,200 families across 6 districts. Across the response, Start Network
    initiatives supported ~10,200 families with food, NFI, shelter, cash and WASH — funding
    landed roughly a month before CERF's $10,071,433 allocation (end Aug 2022).
- date: '2024-08-20'
  url: https://startnetwork.org/learn-change/news-and-blogs/when-forecasts-failed-action-didnt-start-readys-experience-basis-risk
  note: >-
    GloFAS/Flood Foresight trigger breached in 20 Indus-basin districts (lead times 0-3
    days); Start Network activated members' proposals in 11 of the 20 districts, reaching
    58,000+ people. The Anticipation Hub's per-year record for this activation shows
    $879,221 released against 92,291 people targeted.
- date: '2025-08'
  url: https://jbagr.com/digital-tools/flood-foresight/
  note: >-
    Rising Indus-basin flood risk (the wider Aug-Sep 2025 Punjab floods) triggered Start
    Ready again, per JBA (the trigger's technical partner); specific funding/people-reached
    figures for this activation were not found in accessible public sources — see
    `extra.schema_strain`. Distinct from PRCS/IFRC's own concurrent Chenab/Indus EAP
    activation the same period (`external-frameworks/ifrc/pak-flood.md`).
last_checked: '2026-07-24'
extra:
  hub_captions:
  - '2022: Flood (Start Network) [Tearfund] [Mercy Corps] [Initiative for Development & Empowerment
    Axis] [HelpAge International] [HANDS] [Help Foundation] [acted]'
  - '2023: Flood (Start Network) [Bright Star Development Balochistan] [Health & Nutrition
    Development Society] [HelpAge International] [Help Foundation] [National Integrated Development
    Association] [Participatory Rural Development Society] [Rural Empowerment and Institutional
    Development] [Welfare Association Jared]'
  - '2024: Flood (Start Network) [CARE International] [Doaba Foundation] [HANDS] [Help Foundation]
    [Tearfund]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - CARE International
  - Doaba Foundation
  - HANDS
  - Help Foundation
  - Tearfund
  risk_pool: >-
    This is Start Ready Risk Pool 1 (RP1), which the Start Network's own evaluation RFP
    describes as "focused on Flooding" in Pakistan specifically — a standing parametric
    pool that can fire repeatedly (confirmed 2022, 2024, 2025), unlike IFRC's versioned
    EAP generations. Start Ready has since added further risk pools (RP2-RP4) across other
    countries/hazards; RP1 is Pakistan flood's.
  coordination: >-
    No OCHA/CERF collective AA framework exists for Pakistan flood (confirmed absent from
    `frameworks/` — see the coordination note on `external-frameworks/ifrc/pak-flood.md`).
    The Pakistan Red Crescent Society (with IFRC/German Red Cross) runs its own, separate
    DREF-funded flood EAP (Kabul River EAP2023PK01, superseded by the nationwide
    EAP2025PK02) — a distinct instrument from this Start Network/READY Pakistan DRF system,
    not a duplicate of it. The two activated within days of each other during the Aug-Sep
    2025 Punjab floods.
  funding_note: >-
    Per-activation figures (2022: £400k + £129k GBP Start Fund/reserves; 2024: $879,221
    per the Hub's per-year record) do not reconcile cleanly to the headline
    `prearranged_funding_usd`/`target_people` above, which are the Anticipation Hub's
    live Pakistan country-page "Active Frameworks" snapshot ($2,634,407 / 635,923 people)
    — likely a current cumulative/model figure rather than a single activation's budget.
    The original Hub-inventory record used to create this page's stub gave different
    figures again ($957,854 / 140,713 people), suggesting these numbers move between Hub
    snapshots; treat all as imprecise, not audited totals.
  schema_strain: >-
    `framework_doc` (startnetwork.org/disaster-risk-financing-pakistan) is a general
    programme page, not a single dated EAP-style protocol document — Start Ready's flood
    trigger is a parametric model (GloFAS discharge + JBA Flood Foresight impact
    translation) rather than a published PDF with an approval date, so `framework_doc_date`
    is left null. startnetwork.org blocks automated full-text fetches (403 on every URL
    tried), so detail here relies on search-engine-surfaced snippets of its own
    blog/activation pages rather than verified full text; a fuller Risk Pool 2-4 activation
    history and confirmed 2025 funding/beneficiary figures were not obtainable this way.
visibility: public
---

# START — Pakistan flood

## Summary
Start Network's Pakistan Disaster Risk Financing (DRF) system, run through the READY
Pakistan hub (all Start Network members in-country, in incubation since 2017), pre-arranges
funding against a parametric flood model covering the Indus River basin — roughly 132
Pakistani districts. The flood-specific instrument is Start Ready Risk Pool 1 (RP1): when
JBA's Flood Foresight model (built on GloFAS discharge forecasts) flags districts as
breaching a return-period threshold, prepositioned funds and Start Fund top-ups become
available for members to run anticipatory cash, NFI, shelter and WASH activities in the
worst-affected districts. RP1 has fired at least three times (2022, 2024, 2025). It is
separate from the Pakistan Red Crescent Society/IFRC's own DREF-funded flood EAP (see
`extra.coordination`); no OCHA/CERF collective framework exists for Pakistan flood.

## Trigger
A parametric, impact-based design rather than a single-station threshold: JBA's Flood
Foresight technology couples the Copernicus GloFAS discharge forecast with hydraulic
modelling to produce daily probabilistic flood-inundation and population-at-risk estimates
across the Indus basin. A district is "breached" when forecast discharge exceeds a
return-period threshold for a sustained period — in the confirmed 20 August 2024 trigger,
this was a 20-year return-period discharge sustained over roughly 10 continuous days,
yielding lead times of 0-3 days once confirmed. Breaches fired in 20 districts that time;
Start Network members then chose 11 of those districts to activate proposals in, rather
than acting in all breached districts automatically. Full published thresholds for
individual gauges/districts were not found in accessible public sources.

## Funding & scope
Headline figures per the Anticipation Hub's live Pakistan country page: ~US$2.63M
pre-arranged, targeting ~635,923 people (see `extra.funding_note` — this doesn't cleanly
match either the original Hub-inventory stub figures or any single activation's actual
spend). Funding for individual activations has come from a mix of Start Ready's
prepositioned risk-pool tranche, the Global Start Fund, READY Pakistan's own national
reserves, and bilateral top-ups (e.g. Germany's Federal Foreign Office, GFFO). Geographic
scope is the Indus River basin (~58% of Pakistan's land area, ~132 districts), with
specific district selection made hazard-event by hazard-event.

## Activations
- **July 2022** — RP1 fired ahead of the mega monsoon floods: Start Fund Alert 619
  (£400,000 GBP, 12 Jul 2022) for Quetta, Pishin and Killa Saif Ullah (Balochistan), plus
  £129,000 GBP from READY Pakistan's reserves for 1,200 families in 6 further districts;
  ~10,200 families supported overall with food, NFI, shelter, cash and WASH — roughly a
  month ahead of CERF's $10.07M allocation.
- **20 August 2024** — trigger breached in 20 Indus-basin districts (0-3 day lead times);
  members activated proposals in 11 districts, reaching 58,000+ people. The Hub's per-year
  record shows $879,221 released against 92,291 people targeted.
- **August 2025** — renewed Indus-basin flood risk (the wider Aug-Sep 2025 Punjab floods)
  triggered Start Ready again per JBA; funding/beneficiary specifics not confirmed in
  public sources reviewed.

## Sources
- **Authoritative:** [Disaster Risk Financing Pakistan](https://startnetwork.org/disaster-risk-financing-pakistan) (framework/programme page) · [current URL](https://startnetwork.org/funds/start-ready/disaster-risk-financing-pakistan)
- [Anticipation Hub — Pakistan country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/pakistan) (live active-framework and per-year activation figures, fetched 2026-07-24)
- [Anticipation Hub — global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
- [RP1 Pakistan Floods — Start Ready activations dashboard](https://startnetwork.org/funds/start-ready/activations/act-00000013)
- [ReliefWeb — "As floods in Pakistan subside, locally led action subverts traditional aid myths"](https://reliefweb.int/report/pakistan/floods-pakistan-subside-locally-led-action-subverts-traditional-aid-myths) (2022 activation detail)
- [Start Network — "When forecasts failed, but action didn't: Start Ready's experience with basis risk"](https://startnetwork.org/learn-change/news-and-blogs/when-forecasts-failed-action-didnt-start-readys-experience-basis-risk) (2024 trigger detail)
- [Start Network — "Start Ready Reaches New Milestone with Fourth Risk Pool"](https://startnetwork.org/learn-change/news-and-blogs/start-ready-reaches-new-milestone-fourth-risk-pool)
- [JBA Consulting — Flood risk and forecast modelling in Pakistan](https://www.jbaconsulting.com/projects/flood-risk-and-forecast-modelling-solutions-supporting-humanitarian-and-financial-early-action-in-pakistan/) (Indus basin coverage, 132 districts)
- [JBA Global Resilience — Flood Foresight](https://jbagr.com/digital-tools/flood-foresight/) (2025 activation mention)
- [Start Network — Pakistan Start Ready Flood Programme Evaluation RFP](https://startnetwork.org/about/current-vacancies/Pakistan-StartReady-Flood-Programme-Evaluation) (confirms RP1 = Pakistan flood pool, 2024 activation review scope)
- [Start Network — READY Pakistan hub](https://startnetwork.org/network/hubs/ready-pakistan)
- Related, distinct instrument: [`external-frameworks/ifrc/pak-flood.md`](../ifrc/pak-flood.md) (Pakistan Red Crescent Society/IFRC's own flood EAP)
