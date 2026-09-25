---
content_type: pipeline
name: nga-flooding-monitoring
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "NGA Riverine Flood Monitoring", ref: "dbx:755265061277015 (bundle resource nga_riverine_monitoring, databricks.yml)", schedule: "quartz 0 0 20 * * ? UTC (daily 20:00 UTC)", status: live }
    - { name: "NGA Flash Flood Monitoring", ref: "dbx:351228559024609 (bundle resource nga_flash_monitoring, databricks.yml)", schedule: "quartz 0 30 1 * * ? UTC (daily 01:30 UTC)", status: live }
    - { name: "deploy-app-cron (GH Pages publish shim)", ref: ".github/workflows/deploy-app-cron.yml", schedule: "0 2 * * * + 45 20 * * * (UTC, ~30-45 min after each monitoring run) + workflow_dispatch", status: live }
    - { name: "Monitor flooding (riverine, GHA manual fallback)", ref: ".github/workflows/monitoring.yml", schedule: "workflow_dispatch only (cron removed 2026-09-24, main@73bd934)", status: live }
    - { name: "Monitor flash flooding (GHA manual fallback)", ref: ".github/workflows/flash-monitoring.yml", schedule: "workflow_dispatch only (cron removed 2026-09-24, main@73bd934)", status: live }
inputs:
  - "CDS/EWDS cems-glofas-forecast (operational ensemble, Wuroboki point, leads 1-12 d)"
  - "CDS/EWDS cems-glofas-historical (version_4_0 intermediate reanalysis, Wuroboki point, walk-back -2..-7 d)"
  - "Google Flood Forecasting API gauges:queryGaugeForecasts (10 endorsed GRRR gauges, one call)"
  - "DB app.floodscan_exposure prod (per-LGA FloodScan x WorldPop exposure, from floodexposure-monitoring)"
outputs:
  - "DB projects.ds_aa_nga_flooding_monitoring dev (riverine forecasts; unique key monitoring_date/valid_date/src) — data plane hardcoded dev on main@73bd934 even under the bundle's prod target; prod cutover pending on branch ops/prod-cutover"
  - "blob projects/ds-aa-nga-flooding/monitoring/{date}_{action}.png + flash_{date}_{triggered}.png (HDX-styled charts, dev)"
  - "blob projects/ds-aa-nga-flooding/monitoring/status/{status.json,riverine_latest.png,flash_latest.png} (dev) — status-page handoff written by the Databricks export_status tasks"
  - "Listmonk campaigns: riverine lists nga:info / nga:trigger / nga:test; flash lists nga-flash:info / nga-flash:trigger / nga-flash:test (list ids are resolved by TAG at runtime, never hardcoded)"
  - "orphan branch `monitoring-status` (legacy): exploration/2026/cerf/monitoring/status.json + PNGs — now written only if a GHA fallback workflow is dispatched manually; blob wins over it at publish time"
dependencies:
  - "ocha-relay v0.3.0 (Listmonk client)"
  - "ocha-stratus, cfgrib, eccodes (GRIB decoding for GloFAS) — Databricks cluster pins eccodes==2.42.0 + cfgrib==0.9.14.0; requirements.txt (GHA fallback) pins eccodes==2.47.0"
  - "Databricks: Job Compute policy 000C79D951EAF0D6 injects DSCI_AZ_DB_*/DSCI_AZ_BLOB_* (dev+prod) + CDSAPI_KEY from the `dsci` secret scope; DSCI_LISTMONK_BASE_URL/API_USERNAME/API_KEY via spark_env_vars from `dsci`; GOOGLE_API_KEY resolved at run time by run_task.py --secret (tolerated if missing); CDSAPI_URL overridden to EWDS"
  - "GHA fallback secrets: DSCI_AZ_BLOB_DEV_SAS(+_WRITE), DSCI_AZ_DB_DEV_*(riverine) / DSCI_AZ_DB_PROD_*(flash read), GOOGLE_API_KEY, CDSAPI_KEY/URL, DSCI_LISTMONK_API_URL->BASE_URL, DSCI_LISTMONK_API_USERNAME/KEY (send-scoped); DSCI_LISTMONK_ADMIN_API_USERNAME/KEY only for the one-off setup script"
  - "STAGE (prod = real lists; anything else = test lists + [TEST] banner) — set by the bundle `stage` variable (prod target = prod) via run_task.py --stage; the GHA fallbacks take a `stage` dispatch input"
  - "upstream: floodexposure-monitoring chain must land the day's exposure before 01:30 UTC (flash has a freshness guard)"
