---
content_type: pipeline
name: som-floods-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor Somalia riverine flooding", ref: ".github/workflows/monitoring.yml", schedule: "0 16 * * * (daily 16:00 UTC) + workflow_dispatch", status: live }
    - { name: "Deploy pages site (overlays monitoring status)", ref: ".github/workflows/deploy-pages.yml", schedule: "45 16 * * * + push to main (pages/**) + workflow_dispatch", status: live }
inputs:
  - "EWDS cems-glofas-forecast (operational ensemble, 50 perturbed members, days 1-12, one box over the 7 trigger cells)"
  - "Google Flood Forecasting API gauges:queryGaugeForecasts (7 HYBAS gauges; Dollow reads the Juba main-stem gauge hybas_1121039440 since 2026-09-15)"
  - "EWDS cems-glofas-forecast form.json (system_version legacy list — the GloFAS version guard)"
outputs:
  - "blob projects/ds-aa-som-floods/monitoring/forecasts/{date}.parquet (dev) — the day's rows of both sources; the store every later step reads (no database)"
  - "blob projects/ds-aa-som-floods/monitoring/status/{date}.json (the evaluation) + monitoring/{date}.png (chart)"
  - "blob raw: raw/glofas/monitoring/glofas_forecast_{date}.grib, raw/google/monitoring/google_forecast_{date}.json"
  - "Listmonk campaigns: lists som:info / som:trigger / som:test (tag ds-aa-som-floods; ids 122/123/124 as observed 2026-09-14, resolved by tag at runtime)"
  - "orphan branch `monitoring-status`: pages/monitoring/status.json + latest.png, pushed directly after each run"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/monitoring/", kind: status, title: "Somalia riverine flood trigger — live monitoring status"}
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/glofas-version/", kind: report, title: "GloFAS version switch — what v4 vs v5 does to the Deyr thresholds"}
dependencies:
  - "ocha-relay v0.3.0 (Listmonk), ocha-stratus (blob only), cdsapi, cfgrib + eccodes==2.47.0, jinja2; pinned in requirements-monitoring.txt"
  - "Secrets: org DSCI_AZ_BLOB_DEV_SAS(+_WRITE), DSCI_LISTMONK_API_URL->BASE_URL, DSCI_LISTMONK_API_USERNAME/KEY; repo GOOGLE_API_KEY, CDSAPI_KEY, CDSAPI_URL (EWDS)"
  - "Run-mode vars TEST_EMAIL / DRY_RUN (default true in code; prod = explicit false repo vars), SIMULATE_TRIGGER"
downstream:
  - "Email recipients on the Listmonk lists (soak: Tristan Downing; Pauline to be added)"
  - "Public status page (district map, window cards, chart, per-station tables) and the site landing page cards"
depends_on: [listmonk]
source_repo: ocha-dap/ds-aa-som-floods
source_branch: feat/monitoring
source_sha: e264ac1
code_ref:
  - .github/workflows/monitoring.yml
  - .github/workflows/deploy-pages.yml
  - pipelines/check_forecasts.py
  - pipelines/save_plots.py
  - pipelines/send_emails.py
  - pipelines/export_monitoring_status.py
  - pipelines/setup_som_listmonk_lists.py
  - src/monitoring/config.py
  - src/monitoring/etl.py
  - src/monitoring/evaluate.py
  - src/monitoring/thresholds.py
  - src/monitoring/thresholds.json
  - scripts/build_monitoring_thresholds.py
  - scripts/build_glofas_version_page.py
  - pages/monitoring/index.html
