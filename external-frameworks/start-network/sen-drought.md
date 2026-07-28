---
content_type: framework-external
framework: start-network-sen-drought
org: START
country_iso3: SEN
hazard: drought
status: active
valid_until: null
trigger_summary: >-
  Not a written EAP-style trigger document — a parametric drought insurance product. Start
  Network holds an ARC Replica policy that mirrors the Government of Senegal's African Risk
  Capacity (ARC) sovereign drought policy; both are keyed to the same Africa RiskView (ARV)
  model, which uses satellite-derived rainfall estimates to model a crop water-deficit index
  and an associated modelled response cost for the season. When ARV's modelled cost crosses
  the policy's pre-agreed attachment point, the Government and Start Network payouts trigger
  together (same season, same underlying data). Public sources describe this only as "when
  rainfall levels fall below a certain threshold" — ARC does not publish the country-specific
  attachment point.
data_sources: [Africa RiskView]
prearranged_funding_usd: 957854
funding_by_source: {}
target_people: 18387
framework_doc: https://reliefweb.int/report/senegal/new-insurance-policy-will-protect-160000-people-senegal-drought
framework_doc_date: 2021-10-07
sources:
- https://reliefweb.int/report/senegal/new-insurance-policy-will-protect-160000-people-senegal-drought
- https://reliefweb.int/report/senegal/global-network-aid-agencies-signs-game-changing-drought-insurance-policy-early
- https://reliefweb.int/report/senegal/10m-insurance-payout-announced-aid-charities-act-early-mitigate-drought-senegal
- https://startnetwork.org/learn-change/news-and-blogs/largest-ever-early-humanitarian-action-payout-received-start-network-mitigate-drought
- https://www.artemis.bm/news/african-risk-capacitys-parametric-drought-payout-to-senegal-hits-23m/
- https://startnetwork.org/learn-change/news-and-blogs/senegal-receive-financial-assistance-ahead-drought-predictions
- https://startnetwork.org/news-and-blogs/statement-arc-replica-start-network
- https://startnetwork.org/funds/disaster-risk-financing/arc-replica
- https://www.anticipation-hub.org/experience/global-map
activations:
- date: "2019-11"
  url: https://startnetwork.org/learn-change/news-and-blogs/largest-ever-early-humanitarian-action-payout-received-start-network-mitigate-drought
  note: >-
    ARC Replica policy triggered by the 2019 agricultural-season drought (ARV-modelled
    deficit). $10.6m paid to Start Network alongside $12.5m to the Government of Senegal
    ($23.1m total ARC payout, a 5% top-up on the initial $22m estimate) — the first payout
    from a sovereign ARC risk pool to a non-sovereign actor, and the largest early-action
    payout to civil society to date. Six Start Network members (Action Against Hunger,
    Catholic Relief Services, Oxfam, Plan International, Save the Children, World Vision)
    delivered enriched flour and cash transfers to ~335,000 people across 7 regions through
    2020.
- date: "2023"
  url: https://startnetwork.org/learn-change/news-and-blogs/senegal-receive-financial-assistance-ahead-drought-predictions
  note: >-
    Separate, smaller Start Fund Anticipation disbursement (~£330,000 / $400,500) released
    ahead of the 2023 drought season for localized early action by Start Network members and
    local partners — distinct from, and much smaller than, the ARC Replica insurance
    mechanism above.
last_checked: '2026-07-28'
extra:
  hub_captions:
  - '2022: Drought (Start Network) [Action Against Hunger]'
  - '2024: Drought (Start Network) [Action Against Hunger] [Catholic Relief Services] [Oxfam]
    [Plan International] [Save the Children] [World Vision International]'
  hub_years:
  - '2022'
  - '2024'
  implementing:
  - Action Against Hunger
  - Catholic Relief Services
  - Oxfam
  - Plan International
  - Save the Children
  - World Vision International
  mechanism: >-
    ARC Replica is Start Network's non-sovereign "shadow" purchase of the same African Risk
    Capacity parametric drought policy the Government of Senegal buys each season, funded via
    BMZ/KfW premium support; it pays a linked, second amount to Start Network members when the
    government's policy triggers. This is structurally an insurance product, not a
    written EAP/protocol like most pages in this section — there is no single public trigger
    document giving the country-specific attachment threshold, lead time, or per-season sums.
  operational_risk: >-
    A Start Network statement (undated relative to this check) records at least one season in
    which the Government of Senegal's ARC premium payment was delayed, and as a result Start
    Network's linked Replica policy "could not be made effective" for that season — a
    coverage gap, not a below-threshold near-miss. Recorded here per the "activation flavors"
    guidance rather than in `activations`, since no policy was in force to trigger.
  schema_strain: >-
    prearranged_funding_usd (957,854) and target_people (18,387) are carried over unchanged
    from the Anticipation-Hub-generated stub (likely the Hub's Action-Against-Hunger-specific
    attribution for the 2022 listing) and could not be traced to a specific public
    Start-Network-published sub-budget. They do not match the more prominent public figures
    found: the Oct 2021-renewed policy's advertised $1.5m cover protecting "up to 160,000
    people," the 2019 season's $10.6m Start Network payout reaching ~335,000 people, or the
    2023 season's separate $400,500 Start Fund Anticipation disbursement. Treat the frontmatter
    numbers as an approximate, Hub-attributed slice for one season/org, not a confirmed
    current budget line.
  currency_note: >-
    2019-season premiums were denominated in FCFA (Government ~1.9bn FCFA, Start Network
    ~1.6bn FCFA per the Artemis.bm report); USD payout figures above are as reported in
    English-language coverage, not converted by us.
