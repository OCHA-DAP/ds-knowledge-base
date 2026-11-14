---
content_type: pipeline
name: bgd-cyclone-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: IMB-CHD-DataScience-EastUS2   # Azure app only (the Shiny tool)
  jobs:
    - name: Monitor ECMWF cyclone tracks
      ref: ".github/workflows/run_monitor_ecmwf.yml"
      schedule: "cron '20 * * * *' (hourly; exits early when the newest cycle is already logged)"
      status: live
    - name: ds-aa-bgd-cyclone-monitoring (Shiny app, Azure App Service)
      ref: "https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net"
      schedule: on-demand
      status: live
    - name: container-registry GHA build
      ref: ".github/workflows/container-registry.yaml"
      schedule: "push to master + workflow_dispatch"
      status: live
inputs:
  - "ECMWF open data tropical-cyclone tracks (https://data.ecmwf.int/forecasts, product tf, BUFR): HRES (oper) + 51-member ensemble (enfo), 4 cycles/day"
  - "data/bgd_adm_sel_bbs_20201113_shp.gpkg (ADM4 union boundaries, 6 target districts; bundled in repo/image)"
  - "data/land_bay_of_bengal_ne10m.geojson, data/countries_bay_of_bengal_ne10m.geojson (Natural Earth 10 m, landfall detection + map outlines)"
  - "blob (dev) projects/ds-aa-bgd-cyclone-monitoring/monitoring/monitoring_log.parquet (processed-cycle state)"
  - "Shiny app only: user-supplied landfall lon/lat, wind speed, threshold"
outputs:
  - "Listmonk email to list 103 per new ECMWF cycle with a storm in play (HRES + ensemble summary, one track map per storm)"
  - "blob (dev) projects/ds-aa-bgd-cyclone-monitoring/monitoring/monitoring_log.parquet (one row per cycle and storm)"
  - "blob (dev) projects/ds-aa-bgd-cyclone-monitoring/monitoring/forecasts/<YYYYMMDD_HHMM>/<storm_id>_{tracks,unions,points}.parquet"
  - "GHA artifact email-preview (output/email.html, 30 days; every run incl. dry runs)"
  - "Shiny app: in-browser map + Division/Union wind tables (CSV download)"
surfaces: []
dependencies:
  - "ocha-stratus 0.1.7 (blob read/write, dev stage, container projects)"
  - "ocha-relay v0.2.0 (ListmonkClient)"
  - "pybufrkit 0.2.25 + bitstring 4.2.3 (BUFR decode), geopandas, shapely, matplotlib, pandas, requests"
  - "Listmonk list id 103 (hard-coded in src/constants.py, all run modes)"
  - "GHA secrets: DSCI_AZ_BLOB_DEV_SAS, DSCI_AZ_BLOB_DEV_SAS_WRITE, DSCI_LISTMONK_API_URL, DSCI_LISTMONK_API_USERNAME, DSCI_LISTMONK_API_KEY"
  - "Shiny app: R 4.5.0 (rocker/r-ver), shiny, leaflet, sf, renv; ACR_ENDPOINT/ACR_USERNAME/ACR_PASSWORD for the image build"
downstream:
  - "frameworks/bgd-cyclone (v2025-04-25): ECMWF contribution to the 2-of-5-model trigger (BMD, IMD, ECMWF, GFS, JTWC); the email covers ECMWF only"
depends_on:
  - listmonk
  - ocha-stratus
  - ocha-relay
source_repo: ocha-dap/ds-aa-bgd-cyclone-monitoring
source_branch: master
source_sha: 16cfe39
code_ref:
  - pipelines/monitor_ecmwf.py
  - src/ecmwf.py
  - src/trigger.py
  - src/emails.py
  - src/blob_utils.py
  - src/constants.py
  - .github/workflows/run_monitor_ecmwf.yml
  - app.R
  - .github/workflows/container-registry.yaml
  - Dockerfile
extra:
  threshold_kmh: 118
  wind_model: "0.9807 * exp(-0.003 * distance_km) * landfall wind; distance from landfall point to union boundary (UTM 46N)"
  districts_in_scope: "Barguna, Bhola, Patuakhali, Noakhali, Satkhira, Khulna (ADM2)"
  windows: "readiness 72-120 h before landfall; action <= 72 h"
  relevance: "storm in play if HRES or any member within 500 km of a target district within 168 h"
  discrepancies:
    - "[gap] The hourly ECMWF monitor (run_monitor_ecmwf.yml) is not yet in infrastructure/pipeline-registry.md, so its health is not tracked there."
    - "[gap] Production state lives on the DEV blob stage: src/constants.py sets BLOB_STAGE='dev', so the monitoring log and forecast tables are written to dev, not prod."
    - "[gap] deployments.md lists the Azure app ds-aa-bgd-cyclone-monitoring with an empty repo column."
    - "[stale] The src/constants.py comment says app.R compares with a strict '>'; since 16cfe39 app.R uses '>=' too, so the app and the monitor now agree. AzureStor is still in renv.lock but no longer loaded by app.R."
visibility: internal
last_synced: "2026-10-24"
---

