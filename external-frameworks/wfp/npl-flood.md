---
content_type: framework-external
framework: wfp-npl-flood
org: WFP
country_iso3: NPL
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Two layers, both public-sourced but incompletely reconciled: (1) WFP is one of four UN
  implementing agencies in the OCHA/CERF collective Nepal flood framework's GloFAS+DHM
  compound trigger (readiness: GloFAS forecast probability of exceeding a return-period
  discharge threshold at 7-day lead; action: DHM danger-level gauge/bulletin, 3 hours-3
  days lead) — see `frameworks/npl-flooding` for the authoritative trigger design. (2)
  WFP separately runs its own anticipatory cash-transfer initiative in the Karnali, Babai
  and West Rapti basins (western Nepal), also forecast-based on GloFAS plus the
  government flood-warning system, 3 hours-3 days lead time, funded in part by Germany's
  Federal Foreign Office (GFFO) rather than CERF.
data_sources: [GloFAS, DHM]
prearranged_funding_usd: 1400000
funding_by_source: {}
target_people: 46130
framework_doc: /download/file-5060
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/experience/global-map
- https://www.anticipation-hub.org/download/file-5060
- https://www.anticipation-hub.org/Documents/Framework_documents/OCHA-Nepal-Flood-AA-Framework.pdf
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nepal
- https://www.wfp.org/news/wfps-early-climate-action-supports-risk-communities-monsoon-floods-hit-western-nepal
- https://www.wfp.org/publications/joint-post-distribution-monitoring-pdm-forecast-based-anticipatory-action-project-fbaa
- https://wfp-evaluation.medium.com/acting-early-the-causal-impacts-of-wfps-anticipatory-action-programmes-in-nepal-and-bangladesh-fea93833208b
- https://www.wfp.org/publications/nepal-anticipatory-action-impact-evaluation
- https://centre.humdata.org/triggering-anticipatory-action-for-floods-in-nepal/
activations:
- date: 2022-10
  url: https://www.wfp.org/news/wfps-early-climate-action-supports-risk-communities-monsoon-floods-hit-western-nepal
  note: >-
    Karnali basin monsoon floods — WFP, funded by Germany's Federal Foreign Office,
    provided cash entitlements of NPR 15,000 (~US$120) to 3,000+ vulnerable households
    (~15,000+ people) plus early-warning messages, prioritising households headed by
    persons with disabilities, older people, and women. Ran alongside the broader
    OCHA/CERF-coordinated Karnali (Chisapani) activation the same month ($3.2M CERF,
    ~71,000-90,000 people reached across FAO/UNFPA/UNICEF/WFP/UN Women — recorded on the
    OCHA side, see `frameworks/npl-flooding`); the two funding streams were not clearly
    disentangled in the sources reviewed.
- date: 2024-10
  url: https://reliefweb.int/report/nepal/activation-anticipatory-action-framework-koshi-river-basin-communities-amidst-heavy-floods
  note: >-
    Koshi basin monsoon floods — WFP's share ($3.623M of the $6.5M CERF envelope, per
    the OCHA framework's funding-by-agency table) of the OCHA/CERF collective
    activation; WFP distributed multi-purpose cash (NPR 15,000/household) to Sunsari and
    Saptari districts. This was the OCHA/CERF collective framework's activation, not an
    independent WFP action — recorded primarily on the OCHA side (`frameworks/npl-flooding`).
last_checked: '2026-07-20'
extra:
  hub_captions:
  - '2022: Flood (WFP) [WFP]'
  - '2023: Flood (WFP) [WFP]'
  - '2024: Flood (WFP) [WFP]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - WFP
  coordination: >-
    Nepal has two distinct but overlapping WFP-flood-relevant instruments, not clearly
    separable in public sources: (1) the OCHA/CERF collective "Nepal Anticipatory Action
    Framework for Floods" (`frameworks/npl-flooding`), where WFP is one of four
    implementing UN agencies (with FAO/UNFPA/UNICEF) under a CERF-funded GloFAS+DHM
    trigger — this covered both Koshi and Karnali basins through the 2024 version,
    narrowing to Koshi-only from the 2025 revision; and (2) a WFP-run initiative for the
    Karnali/Babai/West Rapti basins in western Nepal, co-funded by Germany's Federal
    Foreign Office rather than CERF. The 2025-08-25 OCHA framework document itself notes
    that, as the collective framework narrowed to Koshi-only, "WFP and NRCS are noted as
    running independent AA initiatives in western Nepal" — supporting that WFP's western
    program is a genuinely separate, ongoing instrument rather than just relabelled OCHA
    funding, but public sources do not cleanly separate the two funding streams or say
    whether the GFFO-funded program has its own standalone framework document distinct
    from `framework_doc` (which is itself the joint OCHA-WFP PDF, per Anticipation Hub
    metadata "organizations: OCHA and WFP"). Also distinct: the Nepal Red Cross Society
    runs its own DREF-funded sEAP in the Karnali (Kailali) and other basins
    (`external-frameworks/ifrc/npl-flood.md`) — a third, separate instrument again.
  funding_note: >-
    The Hub inventory figures used above ($1.4M pre-arranged, 46,130 people targeted)
    could not be independently reconciled against other public sources: the
    Anticipation Hub's Nepal country page separately lists an "active" WFP flood
    framework at $2,790,592 / 198,860 people (close to, but not matching, the 2025 OCHA
    Koshi-only CERF envelope of $2.7M) and a 2022 WFP activation at $2,713,972 / 86,677
    people — neither of which matches the Hub inventory record's per-year figures either.
    No breakdown of CERF vs GFFO shares was found. Treat all these figures as
    imprecisely-reconciled estimates from different Hub snapshots/views, not a single
    audited total.
  schema_strain: >-
    `framework_doc_date` unknown — file-5060 ("OCHA-Nepal-Flood-AA-Framework.pdf") is a
    generic joint OCHA-WFP filename that may be reused across framework revisions
    (2021/2024/2025 versions all exist as separate PDFs on ReliefWeb); which revision
    this specific Hub-linked file represents was not confirmed, and the PDF's text could
    not be machine-extracted via available tools. No confirmed 2023 activation was found
    in public sources, despite '2023' appearing in the Hub's year listing for this
    record — the 2023 period corresponds to an "addendum to the 2022 framework" (per
    `frameworks/npl-flooding`) with no page or activation record of its own yet.
