---
content_type: pipeline
name: som-floods-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor Somalia riverine flooding", ref: ".github/workflows/monitoring.yml", schedule: "0 20 * * * (daily 20:00 UTC) + workflow_dispatch", status: live }
    - { name: "Deploy pages site (overlays monitoring status)", ref: ".github/workflows/deploy-pages.yml", schedule: "45 20 * * * + push to main (pages/**) + workflow_dispatch", status: live }
inputs:
  - "EWDS cems-glofas-forecast (operational ensemble, 50 perturbed members, days 1-12, one box over the 7 trigger cells)"
  - "Google Flood Forecasting API gauges:queryGaugeForecasts (6 live HYBAS gauges; Dollow's is not served)"
  - "EWDS cems-glofas-forecast form.json (system_version legacy list — the GloFAS version guard)"
outputs:
  - "DB projects.ds_aa_som_floods_monitoring dev (PK monitoring_date, source, station, valid_date; GloFAS rows carry ensemble median + p25/p75/min/max + model_version)"
  - "blob projects/ds-aa-som-floods/monitoring/{date}.png (daily chart, dev) + raw/glofas/monitoring/glofas_forecast_{date}.grib"
  - "Listmonk campaigns: lists som:info / som:trigger / som:test (tag ds-aa-som-floods; ids 122/123/124 as observed 2026-09-14, resolved by tag at runtime)"
  - "orphan branch `monitoring-status`: pages/monitoring/status.json + latest.png, pushed directly after each run"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/monitoring/", kind: status, title: "Somalia riverine flood trigger — live monitoring status"}
  - {url: "https://ocha-dap.github.io/ds-aa-som-floods/glofas-version/", kind: report, title: "GloFAS version switch — what v4 vs v5 does to the Deyr thresholds"}
dependencies:
  - "ocha-relay v0.3.0 (Listmonk), ocha-stratus, cdsapi, cfgrib + eccodes==2.47.0, jinja2; pinned in requirements-monitoring.txt"
  - "Secrets: org DSCI_AZ_BLOB_DEV_SAS(+_WRITE), DSCI_AZ_DB_DEV_*, DSCI_LISTMONK_API_URL->BASE_URL, DSCI_LISTMONK_API_USERNAME/KEY; repo GOOGLE_API_KEY, CDSAPI_KEY, CDSAPI_URL (EWDS)"
  - "Run-mode vars TEST_EMAIL / DRY_RUN (default true in code; prod = explicit false repo vars), SIMULATE_TRIGGER"
downstream:
  - "Email recipients on the Listmonk lists (soak: Tristan Downing; Pauline to be added)"
  - "Public status page and the analysis site landing page cards"
depends_on: [listmonk]
source_repo: ocha-dap/ds-aa-som-floods
source_branch: feat/monitoring
source_sha: 5d585e1
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
  email_cadence: "while a window is open (12 d before season start to season end): Monday informational + immediate on readiness/action; nothing out of season, pipeline still runs and page still updates"
visibility: public
last_synced: "2026-09-14"
---

# Somalia riverine flood monitoring

> Runbook for the daily pipeline that applies the Somalia riverine flood trigger. Trigger design and evidence: [analysis/som-flooding-multisource](../analysis/som-flooding-multisource.md). The repo's `CLAUDE.md` is the code-adjacent runbook; this page is the hub summary.

## One-liner

