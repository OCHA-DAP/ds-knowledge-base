---
content_type: pipeline
name: nga-flooding-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor flooding", ref: ".github/workflows/monitoring.yml", schedule: "0 20 * * * (daily 20:00 UTC) + workflow_dispatch", status: live }
    - { name: "Monitor flash flooding", ref: ".github/workflows/flash-monitoring.yml", schedule: "30 1 * * * (daily 01:30 UTC) + workflow_dispatch", status: live }
    - { name: "deploy-app-cron (GH Pages publish shim)", ref: ".github/workflows/deploy-app-cron.yml", schedule: "0 2 * * * + 45 20 * * * (UTC, ~30-45 min after each monitoring run) + workflow_dispatch", status: live }
inputs:
  - "CDS cems-glofas-forecast (operational ensemble, Wuroboki point, leads 1-12 d)"
  - "CDS cems-glofas-historical (version_4_0 intermediate reanalysis, Wuroboki point, walk-back -2..-7 d)"
  - "Google Flood Forecasting API gauges:queryGaugeForecasts (10 endorsed GRRR gauges, one call)"
  - "DB app.floodscan_exposure prod (per-LGA FloodScan x WorldPop exposure, from floodexposure-monitoring)"
outputs:
  - "DB projects.ds_aa_nga_flooding_monitoring dev (riverine forecasts; unique key monitoring_date/valid_date/src)"
  - "blob projects/ds-aa-nga-flooding/monitoring/{date}_{action}.png + flash_{date}_{triggered}.png (HDX-styled charts, dev)"
  - "Listmonk campaigns: riverine lists nga:info / nga:trigger / nga:test; flash lists nga-flash:info / nga-flash:trigger / nga-flash:test (list ids are resolved by TAG at runtime, never hardcoded)"
  - "orphan branch `monitoring-status`: exploration/2026/cerf/monitoring/status.json + riverine_latest.png/flash_latest.png, pushed directly (no PR) after every run"
  - "public GH Pages status page https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/ (built from the above by deploy-app-cron.yml)"
dependencies:
  - "ocha-relay (Listmonk client)"
  - "ocha-stratus, cfgrib, eccodes (GRIB decoding for GloFAS)"
  - "Secrets: DSCI_AZ_BLOB_DEV_SAS(+_WRITE), DSCI_AZ_DB_DEV_*(riverine) / DSCI_AZ_DB_PROD_*(flash read), GOOGLE_API_KEY, CDSAPI_KEY/URL, DSCI_LISTMONK_API_URL->BASE_URL, DSCI_LISTMONK_API_USERNAME/KEY (send-scoped); DSCI_LISTMONK_ADMIN_API_USERNAME/KEY only for the one-off setup script"
  - "vars: STAGE (prod = real lists; anything else = test lists + [TEST] banner)"
  - "upstream: floodexposure-monitoring chain must land the day's exposure before 01:30 UTC (flash has a freshness guard)"
downstream:
  - "Email recipients on the Listmonk lists (per the 2026-08-11 sync: a two-person soak audience per stream, pending distribution-list migration — Listmonk-internal, not publicly verifiable)"
  - "Public GH Pages status page at https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/ — index.html from main + status.json/PNGs from the monitoring-status branch, assembled and deployed by deploy-app-cron.yml (verified live, HTTP 200, 2026-08-19)"
depends_on: [floodexposure-monitoring, listmonk]
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/", kind: status, title: "Nigeria flood monitoring public status page (status.json + PNGs from the monitoring-status branch)"}
  - {url: "https://ocha-dap.github.io/ds-aa-nga-flooding/", title: "ds-aa-nga-flooding", auto: true, first_seen: 2026-09-01}