extra:
  design: "analysis/som-flooding-multisource.md — trigger definition (TRIGGER_CONFIG in src/constants.py: Gu on Google, Deyr on GloFAS; Juba 3 of 4 points, Shabelle 2 of 3 over own RP level on one forecast day; action leads 1-7, readiness GloFAS leads 8-12); this page is the ops runbook"
  glofas_version: "Design fitted Deyr levels on GloFAS v5 reanalysis assuming v5 was live. Verified 2026-09-14: operational = v4 (v4.5, 16 Apr 2026); v5 pre-operational on EWDS. Pipeline runs on v4-fitted levels (GLOFAS_OPERATIONAL in src/monitoring/config.py); both level sets frozen in thresholds.json. On v4 the adopted Deyr rules over-activate (envelope 1-in-1.9 vs 1-in-3.2) and never register Deyr 2006/2023 on the Shabelle — trigger revision pending, see /glofas-version/."
  monitoring_windows: "Open by calendar month (config.MONITORING_OPEN_MONTHS, decided 2026-09-15): Deyr Sep-Jan, Gu Feb-Jun. Every forecast valid day inside the open months counts toward the rule, although the thresholds are fitted on the Oct-Dec / Mar-May seasonal maxima. Jul-Aug: pipeline runs, page updates, no email."
  dollow: "The design's Dollow Google point hybas_1121038740 is the Dawa branch (31 m3/s mean) and is not served by the live Flood Hub API (404). Since 2026-09-15 Dollow reads hybas_1121039440, the Juba main stem 8 km ESE (142 m3/s mean; Spearman 0.86 vs the SWALIM Dollow gauge in Gu, same as the design point; Gu Juba activation years unchanged with any candidate — scripts/page_additions/dollow_proxy*.py on feat/multisource-trigger). Processed Google tables on blob rebuilt with it; the trigger pages still show the old gauge's Dollow numbers until rebuilt."
  email_cadence: "while a window is open: Monday informational + immediate on readiness/action; nothing when no window is open. Templates are content-only (the Listmonk base_campaign wrapper supplies header, contact and footer), Philippines-typhoon table style."
visibility: public
last_synced: "2026-09-15"
---

# Somalia riverine flood monitoring

> Runbook for the daily pipeline that applies the Somalia riverine flood trigger. Trigger design and evidence: [analysis/som-flooding-multisource](../analysis/som-flooding-multisource.md). The repo's `CLAUDE.md` is the code-adjacent runbook; this page is the hub summary.

## One-liner

