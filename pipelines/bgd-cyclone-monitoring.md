---
content_type: pipeline
name: bgd-cyclone-monitoring
type: monitoring
status: live
deployment:
  platform: azure-webapp
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - name: ds-aa-bgd-cyclone-monitoring
      ref: "https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net"
      schedule: on-demand
      status: live   # Azure registry state: Running; repo column unmapped (—) in deployments.md
    - name: container-registry GHA build
      ref: ".github/workflows/container-registry.yaml"
      schedule: "push to master + workflow_dispatch (manual)"
      status: live
inputs:
  - "data/bgd_adm_sel_bbs_20201113_shp.gpkg (ADM4 union boundaries, bundled in container image)"
  - "user-supplied landfall coordinates (lon/lat) and wind speed (km/h)"
  - "user-supplied trigger threshold (km/h, default 118)"
outputs:
  - "in-browser map: union polygons coloured by whether wind speed exceeds threshold"
  - "Division Summary Table: unions above threshold per division (in-app, downloadable CSV)"
  - "Union Wind Speed Table: per-union distance, reduction factor, estimated wind speed (downloadable CSV)"
dependencies:
  - "R 4.5.0 (rocker/r-ver:4.5.0 base image)"
  - "shiny, shinyWidgets, leaflet, leaflet.extras2, DT, sf, tidyverse, rmapshaper"
  - "AzureStor (imported but not called in current code)"
  - "Docker + Azure Container Registry (ACR_ENDPOINT, ACR_USERNAME, ACR_PASSWORD secrets)"
  - "Azure App Service (IMB-CHD-DataScience-EastUS2)"
downstream:
  - "frameworks/bgd-cyclone (BGD tropical-cyclone AA framework, v2025-04-25) — operators use this tool to assess whether a forecast cyclone meets the trigger across the same 6 coastal ADM2 districts"
depends_on: []
source_repo: ocha-dap/ds-aa-bgd-cyclone-monitoring
source_branch: master
source_sha: f88a623
code_ref:
  - app.R
  - .github/workflows/container-registry.yaml
  - Dockerfile
extra:
  content_type_note: >
    This is an INTERACTIVE APP (Shiny), not a scheduled pipeline. The pipeline
    template is used here because it was ingested as part of the pipelines batch;
    a future sweep should move it to apps/ and apply the app schema.
  schema_strain: "content_type should be 'app' not 'pipeline'; no scheduled jobs, no upstream data pipeline reads"
  districts_in_scope: "Barguna, Bhola, Patuakhali, Noakhali, Satkhira, Khulna (ADM2 coastal districts)"
  wind_model: "0.9807 * exp(-0.003 * distance_km) applied to each union's boundary distance from landfall point"
  azurestor_status: >
    AzureStor is loaded in app.R but no download_blob/get_blob calls exist in current code.
    The DSCI_AZ_BLOB_DEV_SAS build arg appears in commented-out Docker commands in R/lines.R,
    suggesting blob data loading was planned/prototyped but the shipped app bundles the GeoPackage locally.
  deploy_url: "https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net"
  ci_trigger: "push to master branch (or manual workflow_dispatch) triggers container-registry.yaml GHA workflow to build + push to ACR; image tag shiny-azure-app-service"
  discrepancies:
    - "[conflict] App self-labels 'This tool is in development.' (app.R line 146) but is deployed and Running in the Azure registry (deployments.md, state Running). Page status is 'live' to match the deployment; the in-app dev banner is the real operational caveat."
    - "[gap] deployments.md lists app `ds-aa-bgd-cyclone-monitoring` with an empty repo column (—); the app→repo mapping is not recorded in the registry even though the repo is ocha-dap/ds-aa-bgd-cyclone-monitoring. The container build GHA workflow is also not in the registry's GitHub Actions table (that table tracks scheduled pipelines; this is a build-on-push, so omission is expected)."
    - "[stale] AzureStor is imported in app.R (line 9) and renv.lock but never called; DSCI_AZ_BLOB_DEV_SAS appears only in commented-out docker commands in R/lines.R. Blob loading was prototyped but the shipped app bundles the GeoPackage locally."
visibility: internal
last_synced: "2026-06-17"
---

# Bangladesh Cyclone Monitoring Tool

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On-demand Shiny app: user enters cyclone landfall location + wind speed → computes estimated wind speed at every ADM4 union in 6 coastal Bangladesh districts using a distance-decay model → highlights unions above a configurable trigger threshold.*

## Jobs & schedule

This is an interactive web application, not a scheduled data pipeline. There is one deployed artifact:

