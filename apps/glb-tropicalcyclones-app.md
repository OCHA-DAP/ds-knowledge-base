---
content_type: app
name: glb-tropicalcyclones-app
purpose: Interactive return-period explorer for tropical cyclones — lets users dial wind-speed and distance thresholds to determine which historical storms would have triggered for any country, and cross-checks against EM-DAT impact and CERF allocation data.
status: live
tech: dash
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-glb-tropicalcyclones-app
  url: https://chd-ds-glb-tropicalcyclones-app.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "data/all_adm0_thresholds.parquet — pre-computed per-country cyclone threshold matrix (IBTrACS-derived, bundled in repo)"
  - "data/ibtracs_with_wmo_wind.parquet — IBTrACS best-track points with WMO wind speed (bundled in repo)"
  - "data/gaul0_asap_v04/gaul0_asap.shp — GAUL L0 admin boundaries (ASAP v04, bundled in repo)"
  - "data/emdat-tropicalcyclone-2000-2022-processed-sids.csv — EM-DAT tropical cyclone impact data matched to IBTrACS SIDs (bundled in repo)"
  - "data/cerf-storms-with-sids-2024-02-27.csv — CERF storm allocation data matched to IBTrACS SIDs (bundled in repo)"
depends_on: []
source_repo: ocha-dap/ds-glb-tropicalcyclones-app
source_branch: add-return-period
source_sha: 3dd2e5b
code_ref:
  - app.py
  - migrate_data.py
extra:
  data_bundled_in_repo: true
  data_origin: >
    All data files are committed to the repo under data/ rather than loaded
    from blob at runtime. migrate_data.py (reads AA_DATA_DIR / AA_DATA_DIR_NEW
    env vars) was used to populate the data/ directory from the old shared
    AA_DATA dir convention; this script is a one-time migration aid, not a
    live pipeline step.
  upstream_analysis_repo: ocha-dap/ds-glb-tropicalcyclones
  ibtracs_coverage: "Tracks up to 2022 inclusive. WMO validation lag means some 2022 storms are excluded."
  antimeridian_known_issue: "Cyclones near 180 deg may be erroneously excluded (distance calculation artefact)."
  internal_alert_in_ui: "App displays a red banner marking it as an internal tool under development."
  no_ocha_stratus: "Predates ocha-stratus; reads only from bundled local files. No DB or blob access at runtime."
  heroku_branch: "A heroku/master remote ref exists (2024-03-01), indicating the app was previously deployed on Heroku before migrating to Azure."
  deploy_slot: "GHA deploys to the 'development' slot of chd-ds-glb-tropicalcyclones-app (slot-name: 'development', environment: 'development'), NOT the production slot. The deployments.md URL is the prod-slot URL; the auto-deployed add-return-period build lands on the dev slot."
discrepancies:
  - "[conflict] GHA auto-deploy targets the app's 'development' slot (slot-name: 'development') from branch add-return-period, but deployments.md lists only the production-slot app/URL as Running. The return-period feature is deployed to the DEV slot; the prod-slot contents/branch are not confirmed and may be older (e.g. pre-return-period main)."
  - "[stale] main (2024-01-18) lacks the return-period feature; the active/deployed branch is add-return-period (2024-05-17). main should not be deployed."
  - "[stale] heroku/master remote ref (2024-03-01) is a defunct prior Heroku deployment; superseded by the Azure deploy. Informational only."
  - "[gap] No automated data-refresh pipeline: all data/ files are committed manually. IBTrACS/EM-DAT coverage ends 2022, CERF ends 2024-02-27; data goes stale silently until someone reruns ds-glb-tropicalcyclones and commits new outputs."
  - "[gap] Antimeridian (180 deg) distance artefact can erroneously exclude Pacific cyclones, underestimating return periods for those nations (surfaced in-UI but unfixed)."
visibility: internal
last_synced: "2026-06-17"
---

# Global Tropical Cyclones Return Period App

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A humanitarian-action planning tool for exploring tropical cyclone return periods globally. A user selects a country, then adjusts two sliders — maximum sustained wind speed (30–185 knots) and distance from country boundary (0–400 km) — plus a start year, to define an AA-style trigger condition. The app instantly computes how many historical IBTrACS cyclones would have met that condition and returns the implied return period in years. A map panel plots the qualifying cyclone tracks. Two supplementary bar-chart panels let the user assess trigger quality: one shows EM-DAT impact data (deaths, affected people, or economic damage) per cyclone colour-coded by whether the trigger would have fired; the other shows matched CERF emergency allocations. The app is marked internally as "under development" via a dismissable red alert.