*Daily 20:00 UTC GHA: GloFAS operational ensemble (EWDS) + Google Flood Hub at the seven Juba/Shabelle trigger points → four river-season window rules (action leads 1–7 d, readiness GloFAS 8–12 d) → chart → Listmonk email in season → status snapshot on the orphan `monitoring-status` branch → public status page 45 min later.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor Somalia riverine flooding | `.github/workflows/monitoring.yml` | cron `0 20 * * *` + dispatch (date, test_email, dry_run, simulate_trigger) | live once on `main` |
| Deploy pages site | `.github/workflows/deploy-pages.yml` | cron `45 20 * * *` + push (pages/**) + dispatch | live |

20:00 UTC because the GloFAS 00Z run reaches EWDS by ~15:30 UTC and Google issues ~12:00–13:00 UTC. EWDS queueing makes the fetch take 5–15 min.

## Inputs

- GloFAS `cems-glofas-forecast`, `system_version: operational`, `ensemble_perturbed_forecasts`, leads 24–288 h, one box [4.9, 41.9, 1.1, 45.7]; station values taken at the seven frozen 0.05° river cells (`src/monitoring/glofas_cells.json`).
- Google Flood Forecasting API, one `queryGaugeForecasts` call for the 7 HYBAS gauge ids; latest issue per gauge. Returns issue−2…issue+5 days, so the action leg reads Google at leads 1–5.

## Steps

1. `check_forecasts.py` — version guard (EWDS legacy list must not contain `version_4*`; GRIB `generatingProcessIdentifier`/`backgroundProcess` must equal 5/21), fetch both products, upsert. Fails loudly (no email) on a version change unless `ALLOW_VERSION_MISMATCH=true`.
2. `save_plots.py` — `evaluate.evaluate` (same-day votes per window on the ensemble median / deterministic value, valid days inside the season months only) → 2×2 chart (rivers × products, each point as % of its own level) → blob.
3. `send_emails.py` — Listmonk via ocha-relay; lists by tag; Monday informational or immediate readiness/action while any window is open; `[TEST]`/`[SIM]` tags per the run-mode flags.
4. `export_monitoring_status.py` — same evaluation → `status.json` (+ per-point series and levels) + `latest.png` → `monitoring-status` branch under `pages/monitoring/`; `deploy-pages.yml` overlays them into the Pages artifact.

## Outputs

DB table, blob chart and raw GRIB, Listmonk campaigns, the `monitoring-status` branch and the two public pages listed in the frontmatter.

## Dependencies

See frontmatter. `requirements-monitoring.txt` is the runner pin set (the analysis extras in `pyproject.toml` — geoglows → hydrostats — do not build on a clean Python 3.12 runner).

## Failure modes & debugging

- **Run fails on "EWDS now lists a version_4 entry"**: GloFAS v5 has gone operational. Flip `GLOFAS_OPERATIONAL` to `glofas_v5`, rebuild `/glofas-version/`, and take the Deyr rule question back to the working group (the v5 levels are the design levels).
- **Run fails on GRIB process ids**: same signal from the data side; confirm on EWDS before overriding.
- **GloFAS not available for today**: `fetch_glofas` falls back one day (`days_back` in the log). Two days missing = EWDS outage; re-run later via dispatch with `date`.
- **Google 404**: a gauge id disappeared from the live API (Dollow's already has). The run continues with the gauges served; the page and emails show "n of 7 gauges".
- **No email in season**: check `TEST_EMAIL`/`DRY_RUN` repo vars, then whether a window is open (`open_windows` in `status.json`), then Listmonk campaign history.
- **Status page stale but emails fine**: `deploy-pages.yml` is the only publisher; compare the page's `status.json` `generated_at` with the branch's.
- **Crons silently stopped**: GitHub disables schedules after 60 days of repo inactivity — `gh workflow list --all`.
- **Chart missing**: `chart_stale: true` keeps the previous PNG; `save_plots.py` step failed or ran in `DRY_RUN`.

## Gotchas

- The data plane is dev-stage regardless of the email flags (DB + blob); only routing follows `TEST_EMAIL`.
- Google always returns its current forecast: a re-run for a past `MONITORING_DATE` carries today's Google issue (visible in `issued_time`).
- `.env` at repo root is loaded explicitly by every pipeline script (stratus reads DB credentials at import time).
- The public page is a dev-stage data plane on a public site — nothing sensitive goes into `status.json`.

## Downstream consumers

Recipients on the Listmonk lists; the public status page; the working group's pending decision on the Deyr rules under GloFAS v4 (see `/glofas-version/`).
