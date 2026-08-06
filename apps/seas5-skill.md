---
content_type: app
name: seas5-skill
purpose: "Interactive SEAS5 precipitation skill and alert explorer — shows forecast percentile vs. Pearson-r skill for every monitored country, every trimester, for any issued month/year back to 1981."
status: live
tech: marimo
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-seas5-skill
  url: https://chd-ds-seas5-skill.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "blob dev: ds-seas5-skill/processed/skill_stats.parquet"
  - "blob dev: ds-seas5-skill/processed/skill_stats_detrended.parquet"
  - "blob dev: ds-seas5-skill/processed/paired_yearly.parquet"
  - "blob dev: ds-seas5-skill/processed/paired_yearly_detrended.parquet"
  - "DB prod: public.seas5 (via pipeline/compute_skill.py)"
  - "DB prod: public.era5 (monthly climatology — loaded at app startup)"
depends_on: []
source_repo: ocha-dap/ds-seas5-skill
source_branch: prob-rp-alerts
source_sha: 95b2c8d
code_ref:
  - analysis/prob_alerts.py
  - analysis/prob_detail.py
  - analysis/seasonality.py
  - pipeline/compute_skill.py
  - pipeline/export_static_site.py
  - docs/index.html
extra:
  static_site_url: https://ocha-dap.github.io/ds-seas5-skill/
  static_site_source: "docs/ on prob-rp-alerts branch; served via GitHub Pages. Needs repointing to main after PR merges."
  pipeline_blob_stage: dev
  pipeline_run: "manual — run pipeline/compute_skill.py after each new SEAS5 forecast (monthly); writes to blob stage=dev"
  gh_pages_rebuild: "manual — run pipeline/export_static_site.py then commit docs/data/ to update the static site"
  deployment_trigger: "GHA workflow prob-rp-alerts_chd-ds-seas5-skill.yml triggers on push to prob-rp-alerts branch"
visibility: internal
last_synced: "2026-08-06"
---

# SEAS5 Skill Explorer

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

The app answers: "For a given SEAS5 forecast issued in month X of year Y, is the trimester-Z precipitation forecast for country C extreme enough (relative to the historical distribution) to be worth acting on, and does SEAS5 have enough skill in that slot to trust it?" It displays every monitored country on a global map coloured by alert category (strongly below/above normal, below/above normal, roughly normal) with hatching for moderate vs. high skill. Users can drill into a per-country scatter of historical SEAS5 forecasts vs. ERA5 observations to see how well SEAS5 performed in each year. A second marimo app (`prob_detail.py`) provides a deterministic probability view with more chart depth per country. A third app (`seasonality.py`) is a standalone ERA5 seasonality explorer.

## Key features

- **Global alert map** — colour-coded by drought/flood severity × forecast skill (Pearson r thresholds), with rainy-season masking. Five regional zoom presets (Global, LAC, Africa, Asia/Europe, SEA/Pacific). Small island states shown as dots.
- **Skill × severity scatter** — all countries plotted with forecast percentile (x) vs. Pearson r (y), or toggle to return-period view. Configurable RP thresholds (default: 3yr alert, 10yr severe alert) and skill thresholds (default: r≥0.30 moderate, r≥0.50 high).
- **Forecast version toggle** — Raw (forecast normalized to obs distribution), Detrended (both sides detrended in log-normal space), or Best skill (per-country winner).
- **Historical year selector** — browse any issued month/year back to 1981 (SEAS5 hindcast start).
- **Per-country panel** — ERA5 trimester climatology bar chart, rainy-season classification controls, and a scatter of historical SEAS5 vs. ERA5 annual means with the current-year forecast highlighted.
- **Static GH Pages site** — `docs/index.html` with a vanilla-JS + D3 map consuming pre-built `docs/data/forecast.json` and `docs/data/countries.geojson`. Shows only the latest forecast; no backend required. Live at https://ocha-dap.github.io/ds-seas5-skill/.

## Data

**Inputs loaded at app startup:**

| Source | What | Stage |
|---|---|---|
| `ds-seas5-skill/processed/skill_stats.parquet` | Pre-computed skill metrics (Pearson r, forecast percentile, RP, n_years) per pcode × issued_month × trimester | blob dev |
| `ds-seas5-skill/processed/skill_stats_detrended.parquet` | Same but with linear detrending in log-normal space | blob dev |
| `ds-seas5-skill/processed/paired_yearly.parquet` | Year-by-year SEAS5 forecast vs. ERA5 obs pairs per pcode × issued_month × trimester | blob dev |
| `ds-seas5-skill/processed/paired_yearly_detrended.parquet` | Detrended version of the above | blob dev |
| `public.era5` (DB prod) | Monthly mean precipitation per pcode — used for ERA5 climatology, rainy-season classification | DB prod |

**Pipeline (offline, manual):** `pipeline/compute_skill.py` reads `public.seas5` and `public.era5` from the prod DB, computes skill for all pcode × issued_month × trimester combinations, and writes the four parquet files above to blob (stage=dev). Run this after each new SEAS5 forecast lands (~monthly). Supports checkpointing and targeted pcode reruns (`--pcodes`).

