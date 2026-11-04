---
content_type: app
name: chd-pa-aa-nga-cholera
purpose: "Static Quarto book on the BAY-states (Borno/Adamawa/Yobe) 2018-2023 cholera line-list, applying the DRC cholera framework's 2026 trigger to it"
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
  - "nga-aa-cholera/private/raw/cholera/Completeness_timeliness_2023_2024 W15.xlsx (dev blob, IDSR weekly report timeliness by LGA)"
depends_on: [nga-cholera]
source_repo: ocha-dap/pa-aa-nga-cholera
source_branch: explore/cholera-2018-2023-analysis
source_sha: 482658b
code_ref:
  - exploration/cholera_analysis/index.qmd
  - exploration/cholera_analysis/ch01_data_overview.qmd
  - exploration/cholera_analysis/ch02_data_quality.qmd
  - exploration/cholera_analysis/ch03_epidemiology.qmd
  - exploration/cholera_analysis/ch04_trigger_exploration.qmd
  - exploration/cholera_analysis/ch05_activation_frequency.qmd
  - exploration/cholera_analysis/ch06_cerf_validation.qmd
  - exploration/cholera_analysis/methods.qmd
  - exploration/cholera_analysis/analysis_utils.py
  - exploration/cholera_analysis/drc_trigger.py
  - exploration/cholera_analysis/drc_book.py
  - exploration/cholera_analysis/tests/test_drc_trigger.py
  - .github/workflows/deploy-app-service.yml
extra: {}
visibility: internal
last_synced: "2026-11-04"
---

# chd-pa-aa-nga-cholera

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A Quarto book on suspected-cholera surveillance in Nigeria's Borno-Adamawa-Yobe (BAY) states,
2018-2023. Since the 2026-11-04 revision it applies the trigger of the
[DRC cholera framework's 2026 revision](../frameworks/cod-infectious-disease/2026-06-24.md) (the
L3 configuration, via the Python port written for [Haiti](../analysis/hti-cholera.md)) to the
line-list. Summary page with the bottom line, "Is the data enough?" (DRC vs Haiti vs BAY) and
"What would help"; then what the line-list contains (ch01), data quality and the 2020 reporting gap
(ch02), epidemiology (ch03), the DRC rule applied to BAY — thresholds by baseline, weekly levels,
onsets and the L2/L3/L2.5 constraints, and a comparison with the 2024 candidate design (ch04),
activation frequency, return periods, a percentile sweep and timing within outbreaks (ch05), the
comparison with CERF's three cholera allocations to Nigeria and reporting delays (ch06), and method
notes. Explicitly **analysis, not a framework**; findings are summarised on
[analysis/nga-cholera](../analysis/nga-cholera.md). Case-level data is never in the built site —
only aggregates (charts/tables).

## Key features

- **Chapter navigation** (Quarto book sidebar/search) across six chapters, method notes, and a
  summary page with glossary.
- **Threshold chart** (ch04): LGA-weeks with cases by year against the pooled, expanding and DRC 2026
  thresholds.
- **Trigger-level heatmap** (ch04): weekly level per LGA, with the activations kept under L3 marked.
- **Onset tables** (ch04) showing what each constraint keeps or mutes, for the reference and the
  DRC 63 threshold.
- **Onsets vs CERF chart** (ch06): weekly cases by state above onsets under each baseline, with the
  CERF allocation dates (ERC endorsement).
- All code cells are folded (`code-fold: true`) but visible via "Show code".

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

Live at <https://chd-pa-aa-nga-cholera.azurewebsites.net> (last deployed 2026-11-04, from
`482658b`). The repo has a **Deploy cholera analysis to App Service** GitHub Actions workflow
(`.github/workflows/deploy-app-service.yml`, `azure/webapps-deploy@v3`), triggered on
`workflow_dispatch` or a push to `explore/cholera-2018-2023-analysis` / `main` touching
`exploration/cholera_analysis/_book/**`, but the repo secret `AZURE_WEBAPP_PUBLISH_PROFILE` has
never been added, so it fails ("No credentials found"). Deploys so far are manual: zip the
**contents** of `_book/` and `az webapp deploy -n chd-pa-aa-nga-cholera -g
IMB-CHD-DataScience-EastUS2 --type zip --src-path <zip>` (steps in the book README). No prod/dev
slot split — single deployment slot.

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
- **No published framework**: the book applies the DRC 2026 trigger to see what it would have
  done; it does not propose a BAY trigger. See [analysis/nga-cholera.md](../analysis/nga-cholera.md)
  for the discrepancy record (no lab results, unknown reporting delay, data end in 2023, 2020 gap).
- Rebuilding requires a Python 3.12 env with `quarto`, `ocha-stratus` (pin `rasterio<1.5` if 1.5.x
  has no wheel for the machine), `pandas`, `numpy`, `matplotlib`, `geopandas`, `openpyxl`,
  `mapclassify`, `jupyter`, `tabulate`, `pytest`, plus `DSCI_AZ_*` stratus blob credentials. Render
  with `quarto render --execute`: Quarto's freeze does not notice changes to the `.py` modules.
