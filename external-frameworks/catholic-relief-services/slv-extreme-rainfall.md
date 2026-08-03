---
content_type: framework-external
framework: catholic-relief-services-slv-extreme-rainfall
org: Catholic Relief Services
country_iso3: SLV
hazard: extreme-rainfall
status: active
valid_until: null
trigger_summary: null
data_sources: []
prearranged_funding_usd: 200000
funding_by_source: {}
target_people: 10000
framework_doc: null
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/global-overview/countries/el-salvador
- https://www.anticipation-hub.org/experience/global-map/global-map/active-frameworks/area-detail-44/api.json
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: '2024'
  url: null
  note: >-
    Hub country page for El Salvador lists a "Heavy rain" activation by Catholic Relief
    Services in 2024, reaching 10,000 people at $200,000 — identical to the framework's
    headline figures, consistent with a full-scale single activation rather than a
    partial one. No independent CRS/Caritas press release, report, or exact date was
    found to corroborate this beyond the Hub's own record (see `extra.schema_strain`);
    the June 2024 severe-weather/flood emergency (tropical storm Alberto, red alert,
    state of emergency 16 June) is the most plausible trigger event by timing, but no
    source explicitly ties the two.
last_checked: '2026-07-30'
extra:
  hub_captions:
  - '2024: Extreme Rainfall (Catholic Relief Services) [Catholic Relief Services] [Caritas
    of El Salvador]'
  hub_years:
  - '2024'
  implementing:
  - Catholic Relief Services
  - Caritas of El Salvador
  coordination: >-
    No matching OCHA/CERF collective AA framework found for El Salvador extreme
    rainfall/flood under frameworks/ — the repo's two OCHA-coordinated El Salvador
    entries (lac-dry-corridor, nic-drought) both cover drought, a different hazard.
    Reads as CRS/Caritas's own independent framework, not a component of an
    OCHA-coordinated one.
  schema_strain: >-
    No public EAP text, trigger document, or CRS/Caritas press release for this
    framework was found despite searching CRS's own site (crs.org and asa.crs.org both
    403 automated fetch), ReliefWeb, the Anticipation Hub 2023/2024 global overview
    reports, and the Hub's global-map JSON API/country page directly. The only public
    trace is the Hub's own inventory record (project id 344: coordinating org Catholic
    Relief Services, implementing CRS + Caritas of El Salvador, hazard "Heavy rain",
    10,000 people, $200,000) as surfaced on both the area-detail API and the El
    Salvador country overview page — trigger_summary, data_sources, funding_by_source,
    and framework_doc are left null/[] rather than guessed.
visibility: public
---

# Catholic Relief Services — El Salvador extreme rainfall

## Summary
Catholic Relief Services, implementing jointly with Caritas of El Salvador, runs an
active anticipatory action framework for heavy/extreme rainfall in El Salvador, targeting
10,000 people with a $200,000 pre-arranged investment. It is one of four active or
in-development AA frameworks the Anticipation Hub tracks for El Salvador (alongside OCHA,
IFRC, and WFP drought frameworks) and the only one addressing rainfall/flood rather than
drought. No independent public EAP document or press release describing the framework's
trigger or design was found; all confirmed facts trace to the Anticipation Hub's own
inventory.

## Trigger
Not publicly documented. No EAP text, protocol summary, or CRS/Caritas announcement
describing the indicator, threshold, or lead time was found in public sources (see
`extra.schema_strain`).

## Funding & scope
$200,000 pre-arranged investment (source organisation not identified in public sources —
`funding_by_source` left empty), targeting 10,000 people. Figures are unchanged from the
Hub's original global-map listing and are corroborated by the El Salvador country
overview page and the area-detail API record (project id 344).

## Activations
The Hub's El Salvador country page records one activation in 2024 ("Heavy rain",
Catholic Relief Services, 10,000 people, $200,000 — matching the framework's full
headline figures). No independently datable, sourced account of this activation (exact
date, URL, or narrative) was found; the June 2024 nationwide severe-weather/flood
emergency (tropical storm Alberto, red alert declared 16 June, 15-day state of emergency)
is the most plausible real-world trigger by timing, but no source explicitly links the
two, so the connection is not asserted as fact.

## Sources
- **Authoritative (only public trace of this framework):** [Anticipation Hub — El Salvador country overview](https://www.anticipation-hub.org/global-overview/countries/el-salvador) (active-frameworks and activations tables, fetched 2026-07-30)
- [Anticipation Hub global-map API — El Salvador area detail](https://www.anticipation-hub.org/experience/global-map/global-map/active-frameworks/area-detail-44/api.json) (project id 344; fetched 2026-07-30)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory listing, fetched 2026-07-10)

