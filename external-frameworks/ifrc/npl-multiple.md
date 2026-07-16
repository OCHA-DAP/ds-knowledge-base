---
content_type: framework-external
framework: ifrc-npl-multiple
org: IFRC
country_iso3: NPL
hazard: multiple
status: active
valid_until: null
trigger_summary: null
data_sources: []
prearranged_funding_usd: 292208
funding_by_source: {}
target_people: 20000
framework_doc: null
framework_doc_date: null
sources:
  - https://www.anticipation-hub.org/experience/global-map
  - https://www.ifrc.org/sites/default/files/2022-09/Simplified-EAP-brochure-22.pdf
  - https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-operations-update-seap-no-seap2024np01-operation-no-mdrnp017
  - https://reliefweb.int/report/nepal/nepal-urban-heatwave-simplified-early-action-protocol-seap-no-seap2025np02-operation-no-mdrnp020-december-2025
  - https://www.anticipation-hub.org/news/the-nepal-red-cross-society-activates-its-simplified-early-action-protocol-for-floods
activations: []
last_checked: '2026-07-15'
extra:
  hub_captions:
    - '2024: Multiple (IFRC) [Nepal Red Cross Society]'
  hub_years:
    - '2024'
  implementing:
    - Nepal Red Cross Society
  schema_strain: >-
    The Hub's own record for this entry (hazard=Multiple, org=IFRC, NPL, 2024) carries
    framework_link: null, and no independent public document describing a single
    stand-alone "multi-hazard" NRCS/IFRC framework could be located. IFRC's Simplified
    Early Action Protocol (sEAP) mechanism explicitly limits each protocol to ONE hazard
    (max 3 sEAPs per National Society) — NRCS runs at least two: a flood sEAP
    (sEAP2024NP01 / MDRNP017; see external-frameworks/ifrc/npl-flood.md) and an urban
    heatwave sEAP (sEAP2025NP02 / MDRNP020, approved Dec 2025). This "Multiple" record
    most likely represents an aggregate/rollup of NRCS's sEAP portfolio in the Hub's
    underlying overview-report data rather than a single framework document — this could
    not be confirmed from public sources. trigger_summary, framework_doc and activations
    left null/[] rather than guessed.
  related_seaps:
    flood: 'sEAP2024NP01 / MDRNP017 — documented separately, see external-frameworks/ifrc/npl-flood.md'
    heatwave: 'sEAP2025NP02 / MDRNP020 — approved Dec 2025; per IFRC GO, target 8,000 people, budget USD 219,733'
visibility: public
---

# IFRC — Nepal multiple

## Summary
The Anticipation Hub's global map lists a 2024 "Multiple"-hazard anticipatory action entry
for IFRC / Nepal Red Cross Society (NRCS) — 20,000 people targeted, ~US$292,208
pre-arranged — but no single public framework document matches this identity under that
label. NRCS's publicly documented anticipatory action instead consists of separate
single-hazard Simplified Early Action Protocols (sEAPs), each following IFRC's rule that
one sEAP covers exactly one hazard (a National Society may hold up to three): a flood
sEAP activated in September 2024, and an urban heatwave sEAP approved in December 2025.
This page records the Hub's "Multiple" entry as-is; see `npl-flood.md` for the documented
flood sEAP.

## Trigger
Not sourced — no public document was found for a distinct multi-hazard NRCS framework
matching this Hub record. The known constituent sEAPs each publish their own
single-hazard trigger; the flood sEAP's is a Department of Hydrology and Meteorology
heavy-rain alert for the Babai/West Rapti river basins with a 48-hour early-action
timeframe (documented on `npl-flood.md`).

## Funding & scope
Per the Hub inventory: ~US$292,208 pre-arranged, 20,000 people targeted, implementing
agency Nepal Red Cross Society. No funding-source breakdown (DREF vs. other) is given in
the Hub record, and none was found elsewhere for this specific identity.

## Activations
None known under this "Multiple" identity. (NRCS's flood sEAP was activated 26–28
September 2024 for the 2024 monsoon — tracked on `npl-flood.md`, not here, since the Hub
carries the flood and "Multiple" records as separate rows.)

## Sources
- **Hub inventory record** (authoritative for the figures on this page): [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (fetched 2026-07-10; `framework_link` null)
- [IFRC Simplified EAP brochure](https://www.ifrc.org/sites/default/files/2022-09/Simplified-EAP-brochure-22.pdf) — explains the sEAP mechanism (max 3 per National Society, one hazard each)
- [Nepal flood sEAP2024NP01 operations update (MDRNP017)](https://reliefweb.int/report/nepal/nepal-flood-simplified-early-action-protocol-operations-update-seap-no-seap2024np01-operation-no-mdrnp017)
- [Nepal urban heatwave sEAP2025NP02 (MDRNP020), December 2025](https://reliefweb.int/report/nepal/nepal-urban-heatwave-simplified-early-action-protocol-seap-no-seap2025np02-operation-no-mdrnp020-december-2025)
- [Anticipation Hub: NRCS activates its flood sEAP](https://www.anticipation-hub.org/news/the-nepal-red-cross-society-activates-its-simplified-early-action-protocol-for-floods)
