---
content_type: pipeline
name: hnrp-mirror
type: ingest
status: live
source_repo: OCHA-DAP/ds-hnrp-mirror
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "refresh-hnrp", ref: ".github/workflows/refresh-hnrp.yml", schedule: "daily 04:17 UTC (recent years) + Sun 02:47 UTC (full backfill)", status: live }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "on workflow_run(refresh-hnrp) + daily 08:00 UTC backstop", status: live }
inputs:
  - "HPC API: https://api.hpc.tools /v2/public/plan?year=Y + /v1/public/plan/id/{id}?content=measurements (plan metadata, plan/cluster caseloads, requirements; no auth)"
  - "FTS: https://api.hpc.tools/v1/public/fts/flow?planid={id}&groupby=plan (funding totals per plan)"
  - "HDX HAPI: https://hapi.humdata.org/api/v2/affected-people/humanitarian-needs (PiN to admin-2 by sector/category/status, Global HNO, 2024+; needs HAPI_APP_IDENTIFIER)"
  - "HDX global-hpc-hno CSVs (admin-3 PiN rows HAPI truncates: BFA/COD/MMR)"
  - "HDX per-country *-jiaf-humanitarian-needs-* workbooks (~20 country offices — JIAF intersectoral final severity 1-5 AND overall PiN (WS-3.1), 2025+; localized EN/FR/ES templates; newest resource per country-year wins)"
outputs:
  - "DB table: hpc.plans (dev — one row per plan: metadata, requirements, FTS funding, plan-level PiN/target/population; PK plan_id; all years 2004+)"
  - "DB table: hpc.plan_caseloads (dev — cluster-level PiN/target/reached/requirements; PK (plan_id, entity_id))"
  - "DB table: hpc.needs_admin (dev — HAPI + Global HNO adm3, admin 0–3 × sector × category × population_status; full replace each refresh, ~950k rows)"
  - "DB table: hpc.severity_admin (dev — JIAF final severity 1–5 per admin area × population group; admin-3 where published (BFA/COD/SYR); full replace, ~8k rows)"
  - "DB table: hpc.pin_admin (dev — JIAF overall PiN, preliminary + final, per admin area × population group; 2026 rows carry own final severity → PiN-by-severity distribution; full replace, ~11k rows, 37 country-years)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-hnrp-mirror/ (Plans / Admin-level PiN / Severity / PiN × severity tabs, CSV download; site/data/*.json regenerated each deploy)"
dependencies:
  - "ocha-stratus (DB engine; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_HOST / _UID / _PW (read — site export; OCHA-DAP org-level Actions secrets, no per-repo setup)"
  - "DSCI_AZ_DB_DEV_UID_WRITE / _PW_WRITE (write — refresh jobs; org-level secrets)"
  - "HAPI_APP_IDENTIFIER (repo secret; base64 of app-name:email, no registration)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-07-28
---

# HNRP / PiN mirror

Mirrors OCHA **HNRP/HRP plan data and People in Need** figures into the dev DB
(schema `hpc`) and publishes a
[GitHub Pages explorer](https://ocha-dap.github.io/ds-hnrp-mirror/).

Two granularity tiers, deliberately split by source:

- **HPC API + FTS** — plan- and cluster-level (PiN, targeted, reached,
  requirements, funding) for **all plan years** (plans 2004+, caseloads ~2017+).
  Daily refresh covers current/previous/next plan years (funding moves
  continuously); the Sunday run re-walks all years.
- **HDX HAPI** (`affected-people/humanitarian-needs`, the Global HNO dataset) —
  the most granular *standardized* public PiN: **admin-2** × sector × age/gender
  category × population status, 2024+ for ~24 HNRP countries. Full-replace
  mirror with a row-count guard (refuses to wipe on a partial pull). Supplemented
  with **admin-3** rows from the `global-hpc-hno` CSVs (BFA/COD/MMR) that HAPI
  truncates — the CSVs lag HAPI within the current cycle, so HAPI stays primary.
- **JIAF severity + overall PiN** (`hpc.severity_admin`, `hpc.pin_admin`) —
  from per-country `*-jiaf-humanitarian-needs-*` workbooks, 2025+:
  intersectoral **final severity (1–5)** (WS-3.2 / "Severity" sheet) and
  intersectoral **overall PiN, preliminary + final** (WS-3.1 / "PiN" sheet),
  both per admin area × population group. Country offices localize the JIAF
  2.0 template (EN/FR/ES, renamed sheets), so parsing is anchor-based
  (`src/jiaf.py`); unparseable workbooks are logged in the Actions run, never
  silently dropped (currently: UKR ×2, SYR 2026, YEM 2025 publish no severity
  sheet; only UKR 2026 publishes no admin-level PiN — macro-zones only). Per
  country-year the **newest HDX resource wins**, so revised re-uploads
  ("[Revised] DRC ... 2026") supersede the original for both tables.
  **Admin depth**: admin-2 for most countries; admin-3 for COD (zones de
  santé), SYR (sub-districts) and BFA 2025 (communes; BFA 2026 dropped back
  to admin-2). No workbook publishes admin-4.

## Gotchas

- Join key is **`plan_id`** (HPC); plan codes/names change between versions.
- HAPI category rows **overlap** (Total / Adult / by-gender…) — filter, never
  sum across categories: `category='total'` exactly (231 other values are
  sex/age/group breakdowns of the same people).
- **JIAF classifies AREAS, it does not count people per class.** Every finest
  unit (× population group) in `hpc.severity_admin` carries exactly ONE
  `final_severity` and that unit's population (verified across all 8,108 units,
  2026-07). Any "population in severity N" figure derived from this table is
  really *the population of areas classified N* — label it that way. Per-class
  headcounts do not exist in this table; for **PiN by severity class** use
  `hpc.pin_admin` (final PiN grouped by the unit's severity — still
  area-classified, but PiN headcounts rather than area populations). PiN
  (`needs_admin`, `INN`) remains the plan's authoritative people-level caseload
  and is NOT derivable from severity.
