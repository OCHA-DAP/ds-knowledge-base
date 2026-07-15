---
content_type: framework-external
framework: ifrc-ner-flood
org: IFRC
country_iso3: NER
hazard: flood
status: unknown
valid_until: "2025-07"
trigger_summary: >-
  Niger Basin Authority (NBA) SATH-ORIO flood-forecast model for the Niger River at the
  Niamey gauge station: the EAP activates once the forecast/observed water level reaches
  the "orange alert" band (580-619 cm; red alert is ≥620 cm). Forecast information is
  distributed at least 72 hours (up to 4 days) before flooding, covering Niamey, Tillabéri
  and Dosso regions.
data_sources: [SATH-ORIO]
prearranged_funding_usd: 283768
funding_by_source: {DREF-FbA: 250000}
target_people: 21000
framework_doc: /download/file-5062
framework_doc_date: 2020-07-17
sources:
  - https://www.anticipation-hub.org/download/file-5062
  - https://adore.ifrc.org/Download.aspx?FileId=338579
  - https://reliefweb.int/report/niger/niger-floods-early-action-protocol-summary-eap2020ne01
  - https://reliefweb.int/report/niger/forecast-based-early-action-triggered-niger-floods-eap2020ne01
  - https://reliefweb.int/report/niger/niger-floods-early-action-protocol-activation-operations-update-operation-ndeg-mdrne027
  - https://www.anticipation-hub.org/news/niger-activates-its-early-action-protocol-for-floods
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNE027
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNE028
  - https://reliefweb.int/report/niger/imminent-floods-niger-dref-operation-mdrne028
activations:
  - date: 2022-08-31
    url: https://reliefweb.int/report/niger/forecast-based-early-action-triggered-niger-floods-eap2020ne01
    note: >-
      Only confirmed activation (operation MDRNE027). NBA forecast indicated the Niamey
      water level would reach orange alert the week of 5 Sep 2022; readiness/pre-positioning
      funds released, 80 volunteers refresher-trained, 406 people sensitized in high-risk
      Niamey neighbourhoods. A field visit on 8 Sep found the Niamey hydromet station had
      malfunctioned 28 Aug-3 Sep (producing incorrect readings); on 12 Sep the trigger was
      reassessed as a false alarm (<20% flood probability) and EAP actions were stood down
      before full distributions occurred. CHF 83,982 (early-action tranche) recorded as
      fully disbursed/closed by 30 Nov 2022 per IFRC GO.
last_checked: '2026-07-15'
extra:
  hub_captions:
  - '2022: Flood (IFRC) [Red Cross Society of Niger] [Belgian Red Cross]'
  - '2023: Flood (IFRC) [Red Cross Society of Niger]'
  - '2024: Flood (IFRC) [Red Cross Society of Niger]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - Red Cross Society of Niger
  - Belgian Red Cross
  eap_no: EAP2020NE01
  operation_no: MDRNE027
  funding_chf: >-
    CHF 250,000 DREF Forecast-based Action (FbA) allocation, split CHF 65,616 readiness +
    CHF 100,402 pre-positioning stock + CHF 83,982 early action (the tranche released on
    trigger). Approved 17 July 2020 with a stated 5-year EAP timeframe. Secondary sources
    (Anticipation Hub/IFRC operations reporting) cite a slightly different readiness split
    (~CHF 153,175/81,566) in places — likely a later revised or partial-disbursement figure;
    the EAP PDF's budget table is treated as authoritative here. USD figure in
    prearranged_funding_usd is the Anticipation Hub global-map "investment" field, which
    does not exactly match either CHF conversion (≈US$256,150 per the Hub's own 2022
    activation article) — kept as-is pending reconciliation.
  target_detail: >-
    3,000 households (~21,000 people; 1,470 in male-headed / 1,530 in female-headed
    households per the WASH sector breakdown) across Niamey, Tillabéri and Dosso regions.
    Sub-allocations: 2,000 HH for water-purification kits (aqua tabs, jerry cans), 1,000 HH
    for mosquito nets, 150 HH (~1,050 people) for emergency shelter/relocation-site support.
  coordination: >-
    NOT a component of a collective OCHA/CERF framework. A separate OCHA/CERF Niger flood
    framework exists (frameworks/ner-flooding/2025-11-04.md — CERF-funded, $5M, operated by
    OCHA Niger + the Centre for Humanitarian Data, targeting 109,156 people across 13
    communes in Dosso/Tillabéri). Both frameworks key off water levels at the same Niamey
    gauge station on the Niger River (NBA/ABN's sath.abn.ne site) but set independent
    thresholds — this EAP's 580-619 cm "orange alert" vs the OCHA framework's tiered
    530/592/604 cm (2025 version; a single 580 cm threshold in its 2024 pilot) — and run on
    separate funding mechanisms (IFRC DREF FbA vs CERF) with different operators and target
    populations. Shared data source, independently designed and triggered frameworks — not
    one framework's components.
  schema_strain: >-
    ReliefWeb report pages returned HTTP 403 to direct fetch; facts are drawn from the EAP
    summary PDF (fetched via the Anticipation Hub/adore.ifrc.org mirrors), the IFRC GO API,
    and Anticipation Hub news coverage that quote the same underlying reports. The Hub
    inventory lists activation years 2022/2023/2024, but public sources found here confirm
    only the single 31 Aug 2022 activation (MDRNE027); no sourced record of a distinct EAP
    trigger in 2023 or 2024 was found — the major 2023 Niger flood response (MDRNE028,
    started 17 Aug 2023, $497,452, 200,000 people) was a regular DREF "Imminent Floods"
    operation, not an EAP/FbA activation, per the IFRC GO API. Left as an open gap rather
    than guessed; the 2023/2024 Hub years may reflect the framework's continuous 5-year
    "active" listing rather than repeat activations. Separately, the EAP's stated 5-year
    timeframe from its 17 July 2020 approval lapsed around July 2025; no public record of a
    renewal or new-generation EAP was found, so `status`/`valid_until` are recorded as
    unknown/lapsed rather than assumed still active.
visibility: public
---

# IFRC — Niger flood

## Summary
The Red Cross Society of Niger's flood Early Action Protocol (EAP2020NE01, approved 17
July 2020, IFRC DREF Forecast-based Action pillar, developed with Belgian Red Cross
technical support). It targets communities along the Niger River basin in Niamey,
Tillabéri and Dosso regions — 3,000 households (~21,000 people) — with sandbag/dike
materials, water-purification supplies, mosquito nets and emergency shelter/evacuation
support. Its one confirmed activation, in August-September 2022, was triggered by a
forecast that later proved to be a false alarm caused by a malfunctioning water-level
station, and actions were stood down before full distribution.

