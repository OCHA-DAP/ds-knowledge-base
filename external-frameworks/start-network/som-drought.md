---
content_type: framework-external
framework: start-network-som-drought
org: START
country_iso3: SOM
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  Parametric: Start Network holds an ARC Replica drought insurance policy that mirrors the
  Federal Government of Somalia's own African Risk Capacity (ARC) sovereign policy. Payout
  is automatic when ARC's Africa RiskView model — a WRSI-based index combining satellite
  rainfall/crop-water-deficit data with population-vulnerability weighting — crosses its
  pre-agreed threshold for a given Gu (Mar-Jun) or Deyr (Oct-Dec) season, releasing funds
  within weeks of a confirmed failed season to pre-identified NGO-delivered cash transfers.
  No source reviewed states the specific numeric WRSI/index threshold set for Somalia's
  policy.
data_sources: [WRSI]
prearranged_funding_usd: 2027586
funding_by_source: {}
target_people: 22207
framework_doc: https://arcltd.org/the-arc-group-makes-climate-insurance-payouts-to-the-federal-republic-of-somalia-and-the-start-network-to-assist-people-affected-by-drought/
framework_doc_date: 2025-03-21
sources:
  - https://arcltd.org/the-arc-group-makes-climate-insurance-payouts-to-the-federal-republic-of-somalia-and-the-start-network-to-assist-people-affected-by-drought/
  - https://arc.int/news/new-funding-streams-activated-after-fifth-successive-failed-rainy-season-somalia
  - https://www.reinsurancene.ws/start-network-receives-727k-arc-replica-insurance-payout-for-drought-relief-in-somalia/
  - https://www.reinsurancene.ws/somalia-secures-5-5m-drought-parametric-payout-from-arc/
  - https://www.theinsurer.com/parametric-insurer/news/somalia-drought-triggers-55-million-african-risk-capacity-payouts-2026-05-26/
  - https://startnetwork.org/learn-change/resources/library/start-ready-and-arc-replica-response-drought-somalia
  - https://startnetwork.org/funds/disaster-risk-financing/arc-replica
  - https://www.artemis.bm/news/arc-sells-first-replica-parametric-policies-to-wfp-start-network/
  - https://arc.int/news/africa-riskview-methodology
  - https://www.anticipation-hub.org/global-overview/countries/somalia
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2023-03
    url: https://arc.int/news/new-funding-streams-activated-after-fifth-successive-failed-rainy-season-somalia
    note: >-
      ARC's index registered a fifth consecutive failed rainy season; Start Network's ARC
      Replica policy paid out US$3.38M, topped up with US$891,800 (£700,000) from Start
      Ready, for a combined ~US$4.2M. Delivered by a consortium of Gargaar Relief and
      Development Organization (GREDO), Wajir South Development Association (WASDA), Save
      Somali Women and Children (SSWC), Save the Children, Oxfam and World Vision as
      three monthly cash transfers of US$120/household (April-July 2023), reaching 51,318
      people.
  - date: 2025-03-21
    url: https://arcltd.org/the-arc-group-makes-climate-insurance-payouts-to-the-federal-republic-of-somalia-and-the-start-network-to-assist-people-affected-by-drought/
    note: >-
      2024/25-season ARC payout of US$2,183,565 total: US$1,455,710 to the Federal
      Republic of Somalia (targeting 35,000 households) and US$727,855 to Start Network's
      ARC Replica policy, funding cash transfers to 10,500 households.
  - date: 2026-05-28
    url: https://www.reinsurancene.ws/somalia-secures-5-5m-drought-parametric-payout-from-arc/
    note: >-
      Parametric indices confirmed for the failed 2025 Deyr and weak 2026 Gu seasons;
      combined ARC payout of US$5.5M split SODMA (Somali Disaster Management Agency)
      62.7%, Start Network 21.5% (~US$1.18M), WFP 15.8% — the three partners reported
      reaching a combined 153,000+ people.
last_checked: '2026-07-31'
extra:
  hub_captions:
  - '2024: Drought (Start Network) [acted] [ActionAid] [Action Aid Somaliland] [Muslim Aid]
    [Oxfam] [Save the Children]'
  hub_years:
  - '2024'
  implementing:
  - acted
  - ActionAid
  - Action Aid Somaliland
  - Muslim Aid
  - Oxfam
  - Save the Children
  mechanism: >-
    Start Network's Somalia drought instrument is the ARC Replica parametric insurance
    policy (bought alongside/mirroring the Federal Government of Somalia's own ARC
    sovereign policy), topped up in at least one season by the pre-arranged Start Ready
    facility. This is distinct in kind from the single-EAP-document model used by IFRC/WFP
    pages in this KB: there is no public EAP-style trigger document, only ARC/Start
    Network payout press releases per season.
  coordination: >-
    Not a component of a collective OCHA/CERF framework. A separate, unrelated OCHA/CERF
    Somalia drought/famine AA pilot exists in this KB (frameworks/som-drought/2019.md,
    status retired, last activated Feb 2021) — it used IPC food-security projections as a
    proxy trigger and CERF finance to seven UN agencies (WFP among them), with no
    documented link to Start Network's ARC Replica/Start Ready instrument (different
    trigger mechanism, funding source, and operating partners).
  schema_strain: >-
    The Anticipation Hub inventory lists prearranged_funding_usd US$2,027,586 and
    target_people 22,207 for this framework, but no single public document found
    reconciles those exact figures to a specific policy premium, sum-insured, or season —
    documented per-season payouts (US$3.38-4.2M in 2023, ~US$0.73M in 2025, ~US$1.18M in
    2026) and reach (51,318 people in 2023; 10,500 households in 2025) are recorded
    instead under `activations`. Separately, the Hub's 2024 implementing-organisation
    list (acted, ActionAid, Action Aid Somaliland, Muslim Aid, Oxfam, Save the Children)
    does not match the consortium named in the ARC Replica/Start Ready press coverage
    reviewed for 2023 (GREDO, WASDA, SSWC, Save the Children, Oxfam, World Vision) or the
    unnamed "Start Network" attribution in the 2025/2026 ARC payout releases — no source
    was found describing a discrete 2024 activation implemented by exactly the Hub's
    six-organisation list; kept as-is (not reconciled/guessed) per `extra.implementing`.
    No numeric WRSI/rainfall-index threshold specific to Somalia's ARC Replica policy was
    found in any public source reviewed.
