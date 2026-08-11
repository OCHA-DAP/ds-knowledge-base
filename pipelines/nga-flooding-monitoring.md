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
inputs:
  - "CDS cems-glofas-forecast (operational ensemble, Wuroboki point, leads 1-13 d)"
  - "CDS cems-glofas-historical (version_4_0 intermediate reanalysis, Wuroboki point, walk-back -2..-7 d)"
  - "Google Flood Forecasting API gauges:queryGaugeForecasts (10 endorsed GRRR gauges, one call)"
  - "DB app.floodscan_exposure prod (per-LGA FloodScan x WorldPop exposure, from floodexposure-monitoring)"
outputs:
  - "DB projects.ds_aa_nga_flooding_monitoring dev (riverine forecasts; unique key monitoring_date/valid_date/src)"
  - "blob projects/ds-aa-nga-flooding/monitoring/{date}_{action}.png + flash_{date}_{triggered}.png (HDX-styled charts, dev)"
  - "Listmonk campaigns: riverine lists nga:info 113 / nga:trigger 114 / nga:test 115; flash lists nga-flash:info 118 / nga-flash:trigger 119 / nga-flash:test 120"
dependencies:
  - "ocha-relay @v0.3.0 (Listmonk client)"
  - "ocha-stratus, cfgrib, eccodes==2.47.0 (bundled libeccodes 2.48 — REQUIRED for post-GloFAS-v5 GRIBs)"
  - "Secrets: DSCI_AZ_BLOB_DEV_SAS(+_WRITE), DSCI_AZ_DB_DEV_*(riverine) / DSCI_AZ_DB_PROD_*(flash read), GOOGLE_API_KEY, CDSAPI_KEY/URL, DSCI_LISTMONK_API_URL->BASE_URL, DSCI_LISTMONK_API_USERNAME/KEY"
  - "vars: STAGE (prod = real lists; anything else = test lists + [TEST] banner)"
  - "upstream: floodexposure-monitoring chain must land the day's exposure before 01:30 UTC (flash has a freshness guard)"
downstream:
  - "Email recipients on the Listmonk lists (currently a two-person soak audience per stream, pending distribution-list migration)"
depends_on: [floodexposure-monitoring, listmonk]
source_repo: ocha-dap/ds-aa-nga-flooding
source_branch: main
source_sha: 60468c0
code_ref:
  - pipelines/check_forecasts.py
  - pipelines/save_plots.py
  - pipelines/send_emails.py
  - pipelines/monitor_flash_flood.py
  - pipelines/setup_nga_listmonk_lists.py
  - src/monitoring/etl.py
  - src/monitoring/flash.py
  - src/monitoring/plot.py
  - src/constants.py
extra:
  framework: "frameworks/nga-flooding/2026-06-18.md — trigger definitions and provenance live there; this page is the ops runbook"
  email_cadence: "weekly Monday informational per stream; immediate on trigger (both streams) and on flash approaching-threshold (>=80% of any LGA threshold)"
visibility: internal
last_synced: "2026-08-11"
---

# Nigeria Flooding Monitoring (2026 framework)

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am." Trigger design and provenance: [frameworks/nga-flooding/2026-06-18](../frameworks/nga-flooding/2026-06-18.md).

## One-liner

*Two daily GHA pipelines evaluate the 2026 Nigeria AA triggers — Adamawa riverine (GloFAS readiness + 10-gauge Google action) at 20:00 UTC, BAY-states flash flood (FloodScan exposure vs per-LGA thresholds) at 01:30 UTC — and email HDX-styled status updates via Listmonk.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor flooding (riverine) | `.github/workflows/monitoring.yml` | cron `0 20 * * *` | live |
| Monitor flash flooding | `.github/workflows/flash-monitoring.yml` | cron `30 1 * * *` | live |

The flash cron is deliberately placed after the `floodexposure-monitoring` chain (23:15 UTC cron; DB write normally done 23:40–23:52 UTC, worst observed ~01:10). There is no cross-repo event trigger — on the rare day the chain slips past 01:30, the flash run fails its freshness guard visibly; re-run via `workflow_dispatch` or let the next day self-correct.

## Steps

**Riverine** (`check_forecasts.py` → `save_plots.py` → `send_emails.py`):

1. Download GloFAS operational forecast (leads 1–13 d) at Wuroboki; walk back −2..−7 d for the latest available `version_4_0` intermediate reanalysis (missing reanalysis = warning, never fatal). Fetch all 10 GRRR gauges in one Google API call. Upsert to `projects.ds_aa_nga_flooding_monitoring` (dev).
2. Evaluate (`etl.evaluate_trigger`): action = ≥6/10 gauges over their per-gauge 4-yr RP thresholds on the same valid day; readiness = GloFAS forecast OR reanalysis > 3,132 m³/s. Chart to blob.
3. Email: action → `nga:trigger`; readiness → `nga:info`; Monday informational → `nga:info`. `STAGE != prod` → everything to `nga:test`.

**Flash** (`monitor_flash_flood.py`):

1. Read the 4 LGAs' exposure from `app.floodscan_exposure` (prod), strict 3-day rolling mean (matches the threshold derivation exactly — thresholds validated as ~7.75-yr empirical RP / 3-in-28-years each on this precise aggregation).
2. Freshness guard: latest `valid_date` must be ≥ run-date−2, else exit 1 with no email.
3. Email: any LGA over threshold → `nga-flash:trigger`; any LGA ≥80% → advisory to `nga-flash:info` (any day); Monday informational → `nga-flash:info`. `STAGE != prod` → `nga-flash:test`.

## When it breaks

- **Riverine run fails in CDS download**: check whether CEMS restructured the dataset again (the Aug-2026 GloFAS v5 rollout renamed params/variables on `cems-glofas-historical` and broke old requests with opaque 400s). The reanalysis is pinned to `version_4_0` for calibration consistency — when v4 intermediate production stops, or when `operational` flips to v5 on the forecast dataset, **the 3,132 m³/s readiness threshold needs re-derivation against v5 climatology** (it cannot be pinned on the forecast side).
- **GRIB decode errors** ("No final 7777", KeyError `gridType`): libeccodes too old for ECMWF's local-section template — the pip `eccodes==2.47.0` pin bundles libeccodes 2.48; don't downgrade. Segfault at interpreter exit *after* "rows saved" is a known linux teardown quirk, absorbed by `os._exit(0)` in `check_forecasts.py`.
- **Flash run fails the freshness guard**: check the `floodexposure-monitoring` Actions history — its chain is the sole data source.
- **No emails arriving**: check `STAGE` repo var (test vs prod lists), then Listmonk campaign history (instance in `infrastructure/comms-listmonk.md`). Sends are campaigns to lists resolved by tag — never hardcoded ids except in the docs above.
- **Crons silently stopped**: GitHub auto-disables schedules after 60 days of repo inactivity (`disabled_inactivity`) — this killed the 2025 pipeline from Dec 2025 to Aug 2026 unnoticed. `gh workflow list --all` shows it; `gh workflow enable <id>` fixes it.

## Gotchas

- The data plane is dev-stage regardless of `STAGE` (riverine DB + chart blobs); only email routing follows `STAGE`. Flash *reads* prod (`app.floodscan_exposure`) because that's where floodexposure-monitoring writes.
- `app.floodscan_exposure.adm_level` is TEXT — quote comparisons.
- Legacy blob distribution CSVs (`ds-aa-nga-flooding/email/*.csv`) are superseded by Listmonk; `setup_nga_listmonk_lists.py` migrates them into the riverine lists when the full audience onboards (`--dry-run` first). The flash audience is managed directly in Listmonk.
