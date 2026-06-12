---
content_type: pipeline
name: storms-alerts
type: alert
status: live
schedule: "0 30 3,9,15,21 * * ?"   # UTC, ~30 min after each NHC advisory (Databricks). GHA runner retired (latency).
deployment:
  platform: databricks-job
  ref: bundle "ds-storms-alerts" → job "Storm Alert" (storm_alert) runs databricks/run_alert_job.py → pipelines/run_alert.py
  url: workspace adb-6009046713167663 (cluster 0515-161935-i2w5mxhc, shared with storms-pipeline)
  resource_group: n/a
inputs:   # all from the `storms` schema (see storms-pipeline.md)
  - nhc_tracks_fcastonly_exposure, nhc_tracks_obsv_exposure (adm0+adm1)
  - nhc_wsp_fcastonly_exposure / _polygon
  - gdacs_exposure, adam_exposure (+ *_fm_lookup), storm_id_lookup, admin_population
  - FieldMaps adm0/adm1 boundaries (blob)
outputs:
  - Listmonk campaigns (HTML alert email + per-storm exposure CSV attachments)
  - sent to per-country lists (tag iso3:<ISO3>) + aggregate:all + aggregate:lac + aggregate:monitoring
dependencies: [ocha-relay (ListmonkClient, pinned by SHA), Listmonk, ocha-stratus, matplotlib, geopandas]
downstream: [email subscribers — self-manage via the GH Pages signup form]
source_repo: ocha-dap/ds-storms-alerts
source_branch: adm1-exposure-csv   # ahead of main (2026-06-10). Deployed job uses git_source var default `main`.
source_sha: 89bdcc3
code_ref:
  - pipelines/run_alert.py     # main: generate_alert_html / generate_monitoring_html / resolve_country_list_ids
  - src/data.py                # DB/blob fetchers
  - src/constants.py           # TEST_LIST_IDS=[5], COUNTRY_LIST_TAG, LAC_ISO3S
  - pipelines/setup_country_lists.py   # provisions Listmonk lists
visibility: internal
last_synced: 2026-06-12
---

# Storms alerts (email)

## One-liner
~30 min after each NHC advisory: read storm exposure from the `storms` schema, render an HTML alert (maps, per-country strip charts, return periods) + exposure CSVs, and send as a **Listmonk campaign** to affected-country and aggregate lists. Consumes [storms-pipeline](storms-pipeline.md); uses [Listmonk + ocha-relay](../infrastructure/comms-listmonk.md).

## Schedule / trigger
Databricks job "Storm Alert", cron `0 30 3,9,15,21 * * ?` UTC. The old GitHub Actions runner (`run_alert.yml`) is disabled — trigger latency had degraded to ~1h; Databricks replaced it. (A separate GHA workflow deploys the Azure web app `chd-ds-storms-alerts` hosting the subscriber **signup site** — not the alert send.)

## Inputs / Outputs
Reads the NHC/GDACS/ADAM exposure + WSP tables. Sends two email types: **full alert** (countries with exposure) and **monitoring** (storms active but no monitored exposure → maps only, to `aggregate:monitoring`). Images uploaded to Listmonk media (avoids Gmail's ~102 KB clip); CSVs as attachments. `TEST_EMAIL`/`DRY_RUN` default True in code; the prod target sets both False.

## Dependencies
`ocha-relay` (`ListmonkClient`, pinned to a git SHA), self-hosted Listmonk, ocha-stratus. Upstream producer: storms-pipeline.

## Failure modes & debugging
- Missing per-country Listmonk list for an affected iso3 → `resolve_country_list_ids` raises (run `setup_country_lists.py` first).
- `send_campaign` hard-refuses a "finished" campaign (anti-duplicate); headless confirm raises rather than sending silently.
- Late-publishing source silently drops from the MAX consolidation — logged as a warning.
- **Operational footgun:** a bare `databricks bundle run storm_alert` on the default (prod) target **sends for real** — guard with `--params test_email=True,dry_run=True`.
- DBX can report exit 0 while the task failed — verify "Sent campaign …" in task logs.

## Key decisions & rationale
Consolidate CHD + ADAM + GDACS exposure by **MAX** across sources ("bias to action"). adm1 figures held consistent within a storm-country and do **not** sum to adm0. Return periods vs historical seasons ≥2002. Wind thresholds 34/50/64 kt.

> **Note:** the exposure-consolidation logic (MAX across sources, adm0/adm1 harmonization, WSP probability-band expected value, return periods) is real analytical methodology living in this alert repo — a candidate for a future `methods/` page. Public methodology: https://ocha-dap.github.io/ds-storms-alerts/guide.html
