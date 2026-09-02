---
content_type: pipeline
name: storm-impact-harmonisation
type: exposure
status: live
deployment:
  platform: github-actions
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - { name: "Daily GDACS Monitor Email", ref: ".github/workflows/daily-gdacs-monitor-email.yml", schedule: "20 3,9,15,21 * * *", status: live }
    - { name: "PDC Cyclone Poll", ref: ".github/workflows/pdc-cyclone-poll.yml", schedule: "40 */3 * * *", status: live }
    - { name: "Deploy Pages site", ref: ".github/workflows/deploy-app.yml", schedule: "on push to main", status: live }
    - { name: "Deploy adm0_exp_app (global-cyclones slot)", ref: ".github/workflows/usa-radii-exp_chd-pa-aa-fji-storms-app(global-cyclones).yml", schedule: "workflow_dispatch only (push trigger removed 2026-08-03)", status: manual }
    - { name: "Deploy CERF predictor app (cerf-rr slot)", ref: "(deleted)", schedule: "—", status: retired }
inputs:
  - "GDACS REST API (live tropical cyclone events, per-country exposure) — https://www.gdacs.org/gdacsapi"
  - "blob: ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp_all.parquet (CHD historical IBTrACS exposure baseline)"
  - "blob: ds-storm-impact-harmonisation/processed/combined_historical_national_exposure.csv (merged CHD+GDACS+ADAM historical)"
  - "blob: ds-storm-impact-harmonisation/processed/ibtracs_usa_buffers.parquet (IBTrACS USA radii buffers)"
  - "blob: ds-storm-impact-harmonisation/processed/adam_gdacs_per_storm_source_diagnostics.csv (coverage diagnostic)"
  - "blob: ds-cyclone-exposure/gdacs_historical_national_exposure.csv (GDACS historical exposure)"
  - "blob: ds-cyclone-exposure/adam_historical_national_exposure.csv (ADAM historical exposure)"
  - "blob: ds-storm-impact-harmonisation/processed/cerf-storms-with-sids-2024-02-27.csv (CERF allocations matched to storm SIDs)"
  - "DB (dev): storms.nhc_tracks_fcast_exposure, storms.nhc_tracks_obsv_exposure, storms.nhc_tracks_fcastonly_exposure"
  - "DB (dev): storms.nhc_wsp_exposure, storms.nhc_wsp_fcastonly_exposure, storms.nhc_wsp_polygon, storms.nhc_wsp_fcastonly_polygon"
  - "DB (dev): storms.nhc_tracks_fcast_buffers, storms.nhc_tracks_fcastonly_buffers, storms.nhc_tracks_obsv_buffers"
  - "DB (dev): storms.gdacs_exposure, storms.adam_exposure, storms.storm_id_lookup, storms.gdacs_fm_lookup"
  - "DB (prod): storms.ibtracs_tracks_geo, storms.ibtracs_storms, storms.nhc_storms"
  - "CERF GMS API (https://cerfgms-webapi.unocha.org/v1/application/All.xml)"
  - "INFORM Risk API (src/datasets/inform.py)"
  - "blob: fieldmaps/edge-matched/humanitarian/intl/adm1/{iso3}.parquet (FieldMaps boundaries, global container)"
  - "Worldpop COG raster: blob raster container worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif"
outputs:
  - "Listmonk email campaign — daily GDACS monitor digest sent to list 25 (test); prod list ID passed at runtime"
  - "blob: ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp_all.parquet (CHD historical exposure, written by adm0_exp.ipynb)"
  - "blob: ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp/{iso3}_exp.parquet (per-country partitioned exposure, written by adm0_exp.ipynb)"
  - "blob: ds-storm-impact-harmonisation/processed/adam_gdacs_per_storm_source_diagnostics.csv (written by source_exposure/source_diagnostics.py)"
  - "blob: ds-storm-impact-harmonisation/raw/pdc/cyclones/ — raw PDC cyclone captures (polls/<ts>/_list.json + hazards/<uuid>/<updatedAt>.json), 3-hourly"
  - "Azure web app slot chd-pa-aa-fji-storms-app/global-cyclones — adm0 exposure explorer (adm0_exp_app.py)"
  - "Excel workbook: src/source_exposure/out/historical_tropical_cyclone_pop_exposure_estimates_AL_EP_basins.xlsx (local, gitignored)"