source_repo: ocha-dap/ds-aa-nga-flooding
source_branch: main
source_sha: c812dad
code_ref:
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
extra:
  framework: "frameworks/nga-flooding/2026-06-18.md — trigger definitions and provenance live there; this page is the ops runbook"
  email_cadence: "weekly Monday informational per stream; immediate on trigger (both streams) and on flash approaching-threshold (>=80% of any LGA threshold) — verified in send_emails.py / monitor_flash_flood.py at c812dad"
  data_branch: "monitoring-status (tip 51bb2ab as of 2026-08-19) is NOT a code branch — an orphan branch that only receives twice-daily generated-data pushes (status.json + the two chart PNGs) from the export_monitoring_status.py step at the end of each GHA job on `main`. Its README documents the direct-push exception. The runbook below is anchored to `main` (source_sha), which is where all the code lives."
  qa_note: "QA pass 2026-08-19: the whole runbook was re-verified against the PUBLIC repo at main c812dad (workflow YAML, all pipeline scripts, src/constants.py, src/monitoring/etl.py + flash.py, requirements.txt) — the prior draft's claim that main was unreachable did not hold in CI. Corrections applied: readiness lead time 13 d -> 12 d (repo commit 38a674c, 2026-08-18), the third scheduled workflow deploy-app-cron.yml added, and the GH Pages publication of the status page confirmed live rather than left open."
  related_branch: "feat/niger-benue-multistate-monitoring holds the Niger/Benue multistate static app served at https://ocha-dap.github.io/ds-aa-nga-flooding/app/ — a broader effort not yet reconciled with the two-job (Adamawa riverine + BAY flash) monitoring documented on this page. Its own deploy-app.yml (6-h cron) does NOT fire, because GitHub only honours schedules on the default branch; deploy-app-cron.yml on main is the shim that actually deploys it (and overlays this pipeline's status page), and is to be deleted once the feature branch merges."
visibility: internal
last_synced: "2026-08-19"
---

# Nigeria Flooding Monitoring (2026 framework)

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am." Trigger design and provenance: [frameworks/nga-flooding/2026-06-18](../frameworks/nga-flooding/2026-06-18.md). The repo's own `CLAUDE.md` at `main` is the code-adjacent runbook — this page is the hub summary + cross-repo context.

## One-liner

*Two daily GHA pipelines evaluate the 2026 Nigeria AA triggers — Adamawa riverine (GloFAS readiness + 10-gauge Google action) at 20:00 UTC, BAY-states flash flood (FloodScan exposure vs per-LGA thresholds) at 01:30 UTC — email HDX-styled status updates via Listmonk, and push a machine-readable status snapshot to an orphan `monitoring-status` branch, which a third cron publishes as a public GH Pages status page.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor flooding (riverine) | `.github/workflows/monitoring.yml` | cron `0 20 * * *` | live |
| Monitor flash flooding | `.github/workflows/flash-monitoring.yml` | cron `30 1 * * *` | live |
| deploy-app-cron (GH Pages publish) | `.github/workflows/deploy-app-cron.yml` | crons `0 2 * * *` + `45 20 * * *` | live |

All three are on `main`; all three also accept `workflow_dispatch` (the two monitoring workflows take optional `date` and `stage` inputs, `stage` defaulting to `dev`). The flash cron is deliberately placed after the `floodexposure-monitoring` chain (23:15 UTC cron; DB write normally done 23:40–23:52 UTC, worst observed ~01:10). There is no cross-repo event trigger — on the rare day the chain slips past 01:30, the flash run fails its freshness guard visibly; re-run via `workflow_dispatch` or let the next day self-correct.

`deploy-app-cron.yml` is a **deliberate pre-merge shim** (its own header says to delete it once `feat/niger-benue-multistate-monitoring` merges): GitHub only honours `schedule:` on the default branch, so this file on `main` checks out the feature branch, runs its deploy steps, overlays `index.html` from `main` and the generated data from `monitoring-status`, and publishes the whole thing to GH Pages. Its two crons are timed ~30 min after the flash run and ~45 min after the riverine run so the published page is never far behind the data.

## Inputs

- GloFAS operational forecast (ensemble perturbed, leads 1–12 d) at Wuroboki, CDS `cems-glofas-forecast`.
- GloFAS `version_4_0` intermediate reanalysis, walk-back −2..−7 d, CDS `cems-glofas-historical`.
- 10 endorsed GRRR gauges via one Google Flood Forecasting API call (`gauges:queryGaugeForecasts`).
- `app.floodscan_exposure` (prod DB) — per-LGA FloodScan × WorldPop exposure, written by [floodexposure-monitoring](floodexposure-monitoring.md); flash's sole data source.

