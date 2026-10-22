---
content_type: framework-external
framework: ifrc-uga-flood
org: IFRC
country_iso3: UGA
hazard: flood
status: active   # IFRC GO lists operation MDRUG048 as Active to 2026-11-30; whether the EAP itself is renewed past its May 2026 timeframe is unconfirmed (see valid_until)
valid_until: 2026-05-27   # the Nov 2023 activation document gives the EAP's timeframe as 27 May 2021 - 27 May 2026; no second-generation EAP found (checked 2026-09-30)
trigger_summary: >-
  Uganda Red Cross Society (URCS) activates on a GloFAS ensemble forecast of a 5-year
  return-period flood at a 5-day lead, expected to affect more than 1,000 households. The
  approved EAP (May 2021) set ≥70% probability of a 5-yr flood in high-priority districts and
  a 10-yr flood in lower-priority ones, with a false-alarm ratio ≤0.5; the Nov 2023 activation
  wording and the 510 IBF portal that computes the trigger use ≥60% probability of a 5-yr flood
  in flood-prone districts.
data_sources: [GloFAS, UNMA, ICPAC]
prearranged_funding_usd: 395000
funding_by_source: {DREF: 395000}
target_people: 11201
framework_doc: https://www.anticipation-hub.org/download/file-3684
framework_doc_date: 2021-08-18
sources:
  - https://www.anticipation-hub.org/download/file-3684
  - https://reliefweb.int/report/uganda/uganda-floods-early-action-protocol-summary-eap-number-eap2021ug01
  - https://www.anticipation-hub.org/news/uganda-acts-in-anticipation-of-the-peak-impacts-of-floods
  - https://reliefweb.int/report/uganda/uganda-floods-early-action-protocol-activation-operation-ndeg-mdrug048
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRUG048
  - https://zcralliance.org/blogs/coproduction-of-early-action-protocol-for-floods-in-uganda/
  - https://www.anticipation-hub.org/global-overview/countries/uganda
  - https://github.com/rodekruis/IBF-river-flood-pipeline
activations:
  - date: 2023-11-15
    url: https://www.anticipation-hub.org/news/uganda-acts-in-anticipation-of-the-peak-impacts-of-floods
    note: >-
      First-ever activation (EAP2021UG01, operation MDRUG048): GloFAS forecast met the
      ≥60%-probability 5-year-return-period threshold ahead of El Niño-driven rains; CHF
      348,761 (≈US$395,000) released for 2,383 households (~11,201 people) in Butaleja,
      Kikuube and Ntoroko districts. Actions: water-source cleaning and drainage-channel
      desilting, community risk-awareness campaigns, rapid mapping of evacuation
      centres/routes, then cash & voucher assistance, shelter kits and WASH supplies
      (water-purification tablets, soap, storage containers).