downstream:
  - "Email recipients on the Listmonk lists (per the 2026-08-11 sync: a two-person soak audience per stream, pending distribution-list migration — Listmonk-internal, not publicly verifiable)"
  - "Public GH Pages status page at https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/ — index.html from main + status.json/PNGs from blob (fallback: monitoring-status branch), assembled by deploy-app-cron.yml (verified HTTP 200, 2026-09-25)"
depends_on: [floodexposure-monitoring, listmonk, dbx-job-compute]
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/", kind: status, title: "Nigeria flood monitoring public status page (status.json + PNGs from blob)"}
  - {url: "https://ocha-dap.github.io/ds-aa-nga-flooding/", kind: landing, title: "Nigeria flooding — anticipatory action (site landing page)"}
source_repo: ocha-dap/ds-aa-nga-flooding
source_branch: main
source_sha: 73bd934
code_ref:
  - databricks.yml
  - databricks/run_task.py
  - .github/workflows/monitoring.yml
  - .github/workflows/flash-monitoring.yml
  - .github/workflows/deploy-app-cron.yml
  - pipelines/check_forecasts.py
  - pipelines/save_plots.py
  - pipelines/send_emails.py
  - pipelines/monitor_flash_flood.py
  - pipelines/setup_nga_listmonk_lists.py
  - pipelines/export_monitoring_status.py
  - src/monitoring/etl.py
  - src/monitoring/flash.py
  - src/monitoring/plot.py
  - src/constants.py
  - exploration/2026/cerf/monitoring/index.html
extra: {
  framework: "frameworks/nga-flooding/2026-06-18.md — trigger definitions and provenance live there; this page is the ops runbook",
  email_cadence: "weekly Monday informational per stream; immediate on trigger (both streams) and on flash approaching-threshold (>=80% of any LGA threshold) — send_emails.py / monitor_flash_flood.py unchanged between c812dad and 73bd934",
  migration: "2026-09-24 (PR #47, merged as main@73bd934): both monitors moved from GHA crons to a Databricks Asset Bundle because GitHub runners are losing network access to the Postgres DB. GHA workflows kept as workflow_dispatch-only fallbacks. Status-page handoff moved from git push (monitoring-status branch) to blob (STATUS_BLOB_PREFIX=ds-aa-nga-flooding/monitoring/status), since a Databricks job cannot push the branch. Branch ops/prod-cutover (9dda278 'Bundle: prod data plane + SES switches') is stacked on top and not yet merged.",
  data_branch: "monitoring-status (tip 216dd8c, 2026-09-25T00:20Z riverine update) is an orphan data-only branch — no code. Since the migration it is legacy: only a manually dispatched GHA fallback writes it, and deploy-app-cron.yml overlays blob on top of it.",
  related_branch: "feat/niger-benue-multistate-monitoring holds the Niger/Benue multistate static app served at https://ocha-dap.github.io/ds-aa-nga-flooding/app/ — not reconciled with the two-job monitoring on this page. Its own deploy-app.yml cron never fires (GitHub only honours schedules on the default branch); deploy-app-cron.yml on main is the shim that deploys it and overlays this pipeline's status page."
}
visibility: internal
last_synced: "2026-09-25"
---

# Nigeria Flooding Monitoring (2026 framework)

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am." Trigger design and provenance: [frameworks/nga-flooding/2026-06-18](../frameworks/nga-flooding/2026-06-18.md). The repo's own `CLAUDE.md` / `README.md` at `main` is the code-adjacent runbook — this page is the hub summary + cross-repo context.

## One-liner

