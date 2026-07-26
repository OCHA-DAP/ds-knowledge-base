---
content_type: framework-external
framework: wfp-moz-drought
org: WFP
country_iso3: MOZ
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  A forecast-based-financing "trigger menu": ECMWF's 7-month seasonal rainfall ensemble
  forecast is used to estimate the probability that the Standardized Precipitation Index
  (SPI, 2- and 3-month accumulations) will fall to or below a severe-drought threshold
  (SPI ≤ -1, roughly a 1-in-6-7-year event) during the Oct-May rainy season; probability
  thresholds are optimized per district, forecast month and SPI window. A two-stage
  "Ready, Set & Go" design (readiness alert, then a confirmed activation ~1 season later)
  gives up to ~3 months' lead time, vs ~2 months for a single-alert design; readiness
  alerts can issue as early as May for southern districts. The general trigger menu
  covers an estimated 76% of Mozambique's districts across both rainy-season windows
  (87% in the first window alone); a stricter "emergency" menu covers 59-66%.
data_sources: [ECMWF, INAM]
prearranged_funding_usd: 12000000
funding_by_source: {}
target_people: 658000
framework_doc: /global-overview/countries/mozambique/scaling-up-drought-anticipatory-action-for-food-security-in-mozambique-wfp
framework_doc_date: null
sources:
  - https://www.anticipation-hub.org/global-overview/countries/mozambique/scaling-up-drought-anticipatory-action-for-food-security-in-mozambique-wfp
  - https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/mozambique
  - https://www.anticipation-hub.org/news/integrating-shock-responsive-social-protection-into-anticipatory-action-protocols-ahead-of-a-drought-in-mozambique
  - https://www.sciencedirect.com/science/article/pii/S2405880723000055
  - https://nhess.copernicus.org/articles/24/4661/2024/
  - https://www.wfp.org/news/wfp-races-cushion-people-looming-drought-southern-africa-largest-cash-payout-date
  - https://reliefweb.int/report/mozambique/wfp-mozambique-country-brief-april-2024
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2023-09
    url: https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/mozambique
    note: >-
      2023/24 El Niño season: WFP and the Southern-Africa AA programme (Lesotho,
      Madagascar, Mozambique, Zimbabwe) released a combined US$12.8M (Germany, EU, Norway)
      for 550,000+ people region-wide from Sept 2023; the Hub's Mozambique-specific tally
      for the year records 518,795 people reached and US$10,182,259 invested (early
      warning SMS, drought-tolerant seeds, anticipatory cash, safe-water support).
  - date: 2024-04
    url: https://reliefweb.int/report/mozambique/wfp-mozambique-country-brief-april-2024
    note: >-
      Continuation of the same 2023/24 El Niño season response: first cycle of
      anticipatory cash transfers concluded in Caia and Chemba (Sofala) and Marara and
      Changara (Tete) — ~4,000 households via commodity vouchers or mobile money,
      coordinated between INGD and INAS. The Hub records the same annual totals
      (518,795 people / US$10,182,259) against the 2024 map entry, which may be a
      re-statement of the 2023/24-season figures rather than a distinct second event
      (see `extra.schema_strain`).