dependencies:
  - ocha-stratus
  - "ocha-relay (v0.2.0, for Listmonk)"
  - marimo
  - geopandas
  - plotnine
  - statsmodels
  - openpyxl
  - python-dotenv
  - "Listmonk list ID 25 (test list)"
  - "Secrets: DSCI_AZ_BLOB_DEV_SAS, DSCI_LISTMONK_BASE_URL, DSCI_LISTMONK_API_USERNAME, DSCI_LISTMONK_API_KEY"
downstream:
  - "ds-storms-alerts (vendors TWO files from src/source_exposure/ — fm_matching.py and style.py→src/xlsx_style.py — kept code-identical; a third vendored file triggers de-vendoring into a shared package)"
  - "ds-cerf-3rm-app (CERF predictor was PORTED there; the old chd-ds-seas5-viz/cerf-rr slot was deleted 2026-08-03, ADR 0006)"
  - "chd-pa-aa-fji-storms-app global-cyclones slot (exposure explorer)"
depends_on:
  - storms-pipeline
  - nhc-forecast
  - listmonk
surfaces:
  - {url: "https://ocha-dap.github.io/ds-storm-impact-harmonisation/", kind: landing, title: "Storm impact harmonisation site landing page (manifest-driven, pages/products/*/page.toml)"}
source_repo: ocha-dap/ds-storm-impact-harmonisation
source_branch: main
source_sha: 210860c
code_ref:
  - "scripts/daily_gdacs_monitor_email.py — GHA cron entrypoint: fetch active GDACS storms, render HTML email, send via Listmonk"
  - "src/gdacs_monitor_email.py — email rendering helpers (strip charts, historical baseline load)"
  - "src/datasets/gdacs.py — GDACS REST API client"
  - "src/datasets/cerf.py — CERF GMS API client + CERFCODE_TO_SID authoritative mapping"
  - "src/models/cerf_inform.py — CERF rapid-response allocation predictor (OLS on INFORM Composite)"
  - "src/source_exposure/ — three-source (CHD / GDACS / ADAM) exposure comparison module; fm_matching.py and style.py both vendored to ds-storms-alerts"
  - "app/cerf_predictor.py — marimo CERF predictor; NO LONGER DEPLOYED from here (ported to ds-cerf-3rm-app, slot deleted 2026-08-03)"
  - "adm0_exp_app.py — marimo app deployed to chd-pa-aa-fji-storms-app global-cyclones slot"
  - "compare_exposure.py — marimo app for interactive CHD/GDACS/ADAM comparison (dev, not deployed; on merge-cerf-exposure)"
  - "storm_impact_app.py — marimo app: NHC tracks + WSP + exposure plots (dev, uses stratus stage=dev; ON nhc-exp-app branch, NOT on pinned merge-cerf-exposure SHA)"
  - "src/utils/exposure.py — raster clip helpers, IBTrACS exposure calculations (ON nhc-exp-app/usa-radii-exp, NOT on merge-cerf-exposure)"
  - "adm0_exp.ipynb (adm0_exp.md) — notebook: computes CHD ADM0 historical exposure from WorldPop + IBTrACS buffers, uploads to blob (ON nhc-exp-app/usa-radii-exp, NOT on merge-cerf-exposure)"
  - "adm0_exp_app.py — note this file lives on nhc-exp-app/usa-radii-exp, NOT on the pinned merge-cerf-exposure SHA; usa-radii-exp is the branch actually deployed to the global-cyclones slot"
