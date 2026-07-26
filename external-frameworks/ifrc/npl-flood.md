---
content_type: framework-external
framework: ifrc-npl-flood
org: IFRC
country_iso3: NPL
hazard: flood
status: active
valid_until: "2026-06"
trigger_summary: >-
  Forecast trigger, checked independently for each of three river basins. It fires when a
  DHM flood forecast bulletin, DHM special flood advisory, or ICIMOD regional flood outlook
  predicts that river levels will reach the existing government danger level within the
  next 48 hours — at Chepang station (Babai river, Bardiya) and Kusum station (West Rapti
  river, Banke); a third basin, Karnali (Kailali district), is covered but its monitoring
  station was not identified in public sources.
data_sources: [DHM, ICIMOD]
prearranged_funding_usd: 226974
funding_by_source: {DREF: 226974}
target_people: 10500
framework_doc: https://www.anticipation-hub.org/download/file-4331
framework_doc_date: 2024-06-12
sources:
- https://www.anticipation-hub.org/download/file-4331
- https://www.anticipation-hub.org/experience/global-map
- https://www.anticipation-hub.org/news/the-nepal-red-cross-society-activates-its-simplified-early-action-protocol-for-floods
- https://reliefweb.int/report/nepal/nepal-western-terai-flood-simplified-early-action-protocol-seap2024np01
- https://reliefweb.int/report/nepal/simplified-early-action-protocol-activation-nepal-western-terai-flood-mdrnp017
- https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-operations-update-seap-no-seap2024np01-operation-no-mdrnp017
- https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-operations-update-seap-no-seap2024np01-operation-no-mdrnp017-30-october-2024
- https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-report-seap-activation-lesson-learning-meeting-19-december-2024
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNP017
activations:
- date: "2024-09-26"
  url: https://www.anticipation-hub.org/news/the-nepal-red-cross-society-activates-its-simplified-early-action-protocol-for-floods
  note: >-
    DHM special flood advisory issued 5pm 26 Sep 2024 (Babai and West Rapti rivers flagged
    red) forecast both rivers would surpass danger levels — 6.8 at Chepang (Babai), 7.8 at
    Kusum (West Rapti) — within 48 hours (by 28 Sep). SEAP activated for these two basins
    only; the Karnali/Kailali basin did not trigger. CHF 28,736 (~US$34,000) released from
    the DREF anticipatory pillar; NRCS volunteers (102, Bardiya 72/Banke 40) reached ~5,400
    people at risk with evacuation support, ~3,600 with early-warning messages, and staged
    evacuation-site setup, water testing, and hygiene-kit distribution in Banke and Bardiya.
    De-escalated 28 Sep 2024 after the 48-hour window closed.
last_checked: '2026-07-16'
extra:
  hub_captions:
  - '2024: Flood (IFRC) [Nepal Red Cross Society]'
  hub_years:
  - '2024'
  implementing:
  - Nepal Red Cross Society
  eap_no: sEAP2024NP01
  operation_no: MDRNP017
  partners: Danish Red Cross, Finnish Red Cross, IFRC/RCRC Climate Centre (technical support)
  funding_note: >-
    Figures for this sEAP disagree slightly by source: the Anticipation Hub inventory
    (used above) gives US$226,974 pre-arranged; the IFRC GO appeal record for MDRNP017
    ("Nepal - Floods EAP", 10 Jun 2024-30 Jun 2026) shows a budget of US$199,964, fully
    funded, for 10,500 beneficiaries. Neither figure is the amount actually released on
    activation (CHF 28,736, ~US$34,000 — see `activations`), which is a partial
    early-action tranche, not the full 2-year programme budget. Do not confuse this sEAP
    (MDRNP017) with the separate, larger post-event DREF operation "Nepal Flood and
    Landslide Response 2024" (MDRNP018, CHF 520,718) — that is an ordinary emergency
    response to the same 2024 floods, not part of this anticipatory framework.
  coordination: >-
    This is NRCS's own DREF-funded instrument, distinct from the OCHA/CERF collective
    "Nepal Anticipatory Action Framework for Floods" (`frameworks/npl-flooding`), which
    covers the Koshi and Karnali basins under a GloFAS+DHM trigger and is implemented by
    FAO/UNFPA/UNICEF/WFP (with NRCS credited there only as a delivery partner for the CERF
    response, e.g. the Oct 2024 Koshi activation). This sEAP's own Karnali-basin coverage
    (Kailali district: Tikapur, Janaki, Geruwa, Rajapur and Madhuwan municipalities) runs
    in parallel with, and geographically overlaps, the OCHA framework's separate
    Karnali/Chisapani trigger — no source found describing the two as jointly coordinated;
    treat as two distinct, non-identical Karnali-basin AA instruments run by different
    organisations, per the pattern documented for IFRC's Bangladesh flood EAP.
  schema_strain: >-
    The Karnali-basin (Kailali) monitoring station and its specific danger-level threshold
    were not found in public sources — only the Babai (Chepang, 6.8) and West Rapti (Kusum,
    7.8) stations/thresholds were confirmed, both from the Sep 2024 activation reporting.
    The full sEAP document (framework_doc) is a PDF that public web-fetch tools could not
    extract text from; trigger/funding/scope details above are drawn from Anticipation Hub
    news, ReliefWeb operations-update summaries, and the IFRC GO API, not the source PDF
    itself.
