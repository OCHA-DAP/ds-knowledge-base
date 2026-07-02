---
content_type: pipeline
name: seasonal-bulletin
type: monitoring
status: live
deployment:
  platform: azure-webapp
  resource_group: IMB-CHD-DataScience-EastUS2
  jobs:
    - { name: "bulletin (prod slot)", ref: "chd-ds-demos/bulletin", schedule: "on-push to python-migrate + workflow_dispatch", status: live }
    - { name: "bulletin-dev (dev slot)", ref: "chd-ds-demos/bulletin-dev", schedule: "on-push to add-skill-plot + workflow_dispatch", status: live }
inputs:
  - "DB table: public.seas5 (SEAS5 precipitation raster stats, issued_date + valid_date, per pcode)"
  - "DB table: public.era5 (ERA5 precipitation raster stats, valid_date, per pcode)"
  - "DB table: public.polygon (ADM0 name/iso3/pcode lookup)"
  - "Blob: emdat/processed/emdat_all.parquet (container=global; EM-DAT historical disasters)"
  - "Blob: ds-seasonal-bulletin/harmonic_seasonality/<iso3>_adm<n>_seasonality.csv (container=dev; bimodal-season filter)"
  - "API: HAPI humdata.org baseline-population (v2, per iso3+adm_level)"
  - "Blob COGs: SEAS5 raster (via stratus.stack_cogs, for gridded anomaly view)"
  - "Blob COGs: ERA5 raster (via stratus.stack_cogs, for gridded anomaly view)"
  - "CERF allocations: hardcoded stub for ETH/SSD Flood rapid-response (TODO: replace with live data)"
outputs:
  - "Interactive marimo app served at chd-ds-demos Azure web app (bulletin slot)"
  - "No blob/DB writes — read-only analysis surface"
dependencies:
  - ocha-stratus==0.1.7
  - marimo
  - pandas
  - plotly
  - matplotlib
  - xarray
  - duckdb
  - python-dotenv
  - HAPI_APP_IDENTIFIER (env var, for humdata population API)
  - Azure App Service publish profile secrets (AZUREAPPSERVICE_PUBLISHPROFILE_*)
downstream:
  - "Seasonal bulletin documents (outputs copied manually into Figma for final bulletin production)"
depends_on:
  - public.seas5
  - public.era5
  - public.polygon
source_repo: ocha-dap/ds-seasonal-bulletin
source_branch: hannah-updates
source_sha: fe138c6
code_ref:
  - seasonal_bulletin.py
  - src/datasources/seas5.py
  - src/datasources/era5.py
  - src/datasources/emdat.py
  - src/datasources/hapi.py
  - src/datasources/codab.py
  - .github/workflows/python-migrate_chd-ds-demos(bulletin).yml
  - .github/workflows/add-skill-plot_chd-ds-demos(bulletin-dev).yml
extra:
  climatology_period: "1993–2016 (CLIM_START/CLIM_END in src/constants.py)"
  cerf_stub: "cerf.py is a hardcoded stub for ETH and SSD Flood rapid-response allocations only; a TODO comment marks it for replacement with real data"
  anomaly_section_is_optional: "Gridded anomaly view is behind a switch UI element and may take minutes to compute if not cached (calls stratus.stack_cogs)"
  marimo_app: "App is a marimo notebook (seasonal_bulletin.py) served in run mode via Azure App Service; __marimo__/session/ is the cache dir"
  discrepancies:
    - "[conflict] Deployed branch != checked-out branch: prod deploy fires on push to `python-migrate`, dev slot on push to `add-skill-plot`, but active dev work (and this page's source_sha) is on `hannah-updates`. The latest `hannah-updates` code is NOT what is serving on prod — a merge to `python-migrate` (or manual workflow_dispatch from that branch) is needed to surface new work."
    - "[gap] CERF data is a hardcoded stub (`src/datasources/cerf.py` -> `load_cerf_raw`): static ETH (2023/2020/2018/2006) and SSD (2019-2022,2024) Flood Rapid-Response years, value=1. A code comment marks it 'dummy ... until we load the actual thing' — not live CERF allocation data."
    - "[gap] `rioxarray` is used at runtime (`src/utils/plot.py` `.rio.clip`) but is NOT pinned in requirements.txt; it is pulled transitively via xarray/ocha-stratus. A dependency-resolution change could break the optional anomaly map silently."
    - "[stale] Both seas5.py and era5.py carry large commented-out `pd.read_sql` blocks (parameterized `FROM public.seas5/era5`); the live queries use f-string month interpolation against unqualified `seas5`/`era5` table names."
    - "[stale] `src/utils/precip.py` is imported (`from src.utils import plot, precip, rp_calc` in seasonal_bulletin.py) but its entire contents (`process_cogs`) are commented out — a no-op dead module kept around, harmless but unused."
  deployed_app_url: "https://chd-ds-demos-h7feecemach7cchk.eastus2-01.azurewebsites.net (chd-ds-demos, slots `bulletin` / `bulletin-dev`)"
