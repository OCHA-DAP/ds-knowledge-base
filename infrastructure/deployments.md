# Deployments — runtime registry

Where things actually **run**. Generated/refreshable from the platforms; cross-linked to repos. App pages and pipeline pages should link here (and carry their own `deployment` block).

## Azure web apps

Resource group **`IMB-CHD-DataScience-EastUS2`** (OCHA-PROD). 20 apps. App `chd-<x>` generally maps to repo `<x>` (or `<x>` minus/plus `-app`).

| app | state | repo | url |
|---|:--:|---|---|
| CERF-3RM | Running | `ds-cerf-3rm-app` | https://cerf-3rm.azurewebsites.net |
| DataScienceFTP | Running | `ds-cma-datasharing` | https://datascienceftp-dvf6gdfbcggaf7b5.eastus2-01.azurewebsites.net |
| chd-demo | Running | — | https://chd-demo-dxh9adanachxfegp.eastus2-01.azurewebsites.net |
| chd-ds-aa-hti-hurricanes-app | Running | `ds-aa-hti-hurricanes-app` | https://chd-ds-aa-hti-hurricanes-app.azurewebsites.net |
| chd-ds-data-validation | Running | `ds-app-data-validation` | https://chd-ds-data-validation-fhfyfahyb7gaa6a7.eastus2-01.azurewebsites.net |
| chd-ds-demos | Running | `ds-seasonal-bulletin` | https://chd-ds-demos-h7feecemach7cchk.eastus2-01.azurewebsites.net |
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

## Databricks jobs — prod-pipeline registry

