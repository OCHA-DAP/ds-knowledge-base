---
content_type: app
name: onegms-public
purpose: "Live indicator-reporting explorer for CBPF US Award (NSFT) projects, read straight from the public OneGMS/CBPF API"
status: live
tech: other
related: standalone
deployment:
  platform: gh-pages
  ref: "ocha-dap/ds-onegms-public@main"
  url: "https://ocha-dap.github.io/ds-onegms-public/"
  resource_group: null
surfaces: []
inputs:
  - "cbpfapi.unocha.org/vo3/odata/GlobalGenericDataExtract (SPCode=PF_GLB_INDIC) — per-project global-indicator targets/achievements"
  - "cbpfapi.unocha.org/vo3/odata/ProjectSummaryV2 — partner, title, status, budget, dates, targeted people"
  - "cbpfapi.unocha.org/vo3/odata/GlobalGenericDataExtract (SPCode=PF_PROJ_DETAIL) — reached people + partner risk (fallback titles)"
  - "cbpfapi.unocha.org/vo3/odata/NarrativeReportLogicalFramework — cash/voucher indicator rows from each project's latest progress report"
  - "cbpfapi.unocha.org/vo3/odata/GlobalGenericDataExtract (SPCode=GLB_INDIC_MST) — global indicator names/codes/units/core flag"
  - "cbpfapi.unocha.org/vo3/odata/MstClusters — sector names"
depends_on: []
source_repo: ocha-dap/ds-onegms-public
source_branch: main
source_sha: 7d372dc
code_ref:
  - "index.html"
  - "serve.py"
extra:
  schema_strain: "Reads OneGMS's vo3 OData API (indicator/reporting endpoints); infrastructure/datasets/cbpf-odata.md documents the vo2 allocation-level API from the same OneGMS/CBPF system. No dataset page currently covers vo3 — flagging as a gap rather than mis-linking depends_on to the vo2 page."
  no_build_step: true
visibility: public
last_synced: "2026-09-18"
---

# US Allocation: OneGMS Reporting Explorer

> The canonical behaviour is the code at `code_ref` (a single `index.html`); this page explains it.

## What it shows