visibility: internal
last_synced: "2026-07-02"
---

# Seasonal Bulletin

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On-demand: user selects country/season/leadtime → pulls SEAS5 + ERA5 stats from DB → computes precipitation terciles, return periods, and population exposure → interactive marimo dashboard served on Azure; plots are manually exported into Figma for final bulletin production.*

## Jobs & schedule

This is an **Azure web app**, not a scheduled pipeline. Deployment is triggered by git push to specific branches; the app then serves on-demand user requests.

| job | ref | schedule | status |
|---|---|---|---|
| bulletin (prod slot) | `chd-ds-demos` app, slot `bulletin` | on-push to `python-migrate` + manual dispatch | live |
| bulletin-dev (dev slot) | `chd-ds-demos` app, slot `bulletin-dev` | on-push to `add-skill-plot` + manual dispatch | live |

Note: `chd-ds-demos` does **not** appear as a standalone entry in `infrastructure/deployments.md` (only the named app pages are listed). The bulletin slots share the `chd-ds-demos` Azure app.

## Inputs

| source | type | detail |
|---|---|---|
| `public.seas5` | DB table (prod) | SEAS5 precipitation stats per pcode; filtered by `iso3`, `adm_level`, `issued_date` month, `valid_date` month |
| `public.era5` | DB table (prod) | ERA5 precipitation stats per pcode; filtered by `iso3`, `adm_level`, `valid_date` month |
| `public.polygon` | DB table (prod) | ADM0 name + iso3 + pcode for country dropdown |
| `emdat/processed/emdat_all.parquet` | Blob (`global` container) | EM-DAT historical disasters; loaded via duckdb with push-down filters for iso3 + disaster type |
| `ds-seasonal-bulletin/harmonic_seasonality/<iso3>_adm<n>_seasonality.csv` | Blob (`dev` container) | Pre-computed harmonic seasonality clusters; used to filter admin units to bimodal-season regions only |
| HAPI population API | External REST API | `hapi.humdata.org/api/v2/geography-infrastructure/baseline-population`; single request (`limit=10000, offset=0`, no pagination loop), requires `HAPI_APP_IDENTIFIER` env var |
| SEAS5 raster COGs | Blob (via `stratus.stack_cogs`) | Raw gridded SEAS5 for anomaly section (optional, user-triggered) |
| ERA5 raster COGs | Blob (via `stratus.stack_cogs`) | Raw gridded ERA5 for anomaly section (optional, user-triggered) |
| CERF allocations | Hardcoded stub | `cerf.py` returns hard-coded ETH + SSD Flood rapid-response years; **not live data** — marked TODO |

## Steps

