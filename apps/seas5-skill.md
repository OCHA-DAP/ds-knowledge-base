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
  - "DB dev: hpc.*, ipc.*, pop.*, fews.* mirrors (Forecast x HNRP tab, via pipeline/export_hnrp_drought.py)"
  - "blob dev: projects/ds-seas5-skill/site/<YYYY-MM>/ (the generated site-data bundle the Pages deploy downloads)"
depends_on: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-seas5-skill/", kind: landing, title: "SEAS5 site landing page (multi-product)"}
  - {url: "https://ocha-dap.github.io/ds-seas5-skill/app/", kind: app, title: "SEAS5 skill & alert explorer (vanilla JS + Leaflet, static)"}
  - {url: "https://ocha-dap.github.io/ds-seas5-skill/enso/", kind: report, title: "ENSO & the seasonal forecast, by country — ERA5 teleconnection vs the current SEAS5 outlook"}
  - {url: "https://ocha-dap.github.io/ds-seas5-skill/uganda-flood-trigger/", kind: report, title: "Uganda — OND 2026 flood trigger: revised analysis and design options (design plan; trigger work continues in ds-aa-uga-flooding)"}
  - {url: "https://ocha-dap.github.io/ds-seas5-skill/hdx-signal/", kind: docs, title: "HDX signal for SEAS5 — data hand-over (blob paths, processing, caveats, how to refresh)"}
source_repo: ocha-dap/ds-seas5-skill
source_branch: main
source_sha: 95b2c8d
code_ref:
  - analysis/prob_alerts.py
  - analysis/prob_detail.py
  - analysis/seasonality.py
  - pipeline/compute_skill.py
  - pipeline/export_static_site.py
  - docs/index.html
extra:
  static_site_source: "docs/ on main, assembled to /app/ by the deploy-pages workflow (pages/ -> site root, docs/ -> site/app/). Workflow build, NOT branch-served, since 2026-08-22."
  pipeline_blob_stage: dev
  pipeline_run: "Databricks job 'SEAS5 Skill Monthly Refresh' (databricks.yml, 6th 13:15 UTC right behind the raster-stats jobs, with a preflight task polling until public.seas5/era5 are current; Job Compute): compute_skill / _adm1 / _adm2 / _raster + monthly_clim + hdx-signal inputs -> blob stage=dev; since 2026-09-25 (the DBs are only reachable from the workspace)"
  gh_pages_rebuild: "automatic — the same job runs every exporter, verify_site_data.py --expect <YYYY-MM>, and uploads docs/data + docs/raster/data + docs/cma/data as a bundle to dev blob projects/ds-seas5-skill/site/<YYYY-MM>/ (pipeline/sync_site_data.py); deploy-pages.yml downloads it (dispatch from the job, or its 06:00 UTC cron on the 7th). Generated data is NOT in git any more."
  deployment_trigger: "GHA workflow prob-rp-alerts_chd-ds-seas5-skill.yml triggers on push to MAIN — the filename is a leftover from the branch it was generated on, not the branch it watches"
visibility: internal
last_synced: "2026-09-25"
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
- **Forecast × HNRP tab** (static site) — overlays the drought forecast on humanitarian severity per admin unit: HNRP PiN with the plan's own JIAF intersectoral class, or IPC/CH phases, with an interactive legend, a sortable per-admin bar chart, and a plan-year / IPC-period picker. Listed in the nav since 2026-08. Since 2026-08 the RP readout is paired with **forecast + normal seasonal totals in mm** (same detrended obs-normalized log space as the skill stats; % of normal suppressed where normal < 10 mm) — RP says how unusual, the mm pair says how much water is at stake ([#68](https://github.com/OCHA-DAP/ds-seas5-skill/pull/68)).
- **Static GH Pages site** — `docs/index.html` with a vanilla-JS + Leaflet map (leaflet 1.9.4 from unpkg — the only third-party script) consuming pre-built `docs/data/*.json` and `docs/data/*.geojson`. Shows only the latest forecast; no backend required. Live at https://ocha-dap.github.io/ds-seas5-skill/app/.

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