*Two daily Databricks jobs evaluate the 2026 Nigeria AA triggers — Adamawa riverine (GloFAS readiness + 10-gauge Google action), BAY-states flash flood (FloodScan exposure vs per-LGA thresholds) — email HDX-styled status updates via Listmonk, and write a machine-readable status snapshot to blob, which a GHA cron publishes as a public GH Pages status page. Moved from GitHub Actions to Databricks on 2026-09-24.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| NGA Riverine Flood Monitoring | `dbx:755265061277015` (`nga_riverine_monitoring` in `databricks.yml`) | quartz `0 0 20 * * ?` UTC | live — deployed 2026-09-24; registry showed `NO-RUNS` at its 2026-09-25 07:01 UTC snapshot, which is expected (first scheduled prod run is 2026-09-25 20:00 UTC) |
| NGA Flash Flood Monitoring | `dbx:351228559024609` (`nga_flash_monitoring`) | quartz `0 30 1 * * ?` UTC | live — 🟢 in the registry, last success ~01:30 UTC 2026-09-25 |
| deploy-app-cron (GH Pages publish) | `.github/workflows/deploy-app-cron.yml` | crons `0 2 * * *` + `45 20 * * *` | live |
| Monitor flooding (riverine) — fallback | `.github/workflows/monitoring.yml` | `workflow_dispatch` only | manual fallback; cron removed at `73bd934` |
| Monitor flash flooding — fallback | `.github/workflows/flash-monitoring.yml` | `workflow_dispatch` only | manual fallback; cron removed at `73bd934` |

