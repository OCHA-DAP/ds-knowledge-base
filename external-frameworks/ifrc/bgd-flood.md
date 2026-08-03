---
content_type: framework-external
framework: ifrc-bgd-flood
org: IFRC
country_iso3: BGD
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Two-stage trigger on the Jamuna river at Bahadurabad. Stage I (pre-activation, ~15-day
  lead) fires when GloFAS forecasts ≥50% probability of streamflow exceeding the 1-in-5-year
  return period for 3+ days (revised in the Aug 2021 EAP from a 1-in-10-year/10-day
  threshold used in the first two generations); Stage II (activation, shorter lead) is
  confirmed against the Flood Forecasting and Warning Centre's (FFWC) forecast, releasing
  boat-based evacuation support and cash grants in the most flood-exposed Jamuna floodplain
  districts.
data_sources: [GloFAS, FFWC]
prearranged_funding_usd: 349920
funding_by_source: {DREF-anticipatory: 349920}
target_people: 50000
framework_doc: https://reliefweb.int/report/bangladesh/bangladesh-floods-early-action-protocol-summary-eap-number-eap2021bd03
framework_doc_date: 2021-08
sources:
- https://reliefweb.int/report/bangladesh/bangladesh-floods-early-action-protocol-summary-eap-number-eap2021bd03
- https://adore.ifrc.org/Download.aspx?FileId=454009
- https://www.anticipation-hub.org/download/file-3933
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRBD037
- https://reliefweb.int/report/bangladesh/bangladesh-floods-early-action-protocol-activation-9-july-2024-mdrbd037
- https://www.forecast-based-financing.org/2020/07/02/protecting-families-in-bangladesh-against-floods-early-action-protocol-activated/
- https://www.anticipation-hub.org/global-overview/countries/bangladesh
activations:
- date: 2020-06-29
  url: https://www.forecast-based-financing.org/2020/07/02/protecting-families-in-bangladesh-against-floods-early-action-protocol-activated/
  note: >-
    First flood EAP activation (under EAP2019BD02) — GloFAS forecast (25 Jun) plus FFWC
    5-day confirmation (28 Jun) of severe Jamuna flooding; CHF 230,000+ released, boat
    evacuation and BDT 4,500 cash grants for ~16,500 people in Gaibandha, Jamalpur and
    Kurigram (plus 6,000 households assisted by WFP separately).
- date: 2024-07-09
  url: https://reliefweb.int/report/bangladesh/bangladesh-floods-early-action-protocol-activation-9-july-2024-mdrbd037
  note: >-
    Jamuna River Basin activation under the current EAP2021BD03/MDRBD037 — CHF 249,862
    FbA allocation (15,059 readiness + 234,803 automatic-on-trigger), ~50,000 people
    targeted. Coincided with the OCHA/CERF collective framework's own 4 Jul 2024 trigger
    for the same flood event (see `extra.coordination`).
