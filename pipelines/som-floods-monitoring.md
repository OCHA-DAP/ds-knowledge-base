---
content_type: pipeline
name: som-floods-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor Somalia riverine flooding", ref: ".github/workflows/monitoring.yml", schedule: "0 10 * * * (daily 10:00 UTC / 13:00 EAT; step 1 waits for the day's issues until 15:45 UTC) + workflow_dispatch", status: live }
    - { name: "Deploy pages site (overlays monitoring status)", ref: ".github/workflows/deploy-pages.yml", schedule: "workflow_run on monitoring completion + push to main (pages/**) + workflow_dispatch", status: live }
inputs:
  - "EWDS cems-glofas-forecast (operational ensemble, 51 perturbed members, days 1-12, one box over the 7 trigger cells)"
  - "Google Flood Forecasting API gauges:queryGaugeForecasts (7 HYBAS gauges; Dollow reads the Juba main-stem gauge hybas_1121039440 since 2026-09-15)"
  - "EWDS cems-glofas-forecast form.json (system_version legacy list — the GloFAS version guard) + GRIB process ids"
  - "blob projects/ds-aa-som-floods/monitoring/notified/{season}_{year}.json (what has already been emailed this season)"
outputs:
  - "blob projects/ds-aa-som-floods/monitoring/forecasts/{date}.parquet (dev) — the day's rows of both sources; the store every later step reads (no database)"
  - "blob projects/ds-aa-som-floods/monitoring/status/{date}.json (the evaluation) + monitoring/{date}.png (chart)"
  - "blob projects/ds-aa-som-floods/monitoring/notified/{season}_{year}.json — trigger legs already announced (real-list, non-simulated sends only)"
  - "blob raw: raw/glofas/monitoring/glofas_forecast_{date}.grib, raw/google/monitoring/google_forecast_{date}.json"
  - "Listmonk campaigns: Monday informational → list id 103 ('Pauline', untagged, every run mode; decision 2026-09-21); readiness/activation → som:trigger (tag ds-aa-som-floods), or som:test when TEST_EMAIL. The tagged som:info list (id 122) still exists but is not used by the pipeline"
  - "orphan branch `monitoring-status`: pages/monitoring/status.json + latest.png, pushed directly after each non-dry run"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/monitoring/", kind: status, title: "Somalia riverine flood trigger — live monitoring status"}
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/glofas-version/", kind: report, title: "GloFAS version switch — what v4 vs v5 does to the Deyr thresholds"}
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/activation-timing/", kind: report, title: "Timing of activations — dates the Somalia riverine flood trigger is met each season, with gauges and exposure in the 14 AA districts"}
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/ensemble-agreement/", kind: report, title: "The ensemble agreement level — supporting analysis for the Somalia riverine flood trigger"}
dependencies:
  - "ocha-relay v0.3.0 (Listmonk, git tag pin), ocha-stratus>=0.1.7 (blob only), cdsapi, cfgrib + eccodes==2.47.0, jinja2; pinned in requirements-monitoring.txt"
  - "Secrets: org DSCI_AZ_BLOB_DEV_SAS(+_WRITE), DSCI_LISTMONK_API_URL->BASE_URL, DSCI_LISTMONK_API_USERNAME/KEY; repo GOOGLE_API_KEY, CDSAPI_KEY, CDSAPI_URL (EWDS)"
  - "Run-mode vars TEST_EMAIL / DRY_RUN (default true in code; prod = explicit false repo vars), SIMULATE_TRIGGER (+ ALLOW_REAL_SIMULATION for a real-list simulation); WAIT_FOR_ISSUE_UNTIL_UTC (15:45 in the workflow)"
  - "One-off admin path (pipelines/setup_som_listmonk_lists.py, not part of the daily run): DSCI_LISTMONK_ADMIN_API_USERNAME/KEY — the send-scoped key used by the daily job cannot write subscribers/lists"
downstream:
  - "Email recipients: list 103 (framework owner only) for the Monday informational; the som:trigger list for readiness/activation"
  - "Public status page (district map, window cards, chart, per-station tables) and the site landing page cards"
depends_on: [listmonk]
source_repo: ocha-dap/ds-aa-som-floods
source_branch: main
source_sha: 4b464cf
code_ref:
  - .github/workflows/monitoring.yml
  - .github/workflows/deploy-pages.yml
  - pipelines/check_forecasts.py
  - pipelines/save_plots.py
  - pipelines/send_emails.py
  - pipelines/export_monitoring_status.py
  - pipelines/setup_som_listmonk_lists.py
  - pipelines/render_dryrun_emails.py
  - src/monitoring/config.py
  - src/monitoring/etl.py
  - src/monitoring/evaluate.py
  - src/monitoring/thresholds.py
  - src/monitoring/thresholds.json
  - src/monitoring/flags.py
  - scripts/build_monitoring_thresholds.py
  - scripts/build_glofas_version_page.py
  - scripts/check_pages_match_config.py
  - pages/monitoring/index.html
extra:
  design: "analysis/som-flooding-multisource.md — trigger definition (TRIGGER_CONFIG in src/constants.py: Gu on Google Flood Hub, Deyr on GloFAS v5-fitted thresholds; Juba 3 of 4 points, Shabelle 2 of 3 over own return-period level on one forecast day; RPs Juba Gu 5 / Juba Deyr 4 / Shabelle Gu 6 / Shabelle Deyr 5 — Shabelle Deyr moved 1-in-4 → 1-in-5 on 2026-09-18 so the envelope releases in 8 river-seasons, not 10; action leads 1-7, readiness GloFAS leads 8-12, RP capped at 1-in-5); this page is the ops runbook"
  readiness_levels: "Since the 2026-09-16 sync the readiness leg reads the SAME reanalysis levels as the action leg (at the capped RP), not the readiness-band refit; the readiness_band rows stay in thresholds.json for reference only (src/monitoring/thresholds.py, evaluate.py)."
  glofas_version: "Design fitted Deyr levels on GloFAS v5 reanalysis assuming v5 was live. Operational forecast is still v4 (v4.5, 16 Apr 2026); v5 pre-operational on EWDS. Pipeline runs on v4-fitted levels (GLOFAS_OPERATIONAL = glofas_v4 in src/monitoring/config.py; live status.json 2026-09-23 reports glofas_v4 (gpi5/bp21)); both level sets frozen in thresholds.json. On v4 the adopted Deyr rules over-activate — trigger revision pending, see /glofas-version/."
  monitoring_windows: "Open by calendar month (config.MONITORING_OPEN_MONTHS): Deyr Sep-Jan, Gu Feb-Jun. Every forecast valid day inside the open months counts toward the rule; the months outside the fitted season (Gu Mar-May, Deyr Oct-Dec) are a surveillance buffer. Jul-Aug: pipeline runs, page updates, no email."
  dollow: "The design's Dollow Google point hybas_1121038740 is the Dawa branch and is not served by the live Flood Hub API (404). Dollow now reads hybas_1121039440, the Juba main stem 8 km ESE. Dollow's Gu levels in thresholds.json are fitted on the main-stem gauge's retrospective. config.GOOGLE_NOT_SERVED is empty — every trigger gauge is currently live on the Flood Hub API."
  email_cadence: "While a window is open: Monday informational (to list 103 in every mode) + an immediate email the day readiness or activation is first reached. Each trigger leg is announced ONCE per season (state in monitoring/notified/{season}_{year}.json; Deyr's January days count to the previous year); readiness is suppressed once activation has been reached. Nothing when no window is open. Templates are content-only (the Listmonk base_campaign wrapper supplies header, contact and footer)."
  other_repo_job: "databricks.yml also defines one Databricks job, download_glofas_reforecast_box (SOM, leads 8-12) — a manual-only, one-shot GloFAS v4.2 reforecast download for the analysis/calibration side, not part of this daily runbook. Seen in infrastructure/pipeline-registry.md as dbx:928609832532141, dev-mode, manual, last run 1044h ago as of the 2026-09-24 snapshot."
visibility: public
last_synced: "2026-09-24"
---

# Somalia riverine flood monitoring

> Runbook for the daily pipeline that applies the Somalia riverine flood trigger. Trigger design and evidence: [analysis/som-flooding-multisource](../analysis/som-flooding-multisource.md). The repo's `CLAUDE.md` is the code-adjacent runbook; this page is the hub summary.

## One-liner

*Daily 10:00 UTC GHA: wait for the day's GloFAS operational ensemble (EWDS) + Google Flood Hub issue at the seven Juba/Shabelle trigger points (until 15:45 UTC) → the day's rows to blob → four river-season window rules (action leads 1–7 d, readiness GloFAS 8–12 d) → chart → Listmonk email while a window is open → status snapshot on the orphan `monitoring-status` branch → public status page redeployed when the run completes.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor Somalia riverine flooding | `.github/workflows/monitoring.yml` | cron `0 10 * * *` (13:00 EAT) + dispatch (date, test_email, dry_run, simulate_trigger); `timeout-minutes: 355` | live on `main` |
| Deploy pages site | `.github/workflows/deploy-pages.yml` | `workflow_run` on monitoring completion + push to `main` (pages/**) + dispatch | live |

The run starts at 10:00 UTC and step 1 asks EWDS for the day's own GloFAS issue and Google for an issue dated today, retrying every 15 min while either is missing, until `WAIT_FOR_ISSUE_UNTIL_UTC` (15:45 UTC, which keeps the job under GitHub's 6 h limit). After that it takes what exists: the previous GloFAS issue (`max_days_back=1`) and the latest Google issue. Runs for a past `date` do not wait. The workflow comments still quote GloFAS arriving at ~14:15–15:30 UTC (seen 2026-09-14/15). But the orphan-branch commits for 2026-09-21/22/23 all landed at ~10:10–10:11 UTC with that day's GloFAS issue, so recently the issue has already been on EWDS by the time the run starts.

There is also a third, unrelated Databricks job in this repo (see `extra.other_repo_job`). It is a manual-only reforecast download for the analysis side and is not part of this schedule.

## Inputs

- GloFAS `cems-glofas-forecast`, `system_version: operational`, `ensemble_perturbed_forecasts`, leads 24–288 h, one box `[4.9, 41.9, 1.1, 45.7]`. Station values are taken at the seven frozen 0.05° river cells (`src/monitoring/glofas_cells.json`), matched with a hard 0.03° guard against a box-edge snap.
- Google Flood Forecasting API: one `queryGaugeForecasts` call for the 7 HYBAS gauge ids (`src/constants.py`), falling back to per-gauge calls if the batch 404s; latest issue per gauge. It returns issue−2…issue+5 days, so the action leg reads Google at leads 1–5. Ids the API stops serving are listed in `config.GOOGLE_NOT_SERVED` and probed one by one (currently empty).
- **Not automated:** a SWALIM moderate flood risk alert for either river can also reach readiness. The pipeline does not read the bulletins. `status.json` carries a `swalim_note`, and both the page and the emails point readers to [FAO SWALIM](https://frrims.faoswalim.org/). Readiness can therefore be reached without anything in this pipeline firing.

## Steps

1. `check_forecasts.py`: runs the version guard (the EWDS legacy list must not contain `version_4*`; GRIB `generatingProcessIdentifier`/`backgroundProcess` must equal 5/21), fetches both products with the wait loop above, and writes `monitoring/forecasts/<date>.parquet` (dev blob). On a version change it fails loudly and sends no email, unless `ALLOW_VERSION_MISMATCH=true`. Raw GRIB and Google JSON are kept under `raw/`, and a re-run reuses the GRIB already in blob. The script ends with `os._exit(0)` to avoid a cfgrib/eccodes teardown segfault on Linux.
2. `save_plots.py`: calls `evaluate.evaluate` (same-day votes per window on the ensemble median / deterministic value, over every valid day inside the open window months; readiness uses the same reanalysis levels at the capped RP), then draws the chart and writes it to blob. The evaluation also goes to `monitoring/status/<date>.json`.
3. `send_emails.py`: sends through Listmonk via ocha-relay while any window is open. The Monday informational goes to list 103. Readiness and activation emails go to `som:trigger` (or `som:test` under `TEST_EMAIL`), resolved by tag at runtime, and each leg is announced **once per season** (`monitoring/notified/`). `[TEST]`/`[SIM]` tags follow the run-mode flags. `SIMULATE_TRIGGER` forces an action activation on the first open window (or Deyr Shabelle if none is open). Test and simulated sends do not write the notified state.
4. `export_monitoring_status.py` (skipped when `DRY_RUN`): runs the same evaluation on the latest day on blob and writes `status.json` (+ per-point series and levels) and `latest.png` to the `monitoring-status` branch under `pages/monitoring/`. `deploy-pages.yml` then runs on `workflow_run` and overlays them into the Pages artifact.

`pipelines/render_dryrun_emails.py` is a manual helper outside the daily run. It renders simulated readiness and activation emails inside the real Listmonk template (via draft campaigns that are deleted immediately) so the wording can be reviewed before a trigger is met.

## Outputs

Per day, the job writes blob parquet/JSON/PNG, raw GRIB and Google JSON, and the per-season notified state. It also sends Listmonk campaigns, updates the `monitoring-status` branch, and feeds the public pages listed in the frontmatter. There is **no database table**: the daily job writes blob only, and no pipeline script opens an engine.

## Dependencies

See frontmatter. `requirements-monitoring.txt` is the runner pin set. The analysis extras in `pyproject.toml` (geoglows → hydrostats) do not build on a clean Python 3.12 runner.

## Failure modes & debugging

- **Run fails on "EWDS now lists a version_4 entry"**: GloFAS v5 has gone operational. Flip `GLOFAS_OPERATIONAL` to `glofas_v5` in `src/monitoring/config.py`, rebuild `/glofas-version/` (`scripts/build_glofas_version_page.py`), and take the Deyr rule question back to the working group (the v5 levels are the design levels).
- **Run fails on GRIB process ids**: same signal from the data side. Confirm on EWDS before overriding with `ALLOW_VERSION_MISMATCH=true`.
- **Run takes ~6 h / GloFAS not available for today**: the loop waited until 15:45 UTC and then fell back to the previous issue (`days_back` in the log). If two days are missing, EWDS is down; re-run later via dispatch with `date`.
- **Google 404**: a gauge id disappeared from the live API. Add it to `config.GOOGLE_NOT_SERVED`. The run continues with the gauges that are served, and the affected window card / email row shows the shortfall against **that window's** station count (`n_reporting` of `n_of`: 4 on the Juba, 3 on the Shabelle), not against all 7.
- **No email in season**: first check the `TEST_EMAIL`/`DRY_RUN` repo vars. Then check whether a window is open (`open_windows` in `status.json`; none is open in Jul–Aug). Then check whether the leg was already announced this season (`monitoring/notified/{season}_{year}.json`: a repeat trigger sends nothing on non-Mondays). Finally check the Listmonk campaign history.
- **Status page stale but emails fine**: `deploy-pages.yml` is the only publisher, and it runs on completion of the monitoring workflow. Check that it ran, then compare the page's `status.json` `generated_at` with the branch's.
- **Crons silently stopped**: GitHub disables schedules after 60 days of repo inactivity. Check with `gh workflow list --all`.
- **Chart missing**: `chart_stale: true` keeps the previous PNG. Either the `save_plots.py` step failed or it ran in `DRY_RUN`.
- **Registry gap**: `infrastructure/pipeline-registry.md` does not carry a `gha:ds-aa-som-floods/monitoring.yml` row (as of 2026-09-24), so don't read the registry as evidence the daily job is or isn't healthy. Check `gh run list --workflow monitoring.yml -R ocha-dap/ds-aa-som-floods` directly. The repo's only row in the registry is the unrelated manual Databricks reforecast job (`extra.other_repo_job`).

## Gotchas

- The data plane is dev-stage blob regardless of the email flags. Only routing follows `TEST_EMAIL`, and the Monday informational ignores even that: it always goes to list 103.
- Google always returns its current forecast, so a re-run for a past `MONITORING_DATE` carries today's Google issue (visible in `issued_time`).
- Every pipeline script explicitly loads `.env` at the repo root, because stratus reads credentials at import time.
- The public page is a dev-stage data plane on a public site, so nothing sensitive goes into `status.json`.
- Windows open by calendar month while thresholds are fitted on season maxima (see `extra.monitoring_windows`). For example, a September forecast day is judged against the Oct–Dec level.
- Changing `TRIGGER_CONFIG` means the published pages must be rebuilt. `scripts/check_pages_match_config.py` fails if any page's visible text disagrees with `src/constants.py`. It is run by hand before a PR, not in CI.
- **[stale]** The sibling analysis page ([analysis/som-flooding-multisource](../analysis/som-flooding-multisource.md)) still says "branch `feat/monitoring`" in its prose. The monitoring code is on `main`; flag this for that page's next re-ingestion.

## Downstream consumers

The informational list (103) and trigger list recipients; the public status page; the working group's pending decisions on the Deyr rules under GloFAS v4 (see `/glofas-version/`) and on the Dollow substitute point.
