---
content_type: framework-external
framework: ifrc-dji-flood
org: IFRC
country_iso3: DJI
hazard: flood
status: expired
valid_until: "2024-12-31"
trigger_summary: >-
  Simplified Early Action Protocol (sEAP) — Djibouti was among the first National
  Societies to develop one, under IFRC's June 2022 simplified-EAP modality. Activates when
  Djibouti's national meteorological service forecasts rainfall of ≥50mm within 7 days for
  Djibouti City and its suburbs (incl. Balbala), corroborated by an IGAD Climate Prediction
  and Applications Centre (ICPAC) East Africa hazard-watch heavy-rainfall alert for the
  same window. Lead time: 7 days.
data_sources: [ICPAC]
prearranged_funding_usd: 200330
funding_by_source: {DREF: 200330}
target_people: 2500
framework_doc: https://www.anticipation-hub.org/download/file-3091
framework_doc_date: 2022-12-02
sources:
- https://www.anticipation-hub.org/download/file-3091
- https://adore.ifrc.org/Download.aspx?FileId=606138
- https://reliefweb.int/report/djibouti/djibouti-africa-floods-simplified-early-action-protocol-eap2022dj01-dref-no-mdrdj006
- https://www.anticipation-hub.org/news/djibouti-activates-its-simplified-eap-for-floods-to-support-at-risk-communities
- https://reliefweb.int/report/djibouti/djibouti-floods-simplified-early-action-protocol-activation-report-mdrdj006-1852026
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRDJ006
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/djibouti
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2023-11-15
  url: https://www.anticipation-hub.org/news/djibouti-activates-its-simplified-eap-for-floods-to-support-at-risk-communities
  note: >-
    Only confirmed activation. Weekly forecast for 14-21 Nov 2023 indicated ≥50mm rainfall
    for Djibouti City/suburbs (El Niño-linked seasonal outlook). CHF 79,266 (~USD
    89,600/EUR 82,000) released from the DREF early-action component; within 7 days the
    Djibouti Red Crescent ran early warning dissemination, hygiene promotion and roofing
    material distribution/replacement in Balbala, reaching ~2,500 at-risk people
    (households facing displacement risk, low-income, female/child-headed, 3+ children,
    under-5s, elderly members).
last_checked: '2026-07-18'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Red Crescent Society of Djibouti] [IFRC]'
  - '2023: Flood (IFRC) [Red Crescent Society of Djibouti]'
  hub_years:
  - '2022'
  - '2023'
  implementing:
  - Red Crescent Society of Djibouti
  eap_no: EAP2022DJ01
  operation_no: MDRDJ006
  funding_chf: >-
    CHF 200,330 total (Readiness CHF 67,999 + Prepositioning CHF 53,064 + Early Action CHF
    79,266), fully funded via DREF. IFRC GO records this appeal's amount as USD 200,330
    (numerically identical to the CHF face value, i.e. a nominal pass-through rather than
    an actual FX conversion); the press release for the Nov 2023 early-action tranche
    separately converts CHF 79,266 to ~USD 89,600 (~1.13 CHF/USD) — the two USD figures in
    public sources are not on a consistent basis.
  validity: >-
    Approved 2 Dec 2022 with a stated "2 years" timeframe; IFRC GO lists the appeal
    (MDRDJ006) start 2022-11-23, end 2024-12-31. No public evidence of a renewal, second
    generation, or extension was found as of this check — the Hub inventory itself only
    lists 2022 and 2023 as active years (not 2024) — so `status` is set to `expired`
    rather than `active`. If a revised/renewed sEAP exists it was not found in public
    sources.
  target_areas: >-
    City of Djibouti and its suburb of Balbala, prioritised for low altitude and
    settlement patterns that compromise natural flood drainage routes.
  target_detail: >-
    2,500 people overall; within that, 100 households targeted specifically for roofing
    reinforcement, plus additional households for WASH (water treatment/hygiene kit
    distribution).
  schema_strain: >-
    No named product for the Djibouti national meteorological service forecast (unlike
    KMD/NDMA-style tags elsewhere) — only `ICPAC` is used in `data_sources`. Trigger
    threshold/lead-time detail above comes from an automated extraction of the Hub-hosted
    PDF (file/FileId 606138) via a text-rendering proxy, not a manual read of the source
    document — treat the exact CHF sub-totals and threshold wording as high-confidence but
    not manually verified against the original PDF layout.