## Steps

**Riverine** (`check_forecasts.py` → `save_plots.py` → `send_emails.py`):

1. Download GloFAS operational forecast (leads 1–12 d) at Wuroboki; walk back −2..−7 d for the latest available `version_4_0` intermediate reanalysis (missing reanalysis = warning, never fatal). Fetch all 10 GRRR gauges in one Google API call (latest issuance per gauge kept). Upsert to `projects.ds_aa_nga_flooding_monitoring` (dev).
2. Evaluate (`etl.evaluate_trigger`): action = ≥6/10 gauges over their per-gauge 4-yr RP thresholds on the same valid day; readiness = ensemble-mean GloFAS forecast at lead ≤12 d **OR** latest reanalysis > 3,132 m³/s. Chart to blob.
3. Email: action → `nga:trigger`; readiness → `nga:info`; Monday informational → `nga:info`. `STAGE != prod` → everything to `nga:test`. The chart is attached on readiness/informational emails only — action emails go out without it.

**Flash** (`monitor_flash_flood.py`):

1. Read the last 120 days of the 4 LGAs' exposure from `app.floodscan_exposure` (prod, `adm_level = '2'`), strict 3-day rolling mean — no `min_periods`, which matches the threshold derivation exactly (thresholds validated as ~7.75-yr empirical RP / 3-in-28-years each on this precise aggregation).
2. Freshness guard: latest `valid_date` must be ≥ run-date−2, else exit 1 with no email.
3. Evaluate on the latest date only: an LGA fires at `rolling >= threshold`, advises at `>= 0.8 × threshold`. An LGA with a `None` threshold is monitored but cannot fire (surfaces as `thresholds_pending`); all four currently have thresholds.
4. Email: any LGA over threshold → `nga-flash:trigger`; any LGA ≥80% → advisory to `nga-flash:info` (any day); Monday informational → `nga-flash:info`. `STAGE != prod` → `nga-flash:test`.

**Status export (both jobs):** a final step runs `pipelines/export_monitoring_status.py {riverine|flash}`, which re-uses the *same* `evaluate_trigger`/`evaluate_flash` functions the email pipelines call (so the page can never disagree with the last email) and writes `{flash: {date, triggered, warning, thresholds_pending, lgas: {<pcode>: {name, rolling, threshold, exceeds, warning}}, chart, chart_stale, generated_at}, riverine: {date, action, readiness, readiness_forecast, readiness_reanalysis, max_gauges_exceeding, n_gauges_reporting, glofas_max, reanalysis_max, chart, chart_stale, generated_at}}` plus the latest chart PNG. The step seeds `status.json` from the branch's current copy first, so each job only rewrites **its own** section. It then pushes **directly** (no PR, via a `git worktree` on `monitoring-status`) to `exploration/2026/cerf/monitoring/`. A missing chart blob degrades gracefully (`chart_stale: true`, keeps the previous PNG) rather than failing the run.

## Outputs

- `projects.ds_aa_nga_flooding_monitoring` (dev DB) — riverine forecasts, unique key `monitoring_date`/`valid_date`/`src`.
- Blob `projects/ds-aa-nga-flooding/monitoring/{date}_{action}.png` + `flash_{date}_{triggered}.png` (HDX-styled charts, dev).
- Listmonk campaigns — riverine lists `nga:info` / `nga:trigger` / `nga:test`; flash lists `nga-flash:info` / `nga-flash:trigger` / `nga-flash:test`. **List ids are resolved by tag at runtime** (`resolve_list_id` filters `fetch_all_lists(tag="ds-aa-nga-flooding")`), never hardcoded — so the numeric ids recorded in earlier syncs (113/114/115, 118/119/120) are observations, not configuration, and the pipeline follows the tag if they change.
- `monitoring-status` branch: `exploration/2026/cerf/monitoring/status.json` + `riverine_latest.png` / `flash_latest.png`, overwritten twice daily. Live sample verified 2026-08-19: riverine `date` 2026-08-18 / `generated_at` 2026-08-18T22:06 UTC (10/10 gauges reporting, `glofas_max` 815.46, `reanalysis_max` 356.53, action/readiness both false); flash `date` 2026-08-17 (exposure valid date, two days behind the run by design) / `generated_at` 2026-08-19T02:04 UTC (4 LGAs — Mobbar `NG008023`, Maiduguri `NG008021`, Jere `NG008013`, Geidam `NG036006` — all `rolling: 0.0`, not triggered/warning).
- Public GH Pages status page at <https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/> (and `status.json` alongside it) — assembled by `deploy-app-cron.yml`; both verified serving HTTP 200 on 2026-08-19 with the same payload as the branch.

