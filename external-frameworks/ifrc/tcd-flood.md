---
content_type: framework-external
framework: ifrc-tcd-flood
org: IFRC
country_iso3: TCD
hazard: flood
status: active
valid_until: "2026-08-31"
trigger_summary: >-
  Two-stage trigger for pluvial (rainfall-driven) flooding across six southern provinces.
  Seasonal readiness trigger (information available in May, ~2-month lead time): an
  above-normal seasonal rainfall forecast from Chad's National Meteorological Agency
  (ANAM). Short-scale action trigger (7-day lead time): the ECMWF weekly Extreme Forecast
  Index (EFI) exceeds 0.8 AND ANAM's own extreme-rainfall forecast agrees.
data_sources: [ECMWF, ANAM]
prearranged_funding_usd: 218880
funding_by_source: {DREF: 192833}
target_people: 2400
framework_doc: /download/file-4972
framework_doc_date: 2024-08-20
sources:
  - https://www.anticipation-hub.org/download/file-4972
  - https://www.anticipation-hub.org/Documents/EAPs/sEAP_Chad_Flood.pdf
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRTD023
  - https://reliefweb.int/report/chad/chad-floods-simplified-early-action-protocol-seap-no-seap2023cd01
  - https://reliefweb.int/report/chad/chad-rainfall-flooding-simplified-early-action-protocol-annual-report-3132026-seap-no-seap2023cd01-operation-number-mdrtd023
  - https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-19'
