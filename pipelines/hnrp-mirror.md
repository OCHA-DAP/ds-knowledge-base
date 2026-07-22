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
  - "HDX per-country *-jiaf-humanitarian-needs-* workbooks (~20 country offices — JIAF intersectoral final severity 1-5, 2025+; localized EN/FR/ES templates)"
outputs:
  - "DB table: hpc.plans (dev — one row per plan: metadata, requirements, FTS funding, plan-level PiN/target/population; PK plan_id; all years 2004+)"
  - "DB table: hpc.plan_caseloads (dev — cluster-level PiN/target/reached/requirements; PK (plan_id, entity_id))"
  - "DB table: hpc.needs_admin (dev — HAPI + Global HNO adm3, admin 0–3 × sector × category × population_status; full replace each refresh, ~950k rows)"
  - "DB table: hpc.severity_admin (dev — JIAF final severity 1–5 per admin area × population group; admin-3 where published (BFA/COD/SYR); full replace, ~8k rows)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-hnrp-mirror/ (Plans + Admin-level PiN tabs, CSV download; site/data/*.json regenerated each deploy)"
dependencies:
  - "ocha-stratus (DB engine; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_HOST / _UID / _PW (read — site export; OCHA-DAP org-level Actions secrets, no per-repo setup)"
  - "DSCI_AZ_DB_DEV_UID_WRITE / _PW_WRITE (write — refresh jobs; org-level secrets)"
  - "HAPI_APP_IDENTIFIER (repo secret; base64 of app-name:email, no registration)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-07-21
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
- **JIAF severity** (`hpc.severity_admin`) — intersectoral **final severity
  (1–5)** per admin area from per-country `*-jiaf-humanitarian-needs-*`
  workbooks, 2025+. Country offices localize the JIAF 2.0 template (EN/FR/ES,
  renamed sheets), so parsing is anchor-based (`src/jiaf.py`); unparseable
  workbooks are logged in the Actions run, never silently dropped (currently:
  UKR ×2, SYR 2026, YEM 2025 publish no severity sheet).

## Gotchas

- Join key is **`plan_id`** (HPC); plan codes/names change between versions.
- HAPI category rows **overlap** (Total / Adult / by-gender…) — filter, never
  sum across categories.
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
