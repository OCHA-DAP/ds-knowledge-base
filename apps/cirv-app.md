---
content_type: app
name: cirv-app
purpose: "Compute and browse the CERF Index for Risk and Vulnerability (CIRV) used for Underfunded Emergencies allocations, from automated source collectors, and export it to the CERF workbook."
status: live   # Azure slot created 2026-11-17; app not yet deployed (placeholder page) — see Deployment & access
tech: streamlit
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-demos/cirv
  url: https://chd-ds-demos-cirv-hdbrh2e2deb6eec8.eastus2-01.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
surfaces: []
inputs:
  - "repo CSV: inform_risk_current.csv, inform_severity_current.csv (INFORM Risk and Severity)"
  - "repo CSV: food_security_current.csv (IPC, FEWS NET, GRFC, FAO Crop Prospects, JRC ASAP hotspots, SOFI)"
  - "repo CSV: conflict_current.csv (ACLED Conflict Index and Trends, CrisisWatch)"
  - "repo CSV: iasc_current.csv (IASC early warning and scale-ups)"
  - "local file (gitignored): the CERF UFE reference workbook (*.xlsx) used for the XLSX export"
depends_on: []
source_repo: ocha-dap/ds-cirv-automation
source_branch: main
source_sha: d8ff659
code_ref:
  - cirv_all_data_app.py
  - cirv_refresh_ui.py
  - collectors/
  - processors/
  - methodology/cirv.py
  - .github/workflows/deploy-azure.yml
extra:
  deploy_auth: "Repo secret AZURE_WEBAPP_PUBLISH_PROFILE = publish profile of the cirv slot only (SCM basic auth on for that slot, FTP off). Lets the app's developer deploy without an Azure login."
visibility: public
last_synced: "2026-11-17"
---

# CIRV app

## What it shows

The CERF Index for Risk and Vulnerability (CIRV) is the country index CERF uses to prioritise
Underfunded Emergencies (UFE) allocations. This Streamlit app rebuilds it from automated source
collectors instead of the hand-filled workbook: it shows each source's current values and the
CIRV scores per country, and exports CSV and an XLSX that keeps the workbook's layout and
formulas. Built by Mansour Altwal; the repo was set up for him on 2026-11-11.

## Data

Collectors and processors in the repo fetch INFORM Risk and Severity, food-security sources (IPC,
FEWS NET, GRFC, FAO Crop Prospects, JRC ASAP, SOFI), conflict sources (ACLED, CrisisWatch) and
IASC early warning, and write `*_current.csv` files at the repo root. The app reads only those
committed CSVs. It does not fetch data on page load, so the data is as fresh as the last commit.
ACLED credentials and the reference workbook are gitignored and exist only on the developer's
laptop.

## Deployment & access

- **Where:** slot `cirv` of `chd-ds-demos` on `DsciAppServicePlan`. A slot because team accounts
  can't create new web apps since 2026-10-15 (see
  [static-data-apps](../methods/static-data-apps.md#self-serve-alternative-deploy-into-the-shared-app-service-plan)
  and [deployments](../infrastructure/deployments.md)).
- **Runtime:** Python 3.14, WebSockets on, `SCM_DO_BUILD_DURING_DEPLOYMENT=true`, container
  logging on, no other app settings. Startup:
  `python -m streamlit run cirv_all_data_app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true`.
- **Access:** public, no login. Entra login was ruled out for now (2026-11-17).
- **Status (2026-11-17):** slot created and configured; nothing deployed yet, so the URL shows the
  Azure placeholder page. The repo has no `requirements.txt` yet.

## Maintenance / known issues

- **Deploys** are manual: Actions → "Deploy to Azure" → Run workflow (`workflow_dispatch` only).
  The workflow fails early if `requirements.txt` is missing. Step-by-step instructions for the
  developer are in the repo's `DEPLOY.md`.
- **No persistence:** files the app writes on the server are lost on restart or redeploy. Refresh
  data locally, commit the CSVs, redeploy.
- **XLSX export may fail on the server** because the reference workbook is gitignored.
- **Logs:** `az webapp log tail -n chd-ds-demos -g IMB-CHD-DataScience-EastUS2 --slot cirv`.
  A deploy 503 is usually the shared plan's memory, see [deployments](../infrastructure/deployments.md).

<!-- TODO: once the first deploy runs, confirm the app starts, drop the "not yet deployed" note,
and record whether the XLSX export works without the workbook. -->
