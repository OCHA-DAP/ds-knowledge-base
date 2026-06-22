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
    - { name: "Deploy CERF predictor app (cerf-rr slot)", ref: ".github/workflows/merge-cerf-exposure_chd-ds-seas5-viz(cerf-rr).yml", schedule: "on push to merge-cerf-exposure", status: live }
    - { name: "Deploy adm0_exp_app (global-cyclones slot)", ref: ".github/workflows/usa-radii-exp_chd-pa-aa-fji-storms-app(global-cyclones).yml", schedule: "on push to usa-radii-exp", status: live }
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
  - "Azure web app slot chd-ds-seas5-viz/cerf-rr — CERF predictor marimo app (app/cerf_predictor.py)"
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
  - "ds-storms-alerts (vendors fm_matching.py from src/source_exposure/fm_matching.py — kept byte-identical)"
  - "chd-ds-seas5-viz cerf-rr slot (CERF predictor app)"
  - "chd-pa-aa-fji-storms-app global-cyclones slot (exposure explorer)"
depends_on:
  - pipelines/storms-pipeline
  - pipelines/nhc-forecast
  - infrastructure/comms-listmonk
source_repo: ocha-dap/ds-storm-impact-harmonisation
source_branch: merge-cerf-exposure
source_sha: 210860c
code_ref:
  - "scripts/daily_gdacs_monitor_email.py — GHA cron entrypoint: fetch active GDACS storms, render HTML email, send via Listmonk"
  - "src/gdacs_monitor_email.py — email rendering helpers (strip charts, historical baseline load)"
  - "src/datasets/gdacs.py — GDACS REST API client"
  - "src/datasets/cerf.py — CERF GMS API client + CERFCODE_TO_SID authoritative mapping"
  - "src/models/cerf_inform.py — CERF rapid-response allocation predictor (OLS on INFORM Composite)"
  - "src/source_exposure/ — three-source (CHD / GDACS / ADAM) exposure comparison module; fm_matching.py vendored to ds-storms-alerts"
  - "app/cerf_predictor.py — marimo app deployed to chd-ds-seas5-viz cerf-rr slot"
  - "adm0_exp_app.py — marimo app deployed to chd-pa-aa-fji-storms-app global-cyclones slot"
  - "compare_exposure.py — marimo app for interactive CHD/GDACS/ADAM comparison (dev, not deployed; on merge-cerf-exposure)"
  - "storm_impact_app.py — marimo app: NHC tracks + WSP + exposure plots (dev, uses stratus stage=dev; ON nhc-exp-app branch, NOT on pinned merge-cerf-exposure SHA)"
  - "src/utils/exposure.py — raster clip helpers, IBTrACS exposure calculations (ON nhc-exp-app/usa-radii-exp, NOT on merge-cerf-exposure)"
  - "adm0_exp.ipynb (adm0_exp.md) — notebook: computes CHD ADM0 historical exposure from WorldPop + IBTrACS buffers, uploads to blob (ON nhc-exp-app/usa-radii-exp, NOT on merge-cerf-exposure)"
  - "adm0_exp_app.py — note this file lives on nhc-exp-app/usa-radii-exp, NOT on the pinned merge-cerf-exposure SHA; usa-radii-exp is the branch actually deployed to the global-cyclones slot"