Profile **`default`** (workspace `adb-6009046713167663`). 16 jobs. This is the **authoritative registry** of the Databricks half of our prod pipelines (the GHA half is below). A job is a real prod pipeline only when **state = UNPAUSED _and_ data-mode = prod** — see [databricks.md → the two dev/prod axes](databricks.md#the-two-devprod-axes-this-is-the-subtle-part). Compute is the **Job Compute** policy (`000C79D951EAF0D6`) unless noted. `status?` = visible to [pipelines-status](../pipelines/pipelines-status.md) (tagged `databricks=job`). _Snapshot 2026-06-22._

| job_id | name | repo | schedule (UTC) | state | data-mode | writes | status? |
|---|---|---|---|:--:|:--:|---|:--:|
| 954457722530604 | Run ERA5 | `ds-raster-pipelines` | `0 0 12 6 * ?` (6th, monthly) | UNPAUSED | **prod** | `public.era5` | ✅ |
| 666239885322861 | Run IMERG | `ds-raster-pipelines` | `56 40 14 * * ?` (daily) | UNPAUSED | **prod** | `public.imerg` | ✅ |
| 710204563973283 | Run SEAS5 | `ds-raster-pipelines` | `19 30 12 5 * ?` (5th, monthly) | UNPAUSED | **prod** | `public.seas5` | ✅ |
| 792911256578092 | Run FloodScan | `ds-raster-pipelines` | `36 0 20 * * ?` (daily) | UNPAUSED | **prod** | `public.floodscan` | ✅ |
| 1053499360455948 | Run ECMWF Storms | `ds-storms-pipeline` | `46 0 22 * * ?` (daily) | UNPAUSED | **prod** | `storms.ecmwf_storms`, `storms.ecmwf_tracks_geo` | ✅ |
| 638351145729392 | Run IBTrACS | `ds-storms-pipeline` | `27 0 16 * * ?` (daily) | UNPAUSED | **prod** | `storms.ibtracs_storms`, `storms.ibtracs_tracks_geo` | ✅ |
| 266763033249426 | Run NHC | `ds-storms-pipeline` | `17 0 0/3 * * ?` | **PAUSED** | prod | `storms.nhc_storms`, `storms.nhc_tracks_geo` | ✅ |
| 959161297191654 | **NHC Pipeline** (new DAB) | `ds-storms-pipeline` | `0 0,30 0/3 * * ?` (3-hourly) | UNPAUSED | ⚠️ **dev** (cutover) | NHC tracks + WSP exposure | ❌ untagged |
| 197203772269744 | **GDACS/ADAM Pipeline** (new DAB) | `ds-storms-pipeline` | `0 0 0/3 * * ?` (3-hourly) | UNPAUSED | ⚠️ **dev** (cutover) | GDACS→ADAM→match | ❌ untagged |
| 500881901438881 | Storm Alert | `ds-storms-alerts` | `0 30 3,9,15,21 * * ?` | UNPAUSED | dev (`stage=dev`) | storm-alert emails (Listmonk) | ❌ — runs on **personal cluster `0515-…`** ⚠️ |
| 527252598381643 | Cuba Hurricane Forecast Monitor | `ds-aa-cub-hurricanes` | manual (triggered by NHC) | — | — | cub-hurricanes monitoring | ❌ runs `main`; `run_as` zarno1 |
| 384915441246190 | [dev adm_tdowning] GDACS/ADAM Pipeline | `ds-storms-pipeline` | `0 0 0/3 * * ?` | UNPAUSED | dev | — (personal dev job) | ❌ |
| 583285176982712 | [dev adm_tdowning] NHC Pipeline | `ds-storms-pipeline` | `0 0,30 0/3 * * ?` | UNPAUSED | dev | — (personal dev job) | ❌ |
| 293793284625510 | [dev adm_zarno1] GDACS/ADAM Pipeline | `ds-storms-pipeline` | `0 0 0/3 * * ?` | UNPAUSED | dev | — (personal dev job) | ❌ |
| 127810131501319 | Get GFM Plots | — | manual | — | — | ad-hoc GFM plots | ❌ |
| 402939227068071 | chirps-gefs-test | — | manual | — | — | test | ❌ |

**⚠️ Health flags surfaced 2026-06-22 (the "trains on the tracks" gaps):**
- **The real prod NHC writer isn't in Databricks at all** — it's the live GHA `Run script` in [`nhc-forecast`](../pipelines/nhc-forecast.md) (`ds-nhc-forecast`, every 3h). On Databricks, `Run NHC` (266…, `--mode prod`) is **PAUSED** and the new `NHC Pipeline` (959…, tracks + WSP exposure) runs **`mode=dev`** mid-cutover. So `storms.nhc_*` is being written (by GHA), but the Databricks NHC story is three overlapping jobs in transition — and a **concurrency hazard** is already noted on the nhc-forecast page (GHA + a dev Databricks job both write every 3h). `GDACS/ADAM Pipeline` is likewise prod-compute/`mode=dev`.
- **`pipelines-status` watches the wrong NHC _and_ can't see the real one** — it shows the tagged-but-PAUSED `Run NHC`, not the live untagged `NHC Pipeline`, and being Databricks-only it never sees the GHA `ds-nhc-forecast` path that's actually producing the data. This is the core argument for a registry that spans **both** Databricks and GHA.
- **`Storm Alert` depends on a personal interactive cluster** (`0515-161935-i2w5mxhc`), not Job Compute — fragile (breaks if that cluster/owner goes away).

_Refresh:_ `databricks jobs list -p default -o json` (+ `databricks jobs get <id>` for schedule/git_source/compute/data-mode). Compute policies & clusters: [databricks.md](databricks.md).

## GitHub Actions pipelines

Many pipelines run on **scheduled GitHub Actions** (cron in `.github/workflows/`), not Databricks — this layer was previously untracked here. The registry indexes them; per-workflow schedules + the full `jobs[]` list live on each pipeline page (one home per fact). Surfaced during systems ingestion 2026-06-17; growing as more pipeline repos are ingested.

| pipeline | repo | GHA workflows (summary) | page |
|---|---|---|---|
| floodexposure-monitoring | `ds-floodexposure-monitoring` | daily `23:15 UTC` exposure → chained `repository_dispatch` (raster-stats → quantiles) + keep-awake | [pipelines/floodexposure-monitoring](../pipelines/floodexposure-monitoring.md) |
| nhc-forecast | `ds-nhc-forecast` | `Run script` every 3h (GHA, live) — note the named prod Databricks `Run NHC` job `266763033249426` is **PAUSED** | [pipelines/nhc-forecast](../pipelines/nhc-forecast.md) |
| imerg | `ds-imerg` | `run_download_imerg.yml` daily (+ Databricks `Run IMERG` `666239885322861`) | [pipelines/imerg](../pipelines/imerg.md) |
| hurricanes-monitoring | `ds-hurricanes-monitoring` | per-country monitoring workflows (GHA-only; not previously in any registry) | [pipelines/hurricanes-monitoring](../pipelines/hurricanes-monitoring.md) |
| mdg-monitoring | `ds-aa-mdg-monitoring` | `run_monitor_imerg.yml` daily `16:00 UTC` (`Monitor IMERG`, live; + `keep-alive` ping job) — GHA-only, scheduled workflow on `main` | [pipelines/mdg-monitoring](../pipelines/mdg-monitoring.md) |
| eth-drought-monitoring | `ds-aa-eth-drought-monitoring` | `run_monitoring.yml` (`Ethiopia Drought Monitoring`) cron `0 6 6 2,4,5 *` — 6th at 06:00 UTC in Feb/Apr/May only, live; single `monitor` job, scheduled workflow on `main` (+ `workflow_dispatch`). Reads SEAS5 from **prod** DB but zone CSVs from the **dev** blob (`STAGE='dev'`) | [pipelines/eth-drought-monitoring](../pipelines/eth-drought-monitoring.md) |
| ken-drought-monitoring | `ds-aa-ken-drought-monitoring` | `run_monitoring.yml` (`Kenya Drought Monitoring`) — `workflow_dispatch`-only (no cron), live; GHA-only on `main` | [pipelines/ken-drought-monitoring](../pipelines/ken-drought-monitoring.md) |
| afro-cholera | `ds-afro-cholera` | `daily_alerts.yml` (`Daily Cholera Alert`) `0 6 * * *` + dispatch, live — Global Cholera Monitoring, Listmonk alerts (GHA-only) | [pipelines/afro-cholera](../pipelines/afro-cholera.md) |
| nga-flood-monitoring | `ds-nga-flood-monitoring` | `nga-gauge-monitor.yaml` daily `14:00 UTC` + dispatch, live (GHA-only) — Nigeria flood gauge monitor | [pipelines/nga-flood-monitoring](../pipelines/nga-flood-monitoring.md) |
| acled-fetcher | `ds-acled-fetcher` | `main.yml` daily `08:00 UTC` + `workflow_dispatch`, live (GHA-only on `main`) | [pipelines/acled-fetcher](../pipelines/acled-fetcher.md) |
| acled-conflict-index | `ds-acled-conflict-index` | `main.yml` weekly `0 9 * * 1` — **not firing** (workflow lives only on `feat/initial-scraper`, not the default branch; effectively `workflow_dispatch`-only); dev | [pipelines/acled-conflict-index](../pipelines/acled-conflict-index.md) |
| cholera-pdf-scraper | `ds-cholera-pdf-scraper` | 5 workflows: `download-latest-who-pdf.yml` `47 13 * * 2,5` → chained `extract-from-pdf` / `rule-based-extract` (`workflow_run`) → `post-process-extractions` (`workflow_call`), live; all `STAGE=dev` (dev blob) | [pipelines/cholera-pdf-scraper](../pipelines/cholera-pdf-scraper.md) |
| pipelines-status | `ds-pipelines-status` | `update.yml` `15 */6 * * *` (scrapes Databricks job status) + `azure-static-web-apps-…0f.yml` deploys the status Static Web App on push, live | [pipelines/pipelines-status](../pipelines/pipelines-status.md) |
| hti-hurricanes-impactmodel | `ds-aa-hti-hurricanes-impactmodel` | `main.yml` (2STG-XGB affected-population predictions) on push to `fede-implementation` + dispatch (daily cron commented out); runs off the feature branch (`main` stale) | [pipelines/hti-hurricanes-impactmodel](../pipelines/hti-hurricanes-impactmodel.md) |
| storm-impact-harmonisation | `ds-storm-impact-harmonisation` | `daily-gdacs-monitor-email.yml` `20 3,9,15,21 * * *` (live) + 2 app-deploy workflows (cerf-rr slot of `chd-ds-seas5-viz`; global-cyclones slot of `chd-pa-aa-fji-storms-app`); work split across 3 branches | [pipelines/storm-impact-harmonisation](../pipelines/storm-impact-harmonisation.md) |
| slack-bot | `ds-slack-bot` | `dataset-updates.yaml` monthly `0 9 1 * *` (manual dataset-update Slack alerts) + `ci.yaml` — **not deployed** (lives on `manual-update-notifications`, unmerged) | [pipelines/slack-bot](../pipelines/slack-bot.md) |

_TODO: GitHub Actions has no single org-wide API like `az`/`databricks`; inventory grows as pipeline repos are ingested. Refresh per-repo via `gh workflow list -R ocha-dap/<repo>`._

## GH Pages apps

Some apps are served from **GitHub Pages** (marimo WASM exports, signup forms) rather than Azure — e.g. `ds-aa-ner-drought` trigger explorer (served from the `iri-trend` branch `docs/`) and the `ds-storms-alerts` signup form (`ocha-dap.github.io/ds-storms-alerts`). These belong in this registry too.

_TODO: inventory via `gh api` / the org's Pages settings._
