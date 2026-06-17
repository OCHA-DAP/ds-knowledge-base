---
content_type: pipeline
name: storms-pipeline
type: dataset-ingest   # + exposure; the tropical-storm data backbone
status: live
deployment:
  platform: databricks-job
  resource_group: n/a   # workspace adb-6009046713167663; secrets from `dsci` scope; PGSSLMODE=require
  jobs:
    - { name: NHC Pipeline, ref: nhc_pipeline, schedule: "0 0,30 0/3 * * ?", status: live }
    - { name: GDACS/ADAM Pipeline, ref: gdacs_adam_pipeline, schedule: "0 0 0/3 * * ?", status: live }
    - { name: Run IBTrACS, ref: "638351145729392", schedule: "27 0 16 * * ?", status: live }
    - { name: Run ECMWF Storms, ref: "1053499360455948", schedule: "46 0 22 * * ?", status: live }
inputs:
  - NHC CurrentStorms JSON + forecast advisories + WSP 5km shapefile (NA+EP basins)
  - IBTrACS v04r01 (NOAA, all basins)
  - ECMWF ensemble cyclone tracks
  - GDACS events + ADAM exposure CSVs
  - WorldPop COG (raster blob) + FieldMaps admin boundaries (mirrored to blob)
outputs:   # Postgres `storms` schema, EPSG:4326 (~25 tables)
  - "ibtracs_*: storms, tracks_geo, wind_buffers, wind_exposure"
  - "nhc_*: storms, tracks_geo, tracks_{fcast,obsv,fcastonly}_buffers + _exposure, wsp_polygon_{raw,matched,fcastonly}, wsp_exposure, wsp_fcastonly_exposure"
  - "ecmwf_*: storms, tracks_geo;  gdacs_exposure, adam_exposure (+ *_fm_lookup)"
  - "storm_id_lookup (cross-source identity), admin_population (WorldPop denominator)"
dependencies: [ocha-stratus, ocha-lens==0.5.1, geopandas, rioxarray, exactextract, antimeridian, databricks-sdk]
downstream: [storms-alerts, chd-ds-storms-explore apps, AA frameworks joining via storm_id_lookup]
source_repo: ocha-dap/ds-storms-pipeline
source_branch: add-cluster-lens-cleanup-script   # tip; main one commit behind (2026-06-09). Deployed job uses git_source var default `main`.
source_sha: 76dee66
code_ref:
  - run_pipeline.py            # single argparse CLI, all subcommands
  - databricks.yml             # bundle: both jobs, crons, clusters, secrets
  - src/pipelines/{ibtracs,nhc,ecmwf,gdacs,adam,match}.py
  - src/utils/exposure.py      # WorldPop + FieldMaps + calculate_exposure
  - src/schemas/sql/*.sql      # DDL for all tables
visibility: internal
last_synced: 2026-06-12
---

# Storms pipeline (data backbone)

## One-liner
The tropical-storm data backbone: ingests IBTrACS / NHC / ECMWF / GDACS-ADAM, computes wind buffers and population exposure, and writes ~25 tables to the Postgres `storms` schema. Standalone (not tied to one framework) — its tables feed [storms-alerts](storms-alerts.md), the explore apps, and AA frameworks.

> **The repo is the runbook.** This page is the cross-portfolio *summary* — what it is, how its jobs fit together, what depends on it. The full operational detail (step-by-step, exact CLI flags, every failure mode) is the source of truth in the [`ds-storms-pipeline` README](https://github.com/OCHA-DAP/ds-storms-pipeline#readme), kept next to the code; this page doesn't restate it.

## Jobs & schedule
One repo, **multiple Databricks jobs** (Databricks Asset Bundle):

| job | schedule (UTC) | tasks |
|---|---|---|
| NHC Pipeline | `0 0,30 0/3 * * ?` (every 3h; :30 = WSP late-arrival fill) | etl → tracks_processing → {tracks_exposure, wsp_processing → wsp_exposure} |
| GDACS/ADAM Pipeline | `0 0 0/3 * * ?` (every 3h) | gdacs → adam → match |
| IBTrACS / ECMWF | on-demand / backfill | `run_pipeline.py ibtracs` / `ecmwf` subcommands |

## Shape (one line per source)
Per source: raw ingest → wind buffers (union of per-point R34/R50/R64 quadrant discs, one polygon per storm×wind-threshold) → exposure (WorldPop × FieldMaps admin). The `match` task links sources via `storm_id_lookup`. Inputs/outputs are in the frontmatter; the **DDL, exact transforms, and CLI** live in the repo (`src/schemas/sql/`, `run_pipeline.py`).

## Orientation gotchas (the rest is in the README)
A few facts you need *before* reading the repo — full backfill flags, sequencing, and known data gaps are in the [README](https://github.com/OCHA-DAP/ds-storms-pipeline#readme):

- **Reads PROD, writes the target env** (default dev) via `--mode` — source data and outputs can be in different environments.
- `admin_population` and `*_fm_lookup` are **static, offline-built** tables, not produced on the schedule.
- **The deployed job runs the `git_source` branch var (default `main`)** — what's checked out locally ≠ what the scheduled job runs.

## Key decisions & rationale
DBX is a thin wrapper (`databricks/dispatch.py`) over plain-Python `run_pipeline.py` — swappable for Airflow/GHA/cron. Antimeridian handled in ocha-lens (buffers split at the dateline) with a defensive net in `nhc.py`. Read-PROD/write-dev decouples prod source data from experimentation. FieldMaps mirrored to same-region blob (~50× faster than upstream egress). Three explicit code tiers (production / offline-build / review-only) with per-module banners.
