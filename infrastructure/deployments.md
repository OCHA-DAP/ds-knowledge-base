# Deployments — runtime registry

Where things actually **run**. Generated/refreshable from the platforms; cross-linked to repos. App pages and pipeline pages should link here (and carry their own `deployment` block).

## Azure web apps

Resource group **`IMB-CHD-DataScience-EastUS2`** (OCHA-PROD). 20 apps. App `chd-<x>` generally maps to repo `<x>` (or `<x>` minus/plus `-app`).

| app | state | repo | url |
|---|:--:|---|---|
| CERF-3RM | Running | — | https://cerf-3rm.azurewebsites.net |
| DataScienceFTP | Running | — | https://datascienceftp-dvf6gdfbcggaf7b5.eastus2-01.azurewebsites.net |
| chd-demo | Running | — | https://chd-demo-dxh9adanachxfegp.eastus2-01.azurewebsites.net |
| chd-ds-aa-hti-hurricanes-app | Running | `ds-aa-hti-hurricanes-app` | https://chd-ds-aa-hti-hurricanes-app.azurewebsites.net |
| chd-ds-data-validation | Running | — | https://chd-ds-data-validation-fhfyfahyb7gaa6a7.eastus2-01.azurewebsites.net |
| chd-ds-demos | Running | — | https://chd-ds-demos-h7feecemach7cchk.eastus2-01.azurewebsites.net |
| chd-ds-floodexposure-monitoring | Running | `ds-floodexposure-monitoring` | https://chd-ds-floodexposure-monitoring.azurewebsites.net |
| chd-ds-glb-tropicalcyclones-app | Running | `ds-glb-tropicalcyclones-app` | https://chd-ds-glb-tropicalcyclones-app.azurewebsites.net |
| chd-ds-ipc-cerf | Running | — | https://chd-ds-ipc-cerf-bsadf9atbhhdcdcq.eastus2-01.azurewebsites.net |
| chd-ds-rosea-ipc | Running | — | https://chd-ds-rosea-ipc-h4h3bgdvd6ekaqcp.eastus2-01.azurewebsites.net |
| chd-ds-seas5-skill | Running | `ds-seas5-skill` | https://chd-ds-seas5-skill.azurewebsites.net |
| chd-ds-seas5-viz | Running | `ds-seas5-viz` | https://chd-ds-seas5-viz-cycyb5daanfvcrcm.eastus2-01.azurewebsites.net |
| chd-ds-storms-alerts | Running | `ds-storms-alerts` | https://chd-ds-storms-alerts.azurewebsites.net |
| chd-ds-storms-explore | Running | — | https://chd-ds-storms-explore-dzgnb8crc8fsfgee.eastus2-01.azurewebsites.net |
| chd-github-runner | Running | — | https://chd-github-runner-daascrgxgmatgdhr.eastus2-01.azurewebsites.net |
| chd-pa-aa-fji-storms-app | Running | `pa-aa-fji-storms-app` | https://chd-pa-aa-fji-storms-app.azurewebsites.net |
| dev-testaccess | Running | — | https://dev-testaccess-c3cbfhcwa0h4crbb.eastus2-01.azurewebsites.net |
| ds-aa-bgd-cyclone-monitoring | Running | — | https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net |
| ds-aa-cerf-allocations | Running | — | https://ds-aa-cerf-allocations-ajebgpgwaebte2bw.eastus2-01.azurewebsites.net |
| listmonk-demo | Running | — | https://listmonk-demo-afhcg8e2hde0fxca.eastus2-01.azurewebsites.net |

_Refresh:_ `az webapp list --resource-group IMB-CHD-DataScience-EastUS2 -o table`

## Databricks jobs

Profile **`default`** (workspace `adb-6009046713167663`). 13 jobs. `PAUSED` = schedule disabled.

| job_id | name | schedule | paused | source / repo |
|---|---|---|:--:|---|
| 384915441246190 | [dev adm_tdowning] GDACS/ADAM Pipeline | `0 0 0/3 * * ?` | UNPAUSED | — |
| 583285176982712 | [dev adm_tdowning] NHC Pipeline | `0 0,30 0/3 * * ?` | UNPAUSED | — |
| 293793284625510 | [dev adm_zarno1] GDACS/ADAM Pipeline | `0 0 0/3 * * ?` | UNPAUSED | — |
| 402939227068071 | chirps-gefs-test | `manual` | — | — |
| 127810131501319 | Get GFM Plots | `manual` | — | — |
| 1053499360455948 | Run ECMWF Storms | `46 0 22 * * ?` | UNPAUSED | — |
| 954457722530604 | Run ERA5 | `0 0 12 6 * ?` | UNPAUSED | — |
| 792911256578092 | Run FloodScan | `36 0 20 * * ?` | UNPAUSED | — |
| 638351145729392 | Run IBTrACS | `27 0 16 * * ?` | UNPAUSED | — |
| 666239885322861 | Run IMERG | `56 40 14 * * ?` | UNPAUSED | — |
| 266763033249426 | Run NHC | `17 0 0/3 * * ?` | PAUSED | — |
| 710204563973283 | Run SEAS5 | `19 30 12 5 * ?` | UNPAUSED | — |
| 500881901438881 | Storm Alert | `0 30 3,9,15,21 * * ?` | UNPAUSED | — |

_Refresh:_ `databricks jobs list -p default -o json`

## GitHub Actions pipelines

Many pipelines run on **scheduled GitHub Actions** (cron in `.github/workflows/`), not Databricks — this layer was previously untracked here. The registry indexes them; per-workflow schedules + the full `jobs[]` list live on each pipeline page (one home per fact). Surfaced during systems ingestion 2026-06-17; growing as more pipeline repos are ingested.

| pipeline | repo | GHA workflows (summary) | page |
|---|---|---|---|
| floodexposure-monitoring | `ds-floodexposure-monitoring` | daily `23:15 UTC` exposure → chained `repository_dispatch` (raster-stats → quantiles) + keep-awake | [pipelines/floodexposure-monitoring](../pipelines/floodexposure-monitoring.md) |
| nhc-forecast | `ds-nhc-forecast` | `Run script` every 3h (GHA, live) — note the named prod Databricks `Run NHC` job `266763033249426` is **PAUSED** | [pipelines/nhc-forecast](../pipelines/nhc-forecast.md) |
| imerg | `ds-imerg` | `run_download_imerg.yml` daily (+ Databricks `Run IMERG` `666239885322861`) | [pipelines/imerg](../pipelines/imerg.md) |
| hurricanes-monitoring | `ds-hurricanes-monitoring` | per-country monitoring workflows (GHA-only; not previously in any registry) | [pipelines/hurricanes-monitoring](../pipelines/hurricanes-monitoring.md) |

_TODO: GitHub Actions has no single org-wide API like `az`/`databricks`; inventory grows as pipeline repos are ingested. Refresh per-repo via `gh workflow list -R ocha-dap/<repo>`._

## GH Pages apps

Some apps are served from **GitHub Pages** (marimo WASM exports, signup forms) rather than Azure — e.g. `ds-aa-ner-drought` trigger explorer (served from the `iri-trend` branch `docs/`) and the `ds-storms-alerts` signup form (`ocha-dap.github.io/ds-storms-alerts`). These belong in this registry too.

_TODO: inventory via `gh api` / the org's Pages settings._
