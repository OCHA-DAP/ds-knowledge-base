---
content_type: framework-external
framework: action-against-hunger-phl-tropical-cyclone
org: Action against hunger
country_iso3: PHL
hazard: tropical-cyclone
status: active
valid_until: null
trigger_summary: null
data_sources: []
prearranged_funding_usd: null
funding_by_source: {}
target_people: 21000
framework_doc: null
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/experience/global-map
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/philippines
- https://care-philippines.org/2025/10/03/access-renewed-commitment-to-timely-dignified-humanitarian-aid/
- https://actionagainsthunger.ph/tag/echo/
- https://actionagainsthunger.ph/25-years-of-action-against-hunger-in-the-philippines-carrying-hunger-solutions-into-2026/
activations: []
last_checked: '2026-07-29'
extra:
  hub_captions:
  - '2024: Cyclone / Typhoon / Hurricane (Action against hunger) [ACCORD] [CARE International]
    [Humanity & Inclusion] [Oxfam] [Plan International] [Save the Children]'
  hub_years:
  - '2024'
  implementing:
  - ACCORD
  - CARE International
  - Humanity & Inclusion
  - Oxfam
  - Plan International
  - Save the Children
  coordination: >-
    No independent Action Against Hunger framework/protocol document for Philippine
    tropical cyclones was found in public sources — only the Hub inventory record itself
    (coordinating org "Action against hunger", 21,000 people, 2024 listing). The
    implementing-partner bracket (ACCORD, CARE International, Humanity & Inclusion,
    Oxfam, Plan International, Save the Children) matches almost exactly the INGO
    membership of ACCESS, an ECHO-funded multi-year, multi-hazard (conflict/flood/typhoon)
    rapid-response and disaster-preparedness consortium of 14 local and international
    organisations in the Philippines (Action Against Hunger and CARE Philippines among
    the co-leads; CARE-led ACCESS 1 ran 2023-2025, reaching 200,000+ people; ACCESS 2
    runs 2025-2027, targeting 350,000 more). This overlap is suggestive but NOT
    confirmed by any document that names this specific Hub record as ACCESS's
    typhoon slice. ACCESS's own public description of its mechanism ("teams mobilize
    within 24 to 72 hours once it is safe") reads as a post-hazard rapid-response
    trigger, not a pre-landfall forecast trigger — so it is unclear whether this
    record reflects classic ex-ante anticipatory action or a broader rapid-response
    programme tagged under the cyclone hazard by the Hub. Separately, Oxfam and Plan
    International also appear (unreconciled, no amounts) among the ~US$4M partner
    co-financing sources of the OCHA/CERF collective framework `frameworks/phl-storms`
    (2025-10-03 version) — raising a possible but unconfirmed double-counting risk
    between that collective framework's NGO co-financing and this Hub record. Treat
    both connections as leads for a future enrichment pass, not established fact.
  schema_strain: >-
    No Action-Against-Hunger-published or ACCESS-published document specifying a
    forecast indicator, threshold, or lead time for typhoons was found. The Anticipation
    Hub's Philippines country page (fetched 2026-07-29) lists Start Network, FAO,
    World Vision International, and IFRC as separate framework entries for the
    Philippines but does not surface "Action against hunger" as a standalone line —
    this record appears to exist only in the underlying global-map API data captured
    by the repo's Hub-ingest pipeline (`fetch_hub_inventory.py`), not in the Hub's
    rendered country page. No funding figure (prearranged_funding_usd) is available
    from the same source that gave `target_people: 21000`. trigger_summary, funding,
    framework_doc, and activations are therefore left null/[] rather than guessed.
visibility: public
---

# Action against hunger — Philippines tropical cyclone

## Summary
The Anticipation Hub's global-map inventory lists a 2024 tropical-cyclone/typhoon
anticipatory-action record for the Philippines coordinated by Action Against Hunger,
targeting an estimated 21,000 people, implemented alongside ACCORD, CARE International,
Humanity & Inclusion, Oxfam, Plan International, and Save the Children. No independent
Action-Against-Hunger-published framework document, trigger, funding breakdown, or
activation could be confirmed in public sources. The implementing-partner list closely
matches the INGO membership of ACCESS, an ECHO-funded multi-hazard rapid-response and
preparedness consortium active in the Philippines since 2023 (see `extra.coordination`
for the caveats on this link — it is a plausible lead, not a confirmed identification).

## Trigger
Not documented in public sources. No Action-Against-Hunger- or ACCESS-published
forecast indicator, threshold, or lead time for typhoons was found. ACCESS's own
public materials describe a rapid-response mechanism that mobilizes "within 24 to 72
hours once it is safe" — language consistent with post-hazard rapid response rather
than a pre-landfall forecast trigger, so it is not established that this Hub record
even describes classic ex-ante anticipatory action.

## Funding & scope
The Anticipation Hub inventory records ~21,000 people targeted (2024 listing); no
pre-arranged funding figure or funding source is available from the same record. If
this record does correspond to ACCESS, the wider (all-hazard) programme figures are:
ACCESS 1 (2023-2025) reached 200,000+ people; ACCESS 2 (2025-2027) targets 350,000
more — but these are whole-of-programme totals across conflict, flood, and typhoon
response, not a typhoon-specific or forecast-triggered AA budget.

## Activations
None known. No public source describes a triggered activation of this specific
record; ACCESS materials describe general rapid-response deployments (e.g. cash,
food, WASH) following typhoons and other hazards, but not a named forecast-based
pre-landfall activation.

## Sources
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record: coordinating org "Action against hunger", 21,000 people, 2024 listing; fetched 2026-07-10) — authoritative for the core facts on this page.
- [Anticipation Hub — Philippines country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/philippines) (fetched 2026-07-29) — lists Start Network, FAO, World Vision International, and IFRC as the Philippines' rendered framework entries; does not show this record separately.
- [ACCESS: Renewed Commitment to Timely, Dignified Humanitarian Aid](https://care-philippines.org/2025/10/03/access-renewed-commitment-to-timely-dignified-humanitarian-aid/) (CARE Philippines, 3 Oct 2025) — ACCESS consortium membership (incl. Action Against Hunger, ACCORD, CARE, Humanity & Inclusion, Oxfam, Plan International, Save the Children), phase timelines and reach figures.
- [Action Against Hunger Philippines — ECHO tag](https://actionagainsthunger.ph/tag/echo/) — ACCESS project description, target regions (Mindanao, Bohol), rapid-response mechanism.
- [25 Years of Action Against Hunger in the Philippines](https://actionagainsthunger.ph/25-years-of-action-against-hunger-in-the-philippines-carrying-hunger-solutions-into-2026/) — organisational history of AAH's Philippines typhoon response (Haiyan, Odette, Kristine/Trami, Tino, Uwan) without a named pre-arranged AA framework.
- Cross-reference: [`frameworks/phl-storms`](../../frameworks/phl-storms) — the separate OCHA/CERF collective framework for the same hazard; Oxfam and Plan International appear (unreconciled) among its NGO co-financing partners.

