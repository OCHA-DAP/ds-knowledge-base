---
content_type: framework-external
framework: ifrc-phl-flood
org: IFRC
country_iso3: PHL
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  GloFAS forecast trigger, checked independently for 4 river basins. Fires ~3 days before
  the flood when GloFAS predicts ≥70% probability of at least a 1-in-5-year return-period
  flood in a basin; the modelled flood extent (ECMWF rainfall + basin-specific hydraulic
  models) is then overlaid on the rice-crop map to select municipalities to act in — a
  lower crop-impact threshold (~30%) applies in the Panay basin, a higher one (~50%) in the
  other three.
data_sources: [GloFAS, ECMWF]
prearranged_funding_usd: 283850
funding_by_source: {DREF: 283850}
target_people: 7500
framework_doc: https://reliefweb.int/report/philippines/philippines-floods-early-action-protocol-summary-eap2021ph02
framework_doc_date: 2021-04-09
sources:
- https://reliefweb.int/report/philippines/philippines-floods-early-action-protocol-summary-eap2021ph02
- https://reliefweb.int/report/philippines/philippines-floods-early-action-protocol-annual-report-eap2021ph02
- https://www.anticipation-hub.org/global-overview/countries/philippines/forecast-based-financing-fbf-in-the-philippines
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/philippines
- https://www.anticipation-hub.org/Documents/Briefing_Sheets_and_Fact_Sheets/Flood_EAP_-_Final.pdf
- https://www.early-action-reap.org/reap-anticipatory-action-enabling-environment-case-studies-philippines
- https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-18'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Philippine Red Cross] [German Red Cross] [Finnish Red Cross]'
  - '2023: Flood (IFRC) [Philippine Red Cross]'
  - '2024: Flood (IFRC) [Philippine Red Cross]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - Philippine Red Cross
  eap_no: EAP2021PH02
  partners: German Red Cross (technical support and, via the German Federal Foreign
    Office, funding; partnership with PRC since 2017), Finnish Red Cross
  funding_chf: >-
    The EAP2021PH02 summary states CHF 234,809 total DREF Forecast-based Action (FbA)
    allocation (CHF 79,215 immediate readiness/pre-positioning + CHF 157,751 automatic
    on-trigger); the Anticipation Hub inventory figure used above (US$283,850) is not a
    straight conversion of that CHF figure at any single plausible rate, so may reflect a
    later top-up (a further CHF 25,298.80 IFRC transfer to PRC is documented for 2024) or a
    different snapshot date.
  basins: >-
    Four river basins, one PRC chapter cluster each (8 chapters total): Cagayan (Cagayan,
    Isabela provinces), Bicol (Albay, Camarines Sur), Agusan (Agusan del Norte, Agusan del
    Sur, Davao de Oro/Compostela Valley), and Panay (Capiz). Sources describe these as
    spanning "four regions — North Luzon, Bicol, Eastern Visayas and Mindanao"; the Panay/
    Capiz basin is administratively Western Visayas (region VI), not Eastern Visayas — kept
    as sourced rather than corrected, since no source resolves the discrepancy.
  no_activation_found: >-
    The EAP2021PH02 annual report (covering 2021-2024) describes only readiness activity —
    2021 procurement via German Red Cross; a pause in 2022-2023 while PRC focused on Typhoon
    Odette response; late-2023 provincial meetings to refresh beneficiary data; a further
    IFRC funding transfer to PRC in 2024 — with no mention of the GloFAS trigger firing or
    an early-action tranche being released. No IFRC GO operation number (MDRPH…) specific to
    this flood EAP was found in public sources either (unlike the parallel typhoon EAP,
    which has MDRPH049 and MDRPH055) — search of the IFRC GO appeals API for PHL "flood"
    appeals surfaces only ordinary post-event DREF operations (MDRPH028, MDRPH053, MDRPH054),
    not an EAP activation. Recorded as no confirmed activation rather than assumed silent one.
  schema_strain: >-
    No operation number (MDRPH…) confirmed for this EAP (see `extra.no_activation_found`);
    no fixed `valid_until` date found (the original pilot ran Aug 2017-Dec 2022 per one
    source, but EAP2021PH02 itself states no expiry and the Hub still lists it active
    through 2024). The primary EAP2021PH02 PDF could not be fetched directly (ReliefWeb
    blocks automated fetches); details above are drawn from search-engine-indexed excerpts
    of that document plus the EAP2021PH02 annual report and Hub secondary sources.
  implementing_partners_note: >-
    8 PRC chapters trained across the 4 basins; the Hub's 2022 caption additionally credits
    the Finnish Red Cross as a partner that year (role not detailed in sources found).
