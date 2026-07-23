---
content_type: framework-external
framework: fao-moz-drought
org: FAO
country_iso3: MOZ
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  ENSO seasonal forecasts confirming El Niño conditions for the Oct-May agricultural
  season (as in 2023/24) lead the Government of Mozambique to approve an Anticipatory
  Action Plan for drought in critical districts (first Gaza province, later extended);
  FAO then releases pre-arranged agricultural inputs — mainly e-vouchers for
  drought-tolerant/early-maturing seeds and tools, plus some cash transfers — ahead of
  planting. No numeric ENSO/SPI threshold or lead-time-in-days is stated publicly; this
  is a separate, government-declaration-based trigger from WFP's own SPI ≤ -1
  forecast-based-financing system running in the same country (see
  `external-frameworks/wfp/moz-drought.md`).
data_sources: [ENSO]
prearranged_funding_usd: 1000000
funding_by_source: {}
target_people: 40000
framework_doc: https://www.fao.org/mozambique/news/details/el-ni%C3%B1o-response--empowering-farmers-to-rebuild-their-livelihoods/en
framework_doc_date: '2025-03-03'
sources:
- https://www.fao.org/mozambique/news/details/el-ni%C3%B1o-response--empowering-farmers-to-rebuild-their-livelihoods/en
- https://www.fao.org/mozambique/news/details/seeds--cash--and-preparedness--fao-s-anticipatory-actions/en
- https://reliefweb.int/report/mozambique/fao-provides-seeds-and-tools-main-agricultural-season-gaza-and-cabo-delgado-provinces-anticipatory-actions-protect-el-nino-and-conflict-affected-farmers
- https://www.anticipation-hub.org/global-overview/countries/mozambique
- https://www.fao.org/emergencies/resources-repository/publications/MOZ/1/en
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2023-2024
  url: https://reliefweb.int/report/mozambique/fao-provides-seeds-and-tools-main-agricultural-season-gaza-and-cabo-delgado-provinces-anticipatory-actions-protect-el-nino-and-conflict-affected-farmers
  note: >-
    2023/24 El Niño season. Government of Mozambique approved a drought Anticipatory
    Action Plan for Gaza province; FAO's first reported tranche (Jan 2024) reached 2,500
    households (12,500 people) in Mabalane, Mapai and Massingir via e-voucher seeds/tools
    ahead of the main agricultural season. FAO's own March 2025 retrospective reports a
    much larger final reach for the same 2023/24 response: 31,000+ households across
    Maríngue (Sofala), Tambara/Guro/Macossa (Manica), Changara (Tete),
    Panda/Mabote/Funhalouro (Inhambane) and Chigubo/Massangena/Guijá/Mapai/Massingir/
    Chicualacuala (Gaza) — combining a 6,990-farmer e-voucher scheme in Maríngue with
    in-kind seed/tool distribution to 24,100 households in the other districts.
last_checked: '2026-07-23'
extra:
  hub_captions:
  - '2023: Drought (FAO) [FAO]'
  - '2024: Drought (FAO) [FAO]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - FAO
  coordination: >-
    Not a component of an OCHA/CERF collective framework: no `frameworks/moz-drought`
    OCHA page exists (checked — only `frameworks/moz-cholera` and
    `frameworks/moz-cyclones` cover Mozambique). FAO publishes and runs this
    independently.
  related_but_separate: >-
    WFP runs its own, separate drought anticipatory action framework in Mozambique
    (SPI ≤ -1 forecast-based-financing "trigger menu" on ECMWF seasonal forecasts,
    US$12M/658,000 people) — see `external-frameworks/wfp/moz-drought.md`. No public
    source describes coordination or a shared trigger between the FAO and WFP
    frameworks; they appear to run in parallel.
  schema_strain: >-
    (1) No numeric ENSO/SPI threshold or lead-time-in-days found for FAO's own drought
    protocol — distinct from WFP's SPI-based system in the same country, which does
    publish a numeric threshold. (2) The Anticipation Hub's current aggregate figure
    (US$1,000,000 / 40,000 people) is far smaller than the ~31,000 households (likely
    150,000+ people at typical household size) FAO's own March 2025 article reports
    reaching in the 2023/24 response alone; unclear whether the Hub figure is a stale
    snapshot, a single funding stream, or a planning target that was later exceeded.
    (3) An FAO project record found in FAO's Mozambique publications repository —
    OSRO/MOZ/141/BEL, Kingdom of Belgium, US$500,000, "Emergency assistance to
    vulnerable smallholder farmers affected by drought caused by the El Niño phenomenon
    in Tete Province" (no dates given) — may or may not be the anticipatory-action
    funding vehicle; its title reads as post-impact response rather than anticipatory,
    so it is not used in `funding_by_source`. (4) The Jan 2024 ReliefWeb report bundles
    a Cabo Delgado component (24,600 households / 123,000 people) attributed to
    conflict displacement, not drought — excluded from this page's activation figures.
