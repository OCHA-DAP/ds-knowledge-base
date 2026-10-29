---
content_type: pipeline
name: vut-cyclones-monitoring
type: monitoring
status: live
deployment:
  platform: databricks
  resource_group:            # n/a
  jobs:
    - { name: "Power Automate flow vut_trigger_monitoring", ref: "personal flow on the maintainer's un.org mailbox, a copy of fji_trigger_monitoring (details in ds-knowledge-base-internal/infrastructure/fji-fms-relay.md)", schedule: "event — each VMHS forecast email", status: paused }
    - { name: "Poll FMS inbox (shared with Fiji)", ref: "pa-aa-fji-storms .github/workflows/poll_fms_inbox.yml, repo var VUT_MONITORING", schedule: "*/10 * * * *", status: active }   # VUT_MONITORING=test since 2026-10-29
    - { name: "Vanuatu Cyclone Monitoring (DAB vut_monitoring)", ref: "ds-aa-vut-cyclones databricks.yml; job 306047616262981 (prod target, deployed 2026-10-29)", schedule: "event — jobs/run-now from the poller, one run per CSV (no schedule)", status: active }
inputs:
  - "RSMC Nadi (FMS) Official Forecast Track CSVs, through the Fiji relay chain (pipelines/fji-storms-monitoring.md); staged by the poller on the dev blob under pa-aa-fji-storms/raw/fms/inbox/"
  - "VMHS (Vanuatu Met) forecast CSVs, emailed to ocha-datascience@un.org; TC Module export, assumed identical to FMS's (no sample yet); staged under ds-aa-vut-cyclones/raw/vmhs/inbox/"
  - "WorldPop 2026 1 km (raster container worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif)"
  - "Vanuatu COD-AB admin 2 — blob (dev) ds-aa-vut-cyclones/raw/codab/vut.shp.zip"
outputs:
  - "Listmonk campaigns: information email per forecast to lists 129 (Vanuatu framework info), 14 (CERF info) and 6 (DSCI); readiness / action / observational emails to lists 130 (Vanuatu framework trigger), 15 (CERF trigger) and 6; test sends to list 5 only, subject prefixed [TEST]"
  - "OneDrive vut_vmhs_forecasts/ — every VMHS CSV the flow received"
  - "blob (dev) ds-aa-vut-cyclones/monitoring/email_record.csv (test_email_record.csv for tests) — send-once record"
  - "blob (dev) ds-aa-vut-cyclones/monitoring/{vmhs,fms}_observed_points.csv (test_... for tests) — the observed track per source: the analysis point of every forecast received (as ds-storms-pipeline's nhc_tracks_obsv_buffers). VMHS's is the observational trigger; both are drawn, faded, on the email maps and counted in the attachments"
surfaces: []
dependencies:
  - "The Fiji relay chain: Zoho relay inbox, the poller and its secrets (pipelines/fji-storms-monitoring.md)"
  - "Databricks service principal fji-fms-relay — CAN_MANAGE_RUN on this job too; pa-aa-fji-storms repo var VUT_DBX_JOB_ID"
  - "pa-aa-fji-storms repo var VUT_MONITORING: off | test | live"
  - "Listmonk sender credentials (dsci secret scope on Databricks); lists 129/130 created 2026-10-28, empty until the distribution list is agreed"
  - "Databricks Job Compute (single node) policy 0017962FF5D1E3B9, DBR 15.4 LTS, pinned requirements-dbx.txt (same pins as the Fiji job)"
  - "ocha-stratus (blob)"
downstream:
  - "Vanuatu tropical cyclone AA framework (endorsed October 2026): the live readiness, action and observational trigger monitoring"
depends_on:
  - fji-storms-monitoring
  - listmonk
source_repo: ocha-dap/ds-aa-vut-cyclones
source_branch: main
source_sha:
code_ref:
  - ds-aa-vut-cyclones/pipelines/monitor_forecast_trigger.py
  - ds-aa-vut-cyclones/src/monitoring/forecast.py
  - ds-aa-vut-cyclones/src/monitoring/exposure.py
  - ds-aa-vut-cyclones/src/monitoring/observed.py
  - ds-aa-vut-cyclones/databricks.yml
  - ds-aa-vut-cyclones/databricks/run_monitor.py
  - pa-aa-fji-storms/pipelines/poll_fms_inbox.py
extra:
  method: "Exposure is counted exactly as in the trigger design (exploration/make_forecast_check_data.py: WorldPop 2026, area councils expanded 500 m seaward, dissolved scope, all_touched) — checked equal on 48 swaths. FMS/VMHS radii are 10-minute winds, so the 64 kt radius is used as is (the design's JTWC forecasts needed the V_EQ conversion)."
visibility: public
last_synced: "2026-10-28"
---

# Vanuatu tropical cyclone monitoring

> Runbook. How an RSMC Nadi or VMHS forecast becomes a Vanuatu trigger check and a Listmonk email, and what to do when one doesn't arrive.

## One-liner