visibility: public
---

# START — Senegal drought

## Summary
Start Network's Senegal drought framework is a parametric **insurance** product, not a
written EAP: an **ARC Replica** policy that mirrors the Government of Senegal's sovereign
African Risk Capacity (ARC) drought policy season for season, funded through BMZ/KfW premium
support and delivered by a consortium of Start Network members (Action Against Hunger,
Catholic Relief Services, Oxfam, Plan International, Save the Children, World Vision — the
full list in the Hub's 2024 listing; only Action Against Hunger in its 2022 listing). First
signed in August 2018 and renewed at least through October 2021, it has produced one
confirmed large payout (2019 season) and at least one much smaller, separately-run
anticipation disbursement (2023).

## Trigger
There is no single public trigger document with a country-specific threshold. Both the
Government's ARC policy and Start Network's linked Replica policy are keyed to **Africa
RiskView (ARV)**, ARC's satellite-rainfall-driven model of crop water deficit and estimated
response cost for the season; when ARV's modelled cost crosses the policy's pre-agreed
attachment point, both payouts trigger together. Public reporting describes this only in
plain terms — "when rainfall levels fall below a certain threshold" — without publishing the
Senegal-specific attachment value or lead time. Because Start Network's Replica payout is
*conditional on* the Government's premium being paid, coverage has at least once lapsed for a
season when that premium payment was delayed (see `extra.operational_risk`) — a structural
risk distinct from a below-threshold non-activation.

## Funding & scope
The most recent confirmed policy (renewed 7 October 2021) was reported as a $1.5m cover
protecting up to 160,000 people. The frontmatter's `prearranged_funding_usd` ($957,854) and
`target_people` (18,387) come from the Anticipation Hub's inventory (likely its
Action-Against-Hunger-specific slice of the 2022 listing) and could not be independently
confirmed — see `extra.schema_strain`. Funding flows via ARC Replica premiums (BMZ/KfW-backed)
rather than a CERF/DREF-style pooled fund.

## Activations
- **2019 (payout Nov 2019):** ARV-modelled drought triggered the linked policies; $10.6m to
  Start Network (of $23.1m total ARC payout, alongside $12.5m to the Government of Senegal) —
  the first ARC payout to a non-sovereign actor. Six Start Network members reached ~335,000
  people with enriched flour and cash transfers across 7 regions through 2020.
- **2023:** a separate, much smaller Start Fund Anticipation disbursement (~$400,500) ahead
  of the drought season, run alongside but distinct from the ARC Replica mechanism.
- At least one season's Replica coverage lapsed due to delayed government premium payment
  (undated) — a coverage gap, not a recorded activation or near-miss; see `extra`.

## Sources
- **Authoritative (current policy terms):** [New insurance policy will protect up to 160,000 people in Senegal from drought, ReliefWeb, 7 Oct 2021](https://reliefweb.int/report/senegal/new-insurance-policy-will-protect-160000-people-senegal-drought)
- [Global network of aid agencies signs 'game-changing' drought insurance policy for early humanitarian response in Senegal, ReliefWeb, 30 Aug 2018](https://reliefweb.int/report/senegal/global-network-aid-agencies-signs-game-changing-drought-insurance-policy-early) (original policy signing)
- [$10m insurance payout announced for aid charities to act early to mitigate drought in Senegal, ReliefWeb, 22 Sep 2019](https://reliefweb.int/report/senegal/10m-insurance-payout-announced-aid-charities-act-early-mitigate-drought-senegal)
- [Largest ever early humanitarian action payout received by the Start Network to mitigate drought in Senegal, Start Network](https://startnetwork.org/learn-change/news-and-blogs/largest-ever-early-humanitarian-action-payout-received-start-network-mitigate-drought) (Nov 2019 payout confirmation)
- [African Risk Capacity's parametric drought payout to Senegal hits $23m, Artemis.bm](https://www.artemis.bm/news/african-risk-capacitys-parametric-drought-payout-to-senegal-hits-23m/) (payout breakdown, FCFA premiums)
- [Senegal to receive financial assistance ahead of drought predictions, Start Network](https://startnetwork.org/learn-change/news-and-blogs/senegal-receive-financial-assistance-ahead-drought-predictions) (2023 disbursement)
- [Statement on ARC Replica: Start Network](https://startnetwork.org/news-and-blogs/statement-arc-replica-start-network) (premium-delay coverage gap)
- [ARC Replica, Start Network](https://startnetwork.org/funds/disaster-risk-financing/arc-replica) (program background)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record, 2022/2024 listings)
