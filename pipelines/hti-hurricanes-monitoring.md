---
content_type: pipeline
name: hti-hurricanes-monitoring
type: monitoring
status: live
deployment:
  platform: databricks-job
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - { name: "HTI Hurricane Monitoring", ref: "databricks.yml (bundle ds-aa-hti-hurricanes; dbx:586426884912849)", schedule: "0 50 3,9,15,21 * * ? UTC — 50 min after each NHC advisory", status: live }
    - { name: run_update_chirps_gefs, ref: .github/workflows/run_update_chirps_gefs.yml, schedule: "50 8 * * *", status: live }
    - { name: keep_awake, ref: .github/workflows/keep_awake.yml, schedule: "0 12 * * 1 (weekly, pushes an empty commit to the `keep-awake` branch)", status: live }
    - { name: "HTI DGPC Rainfall Analysis", ref: "databricks.yml (bundle resource dgpc_rain; dbx:700734159677972)", schedule: "manual (no cron) — analysis backfill, not a monitor", status: live }
inputs:
  - "DB (dev stage): storms.nhc_tracks_geo — NHC track points + quadrant wind radii"
  - "DB (dev stage): storms.nhc_tracks_obsv_exposure / nhc_tracks_obsv_buffers — observed swath exposure"
  - "DB (dev stage): storms.nhc_tracks_fcastonly_exposure / nhc_tracks_fcast_buffers — full-horizon forecast exposure + buffers (leadtime-capped in-repo for 72h/120h)"
  - "DB (dev stage): storms.nhc_wsp_fcastonly_exposure / nhc_wsp_fcastonly_polygon — WSP probabilistic bands (email chart + map)"
  - "DB (dev stage): storms.admin_population, storms.nhc_storms / storms.ibtracs_storms"
  - "DB (prod): public.imerg — observed daily national-mean rainfall"
  - "NASA CMR + GES DISC OPeNDAP (IMERG half-hourly, Earthdata-authenticated) — DGPC sub-daily rain analysis only"
  - "Blob (projects): ds-aa-hti-hurricanes/processed/chirps/gefs/hti — CHIRPS-GEFS national-mean daily (CHIRPS3 c3g datastream since 2026-07-01)"
  - "Blob (global): fieldmaps/edge-matched/humanitarian/intl/adm0/HTI.parquet — boundary for exposure ONLY (matches storms-pipeline)"
  - "Blob (raster): worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif"
  - "Blob (projects): ds-aa-hti-hurricanes/raw/codab/hti.shp.zip — repo CODAB (adm0/adm1, from data.fieldmaps.io), used for rain masks, email maps and DGPC department stats"
outputs:
  - "blob monitoring records: ds-aa-hti-hurricanes/monitoring/hti_fcast_monitoring_v2.parquet, hti_obsv_monitoring_v2.parquet (v1 files frozen for the historical record / Dash app)"
  - "blob: ds-aa-hti-hurricanes/email/email_record_v2.csv — one row per email sent"
  - "blob: ds-aa-hti-hurricanes/processed/dgpc/rain_stats.parquet + imerg_hh/*.nc (cached IMERG windows) — DGPC rainfall analysis, manual Databricks job only"
  - "blob: ds-aa-hti-hurricanes/processed/dgpc/storm_set.parquet, fcast_wind_by_issuance.parquet, obsv_wind.parquet — DGPC wind analysis, run locally (pipelines/run_dgpc_wind.py)"
  - "GitHub Pages: ocha-dap.github.io/ds-aa-hti-hurricanes/dgpc-alertes.html — rendered by pipelines/build_dgpc_page.py"
  - "Listmonk campaigns: info list 116 (AA Haïti ouragans - informations), trigger list 117 (déclencheurs); TEST_EMAIL=True routes to internal test list 110"
