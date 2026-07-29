---
content_type: framework-external
framework: unicef-nigeria-country-office-nga-flood
org: UNICEF Nigeria country office
country_iso3: NGA
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  A locally-issued flood forecast for Kaduna city (NIHSA/NiMet-based, no public river-level or
  rainfall threshold documented) triggered the pilot on 2 August 2022, when the forecast showed
  "elevated flood risk that continues in parts of Kaduna city" — releasing pre-arranged cash
  grants to ~5,000 households pre-registered (May 2022) in six flood-prone Kaduna communities.
data_sources: []
prearranged_funding_usd: 450000
funding_by_source: {ECHO: 450000}
target_people: 24850
framework_doc: https://www.unicef.org/nigeria/reports/early-action-protocol-kaduna-state-nigeria-floods
framework_doc_date: 2023-04-06
sources:
- https://www.unicef.org/nigeria/reports/early-action-protocol-kaduna-state-nigeria-floods
- https://www.unicef.org/nigeria/media/7176/file/Early%20Action%20Protocol.pdf
- https://www.climatecentre.org/9094/anticipatory-shock-responsive-social-protection-trialled-as-part-of-nigeria-flood-response/
- https://www.unicef.org/nigeria/stories/cash-transfer-brings-relief-flooding-prone-communities-kaduna-state
- https://leadership.ng/flood-unicef-red-cross-lift-5000-kaduna-households-with-n175m/
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nigeria
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2022-08-02
  url: https://www.climatecentre.org/9094/anticipatory-shock-responsive-social-protection-trialled-as-part-of-nigeria-flood-response/
  note: >-
    Local forecast trigger fired for Kaduna city; NRCS (with UNICEF, IFRC and the Climate
    Centre) disbursed ₦35,000 (~€80) cash grants to all 5,000 pre-registered households in
    six flood-prone communities (Narayi, Romi, Nasarawa, Kigo, Bashama, Kabala West) across
    Chikun, Kaduna North and Kaduna South LGAs — ₦175m total, first week of August 2022.
    Described by the Climate Centre as only the second RCRC-involved anticipatory
    cash-transfer exercise worldwide (after Nepal, 2021).
last_checked: '2026-07-29'
extra:
  hub_captions:
  - '2023: Flood (UNICEF Nigeria country office) [IFRC] [Nigerian Red Cross Society] [Red
    Cross Red Crescent Climate Centre]'
  hub_years:
  - '2023'
  implementing:
  - IFRC
  - Nigerian Red Cross Society
  - Red Cross Red Crescent Climate Centre
  partners: United Bank for Africa (cash disbursement partner)
  target_reconciliation: >-
    5,000 households × Kaduna average household size ≈ the Hub's 24,850-people figure.
    ₦175,000,000 disbursed directly as cash grants ≈ USD 405,000-417,000 at Aug 2022 rates
    (~₦420-430/USD) — close to but not identical to the Hub's USD 450,000 investment figure,
    which likely includes programme costs (registration, logistics, Red Cross delivery)
    beyond the direct cash-transfer amount. No single public document breaks out the full
    budget line by line.
  coordination: >-
    Distinct from two other Nigeria flood AA instruments that partly overlap in name only:
    (1) the OCHA/CERF collective "Anticipatory Action Framework: Nigeria — Floods"
    (`frameworks/nga-flooding`), which covers riverine flooding along the Niger/Benue rivers
    in Adamawa state via a GloFAS/gauge trigger, funded by CERF and the Nigeria Humanitarian
    Fund — geographically and institutionally separate from this Kaduna pilot; (2) IFRC's own
    national simplified EAP (EAP2022NG01 / MDRNG035, DREF-funded CHF 220,000, a 26-gauge
    river-network trigger at 5-year return period with 4-day lead time, targeting ~7,500
    people across Adamawa, Kaduna, Kwara, Akwa Ibom, Bayelsa, Benue, Nasarawa, Delta, Kano,
    Yobe and Taraba) — also Nigerian-Red-Cross-implemented but a separate DREF operation from
    the ECHO-funded pilot this page describes. A further, unrelated DREF (MDRNG034, CHF
    ~140,000) supported anticipatory action for 35,000 people in Anambra, Cross River, Kebbi,
    Kogi and Ondo in 2022. Treat this page as covering only the UNICEF/ECHO-funded Kaduna
    shock-responsive social protection pilot.
  schema_strain: >-
    No public source states a river-level, rainfall, or forecast-probability threshold for
    the local Kaduna trigger (unlike IFRC's national sEAP, which documents a 26-gauge/5-year
    return period/4-day lead design) — `data_sources` left empty and `trigger_summary` kept
    to what the Climate Centre reported. `status` kept as `active` on the strength of UNICEF's
    2023 planning documents (which still budgeted shock-responsive social protection and cash
    transfer targets for Kaduna, later revised down in an August 2023 HAC revision), but no
    evidence of a repeat trigger/activation after Aug 2022 was found; could plausibly be
    `inactive`/`unknown` if the pilot was not renewed past 2023.
