---
content_type: app
name: chd-pa-aa-nga-cholera
purpose: "Static Quarto book exploring the BAY-states (Borno/Adamawa/Yobe) 2018-2023 cholera line-list and a candidate anticipatory-action trigger"
status: live
tech: quarto
related: nga-cholera
deployment:
  platform: azure-webapp
  ref: chd-pa-aa-nga-cholera
  url: "https://chd-pa-aa-nga-cholera.azurewebsites.net"
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "pa-aa-nga-cholera/raw/healthsector/CHOLERA_BAY 2018_2023.xlsx (dev blob, cholera case line-list)"
  - "nga-aa-cholera/public/processed/nga-adm2-populations-2023.csv (dev blob, 2023 LGA populations)"
  - "nga-aa-cholera/public/raw/codab/nga.shp.zip (dev blob, LGA boundaries)"
depends_on: [nga-cholera]
source_repo: ocha-dap/pa-aa-nga-cholera
source_branch: explore/cholera-2018-2023-analysis
source_sha: f73dd0f
code_ref:
  - exploration/cholera_analysis/index.qmd
  - exploration/cholera_analysis/ch01_data_overview.qmd
  - exploration/cholera_analysis/ch02_data_quality.qmd
  - exploration/cholera_analysis/ch03_epidemiology.qmd
  - exploration/cholera_analysis/ch04_trigger_exploration.qmd
  - exploration/cholera_analysis/ch05_activation_frequency.qmd
  - exploration/cholera_analysis/ch06_cerf_validation.qmd
  - exploration/cholera_analysis/analysis_utils.py
  - .github/workflows/deploy-app-service.yml
extra: {}
visibility: internal
last_synced: "2026-07-21"
---

# chd-pa-aa-nga-cholera

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A six-chapter Quarto book exploring suspected-cholera surveillance in Nigeria's Borno-Adamawa-Yobe
(BAY) states, 2018-2023, and testing a candidate anticipatory-action trigger. It walks: what the
line-list contains and how complete it is (ch01), data-quality caveats — especially the 2020
reporting gap (ch02), epidemic curves/seasonality/spatial burden/demographics (ch03), a candidate
trigger — weekly cases above the 99th-percentile population fraction (or ADM1-level absolute
thresholds) **or** a ≥4x week-on-week growth off a base of ≥5 cases, sustained 3 consecutive weeks
(ch04) with a parameter-sensitivity sweep, how often that trigger would have fired historically and
the implied per-LGA return period (ch05), and whether it would have flagged the two Nigeria CERF
Rapid Response cholera allocations (2018-10-31, 2021-10-22) with useful lead time (ch06). Every
chapter imports shared logic from `analysis_utils.py` so numbers are identical throughout; charts
use the HDX v2 palette (Borno = blue, Adamawa = red, Yobe = amber). Explicitly **analysis, not an
endorsed framework** — no BAY cholera AA framework has been published; this is the interactive
front-end for the [nga-cholera](../analysis/nga-cholera.md) analysis page (its `apps: []` field
notes this exact deployment). Case-level data is never in the built site — only aggregates
(charts/tables).

## Key features

- **Chapter navigation** (Quarto book sidebar/search) across the six analytical chapters plus an
  overview page with a "bottom line" summary and glossary.
- **Alert heatmap** (ch04): weekly trigger state (amber = alert, red = sustained) per LGA, showing
  activity clustering in the 2018/2021/2022 outbreak seasons.
- **Threshold-sensitivity table** (ch04-05): activation counts under alternative percentile /
  growth-multiple / consecutive-week parameters.
- **CERF-validation comparison** (ch06): trigger fire dates vs. the 2018 and 2021 CERF Rapid
  Response allocation dates.
- All code cells are folded (`code-fold: true`) but visible via "Show code" for full
  reproducibility of every chart/table.

## Data

Read from the **dev** `projects` Azure blob container at **render time** via `ocha-stratus`
(`stage="dev"`) — not at request time, since the deployed site is a pre-rendered static book:

- `pa-aa-nga-cholera/raw/healthsector/CHOLERA_BAY 2018_2023.xlsx` — case line-list, one row per
  suspected case (onset date, LGA, ward, outcome, age/sex, OCV), Borno/Adamawa/Yobe, 2018-2023.
- `nga-aa-cholera/public/processed/nga-adm2-populations-2023.csv` — 2023 LGA population
  denominators for the BAY-states LGAs (used as per-capita denominators).
- `nga-aa-cholera/public/raw/codab/nga.shp.zip` — CODAB `nga_adm2` LGA boundaries, for choropleths.

Freshness: the line-list covers through 2023 and there is no automated refresh — re-rendering
requires re-running `quarto render` locally (with stratus/blob credentials) and re-committing the
output `_book/` directory to git. There is no scheduled pipeline behind this app; it is a one-off
analytical render, not a monitoring system.

## Deployment & access

Deployed as a **static Quarto book** (`exploration/cholera_analysis/_book/`, versioned in git —
no CI render step, no blob credentials needed at deploy time) served by `pm2 serve
/home/site/wwwroot --no-daemon --spa` on an Azure **App Service** web app (Node 22 LTS runtime,
`SCM_DO_BUILD_DURING_DEPLOYMENT=false`) inside the shared `DsciAppServicePlan` in resource group
`IMB-CHD-DataScience-EastUS2`. This is **not a live server app** in the usual sense — it's the
self-serve alternative to a Static Web App (the team can't create new SWA resources; see
[methods/static-data-apps.md](../methods/static-data-apps.md#self-serve-alternative-deploy-into-the-shared-app-service-plan)),
same pattern as the `ds-geospatial-impact-estimates` viewer.

Live at <https://chd-pa-aa-nga-cholera.azurewebsites.net>. Redeploys via the **Deploy cholera
analysis to App Service** GitHub Actions workflow
(`.github/workflows/deploy-app-service.yml`, `azure/webapps-deploy@v3`), triggered on
`workflow_dispatch` or a push to `explore/cholera-2018-2023-analysis` / `main` touching
`exploration/cholera_analysis/_book/**`. Requires repo secret `AZURE_WEBAPP_PUBLISH_PROFILE`.
No prod/dev slot split — single deployment slot.

Access: currently gated only by a client-side `bay-cholera` password prompt
(`password.html`, injected via Quarto's `include-before-body`) — obfuscation, not real security,
since the built HTML is retrievable regardless. This is interim pending Azure App Service **Easy
Auth** (Entra org-login), which needs an Entra app registration not yet created (blocked on
identity-object creation rights beyond the team's `Website Contributor` role). Cross-ref
[infrastructure/deployments.md](../infrastructure/deployments.md).

## Maintenance / known issues

- **No render-time CI**: `_book/` is rendered locally and committed; there is no workflow that
  re-runs `quarto render` against fresh blob data. Content will silently go stale unless someone
  manually re-renders and re-commits after the underlying line-list is updated.
- **Password gate is not real access control** — anyone with the URL and a browser devtools panel
  can read the page source. Treat the site as effectively public until Entra Easy Auth lands.
- **Shared-plan memory risk**: `DsciAppServicePlan` runs ~22 apps on a single P0v3 plan
  (~4 GB RAM) that routinely sits >90% memory; a memory-pegged plan can cause 503s on deploy or on
  request for *any* app on the plan, including this one (see the "One shared App Service Plan"
  section in [infrastructure/deployments.md](../infrastructure/deployments.md)) — not something
  fixable from this repo alone.
- **No published framework**: the trigger shown (ch04) is a discussion candidate; thresholds and
  the priority-LGA set (Bama, Numan, Dikwa, Ngala) are illustrative, not endorsed. See
  [analysis/nga-cholera.md](../analysis/nga-cholera.md) for the full reconciliation/discrepancy
  record (data-timeliness gap, 2020 reporting gap, R-vs-Python implementation divergence, etc.).
- Rebuilding requires a Python env with `quarto`, `ocha-stratus`, `pandas`, `numpy`, `matplotlib`,
  `geopandas`, `openpyxl`, `mapclassify`, `jupyter`, plus `DSCI_AZ_*` stratus blob credentials in
  the environment.
