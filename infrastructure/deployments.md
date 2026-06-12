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

> **Pending auth.** `databricks auth login --profile CHD-Databricks-Dev`, then `databricks jobs list -p CHD-Databricks-Dev -o json`. Each job → name, job_id, schedule (cron), notebook/task source, status. Cross-link to the repo that defines it.

_(empty until Databricks re-auth)_