visibility: public
---

# UNICEF Nigeria country office — Nigeria flood

## Summary
A shock-responsive social protection pilot for flood-affected communities in Kaduna city,
funded by the EU's humanitarian aid office (ECHO) and delivered by the Nigerian Red Cross
Society (NRCS) with technical support from IFRC and the Red Cross Red Crescent Climate
Centre, and programmatic partnership from UNICEF. It pre-registered 5,000 vulnerable
households in six flood-prone Kaduna communities and released unconditional cash grants when
a local flood forecast fired in August 2022 — described at the time as only the second
Red-Cross-involved anticipatory cash exercise carried out anywhere in the world. It is
distinct from Nigeria's other flood AA instruments run by OCHA/CERF and by IFRC's own
national DREF-funded protocol (see `extra.coordination`).

## Trigger
A locally-issued flood forecast for Kaduna city (drawing on Nigerian Hydrological Services
Agency/Nigerian Meteorological Agency information, per UNICEF and Climate Centre reporting)
showed "elevated flood risk that continues in parts of Kaduna city" on 2 August 2022,
triggering release of pre-arranged cash grants to households pre-identified in May 2022
through a combination of vulnerability criteria (poverty, gender, disability, age, prior
flood exposure) and Climate Centre flood-risk mapping. No public document gives a specific
river-level, rainfall, or forecast-probability threshold or lead time for this local trigger.

## Funding & scope
ECHO-funded; the Nigerian Red Cross disbursed ₦35,000 (~€80) per household to all 5,000
registered households (₦175,000,000 ≈ USD 405,000-417,000 at 2022 rates) in six communities
(Narayi, Romi, Nasarawa, Kigo, Bashama, Kabala West) across Chikun, Kaduna North and Kaduna
South LGAs. The Anticipation Hub's own figures for this framework are USD 450,000 invested
and 24,850 people targeted — consistent with the ~5,000 households once average household
size is applied, though the extra ~$35-45k above the reported cash-grant total is not
itemised in any public source (likely registration/logistics/delivery costs). UNICEF's 2023
humanitarian planning documents initially budgeted a scale-up (8,500 households for
shock-responsive social protection, 18,000 for humanitarian cash transfers generally) before
revising down in an August 2023 revision (3,000 and 7,600 households respectively).

## Activations
- **2 August 2022** — local forecast trigger fired for Kaduna city; NRCS (with UNICEF, IFRC
  and the Climate Centre) disbursed cash grants to all 5,000 pre-registered households across
  the six target communities, ₦175m total, in the first week of August 2022.
- No further public evidence of a repeat trigger/activation after 2022 was found, despite the
  Hub listing "2023" as an active year for this framework (likely reflecting the April 2023
  publication of the retrospective EAP document, or continued 2023 programme planning, rather
  than a second trigger event).

## Sources
- **Authoritative:** [Early Action Protocol — Kaduna State, Nigeria (UNICEF Nigeria, published 6 Apr 2023)](https://www.unicef.org/nigeria/reports/early-action-protocol-kaduna-state-nigeria-floods) ([PDF](https://www.unicef.org/nigeria/media/7176/file/Early%20Action%20Protocol.pdf))
- [Red Cross Red Crescent Climate Centre — "Anticipatory shock-responsive social protection trialled as part of Nigeria flood response"](https://www.climatecentre.org/9094/anticipatory-shock-responsive-social-protection-trialled-as-part-of-nigeria-flood-response/) (contemporaneous account of the Aug 2022 trigger/disbursement)
- [UNICEF Nigeria — "Cash transfer brings relief to flooding-prone communities in Kaduna State"](https://www.unicef.org/nigeria/stories/cash-transfer-brings-relief-flooding-prone-communities-kaduna-state)
- [Leadership (Nigeria) — "Flood: UNICEF, Red Cross Lift 5,000 Kaduna Households With N175m" (9 Aug 2022)](https://leadership.ng/flood-unicef-red-cross-lift-5000-kaduna-households-with-n175m/)
- [Anticipation Hub — Nigeria country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nigeria) (framework listing, funding/target figures)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Related OCHA/CERF collective framework: [`frameworks/nga-flooding`](../../frameworks/nga-flooding) (different geography/instrument, see `extra.coordination`)
