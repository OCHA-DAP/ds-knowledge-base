---
content_type: dataset
name: IPC
aliases: [CH, "Cadre Harmonisé", IPC-CH, IPC/CH]
provider: "IPC Global Partnership (FAO, FEWS NET, WFP, UNICEF, Save the Children, CILSS/CH for West Africa & the Sahel, and others)"
data_type: food-security-phase
access: registered
api: "https://api.ipcinfo.org/  (docs: https://docs.api.ipcinfo.org/)"
auth: "free API key — request via a form; key is per-user"
formats: [json, geojson, vector-tiles, xlsx]
resolution: "sub-national units (admin areas, urban areas, IDP camps, HFA zones); Acute Food Insecurity phases 1–5; 'current' + 'projection' periods"
update_cadence: "2–3 analyses per country per year (irregular; on assessment cycles); >45 countries covered"
license: "IPC Terms of Use — attribution required, non-commercial"
code_ref: OCHA-DAP/ds-ipc-mirror
mirror: automated       # none | manual | automated | n/a  — is a copy in OUR blob/DB?
mirror_priority: high   # mirrored since 2026-07 — see pipelines/ipc-mirror.md
used_by:
  - frameworks/som-drought/2019.md
  - frameworks/eth-drought/2020-12-07.md
  - frameworks/eth-drought/2026-06-09.md
  - frameworks/ken-drought/2023-02-19.md
  - frameworks/mrt-drought/2026-04-17.md
  - frameworks/lac-dry-corridor/2025-02.md
  - analysis/eth-flooding.md
last_verified: 2026-07-24
---

# IPC / Cadre Harmonisé

The **Integrated Food Security Phase Classification** (and its West-Africa/Sahel
counterpart, the **Cadre Harmonisé**) is the consensus classification of acute food
insecurity — the **Phase 1–5** scale (Minimal → Famine) most of our drought/food-security
frameworks trigger against or reference for context. IPC and CH share a single API.

## How we access it

- **Public API** at `api.ipcinfo.org` — Acute Food Insecurity classifications for 45+
  countries, current + projection periods, as **population tables** and **maps** (GeoJSON
  or vector tiles). Requires a **free API key** (request form → per-user key). Full
  reference at `docs.api.ipcinfo.org` (Public API v2.0).