- **How PiN is calculated (JIAF 2.0 "Mosaic Method")**: each sector estimates
  its own PiN per finest analysis unit; intersectoral PiN takes the *highest*
  sectoral PiN per unit and sums those maxima upward, then validation workshops
  resolve flags by consensus. Consequences: (a) intersectoral < sum(sectors)
  always — never sum sector PiNs; (b) sectoral arithmetic won't reproduce the
  intersectoral exactly (TCD 2025: 73% of admin-2 units equal max(sector); SDN 0%
  equal but 98% ≥ — the mosaic ran at a finer unit); (c) from HPC 2026 overall
  PiN counts only areas in intersectoral severity 3+ (2025-cycle PiN can include
  class-1/2 areas).
- **PiN-by-severity is now mirrored** (`hpc.pin_admin`, added 2026-07-28). The
  2025 Humanitarian Reset reintroduced "the distribution of PiN by severity
  level"; in the **published** workbooks this lives in WS-3.1 as a final PiN +
  final severity per analysis unit — 2026-cycle rows carry both, so
  `final_pin` grouped by `severity` is the distribution, with no
  sector-collapse choice needed. 2025 rows have `severity` NULL: join
  `severity_admin` on (iso3, year, admin codes, population_group) — verified
  100% of final PiN joins wherever severity is published. NOTE the sector ×
  severity "PiN par gravité" sheet the CAR analysis used
  (analysis/jiaf-pbs-analysis) is **not in any HDX-published workbook** — that
  was an internal workbook hand-uploaded to blob; per-sector distributions
  (and the six-method collapse question) only return if such sheets ever get
  published.
- **`pin_admin` quirks** (mirrored as-is from the sheets): SSD 2026 fills a
  constant severity 4 on every PiN row while its severity sheet has a real
  3/4/5 spread — sanity-check degenerate distributions against
  `severity_admin`; NGA 2025 publishes preliminary PiN only (final column
  empty); national sums can differ from `hpc.plans.in_need` (workbook vs
  HPC-reconciled figures; some workbooks track refugees in a separate column).
- **One sector_code, several named series.** Within a single reference period a
  sector code can carry multiple `sector_name` series ("Protection (total)" AND
  "General Protection", both `PRO`, both `category='total'`) — summing across
  them double-counts (MMR PRO 2024 sums to 2.18× its published admin-1 total).
  Names also mutate BETWEEN cycles (COD: "Final HRP Caseload" 2024 vs "…caseload"
  2025) — pick one series per (country, sector, reference period), never
  globally.
- **Prefer the coarsest published admin level.** Where a country publishes the
  same series at admin-1 and finer, the admin-1 figures equal the finer sums
  (ratio 1.000) except where the finer level double-counts — aggregate the
  coarsest level at/below your target, never mix.
- **`*-XXX` placeholder sub-codes can carry a WRONG parent admin-1** upstream
  (MOZ 2024: Nampula districts filed under Sofala, Zambézia under Cidade de
  Maputo — a systematic shift). The names are good — re-attribute by unique COD
  name match before any rollup (see `export_hnrp_drought.py::sub_parent`).
- **Coverage boundaries**: the HPC mirror includes every plan type (HNRPs,
  **flash appeals**, RRPs, other) at plan/cluster level, all years. HAPI's
  admin-level PiN covers only Global-HNO countries (~24 HNRPs, 2024+) — flash
  appeals (e.g. OPT) and RRPs have no standardized admin-level PiN anywhere
  public. Historical (pre-2024) admin-level PiN exists only as heterogeneous
  per-country `*_hpc_needs_<year>.xlsx` on HDX (`ocha-hpc-tools` org, some back
  to 2015) or raw HPC disaggregation matrices (~8 MB/attachment) — bespoke
  parsing, not mirrored.
- **If HAPI is ever discontinued**: the same data ships as flat CSVs on HDX
  (`hdx-hapi-humanitarian-needs`, `global-hpc-hno`, per-country
  `*_hpc_needs_api_<year>.csv`) — swap `src/hapi.py` to those, schema unchanged.
  (Checked 2026-07: HAPI actively maintained, no public sunset plan.)
- Runbook: failures are visible in the repo's Actions tab; both workflows are
  `workflow_dispatch`-able, and `refresh-hnrp` takes an `all_years` input for
  on-demand backfills.