last_checked: '2026-07-20'
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
  origin: >-
    Piloted under the Multi-Country Programme on Scaling-up Anticipatory Action for Food
    Security (MCP-AA4FS Phase I, 2019-2022), NORAD-funded, with WFP MoUs (from 2020) with
    Mozambique's national met service (INAM), disaster-management institute (INGD) and
    agriculture ministry (MADER), plus SETSAN and the social-protection institute
    INAS/MGCAS. Initial pilot in 4 districts — Chibuto and Guijá (Gaza), Marara and
    Changara (Tete) — later described as a government-led plan covering 11 pilot
    districts; ongoing support also from the EU, ECHO, DEVCO, Norway and the WFP
    Innovations Accelerator.
  funding_note: >-
    No clean per-donor breakdown found for the current US$12M/658,000-person framework
    total (Hub country page); it blends the original NORAD-funded pilot with later
    EU/ECHO/DEVCO/Norway support and the Germany/EU/Norway-funded 2023/24 El Niño
    regional top-up. `funding_by_source` left empty rather than guessing a split.
  related_but_separate: >-
    FAO runs its own, separate drought AA framework in Mozambique (per the same Hub
    country page: ~40,000 people, US$1M) — not part of this WFP framework and not an
    OCHA/CERF collective (no `frameworks/moz-drought` OCHA page exists to cross-link).
  schema_strain: >-
    (1) The Hub global-map API's stub-derived figures (US$8M / 200,000 people, as
    originally captured in this page) differ from the Hub country-overview page's current
    totals (US$12M / 658,000) — likely different snapshot years of the same evolving
    programme; this rewrite uses the country-overview figures as the more current source.
    (2) No Mozambique-specific numeric SPI probability threshold (vs the general "SPI ≤
    -1" severe-drought definition) or per-district trigger values were found in public
    sources — the optimized per-district/month thresholds are described as existing but
    not tabulated publicly. (3) `framework_doc_date` is null: the Hub project page has no
    stated publish date (the underlying MCP-AA4FS Phase I project ran Sept 2019-Dec 2022).
visibility: public
---

# WFP — Mozambique drought

## Summary
WFP's drought anticipatory action programme in Mozambique, developed with national
partners (INAM, INGD, MADER, SETSAN, INAS/MGCAS) since 2019 under the NORAD-funded
MCP-AA4FS Phase I pilot and now described by the Anticipation Hub as a government-led
plan. It runs a forecast-based-financing "trigger menu" over the Oct-May rainy season and
has been activated at least twice (2023 and continuing into 2024) as part of the region-
wide response to El Niño-driven drought across Southern Africa.

## Trigger
A forecast-based-financing design: ECMWF's 7-month seasonal rainfall ensemble forecast is
converted into the probability that the Standardized Precipitation Index (SPI, 2- and
3-month accumulations) will fall to or below a severe-drought threshold (SPI ≤ -1, an
event expected roughly once every 6-7 years) at some point in the Oct-May rainy season.
Probability trigger values are optimized per district, forecast month, and SPI window
("trigger menu"), rather than a single fixed number nationwide. A two-stage "Ready, Set &
Go" double-confirmation design (a readiness alert followed by a confirmed go/no-go) gives
up to ~3 months of lead time — readiness alerts can issue as early as May for southern
districts — versus ~2 months for a single-alert design. Coverage varies by menu: the
general trigger menu reaches an estimated 76% of Mozambique's districts across both
rainy-season windows (87% counting only the first window); a stricter emergency menu
covers 59-66%. No public source gives the specific numeric probability threshold used for
any one district.

## Funding & scope
The Anticipation Hub's country page lists a current budget of US$12,000,000 targeting
658,000 people. That figure spans several funding streams rather than one grant: the
original NORAD-funded MCP-AA4FS Phase I pilot (2019-2022, 4 districts: Chibuto and Guijá
in Gaza, Marara and Changara in Tete), continued EU/ECHO/DEVCO/Norway support as the
programme expanded to a government-led plan covering 11 pilot districts, and the
Germany/EU/Norway-funded regional top-up for the 2023/24 El Niño season (a combined
US$12.8M released across Lesotho, Madagascar, Mozambique and Zimbabwe from September
2023). No source gives a clean per-donor USD split, so `funding_by_source` is left empty.
An earlier Hub inventory snapshot for this page recorded US$8,000,000 / 200,000 people —
likely an earlier point in the same programme's growth (see `extra.schema_strain`).

## Activations
- **2023/24 El Niño season (from Sept 2023).** Regional AA activation across Lesotho,
  Madagascar, Mozambique and Zimbabwe; Mozambique-specific Hub totals: 518,795 people
  reached, US$10,182,259 invested in early-warning SMS, drought-tolerant seeds,
  anticipatory cash transfers, and safe-water support.
- **April 2024.** First cycle of anticipatory cash transfers concluded in Caia and Chemba
  (Sofala province) and Marara and Changara (Tete province) — about 4,000 households
  reached via commodity vouchers or mobile-money transfers, coordinated between INGD and
  INAS as part of the same 2023/24-season response (which also covered districts in
  Gaza). The Hub's 2024 map entry repeats the same annual totals as 2023; this may be a
  re-statement of the season's cumulative figures rather than a second distinct event.

No non-activation ("trigger not met") events were found in public reporting.

## Sources
- **Authoritative:** [Anticipation Hub — Mozambique framework page](https://www.anticipation-hub.org/global-overview/countries/mozambique/scaling-up-drought-anticipatory-action-for-food-security-in-mozambique-wfp)
- [Anticipation Hub — Mozambique country overview](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/mozambique) (current budget/target-people, 2023 & 2024 activation totals)
- [Anticipation Hub news, Jan 2022 — social protection integration, pilot districts](https://www.anticipation-hub.org/news/integrating-shock-responsive-social-protection-into-anticipatory-action-protocols-ahead-of-a-drought-in-mozambique)
- [Gubbels et al., "Forecasting, thresholds, and triggers: Towards developing a Forecast-based Financing system for droughts in Mozambique," Climate Services (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2405880723000055)
- ["Ready, Set & Go! An anticipatory action system against droughts," NHESS 2024](https://nhess.copernicus.org/articles/24/4661/2024/) (SPI threshold, lead-time, district-coverage figures)
- [WFP news, 4 Sept 2023 — regional El Niño cash payout](https://www.wfp.org/news/wfp-races-cushion-people-looming-drought-southern-africa-largest-cash-payout-date)
- [WFP Mozambique Country Brief, April 2024 (ReliefWeb)](https://reliefweb.int/report/mozambique/wfp-mozambique-country-brief-april-2024)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
