---
content_type: framework-external
framework: start-network-phl-tropical-cyclone
org: START
country_iso3: PHL
hazard: tropical-cyclone
status: active
valid_until: null
trigger_summary: >-
  Start Ready's general model releases pre-arranged funds ahead of forecast tropical-cyclone
  impact; in the Philippines the local consortium (Oxfam, FAO, Start Network member agencies)
  co-designs activation indicators with communities — storm-surge cues from fisherfolk,
  rainfall thresholds from farmers, market/food-supply-chain signals from women's groups —
  rather than a single published meteorological threshold. Realized lead times: ~55 hours
  before Typhoon Doksuri's closest approach (2023) and up to 48 hours before Trami/Man-yi
  landfalls (2024). No quantitative threshold document was accessible to verify further (see
  `extra.schema_strain`).
data_sources: [PAGASA]
# --- funding & scope (same field names as OCHA pages) ---
prearranged_funding_usd: 2149553
funding_by_source: {Start Ready fund: 2149553}
target_people: 55331
# --- documents ---
framework_doc: https://startnetwork.org/funds/start-ready/activations/pln-00000202
framework_doc_date: null
sources:
- https://www.anticipation-hub.org/experience/global-map
- https://www.anticipation-hub.org/global-overview/countries/philippines
- https://www.macphilanthropies.org/highlights/saving-lives-through-early-action-and-locally-led-response/
- https://www.fmreview.org/climate-choices/chadburn-espinola-abogado/
- https://oxfam.org.ph/anticipatory-financing-enabling-choice-amid-displacement-in-the-philippines/
- https://startnetwork.org/learn-change/resources/library/typhoon-doksuri-and-start-ready-insights-anticipatory-action-cagayan
# --- activation history (same shape as OCHA pages) ---
activations:
- date: '2023-07-23'
  url: https://www.macphilanthropies.org/highlights/saving-lives-through-early-action-and-locally-led-response/
  note: >-
    Super Typhoon Doksuri (local name Egay) — Start Ready activated ~55 hours before
    closest approach; the Cagayan Consortium (led by Humanity & Inclusion, with Relief
    International, Saint Paul University Philippines, and Green Meadow Development
    Foundation) delivered anticipatory cash, WASH, health, GBV-prevention and awareness
    activities reaching ~37,538 people at highest risk, including multi-purpose cash to
    252 households in Camalaniugan.
- date: '2024-10'
  url: https://www.fmreview.org/climate-choices/chadburn-espinola-abogado/
  note: >-
    2024 cyclone cluster (Trami, Kong-rey, Yinxing, Toraji, Usagi, Man-yi, six storms in
    rapid succession) — ahead of Trami (landfall ~24 Oct) and Man-yi (landfall ~Nov),
    Start Network partners (with Oxfam, FAO) distributed anticipatory cash of US$56-60
    to ~21,250 households (≈US$205,300 total) in Cagayan and Catanduanes provinces,
    enabling evacuation up to 48h in advance.
last_checked: '2026-07-24'
extra:
  hub_captions:
  - '2022: Cyclone / Typhoon / Hurricane (Start Network) [Humanity & Inclusion] [CARE International]
    [Agri-Aqua Development Coalition] [Leyte Center for Development] [ACCORD] [Green Meadow
    Development Foundation] [Saint Paul University Philippines - Community Development Center]'
  - '2023: Cyclone / Typhoon / Hurricane (Start Network) [CARE International] [Green Meadow
    Development Foundation] [Humanity & Inclusion] [Relief International] [Saint Paul University
    Philippines - Community Development Center]'
  - '2024: Cyclone / Typhoon / Hurricane (Start Network) [Humanity & Inclusion]'
  hub_years:
  - '2022'
  - '2023'
  - '2024'
  implementing:
  - Humanity & Inclusion
  investment_by_year:
    '2022': {target_people: 30340, investment_usd: 616841}
    '2023': {target_people: 14985, investment_usd: 761100}
    '2024': {target_people: 55331, investment_usd: 2149553}
  coordination: >-
    OCHA's phl-storms 2025 CERF AA framework (frameworks/phl-storms/2025-10-03.md) lists
    "Start Network" among ~US$4M of partner co-financing alongside Plan, WFP internal
    funds, Oxfam and the Philippine Red Cross. However the confirmed Start Ready
    activations here (Doksuri 2023 in Cagayan; Trami/Man-yi 2024 in Cagayan and
    Catanduanes) fall in Region 2 and Bicol-adjacent provinces, outside the CERF
    framework's three funded regions (5 Bicol, 8 Eastern Visayas, 13 Caraga). Start Ready
    therefore reads as an independently-triggered NGO mechanism that co-finances/aligns
    with the OCHA collective framework rather than being literally one of its components
    — do not present it as a piece of `phl-storms`.
  schema_strain: >-
    The Hub inventory records 2022/2023/2024 as three separate annual figures linked to
    the same plan URL (2022: 30,340 people/US$616,841; 2023: 14,985/US$761,100; 2024:
    55,331/US$2,149,553), not a single fixed pre-arranged ceiling — prearranged_funding_usd
    and target_people above are the most recent (2024) year; treat as realized annual
    reach, not a static envelope (see extra.investment_by_year). The Start Ready plan
    document (framework_doc, pln-00000202) returns HTTP 403 to automated fetches and is
    unreachable via web.archive.org from this environment, so trigger thresholds,
    validity period, and framework_doc_date could not be verified against Start
    Network's own primary document; trigger_summary is reconstructed from partner
    secondary reporting (Oxfam Philippines, macphilanthropies.org, Forced Migration
    Review). A reported "£20k released" figure for the Doksuri activation surfaced only
    in an AI-summarized web search (not a directly fetchable page) and is omitted here
    as uncorroborated.
