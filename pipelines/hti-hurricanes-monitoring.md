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
dependencies: [Azure Postgres (storms dev + imerg prod), Azure Blob, Listmonk (ocha-relay), Databricks cluster 0515-161935-i2w5mxhc, ds-storms-pipeline (upstream)]
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

Four times daily (:50, after `ds-storms-pipeline` lands each NHC advisory): evaluate the 2026 trigger — Mobilisation (≤120 h) / Action (≤72 h) fire on forecast 2-day rain ≥68 mm OR >0 people exposed to ≥64 kt forecast winds; Réponse précoce (obsv) fires on observed rain ≥57 mm OR >0 observed 64 kt exposure — and send French Listmonk emails (info every advisory; one trigger email per storm per stage). **Folded into the [hti-hurricanes framework repo](../frameworks/hti-hurricanes/2026-06-09.md).** Replaced the v1 GHA/SES system on 2026-08-10 (framework pending endorsement; sends routed to the internal test list until go-live).

## Schedule / trigger

Databricks job `HTI Hurricane Monitoring` (bundle `databricks.yml`, `source: GIT` from `main`), cron `0 50 3,9,15,21 * * ?` UTC. Advisories whose tracks haven't landed in the storms DB yet are deferred to the next run (`monitor_id` dedup, idempotent back-fill). `run_update_chirps_gefs.yml` (GHA cron 08:50 UTC) keeps the rainfall-forecast archive current. The job (`dbx:586426884912849`) runs on the durable interactive cluster `0515-161935-i2w5mxhc`, so the registry flags it `PERSONAL-CLUSTER` ([why that's fragile](../infrastructure/databricks.md#clusters)); live health in [pipeline-registry.md](../infrastructure/pipeline-registry.md).

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

Listmonk lists 116/117 (pending endorsement: Tristan only; migrate the real distribution list at go-live). Monitoring v2 parquets; the v1 parquets/`email_record.csv` are frozen for the historical record and the Dash app.
