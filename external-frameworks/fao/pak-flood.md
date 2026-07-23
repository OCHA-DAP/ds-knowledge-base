---
content_type: framework-external
framework: fao-pak-flood
org: FAO
country_iso3: PAK
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Forecast-based: cash disbursed ahead of a predicted monsoon/riverine flood peak in
  flood-prone Sindh (and Balochistan) districts — in the one documented 2025 case,
  roughly 3 days before peak flooding reached Khairpur district. The specific hydromet
  indicator/threshold and confirmation mechanism used by FAO's own protocol were not
  in any accessible public document — see `extra.schema_strain`.
data_sources: []
prearranged_funding_usd: 310000
funding_by_source: {}
target_people: 7500
framework_doc: https://openknowledge.fao.org/items/5e176d46-9488-4aba-a9d0-045b5ef395ce
framework_doc_date: null
sources:
- https://openknowledge.fao.org/items/5e176d46-9488-4aba-a9d0-045b5ef395ce
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/pakistan
- https://www.anticipation-hub.org/experience/global-map
- https://news.fundsforngos.org/2026/06/30/pakistan-launches-first-anticipatory-action-strategy-to-reduce-climate-disaster-risks/
- https://www.nation.com.pk/04-Jul-2026/pakistan-strengthens-anticipatory-action-reduce-climate-related-disaster-impact
- https://pakobserver.net/pakistan-launches-first-anticipatory-action-strategy-to-reduce-climate-disaster-risks/
- https://www.fao.org/pakistan/news/detail-events/en/c/1711133/
activations:
- date: '2025'
  url: https://news.fundsforngos.org/2026/06/30/pakistan-launches-first-anticipatory-action-strategy-to-reduce-climate-disaster-risks/
  note: >-
    Joint WFP/FAO anticipatory cash assistance (EU-funded), US$179/PKR 50,000 per
    household, to 15,000 vulnerable people in Khairpur district, Sindh, roughly 3 days
    ahead of peak flooding during the 2025 monsoon floods — cited by WFP/FAO/the
    Anticipation Hub as the demonstration case for Pakistan's AA approach. Exact date,
    the FAO-specific share of the 15,000 people, and whether this was formally invoked
    under the framework_doc protocol vs. an ad hoc joint response were not confirmed in
    public sources — see `extra.schema_strain`.
last_checked: '2026-07-23'
extra:
  hub_captions:
  - '2024: Flood (FAO) [FAO]'
  hub_years:
  - '2024'
  implementing:
  - FAO
  partners: WFP, European Union (funder, incl. via ECHO), Government of Pakistan/NDMA,
    German development cooperation (national AA strategy); Pakistan Red Crescent
    Society/IFRC run a separate, unrelated riverine-flood EAP (see external-frameworks/ifrc/pak-flood.md)
  coordination: >-
    No matching OCHA/CERF collective AA framework found for Pakistan flood under
    frameworks/ — this reads as FAO's own framework, run jointly with WFP and
    EU-funded, not a component of an OCHA-coordinated collective framework.
  schema_strain: >-
    (1) The framework_doc item page (openknowledge.fao.org, DSpace) returns HTTP 403 to
    automated fetches, including its own bitstream/API endpoints tried repeatedly — its
    title, publication date, and the precise trigger indicator/threshold/lead-time table
    could not be verified or extracted; framework_doc_date left null rather than guessed.
    (2) prearranged_funding_usd (US$310,000) and target_people (7,500) are the
    Anticipation Hub's live "Active Frameworks" country-page figures, carried over
    unchanged from the original stub — no FAO-published document with matching figures
    was independently found, so these could not be cross-verified against a primary
    source. (3) A separate WFP/FAO Sindh resilience project (Shaheed Benazirabad
    district) is reported elsewhere as "reaching up to 7,500 households" — the
    coincidental match with target_people=7,500 (people, not households) could not be
    confirmed as the same initiative and is NOT treated as corroboration here. (4) No
    FAO-specific data source/indicator (e.g. GloFAS, a named flood-forecasting model)
    could be confirmed, unlike IFRC's PMD/FFD-bulletin-based protocol for the same
    hazard in Pakistan.
visibility: public
---

# FAO — Pakistan flood