extra:
  adm0_exp_app_note: "adm0_exp_app.py runs on prod DB (stage=dev in code but uses prod stratus for ibtracs_storms). Deployed to chd-pa-aa-fji-storms-app global-cyclones slot from usa-radii-exp branch — NOT the main current-work branch."
  storm_impact_app_note: "storm_impact_app.py (merge-cerf-exposure) uses stratus stage=dev throughout. It is the NHC-specific visualiser (buffers, WSP polygons, exposure time series). Currently on merge-cerf-exposure only, not deployed to a named slot."
  three_source_comparison: "src/source_exposure produces a styled Excel archive workbook comparing CHD / GDACS / ADAM at ADM0 and ADM1. GDACS ≈ ADAM (Spearman 0.96-0.997; ADAM ingests GDACS upstream). CHD is systematically lower at higher wind thresholds. fm_matching.py is the authoritative admin-1 matcher; style.py is the workbook styling. ds-storms-alerts vendors code-identical copies of BOTH (docstrings differ; style.py → src/xlsx_style.py there). Agreed in review: a third vendored file triggers de-vendoring into a shared package."
  workbook_identity_columns: "Archive workbook (workbook.py) identity columns aligned with the alerts attachment and DB (PR #11, merge-cerf-exposure): storm key is atcf_id (NHC ATCF id like AL132025) on every tab — was storm_id, which collided with the DB's slug-valued storms.nhc_storms.storm_id (e.g. melissa_2025); sources joined with | (rendering CHD|GDACS|ADAM), was +; admin_pcode retained (an earlier rename to pcode was reverted)."
  cerf_predictor_note: "CERF rapid-response allocation predictor uses INFORM Composite OLS on 2016+ 3RM data. NO LONGER DEPLOYED FROM THIS REPO — ported to ds-cerf-3rm-app (https://cerf-3rm.azurewebsites.net); the chd-ds-seas5-viz/cerf-rr slot was deleted 2026-08-03 (ADR 0006). app/cerf_predictor.py survives here as a deployment-less duplicate and will drift; edit the ds-cerf-3rm-app copy. It uses app/pyproject.toml (Python 3.10) separately from the root env (Python 3.12)."
  deployments_md_status: "deployments.md lists chd-pa-aa-fji-storms-app as belonging to repo pa-aa-fji-storms-app (incorrect for the global-cyclones slot, which this repo deploys). [gap] The cerf-rr slot reference has been removed from deployments.md as of 2026-08-03 (slot deleted)."
  branch_layout: "Resolved 2026-08-03. This repo previously split work across THREE unmerged feature branches (merge-cerf-exposure, nhc-exp-app, usa-radii-exp) with main carrying only workflow triggers that checked those branches out at runtime. All are now merged into main (PR #3) and deleted. main is the single trunk. ONE branch is deliberately kept unmerged: gdacs-adam-data (Hannah Ker's cyclone exposure dashboard, 86k lines) — ADR 0004 retired it, closing PR #2 without merging and explicitly keeping the branch as the only place that dashboard exists. Do not delete it and do not propose merging it; both were considered and rejected."
visibility: internal
last_synced: "2026-06-22"
---

# Storm Impact Harmonisation

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Four-times-daily: fetch active GDACS tropical cyclones → compare per-country population exposure against CHD historical baseline → email digest via Listmonk. Also produces a three-source (CHD / GDACS / ADAM) exposure comparison workbook and several marimo apps for storm impact exploration.*

## Jobs & schedule

This repo runs several distinct pipelines and deploys several apps:

| job | ref | schedule | status |
|---|---|---|---|
| Daily GDACS Monitor Email | `.github/workflows/daily-gdacs-monitor-email.yml` | `20 3,9,15,21 * * *` (4× daily, 20 min after NHC TCM synoptic cycles) | live |
| PDC Cyclone Poll | `.github/workflows/pdc-cyclone-poll.yml` | `40 */3 * * *` (2× the 6-hourly synoptic advisory rate) | live |
| Deploy Pages site | `.github/workflows/deploy-app.yml` | on push to `main` | live |
| Deploy adm0 exposure explorer | `.github/workflows/usa-radii-exp_chd-pa-aa-fji-storms-app(global-cyclones).yml` | `workflow_dispatch` only | manual |
| ~~Deploy CERF predictor app~~ | *(workflow deleted)* | — | **retired 2026-08-03** — app ported to [`ds-cerf-3rm-app`](../apps/cerf-3rm-app.md); slot deleted (ADR 0006) |