visibility: public
---

# START — Philippines tropical cyclone

## Summary
Start Network's Start Ready risk-financing facility pre-arranges rapid funding for NGO
consortia to deliver anticipatory cash and other assistance ahead of destructive typhoons
in the Philippines, implemented mainly through Humanity & Inclusion-led consortia (with
CARE International, Relief International, Green Meadow Development Foundation, Saint Paul
University Philippines, and others across 2022-2024). It has been activated at least
twice with confirmed real-world impact: for Typhoon Doksuri (2023) in Cagayan, and for the
dense 2024 cyclone cluster (Trami, Man-yi and four other storms) in Cagayan and
Catanduanes. It operates alongside, but is distinct from, OCHA's CERF anticipatory action
framework for the same hazard (see `extra.coordination`).

## Trigger
No quantitative trigger document was accessible (see `extra.schema_strain`). What is
confirmed from partner reporting: Start Ready's general model releases pre-arranged funds
ahead of forecast typhoon impact, and in the Philippines specifically, local consortium
partners (Oxfam, FAO, Start Network members) co-design activation indicators with
communities — storm-surge cues from fisherfolk, rainfall thresholds from farmers, and
market/food-supply-chain disruption signals from women's groups — rather than relying on
a single published meteorological index. Realized lead times were ~55 hours before
Typhoon Doksuri's closest approach (2023) and up to 48 hours before Trami/Man-yi landfalls
(2024).

## Funding & scope
Hub inventory figures vary substantially by year rather than reflecting one fixed ceiling:
2022 US$616,841 / 30,340 people targeted; 2023 US$761,100 / 14,985; 2024 US$2,149,553 /
55,331 (see `extra.investment_by_year`). The 2024 cyclone-cluster response alone
distributed ≈US$205,300 (US$56-60/household) to ~21,250 households in Cagayan and
Catanduanes.

## Activations
- **Jul 2023, Super Typhoon Doksuri (Egay)** — Start Ready activated ~55h before closest
  approach; Cagayan Consortium (led by Humanity & Inclusion) reached ~37,538 people at
  highest risk, incl. cash to 252 households in Camalaniugan.
- **Oct-Nov 2024, cyclone cluster (Trami, Kong-rey, Yinxing, Toraji, Usagi, Man-yi)** —
  ~21,250 households received anticipatory cash (≈US$205,300 total) in Cagayan and
  Catanduanes, enabling evacuation up to 48h in advance.

## Sources
- **Framework page (authoritative, but blocked to automated fetch — HTTP 403):**
  [Start Ready — Philippines activation pln-00000202](https://startnetwork.org/funds/start-ready/activations/pln-00000202)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory records, fetched 2026-07-10)
- [Anticipation Hub — Philippines country overview](https://www.anticipation-hub.org/global-overview/countries/philippines)
- [Margaret A. Cargill Philanthropies — "Saving lives through early action and locally-led response"](https://www.macphilanthropies.org/highlights/saving-lives-through-early-action-and-locally-led-response/) (Doksuri 2023 detail)
- [Forced Migration Review — "Anticipatory financing: enabling choice amid displacement in the Philippines"](https://www.fmreview.org/climate-choices/chadburn-espinola-abogado/) (2024 cyclone cluster detail)
- [Oxfam Pilipinas — same title](https://oxfam.org.ph/anticipatory-financing-enabling-choice-amid-displacement-in-the-philippines/) (trigger co-design detail)
- [Start Network resource library — "Typhoon Doksuri and Start Ready"](https://startnetwork.org/learn-change/resources/library/typhoon-doksuri-and-start-ready-insights-anticipatory-action-cagayan) (cited by search; page itself blocked to automated fetch)
