---
content_type: pipeline
name: storms-pipeline
type: dataset-ingest   # + exposure; the tropical-storm data backbone
status: live
deployment:
  platform: databricks-job
  resource_group: n/a   # workspace adb-6009046713167663; secrets from `dsci` scope; PGSSLMODE=require
  jobs:
    - { name: NHC Pipeline, ref: "959161297191654", schedule: "0 0,30 0/3 * * ?", status: live }
    - { name: GDACS/ADAM Pipeline, ref: "197203772269744", schedule: "0 0 0/3 * * ?", status: live }
    - { name: "Run NHC (legacy, pre-DAB)", ref: "266763033249426", schedule: "every 3h (not in databricks.yml)", status: paused }
    - { name: Run IBTrACS, ref: "638351145729392", schedule: "daily 27 0 16 * * ? (not in databricks.yml)", status: live }
    - { name: Run ECMWF Storms, ref: "1053499360455948", schedule: "daily 46 0 22 * * ? (not in databricks.yml)", status: live }
inputs:
  - NHC CurrentStorms JSON + forecast advisories + WSP 5km shapefile (NA+EP basins)
  - IBTrACS v04r01 (NOAA, all basins)
  - ECMWF ensemble cyclone tracks (via ocha-lens)
  - GDACS events + ADAM (WFP) exposure CSVs (NOAA/JTWC source filter)
  - WorldPop COG (raster blob, global 1km pop count) + FieldMaps admin boundaries (mirrored to `global` blob container)
outputs:   # Postgres `storms` schema, EPSG:4326 (~25 tables)
  - "storms.ibtracs_storms, storms.ibtracs_tracks_geo, storms.ibtracs_wind_buffers, storms.ibtracs_wind_exposure"
  - "storms.nhc_storms, storms.nhc_tracks_geo"
  - "storms.nhc_tracks_{fcast,obsv,fcastonly}_buffers + _exposure"
  - "storms.nhc_wsp_polygon_{raw,matched}, storms.nhc_wsp_fcastonly_polygon, storms.nhc_wsp_exposure, storms.nhc_wsp_fcastonly_exposure"
  - "storms.ecmwf_storms, storms.ecmwf_tracks_geo"
  - "storms.gdacs_exposure, storms.adam_exposure (+ *_fm_lookup crosswalks)"
  - "storms.storm_id_lookup (cross-source identity: gdacs_eventid <-> atcf_id), storms.admin_population (WorldPop denominator, static)"
dependencies: [ocha-stratus, ocha-lens==0.5.1, geopandas, rioxarray, rasterio, exactextract, antimeridian, databricks-sdk, geoalchemy2]
downstream: [storms-alerts, chd-ds-storms-explore app, hti-hurricanes framework (2026-06-09 wind-exposure trigger redesign), cub-hurricanes framework (2026-06-17 wind-exposure trigger redesign), "Cuba Hurricane Forecast/Observational Monitor (ds-aa-cub-hurricanes; fire-and-forget trigger)", AA frameworks joining via storm_id_lookup]
depends_on:
  - "dbx-job-compute"
