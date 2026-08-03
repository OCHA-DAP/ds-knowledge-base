---
content_type: framework-external
framework: oxfam-som-el-nino
org: Oxfam
country_iso3: SOM
hazard: el-nino
status: active
valid_until: null
trigger_summary: >-
  No single quantified threshold is published. Oxfam pre-funds NEXUS — a locally-led
  consortium of Somali NGOs (incl. Centre for Peace and Democracy/CPD, KAALO, and Social
  Life and Agricultural Development Organization/SADO) — whose Anticipatory and Emergency
  Response Fund releases pre-arranged cash to member organisations when a Steering
  Committee judges, against seasonal forecasts (WMO/ENSO, FSNAU food-security data,
  national weather agencies) and local early-warning reports, that a forecast hazard
  (drought, flood, or other) meets fund criteria (>=100 people likely affected). This is
  an expert-judgement/multi-source alert process, not a single indicator-threshold trigger
  — see `extra.schema_strain`.
data_sources: [FSNAU]
prearranged_funding_usd: 250000
funding_by_source: {}
target_people: 25000
framework_doc: https://www.anticipation-hub.org/download/file-803
framework_doc_date: 2020-10
sources:
- https://www.anticipation-hub.org/download/file-803
- https://www.anticipation-hub.org/global-overview/countries/somalia
- https://www.anticipation-hub.org/experience/global-map
- https://heca.oxfam.org/latest/policy-paper/governance-and-structure-nexus-somalia
- https://heca.oxfam.org/latest/policy-paper/enough-theory-somali-consortium-putting-nexus-programming-action
- http://nexusom.org/
activations: []
last_checked: '2026-07-29'
extra:
  hub_captions:
  - '2023: El Niño/La Niña (Oxfam) [Centre for Peace and Democracy] [KAALO] [Oxfam] [Social
    Life and Agricultural Development Organization]'
  hub_years:
  - '2023'
  implementing:
  - Centre for Peace and Democracy
  - KAALO
  - Oxfam
  - Social Life and Agricultural Development Organization
  fund_mechanism: >-
    The named partners are members (CPD, KAALO, SADO) and funder (Oxfam) of NEXUS, a
    Somali civil-society platform founded 2019 with eight core Somali NGO members (CPD,
    GREDO, HAVOYOCO, KAALO, SSWC, SADO, TASCO, WASDA), supported by Oxfam and Save the
    Children International since 2019. NEXUS's Anticipatory and Emergency Response Fund
    (est. 2020) is fully locally-led: Oxfam disburses funds to NEXUS in advance, and a
    NEXUS Steering Committee (not Oxfam) decides allocations. Per the framework document,
    an activation runs: member raises an alert -> Steering Committee reviews against fund
    criteria within 24h -> member submits a proposal (location, amount, target
    population, mitigation actions) within 48h -> Steering Committee approval within 72h
    -> funds transferred within 72h -> response starts within 5-7 days -> completed
    within 60 days. Per-activation amounts were originally EUR 50,000-80,000; hazards
    covered include drought, flood, locusts, disease outbreak, conflict/displacement and
    heatwave, not only El Niño/La Niña.
  coordination: >-
    Not a component of an OCHA/CERF collective framework — this KB holds no OCHA-portfolio
    Somalia flood or El Niño page (only the unrelated, retired `frameworks/som-drought`
    2019 pilot, a different hazard and instrument). Independent of WFP's and IFRC's own
    Somalia AA frameworks (`external-frameworks/wfp/som-drought.md`,
    `external-frameworks/ifrc/som-drought.md`) — no source found linking this NEXUS/Oxfam
    mechanism to either.
  schema_strain: >-
    No primary document was found describing a specific, dated 2023 El Niño activation
    (trigger levels actually met, districts, disbursement date, beneficiary breakdown by
    partner) — the Hub's global-map API record for this framework carries `year: "2023"`
    and `framework_link` pointing only to the Anticipation Hub homepage (no project page),
    and the Hub's Somalia country page repeats the same USD 250,000 / 25,000-people
    figures without a document citation. It is unclear whether "2023" marks a confirmed
    activation or just the year this framework entry was catalogued as active; `activations`
    is left empty rather than guessing. The only primary document located for the
    underlying fund mechanism (`framework_doc`) is NEXUS's October 2020 fund design paper,
    which predates and is hazard-agnostic beyond El Niño/La Niña specifically — it explains
    the mechanism and partners but not the 2023 figures themselves. `data_sources: [FSNAU]`
    reflects the one named forecasting input in that document; ENSO/WMO seasonal forecasts,
    Radio Ergo community reports and the Red Cross Climate Centre/REAP are also cited
    there as alert inputs but have no matching KB tag.
