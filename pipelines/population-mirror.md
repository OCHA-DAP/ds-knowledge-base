---
content_type: pipeline
name: population-mirror
type: ingest
status: live
source_repo: OCHA-DAP/ds-population-mirror
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "refresh-pop", ref: ".github/workflows/refresh-pop.yml", schedule: "monthly, 3rd at 04:23 UTC", status: live }
inputs:
  - "HDX HAPI: https://hapi.humdata.org/api/v2/geography-infrastructure/baseline-population (UNFPA COD-PS derived, p-coded admin 0-2; needs HAPI_APP_IDENTIFIER; endpoint moved in HAPI v2 from population-social/population)"
outputs:
  - "DB table: pop.population_admin (dev — total population per admin unit, admin 0-2, totals only (gender=all, age_range=all); ~21k rows, 143 countries; all reference periods kept; full replace with min-row guard)"
dependencies:
  - "ocha-stratus (DB engine; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_* (org-level Actions secrets; _WRITE for refresh)"
  - "HAPI_APP_IDENTIFIER (repo secret; base64 of app-name:email)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-07-26
---

# Population mirror

Mirrors the **HDX HAPI baseline population** (UNFPA COD-PS derived) into the
dev DB (schema `pop`) — the **canonical total-population denominator per
admin unit** for population-share products. Built because the seas5-skill
HNRP tab had to proxy the denominator with `max(IPC analysed, JIAF analysed)`,
which overstates shares badly where IPC coverage is partial (PAK ~21%,
BEN ~21%, YEM ~30%, UGA ~32%, BGD ~59%, TGO ~73%), and other DS work (CERF
predictor, exposure products) kept re-deriving population ad hoc.

One table:

- **`pop.population_admin`** — admin 0–2 with COD p-codes, **totals only**
  (`gender='all'`, `age_range='all'`). HAPI also carries sex/age
  disaggregation but at ~54× the rows (~1M vs ~21k) — deliberately not
  mirrored. All reference periods are kept (population vintages differ by
  country: e.g. PAK 2017 census, KEN 2019 census, MOZ 2025 projection);
  consumers pick the latest per unit.

## Conventions (the part people get wrong)

- **Mirror raw, reconcile downstream.** P-codes are stored exactly as HAPI
  serves them — no rewriting at ingest. Consumers reconcile to their COD
  vintage via the crosswalk pattern in [methods/pcode-matching.md](../methods/pcode-matching.md)
  (ISO3-vs-ISO2 prefix styles like Chad `TCD01` vs `TD01`, zero-padding,
  admin-reform crosswalks).
- Where COD-PS lacks p-codes HAPI ships `*-XXX` placeholder codes with real
  names (all 22 MDG regions are name-only) — usable by name-matching.

## Coverage (audited vs public.polygon prod, 2026-07)

- Adm1 p-codes join ~100% where both sides have real codes; adm2 misses are
  dominated by 30+ countries with **no adm2 in `public.polygon`** (our gap,
  same as the ipc-mirror audit found).
- Countries in `public.polygon` with NO HAPI population at all: ARE, BES,
  BGR, BLR, CHN, COG, DZA, ESH, GMB, GNB, GNQ, KWT, LBN, LBY, MMR, OMN, RUS,
  SYR, UKR, **YEM**. Yemen matters most (partial-IPC country the HNRP tab
  needs); the designed fallback is a phase-2 WorldPop zonal-stats pass over
  our COD polygons (`{iso3}_shp.zip` in the prod `polygon` blob container) —
  not yet built.
- Key partial-IPC countries covered at adm1: PAK (4 units — COD-PS covers
  the 4 main provinces only), BEN 12/12, UGA 4/4, BGD 8/8, TGO 5/5,
  KEN 47/47, MDG 22/22 (name-only), MOZ 11/11, SDN 18/19.
- Run `scripts/pcode_audit.py` in the repo for a current report.

## Gotchas

- **PAK adm1 is mis-p-coded upstream in HAPI** (2026-07): 5 rows with a
  duplicate PK7 and populations shifted one unit against their names (PK2
  "Balochistan" carries KP's 35.5M, PK5 "KP" carries Islamabad's 2.0M —
  verified against the 2017 census). Mirrored raw per doctrine; consumers
  must distrust PAK adm1 until fixed upstream (seas5-skill excludes it and
  also falls back wherever an analysed base exceeds 1.3× the "total" —
  slight excess is normal vintage growth against old-census baselines, more
  means one side is mis-assigned). Worth reporting to the HDX HAPI team.
- **NAM adm1 rows are ~10% of reality** (sum 284k vs 3.0M census 2023) —
  the true constituency-level figures sit in its adm2 rows; aggregate those
  instead for Namibia adm1.

- Reference years vary by country (census vs projection vintages) — always
  report the reference year alongside a share.
- Full-replace loads refuse to shrink the table >50% (partial-pull guard).
- License: COD-PS via HDX is CC-BY (IGO) — credit UNFPA/OCHA on any
  published page.
- Runbook: Actions tab; `workflow_dispatch`-able. Monthly cron (population
  vintages change rarely).
