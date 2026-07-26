---
content_type: framework-external
framework: ifrc-ken-drought
org: IFRC
country_iso3: KEN
hazard: drought
status: active
valid_until: "2027-10"
trigger_summary: >-
  For the October-November-December (OND) short-rains season, activates when the Kenya
  Meteorological Department's OND seasonal forecast shows a Standardised Precipitation
  Index (SPI) below -0.98 with ≥33% probability of occurrence in at least 3 of Kenya's 23
  arid/semi-arid (ASAL) counties (lead time up to ~12 weeks, checkpoints in July/August/
  September). Qualifying counties are risk-ranked; any already in NDMA "alarm" or
  "emergency" drought phase are dropped as too late for anticipatory action, and early
  actions are delivered in the top 3 remaining counties.
data_sources: [KMD, NDMA]
prearranged_funding_usd: 628292
funding_by_source: {DREF-anticipatory: 628292}
target_people: 150000
framework_doc: https://reliefweb.int/report/kenya/kenya-drought-early-action-protocol-summary-eap2022ke02
framework_doc_date: 2023-02-19
sources:
  - https://www.anticipation-hub.org/download/file-3530
  - https://adore.ifrc.org/Download.aspx?FileId=640328
  - https://reliefweb.int/report/kenya/early-action-protocol-activation-kenya-drought-eap-no-eap2022ke02-operation-no-mdrke055
  - https://go-api.ifrc.org/api/downloadfile/92390/MDRKE055_EAP%20Activation
  - https://www.anticipation-hub.org/news/acting-to-anticipate-the-impacts-of-drought-in-kenya
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2025-09-12
    url: https://reliefweb.int/report/kenya/early-action-protocol-activation-kenya-drought-eap-no-eap2022ke02-operation-no-mdrke055
    note: >-
      First-ever activation, ~3 years after EAP approval. KMD's OND forecast (driven by a
      negative Indian Ocean Dipole) met the SPI < -0.98 / ≥33% probability trigger in ≥3
      of 23 ASAL counties. CHF 365,775 (≈US$460,210/€391,408) released from the DREF
      Anticipatory Pillar. Priority counties: Kwale, Kilifi, Kitui. Actions: drought-tolerant
      seed and fodder distribution, water-facility repair/cash-for-WASH, early-warning
      radio/SMS messaging, community engagement.
last_checked: '2026-07-14'
extra:
  hub_captions:
  - '2023: Drought (IFRC) [Kenya Red Cross Society]'
  - '2024: Drought (IFRC) [Kenya Red Cross Society]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Kenya Red Cross Society
  eap_no: EAP2022KE02
  operation_no: MDRKE055
  eap_approved_date: '2022-10-11'
  eap_timeframe_years: 5
  early_action_timeframe_months: 7
  funding_chf: >-
    Total budget CHF 499,199 (approved 2022-10-11, 5-year EAP lifetime to ~2027-10):
    CHF 85,107 readiness + CHF 46,855 pre-positioned stock + CHF 367,238 early-action
    tranche, all from the DREF Anticipatory Pillar (appeal code MDR00001). On the 2025-09
    activation, CHF 365,775 was actually released (≈US$460,210/€391,408 per IFRC's own
    conversion). The prearranged_funding_usd/funding_by_source figures above apply that
    same conversion rate (~1.2586 USD/CHF) to the full CHF 499,199 budget — an
    approximation, not a rate IFRC published for the full envelope.
  priority_counties: >-
    First 3 prioritized: Kwale, Kilifi, Kitui — chosen by drought-risk ranking (INFORM-style
    index) across the 23 ASAL counties meeting the SPI trigger, after dropping any county
    NDMA already classifies as alarm/emergency phase (too late for anticipatory action).
  coordination: >-
    NOT a component of an OCHA/CERF collective framework. The Centre for Humanitarian
    Data (OCHA CHD) runs a separate, unendorsed, in-development exploratory analysis at
    frameworks/ken-drought (repo ocha-dap/ds-aa-ken-drought, Dec 2025-Jun 2026) proposing
    an IOD-adjusted alternative trigger as a possible future enhancement to THIS EAP. That
    OCHA work has never been deployed or triggered — the EAP described on this page,
    run by KRCS/KMD/NDMA, is the sole operational framework and owns the Sep 2025
    activation.
  wfp_activation_2025: >-
    WFP separately activated its own anticipatory action for the same OND 2025 season in
    Marsabit and Wajir counties (10,750 households, US$70/household/month, Sep-Nov 2025)
    under a distinct WFP framework/trigger — see external-frameworks/wfp/ken-drought.md.
    No county overlap with the IFRC/KRCS activation (Kwale, Kilifi, Kitui).