| job | ref | schedule | status |
|---|---|---|---|
| ds-aa-bgd-cyclone-monitoring Azure App Service | https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net | on-demand (user-triggered) | Running (registry); app self-labels "in development" |
| container-registry GHA build | `.github/workflows/container-registry.yaml` | push to `master` + manual `workflow_dispatch` | live |

> **Registry note:** in `infrastructure/deployments.md` this Azure app is **Running** but its repo column is blank (`—`) — the app→repo link (`ocha-dap/ds-aa-bgd-cyclone-monitoring`) is not yet recorded there. See `extra.discrepancies`.

## Inputs

- **Bundled GeoPackage** `data/bgd_adm_sel_bbs_20201113_shp.gpkg` — ADM4 union boundaries (BBS 2020-11-13 release), layer `bgd_admbnda_adm4_bbs_20201113`. Baked into the Docker image at build time; no runtime blob or DB reads.
- **User inputs at runtime:**
  - Landfall point (longitude / latitude), entered manually or by clicking the map
  - Forecasted landfall wind speed (km/h)
  - Trigger threshold (km/h, default 118)

## Steps

1. App startup: reads GeoPackage, filters to 6 coastal ADM2 districts (Barguna, Bhola, Patuakhali, Noakhali, Satkhira, Khulna), simplifies geometry for rendering, projects to UTM 46N (EPSG:32646) for distance calculations.
2. User selects/enters landfall point and wind speed; clicks **Compute Union Wind Speed**.
3. Server computes distance (km) from each union boundary to the landfall point (UTM 46N, `st_distance` on boundary geometry — not centroid).
4. Applies wind reduction factor: `wind_speed_union = 0.9807 * exp(-0.003 * distance_km) * input_wind_speed`.
5. Unions with `wind_speed_union > threshold` are flagged as triggered.
6. Outputs rendered to: map (polygon colours), Division Summary Table, Union Wind Speed Table. CSV download available.

## Outputs

- **Map tab:** leaflet map with union polygons coloured tomato (triggered) or green (below threshold); landfall point marker.
- **Division Summary Table:** per-ADM1 count of triggered unions, total unions, percent triggered. In-browser only.
- **Wind Speed Table:** per-ADM4 union with distance (km), wind reduction factor, estimated wind speed (km/h). Downloadable as CSV (`distance_table_<date>_<HHMMSS>.csv`).
- No DB writes. No blob writes. No email outputs.

## Dependencies

- **R 4.5.0** (rocker/r-ver:4.5.0), managed with `renv` (lockfile at `renv.lock`).
- Key R packages: `shiny`, `shinyWidgets`, `leaflet`, `leaflet.extras2`, `DT`, `sf`, `tidyverse`, `rmapshaper`, `AzureStor` (imported but currently unused in app logic).
- **Docker** for containerization; image pushed to Azure Container Registry (secrets: `ACR_ENDPOINT`, `ACR_USERNAME`, `ACR_PASSWORD`).
- **Azure App Service** in resource group `IMB-CHD-DataScience-EastUS2`; app name `ds-aa-bgd-cyclone-monitoring`.
- No `ocha-stratus`, `ocha-lens`, or `ocha-relay` dependencies (pure R Shiny app).

## Failure modes & debugging

- **App not loading / 500 error:** check Azure App Service logs in portal. Most likely cause is a failed container startup — the GeoPackage read happens at startup before the UI renders. If `data/bgd_adm_sel_bbs_20201113_shp.gpkg` is missing or corrupt in the container, the app crashes immediately.
- **Wrong/stale boundary data:** the GeoPackage is baked into the Docker image. To update it, replace the file and push to `master` — the GHA workflow rebuilds the image automatically.
- **Dependency breakage / renv mismatch:** if `renv::restore()` fails during image build, the GHA `container-registry.yaml` build step fails. Check ACR for recent successful push; inspect GHA run logs.
- **ACR push fails:** verify `ACR_ENDPOINT`, `ACR_USERNAME`, `ACR_PASSWORD` secrets are current in the repo's GitHub settings.
- **AzureStor / SAS token:** `DSCI_AZ_BLOB_DEV_SAS` is referenced in commented-out Docker commands in `R/lines.R`. If blob access is re-enabled in future, this SAS token will need to be wired as a live secret/env var.
- **Contact:** Pauline Ndirangu (pauline.ndirangu@un.org) — listed in-app as the dev contact.

## Downstream consumers

- [`frameworks/bgd-cyclone`](../frameworks/bgd-cyclone/2025-04-25.md) operators assessing whether a Bangladesh cyclone meets the AA trigger threshold in real time during a cyclone event. Same 6 coastal ADM2 districts and ADM4 unions as the framework's geographic scope.
- No other automated systems consume this app's output — it produces on-demand user-downloaded CSVs only.