visibility: public
---

# WFP — Nepal floods

## Summary
WFP's flood-related anticipatory action in Nepal spans two overlapping instruments that
public sources do not cleanly separate (see `extra.coordination`). First, WFP is one of
four UN implementing agencies — alongside FAO, UNFPA and UNICEF — in the OCHA/CERF
collective "Nepal Anticipatory Action Framework for Floods" (`frameworks/npl-flooding`),
which used a GloFAS-forecast-plus-DHM-danger-level compound trigger across the Koshi
(east) and, through 2024, Karnali (west) basins, funded by CERF. Second, WFP separately
runs (or ran) its own anticipatory cash-transfer initiative for the Karnali, Babai and
West Rapti basins in western Nepal, co-funded by Germany's Federal Foreign Office (GFFO)
— the 2025 OCHA framework document itself describes this as an "independent AA
initiative" run by WFP (and separately by the Nepal Red Cross Society) once the
collective framework narrowed to Koshi-only. Both instruments have delivered NPR 15,000
(~US$120) household cash transfers ahead of monsoon flood peaks.

## Trigger
Forecast-based in both layers, but with different specifics documented:
- **Collective framework (WFP as implementing partner):** GloFAS 7-day ensemble
  discharge forecast for readiness (≥70% probability of a return-period threshold,
  basin-specific station); DHM real-time danger-level gauge or short-range GloFAS/DHM
  bulletin for action (3 hours-3 days lead). Full detail on `frameworks/npl-flooding`.
- **WFP's own western-basin initiative:** described in WFP's own communications as
  using "the government system's flood warning system and the GloFAS forecast,"
  providing 3 hours to 3 days' lead time, with separate trigger systems for the Karnali,
  Babai and West Rapti basins. Specific thresholds for this instrument were not found in
  the public sources reviewed.

## Funding & scope
Pre-arranged funding of ~US$1.4M targeting ~46,130 people per the Anticipation Hub
inventory — figures that could not be reconciled against other public Hub/WFP sources,
which show different totals for what may be different snapshots or scopes (see
`extra.funding_note`). The one activation with disclosed per-household detail (Oct 2022,
Karnali) delivered NPR 15,000 (~US$120) to 3,000+ households (~15,000+ people), funded by
Germany's Federal Foreign Office. WFP's share of the OCHA/CERF collective framework's
CERF envelope was $3,623,000 of $6,500,000 in the 2024 (two-basin) version and $392,810
of $2,700,000 in the 2025 (Koshi-only) version.

## Activations
- **October 2022 — Karnali basin:** WFP (GFFO-funded) cash entitlements of NPR 15,000 to
  3,000+ households, plus early-warning messaging, prioritising vulnerable households.
  Coincided with the broader OCHA/CERF Karnali activation ($3.2M CERF) the same month;
  the two funding streams are not clearly disentangled in public reporting.
- **October 2024 — Koshi basin:** WFP's share of the OCHA/CERF collective activation
  ($3.4M CERF released overall); WFP distributed NPR 15,000/household multi-purpose cash
  in Sunsari and Saptari districts. This was the collective framework's activation, not
  an independent WFP action — see `frameworks/npl-flooding` for the authoritative record.
- No confirmed 2023 activation found, despite '2023' appearing in the Hub's year listing
  for this record (see `extra.schema_strain`).

## Sources
- **Authoritative (contested):** [Framework document, file-5060](https://www.anticipation-hub.org/download/file-5060) — joint OCHA-WFP PDF ("OCHA-Nepal-Flood-AA-Framework.pdf"); exact revision/date not confirmed, text not machine-extractable via available tools.
- [Anticipation Hub — global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
- [Anticipation Hub — Nepal country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/nepal)
- [WFP — early climate action ahead of monsoon floods, western Nepal](https://www.wfp.org/news/wfps-early-climate-action-supports-risk-communities-monsoon-floods-hit-western-nepal) (Oct 2022 activation account)
- [WFP — Joint Post-Distribution Monitoring of the Forecast-based Anticipatory Action Project (FbAA) 2022](https://www.wfp.org/publications/joint-post-distribution-monitoring-pdm-forecast-based-anticipatory-action-project-fbaa)
- [WFP evaluation — causal impacts of AA in Nepal and Bangladesh](https://wfp-evaluation.medium.com/acting-early-the-causal-impacts-of-wfps-anticipatory-action-programmes-in-nepal-and-bangladesh-fea93833208b) (Aug 2025)
- [WFP — Nepal Anticipatory Action: Impact evaluation](https://www.wfp.org/publications/nepal-anticipatory-action-impact-evaluation)
- [Centre for Humanitarian Data — Triggering anticipatory action for floods in Nepal](https://centre.humdata.org/triggering-anticipatory-action-for-floods-in-nepal/)
- Related OCHA/CERF collective framework: [`frameworks/npl-flooding`](../../frameworks/npl-flooding) · related NRCS instrument: [`external-frameworks/ifrc/npl-flood.md`](../ifrc/npl-flood.md)
