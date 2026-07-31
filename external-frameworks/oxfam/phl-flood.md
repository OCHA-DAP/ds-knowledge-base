---
content_type: framework-external
framework: oxfam-phl-flood
org: Oxfam
country_iso3: PHL
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  No single published trigger document was found; public reporting describes at least two
  overlapping, project-based flood triggers rather than one framework. In Cotabato City
  barangays (SUPPA/ACCESS lineage), residents report rising water levels and impending
  flood-warning signals to barangay officials, who assess and authorise pre-positioned cash
  transfers before water peaks (~4-day lead time observed in a 2020 activation). In Dolores,
  Eastern Samar (SHARPER/B-READY lineage with SIKAT Inc.), an institutionalized municipal
  "flood trigger index" combining weather forecasts, local knowledge and historical data
  authorises local-government-funded pre-emptive cash transfers. Neither trigger's specific
  thresholds (rainfall/gauge levels, forecast probabilities) were found in public sources.
data_sources: []
prearranged_funding_usd: 7840
funding_by_source: {}
target_people: 1150
framework_doc: null
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/experience/global-map
- https://oxfam.org.ph/what-we-do/anticipatory-action/
- https://oxfam.org.ph/echo-funded-project-strengthens-cotabato-villages-pre-disaster-response/
- https://oxfam.org.ph/flood-assistance-helps-poor-bangsamoro-families-avoid-debt/
- https://oxfam.org.ph/852-families-receive-cash-assistance-in-dolores-e-samar-before-floods-hit/
- https://www.oxfamamerica.org/explore/countries/philippines/
- https://oxfam.org.ph/2000-families-receive-assistance-to-combat-anticipated-el-nino-impacts-in-barmm-2/
- https://pia.gov.ph/gender-responsive-anticipatory-action-to-boost-disaster-response-in-barmm/
- https://care-philippines.org/2024/08/19/access-gets-%E2%82%B176-million-from-eu-for-mindanao-flood-aid/
- https://reliefweb.int/report/philippines/access-gets-76-million-eu-mindanao-flood-aid
- https://oxfam.org.ph/over-190000-affected-by-barmm-floods-oxfam-partners-launch-emergency-response/
activations:
- date: '2020'
  url: https://www.oxfamamerica.org/explore/countries/philippines/
  note: >-
    After a forecast of heavy rains, Oxfam (with local partners, ECHO-funded SUPPA-lineage
    project) disbursed cash to 852 families in five flood-prone villages near Cotabato
    City roughly four days before ~6 feet of floodwater inundated the area. Exact date,
    trigger threshold and total funding not found in public sources.
- date: 2023-11-18
  url: https://oxfam.org.ph/852-families-receive-cash-assistance-in-dolores-e-samar-before-floods-hit/
  note: >-
    A shear line and low-pressure area (which went on to cause flash floods in Eastern
    and Northern Samar) triggered the Dolores, Eastern Samar municipal flood trigger
    index (SHARPER project, partner SIKAT Inc.); the local government
    disbursed PHP 1,500 (~US$27) each to 852 families in flood-prone barangays. Matches
    the Hub's "2023: Flood (Oxfam) [Sikat Inc.]" listing.
