---
content_type: framework-external
framework: ifrc-com-vulcano-ash
org: IFRC
country_iso3: COM
hazard: vulcano-ash
status: active
valid_until: 2026-04-30
trigger_summary: >-
  Karthala Volcano Observatory (OVK) seismic + ground-deformation monitoring drives a
  3-level alert (yellow → orange → red). Early action starts when CRCS receives the
  special orange-alert bulletin (OVK-SB2), ~4 days before impact — WASH/sanitation/dignity
  kit distribution and evacuation support; the red-alert bulletin (OVK-BS3, ~2 days out)
  triggers dust-mask/goggle distribution ahead of evacuation.
data_sources: [OVK]
prearranged_funding_usd: 210958
funding_by_source: {DREF-anticipatory: 210958}
target_people: 12000
framework_doc: /download/file-5005
framework_doc_date: 2024-04-23
sources:
- /download/file-5005
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRKM012
- https://www.anticipation-hub.org/global-overview/countries/comoros
- https://piroi.croix-rouge.fr/formation-dref-2022/?lang=en
- https://reliefweb.int/report/comoros/comoros-yellow-alert-volcanic-eruption-dref-operation-final-report-ndeg-mdrkm009
- https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-16'
extra:
  hub_captions:
  - '2024: Volcanic ash (IFRC) [American Red Cross]'
  hub_years:
  - '2024'
  implementing:
  - Comorian Red Crescent Society (CRCS)
  eap_no: sEAP2023KM01
  operation_no: MDRKM012 / PKM514
  funding_chf: >-
    CHF 210,958 pre-arranged (Readiness 37,699 + Prepositioning 99,207 + Early Action
    74,052); IFRC GO records the same figure as USD funded (nominal 1:1, not a currency
    conversion) — the Hub map API's USD 239,453 for this framework is a different
    conversion snapshot and is not used here.
  precursor: >-
    A 2022 yellow-alert volcanic-eruption DREF operation (MDRKM009) preceded and
    motivated this sEAP — CRCS applied for an anticipatory DREF when Karthala's alert
    level rose in 2022, per a PIROI DREF-training writeup; report body not independently
    verified (ReliefWeb blocks default fetch).
  partners: >-
    IFRC (Programme Support Delegate in-country + CCD Madagascar), French Red
    Cross/PIROI (technical + financial support incl. tank tarpaulins), Government of
    Comoros/Ministry of Interior (overall coordination, multisectoral response plan),
    OVK (trigger data).
  schema_strain: >-
    GO API (queried 2026-07-16) still shows this appeal "Active" with end date
    2026-04-30 — already past as of last_checked; status kept as `active` per the
    source but the record may be pending closure/renewal that hasn't posted yet.
    "American Red Cross" in the Hub caption is unconfirmed by the sEAP document itself,
    which names French Red Cross/PIROI and IFRC as partners, not American Red Cross;
    kept in extra.hub_captions as-is pending clarification.
visibility: public
---

# IFRC — Comoros volcanic ash (Karthala) sEAP

## Summary
The Comorian Red Crescent Society (CRCS)'s Simplified Early Action Protocol
(sEAP2023KM01, approved 23 April 2024) for ash from Mount Karthala, one of the world's
most active volcanoes (eruptions roughly every decade; the 1903 eruption killed ~17
people, the 2005 eruption contaminated water tanks for ~118,000 people). The sEAP
targets 12,000 people on Ngazidja (Grande Comore) with WASH, health, protection and
evacuation support, funded through the IFRC DREF anticipatory pillar. No activation
recorded since approval.

## Trigger
Karthala Volcano Observatory (OVK) monitors seismicity (7 stations) and ground
deformation (4 inclinometers), issuing three special-bulletin alert levels — yellow
(~2 weeks lead), orange (~4 days lead), red (~2 days lead). Sensitization starts at
yellow; the early-action trigger threshold is reached when CRCS receives the special
orange-alert bulletin (OVK-SB2), ~4 days before impact, releasing WASH/sanitation/
dignity-kit distribution and evacuation support; the red-alert bulletin (OVK-BS3)
triggers direct distribution of dust masks and protective glasses ahead of evacuation.
Six regions are pre-identified as highest risk: Mbadjini, Hambou, Bambao, Itsandra,
Washilli, Dimani, with priority geographic focus on Moroni.

## Funding & scope
CHF 210,958 pre-arranged (Readiness 37,699 / Prepositioning 99,207 / Early Action
74,052), funded via the IFRC DREF anticipatory pillar (IFRC GO shows the same figure
as USD funded against operation MDRKM012/PKM514). 2-year EAP timeframe from approval,
3-month operational window per activation. Targets 12,000 people, prioritizing large
households, households with under-5s, pregnant/nursing women, female-headed households,
and households with persons with disabilities. Key partners: IFRC, French Red
Cross/PIROI, Government of Comoros (Ministry of Interior).

## Activations
None recorded since sEAP approval (Apr 2024) — IFRC GO lists 0 beneficiaries against
MDRKM012 and the Anticipation Hub country page shows 0 activations to date (both
checked 2026-07-16). A 2022 yellow-alert volcanic-eruption DREF operation (MDRKM009)
predates the sEAP and is not a trigger of this framework, but is the precursor episode
that motivated its design.

## Sources
- **Authoritative:** [Simplified EAP: Comoros — Volcanic Ash](/download/file-5005) (IFRC, approved 23 Apr 2024)
- [IFRC GO — MDRKM012](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRKM012) (machine-readable status/budget)
- [Anticipation Hub — Comoros country overview](https://www.anticipation-hub.org/global-overview/countries/comoros)
- [PIROI — DREF training 2022](https://piroi.croix-rouge.fr/formation-dref-2022/?lang=en) (2022 anticipatory-DREF precursor mention)
- [ReliefWeb — Comoros yellow alert volcanic eruption DREF final report MDRKM009](https://reliefweb.int/report/comoros/comoros-yellow-alert-volcanic-eruption-dref-operation-final-report-ndeg-mdrkm009) (title/existence only; body not fetchable)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
