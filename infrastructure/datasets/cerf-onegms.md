---
content_type: dataset
name: CERF OneGMS allocations
aliases: [OneGMS, "CERF API", "cerfgms-webapi", "CERF allocations", "CERF projects"]
provider: "UN OCHA — CERF secretariat (OneGMS grant-management system)"
data_type: humanitarian-financing
access: public
api: "https://cerfgms-webapi.unocha.org/v1/application/All.xml  (full feed, ~1.6k applications, ~6 MB XML; also .json) + /v1/project/All.json (~8.6k agency projects, ~18 MB, ~8 min server-side generation)"
auth: none
formats: [xml, json]
resolution: "application-level (one row per CERF application) + project-level (one row per agency project under each application), 2006–present; country + emergency type + window (RR/UF), USD amounts, individuals planned/reached (projects: incl. women/men/girls/boys breakdowns), narrative summaries, per-project sector/country splits + HRP cap-codes"
update_cadence: "live feed from OneGMS; reached/planned figures fill in as reports come through (RR reports due ~9 months after allocation)"
license: open (public UN data)
code_ref: "ds-cerf-supplement scripts/refresh_mirror.py (daily allocation upsert) + scripts/refresh_projects.py (daily project upsert) + src/cerf_api.py (fetch); ds-aa-tracking src/ds_aa_tracking/schema.py (the AA layer: activations and their allocation links, D115)"
mirror: automated       # aa.cerf_allocation = pure mirror, upserted DAILY by ds-cerf-supplement refresh-mirror; the AA layer (aa.window_activation + aa.activation_funding; the KB-era aa.actual_activation + aa.activation_allocation are frozen) is owned by ds-aa-tracking
mirror_priority: med
used_by:
  - pipelines/cerf-supplement.md
  - apps/cerf-global-trigger-allocations-app.md
last_verified: 2026-08-07
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
- `GET https://cerfgms-webapi.unocha.org/v1/project/All.json` — the **project-level**
  feed: ~8.6k agency projects (the "Projects included in this allocation" table on
  cerf.un.org), each carrying `applicationCode` (join to applications), agency,
  amount, dates, status, planned/reached people **with women/men/girls/boys
  breakdowns** (post-~2014), project summaries, nested sector/country splits and HRP
  cap-codes. **~8 min server-side generation** — wrong paths 404 instantly, the real
  one just hangs while building; use a generous read timeout (`fetch_project_feed()`
  in `src/cerf_api.py` uses 20 min).
- No pagination; fetch the whole feed (applications ~1 min). `ds-cerf-supplement`'s
  `src/cerf_api.py` has the minimal fetch/parse pattern.

## Key gotchas

- **`ApplicationID` is NOT unique** (~431 collisions, e.g. ID 1019 = both Madagascar
  2007 and Afghanistan 2023). **Always key on `ApplicationCode`**
  (e.g. `23-RR-AFG-61441`, newer style `CERF-GTM-26-RR-1521`) — unique and non-null.
  (Found the hard way in `ds-cerf-supplement`.)
