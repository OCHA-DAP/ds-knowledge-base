---
content_type: pipeline
visibility: internal
name: ipc-mirror
type: dataset-ingest
status: live
surfaces:
  - {url: "https://ocha-dap.github.io/ds-ipc-mirror/", kind: dashboard, title: "IPC/CH mirror explorer (National trends / Areas / P-coded; CSV download)"}
source_repo: OCHA-DAP/ds-ipc-mirror
deployment:
  platform: databricks-job   # + GitHub Pages deploy workflow (no DB access); see note in body
  resource_group: null
  jobs:
    - { name: "IPC Mirror", ref: "databricks.yml:ipc_mirror", schedule: "daily 03:37 UTC (refresh_ipc → export_site → publish_site_data)", status: live }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "daily 07:00 UTC + workflow_dispatch (blob → Pages, no DB)", status: live }
    - { name: "refresh-ipc", ref: ".github/workflows/refresh-ipc.yml", schedule: "daily 03:37 UTC", status: "retired by #2 (removed from main 2026-09-25)" }
inputs:
  - "IPC API: https://api.ipcinfo.org/population?type=A&start=Y&end=Y, one call per year since 2017 (population in phase at national / level-1 / area level; needs IPC_AUTH). A call without a year range returns 2021 onward only, see Gotchas"
  - "IPC API: https://api.ipcinfo.org/analyses?type=A (analysis registry: id/title/link; IPC_AUTH)"
  - "HDX HAPI: https://hapi.humdata.org/api/v2/food-security-nutrition-poverty/food-security (p-coded admin 0-2, Oct 2020+; needs HAPI_APP_IDENTIFIER)"
  - "Fallback only (no IPC_AUTH, or the API gives nothing): HDX `ipc` org per-country datasets, ipc_<iso3>_{national,level1,area}_long.csv — 2021 onward; no auth"
outputs:
  - "DB table: ipc.population (dev — population-in-phase, national/level1/area NAMES only; ~540k rows, 52 countries, every acute analysis since 2017-01 as of 2026-10-12; a load replaces the rounds its pull holds and keeps every other stored round)"
  - "DB table: ipc.population_admin (dev — HAPI p-coded admin 0-2 rows, Oct 2020+; ~361k rows; same load: periods the pull does not hold are kept)"
  - "DB table: ipc.analyses (dev — IPC API analysis registry, ~620 rows, 2012+; upsert on analysis_id)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-ipc-mirror/ (National trends / Areas / P-coded tabs, CSV download)"
dependencies:
  - "ocha-stratus (DB engine + blob; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_* / DSCI_AZ_BLOB_DEV_SAS(_WRITE): injected on Databricks by the Job Compute policy; the Pages deploy needs only the org Actions secret DSCI_AZ_BLOB_DEV_SAS"
  - "HAPI_APP_IDENTIFIER (dsci secret, added 2026-09-25; --secret in the refresh_ipc task)"
  - "IPC_AUTH (dsci secret, added 2026-09-25; passed as --optional-secret, but since 2026-10-12 it is what brings the population history: without it the refresh reads HDX (2021 onward) and ends with an error)"
  - "PGSSLMODE=require (set by src/storage.py)"
last_verified: 2026-10-12
---

# IPC / Cadre Harmonisé mirror

