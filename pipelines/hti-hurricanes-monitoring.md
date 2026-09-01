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
    - { name: run_check_trigger (v1), ref: "deleted from main 2026-08-10", schedule: "was event-dispatched by ds-nhc-forecast", status: retired }
    - { name: run_check_obsv_trigger (v1), ref: "deleted from main 2026-08-10", schedule: "was event-dispatched by the IMERG pipeline", status: retired }
    - { name: "HTI DGPC Rainfall Analysis", ref: "databricks.yml (bundle resource dgpc_rain; dbx:700734159677972)", schedule: "manual (no cron) — analysis backfill, not a monitor", status: live }
inputs:
  - "DB (dev stage): storms.nhc_tracks_geo — NHC track points + quadrant wind radii"
  - "DB (dev stage): storms.nhc_tracks_obsv_exposure / nhc_tracks_obsv_buffers — observed swath exposure"
  - "DB (dev stage): storms.nhc_wsp_fcastonly_exposure / nhc_wsp_fcastonly_polygon — WSP probabilistic bands (email chart + map)"
  - "DB (prod): public.imerg — observed national-mean rainfall"
  - "Blob (projects): ds-aa-hti-hurricanes/processed/chirps/gefs/hti — CHIRPS-GEFS national-mean daily (CHIRPS3 c3g datastream since 2026-07-01)"
  - "Blob (global): fieldmaps/edge-matched/humanitarian/intl/adm0/HTI.parquet — boundary for exposure"
  - "Blob (raster): worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif"
outputs:
  - blob monitoring records (hti_fcast_monitoring_v2.parquet, hti_obsv_monitoring_v2.parquet, email_record_v2.csv)
  - "Listmonk campaigns: info list 116 (AA Haïti ouragans - informations), trigger list 117 (déclencheurs); TEST_EMAIL=True routes to internal test list 110"
dependencies: [Azure Postgres (storms dev + imerg prod), Azure Blob, Listmonk (ocha-relay), Databricks Job Compute (policy 000C79D951EAF0D6), ds-storms-pipeline (upstream)]
downstream: [hti-hurricanes framework; chd-ds-aa-hti-hurricanes-app]
depends_on: [storms-pipeline, imerg, listmonk]
source_repo: ocha-dap/ds-aa-hti-hurricanes
source_branch: main
source_sha: dd851c0
code_ref:
  - pipelines/monitor.py
  - src/monitoring/monitoring_utils.py
  - src/monitoring/exposure.py
  - src/email/
  - databricks.yml
visibility: internal
last_synced: 2026-08-10
---

# Haiti hurricanes monitoring

## One-liner

Four times daily (:50, after `ds-storms-pipeline` lands each NHC advisory): evaluate the 2026 trigger — Mobilisation (≤120 h) / Action (≤72 h) fire on forecast 2-day rain ≥68 mm OR >0 people exposed to ≥64 kt forecast winds; Réponse précoce (obsv) fires on observed rain ≥57 mm OR >0 observed 64 kt exposure — and send French Listmonk emails (info every advisory; one trigger email per storm per stage). **Folded into the [hti-hurricanes framework repo](../frameworks/hti-hurricanes/2026-06-09.md).** Replaced the v1 GHA/SES system on 2026-08-10; live to the real Listmonk lists since 2026-08-11 (framework endorsement pending).

## Schedule / trigger

Databricks job `HTI Hurricane Monitoring` (`dbx:586426884912849`; bundle `databricks.yml` on `main`, resource `hti_monitoring`, `source: GIT`), cron `0 50 3,9,15,21 * * ?` UTC — after each cycle's `ds-storms-pipeline` run has landed the advisory's tracks/exposure/WSP. Advisories whose tracks haven't landed in the storms DB yet are deferred to the next run (`monitor_id` dedup, idempotent back-fill). Task `run_monitoring` → `databricks/run_monitor_job.py` → `pipelines/monitor.py`. Job parameters `test_email` / `dry_run`; the `prod` target sets `test_email=False`, i.e. **live to the AA Haïti Listmonk lists (116 info / 117 déclencheurs) since 2026-08-11**. `adm.zarno1` holds `CAN_MANAGE` (job-level). `run_update_chirps_gefs.yml` (GHA cron 08:50 UTC) keeps the rainfall-forecast archive current. Live health in [pipeline-registry.md](../infrastructure/pipeline-registry.md).

