---
content_type: framework-external
framework: ifrc-eth-drought
org: IFRC
country_iso3: ETH
hazard: drought
status: active
valid_until: 2028-09-30
trigger_summary: >-
  Two-stage. First trigger: seasonal forecast of below-normal rainfall reaching ≥45%
  drought probability across ≥50% of a target zone's area (e.g. East Bale/Oromia,
  Shebelle/Somali) — releases the first early-action tranche (~15 days of activities).
  Second trigger: >50% forecast crop-yield reduction in the same woredas, evidenced by
  below-average rainfall plus NDVI and WRSI below their long-term mean — releases a
  second tranche for a further ~1-month implementation window.
data_sources: [NDVI, WRSI]
prearranged_funding_usd: 566881
funding_by_source: {DREF-anticipatory: 566881}
target_people: 70000
framework_doc: /download/file-3815
framework_doc_date: 2023-09-12
sources:
  - https://reliefweb.int/report/ethiopia/ethiopia-drought-early-action-protocol-summary-eap-no-eap2023et02-operation-no-mdret033
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRET033
  - https://reliefweb.int/report/ethiopia/ethiopia-drought-early-action-protocol-notification-09092024-eap-no-eap2022et02-operation-no-mdret033
  - https://reliefweb.int/report/ethiopia/ethiopia-drought-eap-early-action-protocol-activation-18112025-eap-no-eap2022et02-operation-no-mdret033
  - https://www.anticipation-hub.org/news/the-ethiopian-red-cross-society-acts-to-anticipate-the-impacts-of-drought
  - https://www.anticipation-hub.org/news/the-ethiopian-red-cross-society-begins-anticipatory-actions-ahead-of-a-drought
  - https://www.climatecentre.org/16359/ethiopian-red-cross-triggers-last-part-of-two-stage-early-action-protocol/
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2024-09-16
    url: https://reliefweb.int/report/ethiopia/ethiopia-drought-early-action-protocol-notification-09092024-eap-no-eap2022et02-operation-no-mdret033
    note: >-
      First-trigger activation — seasonal forecast showed ~45% drought probability across
      East Bale (Oromia) and Shebelle (Somali) zones; CHF 207,302 released for ~14,000
      households (~70,000 people); 15 days of rangeland/fodder management, water
      conservation and cash-for-work.
  - date: 2025-11-18
    url: https://reliefweb.int/report/ethiopia/ethiopia-drought-eap-early-action-protocol-activation-18112025-eap-no-eap2022et02-operation-no-mdret033
    note: >-
      Second-trigger activation — >50% forecast crop-yield reduction plus below-average
      rainfall/NDVI/WRSI in Rayitu and Seweyna woredas (East Bale Zone, Oromia); CHF
      141,672 (~US$175,000) released for ~35,000 people; livestock vaccination, cash for
      animal feed, WASH, and cash/food-for-work.
last_checked: '2026-07-14'
extra:
  hub_captions:
  - '2023: Drought (IFRC) [Ethiopian Red Cross Society]'
  - '2024: Drought (IFRC) [Ethiopian Red Cross Society]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Ethiopian Red Cross Society
  eap_no: EAP2023ET02 (authoritative summary doc) / EAP2022ET02 (later ReliefWeb
    notification and activation reports) — same operation MDRET033; EAP numbers persist
    oddly across revisions, both recorded per the known IFRC pattern.
  operation_no: MDRET033
  funding_chf: "CHF 499,422 pre-arranged per the DREF appeal (fully funded): 292,120
    readiness/prepositioning + 207,302 first-trigger tranche; USD figure is an
    approximate Hub-inventory conversion (~1.135 CHF/USD)."
  coordination: >-
    OCHA/CERF runs a separate, independently-funded collective AA framework for Ethiopia
    drought (see frameworks/eth-drought/ — CERF, $20M, endorsed 2020-12-07, now retired;
    a redesign was in development as of 2026-06-09). No public evidence of operational
    coordination between that CERF framework and this IFRC/ERCS DREF-funded EAP: different
    funders, different trigger designs (SEAS5 zone-count vs rainfall-probability +
    crop-yield), and no ERCS/IFRC mention in the OCHA framework pages. Treated as
    independent, not a component of the OCHA collective.
  schema_strain: >-
    Whether the 2025-11-18 second-trigger activation belongs to the same Bega-season
    cycle as the 2024-09-16 first-trigger notification, or a separate subsequent season,
    is not stated explicitly in any source found — recorded as two distinct dated
    activation events per the public record rather than inferred as one continuous cycle.