extra:
  hub_captions:
  - '2024: Flood (IFRC) [Chad Red Cross]'
  hub_years:
  - '2024'
  implementing:
  - Red Cross Society of Chad (Croix-Rouge du Tchad, CRT)
  eap_no: sEAP2023CD01
  operation_no: MDRTD023
  partners: >-
    French Red Cross (FbF delegate — technical support to the CRT Disaster Management
    department and formulation of the sEAP), IFRC Climate Centre (trigger/threshold
    design), Luxembourg Red Cross (Shelter/WASH technical expertise), OCHA Chad (data
    support for the historical risk analysis).
  funding_chf: >-
    CHF 192,833 total: CHF 48,984 readiness, CHF 73,734 pre-positioning, CHF 70,115 early
    action. Sourced from the IFRC DREF Anticipatory Pillar. Validation committee endorsed
    26 June 2024; DREF allocation request signed 19-20 August 2024; sEAP approved
    20 August 2024. The Anticipation Hub global-map USD figure (US$218,880) is a currency
    conversion of this CHF total, not an independently sourced amount.
  target_detail: >-
    2,400 people (~400 households) across six southern provinces: Moyen Chari, Mandoul,
    Logone Oriental, Tandjilé, Mayo Kebbi Ouest and Salamat. The sEAP's own household math
    is internally inconsistent (it states "50 households per province ... equivalent to
    400 households in total" across the 6 listed provinces, i.e. 300, not 400) — kept
    as-is rather than resolved, since the source document does not reconcile it.
  operational_period: "3 months per activation, within a 2-year sEAP timeframe (20 Aug 2024 - 31 Aug 2026 per IFRC GO)."
  coordination: >-
    NOT a component of a collective OCHA/CERF framework. A separate OCHA/CERF Chad flood
    framework exists (frameworks/tcd-flooding/2025-07-31.md — CERF-funded, $4M, operated by
    OCHA's Centre for Humanitarian Data) but it targets a different hazard mechanism
    entirely: riverine flooding of the Chari River at N'Djamena and Mayo-Kebbi Est
    (Bongor), triggered by GloFAS discharge forecasts, implemented by UNHCR/UNICEF/FAO/WFP.
    This IFRC sEAP instead covers pluvial (rainfall) flooding in six southern provinces,
    triggered by ANAM seasonal forecasts and the ECMWF EFI index, funded via DREF and
    implemented by the Red Cross Society of Chad. Different hazard type, geography,
    trigger, funder and operator — two independent Chad flood AA mechanisms, not one
    framework's components.
  schema_strain: >-
    ReliefWeb report pages returned HTTP 403 to direct fetch (as with other IFRC EAP
    pages); facts are drawn from the sEAP PDF itself (fetched via the Anticipation Hub
    mirror) and the IFRC GO API. A "Simplified Early Action Protocol Annual Report" for
    this sEAP (dated 31/3/2026, operation MDRTD023) is listed on ReliefWeb but its content
    was not fetchable (403) and no secondary source describing its content was found — it
    is unclear whether it documents an actual trigger activation or is a routine annual
    report filed regardless of activation (sEAPs require annual reporting under the DREF
    Anticipatory Pillar). No confirmed activation (trigger firing, funds released,
    early actions carried out) was found in public sources, so `activations` is left
    empty rather than guessed. IFRC GO lists the appeal as "Active" and fully funded at
    CHF/US$192,833, consistent with pre-positioned readiness funding rather than a
    completed early-action disbursement.
visibility: public
---

# IFRC — Chad flood

## Summary
The Red Cross Society of Chad's Simplified Early Action Protocol for pluvial (rainfall)
flooding (sEAP2023CD01, approved 20 August 2024, operation MDRTD023), developed with
technical support from the French Red Cross, the IFRC Climate Centre and the Luxembourg
Red Cross. It targets 2,400 people (~400 households) across six flood-prone southern
provinces — Moyen Chari, Mandoul, Logone Oriental, Tandjilé, Mayo Kebbi Ouest and Salamat
— with early-warning dissemination, sandbag/ploughing equipment for home protection, and
NFI/WASH kits (mosquito nets, water-purification supplies, buckets). No public record of
an actual trigger activation was found as of this check.

## Trigger
A two-stage, sequenced trigger designed with the IFRC Climate Centre:
- **Seasonal (readiness) trigger** — information available in May, ~2-month lead time:
  an above-normal seasonal rainfall forecast issued by Chad's National Meteorological
  Agency (ANAM), transmitted to the CRT's Disaster Management department.
- **Short-scale (early action) trigger** — 7-day lead time: the ECMWF weekly Extreme
  Forecast Index (EFI) for the target area exceeds 0.8 (the model's most severe rainfall
  intensity category) AND ANAM's own extreme-rainfall forecast concurs, to reduce false
  alarms.

Thresholds were set at a national workshop in N'Djamena on 19 October 2022, combining
ECMWF forecast skill (chosen because it performs comparatively well over 7-day
accumulations in the Sahel) with local ANAM meteorological judgement.

## Funding & scope
CHF 192,833 (≈US$218,880 per the Anticipation Hub's currency-converted inventory figure)
from the IFRC DREF's Anticipatory Pillar: CHF 48,984 readiness, CHF 73,734
pre-positioning, CHF 70,115 released as the early-action tranche once triggered.
Operational timeframe per activation is 3 months, within a 2-year sEAP validity
(20 August 2024 – 31 August 2026 per the IFRC GO API). Targets 2,400 people across the
six named southern provinces, implemented by the Red Cross Society of Chad with
technical support from the French Red Cross (FbF delegate), IFRC Climate Centre and
Luxembourg Red Cross (Shelter/WASH).

## Activations
None found in public sources. The sEAP has been active (fully funded per IFRC GO) since
August 2024, and a "Simplified Early Action Protocol Annual Report" covering the sEAP is
listed on ReliefWeb for 31 March 2026 (operation MDRTD023), but its content could not be
fetched (403) and no secondary source describing an actual trigger firing, fund release,
or early actions carried out was found — see `extra.schema_strain`. This sEAP is distinct
from the separate OCHA/CERF riverine-flood framework for N'Djamena, which *was* activated
in September 2024 (see `extra.coordination`); no evidence found here should be read as
implying this sEAP shared that activation.

## Sources
- **Authoritative:** [Simplified Early Action Protocol, sEAP2023CD01, approved 20 August 2024](/download/file-4972) ([mirror](https://www.anticipation-hub.org/Documents/EAPs/sEAP_Chad_Flood.pdf))
- [IFRC GO API — MDRTD023](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRTD023) (status, dates, funding, beneficiaries; machine-readable)
- [ReliefWeb — Chad Floods sEAP landing page](https://reliefweb.int/report/chad/chad-floods-simplified-early-action-protocol-seap-no-seap2023cd01) (fetch blocked, 403; listed for completeness)
- [ReliefWeb — Chad Rainfall Flooding sEAP Annual Report, 31/3/2026](https://reliefweb.int/report/chad/chad-rainfall-flooding-simplified-early-action-protocol-annual-report-3132026-seap-no-seap2023cd01-operation-number-mdrtd023) (fetch blocked, 403; content unconfirmed)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record, originally fetched 2026-07-10)