last_checked: '2026-07-31'
extra:
  hub_captions:
  - '2023: Flood (Oxfam) [Sikat Inc.]'
  - '2024: Flood (Oxfam) [Humanity & Inclusion] [Community Organizers Multiversity] [Oxfam]'
  hub_years:
  - '2023'
  - '2024'
  implementing:
  - Humanity & Inclusion
  - Community Organizers Multiversity
  - Oxfam
  coordination: >-
    Not a component of an OCHA/CERF collective framework — the Philippines' OCHA/CERF AA
    portfolio (`frameworks/phl-storms`) covers tropical cyclones, not floods, and Oxfam is
    not listed as an implementing partner there. This flood work sits instead across two
    (or more) overlapping, Mindanao/BARMM-focused, EU(ECHO)-funded NGO consortia that are
    not clearly disentangled in public reporting: (1) SUPPA ("Strengthening Urban
    Preparedness through Pre-emptive Action") in Cotabato City barangays, with Oxfam,
    IDEALS Inc., PDRRN and Humanity & Inclusion; and (2) the wider ACCESS consortium
    (14-16 orgs including Oxfam, Humanity & Inclusion and Community Organizers
    Multiversity), active in Mindanao since 2023 across floods, typhoons and conflict,
    which overlaps with the separate SUPREME BARMM consortium (same three orgs plus
    others) built around BARMM READi/PDRA Group AA triggers for tropical cyclones,
    flooding and El Niño. Separately, the Eastern Samar/Catanduanes SHARPER/B-READY
    project (partners SIKAT Inc., PDRRN, Plan International) runs a distinct,
    LGU-institutionalized flood-and-typhoon trigger with no evident link to the Mindanao
    consortia.
  funding_note: >-
    The Hub inventory figures used above ($7,840 pre-arranged, 1,150 people targeted)
    could not be reconciled against any single public source: known related funding
    figures are an EU/ECHO grant of ₱76 million (~€1.2M) to the wider ACCESS consortium
    for an August 2024 Mindanao flood response (not clearly anticipatory, and split
    across many hazards/sectors and organisations, not Oxfam-flood-specific), and a
    local-government-funded PHP 1,500/family (~US$27) transfer to 852 families in the
    Nov 2023 Dolores activation. Neither maps cleanly onto the Hub figures, which may
    reflect a narrower or different reporting snapshot.
  schema_strain: >-
    No dedicated public trigger/protocol document (EAP-style PDF or OCHA-style framework
    report) was found for this framework — only Oxfam Pilipinas news/project pages, so
    `framework_doc` is left null rather than pointed at a generic org homepage. No
    confirmed real-world flood-specific activation matching the Hub's 2024 listing
    (Humanity & Inclusion / Community Organizers Multiversity / Oxfam) was found: the
    closest 2024 events found were a Feb 2024 SUPREME BARMM El Niño/drought activation
    (same partner org set) and an Aug 2024 ACCESS emergency response to already-occurring
    Mindanao floods/landslides (post-event, not evidently trigger-based) — neither
    recorded in `activations`. `data_sources` left empty: the triggers found are
    community/local-government observation-based (rising water levels, local flood
    warning signals) rather than a named forecast model/dataset.
visibility: public
---

# Oxfam — Philippines flood

## Summary
Oxfam Pilipinas runs flood-related anticipatory cash transfers in the Philippines through
at least two distinct, partner-based projects that public sources do not cleanly unify
into one framework (see `extra.coordination`): an ECHO-funded urban-preparedness project in
Cotabato City, Mindanao barangays (SUPPA, with IDEALS Inc., PDRRN and Humanity &
Inclusion, feeding into the wider Mindanao ACCESS and SUPREME BARMM consortia that also
include Community Organizers Multiversity), and a separate SHARPER/B-READY project in
Eastern Samar with local partner SIKAT Inc. that has institutionalized a municipal flood
trigger with the Dolores, Eastern Samar local government. This is not part of the
OCHA/CERF collective Philippines AA portfolio, which covers tropical cyclones rather than
floods.

## Trigger
No public trigger/protocol document was found; the two known flood triggers are:
- **Cotabato City barangays (SUPPA/ACCESS lineage):** community-reported rising water
  levels and flood-warning signals (residents alert barangay officials, in some
  accounts with photo evidence), assessed by barangay officials, who authorise
  pre-positioned cash transfers (via PayMaya/Palawan Pawnshop remittance) before
  floodwaters peak. A 2020 activation delivered cash roughly 4 days before ~6 feet of
  floodwater inundated the area.
- **Dolores, Eastern Samar (SHARPER/B-READY lineage):** a municipal "flood trigger
  index" combining weather forecasts, local knowledge and historical disaster data,
  developed with SIKAT Inc. and institutionalized by the local government, authorising
  pre-emptive cash disbursement.

Neither trigger's specific rainfall/gauge thresholds or forecast-probability levels were
found in the sources reviewed. Separately, Oxfam Pilipinas has worked with BARMM READi and
the Pre-Disaster Risks Assessment (PDRA) Group to develop AA triggers and early-action
protocols "for tropical cyclones, flooding, and El Niño" for the SUPREME BARMM/ACCESS
consortia, but no flood-specific threshold detail for that work was found either.

## Funding & scope
The Anticipation Hub inventory records ~US$7,840 pre-arranged funding targeting ~1,150
people for this framework, but these figures could not be reconciled against any single
public source (see `extra.funding_note`). Known related figures from public reporting:
the Nov 2023 Dolores activation delivered PHP 1,500 (~US$27) per family, funded by the
Dolores local government, to 852 families; the wider ACCESS consortium received an
EU/ECHO grant of ₱76 million (~€1.2 million) in August 2024 for a Mindanao flood
response covering food, water, sanitation and hygiene support — not clearly anticipatory
and not Oxfam- or flood-specific in isolation.

## Activations
- **2020 — Cotabato City area:** cash to 852 families in five flood-prone villages,
  ~4 days ahead of ~6 feet of floodwater, following a heavy-rain forecast. Exact date
  and funding total not found.
- **18 November 2023 — Dolores, Eastern Samar:** the municipal flood trigger index
  (SHARPER project, with SIKAT Inc.) triggered on a shear line/low-pressure system that
  went on to cause flash floods; the local government disbursed PHP 1,500 to 852
  families in flood-prone barangays. Matches the Hub's 2023 listing.
- No confirmed activation was found matching the Hub's 2024 listing (Humanity &
  Inclusion / Community Organizers Multiversity / Oxfam) — see `extra.schema_strain`
  for the closest (but not clearly matching) 2024 events found.