**In-season (mixed) trimesters (added 2026-07):** valid trimesters per issuance run from leadtime **−2 to 4**, not just 0–4. Negative leads mean the issuance falls inside the trimester: the elapsed 1–2 months are taken from ERA5 observations and only the remainder from SEAS5, with each forecast month bias-corrected against ERA5 for that calendar month (mean/std matched in log space) before blending (`src/skill.py:aggregate_mixed_trimester`). Their "skill" is naturally much higher (1–2 of 3 months are shared with obs) — read it as confidence in the season's final outcome. Pixel layers still cover leads 0–4 only; in-season combos are country-level.

**Static site data rebuild:** `pipeline/export_static_site.py` reads the blob parquets and DB ERA5, then writes `docs/data/forecast.json` and `docs/data/countries.geojson`. Commit the result to update the GH Pages site.

**Freshness:** the GHA workflow `monthly-refresh.yml` (cron: 7th of each month, 03:00 UTC; also `workflow_dispatch`) recomputes country skill, rebuilds all static-site payloads (incl. the Forecast × HNRP levels and plan caseloads), verifies them, and lands the data on `main` via a self-merged PR. The ADM1/ADM2 skill computes and the pixel-raster cube remain **manual** prerequisites run after each issuance (too heavy for CI runners).

## Deployment & access

**Azure web app** `chd-ds-seas5-skill` (resource group `IMB-CHD-DataScience-EastUS2`, state: Running). URL: https://chd-ds-seas5-skill.azurewebsites.net. Deployed to the Production slot (not a dev slot).

Deployment is via the GHA workflow `.github/workflows/prob-rp-alerts_chd-ds-seas5-skill.yml`, which triggers on push to `prob-rp-alerts` and deploys `analysis/prob_alerts.py` as the marimo server entrypoint. The same repo also has workflows that deploy to `chd-ds-seas5-viz` for the detail and seasonality apps.

**GitHub Pages** (second deployment surface): https://ocha-dap.github.io/ds-seas5-skill/. Served from the `prob-rp-alerts` branch `/docs`. Per the README, after the PR merges to `main`, Pages should be repointed to `main/docs` via `gh api`.

Both surfaces are internal (OCHA staff).

## Maintenance / known issues

- **Monthly refresh is scheduled for the 7th — the date is load-bearing.** SEAS5 lands ~5th; ERA5 for the previous month lands ~5th–6th (DB table and the COG stack can lag each other by hours). Running the refresh before ERA5's month arrives triggers the vintage race below.
- **VINTAGE RACE (the worst silent failure — looks like weather, not like a bug).** In-season trimesters (leads −1/−2) blend elapsed ERA5 months with the issuance's forecast. If the pipeline runs before ERA5's elapsed month exists, the current-year composite cannot be built and the machinery **silently falls back to LAST YEAR's issuance**. Both variants happened in Aug 2026: (a) the country pipeline's paired series had no 2026 rows for issued-Aug JJA/JAS, so the history export shipped the issuance file without its in-season trimesters (map slider lost them); (b) the pixel cube baked **Aug-2025** in-season layers under an Aug-2026 label — South Sudan JAS read wet while the country layer said record dry. Nothing errored; only a human comparing layers caught it.
- **Guards added Aug 2026** (`ocha-dap/ds-seas5-skill`): `pipeline/verify_site_data.py` runs in the monthly workflow *before* the commit step and fails on any issuance mismatch across payloads, missing lead −2..4 trimesters, or numeric divergence between the two country exporters; `export_raster_site.py` drops in-season layers whose forecast year is stale (site shows its "pixel unavailable" note); `app.js` disables Pixel mode whenever the raster meta's issuance ≠ the site's latest; `compute_skill_raster.py` warns at end-of-run when combos fell back a year. After any manual raster refresh, run `verify_site_data.py --strict-raster`.
- **Rule of thumb for ANY manual run:** before computing, check `SELECT max(valid_date) FROM public.era5` covers the month before the issuance, and after exporting, check every payload's `issued_label` — mismatched vintages are invisible on the map.
- **All blob reads use `stage="dev"`.** This is intentional (the processed parquets live in the dev container), but it means the app will break if the dev blob is unavailable or the parquets haven't been recomputed.
- **Branch not yet merged to main.** The active branch `prob-rp-alerts` is where all current work lives; `main` is ~2 months stale (last commit 2026-04-28). The Azure web app deploys from `prob-rp-alerts` via the branch-specific workflow. GH Pages is also served from this branch. After the PR merges, the deployment workflow and Pages source should both be repointed to `main`.
- **Static site needs manual data rebuild.** `docs/data/forecast.json` and `docs/data/countries.geojson` are committed files; they are not auto-updated by the Azure app. Run `pipeline/export_static_site.py` and commit after each new forecast.
- **No Databricks job.** Skill computation is done locally or in a dev environment, not via Databricks. There is no scheduled job in the Databricks registry for this repo.
- **PGSSLMODE=require** must be set in the environment (Azure App Service env vars) for the DB connection to succeed on Azure.