- Same in the project feed: **`projectID` is NOT unique** (~3.1k collisions across
  the feed's two source tables, `tableName` M/P). **Key on `projectCode`**
  (e.g. `06-FAO-010-A`, newer style `CERF-TCD-25-UF-HCR-35482`) — unique and
  non-null. Project `totalAmountApproved` sums exactly to the application's
  amount, and the feed has a handful of real duplicate (project, sector) split
  rows — don't assume that pair is a key.
- **No structured AA flag.** Anticipatory-action allocations are only identifiable
  from title keywords — usually "(Anticipatory Action …)", but Somalia and SSD use
  "Early Action". The curated activation↔allocation mapping lives in
  ds-aa-tracking's **`aa.activation_funding`** (see below), not in keyword guesses.
- `TotalIndividualReached` is 0/empty until the country office reports (~9 months
  post-allocation) — 0 for a recent allocation means "not yet reported", not "none".
- An AA application is often **pre-arranged months before the trigger fires**
  (title month = arrangement; `FirstProjectApprovedDate` ≈ disbursement/trigger).
- `CountryCode` is ISO3.

## Where it lands in our DB (dev, schema `aa`)

> ER diagram of the whole `aa` schema (mirror + crosswalk + performance tables):
> [../db-erd.md](../db-erd.md).

The full feed lands in **`aa.cerf_allocation`** — a **pure OneGMS mirror** (feed columns
+ the deterministic `aa_keyword` title flag), upserted daily by `ds-cerf-supplement`'s
`scripts/refresh_mirror.py` (its `refresh-mirror` workflow), keyed on `application_code`.
Nothing else writes it. (The pure-mirror split proposed on this page was completed
2026-07 / D83: the curated `aa_adhoc`/`aa_note` columns moved off the table into the
crosswalk below.)

The project feed lands in three companion tables (same workflow, second step,
`scripts/refresh_projects.py` — sole writer, added 2026-08), joined to the
allocation mirror on `application_code`:

- **`aa.cerf_project`** — one row per agency project, keyed on `project_code`:
  agency, amount, dates, status, planned/reached people incl. demographic
  breakdowns, HRP cap-codes, project summaries.
- **`aa.cerf_project_sector`** — per-sector USD splits (1–5 rows per project; no
  PK — the feed has real duplicate sector rows with split amounts).
- **`aa.cerf_project_country`** — per-country budget splits (regional projects,
  e.g. the 2018 Venezuela-crisis projects, span up to 22 countries).

Everything AA-interpretive lives in **separate tables beside it**, owned by
[ds-aa-tracking](../../pipelines/aa-tracking.md) (D115):

- **`aa.window_activation`** — framework activations, per country and window; ad-hoc AA and
  early-action allocations with no OCHA framework behind them (Somalia 2023-25 early actions,
  Ethiopia OND-2024 drought) are **`aa.adhoc_activation`**.
- **`aa.activation_funding`** — the **curated link** from an activation to its fund
  allocations: one activation × N allocations, any pooled fund (`allocation_code` = the CERF
  `application_code`, or a CBPF code, via `aa.v_allocation`). Entered on the tracking site's
  entry/admin pages or through an entries file.
- **The KB-era record, frozen** — written by the KB's loaders and its `kb-aa-links` confirm
  flow until the framework pages stopped being a source (2026-09-28): `aa.actual_activation`
  (from framework-page `activations:` frontmatter) and `aa.activation_allocation`, the old
  curated crosswalk. Many-to-many (LAC Mar-2026 = 1 activation → 3 country applications;
  TCD-drought 2026 / ETH 2020-21 = several activations → 1 application, flag `SHARED_APP`),
  plus two special row kinds: `NO_CERF` (activation funded outside CERF, e.g. bfa-flooding
  via FHRAOC) and `ADHOC_AA`. **`aa.v_activation_funding`** (per-activation rollup: CERF USD
  approved, individuals planned/**reached**) and **`aa.v_aa_allocation`** (every AA
  allocation, framework-linked or ad-hoc) still read these two tables.

## Related tables (storm matches + drought periods)

Storm/drought enrichment of these allocations lives in a **separate** pair of tables
(same key, `application_code`), produced by [`cerf-supplement`](../../pipelines/cerf-supplement.md):
`aa.cerf_allocation_storm (application_code, sid)` → joins to `storms.ibtracs_storms`,
and `aa.cerf_supplement (application_code, not_tc, valid_month/year_*, confidence, notes)`
— the `valid_*` fields hold each drought allocation's meteorological (rainfall-deficit)
period, Claude-matched with stored confidence. So `aa.cerf_allocation` stays the clean
feed mirror; the storm/drought matching is layered on top.

## Used by

- **`ds-cerf-supplement`** — **refreshes the feed columns** of `aa.cerf_allocation` daily
  (`refresh_mirror.py`) and the project-level tables (`refresh_projects.py`), matches
  storm allocations to IBTrACS storm(s), and dates drought allocations' valid periods,
  writing `aa.cerf_allocation_storm` + `aa.cerf_supplement`
  (chained daily GHAs + static GH Pages site).
- **`ds-aa-tracking`** — links activations to their allocations (`aa.activation_funding`)
  and reads the mirror for its funding and activation pages, next to the backtest tables it
  also owns.
- The CERF global trigger allocations app (`ds-aa-cerf-global-trigger-allocations`)
  is a future consumer (currently reads its own blob extracts).