**Freshness (since 2026-09-25):** the Databricks job **"SEAS5 Skill Monthly Refresh"** (`databricks.yml`, entrypoint `databricks/dispatch.py`; cron 6th 13:15 UTC on ephemeral Job Compute, DS13_v2) does the whole refresh in one run: `preflight` (fails and retries every 30 min, up to 6 h, until `public.seas5` holds the issuance and `public.era5` the month before it — i.e. until "Run SEAS5" (5th 12:30 UTC) and "Run ERA5" (6th 12:00 UTC, 37–68 min) have landed), then `skill_adm0 → skill_adm1 → skill_adm2 → clim_signal` (country, admin-1, admin-2 skill; monthly climatology + HDX-signal input tables), `raster` in parallel (the issuance month recomputed and `--merge`d into the blob cubes), then `site` (every exporter incl. the Forecast × HNRP levels, plan caseloads and the CMA mirror when a newer CMME file exists → `verify_site_data.py --expect <YYYY-MM> --strict-hnrp` → `sync_site_data.py upload`), then `publish` (dispatches `deploy-pages.yml`; needs the dsci secret `GH_SEAS5_PAGES_TOKEN`, else the deploy's own 06:00 UTC cron on the 7th picks the bundle up). The generated site data (`docs/data`, `docs/raster/data`, `docs/cma/data`, ~100 MB) **left git**: it lives as a versioned bundle on the dev blob (`projects/ds-seas5-skill/site/<YYYY-MM>/` + `latest.json`, hash-verified on download; `--tag` rolls the site back). GitHub Actions never touches the database — the runner only needs the dev blob read SAS. The old GHA cron `monthly-refresh.yml` is gone. Still by hand: the ENSO slides (`enso=run` parameter; slow without the teleconnections cache) and the Uganda narrative page.

## Displaying third-party severity data

The HNRP tab shows IPC and JIAF classifications we do not produce. Three defects found in
Aug 2026 by checking the rendered map against ipcinfo.org — not against our own
dataframes, which all looked fine:

1. **Areas outside an IPC projection rendered as Phase 1, "Minimal"** — the class search
   walks down from 5, finds no phase data, and falls through to the mildest category.
   Most of Sudan, mid-famine, displayed as Minimal.
2. **One map blended up to four analysis vintages** under a single title (14 of 39
   countries mixed at least two), because the period was chosen per unit rather than per
   country.
3. **Near-duplicate HAPI rows doubled phase counts** — South Sudan read 9.15M in Phase 3+
   against IPC's published 7.8M.

Fixed in #43–#46. The general rule is
[methods/absent-data.md](../methods/absent-data.md); the source-specific traps are in
[infrastructure/datasets/ipc.md](../infrastructure/datasets/ipc.md). **Aggregate checks
did not catch any of these** — national totals matched while the map was wrong.

## Deployment & access

**Azure web app** `chd-ds-seas5-skill` (resource group `IMB-CHD-DataScience-EastUS2`, state: Running). URL: https://chd-ds-seas5-skill.azurewebsites.net. Deployed to the Production slot (not a dev slot).

Deployment is via the GHA workflow `.github/workflows/prob-rp-alerts_chd-ds-seas5-skill.yml`, which despite its name triggers on push to **`main`** (`on: push: branches: [main]`) and deploys `analysis/prob_alerts.py` as the marimo server entrypoint. Azure names the workflow file after the branch it was configured from, not the branch it watches. The seasonality explorer (`analysis/seasonality.py`) deploys from the same repo to its own standalone web app **`chd-ds-seasonality`** (<https://chd-ds-seasonality.azurewebsites.net>, workflow `prob-rp-alerts_chd-ds-seasonality.yml`, also main-triggered).

The repo formerly deployed the skill and seasonality apps to **deployment slots on `chd-ds-seas5-viz`**; both slots are retired (2026-08) and their hostnames (`chd-ds-seas5-viz-skill-…`, `chd-ds-seas5-viz-seasonality-…`) no longer resolve. Dead "full interactive app" links on the README and the GH Pages methodology section were fixed in [ds-seas5-skill#67](https://github.com/OCHA-DAP/ds-seas5-skill/pull/67).

**GitHub Pages** (second deployment surface): the app is at
https://ocha-dap.github.io/ds-seas5-skill/**app/** — the repo root serves a landing page instead.

Built by the **`deploy-pages.yml` workflow**, not served from a branch (that changed 2026-08-22;
this page said `main:/docs` until 2026-08-24). The workflow rsyncs `pages/` to the site root and
`docs/` to `/app/`. **Do not repoint Pages at a branch** — a `source[branch]` change bypasses the
workflow and serves `docs/` at the root again, breaking every `/app/` and `/uganda/` link.

It also carries a `workflow_run` trigger on the monthly data refresh, because that job merges its
PR with `GITHUB_TOKEN` and such pushes do not fire push-triggered workflows — without it the app's
monthly data would stop reaching the site silently.

Links saved before the move still work: the landing page forwards a recognised app hash or query
(`/#hnrp`, `/?country=...`) to `/app/`, and `/cma/` redirects to `/app/cma/`.

Both surfaces are internal (OCHA staff).

## Maintenance / known issues

- **Monthly refresh runs 13:15 UTC on the 6th, 75 min behind "Run ERA5" — and its `preflight` task is what makes that safe.** SEAS5 lands ~5th ("Run SEAS5" 12:30 UTC); ERA5 for the previous month on the 6th ("Run ERA5" 12:00 UTC, 37–68 min). The preflight polls both prod tables and holds the run until they are current, so the vintage race below cannot start from a stale table; the gate at the end catches anything else.
- **VINTAGE RACE (the worst silent failure — looks like weather, not like a bug).** In-season trimesters (leads −1/−2) blend elapsed ERA5 months with the issuance's forecast. If the pipeline runs before ERA5's elapsed month exists, the current-year composite cannot be built and the machinery **silently falls back to LAST YEAR's issuance**. Both variants happened in Aug 2026: (a) the country pipeline's paired series had no 2026 rows for issued-Aug JJA/JAS, so the history export shipped the issuance file without its in-season trimesters (map slider lost them); (b) the pixel cube baked **Aug-2025** in-season layers under an Aug-2026 label — South Sudan JAS read wet while the country layer said record dry. Nothing errored; only a human comparing layers caught it.
- **Guards added Aug 2026** (`ocha-dap/ds-seas5-skill`): `pipeline/verify_site_data.py` runs in the refresh job *before* the bundle upload (with `--expect <YYYY-MM>`, so a compute that left last month's stats on the blob cannot ship as new) and fails on any issuance mismatch across payloads, missing lead −2..4 trimesters, or numeric divergence between the two country exporters; `export_raster_site.py` drops in-season layers whose forecast year is stale (site shows its "pixel unavailable" note); `app.js` disables Pixel mode whenever the raster meta's issuance ≠ the site's latest; `compute_skill_raster.py` warns at end-of-run when combos fell back a year. After any manual raster refresh, run `verify_site_data.py --strict-raster`.
- **Rule of thumb for ANY manual run:** before computing, check `SELECT max(valid_date) FROM public.era5` covers the month before the issuance, and after exporting, check every payload's `issued_label` — mismatched vintages are invisible on the map.
- **All blob reads use `stage="dev"`.** This is intentional (the processed parquets live in the dev container), but it means the app will break if the dev blob is unavailable or the parquets haven't been recomputed.
- **`main` is the active branch (since 2026-08).** Both surfaces deploy from it. `prob-rp-alerts` is a stale July snapshot kept for reference — 82 commits behind and a strict subset of `main` (no file exists on it that is not on `main`).
- **The GitHub *default* branch was `prob-rp-alerts` until 2026-08-07**, which silently mis-targeted PRs (`gh pr create` without `--base` aimed at the stale branch and came back CONFLICTING) and made the repo landing page show a July snapshot. Now set to `main`. Any branch cut before that date carries the same hazard: **check `.base.ref` before merging anything old** — retargeting one such PR would have deleted 2,501 lines, including the whole HNRP pipeline.
- **Static site data is a blob bundle, not git** (since 2026-09-25). A local checkout has no `docs/data/` until `uv run python pipeline/sync_site_data.py download`; the deploy asserts the bundle's key payloads exist so a failed download is a red deploy, not a gutted site.
- **Databricks job `SEAS5 Skill Monthly Refresh`** (bundle `ds-seas5-skill`, prod target) is the only scheduled pipeline; a dev copy `[dev adm_tdowning] …` runs on the personal cluster for dry runs. Laptops can no longer run the compute scripts (no DB route) — rerun a step with "Repair run" or `databricks bundle run … -t dev`.
- **PGSSLMODE=require** must be set in the environment (Azure App Service env vars) for the DB connection to succeed on Azure.

## ENSO products around this app

- **`/enso/` country slides** (surface above): two slides per monitored country — the pixel-wise
  ERA5 teleconnection with other modes held constant, and what the current issuance predicts
  with skill shading; EN/FR, PDF. Refreshed with each issuance; the NOAA index cache refreshes
  weekly (now on PSL's ERSST v6 series — see the vintage note in
  [methods/enso-country-deep-dive.md](../methods/enso-country-deep-dive.md)).
- **Country deep dives** — curated, question-led reviews (Eritrea, Malawi, Zimbabwe) in
  [ds-teleconnections](../pipelines/teleconnections.md) that read this app's skill cube for
  SEAS5 skill and return periods rather than recomputing them.
- **Niger HCT brief** — [ds-aa-ner-drought/hct-brief](https://ocha-dap.github.io/ds-aa-ner-drought/hct-brief/)
  reuses this app's Niger slides ([frameworks/ner-drought/2026-06-03](../frameworks/ner-drought/2026-06-03.md)).