dependencies: [Azure Postgres (storms dev + imerg prod), Azure Blob, Listmonk (ocha-relay), "NASA Earthdata (CMR + GES DISC OPeNDAP; IMERG_USERNAME/IMERG_PASSWORD from the dsci secret scope)", Databricks Job Compute (policy 000C79D951EAF0D6), ds-storms-pipeline (upstream)]
downstream: [hti-hurricanes framework; chd-ds-aa-hti-hurricanes-app]
depends_on: [storms-pipeline, imerg, listmonk]
source_repo: ocha-dap/ds-aa-hti-hurricanes
source_branch: main
source_sha: 3da8a7b
code_ref:
  - pipelines/monitor.py
  - src/constants.py
  - src/monitoring/monitoring_utils.py
  - src/monitoring/exposure.py
  - src/email/
  - src/dgpc/
  - databricks.yml
extra: {}
visibility: internal
last_synced: 2026-09-02
---

# Haiti hurricanes monitoring

## One-liner

Four times daily (:50, after `ds-storms-pipeline` lands each NHC advisory): evaluate the 2026 trigger — Mobilisation (≤120 h) / Action (≤72 h) fire on forecast 2-day rain ≥68 mm OR >0 people exposed to ≥64 kt forecast winds; Réponse précoce (obsv) fires on observed rain ≥57 mm OR >0 observed 64 kt exposure — and send French Listmonk emails (info every advisory while a storm is within 1 000 km; one trigger email per storm per stage). Neither forecast stage can fire inside the 48 h lead-time cutoff (`LT_CUTOFF_HRS`). **Folded into the [hti-hurricanes framework repo](../frameworks/hti-hurricanes/2026-06-09.md).** Replaced the v1 GHA/SES system on 2026-08-10; live to the real Listmonk lists since 2026-08-11 (framework endorsement pending — README still carries a "STATUS: PENDING ENDORSEMENT" badge).

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| HTI Hurricane Monitoring | Databricks job `dbx:586426884912849` (bundle `databricks.yml`, resource `hti_monitoring`, `source: GIT` on `main`) | `0 50 3,9,15,21 * * ?` UTC | live |
| run_update_chirps_gefs | `.github/workflows/run_update_chirps_gefs.yml` | `50 8 * * *` UTC + `workflow_dispatch` | live |
| keep_awake | `.github/workflows/keep_awake.yml` | `0 12 * * 1` (empty commit to `keep-awake` branch, weekly) | live — **failing since 2026-08-17** (see below) |
| HTI DGPC Rainfall Analysis | Databricks job `dbx:700734159677972` (bundle resource `dgpc_rain`) | manual only (`databricks bundle run dgpc_rain`); `timeout_seconds: 21600` | live |

