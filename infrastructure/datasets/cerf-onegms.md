---
content_type: dataset
name: CERF OneGMS allocations
aliases: [OneGMS, "CERF API", "cerfgms-webapi", "CERF allocations"]
provider: "UN OCHA — CERF secretariat (OneGMS grant-management system)"
data_type: humanitarian-financing
access: public
api: "https://cerfgms-webapi.unocha.org/v1/application/All.xml  (full feed, ~1.6k applications, ~6 MB XML; also .json)"
auth: none
formats: [xml, json]
resolution: "application-level (one row per CERF application), 2006–present; country + emergency type + window (RR/UF), USD amounts, individuals planned/reached, narrative summaries"
update_cadence: "live feed from OneGMS; reached/planned figures fill in as reports come through (RR reports due ~9 months after allocation)"
license: open (public UN data)
code_ref: "ds-cerf-supplement scripts/refresh_mirror.py (daily feed upsert) + src/cerf_api.py (fetch); ds-knowledge-base scripts/load_aa_cerf.py (AA layer + curated flags)"
mirror: automated       # feed columns of aa.cerf_allocation upserted DAILY by ds-cerf-supplement refresh-mirror; the AA layer (aa_adhoc/aa_note + link tables) is still hand-loaded via load_aa_cerf.py
mirror_priority: med
used_by:
  - pipelines/cerf-supplement.md
  - apps/cerf-global-trigger-allocations-app.md
last_verified: 2026-07-13
---

# CERF OneGMS allocations

The authoritative public feed of **every CERF application** (Rapid Response +
Underfunded Emergencies) from the OneGMS grant-management system: amounts requested
and approved, emergency type, **individuals planned and reached**, key dates, and the
narrative chief-of-note summaries. Our reference for CERF allocation facts —
including the **anticipatory-action allocations** that fund CERF AA framework
activations.

## Access

- `GET https://cerfgms-webapi.unocha.org/v1/application/All.xml` — no auth, ~6 MB,
  one `<application>` element per application, 43 fields. `All.json` also works.
- No pagination; fetch the whole feed (takes ~1 min). `ds-cerf-supplement`'s
  `src/cerf_api.py` has the minimal fetch/parse pattern.

## Key gotchas

- **`ApplicationID` is NOT unique** (~431 collisions, e.g. ID 1019 = both Madagascar
  2007 and Afghanistan 2023). **Always key on `ApplicationCode`**
  (e.g. `23-RR-AFG-61441`, newer style `CERF-GTM-26-RR-1521`) — unique and non-null.
  (Found the hard way in `ds-cerf-supplement`.)
- **No structured AA flag.** Anticipatory-action allocations are only identifiable
  from title keywords — usually "(Anticipatory Action …)", but Somalia and SSD use
  "Early Action". The curated activation↔allocation mapping lives in
  `scripts/aa_cerf_links.csv` (see below), not in keyword guesses.
- `TotalIndividualReached` is 0/empty until the country office reports (~9 months
  post-allocation) — 0 for a recent allocation means "not yet reported", not "none".
- An AA application is often **pre-arranged months before the trigger fires**
  (title month = arrangement; `FirstProjectApprovedDate` ≈ disbursement/trigger).
- `CountryCode` is ISO3.

## Where it lands in our DB (dev, schema `aa`)

The full feed lands in **`aa.cerf_allocation`**, written by **two coexisting writers**:

- **Feed columns — refreshed daily, automatically.** `ds-cerf-supplement`'s
  `scripts/refresh_mirror.py` (its `refresh-mirror` workflow) upserts the whole OneGMS
  feed into `aa.cerf_allocation` keyed on `application_code`, so the mirror stays current
  without anyone re-running the KB loader.
- **AA layer — hand-loaded via `scripts/load_aa_cerf.py`** (this repo). It owns the table
  schema and links REAL AA framework activations (parsed from the framework pages'
  `activations:` frontmatter → **`aa.actual_activation`**) to their CERF applications via
  the curated **`aa.activation_allocation`** (many-to-many: LAC Mar-2026 = 1 activation →
  3 country applications; TCD-drought 2026 / ETH 2020-21 = several activations → 1
  application). **Ad-hoc** anticipatory/early-action allocations with no OCHA framework
  behind them (Somalia 2023-25 early actions, Ethiopia OND-2024 drought) are flagged
  `aa_adhoc` + `aa_note` instead of linked. **`aa.v_activation_funding`** gives the
  per-activation rollup — CERF USD approved, individuals planned/**reached** — and
  **`aa.v_aa_allocation`** lists every AA allocation, framework-linked or ad-hoc. Re-run
  the loader + review its gap report (`--propose`) after new activations or allocations.

The two don't clobber each other: `refresh_mirror.py` writes only feed-derived columns
(+ the deterministic `aa_keyword`) and never touches `aa_adhoc`/`aa_note` or the AA-link
tables; `load_aa_cerf.py` re-derives everything from the same feed. So the **pure-mirror
proposal below is now partly realized** — the feed columns are already normalized and
idempotently reloaded from `ds-cerf-supplement`.

<!-- TODO: finish the pure-OneGMS-mirror split — the remaining AA-specific columns
(aa_adhoc, aa_note) are our interpretation, not feed data, and could move to a separate
side table so aa.cerf_allocation is a *pure* mirror owned solely by refresh_mirror.py.
Touches load_aa_cerf.py + the aa.v_* views — coordinate with the aa trigger-performance
work. (aa_keyword is deterministic from the title, so it can stay on the mirror.) -->

## Related tables (storm matches)

Storm/drought enrichment of these allocations lives in a **separate** pair of tables
(same key, `application_code`), produced by [`cerf-supplement`](../../pipelines/cerf-supplement.md):
`aa.cerf_allocation_storm (application_code, sid)` → joins to `storms.ibtracs_storms`,
and `aa.cerf_supplement (application_code, not_tc, valid_month/year_*, notes)`. So
`aa.cerf_allocation` stays the clean feed mirror; the IBTrACS matching is layered on top.

## Used by

- **`ds-cerf-supplement`** — **refreshes the feed columns** of `aa.cerf_allocation` daily
  (`refresh_mirror.py`) and matches storm allocations to IBTrACS storm(s), writing
  `aa.cerf_allocation_storm` + `aa.cerf_supplement` (chained daily GHAs + static GH Pages site).
- **`aa` schema trigger-performance work** — actual-activation outcomes alongside the
  simulated/backtest tables (`load_aa_performance.py`).
- The CERF global trigger allocations app (`ds-aa-cerf-global-trigger-allocations`)
  is a future consumer (currently reads its own blob extracts).