## Sources
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- [Oxfam Pilipinas — Anticipatory Action](https://oxfam.org.ph/what-we-do/anticipatory-action/) (programme overview; no dedicated protocol document found)
- [Oxfam Pilipinas — ECHO-funded project strengthens Cotabato village's pre-disaster response](https://oxfam.org.ph/echo-funded-project-strengthens-cotabato-villages-pre-disaster-response/) (SUPPA trigger detail)
- [Oxfam Pilipinas — Flood assistance helps poor Bangsamoro families avoid debt](https://oxfam.org.ph/flood-assistance-helps-poor-bangsamoro-families-avoid-debt/) (SUPPA, Tamontaka 3, EU-funded)
- [Oxfam Pilipinas — 852 families receive cash assistance in Dolores, E. Samar before floods hit](https://oxfam.org.ph/852-families-receive-cash-assistance-in-dolores-e-samar-before-floods-hit/) (Nov 2023 activation)
- [Oxfam America — Philippines country page](https://www.oxfamamerica.org/explore/countries/philippines/) (2020 Cotabato activation account)
- [Oxfam Pilipinas — 2,000 families receive assistance to combat anticipated El Niño impacts in BARMM](https://oxfam.org.ph/2000-families-receive-assistance-to-combat-anticipated-el-nino-impacts-in-barmm-2/) (SUPREME BARMM consortium, Feb 2024 — drought, not flood)
- [Philippine Information Agency — Gender-responsive anticipatory action to boost disaster response in BARMM](https://pia.gov.ph/gender-responsive-anticipatory-action-to-boost-disaster-response-in-barmm/) (BARMM READi/PDRA multi-hazard trigger context)
- [CARE Philippines — ACCESS gets ₱76 million from EU for Mindanao flood aid](https://care-philippines.org/2024/08/19/access-gets-%E2%82%B176-million-from-eu-for-mindanao-flood-aid/) / [ReliefWeb mirror](https://reliefweb.int/report/philippines/access-gets-76-million-eu-mindanao-flood-aid) (Aug 2024, post-event, not clearly anticipatory)
- [Oxfam Pilipinas — Over 190,000 Affected by BARMM Floods; Oxfam partners launch emergency response](https://oxfam.org.ph/over-190000-affected-by-barmm-floods-oxfam-partners-launch-emergency-response/) (May 2025, post-disaster response)
- Related OCHA/CERF portfolio (tropical cyclones, not floods): [`frameworks/phl-storms`](../../frameworks/phl-storms)
