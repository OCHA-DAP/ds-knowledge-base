---
content_type: framework-external
framework: ifrc-per-flood
org: IFRC
country_iso3: PER
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Two-stage GloFAS (Global Flood Awareness System, ECMWF) forecast trigger for the
  Amazon lowlands around Iquitos (Loreto region): a sub-seasonal forecast at 45-day lead
  time, firing when 75% of GloFAS ensemble members project streamflow exceeding the 80th
  percentile; confirmed/refined by a short-term forecast at 10-day lead, firing when the
  GloFAS 10-day ensemble gives a 60% chance of flow exceeding the 10-year return-period
  level. The 45-day signal opens a readiness window; the 10-day signal triggers early
  action implementation.
data_sources: [GloFAS]
prearranged_funding_usd: 260501
funding_by_source: {DREF: 260501}
target_people: 5000
framework_doc: https://reliefweb.int/report/peru/peru-floods-lower-amazon-jungle-early-action-protocol-summary
framework_doc_date: 2020-02-14
sources:
- https://reliefweb.int/report/peru/peru-floods-lower-amazon-jungle-early-action-protocol-summary
- https://adore.ifrc.org/Download.aspx?FileId=291379
- https://www.anticipation-hub.org/global-overview/countries/peru/implementing-the-fbf-mechanism-in-peru
- https://www.anticipation-hub.org/experience/global-map
- https://www.rcrcmagazine.org/2019/09/a-window-of-time/
- https://www.forecast-based-financing.org/projects/peru/
activations: []
last_checked: '2026-07-18'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Peruvian Red Cross] [German Red Cross]'
  hub_years:
  - '2022'
  implementing:
  - Peruvian Red Cross
  - German Red Cross
  eap_no: EAP2019PE02
  partners: German Red Cross (pioneering partner), Red Cross Red Crescent Climate Centre,
    510 (Netherlands Red Cross), SENAMHI, ENFEN, CENEPRED, INDECI
  approved: October 2019 (IFRC approval of the EAP); the EAP summary document above was
    published on ReliefWeb 14 Feb 2020.
  funding_note: >-
    The EAP summary document states the DREF Forecast-based Action (FbA) allocation as
    CHF 248,546 (CHF 92,892 immediate readiness/pre-positioning + CHF 155,654 automatic
    early-action tranche released once triggers are met). The Anticipation Hub inventory
    figure used above, US$260,501, is a different currency/vintage and could not be
    reconciled to the CHF figure from public sources — treat both as approximate.
  schema_strain: >-
    No activation of this flood EAP was found in public sources (as distinct from the
    Peruvian Red Cross's separate, unrelated ordinary-response DREF operations for
    Peru floods, e.g. MDRPE008/009/012/014, which are not part of this
    forecast-based mechanism). Coverage is confirmed only for the Loreto region
    (around Iquitos); planned expansion to Ucayali and Madre de Dios mentioned in the
    2019/2020 EAP documentation was not confirmed as implemented. `valid_until` is
    unknown — one secondary source (forecast-based-financing.org) gives an overall
    project window of 2015-2020, but this appears to describe the pilot FbF programme
    that preceded the EAP, not a stated expiry of the EAP itself.
visibility: public
---

# IFRC — Peru flood

## Summary
The Peruvian Red Cross (PRC), with the German Red Cross as pioneering partner and
technical support from the Red Cross Red Crescent Climate Centre, runs a Forecast-based
Financing (FbF) Early Action Protocol (EAP2019PE02) for seasonal Amazon-lowland flooding
around Iquitos, Loreto. Approved by IFRC in October 2019 (summary document published on
ReliefWeb 14 February 2020), it is triggered by GloFAS forecasts and, once fired, releases
IFRC DREF funding to distribute water filters and cash grants to roughly 1,000 families
(~5,000 people) ahead of the flood season (December-March). No activation has been found
in public sources.

## Trigger
A two-stage GloFAS (ECMWF Global Flood Awareness System) forecast, evaluated for the
Amazon lowlands near Iquitos:
- **Sub-seasonal stage (45-day lead):** fires when 75% of GloFAS ensemble members
  forecast streamflow exceeding the 80th percentile — opens the readiness window.
- **Short-term stage (10-day lead):** fires when the GloFAS 10-day ensemble forecast
  gives a 60% chance of flow exceeding the level corresponding to a 10-year return
  period — triggers implementation of early actions.

The programme currently covers the **Loreto** region only; work toward extending
triggering to Ucayali and Madre de Dios was described as in progress in the 2019/2020
documentation but is not confirmed as implemented (see `extra.schema_strain`).

## Funding & scope
Funded through the IFRC DREF's Forecast-based Action (FbA) mechanism. The EAP summary
document states a total DREF allocation of **CHF 248,546**: CHF 92,892 released
immediately for readiness and pre-positioning, plus CHF 155,654 released automatically
once the triggers are met. The Anticipation Hub inventory records this framework's
pre-arranged funding as **US$260,501** (a different currency/vintage that could not be
reconciled to the CHF figure — see `extra.funding_note`). Target: ~1,000 families
(~5,000 people) in Loreto — 600 families receive household water filters, 400 families
receive cash grants (~CHF 220 each).

## Activations
None known. No public source describes this flood EAP (EAP2019PE02) as having fired.
This is distinct from the Peruvian Red Cross's ordinary post-event DREF flood-response
operations in Peru (e.g. MDRPE008, MDRPE009, MDRPE012, MDRPE014), which are separate,
non-anticipatory operations not part of this forecast-based mechanism.

## Sources
- **Authoritative:** [Peru: Floods in the Lower Amazon Jungle — Early Action Protocol summary](https://reliefweb.int/report/peru/peru-floods-lower-amazon-jungle-early-action-protocol-summary) (ReliefWeb, published 14 Feb 2020) · [EAP document PDF](https://adore.ifrc.org/Download.aspx?FileId=291379)
- [Anticipation Hub — Implementing the FbF mechanism in Peru](https://www.anticipation-hub.org/global-overview/countries/peru/implementing-the-fbf-mechanism-in-peru) (country overview, covers all three PRC FbF protocols: Amazon floods, cold wave/snowfall, El Niño)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record, funding figure)
- [Red Cross Red Crescent Magazine — "A window of time"](https://www.rcrcmagazine.org/2019/09/a-window-of-time/) (narrative background, partners, pilot history since 2016)
- [Forecast-based-financing.org — Peru project page](https://www.forecast-based-financing.org/projects/peru/) (programme overview across hazards)
- Related PRC EAP for the same country: [`external-frameworks/ifrc/per-cold-wave.md`](per-cold-wave.md)
