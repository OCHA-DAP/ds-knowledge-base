---
content_type: framework-external
framework: ifrc-hnd-drought
org: IFRC
country_iso3: HND
hazard: drought
status: active
valid_until: "2028-01"
trigger_summary: >-
  Two-part trigger, either of which activates the EAP. (1) COPECO/CENAOS issues an alert
  that El Niño conditions in ONI region 3.4 are forecast with ≥60% probability over the
  next 3 months (OND-quarter forecast, excluding the AMJ/MJJ "predictability barrier"
  window). (2) COPECO/CENAOS' climate outlook forecasts accumulated rainfall for the next
  3 months falling in the 10th-20th percentile across the dry corridor, with >60%
  probability, starting from the March-May quarter. ~3-month lead time. Covers 9
  dry-corridor departments: Choluteca, Valle, Lempira, Francisco Morazán, Comayagua, Yoro,
  La Paz, El Paraíso and Intibucá.
data_sources: [COPECO, CENAOS, NOAA-CPC, IRI]
prearranged_funding_usd: 535202
funding_by_source: {DREF-anticipatory: 535202}
target_people: 10300
framework_doc: https://reliefweb.int/report/honduras/honduras-drought-early-action-protocol-summary-eap2023hn02
framework_doc_date: 2023-03-08
sources:
  - https://reliefweb.int/report/honduras/honduras-drought-early-action-protocol-summary-eap2023hn02
  - https://www.anticipation-hub.org/download/file-3441
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRHN018
  - https://reliefweb.int/report/honduras/honduras-drought-early-action-protocol-activation-eap2023hn02-operation-no-mdrhn018
  - https://reliefweb.int/report/honduras/honduras-droughts-early-action-protocol-activation-final-report-operation-no-mdrhn018
  - https://www.anticipation-hub.org/news/the-honduran-red-cross-activates-its-early-action-plan-for-drought-associated-with-el-nino
  - https://www.anticipation-hub.org/news/cruz-roja-hondurena-activa-su-plan-de-accion-temprana-ante-la-sequia-asociada-al-fenomeno-de-el-nino
  - https://www.ifrc.org/press-release/red-cross-activates-early-action-protocols-first-signs-drought-el-salvador-guatemala
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2023-06-26
    url: https://reliefweb.int/report/honduras/honduras-drought-early-action-protocol-activation-eap2023hn02-operation-no-mdrhn018
    note: >-
      First and, as of the 2026-06 Central America drought round (which activated El
      Salvador/Guatemala/Colombia but not Honduras), only known activation. Trigger 1 met:
      NOAA CPC's 8 June 2023 outlook stated El Niño conditions present with >90%
      probability of continuing through March 2024, relayed by CENAOS. CHF 481,187
      (≈US$548,437/€497,281) released from the DREF Anticipatory Pillar for 2,060
      households (360 for cash/voucher assistance, 1,700 for household water-treatment
      kits) across the 145 municipalities under Red Alert as of 15 June 2023. Actions:
      awareness campaigns, drinking-water-kit distribution, water-quality-assessment labs,
      multipurpose cash transfers, WASH team deployment. Final report published
      2024-02-27.
