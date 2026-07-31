---
content_type: framework-external
framework: catholic-relief-services-hti-multiple
org: Catholic Relief Services
country_iso3: HTI
hazard: multiple
status: active
valid_until: null
trigger_summary: null
data_sources: []
prearranged_funding_usd: 80000
funding_by_source: {}
target_people: 32465
framework_doc: https://www.crs.org/global-emergency-updates/global-emergency-update-may-2024#haiti
framework_doc_date: "2024-05"
sources:
- https://www.crs.org/global-emergency-updates/global-emergency-update-may-2024#haiti
- https://www.anticipation-hub.org/experience/global-map
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/haiti
- https://www.crs.org/our-work/program-areas/emergencies/anticipatory-action
- https://www.crs.org/where-we-work/latin-america-caribbean/haiti
activations: []
last_checked: '2026-07-27'
extra:
  hub_captions:
  - '2024: Multiple (Catholic Relief Services) [Catholic Relief Services]'
  hub_years:
  - '2024'
  implementing:
  - Catholic Relief Services
  coordination: >-
    The Anticipation Hub's Haiti country page lists 3 active AA frameworks: WFP
    (~USD 5.92M, 939,504 people), OCHA/CERF's collective hurricane framework (USD 4M,
    120,000 people — see frameworks/hti-hurricanes), and this CRS framework, by far the
    smallest of the three (USD 80,000, 32,465 people). No public CRS or Hub document
    describes CRS's framework as a component of the OCHA/CERF collective framework, or
    of WFP's own AAP (external-frameworks/wfp/hti-multiple.md) — it is presented here as
    its own, independent framework for lack of any evidence otherwise, not because
    independence has been positively confirmed.
  schema_strain: >-
    No trigger document, protocol, or EAP-equivalent for this CRS framework could be
    found in public sources. The only CRS-authored source that references it at all —
    CRS's "Global Emergency Update, May 2024" (the framework_doc, matching the
    Anticipation Hub inventory's project_url exactly) — contains a single passing
    sentence naming Haiti as one of 10 countries where CRS runs AA programming, with no
    Haiti-specific hazard, indicator, threshold, lead-time, funding-source, or date
    detail. CRS's general Anticipatory Action program page
    (crs.org/our-work/program-areas/emergencies/anticipatory-action) profiles Zambia,
    Uganda, Afghanistan and the Philippines as its featured country examples but does
    not mention Haiti at all, and CRS's Haiti country page covers emergency response and
    development programming with no anticipatory-action section. The Anticipation Hub's
    activations-layer API records one Haiti activation (WFP, 2023, multiple hazards,
    512,894 people / USD 1.43M) and none attributed to CRS. All figures above
    (funding, target_people, hazard="multiple") are carried over from the Hub inventory
    record as found in the stub; they could not be corroborated or detailed further from
    CRS's own public materials. trigger_summary, data_sources, funding_by_source, and
    activations are left null/[] rather than guessed.
visibility: public
---

# Catholic Relief Services — Haiti multiple

## Summary
Catholic Relief Services (CRS) runs an anticipatory action (AA) framework in Haiti
covering multiple hazards, per the Anticipation Hub's global inventory: a USD 80,000
pre-arranged budget targeting 32,465 people, active as of the Hub's 2024 listing. It is
the smallest of Haiti's three active AA frameworks tracked by the Hub, alongside WFP's
own AAP (external-frameworks/wfp/hti-multiple.md) and the OCHA/CERF collective hurricane
framework (frameworks/hti-hurricanes). No public trigger document, protocol, or detailed
programme description for this specific CRS framework was found — see `extra.schema_strain`.

## Trigger
Not publicly documented. CRS's own materials — its May 2024 Global Emergency Update (the
only CRS document that references this framework at all) and its general Anticipatory
Action program page — do not state a hazard-specific indicator, threshold, or lead time
for Haiti. CRS more broadly describes AA as action "prior to the onset of a disaster
based on context monitoring or forecasts," and elsewhere favors multi-purpose cash
assistance as its primary anticipatory action, but neither claim is tied to Haiti
specifically in any source found.

## Funding & scope
USD 80,000 pre-arranged, targeting 32,465 people, per the Anticipation Hub inventory
record (org id 1160, project id 312) — the funding source (CRS core funds, a donor, or a
pooled facility) is not stated publicly. No breakdown by activity or sector was found.

## Activations
None known. The Anticipation Hub's activations-layer records one Haiti entry (multiple
hazards, WFP, 2023, 512,894 people, USD 1.43M) — attributed to WFP, not CRS. No CRS-Haiti
activation appears in the Hub's activation data or in CRS's own public reporting.

## Sources
- **[CRS, "Global Emergency Update, May 2024"](https://www.crs.org/global-emergency-updates/global-emergency-update-may-2024#haiti)** — the framework's `project_url` per the Anticipation Hub inventory; authoritative but contains only a one-line mention of Haiti as one of 10 CRS AA countries, no framework-specific detail
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record: org id 1160, project id 312, fetched 2026-07-10 and re-verified 2026-07-27)
- [Anticipation Hub: Haiti country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/haiti) — confirms budget/target/status and the count of 3 active Haiti frameworks (WFP, OCHA, CRS)
- [CRS: Anticipatory Action program page](https://www.crs.org/our-work/program-areas/emergencies/anticipatory-action) — general CRS AA methodology; does not mention Haiti among its featured countries
- [CRS: Haiti country page](https://www.crs.org/where-we-work/latin-america-caribbean/haiti) — CRS's general Haiti programming; no anticipatory-action section
