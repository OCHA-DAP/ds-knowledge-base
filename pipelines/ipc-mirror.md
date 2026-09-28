---
content_type: pipeline
visibility: internal
name: ipc-mirror
type: ingest
status: live
surfaces:
  - {url: "https://ocha-dap.github.io/ds-ipc-mirror/", kind: dashboard, title: "IPC/CH mirror explorer (National trends / Areas / P-coded; CSV download)"}
source_repo: OCHA-DAP/ds-ipc-mirror
deployment:
  platform: databricks-job   # + GitHub Pages deploy workflow (no DB access); see note in body
  resource_group: null
  jobs:
    - { name: "IPC Mirror", ref: "databricks.yml:ipc_mirror", schedule: "daily 03:37 UTC (refresh_ipc → export_site → publish_site_data)", status: "pending (ran green on Job Compute from the PR branch 2026-09-25)" }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "daily 07:00 UTC + workflow_dispatch (blob → Pages, no DB)", status: live }
    - { name: "refresh-ipc", ref: ".github/workflows/refresh-ipc.yml", schedule: "daily 03:37 UTC", status: "retired by #2 (still live on main until merged)" }
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
  - "ocha-stratus (DB engine + blob; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_* / DSCI_AZ_BLOB_DEV_SAS(_WRITE): injected on Databricks by the Job Compute policy; the Pages deploy needs only the org Actions secret DSCI_AZ_BLOB_DEV_SAS"
  - "HAPI_APP_IDENTIFIER (dsci secret, added 2026-09-25; --secret in the refresh_ipc task)"
  - "IPC_AUTH (dsci secret, added 2026-09-25; --optional-secret — analyses table skipped gracefully without it)"
  - "PGSSLMODE=require (set by src/storage.py)"
last_verified: 2026-09-25
---

# IPC / Cadre Harmonisé mirror

> **Runs on Databricks since the private-endpoint cutover (PR open [ds-ipc-mirror#2](https://github.com/OCHA-DAP/ds-ipc-mirror/pull/2), 2026-09-25).** The dev DB is reachable only through its private endpoint, so the refresh and the site-data export run as a Databricks job on the shared Job Compute policy (`databricks.yml` + the generic wrapper `databricks/run_task.py`; same UTC schedule, data plane still dev). The GitHub Pages deploy stays on Actions but no longer touches the DB: the job's last tasks run the unchanged `export_site_data.py` and `scripts/site_data_blob.py upload` (dev blob `projects/ds-ipc-mirror/site-data/`, HNS directory markers skipped, stale files removed), and `deploy-site.yml` (`download`) copies the same `site/data/**` down on its old daily backstop cron, so the site output is identical. Extra secrets come from the `dsci` scope at run time via `--secret` (not `spark_env_vars`, whose missing key blocks the cluster launch). Until the PR is merged and `databricks bundle deploy -t prod` has run, the old GitHub Actions crons in `main` are still the live thing; the `deployment:` block in the frontmatter describes the target state.

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

## Downstream consumers

- **seas5-skill Forecast × HNRP tab** (`ds-seas5-skill/pipeline/export_hnrp_drought.py`,
  [live tab](https://ocha-dap.github.io/ds-seas5-skill/#hnrp)) — `ipc.population_admin`
  phase populations as a selectable severity weight beside the JIAF one (phase 3+/4+/5,
  per-country analysis-period picker; p-codes reconciled downstream against the
  consumer's own COD vintage, as in [population-mirror](population-mirror.md)).
  Note the tab's caveat: IPC and JIAF severity do **not** line up — different
  concepts, analysed-population bases, scopes, and periods; compare shapes, not
  values.

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
- Runbook: refresh = Databricks job runs ("IPC Mirror"); the Pages deploy is in the
  Actions tab and `workflow_dispatch`-able. Full-replace
  loads refuse to shrink tables >50% (partial-pull guard).