extra:
  branch_note: "Active work lives on merge-cerf-exposure; main carries only the GHA schedule trigger. The daily-gdacs-monitor-email workflow on main checks out merge-cerf-exposure at runtime (ref: merge-cerf-exposure) — this is a deliberate workaround because GitHub only fires schedule triggers from the default branch. When merge-cerf-exposure lands on main, the ref: line in the workflow must be removed."
  adm0_exp_app_note: "adm0_exp_app.py runs on prod DB (stage=dev in code but uses prod stratus for ibtracs_storms). Deployed to chd-pa-aa-fji-storms-app global-cyclones slot from usa-radii-exp branch — NOT the main current-work branch."
  storm_impact_app_note: "storm_impact_app.py (merge-cerf-exposure) uses stratus stage=dev throughout. It is the NHC-specific visualiser (buffers, WSP polygons, exposure time series). Currently on merge-cerf-exposure only, not deployed to a named slot."
  three_source_comparison: "src/source_exposure produces a styled Excel workbook comparing CHD / GDACS / ADAM at ADM0 and ADM1. GDACS ≈ ADAM (Spearman 0.96-0.997; ADAM ingests GDACS upstream). CHD is systematically lower at higher wind thresholds. fm_matching.py is the authoritative admin-1 matcher; ds-storms-alerts vendors a byte-identical copy."
  cerf_predictor_note: "CERF rapid-response allocation predictor uses INFORM Composite OLS on 2016+ 3RM data. Deployed to chd-ds-seas5-viz cerf-rr slot (not the main seas5-viz content). Uses app/pyproject.toml (Python 3.10) separately from the root dev env (Python 3.12)."
  deployments_md_status: "deployments.md lists chd-pa-aa-fji-storms-app as belonging to repo pa-aa-fji-storms-app (incorrect for the global-cyclones slot, which this repo deploys). chd-ds-seas5-viz cerf-rr slot is not separately listed — it is a deployment slot of the seas5-viz app. Neither GHA deploy workflow here is yet in deployments.md's GHA-pipelines table; nor is the daily-gdacs-monitor-email cron. [gap]"
  branch_split: "[conflict] This repo's relevant code is split across THREE feature branches; none is merged to main. (1) merge-cerf-exposure (HEAD 210860c) = GDACS email pipeline, src/source_exposure, src/datasets, src/models, app/cerf_predictor.py — the bulk of this page; deploys the CERF predictor to chd-ds-seas5-viz/cerf-rr. (2) nhc-exp-app (HEAD 0d165cd) = storm_impact_app.py, adm0_exp_app.py, adm0_exp.ipynb, src/utils/exposure.py, total_pop_calc.ipynb — does NOT contain the GDACS email/source_exposure code. (3) usa-radii-exp (HEAD 58fb837) = adm0_exp_app.py + the global-cyclones deploy workflow; this is the branch actually deployed to chd-pa-aa-fji-storms-app/global-cyclones. The original page pinned source_sha=0d165cd (nhc-exp-app), which does NOT contain most of what the page documents — corrected to source_branch/source_sha = merge-cerf-exposure/210860c (the primary subject). code_ref entries that live only on nhc-exp-app/usa-radii-exp are annotated inline. main (cf36bbf) carries ONLY the daily-gdacs-monitor-email.yml schedule trigger, which checks out merge-cerf-exposure at runtime."
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
| Deploy CERF predictor app | `.github/workflows/merge-cerf-exposure_chd-ds-seas5-viz(cerf-rr).yml` | on push to `merge-cerf-exposure` | live |
| Deploy adm0 exposure explorer | `.github/workflows/usa-radii-exp_chd-pa-aa-fji-storms-app(global-cyclones).yml` | on push to `usa-radii-exp` | live |

**Important branch quirk:** The GHA `schedule:` trigger only fires from the default branch (`main`). The GDACS email workflow lives on `main` but explicitly checks out `merge-cerf-exposure` at runtime (`with: ref: merge-cerf-exposure`) to get the current scripts and src. This means the deployed runtime code is always `merge-cerf-exposure` not `main`. When that branch merges, the `ref:` line in the workflow must be removed.

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
- `workbook.py` builds a styled Excel workbook with tabs: `storms` (all NHC storms 2001+, source coverage), `adm0_exposure`, `adm1_exposure`, `caveats`, `README`.
- `fm_matching.py` maps GDACS/ADAM admin units onto FieldMaps pcodes. **Vendored byte-identical into ds-storms-alerts** (`src/fm_matching.py`); any change here must be mirrored there.

**CHD historical exposure calculation** (`adm0_exp.ipynb`):
- Load IBTrACS-derived wind buffers from blob; load WorldPop COG from blob.
- For each ADM0 polygon, clip WorldPop to wind buffer intersections; sum population.
- Upload per-country parquets and combined `adm0_ibtracs_exp_all.parquet` to blob.

## Outputs

- **Listmonk email campaign** — daily GDACS monitor digest; test list ID 25; prod list passed via `--list-id` argument or GHA input.
- **blob** `ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp_all.parquet` — CHD global historical exposure (all IBTrACS storms, ADM0).
- **blob** `ds-storm-impact-harmonisation/processed/adm0_ibtracs_exp/{iso3}_exp.parquet` — per-country partitioned exposure.
- **blob** `ds-storm-impact-harmonisation/processed/adam_gdacs_per_storm_source_diagnostics.csv` — GDACS/ADAM per-storm source coverage diagnostic.
- **Azure app slot** `chd-ds-seas5-viz/cerf-rr` — CERF predictor (INFORM-based OLS model predicting CERF rapid-response allocation size).
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
- **fm_matching diverges from ds-storms-alerts**: `src/source_exposure/fm_matching.py` and `ds-storms-alerts/src/fm_matching.py` must remain byte-identical. Track ds-storms-alerts PR #14 / this repo PR #8.
- **Logs**: GHA Actions tab on the repo (no Databricks logs — this is GHA-only).

## Downstream consumers

- **ds-storms-alerts** — vendors `fm_matching.py` from this repo's `src/source_exposure/fm_matching.py`. Changes to the matcher must be mirrored there (PR #14 / #8).
- **chd-ds-seas5-viz (cerf-rr slot)** — CERF predictor app served from this repo.
- **chd-pa-aa-fji-storms-app (global-cyclones slot)** — ADM0 exposure explorer served from this repo.
