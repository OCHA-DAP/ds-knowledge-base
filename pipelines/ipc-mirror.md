---
content_type: pipeline
name: ipc-mirror
type: ingest
status: live
source_repo: OCHA-DAP/ds-ipc-mirror
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "refresh-ipc", ref: ".github/workflows/refresh-ipc.yml", schedule: "daily 03:37 UTC", status: live }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "on workflow_run(refresh-ipc) + daily 07:00 UTC backstop", status: live }
inputs:
  - "HDX `ipc` org per-country datasets (*-acute-food-insecurity-country-data): ipc_<iso3>_{national,level1,area}_long.csv — full analysis history, 2017+ where published; no auth"
  - "HDX HAPI: https://hapi.humdata.org/api/v2/food-security-nutrition-poverty/food-security (p-coded admin 0-2, Oct 2020+; needs HAPI_APP_IDENTIFIER)"
  - "IPC API: https://api.ipcinfo.org/analyses?type=A (analysis registry: id/title/link; optional, IPC_AUTH repo secret)"
outputs:
  - "DB table: ipc.population (dev — full-history population-in-phase, national/level1/area NAMES only; ~508k rows, 51 countries, 2017-01+; full replace with min-row guard)"
  - "DB table: ipc.population_admin (dev — HAPI p-coded admin 0-2 rows, Oct 2020+; ~354k rows; full replace with guard)"
  - "DB table: ipc.analyses (dev — IPC API analysis registry, ~544 rows; upsert on analysis_id)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-ipc-mirror/ (National trends / Areas / P-coded tabs, CSV download)"
dependencies:
  - "ocha-stratus (DB engine; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_* (org-level Actions secrets; read for site export, _WRITE for refresh)"
  - "HAPI_APP_IDENTIFIER (repo secret; base64 of app-name:email)"
  - "IPC_AUTH (repo secret; free per-user IPC API key — analyses table skipped gracefully without it)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-07-24
---

# IPC / Cadre Harmonisé mirror

Mirrors the **IPC/CH acute food insecurity consensus classifications** into the
dev DB (schema `ipc`) and publishes a
[GitHub Pages explorer](https://ocha-dap.github.io/ds-ipc-mirror/).

Three tables, deliberately split by source:

- **`ipc.population`** (per-country HDX datasets) — the deepest public record of
  the consensus product: full analysis history, 2017+ where published, 51
  countries incl. all Cadre Harmonisé. National / level-1 / area rows with
  **names only — no p-codes exist at this level anywhere public**.
- **`ipc.population_admin`** (HDX HAPI food-security) — the **p-coded layer**:
  admin 0–2 with COD p-codes, but **Oct 2020+ only**. HAPI's p-coding is
  name-based and falls back to a higher admin level where matching fails.
- **`ipc.analyses`** (IPC API) — analysis registry (id, title, ipcinfo link),
  loosely joinable on (country, analysis month).

## Keying (the part people get wrong)

Every population row carries BOTH the **analysis round** (`analysis_date`) and
the **reference (validity) period** (`period_type` current / first projection /
second projection × `reference_period_start/end`). Rounds overlap in time — a
newer round's *current* covers the same months as an older round's
*projection* — so a time series must pick one period type AND handle
re-analysis, never just sort by date.

## Gotchas

- **HAPI ships some rows verbatim twice** in `population_admin` (same resource
  file, same value — COD 450 duplicated keys, CAF 204, SSD 138 as of 2026-07):
  `drop_duplicates` before any pivot/sum or those phase populations double.
- Phase rows overlap: `all` = analyzed population; `3+` duplicates 3/4/5 —
  filter, never sum across phase rows. `fraction` is of *analyzed* population,
  which can be well below the country total.
- The HDX **global** dataset and HAPI only reach Oct 2020 — the per-country
  datasets are why the mirror has 2017+ (SOM has 25 rounds from Jan 2017).
- Dead upstream series (not a pipeline bug): ETH stops 2021, BFA stalled
  2024-06 (CH data-sharing), AGO/SLV/ZWE/ZAF historical only.
- P-code audit vs `public.polygon` prod (2026-07): adm1 joins ~100% (minus
  intentional `*-XXX` placeholders); adm2 joins ~95-100% **where our reference
  has adm2** — 20+ HAPI countries (GHA, ZMB, PAK, BEN, SEN…) have NO adm2 in
  `public.polygon`, a coverage gap on OUR side. Chad is `TCD*` in HAPI vs `TD*`
  in polygon. Real divergences concentrate in admin-reform countries
  (BFA/MLI/MOZ/CAF/ETH/COD). Deep-history area names join a HAPI-p-coded name
  ~82% overall (worst: ZWE 0%, GMB 0%, ETH 19%, LBN 22%, AFG 37%).
- **IPC ≠ FEWS NET**: FEWS NET's IPC-compatible classifications (FDW API,
  2011+) are a different product and deliberately NOT mirrored here.
- License: CC BY-NC-SA 3.0 IGO — attribute "IPC CC BY-NC-SA 3.0 IGO", link
  cadreharmonise.org for CH.
- Runbook: Actions tab; both workflows `workflow_dispatch`-able. Full-replace
  loads refuse to shrink tables >50% (partial-pull guard).
