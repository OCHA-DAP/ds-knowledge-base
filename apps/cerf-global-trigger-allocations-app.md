---
content_type: app
name: cerf-global-trigger-allocations-app
purpose: Monte Carlo–simulate CERF's aggregate AA financial exposure across the whole portfolio of trigger frameworks → an interactive Shiny dashboard for CERF colleagues to explore budget-exceedance risk and premium/deductible scenarios for a hypothetical CERF AA insurance mechanism.
status: live
tech: other        # R Shiny / flexdashboard (published via rsconnect)
related: standalone
deployment:
  platform: other  # NOT the team Azure estate or GH Pages — a personal shinyapps.io account
  ref: "zackarno.shinyapps.io/fin_exposure_explore (personal shinyapps.io account, hand-published via rsconnect — see Maintenance)"
  url: https://zackarno.shinyapps.io/fin_exposure_explore/
  resource_group:  # n/a — not on Azure
inputs:
  - "dashboard/trig_probs_202406_CERF.csv — per-framework $ amount, yearly activation probability, and status (Active/under development/closed/prep), hand-maintained; seeded from a CERF-edited Google Sheet, now edited live via the Shiny app's editable table"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/df_cadc_historical_classified.parquet — monthly forecast-vs-threshold classification for the Central America Dry Corridor (CADC), produced upstream by ds-aa-lac-dry-corridor's preprocessing script"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/aa_historical/{monthly,yearly}/*.csv — per-framework historical activation flags, compiled across several framework repos (CADC, Burkina, Niger, Chad, Yemen, DRC cholera, Fiji, Haiti — see exploration/historical_record_code_documentation.qmd)"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/cerf_insurance_net_grid_{active,all}.parquet — precomputed premium/deductible grid-search results used in the insurance-mechanism exploration"
depends_on:
  - lac-dry-corridor
source_repo: ocha-dap/ds-aa-cerf-global-trigger-allocations
source_branch: correlated_sampling
source_sha: a61ecda
code_ref:
  - dashboard/cerf_analysis_flex.Rmd
  - analysis/01_cerf_allocation_simulation.qmd
  - exploration/02_correlated_simulation_case_study.qmd
  - exploration/03_historical_framework_overview.qmd
  - exploration/historical_record_code_documentation.qmd
  - data-raw/01_input_data.R
  - data-raw/02_compile_historical_activation_data.R
  - data-raw/cadc_yearly_monthly_historical_activations.R
  - R/blob_utils.R
  - R/utils.R
extra:
  stack: "R-only repo (one of the few in the portfolio): box modules, AzureStor for blob (no ocha-stratus/lens/relay), simstudy::genCorGen for correlated binary simulation, flexdashboard + shiny + datamods (editable table UI) + reactable, gghdx/gt/glue for viz. No renv.lock — deps are whatever's installed locally. Secret: DSCI_AZ_SAS_DEV (dev blob only)."
  outputs: "Writes back to blob (projects container): aa_historical/monthly/cadc_aa_historical_monthly.csv and aa_historical/yearly/cadc_aa_historical_yearly.csv. Self-contained Quarto HTML + PNG figures under outputs/ are git-ignored (local render only). No DB writes, no Listmonk emails."
  backing_analysis: "The dashboard packages the independent-sampling Monte Carlo model in analysis/01_cerf_allocation_simulation.qmd. A correlated-sampling case study (exploration/02_correlated_simulation_case_study.qmd, current branch HEAD) is work-in-progress and NOT yet reflected in the published app."
  cerf_allocations_app: "[gap] An unrelated-looking `ds-aa-cerf-allocations` Azure webapp exists in infrastructure/deployments.md with an unknown repo; nothing in this repo's code points at it. Treat as a separate app pending further investigation."
visibility: internal
last_synced: "2026-07-02"
---

# ds-aa-cerf-global-trigger-allocations

> Interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

An interactive financial-exposure explorer for CERF colleagues: it Monte Carlo–simulates CERF's **aggregate** anticipatory-action financial exposure across the whole portfolio of trigger frameworks (probability × payout per framework, with policy logic for conditional/mutually-exclusive triggers), sums to a yearly portfolio payout, and plots the exceedance distribution against 5/10/15% of CERF's ~$595M historical average annual budget. It also explores a hypothetical CERF "AA insurance" product (premium/deductible grid search). The question it answers: "Across all our trigger frameworks, how big could CERF's anticipatory payouts get in a bad year, and how would an insurance mechanism price against that?"