1. **Country/season selection**: user picks iso3, adm_level, issued month, leadtime range, and disaster type via marimo dropdowns.
2. **DB fetch** (`get_season_stats`): SEAS5 stats for selected `issued_month` × `valid_months` × `iso3`; ERA5 stats for same `valid_months` × `iso3`.
3. **Yearly aggregation** (`aggregate_seas5_yearly`, `aggregate_era5_yearly`): average mean mm/day across selected months per pcode per year; linear detrend applied.
4. **Tercile classification + return periods** (`rp_calc.classify_groups_quantile`, `rp_calc.calculate_groups_rp`): lower-tercile threshold at q=0.33 per pcode; empirical return periods.
5. **Population exposure** (`lower_tercile_pop`): join HAPI population to classified admin units; sum population in lower-tercile areas.
6. **Optional bimodal filter** (`codab.filter_adm`): if switch enabled, restricts to pcodes in cluster=1 from seasonality CSV.
7. **National aggregation + RP** (`summarize_annually`, `rp_calc.calculate_one_group_rp`): total people in lower-tercile rainfall each year; return period for current year.
8. **Skill plot** (optional, user-triggered): SEAS5 vs ERA5 scatter per pcode with EM-DAT/CERF overlay; correlation + tercile TPR metrics.
9. **Anomaly map** (optional, user-triggered): loads full gridded COGs via `stratus.stack_cogs`; computes seasonal anomaly relative to 1993–2016 climatology; renders map.

## Outputs

The app has **no DB or blob writes**. Outputs are:

- Interactive marimo dashboard rendered in the browser at the `chd-ds-demos/bulletin` Azure slot
- Human operator manually exports figures from the browser into **Figma** for final seasonal bulletin documents

## Dependencies

| dependency | version/detail |
|---|---|
| `ocha-stratus` | ==0.1.7; used for all DB (prod) and blob access |
| `marimo` | notebook server + WASM-compatible UI widgets |
| `duckdb` | push-down queries against EM-DAT parquet blob via URL |
| `xarray` / `rioxarray` | gridded raster handling for anomaly section |
| `plotly` / `matplotlib` | plotting |
| `HAPI_APP_IDENTIFIER` | env var; HAPI population API key |
| `PGSSLMODE=require` | required for Azure PostgreSQL (see `infrastructure/conventions.md`) |
| Azure publish profile secrets | `AZUREAPPSERVICE_PUBLISHPROFILE_D0A2F0DD2C154F548CE9E8427B37C4EC` (prod), `..._026FF6CFA52042E1B7C34C0F0A7F899B` (dev) — stored in GitHub repo secrets |

## Failure modes & debugging

| symptom | likely cause | remediation |
|---|---|---|
| App blank / 500 on startup | DB connection failure (missing `PGSSLMODE`, wrong credentials) | Check Azure app env vars; `PGSSLMODE=require` must be set; validate stratus DB secrets |
| "No data available for {iso3}" | HAPI population API returned empty; bad `HAPI_APP_IDENTIFIER` or API outage | Check env var; test endpoint manually; HAPI has per-country coverage gaps |
| Country dropdown empty | `public.polygon` query failing (DB connectivity) | Same as DB connection failure above |
| Anomaly section hangs / times out | `stratus.stack_cogs` downloading many raster tiles; no cached result | Expected behavior if cache cold; user must wait several minutes; caching is marimo `@mo.cache` in-process only |
| Seasonality filter silently disabled | `ds-seasonal-bulletin/harmonic_seasonality/` CSV not found on dev blob | `codab.filter_adm` catches the exception and logs to stdout (not visible in marimo run); check that CSV exists in dev container |
| Wrong CERF color coding | `cerf.py` is a stub with hardcoded ETH/SSD values | Not a runtime error; update stub or replace with real data source |
| Deployment fails / old code running | GHA workflow deploys to `python-migrate` branch; active work is on `hannah-updates` | The prod deploy workflow triggers on push to `python-migrate`, not `hannah-updates` — **there is a branch mismatch**: the most recent code on `hannah-updates` is NOT deployed to prod. A manual deploy or branch merge is needed to surface new work. |

**Logs**: Azure App Service → `chd-ds-demos` → Log stream. GHA deployment logs in the repo's Actions tab.

## Downstream consumers

- **Seasonal bulletin documents** (Figma-assembled PDFs/reports) — the primary consumers; figures are copy-pasted manually from the app into Figma layouts.
- No automated downstream systems read from this app's outputs; it is a human-in-the-loop analytical surface.
