---
content_type: app
name: cerf-3rm-app
purpose: "Estimate CERF rapid-response allocation size for a given emergency using an OLS model trained on 2016+ 3RM data."
status: live
tech: marimo
related: storm-impact-harmonisation  # shares the 3RM training xlsx + INFORM lineage (ds-storm-impact-harmonisation blob)
deployment:
  platform: azure-webapp
  ref: CERF-3RM
  url: https://cerf-3rm.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "blob: ds-cerf-3rm-app/processed/inform.parquet (processed INFORM Risk + Severity, refreshed weekly)"
  - "blob: ds-storm-impact-harmonisation/raw/CERF 3RM - RR Regression Model - version 1.8.xlsx (3RM training data, loaded at startup)"
  - "blob: hdx-signals/output/acaps_inform_severity/raw.parquet (INFORM Severity, via refresh script)"
  - "API: DRMKC INFORM Risk (https://drmkc.jrc.ec.europa.eu/inform-index/API/InformAPI, via refresh script)"
depends_on:
  - storm-impact-harmonisation  # 3RM training xlsx lives in ds-storm-impact-harmonisation blob; CERF/INFORM lineage owned there
source_repo: ocha-dap/ds-cerf-3rm-app
source_branch: port-app
source_sha: "79eaba4"
code_ref:
  - app/cerf_predictor.py
  - src/datasets/inform.py
  - src/models/cerf_inform.py
  - scripts/refresh_inform_composite.py
extra:
  conflict_model: "An exploratory conflict-routing variant lives in experimental/cerf_predictor.py (not deployed — intentionally excluded from Azure artifact). It adds conflict-specific models (ACLED fatalities, IDMC displacements) for DisplConfl emergencies; production v1 routes DisplConfl through the INFORM-base model."
  blob_inputs_stage: "inform.parquet is on dev blob (DSCI_AZ_BLOB_DEV_SAS); INFORM Severity is read from prod hdx-signals container (DSCI_AZ_BLOB_PROD_SAS). Azure App Service env vars must carry both SAS tokens."
  model_details: "Two OLS variants pre-fit at app startup: INFORM-base with LogTargeted (n=~250, Adj R² ~0.7) and without LogTargeted (lower fit). Target is ln(AllocationUSD); output back-transformed to USD median and 80% PI."
  refresh_schedule: "GHA workflow refresh-inform.yml runs weekly Mondays 00:00 UTC. Writes ds-cerf-3rm-app/processed/inform.parquet. INFORM Risk republishes annually (late Q4); Severity republishes monthly — weekly cadence catches Severity within ~7 days."
  branch_mismatch: "[conflict] All substantive code is on port-app (HEAD 79eaba4); main has ONLY the initial gitignore commit (df0b7e6). The latest port-app commit (79eaba4) retargeted azure-deploy.yml to trigger on push to main + workflow_dispatch — but since main lacks the code, a push to main would NOT deploy the real app. Auto-deploy is effectively inert until port-app is merged into main. The deployed Azure artifact therefore came from a manual workflow_dispatch run off port-app, NOT from a main push. Deployed branch (port-app) != the workflow's configured trigger branch (main)."
  registry_gap: "[gap] infrastructure/deployments.md lists CERF-3RM as Running but with repo '—' (unlinked). It maps to ocha-dap/ds-cerf-3rm-app; the registry row should be linked."
visibility: internal
last_synced: "2026-06-22"
---

# CERF 3RM Allocation Estimator

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A CERF analyst or country-office staff member enters an emergency scenario — emergency type, country, approximate date, funding requested, and (optionally) people targeted — and the app returns a median estimated CERF rapid-response allocation with an 80% prediction interval. The model is an OLS regression on log-scale CERF 3RM allocation data from 2016 onward. It is explicitly framed as a rough planning guide, not a forecast.

## Key features

- **Scenario controls:** emergency type dropdown (9 types including Storm, Flood, Drought, Cholera, Displacement and Conflict), country dropdown filtered to the ~86 3RM countries with INFORM Risk coverage, year/month pickers, funding-required number input, people-targeted number input.
- **INFORM Composite display:** resolves the country/year/month to an INFORM Composite score (mean of INFORM Risk and INFORM Severity when both available, else Risk alone). Shows badge ("blended" or "Risk-only") and a note when Risk is forward-carried from the latest published year.
- **Two model variants:** when people-targeted > 0 the full model (with LogTargeted) is used; otherwise a no-targeted variant runs. Both are pre-fit at startup.
- **Prediction output:** median USD, 80% prediction interval numerically and as a log-normal distribution plot (matplotlib). Model-in-use banner shows n, Adj R², AIC.
- **Technical accordion:** caveats (reliable funding/targeted ranges, country coverage, large-allocation underestimation bias) and methodology summary.