- Country analyses are also downloadable as **xlsx** from the IPC website, and mirrored
  on **HDX** ([`ipc`](https://data.humdata.org/organization/ipc) org) and the FAO catalog.

**Mirrored daily** since 2026-07 by [`ds-ipc-mirror`](../../pipelines/ipc-mirror.md)
into the dev DB, schema `ipc`: full 2017+ analysis history (names only,
`ipc.population`), the HAPI p-coded admin 0–2 layer Oct 2020+
(`ipc.population_admin`), and the analysis registry (`ipc.analyses`). Read it
from there rather than hitting the API/HDX ad hoc.

## How we use it

Drought frameworks use the projected IPC/CH phase as a **situational anchor** or an
**activation condition** (e.g. a threshold share of population in Phase 3+ / a projected
move to Phase 4). Note the authority caveat below when reconciling against FEWS NET.

## Gotchas

- **IPC ≠ [FEWS NET](fews-net.md).** FEWS NET classifications are *IPC-compatible* but
  are FEWS NET's own analysis and **do not always match** the IPC technical consensus.
  Name which source a trigger uses; don't treat them as interchangeable.
- Analyses are **irregular** — coverage and recency vary by country; a "projection" can be
  months old. Check the analysis date, not just the phase.
- Phases are **areal** (a unit's dominant phase), not a continuous surface.

### Reading `ipc.population_admin` (hard-won, 2026-08)

Four traps, all found by checking a live product against the IPC country pages. Each of
them silently understates severity, which is the dangerous direction. See
[methods/absent-data.md](../../methods/absent-data.md) for the general rule.

- **A projection covers FEWER areas than the current period, but the `all` row stays at
  full country scope.** Sudan's Jan-2026 exercise says so outright: Feb–May 2026 covers
  all 195 localities; Jun–Sep 2026 and Oct–Jan 2027 cover **56** — *"data was not
  available for a full nationwide projection analysis"*. So 135 of 189 admin-2 units
  carry a population with **no phase rows at all** for those windows. Those units are
  *outside the projection*, not units with nobody in crisis.
- **Therefore: missing phases must never be read as Phase 1.** The standard area rule
  (highest phase reaching ≥20% of the analysed population) walks down from 5, finds
  nothing, and falls through to **class 1 — "Minimal"**. That renders the world's largest
  food crisis as the mildest category available. Test `sum(phases) > 0` before
  classifying; if it is zero, the unit is *not assessed*.
- **Duplicate rows: dedupe on the KEY, never including the value.** HAPI ships some units
  twice per period, same `resource_hdx_id`, and the two copies round the same published
  figure independently — SSD Rumbek North Apr–Jul 2026 is `77,350 × 0.15 = 11,602.5`
  filed once as `11,603` and once as `11,602`. An all-column `drop_duplicates` keeps both
  and any `sum`/pivot doubles them. The `all` rows of the same pairs round identically and
  *do* dedupe, so phase sums land at a clean **2.00×** their analysed population — that
  ratio is the tell. Dedupe on
  `(location, admin codes, phase, type, period)`; it dropped 1,023 rows at admin-1 and 837
  at admin-2 and reproduced IPC's published South Sudan totals to within 0.2%.
- **The newest analysis is often national-only in the admin layer.** Haiti's Mar–Jun 2026
  and Somalia's Apr–Jun 2026 projection updates each carry **one** usable subnational unit
  while the *previous* analysis carries the full breakdown (11 departments / 18 regions).
  A subnational product must therefore fall back to the earlier analysis — which looks
  like staleness but is not. Check unit counts per period before concluding you are behind.

### Whole countries arrive with placeholder p-codes

HAPI ships every area of some countries under a single `<ISO3>-XXX` code, with the real
admin name in the name column: **Madagascar, Tanzania, Lesotho, Djibouti, Burundi,
Eswatini**. Dropping those rows loses the country — ~9.4M people in phase 3+ were absent
from a live product for this. **And any `groupby`/`pivot` keyed on the p-code sums the
whole country into one row** labelled with an arbitrary area name (Madagascar: 32.7M
analysed on "MENABE"), which is a mis-attribution no national-total check can see.

Key the aggregation on the **name** when the code cannot separate areas, then name-match.
Recovering Madagascar, Lesotho and Djibouti this way reproduced the mirror's own national
phase-3+ totals at ratios 0.92 / 1.000 / 1.000. Full recipe and the four name-matching
traps: [methods/pcode-matching.md](../../methods/pcode-matching.md).

Two of the six stay out, correctly: **Burundi and Eswatini's current analyses are
agro-ecological zones** (`Imbo`, `Crête Congo-Nil`, `Lubombo plateau`), which have no admin
polygon at any level. **Tanzania** publishes at admin-2. Note the IPC table can hold a
country's real regions *and* its zones — Eswatini has both; only the zones are current.

### Presenting it

- **One analysis period per map.** ipcinfo.org draws Current / Projected 1 / Projected 2
  as three separate maps and leaves areas outside a projection **white**. Selecting the
  best period *per unit* instead blends vintages under one title — a real product did
  this and put four different periods on one Sudan map. Pick the period for the whole
  country and blank what it does not cover.
- Reproduce IPC's own ramp so figures are recognisable:
  `#cdfacd · #fae61e · #e67800 · #c80000 · #640000` for phases 1–5.
- Country totals from admin data will sit **slightly below** IPC's headline: IPC analyses
  localities *and IDP settlements*, some of which carry no admin p-code. Sudan Feb–May
  2026 is 19.47M published vs ~17.97M summing mapped admin-2 units. Say so rather than
  quietly differing.
