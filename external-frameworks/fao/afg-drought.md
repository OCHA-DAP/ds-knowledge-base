---
content_type: framework-external
framework: fao-afg-drought
org: FAO
country_iso3: AFG
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  FAO runs a community-based drought early-warning system across four provinces (Faryab,
  Ghor, Kunar, Samangan) tracking hydro-agrometeorological factors (rainfall, snowfall,
  soil moisture, surface water flows), agricultural-livelihoods indicators (productive
  assets, crop cultivation, livestock keeping, prices) and food-insecurity change. A 2021
  precursor activation was triggered by a forecast moderate-to-strong La Niña expected to
  suppress rainfall/snowfall through the spring 2021 wheat season. No single quantified
  numeric threshold or fixed lead time is published in the sources reviewed — see
  `extra.schema_strain`.
data_sources: []
prearranged_funding_usd: 2213962
funding_by_source: {}
target_people: 119000
framework_doc: https://www.fao.org/3/cb9099en/cb9099en.pdf
framework_doc_date: 2022-02
sources:
- https://www.fao.org/3/cb9099en/cb9099en.pdf
- https://www.fao.org/in-action/drought-portal/project-detail/anticipatory-actions-to-mitigate-the-impact-of-drought-on-agricultural-livelihoods-in-acutely-food-insecure-rural-areas-of-afghanistan/en
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/afghanistan
- https://www.anticipation-hub.org/download/file-4044
- https://www.fao.org/emergencies/resources-repository/news/detail/Mitigating-the-potential-impacts-of-dry-conditions-triggered-by-La-Ni%C3%B1a-in-Afghanistan/en
- https://reliefweb.int/report/afghanistan/afghanistan-impact-anticipatory-action-curbing-la-nina-induced-drought
activations:
- date: 2021-01
  url: https://www.fao.org/emergencies/resources-repository/news/detail/Mitigating-the-potential-impacts-of-dry-conditions-triggered-by-La-Ni%C3%B1a-in-Afghanistan/en
  note: >-
    Forecast of a moderate-to-strong La Niña suppressing rainfall/snowfall through the
    2021 wheat season triggered early action in Samangan Province ~6 months before
    drought was officially declared (22 Jun 2021): crop-production packages (2,000
    households), cash-for-work/unconditional cash transfers (1,500 households, ~USD
    50/household), and livestock protection for 2,000 Kuchi herders (~7,680 people
    total). Funded by USD 580,000 from Belgium via FAO's SFERA Anticipatory Action
    window. A subsequent FAO impact evaluation found a return of ~USD 1.42 per USD 1
    spent in avoided losses/added benefits.