*Daily 16:00 UTC GHA: GloFAS operational ensemble (EWDS) + Google Flood Hub at the seven Juba/Shabelle trigger points → the day's rows to blob → four river-season window rules (action leads 1–7 d, readiness GloFAS 8–12 d) → chart → Listmonk email while a window is open → status snapshot on the orphan `monitoring-status` branch → public status page 45 min later.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor Somalia riverine flooding | `.github/workflows/monitoring.yml` | cron `0 16 * * *` + dispatch (date, test_email, dry_run, simulate_trigger) | live once on `main` |
| Deploy pages site | `.github/workflows/deploy-pages.yml` | cron `45 16 * * *` + push (pages/**) + dispatch | live |

16:00 UTC is the first full hour after both feeds are in: the GloFAS 00Z run reaches EWDS between ~14:15 and ~15:30 UTC (observed 2026-09-14/15) and Google issues ~12:00–13:00 UTC. EWDS queueing makes the fetch take 5–15 min; if the day's issue is missing, `fetch_glofas` falls back to the previous day's.

## Inputs

- GloFAS `cems-glofas-forecast`, `system_version: operational`, `ensemble_perturbed_forecasts`, leads 24–288 h, one box [4.9, 41.9, 1.1, 45.7]; station values taken at the seven frozen 0.05° river cells (`src/monitoring/glofas_cells.json`).
- Google Flood Forecasting API, one `queryGaugeForecasts` call for the 7 HYBAS gauge ids (`src/constants.py`); latest issue per gauge. Returns issue−2…issue+5 days, so the action leg reads Google at leads 1–5. Ids the API stops serving are listed in `config.GOOGLE_NOT_SERVED` and probed one by one (empty since Dollow moved to the main-stem gauge).

## Steps

1. `check_forecasts.py` — version guard (EWDS legacy list must not contain `version_4*`; GRIB `generatingProcessIdentifier`/`backgroundProcess` must equal 5/21), fetch both products, write `monitoring/forecasts/<date>.parquet` (dev blob). Fails loudly (no email) on a version change unless `ALLOW_VERSION_MISMATCH=true`. Raw GRIB and Google JSON kept under `raw/`; a re-run reuses the GRIB already in blob.
2. `save_plots.py` — `evaluate.evaluate` (same-day votes per window on the ensemble median / deterministic value, every valid day inside the open window months) → chart (one panel per source the open season uses: GloFAS alone in Deyr, Google + GloFAS in Gu) → blob; the evaluation also goes to `monitoring/status/<date>.json`.
3. `send_emails.py` — Listmonk via ocha-relay; lists by tag; Monday informational or immediate readiness/action while any window is open; `[TEST]`/`[SIM]` tags per the run-mode flags.
4. `export_monitoring_status.py` — same evaluation on the latest day on blob → `status.json` (+ per-point series and levels) + `latest.png` → `monitoring-status` branch under `pages/monitoring/`; `deploy-pages.yml` overlays them into the Pages artifact.

## Outputs

Blob parquet/JSON/PNG per day, raw GRIB and Google JSON, Listmonk campaigns, the `monitoring-status` branch and the two public pages listed in the frontmatter. There is **no database table** (an early `projects.ds_aa_som_floods_monitoring` dev table from 2026-09-14 is orphaned).

## Dependencies

See frontmatter. `requirements-monitoring.txt` is the runner pin set (the analysis extras in `pyproject.toml` — geoglows → hydrostats — do not build on a clean Python 3.12 runner).

## Failure modes & debugging

- **Run fails on "EWDS now lists a version_4 entry"**: GloFAS v5 has gone operational. Flip `GLOFAS_OPERATIONAL` to `glofas_v5`, rebuild `/glofas-version/`, and take the Deyr rule question back to the working group (the v5 levels are the design levels).
- **Run fails on GRIB process ids**: same signal from the data side; confirm on EWDS before overriding.
- **GloFAS not available for today**: `fetch_glofas` falls back one day (`days_back` in the log). Two days missing = EWDS outage; re-run later via dispatch with `date`.
- **Google 404**: a gauge id disappeared from the live API. Add it to `config.GOOGLE_NOT_SERVED`; the run continues with the gauges served and the page/emails show "n of 7 reporting".
- **No email in season**: check `TEST_EMAIL`/`DRY_RUN` repo vars, then whether a window is open (`open_windows` in `status.json`; Jul–Aug none is), then Listmonk campaign history.
- **Status page stale but emails fine**: `deploy-pages.yml` is the only publisher; compare the page's `status.json` `generated_at` with the branch's.
- **Crons silently stopped**: GitHub disables schedules after 60 days of repo inactivity — `gh workflow list --all`.
- **Chart missing**: `chart_stale: true` keeps the previous PNG; `save_plots.py` step failed or ran in `DRY_RUN`.

## Gotchas

- The data plane is dev-stage blob regardless of the email flags; only routing follows `TEST_EMAIL`.
- Google always returns its current forecast: a re-run for a past `MONITORING_DATE` carries today's Google issue (visible in `issued_time`).
- `.env` at repo root is loaded explicitly by every pipeline script (stratus reads credentials at import time).
- The public page is a dev-stage data plane on a public site — nothing sensitive goes into `status.json`.
- Windows open by calendar month while thresholds are fitted on season maxima (see `monitoring_windows` above): a September forecast day is judged against the Oct–Dec 1-in-4 level.

## Downstream consumers

Recipients on the Listmonk lists; the public status page; the working group's pending decisions on the Deyr rules under GloFAS v4 (see `/glofas-version/`) and on the Dollow substitute point.