This surface is captured here — rather than in any single framework repo — because portfolio-wide financial exposure is a cross-cutting artifact no one framework can produce alone. It is a decision-support tool presented directly to CERF colleagues to inform pre-arranged AA financing conversations (portfolio envelope sizing and premium/deductible design). Per the README, "all feedback received up to 2024-06-10 has been implemented into the App."

## Key features

- **Editable framework table** (`datamods` / `reactable`) — one row per trigger "event" (country × shock × window): `$` amount, yearly activation probability, and portfolio `status` (Active / under development / closed / prep). Edits drive the simulation **live**; this table has replaced the original CERF-managed Google Sheet as the working input surface.
- **Portfolio Monte Carlo model** (independent sampling, `dashboard/cerf_analysis_flex.Rmd` packaging `analysis/01_cerf_allocation_simulation.qmd`) — for each `status == "Active"` event, independently samples ~1,000,000 years of Bernoulli(payout | probability), then applies hard-coded conditional/mutually-exclusive payout logic (`enforce_policy_logic()`) across correlated triggers: Bangladesh storm-vs-flood, Burkina Window 3-vs-1, Niger observational-vs-predictive-2, Philippines (max of two scenarios), and each Dry Corridor country's window A vs. B.
- **Payout histogram + exceedance-probability table** (`gt`) — the yearly portfolio-payout distribution against the 5/10/15%-of-budget thresholds.
- **Insurance-mechanism exploration** — premium × deductible grid search for a hypothetical CERF AA insurance product (`cerf_insurance_net_grid_{active,all}.parquet`).
- **Historical sanity-check** — a heatmap (`data-raw/02_compile_historical_activation_data.R`, `exploration/03_historical_framework_overview.qmd`) of when each framework actually activated historically, compiled across framework repos, to compare against the assumed probabilities.

A correlated-sampling case study (`exploration/02_correlated_simulation_case_study.qmd`, restricted to the four Dry Corridor countries: derives an empirical correlation matrix from the historical activation table, simulates 100,000 correlated years with `simstudy::genCorGen` — `ep` preferred over `copula`, which loses information converting continuous→binary — and tests whether ignoring cross-country/cross-window correlation understates tail risk) is **work in progress** (conclusion marked `TBD`) and not yet in the published dashboard. See the [`lac-dry-corridor` framework page](../frameworks/lac-dry-corridor/) for the upstream CADC classification this consumes.

## Data

- **`dashboard/trig_probs_202406_CERF.csv`** — the per-framework probability/amount/status inputs. Originally a CERF-managed Google Sheet (linked in the README), downloaded to CSV once it "got messy"; now edited **live in the app's** `datamods::edit_data` table rather than in the sheet. `data-raw/01_input_data.R` downloads the current CSV from blob to `dashboard/`.
- **`df_cadc_historical_classified.parquet`** (blob, `projects/ds-aa-cerf-global-trigger-allocations/`) — monthly ECMWF/INSIVUMEH forecast-vs-threshold classification for the Central America Dry Corridor, produced upstream by [`ds-aa-lac-dry-corridor`](../frameworks/lac-dry-corridor/)'s `classify_historical_data_for_financial_exposure_analysis.R` (on its `nrt-monitoring` branch). This is the only upstream *data* dependency with traceable code; other frameworks' probabilities are hand-copied into the CSV above rather than pulled programmatically.
- **`aa_historical/{monthly,yearly}/*.csv`** (blob, same container) — per-framework binary activation history, compiled from several framework repos (CADC, Burkina Faso, Niger, Chad, Yemen flash floods, DRC cholera, Fiji, Haiti — see `exploration/historical_record_code_documentation.qmd`). `data-raw/cadc_yearly_monthly_historical_activations.R` reads the CADC classified parquet, thresholds it (`mm <= q_val`) per admin/window, pivots to wide yearly/monthly activation tables, and re-uploads `cadc_aa_historical_{monthly,yearly}.csv`.
- **`cerf_insurance_net_grid_{active,all}.parquet`** (blob) — precomputed premium × deductible grid-search outputs feeding the insurance-mechanism exploration.

