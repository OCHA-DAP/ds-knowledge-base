---
content_type: app
name: cirv-app
purpose: "Compute and browse the CERF Index for Risk and Vulnerability (CIRV) used for Underfunded Emergencies allocations, from automated source collectors, and export it to the CERF workbook."
status: live   # deployed 2026-11-24 (server/public mode); behind the team password since 2026-11-27 — see Deployment & access
tech: streamlit
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-demos/cirv
  url: https://chd-ds-demos-cirv-hdbrh2e2deb6eec8.eastus2-01.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
surfaces:
  - {url: "https://chd-ds-demos-cirv-hdbrh2e2deb6eec8.eastus2-01.azurewebsites.net", kind: app, title: "CERF CIRV All Data (password)", access: password}
inputs:
  - "repo CSV: inform_risk_current.csv, inform_severity_current.csv (INFORM Risk and Severity)"
  - "repo CSV: food_security_current.csv (IPC, FEWS NET, GRFC, FAO Crop Prospects, JRC ASAP hotspots, SOFI)"
  - "repo CSV: conflict_current.csv (ACLED Conflict Index and Trends, CrisisWatch)"
  - "repo CSV: iasc_current.csv (IASC early warning and scale-ups)"
  - "repo files (server mode): config/cirv_public_metadata.json (country list and headers) and config/cirv_public_format.xlsx (header formatting only, no data), used on Azure instead of the reference workbook"
  - "repo CSV: data/processed/fts_*.csv (FTS humanitarian funding, for the charts)"
  - "local file (gitignored, local runs only): the August CERF UFE 2026-I reference workbook (*.xlsx), or config/cirv_template.xlsx — without it a local run shows an error instead of the table"
depends_on: []
source_repo: ocha-dap/ds-cirv-automation
source_branch: main
source_sha: ff25b7b
code_ref:
  - cirv_all_data_app.py
  - password_gate.py
  - cirv_refresh_ui.py
  - collectors/
  - processors/
  - methodology/cirv.py
  - .github/workflows/deploy-azure.yml
extra:
  deploy_auth: "Repo secret AZURE_WEBAPP_PUBLISH_PROFILE = publish profile of the cirv slot (full access to that slot, nothing else). Lets the app's developer deploy without an Azure login."
visibility: public
last_synced: "2026-11-27"
---

# CIRV app

## What it shows

The CERF Index for Risk and Vulnerability (CIRV) is the country index CERF uses to prioritise
Underfunded Emergencies (UFE) allocations. This Streamlit app rebuilds it from automated source
collectors instead of the hand-filled workbook: it shows each source's current values and the
CIRV scores per country, and (in local runs) exports CSV and an XLSX that keeps the workbook's
layout and formulas. Built by Mansour Altwal; the repo was set up for him on 2026-11-11.

## Key features

- **All Data table:** one row per country with each source's raw value, the component scores
  and the CIRV score, coloured like the CERF workbook, with a country/ISO3 filter.
- **Charts:** "CIRV vs Humanitarian Funding" scatterplots (Plotly) from the FTS funding files,
  each with a chart-data CSV download.
- **Exports:** CSV, and an XLSX built on the reference workbook that keeps its sheets, styles
  and formulas and appends the current source sheets. **Local runs only**; the hosted app offers
  only the charts' data CSVs.
- **Data refresh controls:** a "Refresh data" button that runs the collectors and processors
  on the machine serving the app. **Local runs only**; hidden on the hosted app.

## Data

Collectors and processors in the repo fetch INFORM Risk and Severity, food-security sources (IPC,
FEWS NET, GRFC, FAO Crop Prospects, JRC ASAP, SOFI), conflict sources (ACLED, CrisisWatch) and
IASC early warning, and write `*_current.csv` files at the repo root; FTS funding goes to
`data/processed/fts_*.csv`. The page reads those CSVs.
For the country list, headers and formatting, a local run reads the **reference workbook**, which
is gitignored (as are the ACLED credentials) and exists only on the developer's laptop. The hosted
app instead reads two committed files, `config/cirv_public_metadata.json` and
`config/cirv_public_format.xlsx` (header formatting only, no data). Page loads don't fetch data; a
refresh started from the refresh controls (local only) does, and switches the page to that run's
output.

## Deployment & access

- **Where:** slot `cirv` of `chd-ds-demos` on `DsciAppServicePlan`. A slot because team accounts
  can't create new web apps since 2026-10-15 (see
  [static-data-apps](../methods/static-data-apps.md#self-serve-alternative-deploy-into-the-shared-app-service-plan)
  and [deployments](../infrastructure/deployments.md)).