last_checked: '2026-07-23'
extra:
  hub_captions:
  - '2022: Drought (FAO) [FAO]'
  - '2023: Drought (FAO) [FAO]'
  hub_years:
  - '2022'
  - '2023'
  implementing:
  - FAO
  project_code: OSRO/AFG/123/CHG
  coordination: >-
    Distinct from the OCHA/CERF collective Afghanistan Drought Anticipatory Action
    Framework (see frameworks/afg-drought/ — a SEAS5/CDI-triggered, CERF+AHF-funded
    framework covering Balkh, Faryab, Jawzjan, Sar-e-Pul and Badghis, first activated
    April 2025). FAO is an implementing agency in that collective framework too
    (CERF allocation ~$3.25M targeting ~85,120 people), but the framework documented
    on this page is FAO's own, separately designed and funded program (community-based
    EWS, different provinces — only Faryab overlaps) — not a component of the CERF
    framework. Do not conflate the two.
  schema_strain: >-
    (1) `framework_doc` (cb9099en.pdf) returned HTTP 403 on every fetch attempt
    (direct, openknowledge.fao.org mirror, web-proxy) — its content could not be read
    directly. Its title/scope/date are inferred from the FAO drought-portal project
    page for the identically-named project "Anticipatory actions to mitigate the
    impact of drought on agricultural livelihoods in acutely food-insecure rural areas
    of Afghanistan" (OSRO/AFG/123/CHG, budget USD 2,213,962, start 14 Feb 2022, 119,000
    people, Faryab/Ghor/Kunar/Samangan) — matching Hub inventory years (2022, 2023) —
    but this match is inferential, not confirmed from the PDF itself.
    (2) No numeric trigger threshold or lead time for the current (2022-) project is
    published in sources found; only the monitored indicator categories are described.
    (3) The donor behind the "CHG" project code (OSRO/AFG/123/CHG) is not identified in
    sources reviewed; `funding_by_source` left empty rather than guessing (the 2021
    precursor activation's Belgium/SFERA funding is recorded separately in
    `activations`, since it may predate/differ from this project's own funding).
    (4) The Anticipation Hub's Afghanistan country page (checked 2026-07-23) lists a
    separate FAO drought framework entry as "under development" with $0 funding/0
    people targeted — unreconciled with the funded, ongoing OSRO/AFG/123/CHG project;
    may reflect a newer, distinct pipeline entry or a stale/placeholder Hub record.
    (5) The exact relationship between the 2021 Samangan activation (pre-dating
    OSRO/AFG/123/CHG's Feb 2022 start) and the current project is not stated in any
    single source — both are FAO SFERA/EWEA-style drought responses in overlapping
    provinces, but whether the 2021 response was formally the same framework or an
    earlier precursor program is not confirmed.
visibility: public
---

# FAO — Afghanistan drought

## Summary
FAO runs a community-based anticipatory action program for drought in Afghanistan,
currently operating as the project "Anticipatory actions to mitigate the impact of
drought on agricultural livelihoods in acutely food-insecure rural areas of Afghanistan"
(OSRO/AFG/123/CHG, started 14 February 2022, budget USD 2,213,962), targeting 119,000
people — vulnerable livestock-keeping and landless/marginal-asset-holding households,
prioritising women-headed, disability-affected and elderly households — across Faryab,
Ghor, Kunar and Samangan provinces. It is distinct from, though partly geographically
overlapping with, the OCHA/CERF collective Afghanistan Drought Anticipatory Action
Framework in which FAO is also an implementing agency (see `extra.coordination`).

## Trigger
The project establishes a community-based drought early-warning system tracking
hydro-agrometeorological factors (rainfall, snowfall, soil moisture, surface water
flows), agricultural-livelihoods indicators (productive assets, crop cultivation,
livestock keeping, prices) and food-insecurity change. Public sources describe the
monitored indicator categories but do not publish a single quantified numeric threshold
or fixed lead time for the current project. A well-documented 2021 precursor response
was triggered by a seasonal forecast of a moderate-to-strong La Niña expected to
suppress rainfall and snowfall through the 2021 wheat season (harvest May–July),
allowing FAO to act roughly six months before drought was officially declared in
Afghanistan on 22 June 2021.

## Funding & scope
The current project (OSRO/AFG/123/CHG) has a budget of **USD 2,213,962**, targeting
**119,000 people** across four provinces (Faryab, Ghor, Kunar, Samangan); the specific
donor behind the project's "CHG" code is not identified in sources reviewed. Key
interventions: livestock protection packages (concentrated feed, fodder seeds,
deworming), backyard vegetable/home-gardening packages, climate-smart agriculture
training, and early-action disease-management advisories.

The 2021 precursor activation in Samangan Province was funded separately: **USD
580,000** contributed by Belgium through FAO's SFERA (Special Fund for Emergency and
Rehabilitation Activities) Anticipatory Action window, reaching roughly 7,680 people —
2,000 households with crop-production packages, 1,500 households with cash-for-work or
unconditional cash transfers (~USD 50/household), and 2,000 Kuchi (nomadic) livestock
keepers with livelihood-protection support.

## Activations
- **January 2021 (Samangan Province, La Niña-induced drought).** Forecast of a
  moderate-to-strong La Niña suppressing rainfall/snowfall through the 2021 wheat
  season prompted early action roughly six months ahead of Afghanistan's official
  drought declaration (22 June 2021): crop-production packages, cash assistance and
  livestock-protection support for ~7,680 people, funded by USD 580,000 from Belgium
  via FAO's SFERA-AA window. A subsequent FAO impact evaluation found a return of
  ~USD 1.42 per USD 1 spent in avoided losses and added benefits.

No further activation of the current OSRO/AFG/123/CHG project (2022–) is documented in
the public sources reviewed; the Hub lists this FAO drought framework as active for
2022 and 2023, which reflects ongoing project/inventory presence rather than a
confirmed additional trigger event.

## Sources
- **Authoritative:** [Framework document (cb9099en.pdf)](https://www.fao.org/3/cb9099en/cb9099en.pdf) — inaccessible for direct read (HTTP 403 on all fetch attempts); details inferred from the matching drought-portal project page (see `extra.schema_strain`)
- [FAO drought portal — project detail: Anticipatory actions to mitigate the impact of drought on agricultural livelihoods in acutely food-insecure rural areas of Afghanistan](https://www.fao.org/in-action/drought-portal/project-detail/anticipatory-actions-to-mitigate-the-impact-of-drought-on-agricultural-livelihoods-in-acutely-food-insecure-rural-areas-of-afghanistan/en) (project code, budget, target people, provinces, start date)
- [Mitigating the potential impacts of dry conditions triggered by La Niña in Afghanistan](https://www.fao.org/emergencies/resources-repository/news/detail/Mitigating-the-potential-impacts-of-dry-conditions-triggered-by-La-Ni%C3%B1a-in-Afghanistan/en) (FAO, Jan 2021 — the 2021 activation: trigger, funding, target households)
- [Afghanistan: Impact of Anticipatory Action — Curbing La Niña-induced drought](https://reliefweb.int/report/afghanistan/afghanistan-impact-anticipatory-action-curbing-la-nina-induced-drought) (FAO impact evaluation via ReliefWeb; also [Anticipation Hub mirror](https://www.anticipation-hub.org/download/file-4044)) — ROI and outcome detail for the 2021 activation
- [Anticipation Hub — Afghanistan](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/afghanistan) (checked 2026-07-23; shows a separately-listed FAO drought framework entry as "under development" — see `extra.schema_strain`)