Every FMS forecast (through the Fiji relay chain) and every VMHS forecast (through a second Power Automate flow on the same relay) → the Fiji poller starts the Databricks job "Vanuatu Cyclone Monitoring" → people exposed to ≥ 64-knot winds → Listmonk information, readiness, action and observational emails.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Power Automate flow `vut_trigger_monitoring` | the maintainer's personal Power Automate (not in a repo) | each VMHS email | built, off until go-live |
| Poll FMS inbox (shared with Fiji) | `pa-aa-fji-storms/.github/workflows/poll_fms_inbox.yml` | `*/10 * * * *` | `VUT_MONITORING=test` (test list only) from 2026-10-29 |
| Vanuatu Cyclone Monitoring | `ds-aa-vut-cyclones/databricks.yml` (job `306047616262981`) | `jobs/run-now` from the poller | deployed 2026-10-29; first manual test run OK |

No seasonal switch: the chain runs whenever FMS or VMHS sends a forecast (framework monitoring period 1 October–31 May).

## Triggers

All three: at least 15,000 people exposed to winds of at least 64 knots.

| trigger | forecast | part of the track | where |
|---|---|---|---|
| readiness | RSMC Nadi (FMS) | 72–120 h after issue | Sanma, Shefa, Tafea |
| action | VMHS | 24–72 h | Sanma, Shefa, Tafea |
| observational | VMHS observed track | analysis (0 h) points of all VMHS forecasts for the storm | all of Vanuatu |

## Steps

1. **FMS** forecasts follow the Fiji chain ([fji-storms-monitoring](fji-storms-monitoring.md)). With `VUT_MONITORING` on, the poller sends each FMS CSV to the Fiji targets first and then to the Vanuatu job.
2. **VMHS** emails its forecast CSV to `ocha-datascience@un.org`, which forwards it to the maintainer's un.org mailbox. The flow `vut_trigger_monitoring` carries on if the sender ends with `vanuatu.gov.vu` or `meteo.gov.vu` (or the subject is exactly `vut_test`) and a CSV is attached: it saves the CSV to OneDrive `vut_vmhs_forecasts/`, replies to acknowledge, and relays it with the subject `[vut-relay] vmhs_forecast` (`[vut-relay] vmhs_forecast_test`).
3. **The poller** accepts `[vut-relay]` relay emails under the same sender and DMARC gate as Fiji's, stages the CSV under `ds-aa-vut-cyclones/raw/vmhs/inbox/` and starts only the Vanuatu job. The Vanuatu target keeps its own state rows (target `vut`).
4. **The monitor** (`pipelines/monitor_forecast_trigger.py --source fms|vmhs`) reads the staged CSV (not `storms.fms_*`: the Fiji job ingests the FMS CSV at the same moment). It skips FMS forecasts whose track never comes within 1,000 km of Vanuatu, computes the trigger exposure, adds the forecast's analysis point to that source's observed track (FMS ones even for distant storms), and sends the emails. Only an `Official Forecast Track` is monitored. The attached area-council CSV and province PDF count, as ds-storms-alerts does, the observed swath plus the whole forecast (their union, per wind speed); only the trigger values and the likely-range plot are about the trigger window. The maps draw the observed swath faded, the forecast swath beyond it (forecast minus observed of the same speed, ds-storms-pipeline's forecast-only buffers) and the trigger window's 64 kt swath as an outline.

## Outputs

See the frontmatter. Readiness and action emails go out for every forecast that meets them (as in Fiji); the observational email once per storm (disturbance id + season). Every email at most once per CSV.

## Dependencies

See the frontmatter. It shares the Fiji chain's secrets and service principal; the internal KB (`ds-knowledge-base-internal/infrastructure/fji-fms-relay.md`) has the addresses and the flow's id.

## Failure modes & debugging

Follow the chain: the flow's run history (and OneDrive `vut_vmhs_forecasts/`), the relay inbox, the "Poll FMS inbox" log in pa-aa-fji-storms (it says why it skipped an email, and logs VMHS emails while `VUT_MONITORING` is off), the Databricks run, the Listmonk campaign. A failed run emails the maintainer's un.org address.

- **The first real VMHS CSV fails the run:** VMHS had sent no sample when this was built; the parser assumes the FMS export (`src/monitoring/forecast.py`). Look at the CSV in OneDrive and adapt the parser, then send it by hand.
- **A VMHS forecast from a new address isn't picked up:** the flow only accepts senders ending with `vanuatu.gov.vu` or `meteo.gov.vu`.
- **Nothing Vanuatu-side can block Fiji:** a bad `VUT_MONITORING` value or missing `VUT_DBX_JOB_ID` fails the poll run only after the Fiji targets were handled; a failed Vanuatu hand-off is a warning in `test`, a failure in `live`.
- **Send a forecast by hand:** `databricks bundle run vut_monitoring` with `csv_blob` and `event` (see `databricks.yml`); a `*_test` event always goes to list 5.
- **End-to-end test:** email the maintainer's un.org mailbox with subject exactly `vut_test` and an FMS-format CSV; `[TEST]` emails arrive on list 5.
- **Trust:** like Fiji, the first hop is a domain string match; neither Vanuatu domain publishes DMARC (`vanuatu.gov.vu` has SPF `-all`). The poller's DMARC gate covers only the relay hop.

## Downstream consumers

The Vanuatu tropical cyclone AA framework (endorsed October 2026).