> **Runs on Databricks since the private-endpoint cutover (merged [ds-ipc-mirror#2](https://github.com/OCHA-DAP/ds-ipc-mirror/pull/2) 2026-09-25, deployed and first run 2026-09-28).** The dev DB is reachable only through its private endpoint, so the refresh and the site-data export run as a Databricks job on the shared Job Compute policy (`databricks.yml` + the generic wrapper `databricks/run_task.py`; same UTC schedule, data plane still dev). The GitHub Pages deploy stays on Actions but no longer touches the DB: the job's last tasks run the unchanged `export_site_data.py` and `scripts/site_data_blob.py upload` (dev blob `projects/ds-ipc-mirror/site-data/`, HNS directory markers skipped, stale files removed), and `deploy-site.yml` (`download`) copies the same `site/data/**` down on its old daily backstop cron, so the site output is identical. Extra secrets come from the `dsci` scope at run time via `--secret` (not `spark_env_vars`, whose missing key blocks the cluster launch). The old GitHub Actions refresh cron was removed from `main` with the merge; since 2026-09-30 GitHub Actions has no route to the databases at all.

Mirrors the **IPC/CH acute food insecurity consensus classifications** into the
dev DB (schema `ipc`) and publishes a
[GitHub Pages explorer](https://ocha-dap.github.io/ds-ipc-mirror/).

Three tables, deliberately split by source:

- **`ipc.population`** (IPC API, asked year by year) — the deepest record of the
  consensus product: every acute analysis since January 2017, 52 countries incl.
  all Cadre Harmonisé, 545 analyses at national level. National / level-1 / area
  rows with **names only — no p-codes exist at this level anywhere public**.
  `source_dataset` is `ipc-api` (or an HDX dataset name on a fallback day).
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

- **Ask the IPC API for each year; a call without a year range returns 2021 onward
  only (seen 2026-10).** `hdx-scraper-ipc`, which builds the per-country datasets on
  HDX, calls `/population` without one, so each HDX file lost its analyses before 2021
  the next time it was rebuilt (Angola and El Salvador were left with `*_latest.csv`
  files only; Zimbabwe's archived dataset kept 2019–2021). This mirror was loaded from
  those files with a full replace, so it lost them too: by 2026-10-09 `ipc.population`
  had nothing before 2021 except Zimbabwe (national 7,042 rows / 51 countries in the
  site export of 2026-07-24, 5,642 / 49 on 2026-10-09). It went a few countries at a
  time, which the 50% shrink guard could not catch, so nothing alerted. Some countries
  (CAF, HND, MDG, UGA, YEM, DJI, ZAF) had already been cut when the mirror was first
  built in July. Asked with `start=Y&end=Y`, the API still serves everything.
  **Fixed 2026-10-12** ([ds-ipc-mirror#4](https://github.com/OCHA-DAP/ds-ipc-mirror/pull/4)):
  the mirror reads the API itself, one call per year since 2017, and got back all 283
  lost (country, level, analysis) rounds plus 91 it had never held; rows built from
  the API matched the 431,011 HDX-fed rows exactly (key, number, share, country total).
  Whether the API's 2021 floor is fixed or moves each year is unknown; it no longer
  matters here. The HDX datasets themselves are still cut (the scraper would need to
  pass a start year). The API also serves 62 analyses of 2012–2014 that are not
  mirrored (`IPC_HISTORY_START=2012` would add them).
- **Loads never delete a round their pull does not hold.** A pull replaces the rows of
  the rounds it brings — `(iso3, level, analysis_date)` in `ipc.population`,
  `(location_code, ipc_type, reference period)` in `ipc.population_admin` — and leaves
  every other stored round untouched, so a source that stops serving old analyses can
  no longer empty the mirror. Consequences to know: `refreshed_at` is the last time a
  row was read from its source, and differs between rows; a round IPC withdraws or
  re-dates stays as last read until someone deletes it by hand (recipe in the repo's
  `CLAUDE.md`); the run logs such rounds once, on the day they drop out.
- **A refresh that was not a full one ends with an error after loading what it
  could**: a year the API did not answer, a year with stored analyses that came back
  empty, no `IPC_AUTH` (HDX fallback), or a table that refused its pull (empty, or
  fewer than half the stored rounds). Nothing stored is lost in those cases; a failed
  "IPC Mirror" run is the signal to look. Until the bundle is redeployed with
  `run_if: ALL_DONE` on `export_site`, such a day also skips the site export.
- The site export of 2026-07-24 (the last copy made before most of the history went)
  is kept on the dev blob under `projects/ds-ipc-mirror/archive/export-2026-07-24/`.
  It is a record, not a source: the API's current version differs in a few places
  (South Sudan May 2019 and Sudan October 2023 no longer carry a "first projection";
  nine zero totals of DR Congo June 2019 are now filled).
- **HAPI ships some rows verbatim twice** in `population_admin` (same resource
  file, same value — COD 450 duplicated keys, CAF 204, SSD 138 as of 2026-07):
  `drop_duplicates` before any pivot/sum or those phase populations double.
- Phase rows overlap: `all` = analyzed population; `3+` duplicates 3/4/5 —
  filter, never sum across phase rows. `fraction` is of *analyzed* population,
  which can be well below the country total.
- The HDX **global** dataset and HAPI only reach Oct 2020, and the per-country HDX
  datasets now start in January 2021 — see the first gotcha. For anything older,
  read `ipc.population`.
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
  Actions tab and `workflow_dispatch`-able. A run that ends with an error names what
  was incomplete in its last lines; what was stored is kept either way. The load is
  tested against a scratch schema on dev (`IPC_TEST_DB=1 uv run pytest`).