## Trigger
Based on the NBA's SATH-ORIO flood-prediction model for the Niger River at Niamey, which
provides a 6-day forecast with three alert bands (yellow 550-579 cm, orange 580-619 cm,
red ≥620 cm). The EAP activates at the orange alert threshold, with forecast information
distributed at least 72 hours (up to 4 days) ahead of flooding — the lead time the
protocol's early actions (evacuation 48 hours before forecast impact, emergency shelter
set-up in the hours just before) are built around.

## Funding & scope
CHF 250,000 (≈US$0.28M per the Anticipation Hub's inventory figure; ≈US$256,150 per the
Hub's own reporting on the 2022 activation) from the IFRC DREF's Forecast-based Action
mechanism: CHF 166,018 for readiness and pre-positioning, CHF 83,982 released automatically
once the trigger is met. Targets 3,000 households (~21,000 people) across Niamey,
Tillabéri and Dosso, implemented by the Red Cross Society of Niger with Belgian Red Cross
technical support and ICRC advice on security aspects.

## Activations
- **31 August-12 September 2022 (operation MDRNE027)** — the only confirmed activation.
  An NBA forecast of the Niamey water level reaching orange alert the week of 5 September
  triggered readiness funding, refresher training for 80 volunteers, and sensitization of
  406 people in high-risk Niamey neighbourhoods. A field visit on 8 September found the
  Niamey hydromet station had malfunctioned from 28 August to 3 September, producing
  incorrect readings; on 12 September the flood probability was reassessed at under 20%
  and the EAP was stood down before full distributions took place. The CHF 83,982
  early-action tranche was recorded as fully disbursed and the operation closed by 30
  November 2022.
- No sourced evidence of a separate EAP activation in 2023 or 2024 was found, despite
  those years appearing in the Anticipation Hub's inventory listing for this framework
  (see `extra.schema_strain`). The large 2023 Niger flood response (DREF operation
  MDRNE028) was a standard emergency DREF operation, not an EAP/FbA trigger.

## Sources
- **Authoritative:** [EAP summary, EAP2020NE01, approved 17 July 2020](/download/file-5062) ([mirror](https://adore.ifrc.org/Download.aspx?FileId=338579))
- [ReliefWeb — EAP summary landing page](https://reliefweb.int/report/niger/niger-floods-early-action-protocol-summary-eap2020ne01)
- [ReliefWeb — Forecast-based early action triggered in Niger: Floods](https://reliefweb.int/report/niger/forecast-based-early-action-triggered-niger-floods-eap2020ne01) (2022 activation and stand-down)
- [ReliefWeb — EAP activation Operations update, MDRNE027](https://reliefweb.int/report/niger/niger-floods-early-action-protocol-activation-operations-update-operation-ndeg-mdrne027)
- [Anticipation Hub — Niger activates its Early Action Protocol for Floods](https://www.anticipation-hub.org/news/niger-activates-its-early-action-protocol-for-floods) (2022 activation detail)
- [IFRC GO API — MDRNE027](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNE027) (funding/dates, machine-readable)
- [IFRC GO API — MDRNE028](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNE028) (2023 "Imminent Floods" DREF operation — distinct from the EAP)
- [ReliefWeb — Imminent Floods in Niger, DREF Operation MDRNE028](https://reliefweb.int/report/niger/imminent-floods-niger-dref-operation-mdrne028)
