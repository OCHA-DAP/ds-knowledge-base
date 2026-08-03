---
content_type: framework-external
framework: start-network-phl-epidemic
org: START
country_iso3: PHL
hazard: epidemic
status: active
valid_until: null
trigger_summary: >-
  Not a pre-set parametric trigger — this is Start Network's discretionary "Start Fund
  Anticipation" alert mechanism: a member agency raises an alert when forecasts/case data
  point to an imminent outbreak, and the Start Fund Committee votes a proposal into funding
  within days. Alert 850 (2024) was raised after Super Typhoon Carina (Jul 2024) created
  conditions conducive to a dengue outbreak, evidenced by 503 cumulative dengue cases
  recorded in Malabon Jan-Aug 2024.
data_sources: []
prearranged_funding_usd: null
funding_by_source: {}
target_people: null
framework_doc: https://www.worldvision.org.ph/malabon-families-get-hygiene-kits-mosquito-nets-to-combat-dengue-other-diseases/
framework_doc_date: 2024-09-13
sources:
  - https://www.anticipation-hub.org/experience/global-map
  - https://www.worldvision.org.ph/malabon-families-get-hygiene-kits-mosquito-nets-to-combat-dengue-other-diseases/
  - https://startnetwork.org/funds/global-start-fund/alerts/850-philippines-anticipation-disease-outbreak
  - https://startnetwork.org/about/current-vacancies/rfp-impact-assessment-start-fund-anticipation-alert-philippines-anticipation-disease-outbreak
  - https://www.anticipation-hub.org/news/linking-early-warnings-to-early-action-compound-hydrometeorologiacal-hazards-and-dengue-outbreaks
activations:
  - date: '2022'
    note: >-
      Hub-listed disease-outbreak anticipation alert, implemented by Humanity &
      Inclusion. No alert number, funding amount, or activity detail found in public
      sources reviewed — see `extra.schema_strain`.
  - date: 2024-09-07
    url: https://www.worldvision.org.ph/malabon-families-get-hygiene-kits-mosquito-nets-to-combat-dengue-other-diseases/
    note: >-
      Start Fund Alert 850 ("Philippines: Anticipation of disease outbreak"), raised
      after Super Typhoon Carina (Jul 2024) elevated dengue/Mpox risk in Metro Manila.
      Start Fund Committee unanimously awarded GBP 300,000 to a consortium (Relief
      International, Humanity & Inclusion, World Vision, local partner PhilRADS) under
      the project IADOR (Inclusive Anticipatory Disease Outbreak Response for Super
      Typhoon Carina), coordinating with LGUs in Malabon, Manila and San Mateo (Rizal).
      World Vision's slice: hygiene kits, mosquito nets, water-purification tablets and
      dengue/Mpox prevention flyers to 555 families in two Malabon barangays (7 Sep
      2024), plus cash-for-community-cleaning (PHP 1,500/person for 3 days) across five
      Malabon barangays.
last_checked: '2026-07-24'
extra:
  hub_captions:
  - '2022: Disease outbreak (Start Network) [Humanity & Inclusion]'
  - '2024: Disease outbreak (Start Network) [Start Network]'
  hub_years:
  - '2022'
  - '2024'
  implementing:
  - Start Network
  mechanism: >-
    This is Start Network's general "Start Fund Anticipation" facility (ad hoc alerts,
    Committee-voted proposals), not a standing pre-arranged EAP/protocol with fixed
    thresholds — distinct from Start Network's Philippines typhoon Disaster Risk
    Financing (parametric, 510-model-based; see external-frameworks/start-network/phl-tropical-cyclone.md),
    which is a separate framework page.
  funding_2024_gbp: 300000
  schema_strain: >-
    The stub's prior top-level prearranged_funding_usd (95785) and target_people
    (164959) — both from the Hub global-map API, which appears to aggregate the 2022
    and 2024 records under one framework identity — could not be reconciled against
    public sources: the only concrete funding figure found (GBP 300,000 for the 2024
    Alert 850) doesn't match 95785 at any plausible exchange rate, and the only
    concrete reach figure found (555 families / 2 barangays, part of a wider
    multi-barangay, multi-city consortium response) doesn't obviously sum to 164,959
    either (though 164,959 may represent total at-risk population across Malabon/
    Manila/San Mateo Rizal rather than direct beneficiaries — unconfirmed). Set both
    to null rather than guess which record(s) they describe; per-activation funding is
    recorded in `activations` instead. No alert-number, amount, or activity detail was
    found in public sources for the 2022 (Humanity & Inclusion) activation.
  background: >-
    An earlier R&D strand (2021) — Start Network with World Vision's "Dengue Project" —
    developed a Dengue Risk Analysis Tool for Manila/Malabon/Quezon City, finding a
    ~3-month lag between weather conditions (temperature, precipitation, humidity) and
    dengue case spikes (anticipation-hub.org, "Linking early warnings to early action:
    compound hydrometeorological hazards and dengue outbreaks", 21 Jun 2021, incl.
    contribution from Ana Marie Dizon, CARE Philippines/START Network). Not confirmed
    as the formal decision input for either the 2022 or 2024 alert.