visibility: public
---

# START — Somalia drought

## Summary
Start Network's drought anticipatory action in Somalia runs through an **ARC Replica**
parametric insurance policy — a "replica" of the Federal Government of Somalia's own
African Risk Capacity (ARC) sovereign drought policy, which lets Start Network draw a
matching payout when the same index triggers, channelled to civil-society/NGO delivery
rather than government systems. In at least one season (2023) this was supplemented by
Start Network's own pre-arranged Start Ready facility. Unlike IFRC's or WFP's single-EAP
model, there is no standalone public trigger document; the mechanism and its payouts are
documented through ARC Group and Start Network press releases issued each time the
policy pays out.

## Trigger
Parametric, not analyst-judged: ARC's **Africa RiskView** software models a **WRSI**
(Water Requirements Satisfaction Index) drought index from satellite rainfall data,
overlaid with population-vulnerability weighting (poverty distance and agricultural
income exposure), separately for each ARC member country and season (Gu, March-June, or
Deyr, October-December). When the index for Somalia crosses its pre-agreed threshold for
a season, ARC pays out automatically to both the Federal Government of Somalia's policy
and Start Network's Replica policy, typically within weeks of the season's confirmed
failure — much faster than traditional response financing. No source reviewed publishes
the specific numeric WRSI/index threshold set for Somalia's policy (see
`extra.schema_strain`).

## Funding & scope
The Anticipation Hub inventory currently lists a pre-arranged envelope of US$2,027,586
against 22,207 target people for this framework, but that figure does not reconcile
cleanly to any single documented policy premium or sum-insured value (see
`extra.schema_strain`). What is documented, season by season:
- **2023**: US$3.38M ARC Replica payout + US$891,800 (£700,000) Start Ready top-up
  (~US$4.2M combined), reaching 51,318 people via cash transfers.
- **2025 (2024/25 season)**: US$727,855 ARC Replica payout to Start Network (part of a
  US$2,183,565 combined ARC payout with the Somali government), funding cash transfers
  to 10,500 households.
- **2026**: Start Network's ~21.5% share (~US$1.18M) of a US$5.5M combined ARC payout
  with SODMA and WFP.

## Activations
- **March 2023** — fifth consecutive failed rainy season confirmed; US$4.2M combined
  ARC Replica + Start Ready funding delivered by a GREDO/WASDA/SSWC/Save the
  Children/Oxfam/World Vision consortium as three rounds of US$120/household cash
  transfers (April-July 2023), reaching 51,318 people.
- **21 March 2025** — 2024/25-season ARC payout; Start Network's US$727,855 share funded
  cash transfers to 10,500 households (alongside US$1,455,710 to the Somali government
  for 35,000 households).
- **28 May 2026** — parametric indices confirmed for the failed 2025 Deyr and weak 2026
  Gu seasons; a US$5.5M combined ARC payout split SODMA/Start Network/WFP, reported to
  have reached 153,000+ people between the three partners.

No trigger-not-met or near-miss events were found in public reporting.

## Sources
- **Authoritative:** [ARC Group press release, 21 Mar 2025](https://arcltd.org/the-arc-group-makes-climate-insurance-payouts-to-the-federal-republic-of-somalia-and-the-start-network-to-assist-people-affected-by-drought/) (2024/25-season payout breakdown)
- [ARC Group — "New funding streams activated after fifth successive failed rainy season in Somalia"](https://arc.int/news/new-funding-streams-activated-after-fifth-successive-failed-rainy-season-somalia) (2023 activation)
- [Reinsurance News — Start Network receives $727K ARC Replica payout](https://www.reinsurancene.ws/start-network-receives-727k-arc-replica-insurance-payout-for-drought-relief-in-somalia/)
- [Reinsurance News — Somalia secures $5.5m drought parametric payout from ARC](https://www.reinsurancene.ws/somalia-secures-5-5m-drought-parametric-payout-from-arc/) · [The Insurer, same event](https://www.theinsurer.com/parametric-insurer/news/somalia-drought-triggers-55-million-african-risk-capacity-payouts-2026-05-26/)
- [Start Network — "Start Ready and ARC Replica Response to Drought in Somalia"](https://startnetwork.org/learn-change/resources/library/start-ready-and-arc-replica-response-drought-somalia) (org's own case study; could not be fetched directly in this pass, cited by title/URL only)
- [Start Network — ARC Replica fund page](https://startnetwork.org/funds/disaster-risk-financing/arc-replica)
- [Artemis.bm — ARC sells first replica parametric policies to WFP & Start Network](https://www.artemis.bm/news/arc-sells-first-replica-parametric-policies-to-wfp-start-network/) (mechanism background)
- [ARC Group — Africa RiskView methodology](https://arc.int/news/africa-riskview-methodology) (WRSI index background)
- [Anticipation Hub — Somalia country page](https://www.anticipation-hub.org/global-overview/countries/somalia) (current funding/target-people listing)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