## Dependencies

- `ocha-relay` (Listmonk client), pinned to `git+…/ocha-relay.git@v0.3.0` in `requirements.txt`.
- `ocha-stratus`, `cfgrib`, `eccodes` (GRIB decoding for GloFAS) — `eccodes==2.47.0` is pinned in `requirements.txt` (confirmed at `main`), required post-GloFAS-v5 rollout. Both monitoring workflows run Python 3.12 (matching `pyproject.toml`); `deploy-app-cron.yml` runs 3.11 and pip-installs its export deps inline rather than from `requirements.txt`.
- Secrets: `DSCI_AZ_BLOB_DEV_SAS`(+`_WRITE`), `DSCI_AZ_DB_DEV_*` (riverine) / `DSCI_AZ_DB_PROD_*` (flash read), `GOOGLE_API_KEY`, `CDSAPI_KEY`/`CDSAPI_URL`, `DSCI_LISTMONK_API_URL`→`DSCI_LISTMONK_BASE_URL` (the org secret and the name `ocha-relay` reads differ — the workflow does the rename), `DSCI_LISTMONK_API_USERNAME`/`KEY` (send-scoped). The one-off `setup_nga_listmonk_lists.py` needs *admin* creds instead (`DSCI_LISTMONK_ADMIN_API_USERNAME`/`KEY`) — the send-scoped key cannot create lists or subscribers.
- Repo var `STAGE` (prod = real lists; anything else = test lists + `[TEST]` banner).
- Upstream: [floodexposure-monitoring](floodexposure-monitoring.md) chain must land the day's exposure before 01:30 UTC (flash has a freshness guard).
- `main` requires PRs for normal changes; the `monitoring-status` branch is a deliberate, documented exception (direct push, no review, twice-daily generated data only) — see [conventions.md](../infrastructure/conventions.md#version-control--git).

## Failure modes & debugging

- **Riverine run fails in CDS download**: check whether CEMS restructured the dataset again (the Aug-2026 GloFAS v5 rollout switched `cems-glofas-historical` to `year`/`month`/`day` from `hyear`/`hmonth`/`hday`, renamed the discharge variable and added a required `timespan`, breaking old requests with opaque 400s — the current request in `etl.get_glofas_reanalysis` carries the new schema). The reanalysis stays pinned to `version_4_0` for calibration consistency — when v4 intermediate production stops, or `operational` flips to v5 on the forecast dataset, the 3,132 m³/s readiness threshold needs re-derivation against v5 climatology.
- **GRIB decode errors** (`No final 7777`, `KeyError: gridType`): libeccodes too old for ECMWF's local-section template — hence the `eccodes==2.47.0` pin.
- **Riverine run exits 139 with everything apparently done**: expected and worked around — eccodes/cfgrib segfault during interpreter teardown on Linux, so `check_forecasts.py` ends with `os._exit(0)`. Real failures still raise before that point.
- **Flash run fails the freshness guard**: check the `floodexposure-monitoring` Actions history — its chain is the sole data source.
- **No emails arriving**: check `STAGE` repo var (test vs prod lists), then Listmonk campaign history ([comms-listmonk.md](../infrastructure/comms-listmonk.md)).
- **Crons silently stopped**: GitHub auto-disables schedules after 60 days of repo inactivity (`disabled_inactivity`) — this killed the 2025 pipeline from Dec 2025 to Aug 2026 unnoticed. `gh workflow list --all` shows it; `gh workflow enable <id>` fixes it. (Both crons demonstrably fired on 2026-08-19: `status.json` carries `generated_at` 2026-08-18T22:06 and 2026-08-19T02:04 UTC.)
- **`monitoring-status` branch stops updating**: since it's an orphan data branch with no PR gate, a silent failure here won't show up as a blocked PR — check the Actions history for `monitoring.yml`/`flash-monitoring.yml` directly, and compare `status.json`'s `generated_at` against wall-clock. Note the publish step is a *separate* step from the email step: emails can go out fine while the status push fails, and vice versa.
- **Status page shows stale data while emails look fine**: `deploy-app-cron.yml` is the only thing that republishes the page. If it fails (or is deleted at feature-branch merge without `deploy-app.yml`'s own schedule taking over), the branch keeps updating but the public page freezes. Compare the page's `status.json` with the branch's.
- **Not in [pipeline-registry.md](../infrastructure/pipeline-registry.md)**: the registry currently lists only two `OCHA-DAP/ds-aa-nga-flooding` Databricks entries — `dbx:619598372576627` (`[dev adm_tdowning] Download GloFAS Reforecast (Country)`, 🔴 DOWN, ~945h since last success) and `dbx:432260566342587` (`[dev adm_tdowning] Process GloFAS Reforecast…`, 🟢 OK) — both personal dev jobs unrelated to this page's scheduled GHA workflows. `monitoring.yml`/`flash-monitoring.yml`/`deploy-app-cron.yml` have no registry row at all, so the registry's health tracking gives no independent confirmation the crons are still firing — `status.json`'s `generated_at` is the only freshness signal. [gap] worth adding these three to the registry's GHA half.

## Gotchas

- The data plane is dev-stage regardless of `STAGE` (riverine DB + chart blobs); only email routing follows `STAGE`. Flash *reads* prod (`app.floodscan_exposure`) because that's where floodexposure-monitoring writes.
- `app.floodscan_exposure.adm_level` is TEXT — quote comparisons.
- The legacy blob distribution list (`ds-aa-nga-flooding/email/distribution_list.csv`, `to`/`cc` columns per email type) is superseded by Listmonk — `setup_nga_listmonk_lists.py` is the one-off, idempotent migration that created the lists and imported subscribers. It is *not* part of the daily runs.
- **The status page is public.** `exploration/2026/cerf/monitoring/index.html` (on `main`, normal PR review) is served at <https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/> — the whole repo checkout is rsynced into the Pages artifact, so the path is the URL. Worth knowing before putting anything sensitive in `status.json`; note this is a *dev-stage* data plane published on a public site.
- **[stale] [infrastructure/deployments.md](../infrastructure/deployments.md) describes the wrong deploy mechanism** for this repo's GH Pages: it records `deploy-app.yml` on `feat/niger-benue-multistate-monitoring` with a 6-h cron, but that schedule never fires (GitHub only honours `schedule:` on the default branch). The live deployer is `deploy-app-cron.yml` on `main` (02:00 + 20:45 UTC), and it also publishes the 2026 monitoring status page — which has no row there at all. Fix that page separately.
- A separate branch, `feat/niger-benue-multistate-monitoring`, holds the `/app/` site (pre-baked JSON incl. live Google forecasts) — a broader Niger/Benue multistate effort not reconciled with this page's two-job scope, and the `exploration/2026/cerf/workflow/` design notebooks the trigger constants cite live there too, not on `main`.

## Downstream consumers

- Email recipients on the Listmonk lists — per the 2026-08-11 sync, a two-person soak audience per stream pending distribution-list migration. Subscriber counts live in Listmonk and are not publicly checkable; confirm there before assuming the real audience is live.
- The public GH Pages status page, <https://ocha-dap.github.io/ds-aa-nga-flooding/exploration/2026/cerf/monitoring/> — `index.html` from `main` reading `status.json` + the two PNGs from the `monitoring-status` branch.
- [frameworks/nga-flooding/2026-06-18](../frameworks/nga-flooding/2026-06-18.md) — this pipeline *is* that framework version's monitoring.
