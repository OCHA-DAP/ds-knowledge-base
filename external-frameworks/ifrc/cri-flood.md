---
content_type: framework-external
framework: ifrc-cri-flood
org: IFRC
country_iso3: CRI
hazard: flood
status: active
valid_until: '2028-10-31'
trigger_summary: >-
  Two-stage, based on National Meteorological Institute (IMN) forecasts. Trigger 1
  (pre-activation, 5-day lead): IMN forecasts a tropical storm tracking into at least "Zone
  3" of its Emergency Protocol with ≥60% probability. Trigger 2 (activation): IMN forecasts
  extreme rainfall with high probability of exceeding 400mm accumulated over a 5-day
  horizon (or is declared directly, regardless of Trigger 1, when 300-400mm is forecast
  alongside a tropical depression forming in danger zone 1 or 2); a day-2 check continues
  early actions if ≥300mm is still forecast over the next 3 days, otherwise a stop
  mechanism cancels. Releases a Multi-purpose Cash grant.
data_sources: [IMN]
prearranged_funding_usd: 600047
funding_by_source: {DREF-anticipatory: 600047}
target_people: 10000
framework_doc: https://www.anticipation-hub.org/download/file-3672
framework_doc_date: 2023-10-17
sources:
- https://www.anticipation-hub.org/download/file-3672
- https://www.anticipation-hub.org/Documents/EAPs/EAP_Costa_Rica_Floods.pdf
- https://reliefweb.int/report/costa-rica/costa-rica-floods-caused-tropical-cyclones-early-action-protocol-summary-eap-no-eap2023cr02-operation-no-mdrcr024
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRCR024
- https://reliefweb.int/report/costa-rica/costa-rica-floods-early-action-protocol-annual-report-eap-no-eap2023cr02-operation-no-mdrcr024-30-april-2026
- https://reliefweb.int/report/costa-rica/costa-rica-floods-dref-operation-mdrcr026
- https://reliefweb.int/report/costa-rica/costa-rica-floods-imminent-dref-operation-mdrcr027
- https://www.anticipation-hub.org/news/families-benefit-during-the-activation-of-the-costa-rican-red-crosss-early-action-plan-drill-for-floods
- https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-17'
extra:
  hub_captions:
  - '2023: Flood (IFRC) [Costa Rican Red Cross]'
  - '2024: Flood (IFRC) [Costa Rican Red Cross]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Costa Rican Red Cross
  eap_no: EAP2023CR02
  operation_no: MDRCR024
  approved: 2023-10-27
  eap_timeframe: 5 years (early-action window per activation is 3 months; the IMN forecast
    lead time itself is 5 days)
  funding_chf: >-
    CHF 528,641 total: CHF 181,792 readiness + CHF 346,849 automatic-on-trigger, funded
    from the IFRC-DREF Anticipatory Pillar (appeal code MDR00001). Breakdown: Multi-purpose
    Cash 377,517 CHF (AP code 081), Secretariat Services 49,949 CHF, National Society
    Strengthening 101,175 CHF. `prearranged_funding_usd` (600,047) is a Hub-inventory
    currency conversion, not a 1:1 CHF passthrough (unlike some other IFRC pages in this
    KB).
  scope_detail: >-
    Tusubres, Parrita and Damas river basins (Puntarenas province, central Pacific coast);
    highest flood-risk-index districts Parrita, Tárcoles, Quepos, Jacó and Carara. The
    Multi-purpose Cash early action targets ~2,000 people per activation (720 women + 280
    girls, 720 men + 280 boys), funded via ~2,050 pre-purchased debit cards through a
    framework agreement with a local bank; the EAP's 10,000-person target spans its 5-year
    lifetime/multiple possible activations, not a single event.
  partners: >-
    National Meteorological Institute (IMN, forecast/trigger monitoring), National
    Commission for Risk Prevention and Emergency Attention (CNE, national emergency
    coordination and formal notification to the Red Cross), German Red Cross (support
    partner), IFRC Climate Centre (design input).
  drill: >-
    16-21 January 2022: a test drill (predating this EAP generation's Oct 2023 approval) in
    Parrita, Puntarenas — 45 families received US$105 each via debit card, exercising the
    administrative/financial/operational procedures, with German Red Cross support and
    observers from eight other National Societies. Not a real trigger activation; not
    counted in `activations`.
  non_eap_events: >-
    Two flood events since EAP2023CR02's approval were met with standard (non-EAP) DREF
    operations rather than a reported EAP trigger declaration: Nov 2024 Pacific-coast
    flooding (indirect effects of Hurricane Rafael plus Tropical Wave #45; CNE declared a
    Red Alert for Guanacaste and Puntarenas) under DREF operation MDRCR026; Oct 2025
    northern-zone flooding (indirect effects of Hurricane Melissa) under MDRCR027 (~4,500
    people targeted across Guanacaste, Puntarenas, Alajuela and Cartago). Public sources
    found do not describe either as an EAP2023CR02 trigger; treated as non-EAP events, not
    counted in `activations`.
  schema_strain: >-
    A ReliefWeb-listed "Early Action Protocol Annual Report" for MDRCR024 (dated 30 Apr
    2026) could confirm or rule out a genuine EAP trigger during Oct 2024-Oct 2025, but
    ReliefWeb 403s automated fetches and no mirror was found; its content is unverified. No
    earlier flood-EAP generation exists for Costa Rica — a search hit for "EAP2022CR01"
    turned out to be the separate Costa Rica Volcanic Ash EAP
    (`external-frameworks/ifrc/cri-vulcano-ash.md`), not a flood-EAP predecessor.
visibility: public
---

# IFRC — Costa Rica flood

## Summary
The Costa Rican Red Cross's Early Action Protocol for floods caused by tropical cyclones
(EAP2023CR02/MDRCR024, approved 27 October 2023), pre-financed through the IFRC DREF's
Anticipatory Pillar. Designed with the National Meteorological Institute (IMN) and the
National Commission for Risk Prevention and Emergency Attention (CNE), it targets flood-prone
communities in the Tusubres, Parrita and Damas river basins (Puntarenas province) with a
Multi-purpose Cash grant, over a 5-year EAP lifetime aiming to assist up to 10,000 people. No
confirmed trigger activation has been reported to date; two subsequent flood events (Nov 2024,
Oct 2025) were instead handled as standard DREF operations.

## Trigger
Two-stage, driven entirely by IMN forecasts (no international model like GloFAS involved).
**Trigger 1** (pre-activation, 5-day lead): IMN forecasts a tropical storm tracking into at
least "Zone 3" of its Emergency Protocol, with ≥60% probability. **Trigger 2** (activation):
IMN forecasts extreme rainfall with a high probability of exceeding 400mm accumulated over a
5-day horizon — or is declared directly, independent of Trigger 1, when 300-400mm is forecast
alongside formation of a tropical depression in danger zone "1 or 2". A day-2 check keeps
early actions running if ≥300mm is still forecast for the next 3 days; otherwise a stop
mechanism cancels. The 300/400mm thresholds correspond to roughly a 5-year+ return period,
based on historical rainfall from hurricanes Tomas (2010), Otto (2016), Nate (2017) and Eta
(2020). Activation releases a Multi-purpose Cash grant.

## Funding & scope
CHF 528,641 from the IFRC-DREF Anticipatory Pillar (appeal MDR00001): CHF 181,792 readiness +
CHF 346,849 automatic-on-trigger. Of this, CHF 377,517 is earmarked for the Multi-purpose Cash
early action itself (~2,000 people per activation — 720 women + 280 girls, 720 men + 280 boys
— via ~2,050 pre-purchased debit cards through a local-bank framework agreement); the
remainder covers Secretariat Services (CHF 49,949) and National Society Strengthening (CHF
101,175). Geographic priority: Tusubres, Parrita and Damas basins, with Parrita, Tárcoles,
Quepos, Jacó and Carara as the highest flood-risk-index districts. The EAP's cited 10,000-person
target spans its 5-year validity (to 31 Oct 2028) rather than a single activation.

## Activations
None confirmed. A **16-21 January 2022 test drill** in Parrita, Puntarenas (predating this EAP
generation) exercised the procedures with 45 families receiving US$105 each, but was not a real
trigger. Two later flood events were handled outside the EAP: **November 2024** Pacific-coast
flooding (indirect effects of Hurricane Rafael, CNE Red Alert for Guanacaste/Puntarenas) under
standard DREF operation MDRCR026, and **October 2025** northern-zone flooding (indirect effects
of Hurricane Melissa) under DREF operation MDRCR027 (~4,500 people targeted). No public source
found describes either as an EAP2023CR02 IMN-forecast trigger being met.

## Sources
- **Authoritative:** [EAP summary, EAP2023CR02, published 17 Oct 2023](https://www.anticipation-hub.org/download/file-3672) (also mirrored at [anticipation-hub.org/Documents/EAPs](https://www.anticipation-hub.org/Documents/EAPs/EAP_Costa_Rica_Floods.pdf); [ReliefWeb listing](https://reliefweb.int/report/costa-rica/costa-rica-floods-caused-tropical-cyclones-early-action-protocol-summary-eap-no-eap2023cr02-operation-no-mdrcr024))
- [IFRC GO — appeal MDRCR024](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRCR024) (status/budget; active, fully funded, end date 31 Oct 2028)
- [EAP Annual Report, MDRCR024, 30 Apr 2026](https://reliefweb.int/report/costa-rica/costa-rica-floods-early-action-protocol-annual-report-eap-no-eap2023cr02-operation-no-mdrcr024-30-april-2026) (listed on ReliefWeb; content not fetchable by automated tools, unverified)
- [DREF operation MDRCR026](https://reliefweb.int/report/costa-rica/costa-rica-floods-dref-operation-mdrcr026) — Nov 2024 floods, non-EAP
- [Imminent DREF operation MDRCR027](https://reliefweb.int/report/costa-rica/costa-rica-floods-imminent-dref-operation-mdrcr027) — Oct 2025 floods, non-EAP
- [Anticipation Hub — Jan 2022 drill](https://www.anticipation-hub.org/news/families-benefit-during-the-activation-of-the-costa-rican-red-crosss-early-action-plan-drill-for-floods)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory listing)