A single-page tool for CBPF information managers to check indicator reporting on
**CBPF US Award (NSFT) projects** — the "US Award" being the large US grant to
OCHA's country/regional pooled funds, allocated country by country through a
"fast-track" **Reserve Allocation** under an ERC global waiver ([OCHA guidance,
12 Mar 2026](https://www.unocha.org/publications/report/world/ocha-pooled-fund-guidance-landmark-us-award);
[Tranche II guidance](https://www.unocha.org/publications/report/world/ocha-pooled-fund-guidance-us-award-tranche-ii)),
with every funded project code carrying the `NSFT` token — across 21 country funds. Pick a
country, see every project with its partner, budget, status and targeted/reached
beneficiary figures, expand a project to see each indicator's target vs. reach, or
switch to an aggregated view that sums a country's indicators across projects.

## Key features

- **By-project view**: one row per project (partner, status, budget, dates, targeted
  people), expandable to that project's own indicator rows as OneGMS publishes them.
- **By-indicator (aggregated) view**: rows grouped by indicator + sector and summed
  across the country's projects; percentage indicators are averaged, not summed;
  reached totals only include projects that have already reported.
- **Progress charts** popup, following the active filters: a by-sector bar view
  (people targeted vs. reached share) and a core-indicators bar view (US Award core
  indicators, reached vs. targeted, with reporting-project counts).
- **Cash rows** (code `CASH`): pulled from each project's latest progress-report
  logframe (rows named `(CASH)…`), since OneGMS records cash/voucher assistance on
  fund-specific "standard" indicators that never reach the global indicator extract.
  A "Cash indicators only" toggle restricts both views + the CSV export to these rows.
- **CSV export** and print-to-PDF of the current filtered view.
- Not tied to any AA framework or pipeline — a general CBPF reporting utility
  (`related: standalone`).

## Data

No backend, no database, no build step: `index.html` fetches directly from the
public **OneGMS/CBPF `vo3` OData API** (`cbpfapi.unocha.org/vo3/odata/`) in the
browser on every page load, so figures are exactly what OneGMS publishes at that
moment — there is no mirror or cache to go stale. All endpoints are public,
unauthenticated, and return `Access-Control-Allow-Origin: *` on cross-origin
requests (what makes the browser-only design possible — the header only appears
when an `Origin` is sent, so a plain `curl` won't show it). Freshness is shown in the footer from the API's
`LastModified` field.

This is a **different, undocumented slice of the same underlying OneGMS/CBPF
system** as [`infrastructure/datasets/cbpf-odata.md`](../infrastructure/datasets/cbpf-odata.md)
(vo2, allocation-level, mirrored daily into `aa.cbpf_*` by `ds-cerf-supplement`) —
this app hits `vo3` indicator/reporting endpoints live and bypasses our DB mirror
entirely. `depends_on` is left empty rather than mis-pointing at the vo2 dataset page
(see `extra.schema_strain`).

Countries/funds are hardcoded in the `FUNDS` array in `index.html` (pfid +
`PoolfundCodeAbbrv` per fund, 21 entries as of this sha: Bangladesh, CAR, Chad,
Colombia, DRC, El Salvador, Ethiopia, Guatemala, Haiti, Honduras, Kenya, Lebanon,
Mozambique, Myanmar, Nigeria, South Sudan, Sudan, Syria, Uganda, Ukraine,
Venezuela — the same 21 the US Award covers). Both keys are kept because
regional-envelope children share a `PFAbbrv` (Bangladesh is `AP501`; see the
gotchas on [`cbpf-odata.md`](../infrastructure/datasets/cbpf-odata.md)): the
indicator extract is requested by code, then narrowed by pfid. Adding a country
means adding a row there — no other config.

## Deployment & access

**GitHub Pages**, served from the `main` branch root of `ocha-dap/ds-onegms-public`
(legacy Pages build, no GH Actions workflow, no CI) — confirmed live (`200`) at
<https://ocha-dap.github.io/ds-onegms-public/> per
[`infrastructure/pages-registry.md`](../infrastructure/pages-registry.md), though as
of this ingestion **no KB page declared it as `source_repo`** (that gap is what this
page closes). Public, no auth, no dev/prod split — one static site, one URL. Local
preview via `python3 serve.py` (no-cache server, port 8770) before pushing.

## Maintenance / known issues

- **Deploy = push to `main`.** No build step, no workflow to break — GitHub Pages
  serves the committed `index.html` as-is. `.nojekyll` stops GH Pages' Jekyll
  processing from touching the file.
- **The US Award round is hardcoded**: `US_AWARD_YEAR = 2026` (the `AllocationYears`
  / `AllocationYear` filter on every per-fund request) and `US_AWARD_MARK = "NSFT"`.
  A tranche landing in a later allocation year shows as an empty page until that
  constant is bumped. The global-indicator master is also fetched with a hardcoded
  `PoolfundCodeAbbrv=SUD15` (any fund key returns the same global list, but it breaks
  if the Sudan fund key ever changes).
- **Breaks if OneGMS changes its `vo3` OData shape** (field names, `SPCode` params,
  CORS headers) — there is no server layer to absorb a schema change; a break shows
  up directly as a broken fetch/render in the browser. No automated freshness or
  health check beyond the daily Pages-registry HTTP probe (which only confirms the
  static file serves, not that the live API calls still succeed).
- Known data caveats documented in the README (not bugs): some funds (Sudan,
  Myanmar) don't publish partner names; `cbpfapib` (not used here) would include
  under-approval projects that `cbpfapi` omits; indicator sums are not deduplicated
  beneficiary counts.
