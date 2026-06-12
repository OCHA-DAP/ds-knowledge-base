---
content_type: pipeline
name: moz-cyclones-monitoring
type: monitoring
status: live
schedule: "0 * * * *"   # hourly + workflow_dispatch (RSMC publishes every 6h → most runs no-op)
deployment:
  platform: github-actions
  ref: .github/workflows/run_trigger_script.yml   # runs python main.py
  url: https://github.com/OCHA-DAP/ds-aa-moz-cyclones-monitoring
  resource_group: n/a
inputs:
  - RSMC La Réunion TC track JSON (Météo-France FTP)
  - IMERG daily rainfall (blob, via ocha-stratus)
  - Mozambique CODAB (files/moz_adm.shp.zip)
  - distribution_list.csv (blob)
outputs:
  - per-storm forecast/cone/landfall JSON + affected-districts CSV
  - map + rainfall map PNGs
  - HTML info/alert emails (SMTP / AWS SES)
  - commits forecast_updates.csv state back to repo
dependencies: [ocha-stratus==0.1.7, Meteo-France FTP, Azure Blob+Postgres, AWS SES SMTP, geopandas/shapely/rioxarray]
downstream: [moz-cyclones framework — Readiness + Observational windows]
source_repo: ocha-dap/ds-aa-moz-cyclones-monitoring
source_branch: exposure-plots   # NOT main
source_sha: 1055f33
code_ref:
  - main.py                    # orchestration: FTP → parse → wind buffers → landfall → exposed area → activation → email
  - src/exposed_area.py        # clip_uncertainty_cone, create_exposed_area
  - src/activation.py          # get_monitoring_status (OLD two-threshold design)
  - src/monitor_imerg.py       # RAIN_THRESH=120
visibility: internal
last_synced: 2026-06-12
---

# Mozambique cyclone monitoring

## One-liner
Hourly: poll RSMC La Réunion forecasts → build wind buffers + truncate the uncertainty cone at the 119 km/h contour → compute exposed area over coastal provinces → set activation status → email info/alerts. Operates the **Readiness + Observational** windows of the [moz-cyclones framework](../frameworks/moz-cyclones/2026-01-09.md). (The **Action** trigger runs separately in INAM's PRISM.)

## Schedule / trigger
GitHub Actions cron `0 * * * *` (hourly) + `workflow_dispatch`, `main` only. RSMC publishes every 6h, so most hourly runs find no new forecast and exit early.

## Inputs
RSMC La Réunion track JSON (Météo-France FTP); IMERG rainfall (blob); Mozambique CODAB ADM1/ADM2; distribution list CSV.

## Steps
FTP poll → parse track + wind quadrants → wind buffers → landfall detection → clip uncertainty cone to 119 km/h contour → exposed area vs coastal provinces → activation status → save JSON/CSV + plots → email.

## Outputs
Per-storm JSON (forecast/cone/landfall/status), affected-districts CSV, map + rainfall PNGs, HTML emails via AWS SES; commits `forecast_updates.csv` state back to the repo.

## Dependencies
ocha-stratus 0.1.7 (blob/DB), Météo-France FTP (single source of truth), Azure Blob + Postgres, AWS SES SMTP, geo stack.

## Failure modes & debugging
- On any exception, emails a hardcoded failure notice to **one** recipient (person-dependent — fragile).
- FTP credential/availability failure blocks all monitoring (single source).
- Hourly-vs-6-hourly → many no-op runs; `track_processed` flag dedupes.
- IMERG ~24h latency → proceeds with available days.
- **Activation logic encodes the OLD two-threshold (48/64 kt) + 72h scheme and omits Maputo City** — live alerts may not match the 2026 single-threshold / 8-province / 96–6h framework. See framework discrepancies.

## Downstream consumers
OCHA/CHD distribution list (Readiness + Observational) → RC/HC, HCT, ICCG, CERF Secretariat, OCHA Mozambique/ROSEA. Action trigger downstream owned separately by INAM/PRISM → INGD/CTGD.