## Data

| Source | Blob / endpoint | Freshness | Notes |
|---|---|---|---|
| `inform.parquet` | `ds-cerf-3rm-app/processed/inform.parquet` (dev blob) | Weekly (Mon 00:00 UTC) | Processed frame: INFORM Risk (annual, iso3+year) expanded to monthly rows, left-joined with INFORM Severity. Composite computed on read. |
| INFORM Risk | DRMKC API (`/API/InformAPI/Countries/Trends/`) | Fetched by refresh script | Annual; republishes late Q4. The script forward-carries the latest year to the current calendar year so the app can predict for today's date. |
| INFORM Severity | `hdx-signals/output/acaps_inform_severity/raw.parquet` (prod blob, hdx-signals container) | Monthly (ACAPS publishes monthly) | Only exists from 2019 onward; not available for every country-month. |
| CERF 3RM v1.8 | `ds-storm-impact-harmonisation/raw/CERF 3RM - RR Regression Model - version 1.8.xlsx` | Frozen (2016–2023 approx.) | Training data only. Loaded at app startup to fit the OLS model. |

The app reads two blob containers via `ocha-stratus`: the default dev container (for `inform.parquet` and the 3RM xlsx) and `hdx-signals` prod (for raw INFORM Severity, in the refresh script).

## Deployment & access

- **Azure Web App:** `CERF-3RM`, resource group `IMB-CHD-DataScience-EastUS2`, slot **Production** (no dev slot). URL https://cerf-3rm.azurewebsites.net. Matches `infrastructure/deployments.md` (CERF-3RM, Running) — though that registry row is not yet linked to the repo ([gap], see above).
- **Deploy workflow:** `.github/workflows/azure-deploy.yml` — `uv pip compile` → artifact → `azure/webapps-deploy` to the Production slot, on push to `main` + `workflow_dispatch`. Python 3.12 and the marimo startup command are set in the Azure Portal, not the workflow (the workflow file's trailing comment block documents the portal setup); see the repo for the exact command, env vars, and artifact excludes — not restated here.
- **Data refresh workflow:** `.github/workflows/refresh-inform.yml` — runs `scripts/refresh_inform_composite.py` weekly (cron `0 0 * * 1`, Mondays 00:00 UTC) + `workflow_dispatch`, writing `inform.parquet` to dev blob. Needs `DSCI_AZ_BLOB_DEV_SAS` + `DSCI_AZ_BLOB_PROD_SAS` secrets. Independent of the app deploy.
- **Access:** internal — no auth layer in the app code; the App Service is reachable at the public URL.

## Maintenance / known issues

- **[conflict] Branch mismatch (active):** all substantive code lives on `port-app` (HEAD `79eaba4`); `main` has only the initial gitignore commit (`df0b7e6`). `azure-deploy.yml` now triggers on push to `main` (+ `workflow_dispatch`), but because `main` lacks the code, auto-deploy is effectively inert — a push to `main` would not ship the real app. The live Azure artifact came from a manual `workflow_dispatch` run off `port-app`. Deployed branch (`port-app`) ≠ the workflow's configured trigger branch (`main`). Before adding features, merge `port-app` → `main` so auto-deploy actually deploys the current app.
- **[gap] Deployments registry row unlinked:** `infrastructure/deployments.md` lists `CERF-3RM` as Running but with repo `—`. It should link to `ocha-dap/ds-cerf-3rm-app`.
- **`experimental/` excluded from production:** `experimental/cerf_predictor.py` (conflict-routing variant) is intentionally excluded from the Azure deploy artifact. Do not move it to `app/` without reviewing the conflict-model readiness (ACLED/IDMC data paths use `stage="dev"`, Finn xlsx uses `stage="dev"`).
- **[gap] INFORM Severity coverage:** INFORM Severity is only available from 2019 and only for countries ACAPS is actively tracking. The app degrades gracefully (Risk-only composite) but analysts should be aware for historical scenario queries.
- **Forward-carry of Risk:** INFORM Risk always lags by ~1 year. The refresh script carries the latest GNAYear forward to the current calendar year. When this is in effect, the UI shows a yellow warning note.
- **Redeploy:** push to `main` (after merging `port-app`) or trigger `workflow_dispatch` on `azure-deploy.yml`. The data refresh is independent and runs automatically.
- **Environment variables required in Azure:** `DSCI_AZ_BLOB_DEV_SAS` (and optionally `DSCI_AZ_BLOB_PROD_SAS` if conflict data paths are added to production). `PGSSLMODE=require` is not needed here — this app reads only blobs, no DB.