`HTI Hurricane Monitoring` runs after each cycle's `ds-storms-pipeline` run has landed the advisory's tracks/exposure/WSP; advisories not yet in the storms DB are deferred to the next run (`monitor_id` dedup, idempotent back-fill — `MONITORING_START = 2026-08-01`, so the v1 system's era is never backfilled). Task `run_monitoring` → `databricks/run_monitor_job.py` → `pipelines/monitor.py`. Job parameters `test_email` / `dry_run`; the `prod` target pins `test_email=False`, i.e. **live to the AA Haïti Listmonk lists (116 info / 117 déclencheurs) since 2026-08-11**. `adm.zarno1` holds `CAN_MANAGE` on **both** bundle jobs (job-level; covers monitoring ops during Tristan's Aug-2026 leave — the workspace tier has no directory ACLs, so bundle-level permissions don't apply and this is set per-job). Live health in [pipeline-registry.md](../infrastructure/pipeline-registry.md) — both Databricks jobs show 🟢 OK as of the last registry refresh.

**Compute: ephemeral Job Compute**, `job_clusters` under the team Job Compute policy `000C79D951EAF0D6` (`Standard_DS4_v2`, `num_workers: 1`, spot-with-fallback) — the policy injects `DSCI_AZ_*` / `IMERG_*` creds so anyone with `CAN_MANAGE` can operate the job without a personal cluster. See [databricks.md](../infrastructure/databricks.md#clusters).

**`run_update_chirps_gefs`** keeps the CHIRPS-GEFS national-mean archive current; **`keep_awake`** is a housekeeping cron that pushes an empty commit to the `keep-awake` branch weekly — it keeps repo activity non-zero so GitHub does not auto-disable the scheduled workflows after 60 days of inactivity (the workflow itself carries no rationale comment; this is the standard reason for the pattern). **It is currently broken:** the `keep-awake` branch no longer exists on the remote (`git ls-remote --heads` and the GitHub branches API both return `main` only, checked 2026-09-02), so `actions/checkout@v5 with ref: keep-awake` fails. Runs succeeded through 2026-08-10 and have failed on every scheduled run since 2026-08-17. Low impact while the repo is under active development (`main` last pushed 2026-08-25, which resets the 60-day clock by itself), but it will stop protecting the schedules the moment work pauses. Fix = recreate the `keep-awake` branch, or point the workflow at `main`. <!-- TODO: raise with the repo owners; not fixable from the KB. -->

**Manual sibling — `HTI DGPC Rainfall Analysis`** (`dbx:700734159677972`, bundle resource `dgpc_rain`). **Not a monitor** — an analysis backfill that evaluates the DGPC rainfall criteria against IMERG half-hourly for every storm in the Haiti set — the 42 storms that came within `D_THRESH` (230 km) of Haiti in 2002–2025 (task `run_dgpc_rain` → `databricks/run_dgpc_rain_job.py` → `pipelines/run_dgpc_rain.py`; `src/dgpc/rain_analysis.py`). Scoped by the `dgpc_storms` parameter (`""` = all 42 storms, else e.g. `AL142016 AL132025`); the task carries `timeout_seconds: 21600` (~45 min for a full run). It exists as a Databricks job **only because the Earthdata credentials live in the `dsci` secret scope** and are injected by the compute policy as `IMERG_USERNAME` / `IMERG_PASSWORD` (the same pair `Run IMERG` uses) — ~14 000 OPeNDAP granule fetches, and nobody has to hold the password locally. A `--storm`/`dgpc_storms` run **merges** into the stored `rain_stats.parquet` rather than replacing it (a smoke-test on one storm can't wipe the other 41), and the pipeline refuses to write an empty result (a failed run leaves the previous output/published page untouched). Feeds the DGPC-alert-levels analysis published at `/dgpc-alertes.html`, not the live trigger path.

## Inputs

- **Tracks / wind exposure / WSP** (storms DB, dev stage — written by [`ds-storms-pipeline`](../pipelines/storms-pipeline.md)): `storms.nhc_tracks_geo`, `storms.nhc_tracks_obsv_exposure`/`nhc_tracks_obsv_buffers`, `storms.nhc_tracks_fcastonly_exposure`/`nhc_tracks_fcast_buffers`, `storms.nhc_wsp_fcastonly_exposure`/`nhc_wsp_fcastonly_polygon`, `storms.admin_population`, `storms.nhc_storms`/`storms.ibtracs_storms` (`src/datasources/storms_db.py`).
- **Forecast rainfall**: CHIRPS-GEFS national-mean 2-day rolling sum (blob, `processed/chirps/gefs/hti`), refreshed daily by the GHA workflow; CHIRPS3-GEFS `c3g` datastream since 2026-07-01 (CHIRPS2-GEFS discontinued).
- **Observed rainfall**: [IMERG](../pipelines/imerg.md) daily national mean — `SELECT valid_date, mean FROM public.imerg WHERE pcode = 'HT'` on prod Postgres (`imerg.load_imerg_from_postgres`); written by the `Run IMERG` Databricks job in `ds-raster-pipelines`, not by this repo.
- **DGPC analysis only**: IMERG **half-hourly** via NASA CMR (granule discovery, no auth) + GES DISC OPeNDAP (bbox-constrained fetch; needs `IMERG_USERNAME`/`IMERG_PASSWORD`) — the framework's daily rainfall plumbing can't address DGPC's sub-daily criteria (`src/datasources/imerg_hh.py`). Falls back to the Late (non-gauge-adjusted) run when Final hasn't caught up yet, and refuses to compute an accumulation from an incomplete granule series (<98% fetched) rather than silently understating it.
- Boundary/population: **two different boundaries, deliberately.** `src/monitoring/exposure.py` uses the FieldMaps **edge-matched** adm0 parquet (`global` container) + the WorldPop 2026 1 km raster (`raster` container), matching `ds-storms-pipeline` exactly; everything else (rain masks, email maps, DGPC department stats) uses the repo's own CODAB `raw/codab/hti.shp.zip`, downloaded from `data.fieldmaps.io` (`src/datasources/codab.py`).

## Steps

1. `pipelines/monitor.py` (`--fcast`/`--obsv`, both by default): `monitoring_utils.update_fcast_monitoring()` / `update_obsv_monitoring()` pull new NHC advisories / IMERG days since `MONITORING_START`, dedup on `monitor_id`, and evaluate each against `TRIGGERS` (`src/constants.py`).
2. **48 h cutoff** (`LT_CUTOFF_HRS`, `src/constants.py`): no forecast stage may fire once the storm is forecast to make landfall or pass closest to Haiti within 48 h. Informational emails still go out, flagged as past-cutoff. The observational stage has no cutoff.
3. Forecast stages recompute exposure at the 72 h / 120 h leadtime caps in-repo (`src/monitoring/exposure.py` — `nhc_tracks_fcastonly_exposure` only covers the full 120 h horizon in the DB), reproducing the storms-pipeline method deliberately: `ocha-lens` buffer math, the same FieldMaps edge-matched adm0 (**not** the repo's CODAB), WorldPop 2026, and the zonal-stats code copied verbatim from `ds-storms-pipeline` so the numbers agree with the `storms.*` tables. Rain is attributed over the dates the track is within `D_THRESH` (230 km) of Haiti.
4. `update_emails.py` decides what's due (`update_fcast_trigger_emails`/`update_fcast_info_emails`, and the `obsv` equivalents), dedups against `email_record_v2.csv`, builds inline-styled French HTML bodies + a WSP exceedance chart + WSP-polygon storm map (`src/email/body.py`, `plots.py`), and sends via `src/email/send.py`.
5. **Separately, on-demand**: `pipelines/run_dgpc_rain.py` (Databricks) pulls IMERG half-hourly per storm and reduces to max rolling accumulation under 3 spatial aggregations (national mean / department max / any pixel); `pipelines/run_dgpc_wind.py` (local, ~10 min) does the wind leg via `src/dgpc/windfield.py`, which fits a piecewise power-law profile through NHC's 34/50/64-kt quadrant radii plus a climatological RMW (NHC forecasts none of the DGPC levels directly). `pipelines/build_dgpc_page.py` renders both into the committed `docs/dgpc-alertes.html`.

**[gap] The Action stage's third condition — "DGPC red alert confirmed by an NHC Hurricane Warning" — is not implemented in this monitoring system.** The trigger table in the repo README carries it with a footnote, and `src/constants.py` says so in the `TRIGGERS` docstring; monitoring evaluates only the rain and 64 kt exposure conditions, so a DGPC-red-alert-only event would not fire an Action email.

## Outputs

- `ds-aa-hti-hurricanes/monitoring/hti_fcast_monitoring_v2.parquet` / `hti_obsv_monitoring_v2.parquet` (blob, dev container) — one row per storm × issue time / IMERG day, with per-stage rain/exposure values and trigger booleans.
- `ds-aa-hti-hurricanes/email/email_record_v2.csv` — one row per email sent (`info`, `mobilisation`, `action`, `obsv`).
- Listmonk campaigns: info emails → list 116; **trigger emails → lists 117 *and* 116** (`src/email/send.py::_list_ids`), so info subscribers also see a firing. `TEST_EMAIL=True` (the default; the `prod` bundle target sets it `False`) routes everything to test list 110 and prefixes the campaign name `[test]`; `DRY_RUN` (default `True`, `False` on the job) builds without sending.
- DGPC analysis (on-demand): `ds-aa-hti-hurricanes/processed/dgpc/rain_stats.parquet` + cached `imerg_hh/<atcf_id>.nc` windows (Databricks `dgpc_rain`), and `storm_set.parquet` / `fcast_wind_by_issuance.parquet` / `obsv_wind.parquet` (local `run_dgpc_wind.py`). `build_dgpc_page.py` writes `docs/dgpc-alertes.html`, committed to `main` and served from `main:/docs` at [ocha-dap.github.io/ds-aa-hti-hurricanes/dgpc-alertes.html](https://ocha-dap.github.io/ds-aa-hti-hurricanes/dgpc-alertes.html) (alongside the hand-edited `/` landing page and `/slides.html`).

## Dependencies

`ocha-stratus>=0.1.7`, `ocha-relay @ git+…@v0.3.0` (Listmonk client), `ocha-lens==0.5.1` (buffer math), `exactextract`, `geopandas`, `rioxarray`, `azure-storage-blob`, `databricks-sdk`. DGPC job additionally needs `netcdf4`/`h5netcdf`/`h5py` (OPeNDAP serves `.nc4` as raw HDF5; the `netcdf4` backend declines it, so `h5netcdf` + its `h5py` dependency are pulled in explicitly). Azure Postgres (storms dev, imerg prod), Azure Blob (`imb0chd0dev`/`imb0chd0prod`; containers `projects` for this repo's own data, `global` for the FieldMaps adm0, `raster` for WorldPop), Listmonk lists 110/116/117 via `DSCI_LISTMONK_BASE_URL`/`_API_USERNAME`/`_API_KEY`, NASA Earthdata credentials (`dsci` secret scope), Databricks Job Compute policy `000C79D951EAF0D6`.

## Failure modes & debugging

- **No emails, job exits 0**: normal when no active Atlantic storms, or storms >1000 km away (`MIN_EMAIL_DISTANCE`).
- **Advisory deferred every run**: check `ds-storms-pipeline` health — tracks/exposure/WSP for the advisory never landed in the dev DB.
- **CHIRPS-GEFS stale**: a broken GEFS feed does **not** fail the monitoring job — it silently evaluates rain on the last successful issuance and will not alert by itself. The GHA workflow now guards against this: on failure it opens (or comments on) a GitHub issue titled "CHIRPS-GEFS download failing (scheduled run)" assigned to `zackarno`/`t-downing`. Rerunning the workflow backfills missed days.
- **`keep_awake` red in the Actions tab**: expected — the `keep-awake` branch is gone, so the checkout step fails (failing weekly since 2026-08-17). Does not affect monitoring.
- **Listmonk creds**: injected from the `dsci` Databricks secret scope by `databricks/run_monitor_job.py`; missing keys log a warning and real sends fail (dry-run/test-list behaviour is otherwise unaffected).
- **DGPC job**: fails loudly (not silently) if `IMERG_USERNAME`/`IMERG_PASSWORD` are unset, or if a storm's half-hourly window is <98% complete (refuses to compute an accumulation from missing granules — see `imerg_hh.fetch_window`). GES DISC 429/5xx are retried with backoff before that.
- Job failure alerts (`email_notifications.on_failure`, `no_alert_for_skipped_runs: true`): `hti_monitoring` → tristan.downing@un.org **and** zachary.arno@un.org; `dgpc_rain` → tristan.downing@un.org only.

## Downstream consumers

Listmonk lists 116/117 (live since 2026-08-11; subscriber lists managed in Listmonk — see `pipelines/setup_listmonk_lists.py`). Monitoring v2 parquets; the v1 parquets/`email_record.csv` are frozen for the historical record and the Dash app ([chd-ds-aa-hti-hurricanes-app](../infrastructure/deployments.md)). The DGPC alert-level analysis publishes to `/dgpc-alertes.html` on the repo's GitHub Pages site, feeding the in-development trigger redesign in the [hti-hurricanes framework](../frameworks/hti-hurricanes/2026-06-09.md) rather than the live trigger path.