visibility: public
---

# Oxfam — Somalia el nino

## Summary
The Anticipation Hub lists an Oxfam-funded anticipatory action framework for El Niño/La
Niña in Somalia (2023), naming Oxfam alongside three Somali NGOs — Centre for Peace and
Democracy (CPD), KAALO, and the Social Life and Agricultural Development Organization
(SADO) — as implementing partners, with a USD 250,000 pre-arranged envelope against
25,000 target people. Those three NGOs, together with five others, make up **NEXUS**, a
Somali civil-society consortium founded in 2019 and supported by Oxfam and Save the
Children International. Since 2020, NEXUS has run a locally-led **Anticipatory and
Emergency Response Fund**: Oxfam disburses funding to NEXUS in advance, and a NEXUS
Steering Committee — not Oxfam — decides which member organisations receive money and
when, based on forecasts and local early-warning reports. This page most likely records
Oxfam's funding of that fund's use by CPD, KAALO and SADO in the context of the 2023
El Niño-driven Deyr floods, though no primary document describing a specific dated 2023
activation was located (see `extra.schema_strain`).

## Trigger
The underlying NEXUS fund does not use a single quantified indicator/threshold. Instead,
a member organisation raises an alert to the NEXUS Steering Committee when evidence
suggests a forecast hazard will affect a community; the Committee assesses the alert
against fund criteria (at minimum ~100 people likely affected, member presence/access in
the area, community-driven request, a link to longer-term "triple nexus" outcomes) using
a mix of seasonal/meteorological forecasts (WMO/ENSO outlooks, national weather agencies),
food-security data (FSNAU), and community-sourced early-warning reports (e.g. Radio Ergo).
The fund explicitly covers multiple hazards — drought, flood, locusts, disease outbreak,
conflict/displacement, heatwave — with El Niño/La Niña forecasts (as in the October 2020
La Niña outlook that motivated the fund's design) as one forecast input among several,
not a standalone El Niño-specific trigger.

## Funding & scope
The Anticipation Hub lists a USD 250,000 pre-arranged envelope against 25,000 target
people for this Oxfam/NEXUS El Niño framework in Somalia — figures repeated on the Hub's
global map and Somalia country page but not traced to a primary financial document. The
NEXUS fund design document specifies per-activation grants of EUR 50,000-80,000 to
individual member organisations, a maximum 60-day implementation window per activation,
and funding advanced by Oxfam to NEXUS (rather than a fixed line-item budget disclosed
per partner). No source reviewed breaks the USD 250,000 down by recipient organisation
(CPD / KAALO / SADO) or by activation.

## Activations
None confirmed from primary sources. The Anticipation Hub's inventory record for this
framework carries the year "2023" (matching the "2023: El Niño/La Niña" Hub caption), but
no news release, situation report, or NEXUS/Oxfam publication describing an actual 2023
disbursement — dates, districts, trigger levels met, or people reached — was located. It
is possible the "2023" tag reflects when the framework was catalogued rather than a
confirmed activation; treated here as unconfirmed rather than guessed (see
`extra.schema_strain`).

## Sources
- **Authoritative (fund mechanism):** [NEXUS' Anticipatory and Emergency Response Fund (Anticipation Hub, Oct 2020)](https://www.anticipation-hub.org/download/file-803)
- [Anticipation Hub — Somalia country page](https://www.anticipation-hub.org/global-overview/countries/somalia) (current USD 250,000 / 25,000-people listing for this framework)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record; `framework_link` resolves only to the Hub homepage)
- [Oxfam HECA — Governance and structure, NEXUS Somalia](https://heca.oxfam.org/latest/policy-paper/governance-and-structure-nexus-somalia) (Oxfam/Save the Children support since 2019; CPD/KAALO/SADO as core members)
- [Oxfam HECA — "Enough theory! A Somali consortium putting nexus programming into action"](https://heca.oxfam.org/latest/policy-paper/enough-theory-somali-consortium-putting-nexus-programming-action) (NEXUS background, 8 core members)
- [NEXUS Somalia](http://nexusom.org/) (consortium homepage)
