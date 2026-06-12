---
content_type: pipeline
name: storms-pipeline
type: dataset-ingest   # + exposure; the tropical-storm data backbone
status: live
schedule: multiple   # NHC every 3h (:00/:30); GDACS-ADAM every 3h; IBTrACS/ECMWF on-demand
deployment:
  platform: databricks-job
  ref: bundle "ds-storms-pipeline" → jobs "NHC Pipeline" (nhc_pipeline) + "GDACS/ADAM Pipeline" (gdacs_adam_pipeline)
  url: workspace adb-6009046713167663 (Azure)
  resource_group: n/a   # Databricks; secrets from `dsci` scope; PGSSLMODE=require
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

## Jobs & schedule
One repo, **multiple Databricks jobs** (Databricks Asset Bundle):

| job | schedule (UTC) | tasks |
|---|---|---|
| NHC Pipeline | `0 0,30 0/3 * * ?` (every 3h; :30 = WSP late-arrival fill) | etl → tracks_processing → {tracks_exposure, wsp_processing → wsp_exposure} |
| GDACS/ADAM Pipeline | `0 0 0/3 * * ?` (every 3h) | gdacs → adam → match |
| IBTrACS / ECMWF | on-demand / backfill | `run_pipeline.py ibtracs` / `ecmwf` subcommands |

## Steps
Per source: raw ingest (→ blob + `*_storms`/`*_tracks_geo`) → wind buffers (union of per-point R34/R50/R64 quadrant discs, one polygon per storm×wind-threshold) → exposure (WorldPop × FieldMaps admin, via `exactextract`). `fcastonly` = forecast minus cumulative observed swath. The `match` task links sources via `storm_id_lookup`.

## Inputs / Outputs
See frontmatter. Note `admin_population` and `*_fm_lookup` are **static, offline-built** production tables (not produced on the schedule). Pipeline **reads PROD, writes the target env** (default dev) — inputs/outputs can hit different environments via `--mode`.

## Dependencies
ocha-stratus (all DB/blob I/O, `postgres_upsert`), ocha-lens 0.5.1 (wind-buffer math, datasources, `match_wsp_to_tracks`), geo stack. `dsci` Databricks secret scope.

## Failure modes & debugging
- Logs in Databricks job run UI (one `run_pipeline.py` invocation per task; failures raise, no silent suppression).
- Idempotent via `postgres_upsert` + named constraints; resumable without `--overwrite`. Backfill via `--issued-time/--since/--until/--overwrite/--basin`.
- Sequencing: `fcastonly` buffers need fcast+obsv populated for the same `issued_time`; WSP zip publishes after :00 → the :30 NHC tick retries.
- Known gaps: WSP polygons truncated at −180 (dateline); pre-2002 NHC / pre-2004 IBTrACS wind-radii sparse; KIR dateline bbox breaks clip.
- **Deployed job runs `git_source` branch var (default `main`), so what's checked out locally ≠ what the scheduled job runs.**

## Key decisions & rationale
DBX is a thin wrapper (`databricks/dispatch.py`) over plain-Python `run_pipeline.py` — swappable for Airflow/GHA/cron. Antimeridian handled in ocha-lens (buffers split at the dateline) with a defensive net in `nhc.py`. Read-PROD/write-dev decouples prod source data from experimentation. FieldMaps mirrored to same-region blob (~50× faster than upstream egress). Three explicit code tiers (production / offline-build / review-only) with per-module banners.