last_checked: '2026-09-30'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Uganda Red Cross Society] [The Netherlands Red Cross]'
  - '2023: Flood (IFRC) [Uganda Red Cross Society]'
  hub_years:
  - '2022'
  - '2023'
  implementing:
  - Uganda Red Cross Society
  eap_no: EAP2021UG01
  operation_no: MDRUG048
  approved: 2021-05-27   # EAP summary approval date; 18 Aug 2021 is the publication date (framework_doc_date)
  partners: >-
    Design/TWG: Uganda Red Cross Society (implementing), Red Cross Red Crescent Climate
    Centre, Netherlands Red Cross Data & Digital team (510), Uganda Directorate of Water
    Resources Management (DWRM), Uganda National Meteorological Authority (UNMA), Office
    of the Prime Minister (OPM), University of Reading FATHUM project. EAP submitted to
    IFRC's validation committee September 2020, published August 2021. Netherlands Red
    Cross credited as a funding/support partner in the Hub's 2022 listing.
  scope_detail: >-
    The EAP names 14 high-risk districts: Kasese, Katakwi, Amuria, Kampala, Butaleja,
    Sironko, Bududa, Manafwa, Kumi, Ntoroko, Bulambuli, Moyo, Nabilatuk and Ngora (EAP
    summary, May 2021; no public assignment of them to the 5-yr vs 10-yr priority tiers). The
    16 districts in the Nov 2023 activation reports (Ntoroko, Buyende, Namayingo, Kikuube,
    Pallisa, Kagadi, Butaleja, Kyenjojo, Kaliro, Bugiri, Kibuku, Namutumba, Busia, Tororo,
    Budaka, Butebo; Ntoroko with 36,590 and Buyende with 7,732 exposed the highest) are the IBF
    portal's "potentially exposed districts" for that forecast, not the EAP's district list.
    The 2023 activation itself covered only Butaleja, Kikuube and Ntoroko.
  ibf_portal_computation: >-
    How the trigger is actually computed (510 IBF river-flood pipeline, Uganda settings, as read
    Sep 2026): districts, counties and sub-counties (admin 2-4) are each judged at their zonal
    maximum, the largest forecast flow of each of 51 GloFAS members anywhere in the area
    against the largest value of the official GloFAS v4 5-year return-level map in the area; an
    area triggers when ≥60% of members exceed it at any lead up to 5 days, and a triggered
    county or sub-county triggers its district. So the 2023 wording (single 60% / 5-yr bar) is
    what runs, not the 2021 one; the >1,000-household condition is judged from the exposure the
    portal displays. OCHA reproduces it in ocha-dap/ds-aa-uga-flooding
    (analysis/ifrc_reproduction.py), where it is the Teso zone's trigger of OCHA's
    in-development framework (frameworks/uga-flooding).
  funding_chf: >-
    CHF 348,761 pre-arranged (≈US$395,000 / €362,000 per the Anticipation Hub's own
    conversion); the IFRC GO appeal API lists the same numeral, 348,761, under a "$"
    budget field — likely a CHF/USD mislabel rather than a second funding round. Target
    people/prearranged_funding_usd above use the Hub's USD conversion and the GO
    beneficiary count (11,201) respectively.
  schema_strain: >-
    No public evidence of an activation in 2022 despite the Hub's "2022: Flood (IFRC)"
    listing — 2022 URCS news covers Mbale/Kasese landslide-flood response and Uganda's
    first National Dialogue on Anticipatory Action (Nov 2022), not an EAP trigger event;
    the Hub year tags likely mark active programme/support years rather than activations.
    Only one confirmed activation (Nov 2023) found. ReliefWeb pages 403 to automated
    fetch; details above are corroborated across the Anticipation Hub PDF (file-3684),
    Hub news, IFRC GO API, and the ZCR Alliance/Climate Centre coproduction writeups
    instead. `valid_until` is the EAP timeframe stated in the Nov 2023 activation document
    (27 May 2021 - 27 May 2026); IFRC GO keeps operation MDRUG048 open to 30 Nov 2026, and
    whether the EAP runs for Oct-Dec 2026 is unconfirmed. OCHA's in-development Uganda flood
    framework (frameworks/uga-flooding) adopts this trigger for its Teso zone (alignment,
    Sep 2026); this page remains URCS's own EAP and its activations stay here.
visibility: public
---

# IFRC — Uganda flood

> **Not an OCHA/CERF framework.** This is IFRC's anticipatory-action framework, catalogued here for cross-organisation comparison ([why](../README.md)). OCHA's own UGA framework(s): [uga-flooding](../../frameworks/uga-flooding/README.md).

## Summary
The Uganda Red Cross Society's (URCS) national flood Early Action Protocol (EAP2021UG01,
published August 2021 after validation-committee submission in September 2020), financed
through the IFRC DREF. Co-developed with the Red Cross Red Crescent Climate Centre, the
Netherlands Red Cross data team (510), Uganda's Directorate of Water Resources Management
and National Meteorological Authority, and the University of Reading's FATHUM project. It
names 14 high-risk districts and has activated once to date, in November 2023. Its stated
timeframe ran to 27 May 2026; whether it is renewed for the Oct-Dec 2026 season is
unconfirmed.