visibility: public
---

# IFRC — Djibouti flood

## Summary
The Red Crescent Society of Djibouti's Simplified Early Action Protocol for floods
(EAP2022DJ01, IFRC operation MDRDJ006) — one of the first Simplified EAPs (sEAPs)
developed under IFRC's June 2022 simplified-EAP modality, a lighter-weight alternative to
standard EAPs aimed at easier-to-monitor triggers. Approved 2 December 2022 and
pre-financed through the IFRC Disaster Response Emergency Fund (DREF), it covers flash
flooding and seasonal-runoff flooding in Djibouti City and its Balbala suburb. It has one
confirmed activation, in November 2023, and its stated validity window has since lapsed
with no confirmed renewal found in public sources.

## Trigger
Activates when Djibouti's national meteorological service forecasts rainfall of ≥50mm
within a 7-day window for Djibouti City and its suburbs, corroborated by an ICPAC
(IGAD Climate Prediction and Applications Centre) East Africa hazard-watch heavy-rainfall
alert for the same period. Lead time is 7 days. The November 2023 activation followed
exactly this pattern: a weekly forecast (14-21 Nov 2023) of ≥50mm for Djibouti City/suburbs,
issued against the backdrop of an El Niño-influenced wet seasonal outlook.

## Funding & scope
CHF 200,330 pre-arranged via the DREF, fully funded: CHF 67,999 readiness + CHF 53,064
pre-positioning + CHF 79,266 for early-action implementation once triggered. Targets 2,500
people, including 100 households earmarked for roofing reinforcement and further
households for WASH support (water treatment and hygiene kits), in Djibouti City and
Balbala. The appeal's stated timeframe was 2 years; IFRC GO records the operational window
as 2022-11-23 to 2024-12-31 (see `extra.validity` — no renewal confirmed as of this check,
so `status` is recorded as `expired`).

## Activations
- **15 November 2023** (only confirmed activation) — the weekly forecast for 14-21 Nov
  2023 indicated rainfall of ≥50mm and above for Djibouti City and its suburbs, an
  El Niño-linked wet-season signal. CHF 79,266 (~USD 89,600/EUR 82,000) was released from
  the DREF early-action component. Within 7 days, the Djibouti Red Crescent disseminated
  early-warning messages via national media, ran hygiene promotion (addressing stagnant
  water health risks), and distributed/replaced roofing materials in the Balbala
  community, reaching an estimated 2,500 at-risk people (households at risk of
  displacement, low-income, female/child-headed, 3+ children, under-5s, elderly members).
- No other activation was found in public reporting.

## Sources
- **Authoritative:** [Simplified Early Action Protocol, Djibouti Floods, EAP2022DJ01/DREF MDRDJ006 (Anticipation Hub, file-3091, published 2 Dec 2022)](https://www.anticipation-hub.org/download/file-3091) ([IFRC ADORE mirror](https://adore.ifrc.org/Download.aspx?FileId=606138))
- [ReliefWeb — Djibouti, Africa | Floods: Simplified Early Action Protocol - EAP2022DJ01, DREF no. MDRDJ006](https://reliefweb.int/report/djibouti/djibouti-africa-floods-simplified-early-action-protocol-eap2022dj01-dref-no-mdrdj006)
- [Anticipation Hub — "Djibouti activates its Simplified EAP for Floods to support at-risk communities"](https://www.anticipation-hub.org/news/djibouti-activates-its-simplified-eap-for-floods-to-support-at-risk-communities) (Nov 2023 activation)
- [ReliefWeb — Djibouti | Floods - Simplified Early Action Protocol Activation Report, MDRDJ006](https://reliefweb.int/report/djibouti/djibouti-floods-simplified-early-action-protocol-activation-report-mdrdj006-1852026)
- [IFRC GO — appeal MDRDJ006](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRDJ006) (budget/beneficiaries/dates, machine-readable)
- [Anticipation Hub — anticipatory action in Djibouti (country overview)](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/djibouti)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
