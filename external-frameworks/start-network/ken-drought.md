---
content_type: framework-external
framework: start-network-ken-drought
org: START
country_iso3: KEN
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  Funds a set of localized, partner-run Early Action Protocols rather than one shared
  national trigger. Per the founding project document, the drought model draws on
  "various climatological and humanitarian forecast data" and is calibrated to drought
  events with an average 10-year return period; the specific indicator, numeric
  threshold and lead time are left to each local EAP custodian and were still described
  as "to be defined" as of the project's 2020-2022 development phase. No single public
  trigger document (indicator + threshold + lead time) was located for the mechanism
  as a whole — see `extra.schema_strain`.
data_sources: []
prearranged_funding_usd: 700000
funding_by_source: {"Start Network": 700000}
target_people: 100000
framework_doc: https://www.anticipation-hub.org/global-overview/countries/kenya/development-of-forecast-based-action-mechanism-addressing-drought-induced-food-insecurity-in-kenya
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/global-overview/countries/kenya/development-of-forecast-based-action-mechanism-addressing-drought-induced-food-insecurity-in-kenya
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya
- https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya/welthungerhilfe-anticipatory-humanitarian-action-facility-wahafa-in-kenya
- https://reliefweb.int/report/kenya/acted-kenya-providing-emergency-cash-assistance-support-drought-affected-families-turkana-county
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: 2022-07
  url: https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya/welthungerhilfe-anticipatory-humanitarian-action-facility-wahafa-in-kenya
  note: >-
    Welthungerhilfe and local partner PACIDA disbursed anticipatory cash (via M-Pesa,
    two equal cycles, July-September 2022) plus early-warning messaging to 1,060
    drought-affected households in Maikona and Kargi wards, Marsabit County. Start
    Network provided US$193,524 in "fuel funding" for the disbursement.
- date: 2022
  url: https://reliefweb.int/report/kenya/acted-kenya-providing-emergency-cash-assistance-support-drought-affected-families-turkana-county
  note: >-
    ACTED, with local partners TUPADO and SAPCONE and Start Network funding, ran an
    "Early Action Emergency Drought Cash Response" in Northern Turkana: 1,155
    households selected via community-based vulnerability targeting (priority to
    IPC4 households, those who had lost livestock, women/child-headed households,
    the disabled, pregnant/lactating women, and the elderly/ill). Exact activation
    date and disbursement amount not confirmed — the ReliefWeb page returned HTTP 403
    to direct fetch; details are drawn from search-indexed text only.