**Databricks bundle** (`databricks.yml`, PR #47, 2026-09-24). Both jobs run from `source: GIT` on `main` (code changes ship by pushing; `bundle deploy` is only needed for job-config changes), on an ephemeral single-worker cluster under the Job Compute policy, `max_concurrent_runs: 1`, with an `on_failure` email to the job owner. Tasks:

- riverine: `check_forecasts` → `save_plots` → `send_emails` → `export_status`
- flash: `monitor_flash` → `export_status`

Every task goes through `databricks/run_task.py`, which sets `STAGE` (from the `stage` job parameter), `MONITORING_DATE` (empty = today) and other `--env` extras, copies `src/` + `pipelines/` off the workspace FUSE mount onto local disk (importing off wsfs is flaky), and shells out to the unchanged pipeline script. Two dev/prod axes per [databricks.md](../infrastructure/databricks.md): the **target** (`dev` = paused, `[dev <user>]`-prefixed; `prod` = live schedule, `run_as` the owner's admin account pending a service principal) and the **`stage` variable** (`prod` target sets `stage: prod`). On `main`, `stage` switches only live-vs-test **emailing** — the riverine data plane stays hardcoded dev (see Gotchas). That's why the registry reports `data-mode: prod` even though the riverine table is still dev.

```shell
databricks bundle validate -t dev  -p DEFAULT
databricks bundle deploy   -t dev  -p DEFAULT --var git_branch=my-branch   # feature test (paused)
databricks bundle run nga_riverine_monitoring -t dev -p DEFAULT
databricks bundle deploy   -t prod -p DEFAULT                              # the live jobs
```

The flash cron is timed after the `floodexposure-monitoring` chain (23:15 UTC + ~40 min DB write). The GHA fallbacks take optional `date` and `stage` (default `dev`) dispatch inputs.

`deploy-app-cron.yml` is a **deliberate pre-merge shim** (its header says to delete it once `feat/niger-benue-multistate-monitoring` merges): GitHub only honours `schedule:` on the default branch, so this file on `main` checks out the feature branch, runs its deploy steps, overlays `index.html` from `main`, then the `monitoring-status` branch data, then **the blob status files (blob wins)**, and publishes the whole thing to GH Pages.

## Inputs

- GloFAS operational forecast (ensemble perturbed, leads 1–12 d) at Wuroboki, `cems-glofas-forecast` (served from EWDS; the Databricks wrapper overrides the policy's plain-CDS `CDSAPI_URL`).
- GloFAS `version_4_0` intermediate reanalysis, walk-back −2..−7 d, `cems-glofas-historical`.
- 10 endorsed GRRR gauges via one Google Flood Forecasting API call (`gauges:queryGaugeForecasts`).
- `app.floodscan_exposure` (prod DB) — per-LGA FloodScan × WorldPop exposure, written by [floodexposure-monitoring](floodexposure-monitoring.md); flash's sole data source.

## Steps

**Riverine** (`check_forecasts.py` → `save_plots.py` → `send_emails.py` → `export_monitoring_status.py riverine`):

1. Download GloFAS operational forecast (leads 1–12 d) at Wuroboki; walk back −2..−7 d for the latest available `version_4_0` intermediate reanalysis (missing reanalysis = warning, never fatal). Fetch all 10 GRRR gauges in one Google API call (latest issuance per gauge kept). Upsert to `projects.ds_aa_nga_flooding_monitoring` (dev).
2. Evaluate (`etl.evaluate_trigger`): action = ≥6/10 gauges (`ACTION_MIN_GAUGES`) over their per-gauge 4-yr RP thresholds on the same valid day; readiness = ensemble-mean GloFAS forecast at lead ≤12 d **OR** latest reanalysis > 3,132 m³/s. Chart to blob.
3. Email: action → `nga:trigger`; readiness → `nga:info`; Monday informational → `nga:info`. `STAGE != prod` → everything to `nga:test`. The chart is attached on readiness/informational emails only — action emails go out without it.

**Flash** (`monitor_flash_flood.py` → `export_monitoring_status.py flash`):

1. Read the last 120 days of the 4 LGAs' exposure from `app.floodscan_exposure` (prod, `adm_level = '2'`), strict 3-day rolling mean — no `min_periods`, which matches the threshold derivation exactly (thresholds validated as ~7.75-yr empirical RP / 3-in-28-years each on this precise aggregation).
2. Freshness guard: latest `valid_date` must be ≥ run-date−2, else exit 1 with no email.
3. Evaluate on the latest date only: an LGA fires at `rolling >= threshold`, advises at `>= 0.8 × threshold` (`FLASH_WARNING_FRACTION`). An LGA with a `None` threshold is monitored but cannot fire (surfaces as `thresholds_pending`); all four currently have thresholds.
4. Email: any LGA over threshold → `nga-flash:trigger`; any LGA ≥80% → advisory to `nga-flash:info` (any day); Monday informational → `nga-flash:info`. `STAGE != prod` → `nga-flash:test`.

**Status export (both jobs):** the final task runs `pipelines/export_monitoring_status.py {riverine|flash}`, which re-uses the *same* `evaluate_trigger`/`evaluate_flash` functions the email pipelines call (so the page can never disagree with the last email) and writes `{flash: {...}, riverine: {...}}` plus the latest chart PNG. Each job only rewrites **its own** section: with `STATUS_BLOB_PREFIX` set (the Databricks tasks), it seeds `status.json` from `ds-aa-nga-flooding/monitoring/status/status.json` in the dev `projects` container and uploads `status.json` + `{section}_latest.png` back. Without it (the GHA fallbacks), the workflow seeds from and pushes **directly** to the `monitoring-status` branch (no PR, via a `git worktree`). A missing chart blob degrades gracefully (`chart_stale: true`) rather than failing the run.

## Outputs

- `projects.ds_aa_nga_flooding_monitoring` (dev DB) — riverine forecasts, unique key `monitoring_date`/`valid_date`/`src`. Hardcoded dev (`stratus.get_engine(stage="dev")` in `etl.py`) at `73bd934`, regardless of the bundle target.
- Blob `projects/ds-aa-nga-flooding/monitoring/{date}_{action}.png` + `flash_{date}_{triggered}.png` (HDX-styled charts, dev).
- Blob `projects/ds-aa-nga-flooding/monitoring/status/` — `status.json`, `riverine_latest.png`, `flash_latest.png` (dev): the status-page source of truth since the migration. Live page check 2026-09-25: flash `date` 2026-09-23 / `generated_at` 2026-09-25T01:38 UTC (from the Databricks flash job); riverine `generated_at` 2026-09-24T22:12 UTC.
- Listmonk campaigns — riverine lists `nga:info` / `nga:trigger` / `nga:test`; flash lists `nga-flash:info` / `nga-flash:trigger` / `nga-flash:test`. **List ids are resolved by tag at runtime** (`resolve_list_id` filters `fetch_all_lists(tag="ds-aa-nga-flooding")`), never hardcoded.
- `monitoring-status` branch (legacy): `exploration/2026/cerf/monitoring/status.json` + PNGs. Last GHA-written commits: flash 2026-09-24T01:51Z, riverine 2026-09-25T00:20Z (`216dd8c`); it no longer advances unless a fallback workflow is dispatched. Its copy looking "stale" is expected — don't debug it.
- Public GH Pages status page at <https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/> (and `status.json` alongside it) — assembled by `deploy-app-cron.yml`; verified HTTP 200 on 2026-09-25.

## Dependencies

- `ocha-relay` (Listmonk client), `git+…/ocha-relay.git@v0.3.0` (both `requirements.txt` and the bundle's library list).
- `ocha-stratus`, `cfgrib`, `eccodes` (GRIB decoding for GloFAS). **Pins differ by platform:** the Databricks cluster uses `eccodes==2.42.0` + `cfgrib==0.9.14.0` (the 2.47.0 wheel's bundled crypto aborts cluster Python with `FATAL FIPS SELFTEST FAILURE`, exit −6); `requirements.txt` (GHA fallback) keeps `eccodes==2.47.0`. GHA fallbacks run Python 3.12; `deploy-app-cron.yml` runs 3.11 and pip-installs its export deps inline.
- Databricks credentials: the Job Compute policy (`000C79D951EAF0D6`) injects `DSCI_AZ_DB_*` / `DSCI_AZ_BLOB_*` (dev + prod) and `CDSAPI_KEY` from the `dsci` secret scope; `DSCI_LISTMONK_BASE_URL` / `_API_USERNAME` / `_API_KEY` come from `dsci` via `spark_env_vars`; `GOOGLE_API_KEY` is resolved at run time by `run_task.py --secret` (a missing `spark_env_vars` secret stops the cluster launching, which briefly took the flash job down on 2026-09-24).
- GHA secrets (fallbacks + `deploy-app-cron`): `DSCI_AZ_BLOB_DEV_SAS`(+`_WRITE`, `_PROD_SAS`), `DSCI_AZ_DB_DEV_*` (riverine) / `DSCI_AZ_DB_PROD_*` (flash read), `GOOGLE_API_KEY`, `CDSAPI_KEY`/`CDSAPI_URL`, `DSCI_LISTMONK_API_URL`→`DSCI_LISTMONK_BASE_URL`, `DSCI_LISTMONK_API_USERNAME`/`KEY` (send-scoped). The one-off `setup_nga_listmonk_lists.py` needs *admin* creds instead (`DSCI_LISTMONK_ADMIN_API_USERNAME`/`KEY`).
- `STAGE` (prod = real lists; anything else = test lists + `[TEST]` banner) — from the bundle `stage` variable on Databricks, from the `stage` dispatch input on the GHA fallbacks.
- Upstream: [floodexposure-monitoring](floodexposure-monitoring.md) chain must land the day's exposure before 01:30 UTC (flash has a freshness guard).
- `main` requires PRs for normal changes; the `monitoring-status` branch is a deliberate, documented exception (direct push, no review, generated data only) — see [conventions.md](../infrastructure/conventions.md#version-control--git).

## Failure modes & debugging

- **Where the logs are**: Databricks job run pages (`dbx:755265061277015` riverine, `dbx:351228559024609` flash) — each task's output shows a `[run_task] script=… env=…` header. Failures email the job owner. [pipeline-registry.md](../infrastructure/pipeline-registry.md) carries both jobs with last-success-vs-cadence health.
- **Riverine run fails in CDS download**: first check `CDSAPI_URL` is the EWDS override (`https://ewds.climate.copernicus.eu/api`) — the policy default is plain CDS, where GloFAS isn't served. Then check whether CEMS restructured the dataset again (the Aug-2026 GloFAS v5 rollout switched `cems-glofas-historical` to `year`/`month`/`day` from `hyear`/`hmonth`/`hday`, renamed the discharge variable and added a required `timespan`). The reanalysis stays pinned to `version_4_0` for calibration consistency — when v4 intermediate production stops, or `operational` flips to v5 on the forecast dataset, the 3,132 m³/s readiness threshold needs re-derivation against v5 climatology.
- **Riverine `check_forecasts` exits −6 / `FATAL FIPS SELFTEST FAILURE`** on Databricks: eccodes wheel too new for the runtime — keep the cluster on `eccodes==2.42.0`.
- **GRIB decode errors** (`No final 7777`, `KeyError: gridType`) on GHA: libeccodes too old for ECMWF's local-section template — hence `eccodes==2.47.0` in `requirements.txt`.
- **Riverine run exits 139 with everything apparently done** (GHA): expected and worked around — eccodes/cfgrib segfault during interpreter teardown on Linux, so `check_forecasts.py` ends with `os._exit(0)`.
- **Job cluster won't launch ("Spark secret resolution failed")**: a `{{secrets/dsci/…}}` reference in `spark_env_vars` points at a key missing from the scope. Add the key or move it to `run_task.py --secret`.
- **Flash run fails the freshness guard**: check the `floodexposure-monitoring` run history — its chain is the sole data source.
- **No emails arriving**: check the job's `stage` parameter (prod target → real lists; dev target/GHA default → test lists), then Listmonk campaign history ([comms-listmonk.md](../infrastructure/comms-listmonk.md)).
- **Falling back to GHA**: dispatch `monitoring.yml` / `flash-monitoring.yml` manually — but the migration happened *because* GitHub runners are losing network access to the Postgres DB, so the fallback may itself fail on DB connect. A fallback run writes the `monitoring-status` branch, not blob, so if blob exists the page will keep showing the blob copy.
- **Status page stale while the jobs look fine**: compare the live page's `status.json` with the blob copy at `projects/ds-aa-nga-flooding/monitoring/status/status.json` (dev). If blob is fresh but the page isn't, `deploy-app-cron.yml` failed (it's the only thing that republishes). If blob is stale, check the `export_status` task. **Don't** compare against the `monitoring-status` branch — it's legacy since 2026-09-24.
- **Crons silently stopped** (GHA side — now only `deploy-app-cron.yml`): GitHub auto-disables schedules after 60 days of repo inactivity (`disabled_inactivity`) — this killed the 2025 pipeline from Dec 2025 to Aug 2026 unnoticed. `gh workflow list --all` shows it; `gh workflow enable <id>` fixes it.
- **Don't confuse this repo with `OCHA-DAP/ds-nga-flood-monitoring`**: the registry and [deployments.md](../infrastructure/deployments.md#github-actions-pipelines) also carry a *separate* repo, `ds-nga-flood-monitoring` (`nga-gauge-monitor.yaml`, daily 14:00 UTC), documented on its own page, [pipelines/nga-flood-monitoring](nga-flood-monitoring.md).

## Gotchas

- **Data plane is dev regardless of `STAGE`** at `main@73bd934`: riverine DB (`get_engine(stage="dev")`), chart blobs and the status blob are all dev; only email routing follows `STAGE`. Flash *reads* prod (`app.floodscan_exposure`) because that's where floodexposure-monitoring writes. The registry's `data-mode: prod` for both jobs reflects the bundle `stage` variable, not the data plane. The prod cutover (`STAGE` selecting the data plane, SES email backend, prod `projects` schema) sits on the unmerged branch `ops/prod-cutover` (`9dda278`); `databricks.yml`'s own header says to run the `dev` target only until it merges, yet the prod-target jobs are deployed and the flash one is running. <!-- TODO: re-sync when ops/prod-cutover merges — outputs, email backend and status-blob stage will change. -->
- `app.floodscan_exposure.adm_level` is TEXT — quote comparisons.
- The legacy blob distribution list (`ds-aa-nga-flooding/email/distribution_list.csv`) is superseded by Listmonk.
- **The status page is public.** `exploration/2026/cerf/monitoring/index.html` (on `main`, normal PR review) is served at <https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/> — the whole repo checkout is rsynced into the Pages artifact, so the path is the URL. Worth knowing before putting anything sensitive in `status.json`; this is a dev-stage data plane published on a public site.
- **[stale] [infrastructure/deployments.md](../infrastructure/deployments.md) has no row for this repo's `deploy-app-cron.yml` GH Pages deploy** — its "GitHub Actions pipelines" table lists the *different* repo `ds-nga-flood-monitoring`. Databricks coverage is deferred there to [pipeline-registry.md](../infrastructure/pipeline-registry.md), which carries both jobs.
- A separate branch, `feat/niger-benue-multistate-monitoring`, holds the `/app/` site — a broader Niger/Benue multistate effort not reconciled with this page's two-job scope.

## Downstream consumers

- Email recipients on the Listmonk lists — per the 2026-08-11 sync, a two-person soak audience per stream pending distribution-list migration.
- The public GH Pages status page, <https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/> — `index.html` from `main` reading `status.json` + the two PNGs from blob (fallback: the `monitoring-status` branch).
- [frameworks/nga-flooding/2026-06-18](../frameworks/nga-flooding/2026-06-18.md) — this pipeline *is* that framework version's monitoring.