last_checked: '2026-07-14'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Bangladesh Red Crescent Society] [German Red Cross] [American Red
    Cross] [Swiss Red Cross]'
  - '2023: Flood (IFRC) [Bangladesh Red Crescent Society]'
  - '2024: Flood (IFRC) [Bangladesh Red Crescent Society]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - Bangladesh Red Crescent Society
  eap_no: EAP2021BD03
  operation_no: MDRBD037
  generations: >-
    EAP2019BD02 (Dec 2019, 1-in-10-yr/10-day GloFAS threshold) → EAP2021BD03 (Aug 2021,
    current — revised to 1-in-5-yr/15-day using GloFAS v3.1); still the operative
    generation per IFRC GO operations updates on MDRBD037 through at least mid-2026.
  funding_chf: >-
    CHF 249,862 FbA allocation for the Jul 2024 activation (15,059 readiness + 234,803
    automatic); the IFRC GO appeal record for MDRBD037 shows a total operation budget of
    USD 349,920, fully funded — the two figures are not a straight currency conversion
    (GO's budget likely includes costs beyond the FbA disbursement itself).
  coordination: >-
    BDRCS's DREF/FbA-funded EAP runs alongside, and is not the same instrument as, the
    OCHA/CERF collective "Anticipatory Action Framework: Bangladesh Monsoon Floods"
    (`frameworks/bgd-flooding`), which uses the same GloFAS/FFWC Jamuna trigger design and
    covers overlapping districts (Bogra, Jamalpur, Sirajganj, Gaibandha, Kurigram). The
    Jul 2024 events were concurrent: BDRCS activated its own EAP on 9 Jul 2024 while CERF
    allocated $6.2M within 16 minutes of the same flood warning on 4 Jul 2024 under the
    collective framework. Treat this page as BDRCS's own published protocol, not as a
    duplicate of the OCHA page.
  non_eap_event: >-
    The 2022 Bangladesh floods (DREF/emergency appeal MDRBD028, ~CHF 2.7M raised) were a
    standard post-event emergency response, not a forecast-triggered EAP/FbA activation —
    the Hub's "2022" listing likely reflects general BDRCS flood-response activity that
    year rather than a confirmed EAP trigger; not counted in `activations` above.
  partners: German Red Cross, RCRC Climate Centre, Flood Forecasting and Warning Centre
    (Bangladesh Water Development Board), WFP (separate parallel assistance in 2020)
  schema_strain: >-
    No fixed EAP validity end-date found in public sources (unlike the cyclone EAP, which
    states 2029-02-28); `valid_until` left null.
visibility: public
---

# IFRC — Bangladesh flood EAP

## Summary
The Bangladesh Red Crescent Society's (BDRCS) flood Early Action Protocol — pre-financed by
the IFRC Disaster Relief Emergency Fund (DREF) anticipatory pillar, with technical support
from the German Red Cross and the RCRC Climate Centre — covers monsoon flooding of the
Jamuna river. Currently in its third generation (EAP2021BD03, approved August 2021), it
targets roughly 50,000 people with boat-based evacuation assistance and cash grants in the
most exposed Jamuna floodplain districts (Gaibandha, Jamalpur, Kurigram and neighbouring
areas). It runs alongside the separate OCHA/CERF collective Bangladesh Monsoon Floods
framework (see `extra.coordination`).

## Trigger
Two-stage, based on the Jamuna river at Bahadurabad. **Stage I (pre-activation, ~15-day
lead):** GloFAS forecasts ≥50% probability that streamflow will exceed the 1-in-5-year
return period for at least 3 days (the 2021 revision raised this from the original
1-in-10-year/10-day threshold used in EAP2019BD02, using GloFAS v3.1). **Stage II
(activation):** confirmed at shorter lead against the Flood Forecasting and Warning
Centre's (FFWC, Bangladesh Water Development Board) forecast, releasing the automatic DREF
tranche.

## Funding & scope
IFRC DREF Forecast-based Action (FbA) mechanism. The 9 July 2024 activation released CHF
249,862 (CHF 15,059 readiness + CHF 234,803 automatic-on-trigger); the IFRC GO appeal
record (MDRBD037) shows a total operation budget of USD 349,920, 100% funded. Target: ~50,000
people in the Jamuna floodplain districts.

## Activations
- **29 June 2020** (EAP2019BD02) — first flood EAP activation: GloFAS forecast + FFWC
  5-day confirmation of severe Jamuna flooding; CHF 230,000+ released for boat evacuation
  and BDT 4,500 cash grants to ~16,500 people in Gaibandha, Jamalpur and Kurigram (WFP
  separately assisted 6,000 further households).
- **9 July 2024** (EAP2021BD03/MDRBD037) — Jamuna River Basin activation, CHF 249,862 FbA
  allocation, ~50,000 people targeted; concurrent with the OCHA/CERF collective
  framework's own trigger for the same event.
- The Hub also lists 2022 and 2023 as active years; the 2022 flooding was met with a
  standard emergency appeal (MDRBD028), not a confirmed EAP/FbA trigger (see
  `extra.non_eap_event`) — no EAP-specific activation confirmed for 2022 or 2023.

## Sources
- **Authoritative:** [EAP summary, EAP2021BD03, approved Aug 2021](https://reliefweb.int/report/bangladesh/bangladesh-floods-early-action-protocol-summary-eap-number-eap2021bd03) ([PDF via ADORE](https://adore.ifrc.org/Download.aspx?FileId=454009), [Anticipation Hub mirror](https://www.anticipation-hub.org/download/file-3933))
- [IFRC GO — MDRBD037](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRBD037) (machine-readable budget/status) · [Activation report, 9 Jul 2024](https://reliefweb.int/report/bangladesh/bangladesh-floods-early-action-protocol-activation-9-july-2024-mdrbd037)
- [Forecast-based Financing — 2020 activation](https://www.forecast-based-financing.org/2020/07/02/protecting-families-in-bangladesh-against-floods-early-action-protocol-activated/)
- [Anticipation Hub — Bangladesh](https://www.anticipation-hub.org/global-overview/countries/bangladesh)
- Related OCHA/CERF collective framework: [`frameworks/bgd-flooding`](../../frameworks/bgd-flooding)