## Summary
FAO runs a forecast-based anticipatory action framework against flood in Pakistan,
per the Anticipation Hub's 2024 global inventory (US$310,000 pre-arranged, targeting
7,500 people). It sits within a broader joint FAO–WFP anticipatory action partnership
in Pakistan, EU-funded, that has been building since at least 2023 (a December 2023
NDMA-hosted National Dialogue Platform on Anticipatory Action) and that Pakistan's
government folded into its first national Anticipatory Action Strategy, announced in
mid-2026. The clearest public evidence of the mechanism operating is a joint
WFP/FAO cash disbursement in Khairpur district, Sindh, during the 2025 monsoon floods,
delivered roughly three days ahead of peak flooding. FAO's own authoritative framework
document could not be read directly (see Sources) — the summary below is necessarily
built from secondary reporting and the Hub's inventory rather than the primary protocol
text.

## Trigger
Public sources confirm the general mechanism — pre-arranged funding released once a
forecast crosses a pre-defined threshold, ahead of the predicted flood — but not FAO's
specific indicator, gauge/basin, threshold value, or exact lead time for Pakistan. The
one concrete data point available is the 2025 Khairpur case: cash reached households
about three days before the floodwaters did. This contrasts with the separate IFRC/PRCS
riverine-flood EAP for Pakistan (external-frameworks/ifrc/pak-flood.md), whose FFD/PMD
bulletin thresholds (e.g. cusecs at named gauges) are documented in detail — no
equivalent FAO-specific detail was found. FAO's authoritative document
(openknowledge.fao.org item, linked below) consistently returned HTTP 403 to automated
fetching across several attempts (item page, its DSpace API endpoint, and bitstream
URLs), so its content could not be read to confirm or refine this.

## Funding & scope
US$310,000 pre-arranged, targeting 7,500 people, per the Anticipation Hub's current
Pakistan country listing (figures unchanged since the original stub; no independent FAO
document with matching numbers was found to cross-check them against). The broader
FAO–WFP Pakistan AA partnership is EU-funded (including past ECHO-funded FAO
emergency-agriculture response in Sindh/Balochistan) and, as of the 2026 national AA
strategy launch, also references German development-cooperation support, though funding
attribution specifically for this flood framework's $310,000 was not confirmed.

## Activations
- **2025 monsoon floods, Khairpur district, Sindh** — WFP and FAO, with EU funding,
  delivered anticipatory cash assistance of US$179 (PKR 50,000) per household to 15,000
  vulnerable people about three days before peak flooding reached the area. This is the
  event cited by WFP/FAO and the Anticipation Hub as evidence for the approach when
  Pakistan's national Anticipatory Action Strategy was announced in mid-2026. The exact
  date, FAO's specific share of the 15,000 people reached (vs. WFP's), and whether this
  was a formal invocation of the framework_doc protocol are not confirmed in public
  reporting.
- No other named activation of this specific FAO framework was found. (A separate,
  much larger FAO/ECHO emergency-agriculture response reaching 268,000 people in
  Balochistan/Sindh districts followed the 2022 floods, and a WFP-led, EU-funded
  US$3M cash response reached 180,000+ people in seven Sindh districts in the same
  recovery period — both are post-disaster response, not anticipatory action, and are
  excluded here.)

## Sources
- **Framework document (cited by the Hub, content not readable):** [FAO Anticipatory Action item, openknowledge.fao.org](https://openknowledge.fao.org/items/5e176d46-9488-4aba-a9d0-045b5ef395ce) (403 to all automated fetch attempts, 2026-07-23)
- [Anticipation Hub — Pakistan country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/pakistan) (current active-framework figures, fetched 2026-07-23)
- [Anticipation Hub — global map inventory](https://www.anticipation-hub.org/experience/global-map) (original stub source, 2026-07-10)
- [Pakistan Launches First Anticipatory Action Strategy to Reduce Climate Disaster Risks — fundsforNGOs, 2026-06-30](https://news.fundsforngos.org/2026/06/30/pakistan-launches-first-anticipatory-action-strategy-to-reduce-climate-disaster-risks/) (Khairpur 2025 activation detail, national strategy launch)
- [Pakistan strengthens anticipatory action to reduce climate-related disaster impact — The Nation, 2026-07-04](https://www.nation.com.pk/04-Jul-2026/pakistan-strengthens-anticipatory-action-reduce-climate-related-disaster-impact) (national strategy launch, partners)
- [Pakistan launches first anticipatory action strategy — Pakistan Observer](https://pakobserver.net/pakistan-launches-first-anticipatory-action-strategy-to-reduce-climate-disaster-risks/) (same story, additional outlet; not independently fetchable, corroborated via search)
- [Integrating Anticipatory Action into Pakistan's Disaster Risk Financing Systems — FAO in Pakistan](https://www.fao.org/pakistan/news/detail-events/en/c/1711133/) (general AA-financing context, largely donor-funded)
