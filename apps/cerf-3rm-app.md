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
source_sha: "f624f45"
code_ref:
  - app/cerf_predictor.py
  - src/datasets/inform.py
  - src/models/cerf_inform.py
  - scripts/refresh_inform_composite.py
extra:
  conflict_model: "An exploratory conflict-routing variant lives in experimental/cerf_predictor.py (not deployed — intentionally excluded from Azure artifact). It adds conflict-specific models (ACLED fatalities, IDMC displacements) for DisplConfl emergencies; production v1 routes DisplConfl through the INFORM-base model."
  blob_inputs_stage: "inform.parquet is on dev blob (DSCI_AZ_BLOB_DEV_SAS); INFORM Severity is read from prod hdx-signals container (DSCI_AZ_BLOB_PROD_SAS). Azure App Service env vars must carry both SAS tokens."
  model_details: "Two OLS variants pre-fit at app startup: INFORM-base with LogTargeted (n=~250, Adj R² ~0.7) and without LogTargeted (lower fit). Target is ln(AllocationUSD); output back-transformed to USD median and 80% PI."
  refresh_schedule: "GHA workflow refresh-inform.yml runs weekly Mondays 00:00 UTC off main. Writes ds-cerf-3rm-app/processed/inform.parquet. INFORM Risk republishes annually (late Q4); Severity republishes monthly — weekly cadence catches Severity within ~7 days. Needs DSCI_AZ_BLOB_DEV_SAS_WRITE for the upload (PR #3)."
  refresh_status_2026_11_05: "[conflict] Only one successful run ever (manual dispatch 2026-10-06 from the PR #3 branch). The cron could not fire before port-app merged to main (2026-08-25), and every scheduled run since 2026-08-31 (10) failed with NoAuthenticationInformation on the upload: the workflow passes only the read SAS, but stratus.upload_parquet_to_blob needs DSCI_AZ_BLOB_DEV_SAS_WRITE. Fix is PR #3 (open since 2026-10-06), with #4 (fail loudly instead of rebuilding history from an API that now returns only 2026) and #5 (drop the process-lifetime lru_cache so the live app sees refreshes without a restart). Blob last written 2026-10-06; Severity through 2026-09."
  branch_mismatch: "[resolved 2026-08-25] port-app merged into main (PR #1); main is the default branch and holds all code. Remaining quirk: azure-deploy.yml still triggers on push to port-app (restored 2026-06-23 after the retarget-to-main in 79eaba4 broke auto-deploy while main was empty), so an app change merged to main ships only after a fast-forward: git push origin origin/main:port-app. Scheduled workflows (refresh-inform.yml) run off main."
  predecessor: "Supersedes the CERF predictor deployment that ran from ds-storm-impact-harmonisation to the cerf-rr slot of the chd-ds-seas5-viz App Service. That workflow was deleted and the slot removed from Azure on 2026-08-03 (ADR 0006 in ds-storm-impact-harmonisation). This app is now the only CERF predictor deployment. app/cerf_predictor.py still exists in ds-storm-impact-harmonisation as a deployment-less duplicate and is expected to drift — treat THIS repo as the source of truth."
  registry_gap: "[resolved] infrastructure/deployments.md now links CERF-3RM to ds-cerf-3rm-app."
visibility: internal
last_synced: "2026-11-05"
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
- **Deploy workflow:** `.github/workflows/azure-deploy.yml` — `uv pip compile` → artifact → `azure/webapps-deploy` to the Production slot, on push to **`port-app`** + `workflow_dispatch` (not `main`; see Maintenance). Python 3.12 and the marimo startup command are set in the Azure Portal, not the workflow (the workflow file's trailing comment block documents the portal setup); see the repo for the exact command, env vars, and artifact excludes — not restated here.
- **Data refresh workflow:** `.github/workflows/refresh-inform.yml` — runs `scripts/refresh_inform_composite.py` weekly (cron `0 0 * * 1`, Mondays 00:00 UTC) + `workflow_dispatch`, writing `inform.parquet` to dev blob. Needs `DSCI_AZ_BLOB_DEV_SAS` + `DSCI_AZ_BLOB_PROD_SAS` (reads) **and `DSCI_AZ_BLOB_DEV_SAS_WRITE`** (the upload; missing until PR #3 merges). Independent of the app deploy.
- **Access:** internal — no auth layer in the app code; the App Service is reachable at the public URL.

## Maintenance / known issues

- **[conflict] INFORM refresh broken (active, 2026-11-05):** one successful run ever (manual, 2026-10-06). Every scheduled run since 2026-08-31 fails on the upload with `NoAuthenticationInformation` because the workflow passes only the read SAS. Fix is `ds-cerf-3rm-app` PR #3 (one line); #4 and #5 are the follow-ups (fail loudly on the existing-parquet read now that the DRMKC API returns only the latest year, and drop the app's process-lifetime cache). Upstream `hdx-signals` Severity monitor is green; the break is entirely in this repo. A backup of the parquet sits at `ds-cerf-3rm-app/processed/backups/inform_2026-10-06.parquet`.
- **[resolved 2026-08-25] Branch layout:** `port-app` merged into `main` (PR #1); `main` holds everything and PRs target it. `azure-deploy.yml` still triggers on push to `port-app`, so after merging an app change to `main`, fast-forward it: `git push origin origin/main:port-app`. Finishing the cutover means retargeting the workflow and Azure Deployment Center to `main`.
- **Decisions:** the repo now has `docs/decisions/` (ADR 0001 refresh ownership + merge semantics, ADR 0002 no process cache), PR #6.
- **[gap] Deployments registry row unlinked:** `infrastructure/deployments.md` lists `CERF-3RM` as Running but with repo `—`. It should link to `ocha-dap/ds-cerf-3rm-app`.
- **`experimental/` excluded from production:** `experimental/cerf_predictor.py` (conflict-routing variant) is intentionally excluded from the Azure deploy artifact. Do not move it to `app/` without reviewing the conflict-model readiness (ACLED/IDMC data paths use `stage="dev"`, Finn xlsx uses `stage="dev"`).
- **[gap] INFORM Severity coverage:** INFORM Severity is only available from 2019 and only for countries ACAPS is actively tracking. The app degrades gracefully (Risk-only composite) but analysts should be aware for historical scenario queries.
- **Forward-carry of Risk:** INFORM Risk always lags by ~1 year. The refresh script carries the latest GNAYear forward to the current calendar year. When this is in effect, the UI shows a yellow warning note.
- **Redeploy:** push to `port-app` (fast-forward from `main`) or trigger `workflow_dispatch` on `azure-deploy.yml`. The data refresh is independent and runs weekly off `main`.
- **Environment variables required in Azure:** `DSCI_AZ_BLOB_DEV_SAS` (and optionally `DSCI_AZ_BLOB_PROD_SAS` if conflict data paths are added to production). `PGSSLMODE=require` is not needed here — this app reads only blobs, no DB.
