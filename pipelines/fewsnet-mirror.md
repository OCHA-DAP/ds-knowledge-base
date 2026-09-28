---
content_type: pipeline
visibility: internal
name: fewsnet-mirror
type: ingest
status: live
surfaces:
  - {url: "https://ocha-dap.github.io/ds-fewsnet-mirror/", kind: dashboard, title: "FEWS NET mirror explorer (Classifications / Units, CSV download)"}
source_repo: OCHA-DAP/ds-fewsnet-mirror
deployment:
  platform: databricks-job   # + GitHub Pages deploy workflow (no DB access); see note in body
  resource_group: null
  jobs:
    - { name: "FEWS NET Mirror", ref: "databricks.yml:fewsnet_mirror", schedule: "daily 04:52 UTC (refresh_fewsnet → export_site → publish_site_data)", status: pending }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "daily 08:30 UTC + workflow_dispatch (blob → Pages, no DB)", status: live }
    - { name: "refresh-fewsnet", ref: ".github/workflows/refresh-fewsnet.yml", schedule: "daily 04:52 UTC", status: "retired by #1 (still live on main until merged)" }
inputs:
  - "FDW API ipcphase.csv?country_code=<ISO2> (fdw.fews.net — full classification record per country, 2009+; no auth; coverage discovered by probing all ~252 FDW countries)"
  - "FDW API ipcpackage/?country_code=<ISO2> (zip of the LATEST collection round's shapefiles — unit geometry + admin/livelihood-zone attributes)"
outputs:
  - "DB table: fewsnet.classification (dev — one row per FNID unit x scenario CS/ML1/ML2 x collection round; ~1.3M rows, ~45 countries; full replace with min-row guard)"
  - "DB table: fewsnet.units (dev — latest round's unit registry: FNID, admin 0-3 names, livelihood zone; upsert on FNID, old vintages kept)"
  - "Blob: projects/ds-fewsnet-mirror/processed/units/{ISO3}.geojson (dev — latest round's unit geometry, one feature per FNID; re-uploaded only when the round moves on)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-fewsnet-mirror/ (Classifications / Units tabs, CSV download)"
dependencies:
  - "ocha-stratus (DB engine + blob; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_* / DSCI_AZ_BLOB_DEV_SAS(_WRITE): injected on Databricks by the Job Compute policy; the Pages deploy needs only the org Actions secret DSCI_AZ_BLOB_DEV_SAS"
  - "PGSSLMODE=require (set by src/storage.py)"
last_verified: 2026-09-25
---

# FEWS NET mirror

> **Runs on Databricks since the private-endpoint cutover (PR open [ds-fewsnet-mirror#1](https://github.com/OCHA-DAP/ds-fewsnet-mirror/pull/1), 2026-09-25).** The dev DB is reachable only through its private endpoint, so the refresh and the site-data export run as a Databricks job on the shared Job Compute policy (`databricks.yml` + the generic wrapper `databricks/run_task.py`; same UTC schedule, data plane still dev). The GitHub Pages deploy stays on Actions but no longer touches the DB: the job's last tasks run the unchanged `export_site_data.py` and `scripts/site_data_blob.py upload` (dev blob `projects/ds-fewsnet-mirror/site-data/`, HNS directory markers skipped, stale files removed), and `deploy-site.yml` (`download`) copies the same `site/data/**` down on its old daily backstop cron, so the site output is identical. Extra secrets come from the `dsci` scope at run time via `--secret` (not `spark_env_vars`, whose missing key blocks the cluster launch). Until the PR is merged and `databricks bundle deploy -t prod` has run, the old GitHub Actions crons in `main` are still the live thing; the `deployment:` block in the frontmatter describes the target state.

Mirrors **FEWS NET's IPC-compatible acute food insecurity classifications**
(FDW API) into the dev DB (schema `fewsnet`) + dev blob (unit geometry), and
publishes a [GitHub Pages explorer](https://ocha-dap.github.io/ds-fewsnet-mirror/).
Modeled 1:1 on [ipc-mirror](ipc-mirror.md) — and deliberately separate from it:
FEWS NET's analysis is IPC-*compatible* but is not the IPC/CH consensus, and
the two can disagree.

## Keying (the part people get wrong)

Every classification row carries BOTH the **collection round**
(`reporting_date` — a Food Security Outlook ~3×/yr, an Outlook Update, or a
monthly Key Message Update) and the **projection window**
(`projection_start/end`, per `scenario` CS / ML1 / ML2). Rounds overlap in
time — a later round's *current* covers the same months as an earlier round's
*projection* — so never build a series without keying on both.

## Gotchas

- **Units are FEWS NET's own geography (FNIDs)** — livelihood-zone × admin
  intersections (`fsc_admin_lhz`), admin units (`fsc_admin`), IDP camps,
  national parks, `admin0`. No COD p-codes anywhere; join to our boundaries
  via the ADMIN1/ADMIN2 name columns in `fewsnet.units`. FNIDs encode the
  unit vintage (UG2026C3…); geometry is mirrored for the latest round only.
- **`assistance` is the "!" marker, not a series.** Each unit × scenario ×
  round has ONE published row; `assistance = true` means FEWS NET draws that
  unit with "!" (phase held down by humanitarian assistance). Count every row
  at its phase — filtering `assistance = false` silently drops the "!" units
  (Zimbabwe Feb 2020: 98 of 203 kept). Re-verified 2026-09-16 against the Oct
  2016 Zimbabwe package (`HA0/HA1/HA2` flags). <!-- TODO: the repo README still
  says "published map = assistance=false"; the seas5-skill `--level fews`
  export applies that rule — fix both in the spokes. -->
- **No population-in-phase figures exist** — FEWS NET classifies areas. FDW's
  `ipcpopulation` is a national FAOB phase-3+ series only (not mirrored).
- **Absent is not Phase 1**: `phase` null + `status` Not Projected / Not
  Available = not classified; shapefile sentinels 66/88/99 (water / park / no
  data) arrive as null + status. Filter `phase BETWEEN 1 AND 5` for maps.
- Filter `scale <> 'IPC Highest Household'` for maps — that scale is the
  national Food Assistance Outlook Brief series, not the subnational product.
- The FDW JSON API caps page_size at 500 (~50 s/page — unusable at 1.3M rows);
  the **CSV endpoint streams a whole country in seconds** and is what the
  mirror uses.

## Downstream consumers

- **seas5-skill Forecast × HNRP tab** (`ds-seas5-skill/pipeline/export_hnrp_drought.py
  --level fews`, [live tab](https://ocha-dap.github.io/ds-seas5-skill/#hnrp)) —
  "FEWS NET phases" severity source, drawn on FEWS NET's own units with the
  forecast inherited from the containing COD admin unit (name-matched).

See also: [infrastructure/datasets/fews-net.md](../infrastructure/datasets/fews-net.md).