visibility: public
---

# IFRC — Nepal flood sEAP

## Summary
The Nepal Red Cross Society (NRCS) runs a Simplified Early Action Protocol (sEAP2024NP01,
IFRC operation MDRNP017) for flooding in the Terai lowlands of western Nepal, with
technical support from the Danish Red Cross, Finnish Red Cross and the IFRC/RCRC Climate
Centre. Approved 12 June 2024 and funded through IFRC's Disaster Response Emergency Fund
(DREF), the two-year programme (June 2024-June 2026) covers 12 municipalities across three
river basins — West Rapti (Banke), Babai (Bardiya) and Karnali (Kailali) — targeting roughly
10,500 people. It fired for the first time in September 2024, for the Babai and West Rapti
basins. This is NRCS's own instrument, separate from the OCHA/CERF collective Nepal flood
framework that also operates in the Koshi and Karnali basins (see `extra.coordination`).

## Trigger
A single-stage, 48-hour-lead forecast trigger, evaluated independently per basin: it fires
when a Department of Hydrology and Meteorology (DHM) flood forecast bulletin, DHM special
flood advisory, or ICIMOD regional flood outlook predicts that a monitored river will reach
its existing government danger level within the next 48 hours. Confirmed monitoring points:
**Chepang station** on the Babai river (danger level 6.8) and **Kusum station** on the West
Rapti river (danger level 7.8). The Karnali-basin (Kailali) monitoring station was not
identified in public sources (see `extra.schema_strain`).

## Funding & scope
DREF-funded; sources disagree slightly on the pre-arranged total (US$226,974 per the
Anticipation Hub inventory vs. US$199,964 per the IFRC GO appeal record for MDRNP017,
fully funded) — see `extra.funding_note`. Target: ~10,500 people across 12 municipalities
in Banke, Bardiya and Kailali districts. The September 2024 activation released a much
smaller early-action tranche, CHF 28,736 (~US$34,000), from the DREF anticipatory pillar —
this sEAP should not be confused with the separate, larger post-event DREF operation
"Nepal Flood and Landslide Response 2024" (MDRNP018, CHF 520,718) covering the same 2024
flood season.

## Activations
- **26-28 September 2024** — DHM special flood advisory (issued 5pm 26 Sep) forecast the
  Babai and West Rapti rivers would surpass their danger levels within 48 hours (by 28
  Sep); the sEAP activated for these two basins (Karnali/Kailali did not trigger). CHF
  28,736 released; NRCS volunteers (102 total) reached ~5,400 people at risk with
  evacuation support and ~3,600 with early-warning messages in Banke and Bardiya,
  including evacuation-site preparation, water testing and hygiene-kit distribution.
  De-escalated 28 September 2024. A lessons-learned meeting was held 19 December 2024 to
  feed findings into a possible future full EAP.

## Sources
- **Authoritative:** [sEAP2024NP01 document, approved 12 Jun 2024](https://www.anticipation-hub.org/download/file-4331) (PDF; text not machine-extractable via available tools — see `extra.schema_strain`) · [ReliefWeb listing](https://reliefweb.int/report/nepal/nepal-western-terai-flood-simplified-early-action-protocol-seap2024np01)
- [Anticipation Hub — NRCS activates its flood sEAP](https://www.anticipation-hub.org/news/the-nepal-red-cross-society-activates-its-simplified-early-action-protocol-for-floods) (activation account)
- [ReliefWeb — Activation report, Sep 2024](https://reliefweb.int/report/nepal/simplified-early-action-protocol-activation-nepal-western-terai-flood-mdrnp017)
- [ReliefWeb — Operations update](https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-operations-update-seap-no-seap2024np01-operation-no-mdrnp017) · [30 Oct 2024 update](https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-operations-update-seap-no-seap2024np01-operation-no-mdrnp017-30-october-2024)
- [ReliefWeb — Lesson-learning meeting report, 19 Dec 2024](https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-report-seap-activation-lesson-learning-meeting-19-december-2024)
- [IFRC GO — MDRNP017 appeal record](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRNP017) (budget/beneficiaries, machine-readable)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- Related OCHA/CERF collective framework: [`frameworks/npl-flooding`](../../frameworks/npl-flooding) · related NRCS sEAP: [`external-frameworks/ifrc/npl-multiple.md`](npl-multiple.md)