- **Runtime:** Python 3.14, WebSockets on, `SCM_DO_BUILD_DURING_DEPLOYMENT=true`, container
  logging on, no other app settings. Startup:
  `python -m streamlit run cirv_all_data_app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true`.
- **Server mode:** the app checks `WEBSITE_SITE_NAME` (set by App Service). When it is set, the
  app reads the committed public files instead of the workbook and hides the refresh controls and
  the workbook and All Data downloads.
- **Access: password** (since 2026-11-27, [PR #3](https://github.com/OCHA-DAP/ds-cirv-automation/pull/3)):
  the team's usual password for protected pages. `password_gate.py` checks it on the server, so
  no table, charts or downloads are sent before the right password (the title and the stray line
  below do show). It is active only in server mode, so local runs have no prompt. **Remember me**
  (ticked by default) leaves a cookie for up to 30 days, like staticrypt's `--remember 30` on our
  Pages sites (Safari keeps it about 7). Entra login was ruled out for now (2026-11-17).
  - **What it protects:** the hosted page only. The code and every input file, including
    `cirv_baseline.csv` and `cirv_comparison.csv` (per-country scores from the CERF workbook),
    are in the public repo. Whether that is acceptable is CERF's call.
  - **The stored hash is fast** (two SHA-256 rounds, unlike staticrypt's slow key derivation). It
    keeps the password out of the repo text but doesn't resist offline guessing, and this is the
    password shared with the team's other protected pages.
  - **To change the password,** set `CHECK_SHA256` in `password_gate.py` to the output of the
    command below, then redeploy; old cookies then stop working too. It prompts for the password,
    so any characters work and nothing lands in shell history (the one-liner in the file's
    docstring is fine only for letters, digits and simple punctuation):
    `python -c "import getpass, hashlib; t = hashlib.sha256(('cirv-remember-v1:' + getpass.getpass()).encode()).hexdigest(); print(hashlib.sha256(t.encode()).hexdigest())"`
- **Status (2026-11-27):** deployed by the developer from 2026-11-24 (server mode). The
  password version is live from deploy run 46067450835 (main `ff25b7b`).
  Checked in a fresh browser: prompt first, a wrong password shows nothing more, the right one
  sets the cookie (Secure, SameSite=Strict) and a reload skips the prompt.

## Maintenance / known issues

- **Deploys** are manual: Actions → "Deploy to Azure" → Run workflow (`workflow_dispatch` only).
  The workflow fails early if `requirements.txt` is missing. Step-by-step instructions for the
  developer are in the repo's `DEPLOY.md`. **Merging does not deploy**: the live app changes only
  when someone runs the workflow. After a deploy, Azure kept serving the old copy for a few
  minutes after the deploy run succeeded (2026-11-27), so wait before checking.
- **The reference workbook** stays gitignored (`/*.xlsx`, `/config/cirv_template.xlsx`). The
  hosted app doesn't need it (see Server mode). Commit it only if CERF agrees the workbook can be
  public.
- **Stray text on the page:** two strings in `cirv_all_data_app.py` are not real docstrings, so
  Streamlit shows them as text. Line 3 (after two imports) shows at the top of the page, also
  above the password prompt ("CIRV integration based on the actual uploaded collector audit…").
  The string after `import re` in `table_html` (line 1382) shows above the table ("Display CIRV
  using the reference workbook's formatting."). Moving each to the first line of its file or
  function, or deleting it, would hide it; left for the developer (2026-11-27).
- **`DEPLOY.md` in the app repo is out of date** (still says public, no login, nothing deployed,
  workbook required); this page is current.
- **No persistence:** files the app writes on the server are lost on restart or redeploy. Refresh
  data locally, commit the CSVs, redeploy.
- **Requirements:** `requirements.txt` is unpinned, so each deploy installs the latest
  Streamlit (1.67.0 on 2026-11-27). The password prompt's cookie script needs Streamlit 1.52 or
  later (`st.html(..., unsafe_allow_javascript=True)`). Older pins such as `pandas==2.2.2` have
  no Python 3.14 wheel.
- **Logs:** build `az webapp log deployment show -n chd-ds-demos -g IMB-CHD-DataScience-EastUS2 --slot cirv`;
  startup `az webapp log tail -n chd-ds-demos -g IMB-CHD-DataScience-EastUS2 --slot cirv`.
  A deploy 503 is usually the shared plan's memory, see [deployments](../infrastructure/deployments.md).