visibility: public
---

# IFRC — Kenya drought

## Summary
The Kenya Red Cross Society (KRCS) runs a 5-year, IFRC-endorsed drought Early Action
Protocol (EAP2022KE02, operation MDRKE055) approved 11 October 2022, pre-financed from
the DREF's Anticipatory Pillar. It covers Kenya's 23 arid and semi-arid (ASAL) counties for
the October-November-December (OND) short-rains season, delivering livelihoods, WASH,
early-warning and community-engagement support to up to 150,000 people. It triggered for
the first time in September 2025, in Kwale, Kilifi and Kitui counties.

## Trigger
KMD issues OND seasonal forecasts at three checkpoints (roughly July, August, September;
lead time up to ~12 weeks from the July issuance). If the forecast SPI for OND falls below
-0.98 with at least 33% probability of occurrence in 3 or more of the 23 ASAL counties, the
IBF (Impact-Based Forecasting) dashboard flags those counties and ranks them by a
drought-risk index, factoring in IPC phase projections. Any county NDMA already classifies
as "alarm" or "emergency" phase is dropped (too late for anticipatory action); the EAP
activates in the top 3 remaining counties.

## Funding & scope
CHF 499,199 total budget for the EAP's 5-year lifetime (2022-2027): CHF 85,107 readiness +
CHF 46,855 pre-positioned stock + CHF 367,238 early-action tranche, all under the DREF
Anticipatory Pillar (appeal MDR00001). Target: 150,000 people across the 23 ASAL counties.
Sectors: livelihoods (drought-tolerant seed/fodder distribution, ~22,500 people), WASH
(water-facility repair, cash-for-WASH, ~7,500 people), early warning (radio/SMS to 150,000
people) and community engagement and accountability. On the September 2025 activation,
CHF 365,775 (≈US$460,210/€391,408) was released for the three priority counties.

## Activations
- **12 September 2025** — the EAP's first-ever activation, roughly three years after
  approval. Negative-IOD-driven poor OND forecast met the SPI/probability trigger in ≥3 of
  23 ASAL counties; CHF 365,775 released; priority counties Kwale, Kilifi, Kitui; actions
  covered livelihoods, WASH, early-warning messaging and community engagement. WFP
  separately activated anticipatory action in Marsabit and Wajir for the same season under
  its own framework (no county overlap).
- No prior activations known (approved Oct 2022, first fired Sep 2025).

## Sources
- **Authoritative:** [EAP Summary EAP2022KE02, published 2023-02-19](https://reliefweb.int/report/kenya/kenya-drought-early-action-protocol-summary-eap2022ke02) ([full PDF, doc dated 15.02.2022, approved 11/10/2022](https://adore.ifrc.org/Download.aspx?FileId=640328); [Anticipation Hub mirror](https://www.anticipation-hub.org/download/file-3530))
- [Activation report, EAP №EAP2022KE02 / Operation №MDRKE055](https://reliefweb.int/report/kenya/early-action-protocol-activation-kenya-drought-eap-no-eap2022ke02-operation-no-mdrke055) · [internal activation PDF via IFRC GO, 16 Sep 2025](https://go-api.ifrc.org/api/downloadfile/92390/MDRKE055_EAP%20Activation)
- [Anticipation Hub — "Acting to anticipate the impacts of drought in Kenya"](https://www.anticipation-hub.org/news/acting-to-anticipate-the-impacts-of-drought-in-kenya)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Cross-reference: OCHA CHD's separate, in-development exploratory analysis of an alternative trigger for this EAP — [frameworks/ken-drought](../../frameworks/ken-drought/2023-02-19.md)
