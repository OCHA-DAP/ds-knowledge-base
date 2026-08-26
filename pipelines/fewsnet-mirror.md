---
content_type: pipeline
visibility: internal
name: fewsnet-mirror
type: ingest
status: live
source_repo: OCHA-DAP/ds-fewsnet-mirror
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "refresh-fewsnet", ref: ".github/workflows/refresh-fewsnet.yml", schedule: "daily 04:52 UTC", status: live }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "on workflow_run(refresh-fewsnet) + daily 08:30 UTC backstop", status: live }
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
  - "DSCI_AZ_DB_DEV_* and DSCI_AZ_BLOB_DEV_SAS_WRITE (org-level Actions secrets)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-08-26
---

# FEWS NET mirror

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
- **The published map = `assistance = false`** ("not allowing for
  assistance"); `true` rows exist only where factoring assistance changes the
  phase. Verified against the package shapefiles (the rendered map).
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