# Bangladesh Cyclone Monitoring (ECMWF monitor + Shiny tool)

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Hourly poll of ECMWF open-data cyclone tracks (HRES + 51 ensemble members) → find sea-to-land landfalls → apply the framework's wind-reduction factor to estimate wind at every union in six coastal districts → email Listmonk list 103 for each new cycle with a storm in play.* The repo also ships an on-demand R Shiny app doing the same calculation for a hand-entered landfall.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor ECMWF cyclone tracks | `.github/workflows/run_monitor_ecmwf.yml` | hourly at :20 (cron `20 * * * *`); `workflow_dispatch` with `cycle`, `force`, `dry_run`; push to `feat/ecmwf-monitoring` = dry run | live |
| Shiny app (Azure App Service) | https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net | on-demand | live (Running) |
| container-registry build | `.github/workflows/container-registry.yaml` | push to `master` + manual | live |

Concurrency group `monitor-ecmwf` (no cancel) prevents two polls double-sending a cycle.

## Inputs

- ECMWF open data `tf` BUFR files: `data.ecmwf.int/forecasts/<day>/<HH>z/ifs/0p25/{oper,enfo}/…-tf.bufr`. 00/12Z carry 360 h, 06/18Z 144 h. A cycle counts as available once the ensemble file exists (HEAD check). Chosen because CMA's feed has no Bay of Bengal bulletins.
- Bundled boundaries (BBS ADM4 gpkg) and Natural Earth land/country GeoJSON.
- State: monitoring log parquet on dev blob.
- Winds are ECMWF 10 m max wind as published (no averaging-period conversion).

## Steps

1. Pick newest published cycle (or `--cycle`); skip if already in the monitoring log (unless `--force`/`--dry-run`).
2. Download and decode HRES + ensemble BUFR (`src/ecmwf.py`).
3. `trigger.is_relevant`: storms with any track within 500 km of the target districts within 168 h are "in play".
4. `trigger.assess_storm`: per track, find every sea-to-land crossing (interpolated), keep the landfall giving the highest union wind; wind per union = 0.9807·exp(−0.003·km)·landfall wind; meets threshold if any union ≥ 118 km/h (the Shiny app also uses `>=`); window = readiness (72–120 h) / action (≤72 h).
5. Save per-track/union/point parquet to blob, build map + HTML, send one Listmonk campaign (subject `Bangladesh Cyclone Monitoring: ECMWF <dd Mon HH>Z (<ids>)`), then append to the log. Cycles with no storm in play are logged with `in_play=False` so the next poll moves on.
6. Email send reads back Listmonk's sent count and retries with a new campaign (up to 3) because this instance has marked campaigns `finished` with nobody sent.

## Outputs

- Listmonk list **103**, one email per cycle with ≥1 storm in play (HRES landfall country/time/wind, ensemble counts readiness/action and by landfall country, track map).
- Dev blob (container `projects`): `ds-aa-bgd-cyclone-monitoring/monitoring/monitoring_log.parquet` and `…/forecasts/<cycle>/<storm>_{tracks,unions,points}.parquet`.
- `email-preview` GHA artifact on every run.
- Shiny app: map, Division Summary Table, Union Wind Speed CSV (no DB/blob/email writes).

## Dependencies

See frontmatter. Secrets are GitHub Actions secrets on the repo. The framework needs two of five models; this monitor covers ECMWF only, so an email is not itself an activation.

## Failure modes & debugging

- **No email arriving:** check the workflow run on the Actions tab and the `email-preview` artifact; confirm the cycle isn't already in the log (rerun with `force`). Cycles with no relevant storm send nothing by design.
- **Dry-run only:** push runs and `dry_run` never send email or write blob.
- **Listmonk "finished" but nobody sent:** handled by retry; if all 3 attempts fail the run prints a WARNING and returns the last campaign id — check the Listmonk UI.
- **ECMWF files late/404:** `latest_available_cycle` falls back through the last 8 cycles; a missing ensemble file means the cycle is skipped until it lands.
- **Dependency pin breakage:** pybufrkit 0.2.25 breaks on bitstring 5 (pinned 4.2.3); install step retries 3×.
- **Dev blob:** state lives on the dev stage; expired `DSCI_AZ_BLOB_DEV_SAS*` secrets make the log read fail silently into an empty log (any exception → empty frame), which could cause re-sending of an already-processed cycle. Check this first on duplicate emails.
- **Shiny app:** startup reads the bundled gpkg; a missing file crashes the container. Memory-heavy on the shared App Service plan (see [deployments.md](../infrastructure/deployments.md)). Image rebuilds on push to master (ACR secrets). In-app contact is ocha-datascience@un.org.
- Registry cross-check: the monitor is not in `pipeline-registry.md`, so its health isn't tracked there; check the repo's Actions tab.

## Downstream consumers

- [`frameworks/bgd-cyclone`](../frameworks/bgd-cyclone/2025-04-25.md): recipients of list 103 use the email as the ECMWF input to the readiness/action trigger assessment; the Shiny tool supports ad-hoc checks with the same 6 districts and wind model.
- No other automated consumers.