visibility: public
---

# START — Philippines epidemic (dengue outbreak anticipation)

## Summary
Not a standing pre-arranged framework but Start Network's discretionary **Start Fund
Anticipation** facility applied twice to disease-outbreak risk in the Philippines: a
member agency raises an alert, and the Start Fund Committee votes a proposal into funding
within days. Hub-listed for 2022 (implemented by Humanity & Inclusion) and 2024
(implemented by a Start Network-funded consortium). The best-documented instance is 2024
Alert 850, raised after Super Typhoon Carina raised dengue and Mpox risk in Metro Manila.

## Trigger
No fixed parametric threshold — a member agency proposes an alert when conditions and
case data point to imminent outbreak risk, and the Start Fund Committee decides. For
Alert 850 (2024): Super Typhoon Carina (Jul 2024) created conditions conducive to a
dengue outbreak, evidenced by 503 cumulative dengue cases recorded in Malabon between
January and August 2024; the Committee judged that the existing typhoon response wasn't
prioritising disease prevention and unanimously funded a dedicated consortium proposal.
An earlier (2021) Start Network/World Vision R&D effort built a Dengue Risk Analysis Tool
for Metro Manila cities finding a ~3-month lag between weather conditions and case
spikes, but it is not confirmed as the formal input to either activation (see
`extra.background`).

## Funding & scope
2024 Alert 850: **GBP 300,000** (recommended = allocated = total) to a consortium of
Relief International, Humanity & Inclusion, World Vision and local partner PhilRADS
(project name IADOR), covering Malabon, Manila and San Mateo (Rizal), coordinating with
local government units. World Vision's own slice reached 555 families in two Malabon
barangays with hygiene kits/mosquito nets/water-purification tablets, plus
cash-for-community-cleaning across five Malabon barangays. No funding or scope detail
found for the 2022 activation. See `extra.schema_strain` for why top-level
`prearranged_funding_usd`/`target_people` are left null rather than guessed.

## Activations
- **2022** — Hub-listed disease-outbreak anticipation alert implemented by Humanity &
  Inclusion; no further public detail found.
- **7 Sep 2024** — Start Fund Alert 850, post-Typhoon-Carina dengue/Mpox response
  (IADOR): GBP 300,000 to a four-partner consortium; World Vision distributed hygiene
  kits and mosquito nets to 555 families in Malabon and ran cash-for-cleaning across
  five barangays.

## Sources
- **Authoritative for 2024:** [World Vision Philippines — Malabon families get hygiene kits, mosquito nets](https://www.worldvision.org.ph/malabon-families-get-hygiene-kits-mosquito-nets-to-combat-dengue-other-diseases/) (13 Sep 2024)
- [Start Network — Alert 850, Philippines (Anticipation of disease outbreak)](https://startnetwork.org/funds/global-start-fund/alerts/850-philippines-anticipation-disease-outbreak)
- [Start Network — RFP, impact assessment of Alert 850](https://startnetwork.org/about/current-vacancies/rfp-impact-assessment-start-fund-anticipation-alert-philippines-anticipation-disease-outbreak)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record; source of the 2022/2024 hub captions and the unreconciled funding/target figures — see `extra.schema_strain`)
- [Anticipation Hub — Linking early warnings to early action: compound hydrometeorological hazards and dengue outbreaks](https://www.anticipation-hub.org/news/linking-early-warnings-to-early-action-compound-hydrometeorologiacal-hazards-and-dengue-outbreaks) (21 Jun 2021, background on the Dengue Risk Analysis Tool)
