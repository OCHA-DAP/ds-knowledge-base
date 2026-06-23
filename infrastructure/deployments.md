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

## Databricks jobs → see the live registry

The per-job inventory + **live health** for the Databricks **and** GitHub-Actions prod pipelines is the generated **[pipeline-registry.md](pipeline-registry.md)** (`scripts/gen_pipeline_registry.py`) — one row per deployed job keyed by runtime handle, with last-success-vs-cadence health, the data-plane mode, and compute. That's the single source of truth (this section used to carry a hand table; it drifted). The compute platform (policies, clusters, the dev/prod model) is [databricks.md](databricks.md).

Snapshot of what the registry flags (2026-06-22): **7 down** — `Run ECMWF Storms` + `Run IBTrACS` + the `Cuba Hurricane Observational Monitor` failing every run; the intended-prod NHC GHA workflow (`ds-nhc-forecast`) failing since 8 Jun; `ds-afro-cholera`, `ds-acled-fetcher`, `ds-aa-mdg-monitoring` monitoring all silently stalled for weeks–months — plus the NHC/GDACS DAB jobs running `mode=dev` (cutover) and `Storm Alert` on a personal cluster. None of these were visible to `pipelines-status`. (Dev jobs are now health-monitored too.)

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
