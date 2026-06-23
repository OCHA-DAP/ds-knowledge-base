---
content_type: app
name: seas5-viz
purpose: Interactive scatter-plot explorer comparing SEAS5 seasonal rainfall forecasts against ERA5 reanalysis and EM-DAT flood impact, per admin division, for any country/season
status: live
tech: marimo
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-seas5-viz
  url: "https://chd-ds-seas5-viz-cycyb5daanfvcrcm.eastus2-01.azurewebsites.net"
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "DB: public.seas5 (prod) — SEAS5 ensemble mean precipitation by pcode, issued_date, valid_date"
  - "DB: public.era5 (prod) — ERA5 mean daily precipitation by pcode, valid_date"
  - "DB: public.polygon (prod) — admin division names, pcodes, iso3, adm_level"
  - "blob: emdat/processed/emdat_all.parquet (global container) — EM-DAT disaster events"
  - "hardcoded stub: CERF flood allocations (ETH, SSD only; not yet loaded from a real source)"
depends_on: [public.seas5, public.era5]
source_repo: ocha-dap/ds-seas5-viz
source_branch: initial-notebook
source_sha: bfa82ba
code_ref:
  - exploration/test_app.py
  - src/datasources/seas5.py
  - src/datasources/era5.py
  - src/datasources/emdat.py
  - src/datasources/cerf.py
  - src/utils/timeseries.py
  - src/utils/rp_calc.py
extra:
  deployment_slot: development
  deploy_trigger: "push to initial-notebook branch OR workflow_dispatch"
  workflow_file: ".github/workflows/initial-notebook_chd-ds-seas5-viz(development).yml"
  cerf_stub_note: "CERF data is hardcoded for ETH and SSD only; countries outside those two always show 'pre-CERF'. Real CERF loading is unimplemented."
  spurious_workflow: "A second workflow file targeting chd-pa-aa-fji-storms-app also triggers on initial-notebook pushes — appears to be an accidental copy-paste residue."
visibility: internal
last_synced: "2026-06-17"
---

# SEAS5-ERA5-EMDAT Explorer

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A scatter-plot comparison, for any country and admin division (ADM0/1/2), of detrended SEAS5 seasonal rainfall forecasts (x-axis) against ERA5 reanalysis (y-axis). Each point is labelled by year. Users choose an issue month and a leadtime window (1–7 months ahead); the app resolves the corresponding valid months and fetches data live from the DB. Optionally, bubble size encodes EM-DAT flood impact (Total Affected) and bubble colour encodes whether a CERF Rapid Response allocation occurred that year. Upper/lower tercile boundaries can be overlaid. The current-season forecast appears as a vertical dashed line when ERA5 is not yet available for that season. Below the main plot, accuracy metrics are shown: Pearson correlation plus upper- and lower-tercile hit rates (TPR/F1). A secondary bar chart shows the ERA5 precipitation seasonality for the selected area.

## Key features

- **Country/admin picker:** dropdowns for ADM0, ADM1, ADM2; admin list loaded live from `public.polygon`.
- **Season configuration:** issued-month dropdown (defaults to the latest available issue in the DB) + leadtime range slider (1–7 months); valid months are computed and displayed.
- **Detrending:** linear detrend applied to both SEAS5 and ERA5 time series before plotting; the trend is fitted on all years except the current forecast year.
- **Impact overlay:** EM-DAT flood impact bubble sizing at ADM0 only; CERF allocation colour coding for ETH and SSD (hardcoded stub for other countries).
- **Tercile overlays:** optional shading + annotation for upper/lower tercile quadrants.
- **Metrics panel:** correlation, upper- and lower-tercile TPR (= PPV = F1 by construction), and empirical return periods for the current forecast.
- **Reference panel:** ERA5 monthly seasonality bar chart for the selected area.

The app is standalone — it is not a companion of a specific framework page, though it reads from the same `public.seas5` and `public.era5` tables that underpin SEAS5-based AA frameworks.

## Data

| Source | Access | Content | Freshness |
|---|---|---|---|
| `public.seas5` (prod DB) | `stratus.get_engine("prod")` | SEAS5 ensemble mean precipitation per pcode, issued_date, valid_date | Updated by the `Run SEAS5` Databricks job (monthly, 5th of the month) |
| `public.era5` (prod DB) | `stratus.get_engine("prod")` | ERA5 mean daily precipitation per pcode, valid_date | Updated by `Run ERA5` Databricks job (monthly, 6th of each month) |
| `public.polygon` (prod DB) | `stratus.get_engine("prod")` | Admin names, pcodes, iso3, adm_level | Static reference |
| `emdat/processed/emdat_all.parquet` (blob, `global` container) | `stratus.load_parquet_from_blob` / DuckDB direct URL | EM-DAT all disasters | Manual upload via `src/datasources/emdat.py:process_emdat()` — not automated |
| CERF allocations | **Hardcoded stub** in `src/datasources/cerf.py` | Flood allocations for ETH and SSD only | Not live; stub returns dummy data |

ERA5 data goes back to 1981; SEAS5 to approximately 1981 as well. The detrend reference period uses 1981 onward. Impact data shown from 2000+.

## Deployment & access

- **Azure web app:** `chd-ds-seas5-viz`, resource group `IMB-CHD-DataScience-EastUS2`.
- **URL:** <https://chd-ds-seas5-viz-cycyb5daanfvcrcm.eastus2-01.azurewebsites.net>
- **State:** Running (per deployments.md).
- **Slot:** The GHA workflow deploys to the **`development`** slot, not production. The production slot likely serves whatever was last manually deployed or swapped.
- **Deploy trigger:** Push to `initial-notebook` branch, or manual `workflow_dispatch` via `.github/workflows/initial-notebook_chd-ds-seas5-viz(development).yml`.
- **Entrypoint:** `exploration/test_app.py` — a marimo app, run with `marimo run exploration/test_app.py`.
- Cross-ref: `infrastructure/deployments.md` (Azure web apps table, row `chd-ds-seas5-viz`).

## Maintenance / known issues

- **Dev-slot deployment:** The GHA workflow deploys to `slot-name: development`. A prod-slot swap must be done manually via the Azure Portal or CLI after verifying the dev slot. This is the primary operational gotcha.
- **CERF data is a stub:** `src/datasources/cerf.py` hardcodes allocations for ETH and SSD only and returns dummy amounts (all `1`). All other countries display "pre-CERF" permanently. Replacing with a real CERF API or blob-backed parquet is outstanding work.
- **EM-DAT parquet is manually maintained:** `process_emdat()` ingests a local Excel file to blob. There is no scheduled refresh. The blob path is `emdat/processed/emdat_all.parquet` in the `global` container — not under the project prefix.
- **Spurious workflow file:** `.github/workflows/initial-notebook_chd-pa-aa-fji-storms-app(test).yml` also triggers on pushes to `initial-notebook` and targets `chd-pa-aa-fji-storms-app`. This appears to be an accidental copy left over from the Azure auto-generated workflow. It should be deleted or scoped to the correct repo.
- **`main` is stale:** `main` has only a single commit ("init"). All real work is on `initial-notebook`. Deployments.md correctly identifies the repo; the active branch is `initial-notebook`.
- **No test suite:** No tests; breakage surfaces at runtime.
- **`PGSSLMODE=require`:** Required for Azure PostgreSQL connections — set this in the Azure app service configuration; see `infrastructure/conventions.md`.