**Compute: ephemeral Job Compute, not a personal cluster** (corrected 2026-08-27). Both jobs use a `job_clusters` block under the team **Job Compute policy `000C79D951EAF0D6`** (`Standard_DS4_v2`, `num_workers: 1`, spot-with-fallback) — the policy injects the `DSCI_AZ_*` / `IMERG_*` creds, so anyone with `CAN_MANAGE` can operate the job without permissions on someone's personal cluster. The monitor was briefly pinned to the durable interactive cluster `0515-161935-i2w5mxhc` and flagged `PERSONAL-CLUSTER` ([why that's fragile](../infrastructure/databricks.md#clusters)); the estate fingerprint shows it moved to Job Compute between **2026-08-12 and 2026-08-15**, and the flag no longer fires.

**Manual sibling — `HTI DGPC Rainfall Analysis`** (`dbx:700734159677972`, bundle resource `dgpc_rain`, new in the estate on **2026-08-27**, [infra-drift #573](https://github.com/OCHA-DAP/ds-knowledge-base/issues/573)). **Not a monitor** — a one-off/manual analysis backfill that evaluates the **DGPC rainfall criteria against IMERG half-hourly for every storm in the Haiti set** (task `run_dgpc_rain` → `databricks/run_dgpc_rain_job.py` → `pipelines/run_dgpc_rain.py`; `src/dgpc/rain_analysis.py`). Scoped by the `dgpc_storms` parameter (`""` = all 42 storms, else e.g. `AL142016 AL132025`); `timeout_seconds: 21600`. It exists as a Databricks job **only because the Earthdata credentials live in the `dsci` secret scope** and are injected by the compute policy as `IMERG_USERNAME` / `IMERG_PASSWORD` (the same pair `Run IMERG` uses) — ~14 000 OPeNDAP granule fetches, and nobody has to hold the password locally. Feeds the DGPC-validation strand of the [in-development redesign](../frameworks/hti-hurricanes/2026-06-09.md), not the live trigger path.

## Key mechanics

- **48 h cutoff**: no forecast trigger once the forecast closest pass is <48 h away; informational emails still go out flagged "délai dépassé".
- **Leadtime-capped exposure**: `storms.nhc_tracks_fcastonly_exposure` covers the full 120 h horizon only, so the 72 h Action exposure is recomputed in-repo (`src/monitoring/exposure.py`) — ocha-lens buffer math + WorldPop 2026 + exactextract, validated to exact agreement with the DB values at 120 h.
- **Rain attribution**: 2-day rolling national-mean rain counted over dates the track is within 230 km of Haiti (calibration-consistent date window, not a trigger gate).
- **DGPC condition not implemented**: the Action stage's "DGPC red alert + NHC Hurricane Warning" OR-condition is noted in the emails but not monitored.
- **Emails**: composed as inline-styled French HTML (ds-storms-alerts conventions), WSP exceedance chart + WSP-polygon storm map, base64 images swapped for Listmonk media at send. `TEST_EMAIL` / `DRY_RUN` env switches (safe defaults). Test replay: `pipelines/send_test_email.py` (Hurricane Melissa advisory).

## Failure modes & debugging

- **No emails, job exits 0**: normal when no active Atlantic storms, or storms >1000 km away.
- **Advisory deferred every run**: check `ds-storms-pipeline` health — tracks/exposure/WSP for the advisory never landed in the dev DB.
- **CHIRPS-GEFS stale**: v2 datastream died 2026-07-01; the loader now uses the CHIRPS3 `c3g` files. If `load_recent_chirps_gefs_mean_daily()` lags, check the GHA cron and the CHC directory layout.
- **Listmonk creds**: injected from the `dsci` Databricks secret scope by `databricks/run_monitor_job.py`; missing keys log a warning and real sends fail.
- Job failure alerts email tristan.downing@un.org (`email_notifications.on_failure`).

## Downstream consumers

Listmonk lists 116/117 (live since 2026-08-11; subscriber lists managed in Listmonk — see `pipelines/setup_listmonk_lists.py`). Monitoring v2 parquets; the v1 parquets/`email_record.csv` are frozen for the historical record and the Dash app.