**Branch layout (resolved 2026-08-03).** This repo used to run everything off feature branches, with workflows on `main` checking out `merge-cerf-exposure` at runtime because GHA `schedule:` only fires from the default branch. All trunks have now been merged into `main` (PR #3) and the feature branches deleted, so every workflow runs `main` directly and the `ref:` indirections are gone. `gdacs-adam-data` is the one branch deliberately kept unmerged — see [0004](https://github.com/OCHA-DAP/ds-storm-impact-harmonisation/blob/main/docs/decisions/0004-retire-the-cyclone-exposure-dashboard.md).

## Inputs

- **GDACS REST API** — live tropical cyclone events and per-country exposure (`/api/export/gettimeline`, `/api/export/getimpact`). No auth required. Available 2015+ (timeline), ~2022+ (impact).
- **CHD historical exposure blob** — `ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp_all.parquet` — IBTrACS-derived global storm exposure at ADM0 since 2001. Used as the baseline for the email's context strip charts. Written by `adm0_exp.ipynb`.
- **DB (dev stage)** — `storms.nhc_tracks_fcast_exposure`, `nhc_tracks_obsv_exposure`, `nhc_tracks_fcastonly_exposure`, `nhc_wsp_exposure`, `nhc_wsp_fcastonly_exposure`, WSP polygon tables, and track buffer tables. Read by `storm_impact_app.py` and `compare_exposure.py`.
- **DB (prod stage)** — `storms.ibtracs_tracks_geo`, `storms.ibtracs_storms`, `storms.nhc_storms`. Read by `adm0_exp_app.py` and `compare_exposure.py`.
- **DB — GDACS/ADAM exposure** — `storms.gdacs_exposure`, `storms.adam_exposure`, `storms.storm_id_lookup`, `storms.gdacs_fm_lookup`. Written by the storms-pipeline; read here for cross-source comparison.
- **CERF GMS API** — `https://cerfgms-webapi.unocha.org/v1/application/All.xml` — historical CERF rapid-response allocations.
- **INFORM Risk** — via `src/datasets/inform.py`; feeds the CERF predictor model.
- **Worldpop COG raster** — `raster` container: `worldpop/pop_count/global_pop_2026_CN_1km_R2025A_UA_v1.tif`. Used to compute CHD historical exposure in `adm0_exp.ipynb`.
- **FieldMaps boundaries** — `global` container: `fieldmaps/edge-matched/humanitarian/intl/adm1/{iso3}.parquet`. Used for country name resolution in `compare_exposure.py`.

## Steps

**Daily email pipeline** (`scripts/daily_gdacs_monitor_email.py`):
1. Fetch currently-active tropical cyclones from GDACS API (all basins).
2. For each active event fetch per-country exposure at buffer39 (34 kt) and buffer74 (64 kt).
3. Load CHD historical baseline from blob (`adm0_ibtracs_exp_all.parquet`).
4. For each affected country, render a strip chart (plotnine) showing current exposure vs historical distribution.
5. Assemble HTML email embedding charts as base64 data URIs.
6. Create Listmonk campaign and send to configured list ID.

Supports `--dry-run` (write HTML to disk, no Listmonk) and `--inspect` (create draft campaign, print recipients, open preview in browser, no send).

**Source exposure comparison workbook** (`src/source_exposure/`):
- `source_diagnostics.py` probes GDACS/ADAM for each NHC storm — classifies coverage as `have_exposure` / `reported_zero` / `partial_no_final` / `unservable` / `csv_403` / etc. Uploads diagnostic CSV to blob.
- `workbook.py` builds a styled Excel workbook with tabs: `storms` (all NHC storms 2001+, source coverage), `adm0_exposure`, `adm1_exposure`, `caveats`, `README`. Identity columns (aligned across the archive workbook, the alerts attachment and the DB — PR #11): the storm key is **`atcf_id`** (the NHC ATCF id, e.g. `AL132025`) on every tab — it was `storm_id`, but that collided with the DB's slug-valued `storms.nhc_storms.storm_id` (e.g. `melissa_2025`); the `sources` column is joined with **`|`** (`CHD|GDACS|ADAM`), previously `+`; `admin_pcode` is retained.
- `fm_matching.py` maps GDACS/ADAM admin units onto FieldMaps pcodes; `style.py` holds the workbook styling. **Both are vendored code-identical into ds-storms-alerts** (`fm_matching.py` → `src/fm_matching.py`; `style.py` → `src/xlsx_style.py`, docstrings differ); any change here must be mirrored there. Agreed threshold in review: a **third** vendored file triggers de-vendoring into a shared package.

**CHD historical exposure calculation** (`adm0_exp.ipynb`):
- Load IBTrACS-derived wind buffers from blob; load WorldPop COG from blob.
- For each ADM0 polygon, clip WorldPop to wind buffer intersections; sum population.
- Upload per-country parquets and combined `adm0_ibtracs_exp_all.parquet` to blob.

## Outputs

- **Listmonk email campaign** — daily GDACS monitor digest; test list ID 25; prod list passed via `--list-id` argument or GHA input.
- **blob** `ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp_all.parquet` — CHD global historical exposure (all IBTrACS storms, ADM0).
- **blob** `ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp/{iso3}_exp.parquet` — per-country partitioned exposure.
- **blob** `ds-storm-impact-harmonisation/processed/adam_gdacs_per_storm_source_diagnostics.csv` — GDACS/ADAM per-storm source coverage diagnostic.
- **blob** `ds-storm-impact-harmonisation/raw/pdc/cyclones/` — raw PDC cyclone captures, written 3-hourly. PDC serves no archive and no track history, so this record exists only going forward.
- **Azure app slot** `chd-pa-aa-fji-storms-app/global-cyclones` — IBTrACS ADM0 exposure explorer (marimo).
- **Excel workbook** `src/source_exposure/out/historical_tropical_cyclone_pop_exposure_estimates_AL_EP_basins.xlsx` — generated locally; gitignored.

## Dependencies

- `ocha-stratus` — blob and DB access
- `ocha-relay` (v0.2.0) — Listmonk client for sending email campaigns
- `marimo` — interactive app runtime (deployed + dev apps)
- `plotnine` — strip charts in email
- `statsmodels` — OLS model for CERF predictor
- `openpyxl` — Excel workbook generation
- `python-dotenv` — local `.env` loading
- **Listmonk list ID 25** — test/staging list; prod list ID is a runtime parameter
- **Secrets** (GHA repo secrets): `DSCI_AZ_BLOB_DEV_SAS`, `DSCI_LISTMONK_BASE_URL`, `DSCI_LISTMONK_API_USERNAME`, `DSCI_LISTMONK_API_KEY`
- **Azure publish profile secrets** for the two app deployments

## Failure modes & debugging

- **GHA email job fails / email not received**: The schedule fires from `main` but checks out `merge-cerf-exposure`. If that branch is force-pushed or the checkout ref changes, the job will fail with a git ref error. Check the Actions run log on GitHub.
- **GDACS API unreachable or returns empty**: `get_active_cyclones()` and `get_impact_by_country()` have retry logic (`MAX_RETRIES=3`, 5s delay). If GDACS is down, the script exits gracefully with a stub email ("no active storms"). Genuine GDACS data gaps are logged as `WARN fetch failed for eventid=…`.
- **Blob not found**: If `adm0_ibtracs_exp_all.parquet` is missing, the email will fail at `load_ocha_historical()`. Re-run `adm0_exp.ipynb` manually to regenerate.
- **DB connectivity**: All marimo apps that use `stratus.get_engine(stage="dev")` require `PGSSLMODE=require` and the dev DB credentials. The deployed apps need these set in Azure App Service → Configuration → Environment variables.
- **Listmonk campaign created but not sent**: Check if `--auto-send` flag is present in GHA workflow `run:` step. The workflow passes `--auto-send` for scheduled runs; omitting it requires interactive confirmation (not possible in GHA).
- **Excel workbook build fails**: `source_diagnostics.py` requires `ocha_lens` (from the ds-storms-pipeline venv). `workbook.py` requires `openpyxl`. The diagnostic CSV is pre-uploaded to blob as a hand-off; `build.py` can rebuild the workbook from blob alone with `python -m src.source_exposure.build`.
- **Vendored files diverge from ds-storms-alerts**: `src/source_exposure/fm_matching.py` and `src/source_exposure/style.py` must stay code-identical to their vendored copies in ds-storms-alerts (`src/fm_matching.py` and `src/xlsx_style.py` respectively; only docstrings differ). Any change here must be mirrored there. Track ds-storms-alerts PR #14 / this repo PR #8 (fm_matching), and ds-storms-alerts PR #20 / this repo PR #11 (style→xlsx_style). Agreed in review: a third vendored file triggers de-vendoring into a shared package.
- **Logs**: GHA Actions tab on the repo (no Databricks logs — this is GHA-only).

## Downstream consumers

- **ds-storms-alerts** — vendors **two** files from this repo's `src/source_exposure/`: `fm_matching.py` (→ `src/fm_matching.py`) and `style.py` (→ `src/xlsx_style.py`). Both are kept code-identical (docstrings aside); changes must be mirrored there (fm_matching: PR #14 / #8; style→xlsx_style: PR #20 / #11). A third vendored file triggers de-vendoring into a shared package. The alerts email attachment is now a styled per-storm xlsx mirroring this repo's archive workbook — see [storms-alerts](./storms-alerts.md).
- **[ds-cerf-3rm-app](../apps/cerf-3rm-app.md)** — the CERF predictor was ported there and is served at <https://cerf-3rm.azurewebsites.net>. The old `chd-ds-seas5-viz/cerf-rr` slot was deleted 2026-08-03; `app/cerf_predictor.py` remains in this repo as a deployment-less duplicate (ADR 0006).
- **chd-pa-aa-fji-storms-app (global-cyclones slot)** — ADM0 exposure explorer served from this repo.