Freshness is entirely manual — there is **no automated pipeline** feeding this app; a developer runs the `data-raw/` scripts and re-publishes by hand. Blob access is via `AzureStor` directly, not `ocha-stratus`. The app also writes back to blob: `aa_historical/monthly/cadc_aa_historical_monthly.csv` and `aa_historical/yearly/cadc_aa_historical_yearly.csv`. Self-contained Quarto HTML + PNG plots under `outputs/` are git-ignored (local render only). No DB writes, no Listmonk emails.

## Deployment & access

Published by hand to **`https://zackarno.shinyapps.io/fin_exposure_explore/`** — a **personal shinyapps.io account**, not the team's Azure estate or GH Pages. The `dashboard/cerf_analysis_flex.Rmd` `flexdashboard` is republished via `rsconnect`; there is no CI, GHA workflow, or Databricks job anywhere in the repo. Consequently this app does **not** appear in `infrastructure/pipeline-registry.md` or in `infrastructure/deployments.md`'s Azure app table — it runs entirely outside the team's monitored infra.

The README explicitly flags the hosting as provisional: *"Currently app is deployed on my shiny.io... Eventually for production it would need to be dockerized and put on Azure."*

Stack: R-only repo (one of the few in the portfolio) — `box` modules, `AzureStor` for blob (no `ocha-stratus`/`ocha-lens`/`ocha-relay`), `simstudy` (correlated binary simulation), `flexdashboard` + `shiny` + `datamods` + `reactable`, `gghdx`/`gt`/`glue` (viz). No `renv.lock`/package manifest — dependencies are whatever's installed locally. Secret: `DSCI_AZ_SAS_DEV` (dev blob SAS token — see below).

## Maintenance / known issues

- **Bus factor / hosting risk.** Deployed to a named team member's personal shinyapps.io account, not team infra. If that account lapses, the app disappears with no documented redeploy path. Productionizing would require dockerizing and moving to Azure (per README).
- **No monitored infra / no staleness signal.** No GHA workflow, no `databricks.yml`, nothing in the pipeline registry — there's no "breaks at 2am" pager, but also no automated alert if the input CSV or historical blobs go stale.
- **Hard-coded to the dev storage account (dev-slot only).** `azure_endpoint_url()` (in both `R/blob_utils.R` and `R/utils.R`) defaults `stage = c("dev", "prod")` to `"dev"`, and `load_proj_containers()`/`load_proj_contatiners()` never override it — every blob read/write goes to `imb0chddev`, never prod, via `DSCI_AZ_SAS_DEV`. There is no coded path to prod at all.
- **[conflict] Duplicate, drifting blob helpers.** `R/blob_utils.R` exports `load_proj_containers()`; `R/utils.R` exports an independently-defined, typo'd `load_proj_contatiners()` (extra "t"). `data-raw/01_input_data.R` imports the `R/utils.R` version; every other script imports `R/blob_utils.R`. A fix/rename applied to one silently doesn't reach the other.
- **No validation on hand-edited inputs.** Probabilities/amounts are edited directly in the Shiny table (`datamods::edit_data_server`) with no bounds checking or audit trail beyond whatever the app persists — a bad edit silently changes every subsequent simulation.
- **Branch mismatch.** Current HEAD is `correlated_sampling` (`a61ecda`), which is exploratory-only (`exploration/02_correlated_simulation_case_study.qmd` ends "Discussion/Conclusion: TBD"). `main` reflects only the independent-sampling model — the published dashboard has **not** been updated to use correlated sampling.
- **[gap] `ds-aa-cerf-allocations` Azure app.** There's an unrelated-looking `ds-aa-cerf-allocations` Azure webapp in `deployments.md` with an unknown repo; nothing in this repo's code points at it, so treat as a separate app pending further investigation. <!-- TODO: confirm if ds-aa-cerf-allocations Azure app relates to this repo -->
- **No downstream consumers.** No pipeline or app in this KB reads its blob outputs; the dashboard is presented directly to CERF colleagues.
