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
outputs:
  - "DB table: hnrp.plans (dev — one row per plan: metadata, requirements, FTS funding, plan-level PiN/target/population; PK plan_id; all years 2004+)"
  - "DB table: hnrp.plan_caseloads (dev — cluster-level PiN/target/reached/requirements; PK (plan_id, entity_id))"
  - "DB table: hnrp.needs_admin (dev — HAPI mirror, admin 0–2 × sector × category × population_status; full replace each refresh, ~900k rows)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-hnrp-mirror/ (Plans + Admin-level PiN tabs, CSV download; site/data/*.json regenerated each deploy)"
dependencies:
  - "ocha-stratus (DB engine; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_HOST / _UID / _PW (read — site export)"
  - "DSCI_AZ_DB_DEV_UID_WRITE / _PW_WRITE (write — refresh jobs)"
  - "HAPI_APP_IDENTIFIER (base64 of app-name:email, no registration)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-07-21
---

# HNRP / PiN mirror

Mirrors OCHA **HNRP/HRP plan data and People in Need** figures into the dev DB
(schema `hnrp`) and publishes a
[GitHub Pages explorer](https://ocha-dap.github.io/ds-hnrp-mirror/).

Two granularity tiers, deliberately split by source:

- **HPC API + FTS** — plan- and cluster-level (PiN, targeted, reached,
  requirements, funding) for **all plan years** (plans 2004+, caseloads ~2017+).
  Daily refresh covers current/previous/next plan years (funding moves
  continuously); the Sunday run re-walks all years.
- **HDX HAPI** (`affected-people/humanitarian-needs`, the Global HNO dataset) —
  the most granular *standardized* public PiN: **admin-2** × sector × age/gender
  category × population status, 2024+ for ~24 HNRP countries. Full-replace
  mirror with a row-count guard (refuses to wipe on a partial pull).

## Gotchas

- Join key is **`plan_id`** (HPC); plan codes/names change between versions.
- HAPI category rows **overlap** (Total / Adult / by-gender…) — filter, never
  sum across categories.
- The HPC API also exposes raw per-plan disaggregation matrices (admin-level,
  plan-specific categories, ~8 MB per caseload attachment) — **not mirrored**;
  candidate for historical admin-level PiN if ever needed.
- Runbook: failures are visible in the repo's Actions tab; both workflows are
  `workflow_dispatch`-able, and `refresh-hnrp` takes an `all_years` input for
  on-demand backfills.
