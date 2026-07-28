---
content_type: framework-external
framework: fao-bgd-flood
org: FAO
country_iso3: BGD
hazard: flood
status: active
valid_until: "2026"
trigger_summary: >-
  FAO does not run its own trigger — it is an implementing partner in the OCHA/CERF
  collective "Anticipatory Action Framework: Bangladesh Monsoon Floods" and activates on
  that framework's two-step GloFAS-based readiness / FFWC-based action trigger for the
  Jamuna and (since 2023) Padma basins. On activation, FAO delivers livestock feed and
  floodproof storage to farming households ahead of the flood peak.
data_sources: [GloFAS, FFWC]
prearranged_funding_usd: 595640
funding_by_source: {CERF: 595640}
target_people: null
framework_doc: https://www.unocha.org/attachments/b9e1bf90-a96b-490f-bfc7-a31e98de669d/Bangladesh%20AA%20Framework%20-%20Flood%20-%20April%202025%20-%20FINAL%20.pdf
framework_doc_date: 2025-04-25
sources:
- https://www.unocha.org/attachments/b9e1bf90-a96b-490f-bfc7-a31e98de669d/Bangladesh%20AA%20Framework%20-%20Flood%20-%20April%202025%20-%20FINAL%20.pdf
- https://www.unocha.org/publications/report/bangladesh/anticipatory-action-framework-bangladesh-monsoon-floods-2023-version
- https://www.fao.org/newsroom/story/Bangladesh-Striking-before-disaster-does/en
- https://bangladesh.un.org/en/289287-race-against-floods-bangladesh
- https://www.fao.org/emergencies/resources-repository/news/detail/Protecting-livelihood-assets-through-anticipatory-actions-in-flood-prone-communities-in-northwestern-Bangladesh/en
- https://www.anticipation-hub.org/global-overview/countries/bangladesh
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: "2020-07"
  url: https://www.fao.org/newsroom/story/Bangladesh-Striking-before-disaster-does/en
  note: >-
    First OCHA-coordinated activation (the 2020 pilot). CERF released $5.2M to FAO, WFP
    and UNFPA jointly (FAO's specific share not stated in sources reviewed); FAO reached
    ~19,000 small-scale farmers (~94,000 individuals) in the Jamuna flood plains with
    animal feed and floodproof/waterproof storage for seeds, grain and tools, funds
    disbursed within about four hours of the CERF release.
- date: "2024-07-04"
  url: https://bangladesh.un.org/en/289287-race-against-floods-bangladesh
  note: >-
    CERF released $6.2M within 16 minutes of the early-warning alert (plus $2.3M from
    partners), reaching ~430,000-600,000 people collectively ahead of the Jamuna flood
    peak. FAO's specific piece: cattle feed (50kg) and waterproof silo drums delivered to
    farming households roughly 24 hours before flooding; FAO-specific dollar figure for
    this activation not stated in sources reviewed (11,310 farming households reported
    assisted per contemporaneous coverage).
last_checked: '2026-07-22'
extra:
  hub_captions:
  - '2023: Flood (FAO) [FAO]'
  - '2024: Flood (FAO) [FAO]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - FAO
  coordination: >-
    FAO's component OF the OCHA/CERF collective "Anticipatory Action Framework: Bangladesh
    Monsoon Floods" — the collective framework itself is the OCHA portfolio page
    `frameworks/bgd-flooding` (2025-04-25 version). No independently-published FAO-only
    Bangladesh flood framework/protocol was found; this page tracks only FAO's piece:
    livestock feed and floodproof/waterproof storage of agricultural assets, delivered
    through the Government's Department of Livestock Services, funded via FAO's CERF
    allocation within the collective envelope (US$400,000 Jamuna + US$195,640 Padma =
    US$595,640 per the 2025 framework doc's funding_by_agency table).
  households_target: >-
    The 2023 framework version states FAO "will support 25,000 households" with animal
    feed at evacuation points and floodproof storage of agricultural/productive assets
    (same wording recurs across OCHA/ReliefWeb summaries of that version). This is a
    household count, not a people count, so it is not converted into `target_people`
    above. The 2025 framework PDF does not restate a people/household target for FAO
    specifically (matches the OCHA page's own note that "people targeted per activation"
    is blank in that PDF's finance table).
  schema_strain: >-
    FAO does not appear to publish its own Bangladesh-flood framework or protocol
    document; all trigger, funding-design and scope detail above is FAO's slice of the
    OCHA-facilitated collective framework document, corroborated by FAO/UN news coverage
    of the 2020 and 2024 activations. unocha.org and the 2023-version ReliefWeb/OCHA
    listing pages returned 403 to this session's fetch tool (consistent with the
    `external-frameworks/README.md` note that these hosts block default fetchers) — the
    2023-version FAO figures above are corroborated across multiple independent
    search-result excerpts of that page rather than a single direct fetch. FAO-specific dollar
    amounts actually disbursed in the 2020 and 2024 activations (as opposed to the
    pre-arranged design figure of $595,640 in the current framework) were not found
    broken out separately from the collective CERF release in public reporting.
visibility: public
---

# FAO — Bangladesh flood (component of the OCHA/CERF collective framework)

## Summary
FAO does not run an independent anticipatory-action framework for Bangladesh floods.
Instead it is one of several implementing partners (with UNFPA, UNICEF, WFP, BDRCS and
the Start Network) in the OCHA/CERF-facilitated collective **"Anticipatory Action
Framework: Bangladesh Monsoon Floods"** — the OCHA portfolio page
[`frameworks/bgd-flooding`](../../frameworks/bgd-flooding). FAO's own piece is
agricultural/livestock protection: cattle feed and floodproof, water-sealable storage for
seeds, grain and tools, delivered to at-risk farming households in the Jamuna basin (and,
since the framework's 2023 expansion, the Padma basin too) ahead of the monsoon flood
peak.

## Trigger
FAO has no trigger of its own; it activates on the collective framework's two-step
trigger — a GloFAS-based probabilistic readiness trigger (12-15 day lead time) and an
FFWC-based deterministic action trigger (3-5 day lead time) for the Jamuna and Padma
basins. See `frameworks/bgd-flooding` for the full trigger design; this page does not
duplicate that detail.

## Funding & scope
CERF-funded, within the collective envelope. Per the current (2025) framework document's
funding-by-agency table, FAO's pre-arranged allocation is **US$595,640** (US$400,000 for
the Jamuna window, US$195,640 for Padma). The 2023 framework version states FAO's target
as **25,000 households** supported with animal feed at evacuation points and floodproof
storage of agricultural/productive assets — the current PDF does not restate a
people/household target for FAO specifically (see `extra.households_target`).

## Activations
- **July 2020** (pilot, first OCHA-coordinated activation) — CERF released $5.2M jointly
  to FAO, WFP and UNFPA; FAO reached roughly 19,000 small-scale farmers (~94,000
  individuals) in the Jamuna flood plains with animal feed and floodproof/waterproof
  storage (large floating plastic drums and rope) for seeds, grain and farming tools,
  disbursed within about four hours of the CERF release.
- **4 July 2024** — CERF released $6.2M within 16 minutes of the early-warning alert
  (plus $2.3M from partners); FAO's piece delivered cattle feed (50kg per household) and
  waterproof silo drums to farming households roughly 24 hours before the Jamuna flood
  peak, reported at 11,310 farming households assisted. FAO-specific dollar figures for
  either activation were not found broken out from the collective CERF release in the
  sources reviewed.

## Sources
- **Authoritative:** [Anticipatory Action Framework: Bangladesh Monsoon Floods, 2025 version (PDF, 25 Apr 2025)](https://www.unocha.org/attachments/b9e1bf90-a96b-490f-bfc7-a31e98de669d/Bangladesh%20AA%20Framework%20-%20Flood%20-%20April%202025%20-%20FINAL%20.pdf) — same document as `frameworks/bgd-flooding`'s `framework_doc`; blocked this session's fetch tool (403), figures corroborated via that internal page's extraction and via the 2023-version listing below.
- [OCHA/ReliefWeb — Anticipatory Action Framework: Bangladesh Monsoon Floods, 2023 version](https://www.unocha.org/publications/report/bangladesh/anticipatory-action-framework-bangladesh-monsoon-floods-2023-version) (FAO 25,000-household target language; also 403'd to direct fetch, corroborated across multiple search excerpts)
- [FAO newsroom — "Bangladesh: Striking before disaster does" (2020 pilot)](https://www.fao.org/newsroom/story/Bangladesh-Striking-before-disaster-does/en)
- [UN Bangladesh — "A race against floods in Bangladesh" (2024 activation)](https://bangladesh.un.org/en/289287-race-against-floods-bangladesh)
- [FAO — Protecting livelihood assets through anticipatory actions in flood-prone communities in northwestern Bangladesh](https://www.fao.org/emergencies/resources-repository/news/detail/Protecting-livelihood-assets-through-anticipatory-actions-in-flood-prone-communities-in-northwestern-Bangladesh/en)
- [Anticipation Hub — Bangladesh country overview](https://www.anticipation-hub.org/global-overview/countries/bangladesh)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Related OCHA/CERF collective framework: [`frameworks/bgd-flooding`](../../frameworks/bgd-flooding)
