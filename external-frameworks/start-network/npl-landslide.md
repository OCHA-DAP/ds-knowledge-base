---
content_type: framework-external
framework: start-network-npl-landslide
org: START
country_iso3: NPL
hazard: landslide
status: active
valid_until: null
trigger_summary: null
data_sources: []
prearranged_funding_usd: 43292
funding_by_source: {}
target_people: 1500
framework_doc: null
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nepal
- https://www.anticipation-hub.org/experience/global-map
- https://www.crs.org/where-we-work/asia/nepal
- https://startnetwork.org/funds/global-start-fund/alerts/n-22-nepal-anticipation-landslide-jajarkot-and-rukum
- https://plan-international.org/uploads/sites/79/2023/06/HDPRP.pdf
activations:
- date: "2022"
  url: https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nepal
  note: >-
    Per the Anticipation Hub's Nepal country page, the framework activated in 2022,
    reaching 2,063 people with US$78,003 disbursed (above the framework's 1,500-person /
    US$43,292 pre-arranged baseline). Exact trigger date, the specific district(s)
    affected, and an activation report were not found in public sources.
last_checked: '2026-07-28'
extra:
  hub_stub_removed: true
  hub_captions:
  - '2022: Landslide (Start Network) [Cordaid] [Catholic Relief Services]'
  hub_years:
  - '2022'
  implementing:
  - Cordaid
  - Catholic Relief Services
  districts_crs: >-
    Catholic Relief Services describes its own piece of this consortium as "Landslide
    Anticipatory Action" projects in Gorkha, Taplejung, Jajarkot and Rukum (West) —
    per CRS's Nepal country page. This is CRS's stated area of operation, not
    necessarily the full geographic footprint of the combined Start
    Network/Cordaid/CRS framework (Cordaid's districts were not identified).
  related_ews_tool: >-
    A digital "Anticipatory Action" tool integrating a Community Based Landslide Early
    Warning System (CBLEWS) and a Household Disaster Preparedness and Response Plan
    (HDPRP) was developed for Nepal landslides with support from Start Network, Plan
    International, NAXA Pvt. Ltd and the Institute of Himalayan Risk Reduction (IHRR).
    It plausibly relates to this framework's trigger/preparedness mechanism given the
    shared Start Network involvement, but no source confirms the two are the same
    instrument, and the source PDF (plan-international.org) returned HTTP 403 to
    automated fetch — content here is drawn from search-engine snippets only, not a
    direct read.
  related_later_alert: >-
    A separate Start Fund alert, "N-22 Nepal (Anticipation Landslide in Jajarkot and
    Rukum)", concerns rainfall-induced landslide risk on slopes destabilised by the
    November 2023 Jajarkot-Rukum earthquake — i.e. a later (2023/2024) event, not the
    2022 activation recorded above. It overlaps geographically with CRS's Jajarkot/Rukum
    West operating area. Relationship to this framework (same instrument re-alerted, vs.
    a distinct one-off Start Fund alert) is unconfirmed: the Start Network alert page
    returned HTTP 403 to automated fetch, so no date, funding or outcome figures could be
    verified — not added to `activations` pending confirmation.
  coordination: >-
    Independent of the OCHA/CERF collective "Nepal Anticipatory Action Framework for
    Floods" (`frameworks/npl-flooding`), which covers a different hazard (river flooding
    in the Koshi/Karnali basins) — no coordination relationship found between the two.
  schema_strain: >-
    No authoritative framework/EAP document was located for this Start Network/Cordaid/CRS
    instrument (unlike, e.g., IFRC's Nepal flood sEAP, which has a citable PDF) —
    `framework_doc` left null. The specific trigger indicator, threshold and lead time
    were likewise not found in public sources — `trigger_summary` left null rather than
    guessed; see `extra.related_ews_tool` for the closest public description of a
    landslide early-warning mechanism involving Start Network in Nepal. startnetwork.org
    returned HTTP 403 to every automated fetch attempted (alert pages, fund pages),
    limiting verification to search-engine snippets and the Anticipation Hub's own
    country-page tables.
visibility: public
---

# START — Nepal landslide

## Summary
A landslide anticipatory-action framework in Nepal coordinated by the Start Network,
implemented through a consortium of Cordaid and Catholic Relief Services (CRS), per the
Anticipation Hub's global inventory (listed since 2022). It targets 1,500 people with
US$43,292 pre-arranged funding. CRS's own share of the work covers landslide-prone
districts in Gorkha, Taplejung, Jajarkot and Rukum (West). The framework activated once,
in 2022, reaching 2,063 people with US$78,003 disbursed — above its baseline scale. Public
documentation of this specific instrument is thin: no authoritative framework/EAP document
or specific trigger threshold could be located (see `extra.schema_strain`).

## Trigger
Not confirmed in public sources: no specific indicator, threshold or lead time for this
framework could be found. The closest related public material is a Start
Network/Plan-International-supported digital tool for Nepal landslides that pairs a
Community Based Landslide Early Warning System (CBLEWS) with a Household Disaster
Preparedness and Response Plan (HDPRP), built with NAXA Pvt. Ltd and the Institute of
Himalayan Risk Reduction (IHRR) — but no source confirms this tool is the trigger
mechanism for this particular Start Fund framework (`extra.related_ews_tool`).

## Funding & scope
US$43,292 pre-arranged, targeting 1,500 people (Anticipation Hub inventory figures;
funding split between Cordaid and CRS not published). CRS describes its own operating
area as Gorkha, Taplejung, Jajarkot and Rukum (West) districts (`extra.districts_crs`);
Cordaid's districts were not identified in public sources.

## Activations
- **2022** — activated, reaching 2,063 people with US$78,003 disbursed (Anticipation Hub
  Nepal country page). Exact date, trigger conditions and a dedicated activation report
  were not found in public sources.

A separate, later Start Fund alert for rainfall-induced, co-seismic landslide risk in
Jajarkot and Rukum West (following the November 2023 earthquake) may relate to this same
framework, but could not be confirmed or dated — see `extra.related_later_alert`.

## Sources
- **Authoritative:** none located — no citable framework/EAP document was found for this
  instrument (`extra.schema_strain`).
- [Anticipation Hub — Anticipatory action in Nepal](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nepal) (country page; active-framework and 2022-activation figures)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
- [CRS — Nepal](https://www.crs.org/where-we-work/asia/nepal) (implementing districts for CRS's share of the consortium)
- [Start Network — N-22 Nepal (Anticipation Landslide in Jajarkot and Rukum)](https://startnetwork.org/funds/global-start-fund/alerts/n-22-nepal-anticipation-landslide-jajarkot-and-rukum) (later, unconfirmed-relationship alert; page not machine-fetchable, HTTP 403)
- [Plan International — Anticipatory Action tool (CBLEWS/HDPRP)](https://plan-international.org/uploads/sites/79/2023/06/HDPRP.pdf) (related landslide EWS tool; PDF not machine-fetchable, HTTP 403)
- Related OCHA/CERF collective framework (different hazard, no coordination link found): [`frameworks/npl-flooding`](../../frameworks/npl-flooding)
