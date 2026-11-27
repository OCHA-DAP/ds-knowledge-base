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
  - "local file (gitignored): the August CERF UFE 2026-I reference workbook (*.xlsx), or config/cirv_template.xlsx — REQUIRED: the page takes its country list, headers and formatting from it and shows only an error without it"
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
  deploy_auth: "Repo secret AZURE_WEBAPP_PUBLISH_PROFILE = publish profile of the cirv slot (full access to that slot, nothing else). Lets the app's developer deploy without an Azure login."
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

## Key features

- **All Data table:** one row per country with each source's raw value, the component scores
  and the CIRV score, coloured like the CERF workbook, with a country/ISO3 filter.
- **Source views and charts:** per-source tables and CIRV scatterplots (Plotly).
- **Exports:** CSV, and an XLSX built on the reference workbook that keeps its sheets, styles
  and formulas and appends the current source sheets.
- **Data refresh controls:** buttons that run the collectors and processors on the machine
  serving the app, plus an option to refresh at server start.

## Data

Collectors and processors in the repo fetch INFORM Risk and Severity, food-security sources (IPC,
FEWS NET, GRFC, FAO Crop Prospects, JRC ASAP, SOFI), conflict sources (ACLED, CrisisWatch) and
IASC early warning, and write `*_current.csv` files at the repo root. The page reads those CSVs
plus the **reference workbook**, which it needs to render at all (country list, headers,
formatting). The workbook is gitignored, as are the ACLED credentials, so both exist only on the
developer's laptop. Page loads don't fetch data; a refresh started from the refresh controls
does, and switches the page to that run's output.

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
- **Blocker: the reference workbook.** Without it on the server the page shows only the error
  "Put the August reference workbook in the project root (or config/cirv_template.xlsx)".
  `config/cirv_template.xlsx` is not gitignored, so it could be committed to the public repo by
  mistake. Commit it only if CERF agrees the workbook can be public; otherwise the app needs a
  non-sensitive template or a login first.
- **Refresh controls are open to every visitor** on a no-login site: anyone could start a full
  collector run (up to 15 subprocesses) on the shared, memory-tight plan, turn on
  refresh-at-startup, or read the refresh log. The developer has been asked to hide them on the
  server (App Service sets `WEBSITE_SITE_NAME`, which the app can test).
- **No persistence:** files the app writes on the server are lost on restart or redeploy. Refresh
  data locally, commit the CSVs, redeploy.
- **Requirements:** the page needs `streamlit`, `lxml`, `openpyxl`, `plotly`, `beautifulsoup4`
  (resolves to Python 3.14 wheels). Older pins such as `pandas==2.2.2` have no 3.14 wheel.
- **Logs:** build `az webapp log deployment show -n chd-ds-demos -g IMB-CHD-DataScience-EastUS2 --slot cirv`;
  startup `az webapp log tail -n chd-ds-demos -g IMB-CHD-DataScience-EastUS2 --slot cirv`.
  A deploy 503 is usually the shared plan's memory, see [deployments](../infrastructure/deployments.md).

<!-- TODO: once the first deploy runs, confirm the app starts, drop the "not yet deployed" note,
and record how the workbook question was settled. -->