visibility: public
---

# IFRC — Ethiopia drought

## Summary
The Ethiopian Red Cross Society's (ERCS) drought Early Action Protocol, validated by
IFRC and pre-financed by the DREF Anticipatory Pillar (appeal MDRET033, active through
2028). A two-stage design: an early tranche on a seasonal drought-probability forecast,
and a second, larger-reach tranche if forecast crop-yield losses subsequently confirm
the drought — targeting pastoralist woredas in Oromia and Somali regions.

## Trigger
**First trigger** (rainfall-forecast based): a seasonal forecast of below-normal
precipitation reaching ≥45% drought probability across at least half of a target zone's
area (documented for East Bale zone, Oromia, and Shebelle zone, Somali Region) releases
the first early-action tranche — about 15 days of activities (rangeland/fodder
management, water conservation, cash-for-work) ahead of the Bega (OND) dry season.
**Second trigger** (crop-yield based): a forecast of >50% crop-yield reduction in the
same woredas, corroborated by below-average rainfall together with NDVI and WRSI values
below their long-term mean, releases a second tranche for a further ~1-month window of
livestock, WASH, and cash/food-for-work support. Exact numeric lead times are not stated
in the public documents found.

## Funding & scope
CHF 499,422 pre-arranged via DREF (≈US$566,881): CHF 292,120 for readiness and
prepositioning, CHF 207,302 for the first-trigger early-action tranche. Overall EAP
target is ~70,000 people (~14,000 households); individual activations to date have
reached subsets of that population (14,000 households in 2024; 35,000 people in the
Rayitu/Seweyna 2025 activation).

## Activations
- **Sept 2024 — first trigger.** ~45% drought probability forecast across East
  Bale/Shebelle zones; CHF 207,302 released for ~14,000 households.
- **Nov 2025 — second trigger.** >50% forecast crop-yield reduction in Rayitu and
  Seweyna woredas (East Bale Zone, Oromia); CHF 141,672 (~US$175,000) released for
  ~35,000 people — livestock vaccination, cash for animal feed, WASH, and cash/food-for-work.

No non-activation (trigger-not-met) events were found in public reporting.

## Sources
- **Authoritative:** [EAP summary EAP2023ET02 / MDRET033, 12 Sept 2023](https://reliefweb.int/report/ethiopia/ethiopia-drought-early-action-protocol-summary-eap-no-eap2023et02-operation-no-mdret033) ([Hub PDF](/download/file-3815))
- [IFRC GO — MDRET033](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRET033) (machine-readable status/budget — $499,422 fully funded, 70,000 beneficiaries, active through 2028-09-30)
- [First-trigger notification, 16 Sept 2024 (EAP2022ET02/MDRET033)](https://reliefweb.int/report/ethiopia/ethiopia-drought-early-action-protocol-notification-09092024-eap-no-eap2022et02-operation-no-mdret033)
- [Second-trigger activation, 18 Nov 2025 (EAP2022ET02/MDRET033)](https://reliefweb.int/report/ethiopia/ethiopia-drought-eap-early-action-protocol-activation-18112025-eap-no-eap2022et02-operation-no-mdret033)
- Anticipation Hub news: [first-trigger activation](https://www.anticipation-hub.org/news/the-ethiopian-red-cross-society-acts-to-anticipate-the-impacts-of-drought), [second-trigger activation](https://www.anticipation-hub.org/news/the-ethiopian-red-cross-society-begins-anticipatory-actions-ahead-of-a-drought)
- [Red Cross Red Crescent Climate Centre write-up](https://www.climatecentre.org/16359/ethiopian-red-cross-triggers-last-part-of-two-stage-early-action-protocol/)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