## Key features

- Country dropdown (GAUL L0, all countries with IBTrACS coverage)
- Wind speed and distance sliders with live return-period calculation
- Start-year selector (1851–2022) to bound the analysis window
- Mapbox choropleth showing the selected country boundary plus triggered cyclone tracks
- EM-DAT impact bar chart (Total Deaths / Total Affected / Total Damage) with triggered/not-triggered colour coding
- CERF allocation bar chart with the same triggered/not-triggered colour coding
- Methodology and data-source footnotes in the UI
- Known-issue banners: antimeridian exclusion artefact; 2022 WMO validation lag

The underlying distance/threshold analysis is from `ocha-dap/ds-glb-tropicalcyclones` (a separate repo); this app only visualises pre-computed outputs.

## Data

All data is **bundled directly in the repo** under `data/` — there is no live DB or blob fetch at runtime. This makes the app self-contained but means data staleness is tied to manual repo updates.

| File | Source | Coverage |
|---|---|---|
| `all_adm0_thresholds.parquet` | IBTrACS, processed by `ds-glb-tropicalcyclones` | up to 2022 |
| `ibtracs_with_wmo_wind.parquet` | IBTrACS with WMO agency wind | up to 2022 |
| `gaul0_asap_v04/gaul0_asap.shp` | FAO GAUL L0 (ASAP v04) | static reference |
| `emdat-tropicalcyclone-2000-2022-processed-sids.csv` | EM-DAT, matched to IBTrACS SIDs | 2000–2022 |
| `cerf-storms-with-sids-2024-02-27.csv` | CERF Allocation Summaries, matched to SIDs | up to 2024-02-27 |

`migrate_data.py` is a one-off utility that populated `data/` from the old `AA_DATA_DIR` environment convention; it is not invoked at runtime and can be ignored once the data directory is populated.

Data freshness is static until someone reruns the upstream analysis in `ds-glb-tropicalcyclones` and commits new parquet/CSV files to this repo.

## Deployment & access

Azure Web App `chd-ds-glb-tropicalcyclones-app`, resource group `IMB-CHD-DataScience-EastUS2`, state Running per `infrastructure/deployments.md` (prod-slot URL below).

- Prod-slot URL: https://chd-ds-glb-tropicalcyclones-app.azurewebsites.net
- **Deploys to the `development` SLOT, not prod.** The GHA workflow (`.github/workflows/add-return-period_chd-ds-glb-tropicalcyclones-app(development).yml`) runs `azure/webapps-deploy@v2` with `slot-name: 'development'` and `environment: 'development'`, triggered on push to `add-return-period` (or manual `workflow_dispatch`). So the live return-period build lands on the dev slot; the deployments.md row is the production slot, whose branch/contents are not confirmed.
- Served via Gunicorn (`gunicorn==21.2.0` in `requirements.txt`; WSGI object is `server = app.server` in `app.py`)
- Access: internal — the UI carries a dismissable red "internal tool under development" banner
- Previously on Heroku (`heroku/master` ref, 2024-03-01); migrated to Azure.

See `infrastructure/deployments.md` for the registry row.

## Maintenance / known issues

**Redeployment:** pushing to `add-return-period` triggers the GHA workflow, which builds and deploys to the **`development` slot**. To refresh data first, re-run the upstream analysis in `ds-glb-tropicalcyclones` and commit new `data/` outputs here, then push (CLI/job detail lives in that repo and the workflow file — not restated here).

**Dev-slot vs prod-slot gotcha:** CI deploys only to the `development` slot. The production slot served at the deployments.md URL is updated separately (slot swap or manual deploy) — its branch/build are unconfirmed and may predate the return-period feature. `main` (2024-01-18) lacks return-period; `add-return-period` (2024-05-17) is the active branch and `source_sha` anchor (`3dd2e5b`). Verify what the prod slot actually serves before assuming it matches the dev build.

**Known data issues (surfaced in the UI):**
- Cyclones near the antimeridian (180°) may be erroneously excluded due to EPSG:3857 distance calculation artefact — return period will be underestimated for Pacific island nations.
- Some 2022 cyclones are excluded pending WMO best-track validation in IBTrACS.

**Data staleness:** IBTrACS coverage ends at 2022; EM-DAT ends at 2022; CERF data ends 2024-02-27. No automated update pipeline exists — data must be manually refreshed and committed.

**No ocha-stratus / no live data pull:** predates the team's ocha-stratus convention. Updating to pull from blob at startup would be the correct modernisation path.
