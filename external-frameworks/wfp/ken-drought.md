---
content_type: framework-external
framework: wfp-ken-drought
org: WFP
country_iso3: KEN
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  WFP's Anticipatory Action Plan (AAP) for drought covers Wajir and Marsabit counties;
  approved in 2024 for use from the October-December rainy season onward. It triggers
  pre-agreed anticipatory cash transfers once forecast thresholds are met, but the
  specific indicator, threshold value, and lead time are not stated in the public
  sources reviewed — see `extra.schema_strain`.
data_sources: []
prearranged_funding_usd: 2267757
funding_by_source: {}
target_people: 259044
framework_doc: null
framework_doc_date: null
sources:
  - https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya
  - https://reliefweb.int/report/kenya/wfp-kenya-country-brief-august-2024
  - https://actalliance.org/wp-content/uploads/2025/12/Kenya-Drought-.pdf
  - https://www.wfp.org/publications/2025-anticipatory-action-activations
  - https://docs.wfp.org/api/documents/WFP-0000169417/download/
  - https://www.anticipation-hub.org/news/acting-to-anticipate-the-impacts-of-drought-in-kenya
activations:
  - date: 2025-09
    url: https://actalliance.org/wp-content/uploads/2025/12/Kenya-Drought-.pdf
    note: >-
      WFP, with the Government of Kenya, activated AA in Marsabit and Wajir: 10,750
      poor households received unconditional cash transfers of USD 70/household/month
      from September to November 2025, plus nutrition top-ups for pregnant/breastfeeding
      women and children under two. WFP also published a standalone activation
      document (docs.wfp.org WFP-0000169417) whose full text could not be extracted
      for this page.
last_checked: '2026-07-20'
extra:
  hub_captions:
  - '2024: Drought (WFP) [WFP]'
  hub_years:
  - '2024'
  implementing:
  - WFP
  schema_strain: >-
    No public WFP document giving the AAP's actual trigger indicator, threshold, or
    lead time was found (searched WFP publications, docs.wfp.org, ReliefWeb, and the
    Anticipation Hub Kenya pages) — WFP's own site and Hub pages state funding/target
    figures but not trigger design. The August 2024 WFP Kenya Country Brief (ReliefWeb)
    confirms AAP approval and intended use in the Oct-Dec 2024 season but returned
    HTTP 403 to direct fetch; the claim here rests on search-indexed snippets of that
    report, not a directly read full text. It is unconfirmed whether the plan actually
    triggered in Oct-Dec 2024 — only the September 2025 activation is independently
    verified (via the ACT Alliance alert note, which cites WFP as its source).
  coordination: >-
    Not a component of an OCHA/CERF collective framework. OCHA's own Kenya drought
    framework (frameworks/ken-drought) is a separate, still in-development IOD-adjusted
    trigger; the endorsed operational baseline it would enhance is the IFRC/KRCS
    EAP2022KE02, not WFP's. This WFP AAP (Wajir/Marsabit) runs independently of both.
visibility: public
---

# WFP — Kenya drought

## Summary
WFP runs an Anticipatory Action Plan (AAP) for drought in Wajir and Marsabit counties,
approved in 2024, with a stated envelope of ~USD 2.27M against ~259,000 targeted people
(Anticipation Hub). It is one of several parallel drought AA efforts in Kenya — alongside
the IFRC/Kenya Red Cross Society EAP2022KE02 (23 ASAL counties, endorsed and separately
tracked as an OCHA framework) and Welthungerhilfe's WAHAFA community-led plans (Marsabit,
Samburu, Turkana) — and is not itself an OCHA/CERF-coordinated framework.

## Trigger
Public sources confirm the AAP was designed to release pre-agreed anticipatory cash once
forecast thresholds for the October-December rains are met, but none state the specific
indicator, numeric threshold, or lead time used. The clearest evidence of the trigger
firing in practice is the September 2025 activation (below); no technical trigger
document for the plan was locatable.

## Funding & scope
- Pre-arranged budget: USD 2,267,757; ~259,044 people targeted (Anticipation Hub Kenya
  page, coordinating org WFP) — no further breakdown by funding source found.
- Counties: Wajir and Marsabit (per the WFP Kenya Country Brief, August 2024, and the
  September 2025 activation).

## Activations
- **Sep-Nov 2025** — WFP, with the Government of Kenya, activated AA in Marsabit and
  Wajir: 10,750 poor households received unconditional cash transfers of USD 70 per
  household per month, plus nutrition top-ups for pregnant/breastfeeding women and
  children under two (ACT Alliance alert note, citing WFP; corroborated by WFP's own
  "Anticipatory Action Activation — Kenya — September 2025" publication).
- Whether the plan triggered in its first live window (Oct-Dec 2024) is not confirmed
  in the public sources reviewed.

## Sources
- **Most detailed on the 2025 activation:** [ACT Alliance Kenya Drought 2025 alert note](https://actalliance.org/wp-content/uploads/2025/12/Kenya-Drought-.pdf) (completed 2025-12-08; cites WFP for the Marsabit/Wajir cash-transfer figures)
- [Anticipation Hub — Anticipatory action in Kenya](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya) (WFP budget/target-people figures; coordinating org)
- [WFP Kenya Country Brief, August 2024](https://reliefweb.int/report/kenya/wfp-kenya-country-brief-august-2024) (AAP approval for Wajir/Marsabit — accessed via search snippet, direct fetch returned HTTP 403)
- [WFP — 2025 Anticipatory Action Activations](https://www.wfp.org/publications/2025-anticipatory-action-activations) (links the Kenya activation document)
- [WFP activation document — Anticipatory Action Activation, Kenya, September 2025](https://docs.wfp.org/api/documents/WFP-0000169417/download/) (title/existence confirmed; full text not extractable)
- [Anticipation Hub — Acting to anticipate the impacts of drought in Kenya](https://www.anticipation-hub.org/news/acting-to-anticipate-the-impacts-of-drought-in-kenya) (Sep 2025 context, WFP "preparing to act" in Marsabit/Wajir)