visibility: public
---

# FAO — Mozambique drought

## Summary
FAO runs a drought anticipatory action framework in Mozambique triggered by seasonal
(ENSO) forecasts and formalized through government-approved Anticipatory Action Plans,
releasing pre-arranged agricultural inputs — chiefly e-vouchers for seeds and tools,
occasionally cash — to smallholder farmers ahead of the main agricultural season. It ran
in the Anticipation Hub's inventory for 2023 and 2024, corresponding to the 2023/24
El Niño-driven drought. It is independent of, and runs in parallel with, WFP's own
SPI-based drought anticipatory action system in the same country.

## Trigger
ENSO seasonal forecasts confirming El Niño conditions for the Oct-May agricultural
season trigger the process: the Government of Mozambique approves an Anticipatory
Action Plan for drought in specific at-risk districts (in 2023/24, starting with Gaza
province), and FAO then distributes pre-arranged agricultural inputs — mainly e-vouchers
redeemable with local agro-dealers for drought-tolerant and early-maturing seeds plus
tools, and in-kind seed/tool kits — timed to arrive before planting. No public document
gives a numeric ENSO/SPI threshold or a lead-time-in-days for FAO's own protocol; this
differs from WFP's separate Mozambique drought system, which does publish a numeric
SPI ≤ -1 probability threshold.

## Funding & scope
The Anticipation Hub's country page lists a current FAO Mozambique drought framework of
US$1,000,000 targeting 40,000 people. No clean per-donor breakdown was found for that
aggregate figure, so `funding_by_source` is left empty. A separate FAO project record,
OSRO/MOZ/141/BEL (Kingdom of Belgium, US$500,000, "Emergency assistance to vulnerable
smallholder farmers affected by drought caused by the El Niño phenomenon in Tete
Province"), may relate to this framework but its title suggests post-impact response
rather than anticipatory action, so it is noted but not asserted as the AA funding
source (see `extra.schema_strain`).

## Activations
- **2023/24 El Niño season.** The Government of Mozambique approved a drought
  Anticipatory Action Plan for Gaza province. FAO's first reported tranche (reported
  January 2024) reached 2,500 households (12,500 people) in Mabalane, Mapai and
  Massingir with seeds and tools via e-voucher. FAO's own March 2025 retrospective
  reports a much larger final reach for the same response: over 31,000 farming
  households across Maríngue (Sofala), Tambara/Guro/Macossa (Manica), Changara (Tete),
  Panda/Mabote/Funhalouro (Inhambane) and six Gaza districts, combining a 6,990-farmer
  e-voucher scheme in Maríngue with in-kind distribution (231,950 kg maize, 110,500 kg
  sorghum, plus other seeds and 9,615 hoes) to 24,100 households in the remaining
  districts, delivered ahead of the planting season.
- The same January 2024 report also describes a Cabo Delgado component (24,600
  households / 123,000 people) — attributed to conflict displacement, not drought, and
  excluded here.
- No activations found before 2023/24 or after the 2024 Hub listing.

## Sources
- **Authoritative:** [FAO Mozambique — "El Niño Response: Empowering Farmers to Rebuild their Lives"](https://www.fao.org/mozambique/news/details/el-ni%C3%B1o-response--empowering-farmers-to-rebuild-their-livelihoods/en) (FAO, 3 Mar 2025) — fullest account of the 2023/24 drought response
- [FAO Mozambique — "Seeds, Cash, and Preparedness: FAO's Anticipatory Actions"](https://www.fao.org/mozambique/news/details/seeds--cash--and-preparedness--fao-s-anticipatory-actions/en) (FAO, 2 Mar 2025) — describes FAO's general AA approach in Mozambique, but its featured case (Machanga/Maganja da Costa, 2024/25) is the separate La Niña **floods** project (OSRO/MOZ/142/GER), not this drought framework
- [FAO provides seeds and tools ... Gaza and Cabo Delgado provinces (ReliefWeb)](https://reliefweb.int/report/mozambique/fao-provides-seeds-and-tools-main-agricultural-season-gaza-and-cabo-delgado-provinces-anticipatory-actions-protect-el-nino-and-conflict-affected-farmers) (FAO/ReliefWeb, 9 Jan 2024)
- [Anticipation Hub — Mozambique country overview](https://www.anticipation-hub.org/global-overview/countries/mozambique) (current FAO budget/target-people figures)
- [FAO emergencies resources repository — Mozambique](https://www.fao.org/emergencies/resources-repository/publications/MOZ/1/en) (project funding records, incl. OSRO/MOZ/141/BEL, OSRO/MOZ/142/GER)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