source_repo: ocha-dap/ds-storms-pipeline
source_branch: main
source_sha: de2941d
code_ref:
  - run_pipeline.py                    # single argparse CLI, all subcommands
  - databricks.yml                     # bundle: nhc_pipeline + gdacs_adam_pipeline, crons, clusters, secrets
  - databricks/dispatch.py             # DBX->CLI dispatcher, composite expansion, task-value passing
  - databricks/trigger_job.py          # fire-and-forget Cuba Forecast Monitor kick
  - src/pipelines/{ibtracs,nhc,ecmwf,gdacs,adam,match}.py
  - src/utils/exposure.py              # WorldPop + FieldMaps loaders, exposure session, calculate_exposure
  - src/schemas/sql/*.sql              # DDL for all tables
  - config/adm_level_config.toml       # per-ISO3 FieldMaps<->GADM/GDACS/ADAM admin-level crosswalk overrides
extra: {}
visibility: internal
last_synced: "2026-07-02"
---

# Storms pipeline (data backbone)

## One-liner
The tropical-storm data backbone: ingests IBTrACS / NHC / ECMWF / GDACS-ADAM, computes wind buffers and population exposure, and writes ~25 tables to the Postgres `storms` schema. Standalone (not tied to one framework) — its tables feed [storms-alerts](storms-alerts.md), the explore apps, and AA frameworks (e.g. the Haiti and Cuba hurricanes wind-exposure triggers).

> **The repo is the runbook.** This page is the cross-portfolio *summary*. The full operational detail (step-by-step, exact CLI flags, DB schema, every known limitation) is the source of truth in the [`ds-storms-pipeline` README](https://github.com/OCHA-DAP/ds-storms-pipeline#readme) and [`databricks/README.md`](https://github.com/OCHA-DAP/ds-storms-pipeline/blob/main/databricks/README.md); this page doesn't restate it.

## Jobs & schedule
One repo, **two jobs defined in the Databricks Asset Bundle** (`databricks.yml`) — `nhc_pipeline` and `gdacs_adam_pipeline` — plus **three older jobs that exist in the workspace but are NOT in the bundle's IaC** (created before/outside the DAB migration; their schedule/config can't be verified from the repo, only from the live registry).

| job | ref | schedule | status |
|---|---|---|---|
| NHC Pipeline (bundle) | `dbx:959161297191654` | `0 0,30 0/3 * * ?` UTC — every 3h; the `:30` run is a WSP late-arrival fill (stages short-circuit on an already-present `issued_time`) | live, but **writing the DEV data-plane** (`mode=dev` cutover — see gotchas) |
| GDACS/ADAM Pipeline (bundle) | `dbx:197203772269744` | `0 0 0/3 * * ?` UTC — every 3h, matches NHC cadence | live, **`mode=dev`** cutover |
| Run NHC (legacy, pre-DAB) | `dbx:266763033249426` | every ~3h (not in `databricks.yml`) | **paused** — writes `storms.nhc_storms`/`nhc_tracks_geo` at `mode=prod` when unpaused, but hasn't run in ~479h |
| Run IBTrACS | `dbx:638351145729392` | daily, `27 0 16 * * ?` (not in `databricks.yml`) | live schedule, but **failing every run** (`INTERNAL_ERROR`), no recorded success |
| Run ECMWF Storms | `dbx:1053499360455948` | daily, `46 0 22 * * ?` (not in `databricks.yml`) | live schedule, but **failing every run**, no recorded success |

IBTrACS and ECMWF archive/backfill runs can also be driven on-demand via `run_pipeline.py ibtracs` / `ecmwf` locally or from any cluster — the two failing scheduled jobs above are the only automation for them.

## Inputs
- **NHC**: live `CurrentStorms.json` + forecast advisory text + the WSP (wind speed probability) 5km shapefile, NA + EP basins only. A frozen sample JSON (`--sample-json`) exists for end-to-end smoke tests.
- **IBTrACS** v04r01 (NOAA), all basins — historical best-track archive, fetched via `ocha-lens`.
- **ECMWF** ensemble cyclone tracks, via `ocha-lens`.
- **GDACS** events + **ADAM** (WFP) admin-level exposure CSVs, NOAA/JTWC source filter, current (rolling window) or archive (date-range) mode.
- **WorldPop** global 1km population COG (`worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif`, blob) and **FieldMaps** adm0/adm1 boundaries, mirrored to the `global` blob container (~50x faster than fetching the 1.4GB upstream parquet over DBX egress; see [`scripts/mirror_fieldmaps_to_blob.py`](https://github.com/OCHA-DAP/ds-storms-pipeline)).
- `config/adm_level_config.toml` — per-ISO3 hand-curated crosswalk overrides where FieldMaps/GADM/GDACS/ADAM disagree on what "admin 1" means (used by the offline FM-lookup builders, not the realtime path).

## Steps
Per source, the shape is: raw ingest → wind buffers (union of per-point R34/R50/R64 quadrant discs, one polygon per storm x wind-threshold) → population exposure (WorldPop x FieldMaps admin, `exactextract`/`rioxarray`). The `match` task links GDACS events to NHC's `atcf_id` via `ocha_lens.datasources.gdacs.match_to_atcf`, writing `storm_id_lookup`.

The NHC realtime cascade (the bundle's `nhc_pipeline` job) is 5 chained tasks dispatched through `databricks/dispatch.py`: `etl` → `tracks_processing` (fcast/obsv/fcastonly buffers) → `{tracks_exposure, wsp_processing → wsp_exposure}`. A leaf task, `trigger_cuba_forecast`, fires right after `etl` to fire-and-forget kick the Cuba Hurricane Forecast Monitor job (never fails the run; see Downstream). The GDACS/ADAM job is 3 chained tasks (`gdacs` → `adam` → `match`) via `databricks/dispatch_gdacs_adam.py`. Both dispatchers just build a `python run_pipeline.py <subcommand> …` argv and shell out — DBX is a thin wrapper, swappable for another orchestrator. Exact transforms, DDL and the full CLI surface (30+ subcommands) live in the repo (`src/schemas/sql/`, `run_pipeline.py`, `databricks/README.md`).

## Outputs
All tables live in the Postgres `storms` schema, EPSG:4326 (see frontmatter `outputs` for the full table list). Highlights: `nhc_tracks_{fcast,obsv,fcastonly}_exposure` and `ibtracs_wind_exposure` are what the hurricane wind-exposure triggers key off — hti-hurricanes 2026-06-09 uses `nhc_tracks_fcastonly_exposure` + `nhc_tracks_obsv_exposure`, and cub-hurricanes 2026-06-17 uses `nhc_tracks_fcast_exposure` + `nhc_tracks_obsv_exposure` + `ibtracs_wind_exposure`; `admin_population` is the static WorldPop-per-admin-unit denominator (recomputed on demand via `scripts/compute_admin_population.py`, not on the schedule); `*_fm_lookup` crosswalks are static, offline-built (`scripts/build_{gdacs,adam}_fm_lookup.py`), not produced on the schedule either.

## Dependencies
`ocha-stratus` (blob + DB), `ocha-lens==0.5.1` (IBTrACS/ECMWF/GDACS/ADAM source adapters + `match_wsp_to_tracks`/`match_to_atcf`), `geopandas`/`rioxarray`/`rasterio`/`exactextract` (raster exposure), `antimeridian` (dateline-safe buffers, with a defensive net in `nhc.py`), `databricks-sdk` (the DBX-only `trigger_job.py`). Secrets come from the `dsci` Databricks secret scope (DB + blob creds for both dev and prod, injected by the Job Compute policy `000C79D951EAF0D6`); `PGSSLMODE=require`. No Listmonk/email — this pipeline only writes tables; alerting is [storms-alerts](storms-alerts.md)'s job.

## Failure modes & debugging
- **Two scheduled jobs are down with no code fix available in this repo**: `Run IBTrACS` (`dbx:638351145729392`) and `Run ECMWF Storms` (`dbx:1053499360455948`) are `INTERNAL_ERROR`-failing on every run with no recorded success, and — critically — **neither is defined in `databricks.yml`**. They were created directly in the workspace outside the bundle's IaC, so there's no git history or config to diff against; fixing them means first finding what they actually run (check the job's task config in the Databricks UI/`jobs get <job_id>`), then deciding whether to bring them into the bundle.
- **The bundle's `nhc_pipeline`/`gdacs_adam_pipeline` prod deployment writes the DEV data-plane.** `databricks.yml`'s `prod` target sets `variables.mode: dev` with an explicit `TEMPORARY` comment — "flip to prod once we're ready to write prod tables." Until that flip, `storms.*` prod rows are **not** being refreshed by these two jobs; whatever consumes prod is stale or reading dev instead.
- **A separate legacy job, `Run NHC` (`dbx:266763033249426`), is the one actually tagged/watched at `mode=prod`** for `storms.nhc_storms`/`nhc_tracks_geo` — and it's **paused** (no run in ~479h). It predates the DAB and isn't in `databricks.yml`.
- **The real intended prod NHC writer may not even be this repo**: per `docs/DESIGN.md` D43, the GitHub Actions workflow in the separate `ds-nhc-forecast` repo is the pipeline actually meant to be the prod NHC data source, and it's been failing since 2026-06-08. Cross-check [`pipeline-registry.md`](../infrastructure/pipeline-registry.md) before assuming this repo's NHC job is "the" NHC pipeline.
- **Reads PROD, writes the target env** (`--mode`, default `dev`) — source data and outputs can be in different environments for any manual/local run; always check which `--mode` you passed before trusting a row count.
- **`nhc-scrub`** exists to delete test/sample rows across every NHC table by `atcf_id`/`issued_time` — use `--dry-run` first.
- **WSP polygons truncated at -180°** (upstream NHC 5km shapefile wraparound is lopped off at the antimeridian; only matters for storms crossing ±180°, outside current NA+EP coverage) and **pre-2002 (NHC) / pre-2004 (IBTrACS) wind-radii gaps** (buffers thin/missing for older storms) are known, accepted limitations — not bugs to chase.
- **KIR (Kiribati) exposure is wrong**: its bbox spans ~351° across the dateline with no polygon vertex at ±180°, so `rio.clip`'s pixel window misses the islands.
- Full failure-mode detail (env-var footguns, DBX-vs-local divergence checks, composite-subcommand quirks) is in `databricks/README.md`'s "Verifying DBX and local runs agree" section — start there before debugging a DBX-only discrepancy.

## Downstream consumers
- [storms-alerts](storms-alerts.md) — email alerting off this pipeline's exposure tables (runs on its own dev-mode/personal-cluster job, `Storm Alert` `dbx:500881901438881`).
- `chd-ds-storms-explore` app (Azure) — interactive explore surface, no dedicated KB page yet.
- **hti-hurricanes** framework — the 2026-06-09 wind-exposure trigger redesign (the new Haiti trigger) depends hard on `storms.nhc_tracks_fcastonly_exposure` and `storms.nhc_tracks_obsv_exposure` (HTI-filtered, dev DB); see [frameworks/hti-hurricanes/2026-06-09](../frameworks/hti-hurricanes/2026-06-09.md).
- **cub-hurricanes** framework — the in-development 2026 trigger redesign reads `storms.nhc_tracks_fcast_exposure`, `storms.nhc_tracks_obsv_exposure` and `storms.ibtracs_wind_exposure` (CUB-filtered, dev DB) for its wind-exposure trigger; per maintainer (@t-downing, PR #149) the finalized revised trigger **will** keep this dependency. Still analysis-only (the `wsp_trigger.py` marimo exploration app), not yet wired into the live monitoring pipeline; see [frameworks/cub-hurricanes/2026-06-17](../frameworks/cub-hurricanes/2026-06-17.md).
- **Cuba Hurricane Forecast Monitor** (`ds-aa-cub-hurricanes`) — fired fire-and-forget after every `nhc_pipeline` `etl` task (skipped on the `:30` WSP-retry run); isolated by design so a trigger failure never fails the NHC run.
- Any AA framework joining exposure/track tables via `storm_id_lookup` (GDACS<->NHC identity resolution).

<!-- TODO: chd-ds-storms-explore has no apps/ page yet — add one if it becomes a dependency target for other work. -->