visibility: public
---

# IFRC — Philippines flood EAP

## Summary
The Philippine Red Cross (PRC) runs a Flood Early Action Protocol (EAP2021PH02, published
9 April 2021), developed with the German Red Cross since 2017 and funded through IFRC's DREF
Forecast-based Action (FbA) mechanism. It covers four river basins — Cagayan, Bicol, Agusan
and Panay — across eight PRC chapters, targeting roughly 7,500 people with early harvesting,
livestock/asset evacuation and urban-microenterprise relocation ahead of forecast flooding.
It is a separate PRC-owned instrument, distinct from OCHA/CERF's Philippines framework, which
covers tropical cyclones, not floods (see [`frameworks/phl-storms`](../../frameworks/phl-storms)).

## Trigger
A GloFAS-based forecast trigger, evaluated independently per basin: it fires roughly 3 days
before the flood when GloFAS forecasts ≥70% probability of at least a 1-in-5-year
return-period flood, using ECMWF rainfall input and basin-specific hydraulic/hydrological
models (HEC-RAS, HEC-HMS, Flo2D or RRI, depending on the basin) to model the flood extent.
That modelled extent is overlaid on the rice-crop map to identify which municipalities to
act in — the design uses a lower crop-impact threshold (~30%) in the Panay basin and a
higher one (~50%) in the other three basins, in at least one municipality. Early actions:
early harvesting of crops or fish, livestock and asset evacuation, and temporary relocation
of urban micro-enterprises for urban flooding.

## Funding & scope
DREF FbA-funded. Anticipation Hub inventory figure: US$283,850 pre-arranged, ~7,500 people
targeted. The EAP2021PH02 summary document itself states CHF 234,809 (CHF 79,215 readiness
+ CHF 157,751 automatic on-trigger) — see `extra.funding_chf` for why the two figures don't
reconcile cleanly. Geographic scope: 8 PRC chapters across the Cagayan (Cagayan, Isabela),
Bicol (Albay, Camarines Sur), Agusan (Agusan del Norte, Agusan del Sur, Davao de Oro) and
Panay (Capiz) river basins.

## Activations
None confirmed. The EAP2021PH02 annual report (2021-2024) describes readiness activity only
— initial procurement (2021), a pause during the PRC's Typhoon Odette response (2022-2023),
provincial beneficiary-data meetings (late 2023), and a further IFRC funding transfer (2024)
— with no record of the GloFAS trigger firing or an early-action tranche being disbursed.
No IFRC GO operation number specific to this flood EAP was found either. See
`extra.no_activation_found`.

## Sources
- **Authoritative:** [EAP2021PH02 summary, published 9 Apr 2021](https://reliefweb.int/report/philippines/philippines-floods-early-action-protocol-summary-eap2021ph02) (PDF not directly fetchable; drawn from indexed excerpts)
- [EAP2021PH02 annual report](https://reliefweb.int/report/philippines/philippines-floods-early-action-protocol-annual-report-eap2021ph02) (readiness activity by year, 2021-2024)
- [Anticipation Hub — Philippines FbF country page](https://www.anticipation-hub.org/global-overview/countries/philippines/forecast-based-financing-fbf-in-the-philippines)
- [Anticipation Hub — anticipatory action in the Philippines](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/philippines)
- [Flood EAP pocket version for PRC chapters (PDF)](https://www.anticipation-hub.org/Documents/Briefing_Sheets_and_Fact_Sheets/Flood_EAP_-_Final.pdf)
- [REAP — Philippines enabling-environment case study](https://www.early-action-reap.org/reap-anticipatory-action-enabling-environment-case-studies-philippines)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Related OCHA/CERF framework (different hazard, tropical cyclone): [`frameworks/phl-storms`](../../frameworks/phl-storms)
