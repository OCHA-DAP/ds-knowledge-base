---
content_type: framework-external
framework: ifrc-ecu-vulcano-ash
org: IFRC
country_iso3: ECU
hazard: vulcano-ash
status: active
valid_until: 2028-10-31
trigger_summary: >-
  IGEPN (Ecuador's geophysical institute) volcanic ash dispersion/deposition forecasts
  for six priority volcanoes (very-high-threat: Tungurahua, Cotopaxi, Guagua Pichincha;
  high-threat: Reventador, Cayambe, Sangay) trigger early action when forecast ashfall
  reaches damaging depths in specific communities. The only documented real-world trigger
  (Sangay, Sept 2020) used an IGEPN forecast of 1-30mm ashfall across four provinces, with
  cash assistance released in communities forecast to receive >10mm. The current (2023)
  EAP's codified numeric threshold/lead time text was not accessible in public sources
  found — see `extra.schema_strain`.
data_sources: [IGEPN]
prearranged_funding_usd: 460521
funding_by_source: {DREF-anticipatory: 460521}
target_people: 10000
framework_doc: /download/file-3671
framework_doc_date: 2023-09-26
sources:
  - https://www.anticipation-hub.org/download/file-3671
  - https://reliefweb.int/report/ecuador/ecuador-volcanic-ash-early-action-protocol-summary-eap-no-eap2023ec03-operation-no-mdrec024-26-september-2023
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDREC024
  - https://reliefweb.int/report/ecuador/ecuador-volcanic-ash-early-action-protocol-annual-report-eap-no-eap2023ec03-operation-no-mdrec024-march-2025
  - https://reliefweb.int/report/ecuador/forecast-based-early-action-triggered-ecuador-volcanic-ash-dispersion-sangay-volcano
  - https://www.forecast-based-financing.org/2020/09/21/early-actions-will-support-ecuadorian-families-to-face-volcanic-ash-fall/
  - https://www.climatecentre.org/news/1328/ecuador-red-cross-assists-residents-threatened-by-volcanic-ash
  - https://reliefweb.int/report/ecuador/ecuador-volcanic-ashfall-early-action-final-report-early-action-phase-eap2019ec01
  - https://reliefweb.int/report/ecuador/ecuador-volcanic-eruption-dref-operation-mdrec016
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2020-09-20
    url: https://www.forecast-based-financing.org/2020/09/21/early-actions-will-support-ecuadorian-families-to-face-volcanic-ash-fall/
    note: >-
      Sangay volcano eruption — activated under the first-generation EAP2019EC01. IGEPN
      forecast 1-30mm ashfall across Chimborazo, Bolívar, Guayas and Manabí provinces;
      ~1,000 rural families received health kits (N95 masks, eye protection), animal/crop
      protection kits (tarpaulins), and cash transfers (~US$200 via IFRC debit card in
      communities forecast >10mm ashfall). A complementary (non-EAP) DREF operation
      MDREC016 followed in Oct 2020 for the broader emergency response.
last_checked: '2026-07-17'
extra:
  hub_captions:
  - '2023: Volcanic ash (IFRC) [Ecuadorian Red Cross]'
  - '2024: Volcanic ash (IFRC) [Ecuadorian Red Cross]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Ecuadorian Red Cross
  eap_no: EAP2023EC03 (current) — supersedes first-generation EAP2019EC01 (approved
    April 2019, budget CHF 246,586).
  operation_no: MDREC024 (current appeal, active 2023-10-09 to 2028-10-31) / MDREC016
    (Oct 2020 complementary DREF operation for the Sangay response, not the EAP tranche
    itself).
  generations: EAP2019EC01 (Apr 2019, CHF 246,586) → EAP2023EC03 (26 Sept 2023, CHF
    454,166, runs to 2028-10-31).
  funding_chf: "CHF 454,166 pre-arranged under EAP2023EC03: CHF 313,586 readiness/
    prepositioning + CHF 140,580 early-action tranche. IFRC GO reports this as USD
    460,521, fully funded. The Anticipation Hub inventory record (used for the original
    stub) listed USD 522,725 instead — discrepancy not reconciled, likely a different
    CHF/USD conversion date; GO API figure used here as the more current source."
  volcanoes: >-
    6 priority volcanoes (of 24 assessed) per Bernard et al. 2018 criteria: very-high-
    threat — Tungurahua, Cotopaxi, Guagua Pichincha; high-threat — Reventador, Cayambe,
    Sangay.
  partners: Ecuadorian Red Cross (CRE), CRA, RCRC Climate Centre, IGEPN, INAMHI,
    Secretariat of Risk Management, local GADs
  schema_strain: >-
    No public evidence found of an activation under the current (2023-generation)
    EAP2023EC03/MDREC024 — the only confirmed real activation is the Sept 2020 Sangay
    event under the prior EAP2019EC01. The exact numeric ashfall threshold/lead time as
    codified in the current EAP text could not be fetched (ReliefWeb blocks automated
    fetches with 403; the Anticipation Hub PDF mirror returned metadata only, not body
    text) — the recorded trigger detail is drawn from the 2020 activation reporting
    instead, which may not exactly match the current EAP's codified numbers.
visibility: public
---

# IFRC — Ecuador vulcano ash

## Summary
The Ecuadorian Red Cross's (ERC/CRE) volcanic-ash Early Action Protocol, validated by
IFRC and pre-financed by the DREF Anticipatory Pillar (current operation MDREC024,
EAP2023EC03, active through 2028). Now in its second generation (first approved 2019),
it covers six priority volcanoes and uses IGEPN ash-dispersion/deposition forecasts to
trigger health, livelihood-protection and cash assistance for ~10,000 people in
communities forecast to receive damaging ashfall.

## Trigger
IGEPN (Instituto Geofísico, Ecuador's geophysical monitoring institute) issues ash
dispersion/deposition forecasts for six volcanoes ranked by threat level — very-high:
Tungurahua, Cotopaxi, Guagua Pichincha; high: Reventador, Cayambe, Sangay — selected from
24 assessed volcanoes using the Bernard et al. (2018) prioritization criteria. When a
forecast shows damaging ashfall reaching specific communities, the EAP releases
pre-defined early actions (health/livelihood kits, cash transfers). The only documented
real trigger event (Sangay, 20 Sept 2020, under the prior-generation EAP2019EC01) used an
IGEPN forecast of 1-30mm ashfall across four provinces, with cash assistance specifically
tied to communities forecast >10mm. The current (2023) EAP's own codified threshold and
lead-time figures were not accessible in the sources found — see `extra.schema_strain`.

## Funding & scope
CHF 454,166 pre-arranged under the current EAP2023EC03 (CHF 313,586 readiness/
prepositioning + CHF 140,580 early-action tranche) — reported by IFRC GO as USD 460,521,
fully funded, for ~10,000 people. The prior EAP2019EC01 (2019-2023) carried a smaller
budget of CHF 246,586. Designed with the Austrian Red Cross (CRA), the RCRC Climate
Centre, IGEPN, INAMHI, Ecuador's Secretariat of Risk Management and local GADs.

## Activations
- **20 Sept 2020 — Sangay volcano.** The one confirmed real activation, under the
  first-generation EAP2019EC01. IGEPN forecast 1-30mm ashfall across Chimborazo, Bolívar,
  Guayas and Manabí provinces; ~1,000 rural families received health kits, animal/crop
  protection kits, and cash transfers (~US$200 in the hardest-hit, >10mm-forecast
  communities). A separate, complementary DREF operation (MDREC016) followed in October
  2020 for the wider emergency response — not part of the EAP tranche itself.

No activation has been found in public reporting under the current (2023-generation)
EAP2023EC03/MDREC024, despite Hub inventory listings for both 2023 and 2024.

## Sources
- **Authoritative:** [EAP summary EAP2023EC03/MDREC024, 26 Sept 2023](https://reliefweb.int/report/ecuador/ecuador-volcanic-ash-early-action-protocol-summary-eap-no-eap2023ec03-operation-no-mdrec024-26-september-2023) ([Hub PDF mirror](https://www.anticipation-hub.org/download/file-3671))
- [IFRC GO — MDREC024](https://goadmin.ifrc.org/api/v2/appeal/?code=MDREC024) (machine-readable status/budget — $460,521 fully funded, 10,000 beneficiaries, active 2023-10-09 to 2028-10-31)
- [Annual report, March 2025 (EAP2023EC03/MDREC024)](https://reliefweb.int/report/ecuador/ecuador-volcanic-ash-early-action-protocol-annual-report-eap-no-eap2023ec03-operation-no-mdrec024-march-2025)
- [Sangay activation notification, Sept 2020](https://reliefweb.int/report/ecuador/forecast-based-early-action-triggered-ecuador-volcanic-ash-dispersion-sangay-volcano) · [Forecast-based Financing write-up](https://www.forecast-based-financing.org/2020/09/21/early-actions-will-support-ecuadorian-families-to-face-volcanic-ash-fall/) · [RCRC Climate Centre write-up](https://www.climatecentre.org/news/1328/ecuador-red-cross-assists-residents-threatened-by-volcanic-ash)
- [First-generation EAP2019EC01 final report](https://reliefweb.int/report/ecuador/ecuador-volcanic-ashfall-early-action-final-report-early-action-phase-eap2019ec01) · [complementary DREF operation MDREC016](https://reliefweb.int/report/ecuador/ecuador-volcanic-eruption-dref-operation-mdrec016)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