last_checked: '2026-07-16'
extra:
  hub_captions:
  - '2023: Drought (IFRC) [Honduran Red Cross]'
  hub_years:
  - '2023'
  implementing:
  - Honduran Red Cross
  eap_no: EAP2023HN02
  operation_no: MDRHN018
  eap_approved_date: '2023-01-17'
  eap_timeframe_years: 5
  early_action_timeframe_months: 3
  funding_chf: >-
    CHF 481,147 total budget (fully funded via DREF, approved 2023-01-17), sector split
    per the EAP summary: CHF 197,957 multipurpose cash transfers, CHF 118,956 WASH, CHF
    60,142 risk reduction/climate adaptation (remainder readiness/overhead). On the
    2023-06-26 activation the amount actually released is reported as CHF 481,187
    (≈US$548,437/€497,281 per IFRC's own conversion) — the ~CHF 40 difference from the
    budgeted 481,147 is unexplained in public reporting and immaterial.
    prearranged_funding_usd/funding_by_source above instead carry the Hub-inventory
    conversion (~1.117 CHF/USD), kept for consistency with the original stub.
  target_discrepancy: >-
    The EAP summary's planned target is 10,300 people / 1,800 households; the 2023-06-26
    activation actually reached 2,060 households (360 CVA + 1,700 WASH), implying ~10,300
    people at ~5/household — treated as the same overall scale, not a shortfall.
  coordination: >-
    NOT a component of an OCHA/CERF collective framework. OCHA/CERF runs a separate
    collective Central American Dry Corridor drought framework covering Guatemala, El
    Salvador and Honduras (frameworks/lac-dry-corridor — CERF-funded to FAO/PAHO/UNICEF/
    WFP, USD 10.5M, endorsed 2026-03-13; triggered for Honduras 2026-03-05 in El Paraíso
    and Francisco Morazán). That CERF/UN framework and this IFRC/Honduran-Red-Cross
    DREF-funded EAP are independent: different funders, different implementing agencies
    (UN agencies vs Red Cross), different trigger designs (ECMWF SEAS5 return-period
    aggregation vs ONI/rainfall-percentile), and no cross-mention found in either
    framework's public documents. Both happen to cover El Paraíso/Francisco Morazán-type
    dry-corridor geography but operate as parallel, uncoordinated tracks per the public
    record.
  schema_strain: >-
    Exact numeric lead time in days/weeks (beyond "~3 months") and any monitoring
    checkpoints analogous to the KEN/ETH EAPs are not stated in the sources found.
visibility: public
---

# IFRC — Honduras drought

## Summary
The Honduran Red Cross runs a 5-year, IFRC-endorsed drought Early Action Protocol
(EAP2023HN02, operation MDRHN018), approved 17 January 2023 and pre-financed by the
DREF's Anticipatory Pillar. It covers 9 departments of the Honduran dry corridor,
targeting subsistence-farming households with cash, WASH, and awareness support. It has
activated once, in June 2023, on an El Niño trigger.

## Trigger
Either of two conditions activates the EAP, monitored by COPECO/CENAOS with roughly a
3-month lead time: **(1) El Niño trigger** — an alert that ONI region 3.4 is forecast
with ≥60% probability of El Niño conditions over the next 3 months (OND-quarter
forecast; excluded during the AMJ/MJJ "predictability barrier" window when such forecasts
are unreliable). **(2) Precipitation-deficiency trigger** — a climate outlook forecasting
accumulated rainfall in the 10th-20th percentile across the dry corridor with >60%
probability, starting from the March-May quarter. Both draw on COPECO/CENAOS analysis of
NOAA Climate Prediction Center and IRI forecast products. Geographic scope: Choluteca,
Valle, Lempira, Francisco Morazán, Comayagua, Yoro, La Paz, El Paraíso and Intibucá.

## Funding & scope
CHF 481,147 total budget (fully funded via the DREF Anticipatory Pillar): CHF 197,957 for
multipurpose cash transfers, CHF 118,956 for WASH, CHF 60,142 for risk reduction/climate
adaptation, plus readiness costs. Planned target: 10,300 people (~1,800 households) in
the dry corridor's subsistence-farming population. Early-action implementation window is
3 months once triggered.

## Activations
- **26 June 2023** — the EAP's first and, to date, only known activation. NOAA's Climate
  Prediction Center forecast (8 June 2023) put El Niño conditions at >90% probability of
  persisting through March 2024, relayed by CENAOS; 145 municipalities were under drought
  Red Alert by 15 June 2023. CHF 481,187 (≈US$548,437/€497,281) released for 2,060
  households — 360 for cash/voucher assistance, 1,700 for household water-treatment kits
  — plus awareness campaigns, water-quality labs and WASH team deployment. Final report
  published 27 February 2024. No subsequent activation is documented as of the 2026-06
  Central American drought round, which activated El Salvador, Guatemala and Colombia but
  not Honduras.

## Sources
- **Authoritative:** [EAP Summary EAP2023HN02](https://reliefweb.int/report/honduras/honduras-drought-early-action-protocol-summary-eap2023hn02) (published 2023-03-08; approved 2023-01-17) · [Anticipation Hub PDF mirror](https://www.anticipation-hub.org/download/file-3441)
- [IFRC GO — MDRHN018](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRHN018) (machine-readable status/budget — $481,147 fully funded, 10,300 beneficiaries, Feb-Oct 2023, closed)
- [Activation notification, EAP2023HN02/MDRHN018, 26 June 2023](https://reliefweb.int/report/honduras/honduras-drought-early-action-protocol-activation-eap2023hn02-operation-no-mdrhn018)
- [Activation final report, MDRHN018, 27 February 2024](https://reliefweb.int/report/honduras/honduras-droughts-early-action-protocol-activation-final-report-operation-no-mdrhn018)
- Anticipation Hub news: [English](https://www.anticipation-hub.org/news/the-honduran-red-cross-activates-its-early-action-plan-for-drought-associated-with-el-nino) · [Spanish](https://www.anticipation-hub.org/news/cruz-roja-hondurena-activa-su-plan-de-accion-temprana-ante-la-sequia-asociada-al-fenomeno-de-el-nino)
- [IFRC press release, June 2026 Central America drought activations (El Salvador/Guatemala/Colombia — Honduras not among them)](https://www.ifrc.org/press-release/red-cross-activates-early-action-protocols-first-signs-drought-el-salvador-guatemala)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
- Cross-reference: OCHA/CERF's separate collective Dry Corridor framework, which also covers Honduras — [frameworks/lac-dry-corridor](../../frameworks/lac-dry-corridor/2026-03-13.md)