last_checked: '2026-07-24'
extra:
  hub_captions:
  - '2022: Drought (Start Network) [Welthungerhilfe] [PACIDA] [Oxfam] [Merti Integrated
    Development Programme] [acted] [SAPCONE] [TUPADO]'
  hub_years:
  - '2022'
  implementing:
  - Welthungerhilfe
  - PACIDA
  - Oxfam
  - Merti Integrated Development Programme
  - acted
  - SAPCONE
  - TUPADO
  project_period: >-
    March 2020 - December 2022, per the framework_doc — the period for developing the
    forecast-based-action mechanism and its local EAPs (implementation/activation, e.g.
    the July-Sept 2022 Marsabit and 2022 Turkana responses, occurred within/at the end
    of this window). The Anticipation Hub's Kenya country page still lists the
    mechanism as an "active framework" as of this check, so `status: active` is kept;
    no later renewal or closure document was found.
  activation_2022_aggregate: >-
    The Anticipation Hub's Kenya country overview page records one combined "2022:
    Drought" activation line for this Start Network framework — 7,560 people reached,
    US$656,788 disbursed. This is consistent in order of magnitude with the two
    activations listed above (1,060 + 1,155 = 2,215 households, i.e. ~3.4 people/hh) but
    the page does not itself break the total down by county/partner, so the match is
    inferred, not source-confirmed.
  funding_note: >-
    The US$700,000 / 100,000-people figures are the Anticipation Hub Kenya country
    page's headline numbers for this framework (not broken down by partner/county).
    Start Network is the financing mechanism/EAP fund-holder; the underlying donor
    named on the framework_doc page is the German Federal Foreign Office (GFFO).
  wahafa_relationship: >-
    Welthungerhilfe's Anticipatory Humanitarian Action Facility (WAHAFA) is a distinct,
    later Welthungerhilfe/PACIDA program (build phase Aug 2023-Aug 2024, fuel funding
    guaranteed through Apr 2026) covering Marsabit, Samburu and Turkana counties for
    both drought and flood — it is not itself a Start Network framework, but its own
    page cites the 2022 Start Network/Marsabit activation as prior context. No separate
    external-frameworks page exists for WAHAFA as of this check.
  schema_strain: >-
    No single public document states one indicator/threshold/lead-time trigger for
    this mechanism — it appears to fund multiple locally-designed EAPs under a shared
    "~10-year return period" design principle, each left to its EAP custodian; hence
    `data_sources: []` and a prose-only `trigger_summary`. No publish date was found on
    the framework_doc page itself (only the Mar 2020-Dec 2022 project period). Oxfam's
    and Merti Integrated Development Programme's specific roles/counties/activations
    under this framework (both named in the Hub's 2022 inventory caption) could not be
    independently confirmed from public sources — searches for Oxfam+MIDP+Start
    Network+Kenya+drought surfaced only an unrelated, later (Dec 2023-Mar 2024) Oxfam
    loss-and-damage project with MIDP, which is NOT cited here as part of this
    framework. The ACTED/Turkana activation's exact date and disbursement amount are
    likewise unconfirmed (source page blocked direct fetch, HTTP 403).
  coordination: >-
    Not a component of an OCHA/CERF collective framework. Two other, separate drought
    AA efforts run in parallel in Kenya: the IFRC/Kenya Red Cross Society EAP2022KE02
    (23 ASAL counties, first activated Sep 2025 in Kwale/Kilifi/Kitui — see
    external-frameworks/ifrc/ken-drought.md) and WFP's Anticipatory Action Plan for
    Wajir/Marsabit (activated Sep-Nov 2025 — see external-frameworks/wfp/ken-drought.md).
    No county overlap identified between this Start Network mechanism's known 2022
    activations (Marsabit's Maikona/Kargi wards, Northern Turkana) and those later
    IFRC/WFP activations.
visibility: public
---

# START — Kenya drought

## Summary
Start Network's multi-country Forecast-based Action (FbA) programme funds a Kenya
mechanism for drought-induced food insecurity, developed March 2020-December 2022
with Welthungerhilfe as lead EAP custodian and the German Federal Foreign Office (GFFO)
as underlying donor. Rather than one national EAP, it finances several localized,
partner-run Early Action Protocols — in 2022 these paid out anticipatory cash to
drought-affected households in Marsabit County (Welthungerhilfe/PACIDA) and Turkana
County (ACTED/TUPADO/SAPCONE). The Anticipation Hub lists the framework as active, with
a US$700,000 envelope against 100,000 targeted people.

## Trigger
The framework document describes a drought model built on "various climatological and
humanitarian forecast data," informed by risk and vulnerability analysis, and designed
around drought events with an average 10-year return period. It does not fix a single
indicator, numeric threshold or lead time — those are left to each local EAP custodian,
and were still "to be defined" as of the 2020-2022 development phase. No later public
document was found that nails down the trigger design for any of the local EAPs
individually.

## Funding & scope
- Headline envelope: US$700,000 pre-arranged funding against 100,000 targeted people
  (Anticipation Hub Kenya country page) — not broken down by partner or county.
- Start Network is the fund-holder/financing mechanism; GFFO is the donor named on the
  framework document.
- 2022 activations disbursed at least US$193,524 (Marsabit, confirmed) within a
  Hub-recorded combined 2022 total of US$656,788 reaching 7,560 people (see
  `extra.activation_2022_aggregate`).

## Activations
- **July-September 2022 (Marsabit County)** — Welthungerhilfe and PACIDA disbursed
  anticipatory cash (M-Pesa, two equal cycles) and early-warning messages to 1,060
  households in Maikona and Kargi wards; Start Network provided US$193,524 in
  "fuel funding."
- **2022 (Northern Turkana)** — ACTED, with TUPADO and SAPCONE, ran an "Early Action
  Emergency Drought Cash Response" targeting 1,155 vulnerable households (IPC4,
  livestock loss, women/child-headed, disabled, pregnant/lactating, elderly), funded
  by Start Network. Exact date and amount not confirmed in sources reviewed.
- No activations are confirmed for Oxfam or Merti Integrated Development Programme,
  though both are named as implementing partners in the Hub's 2022 inventory listing.

## Sources
- **Authoritative:** [Development of Forecast-based Action mechanism addressing drought induced food insecurity in Kenya — Anticipation Hub](https://www.anticipation-hub.org/global-overview/countries/kenya/development-of-forecast-based-action-mechanism-addressing-drought-induced-food-insecurity-in-kenya) (project period Mar 2020-Dec 2022; no separate publish date shown)
- [Anticipatory action in Kenya — Anticipation Hub country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya) (US$700,000/100,000-people framework figures; combined 2022 activation record: 7,560 people, US$656,788)
- [Welthungerhilfe Anticipatory Humanitarian Action Facility (WAHAFA) in Kenya — Anticipation Hub](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/kenya/welthungerhilfe-anticipatory-humanitarian-action-facility-wahafa-in-kenya) (Marsabit 2022 activation detail: 1,060 households, US$193,524, Jul-Sep 2022 M-Pesa cycles)
- [ACTED Kenya: providing emergency cash assistance to support the drought-affected families in Turkana County — ReliefWeb](https://reliefweb.int/report/kenya/acted-kenya-providing-emergency-cash-assistance-support-drought-affected-families-turkana-county) (Turkana 2022 activation; direct fetch returned HTTP 403, used via search-indexed text)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record, org/partner listing)