## Trigger
The approved EAP (May 2021) activates when GloFAS forecasts at least 70% probability of a
5-year-return-period flood in high-priority flood-prone districts, and of a 10-year flood in
lower-priority ones, expected to affect more than 1,000 households, at a 5-day lead time, in
locations where the false-alarm ratio is at most 0.5. The November 2023 activation document
states it as at least 60% probability of a 5-year flood in flood-prone districts (no 10-year
tier), and that is what the 510 IBF portal computes: every district, county and sub-county is
judged at its zonal maximum (the largest forecast flow of each of 51 ensemble members anywhere
in the area against the largest value of the official GloFAS v4 5-year return-level map
there), it triggers when at least 60% of members exceed that level at a lead of 5 days or
less, and a triggered county or sub-county triggers its district. The GloFAS signal is
triangulated against forecasts from the Uganda National Meteorological Authority (UNMA) and
ICPAC.

## Funding & scope
CHF 348,761 (≈US$395,000 / €362,000) pre-arranged through the IFRC DREF. The EAP names 14
high-risk districts (Kasese, Katakwi, Amuria, Kampala, Butaleja, Sironko, Bududa, Manafwa,
Kumi, Ntoroko, Bulambuli, Moyo, Nabilatuk, Ngora). The 16 "potentially exposed districts" in
the November 2023 activation reports, with Ntoroko (36,590 exposed) and Buyende (7,732
exposed) the highest, are the IBF portal's output for that forecast, not the EAP's district
list. Early actions span shelter, WASH, cash & voucher assistance and disaster-risk-reduction
(evacuation mapping, awareness campaigns).

## Activations
- **15 November 2023** (EAP2021UG01 / MDRUG048) — first-ever activation, triggered by a
  GloFAS forecast meeting the ≥60%-probability 5-year-return-period threshold ahead of
  El Niño-driven rains. CHF 348,761 (≈US$395,000) released for 2,383 households (~11,201
  people) in Butaleja, Kikuube and Ntoroko districts: water-source cleaning and drainage
  desilting, risk-awareness campaigns, evacuation-route/centre mapping, followed by cash
  and voucher assistance, shelter kits (tarpaulins, mosquito nets, blankets, tents) and
  WASH supplies (purification tablets, soap, storage containers).
- No other activations known. The Hub's "2022: Flood" listing does not correspond to a
  found activation — 2022 URCS activity was flood/landslide response in Mbale and Kasese
  plus Uganda's first National Dialogue on Anticipatory Action, not an EAP trigger event.

## Sources
- **Authoritative:** [EAP for Floods: Uganda (EAP2021UG01)](https://www.anticipation-hub.org/download/file-3684) (IFRC/URCS, published 18 Aug 2021)
- [Uganda Floods: EAP summary, EAP2021UG01](https://reliefweb.int/report/uganda/uganda-floods-early-action-protocol-summary-eap-number-eap2021ug01) (ReliefWeb mirror)
- [Uganda acts in anticipation of the peak impacts of floods](https://www.anticipation-hub.org/news/uganda-acts-in-anticipation-of-the-peak-impacts-of-floods) (Anticipation Hub news, Nov 2023 activation)
- [Uganda Floods — EAP Activation Operation, MDRUG048](https://reliefweb.int/report/uganda/uganda-floods-early-action-protocol-activation-operation-ndeg-mdrug048) (ReliefWeb)
- [IFRC GO — appeal MDRUG048](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRUG048) (budget/beneficiary figures)
- [The coproduction of the EAP for floods in Uganda](https://zcralliance.org/blogs/coproduction-of-early-action-protocol-for-floods-in-uganda/) (Zurich Climate Resilience Alliance — design partners/process)
- [Anticipation Hub — Uganda country page](https://www.anticipation-hub.org/global-overview/countries/uganda) (original Hub inventory link)
- [rodekruis/IBF-river-flood-pipeline](https://github.com/rodekruis/IBF-river-flood-pipeline) (the 510 IBF pipeline that computes the trigger; Uganda settings read Sep 2026)
