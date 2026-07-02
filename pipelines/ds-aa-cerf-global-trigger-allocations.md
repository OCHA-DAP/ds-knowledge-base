---
content_type: pipeline
name: cerf-global-trigger-allocations
type: exposure
status: live
deployment:
  platform: manual
  jobs:
    - { name: "Financial Exposure Explorer (Shiny dashboard)", ref: "dashboard/cerf_analysis_flex.Rmd (published to https://zackarno.shinyapps.io/fin_exposure_explore/)", schedule: "on-demand", status: live }
    - { name: "Refresh input probabilities/amounts from blob", ref: "data-raw/01_input_data.R", schedule: "manual", status: live }
    - { name: "Compile CADC historical activation dataset", ref: "data-raw/cadc_yearly_monthly_historical_activations.R", schedule: "manual", status: live }
    - { name: "Compile cross-framework historical activation dataset", ref: "data-raw/02_compile_historical_activation_data.R", schedule: "manual", status: live }
    - { name: "Portfolio Monte Carlo simulation (independent sampling)", ref: "analysis/01_cerf_allocation_simulation.qmd", schedule: "on-demand", status: live }
    - { name: "Correlated-sampling case study (Central America Dry Corridor)", ref: "exploration/02_correlated_simulation_case_study.qmd", schedule: "on-demand", status: "in development" }
inputs:
  - "dashboard/trig_probs_202406_CERF.csv — per-framework $ amount, yearly activation probability, and status (Active/under development/closed/prep), hand-maintained; seeded from a CERF-edited Google Sheet, now edited live via the Shiny app's editable table"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/df_cadc_historical_classified.parquet — monthly forecast-vs-threshold classification for the Central America Dry Corridor (CADC), produced upstream by ds-aa-lac-dry-corridor's preprocessing script"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/aa_historical/{monthly,yearly}/*.csv — per-framework historical activation flags, compiled across several framework repos (CADC, Burkina, Niger, Chad, Yemen, DRC cholera, Fiji, Haiti — see exploration/historical_record_code_documentation.qmd)"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/cerf_insurance_net_grid_{active,all}.parquet — precomputed premium/deductible grid-search results used in the insurance-mechanism exploration"
outputs:
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/aa_historical/monthly/cadc_aa_historical_monthly.csv"
  - "blob (projects container): ds-aa-cerf-global-trigger-allocations/aa_historical/yearly/cadc_aa_historical_yearly.csv"
  - "Shiny dashboard: https://zackarno.shinyapps.io/fin_exposure_explore/ — interactive, editable financial-exposure explorer (personal shinyapps.io account)"
  - "Self-contained Quarto HTML reports + PNG figures under outputs/ (git-ignored, local render only — not published anywhere durable besides an experimental Confluence push mentioned in .gitignore)"
dependencies:
  - "R (box modules) — not a Python/ocha-stratus pipeline; one of the few R-only repos in the portfolio"
  - "AzureStor (R package) for blob access, called directly — no ocha-stratus/lens/relay"
  - "simstudy::genCorGen — multivariate correlated binary simulation (copula vs ep methods)"
  - "flexdashboard + shiny + datamods (editable table UI) + reactable — the dashboard"
  - "gghdx, gt, glue — plotting/formatting"
  - "secret: DSCI_AZ_SAS_DEV (blob SAS token, dev storage only — see failure modes)"
  - "shinyapps.io (personal account hosting, not team Azure estate)"
downstream: []
depends_on:
  - lac-dry-corridor
source_repo: ocha-dap/ds-aa-cerf-global-trigger-allocations
source_branch: correlated_sampling
source_sha: a61ecda
code_ref:
  - R/blob_utils.R
  - R/utils.R
  - data-raw/01_input_data.R
  - data-raw/02_compile_historical_activation_data.R
  - data-raw/cadc_yearly_monthly_historical_activations.R
  - analysis/01_cerf_allocation_simulation.qmd
  - exploration/02_correlated_simulation_case_study.qmd
  - exploration/03_historical_framework_overview.qmd
  - exploration/historical_record_code_documentation.qmd
  - dashboard/cerf_analysis_flex.Rmd
extra: {}
visibility: internal
last_synced: "2026-07-02"
---

# ds-aa-cerf-global-trigger-allocations

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*on-demand: Monte Carlo–simulate CERF's aggregate AA financial exposure across the whole portfolio of trigger frameworks (probability × payout per framework, with policy logic for conditional/mutually-exclusive triggers) → interactive Shiny dashboard for CERF colleagues to explore budget-exceedance risk and premium/deductible scenarios for a hypothetical CERF AA insurance mechanism.*

Despite living in `pipelines/`, this is **not a scheduled system** — there is no cron, GHA workflow, or Databricks job anywhere in the repo. It's a manually-run R analysis + a hand-published Shiny app, captured here because its output (portfolio-wide financial exposure) is a cross-cutting artifact no single framework repo can produce alone.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Financial Exposure Explorer (Shiny dashboard) | `dashboard/cerf_analysis_flex.Rmd`, published to https://zackarno.shinyapps.io/fin_exposure_explore/ | on-demand (manually republished via rsconnect) | live |
| Refresh input probabilities/amounts from blob | `data-raw/01_input_data.R` | manual | live |
| Compile CADC historical activation dataset | `data-raw/cadc_yearly_monthly_historical_activations.R` | manual | live |
| Compile cross-framework historical activation dataset | `data-raw/02_compile_historical_activation_data.R` | manual | live |
| Portfolio Monte Carlo simulation (independent sampling) | `analysis/01_cerf_allocation_simulation.qmd` | on-demand | live |
| Correlated-sampling case study (CADC) | `exploration/02_correlated_simulation_case_study.qmd` | on-demand | in development (current `correlated_sampling` branch HEAD) |

## Inputs

- **`dashboard/trig_probs_202406_CERF.csv`** — one row per trigger "event" (country × shock × window): `$` amount, yearly activation probability, and portfolio `status` (Active / under development / closed / prep work). Originally a CERF-managed Google Sheet (linked in README), downloaded to CSV once it "got messy"; now edited **live in the Shiny app's** `datamods::edit_data` table rather than the sheet.
- **`df_cadc_historical_classified.parquet`** (blob, `projects/ds-aa-cerf-global-trigger-allocations/`) — monthly ECMWF/INSIVUMEH forecast-vs-threshold classification for the Central America Dry Corridor, produced upstream by [`ds-aa-lac-dry-corridor`](../frameworks/lac-dry-corridor/)'s `classify_historical_data_for_financial_exposure_analysis.R` (on its `nrt-monitoring` branch). This is the only upstream *data* dependency with traceable code; other frameworks' probabilities are hand-copied into the CSV above rather than pulled programmatically.
- **`aa_historical/{monthly,yearly}/*.csv`** (blob, same container) — per-framework binary activation history, compiled from several framework repos' own historical-activation outputs (see `exploration/historical_record_code_documentation.qmd` for the full source list: CADC, Burkina Faso, Niger, Chad, Yemen flash floods, DRC cholera, Fiji, Haiti).
- **`cerf_insurance_net_grid_{active,all}.parquet`** (blob) — precomputed premium × deductible grid-search outputs feeding the insurance-mechanism exploration in `analysis/01_cerf_allocation_simulation.qmd`.

## Steps

1. **`data-raw/01_input_data.R`** downloads the current probability/amount CSV from blob to `dashboard/`.
2. **`data-raw/cadc_yearly_monthly_historical_activations.R`** reads the CADC classified parquet, thresholds it (`mm <= q_val`) per admin/window, pivots to wide yearly/monthly activation tables, and re-uploads them to `aa_historical/{monthly,yearly}/` — feeding both the historical-overview exploration and step 4's correlation matrix.
3. **`data-raw/02_compile_historical_activation_data.R`** and **`exploration/03_historical_framework_overview.qmd`** join the per-framework historical CSVs across all frameworks into one long-format table, for a sanity-check heatmap of "when did each framework actually activate historically" vs. the assumed probabilities.
4. **`analysis/01_cerf_allocation_simulation.qmd`** (the original/"production" analysis): for each `status == "Active"` event, independently samples 1,000,000 years of Bernoulli(payout | probability), then applies hard-coded conditional/mutually-exclusive payout logic (`enforce_policy_logic()`) across correlated triggers — Bangladesh storm-vs-flood, Burkina Window 3-vs-1, Niger observational-vs-predictive-2, Philippines (max of two scenarios), and each Dry Corridor country's window A vs. B — sums to a yearly portfolio payout, and plots the exceedance distribution against 5/10/15% of CERF's ~$595M historical average annual budget. Also explores a hypothetical CERF "AA insurance" product (premium/deductible grid search).
5. **`exploration/02_correlated_simulation_case_study.qmd`** (current branch HEAD, **work in progress**) — restricted to the four Dry Corridor countries: derives an empirical correlation matrix from the step-2 historical activation table, simulates 100,000 correlated years with `simstudy::genCorGen` (compares `copula` vs `ep` — `ep` is preferred, since `copula` loses information converting continuous→binary), applies the same window-A/B payout logic, and compares the resulting payout distribution against plain independent sampling to test whether ignoring cross-country/cross-window correlation understates tail risk. Conclusion section is marked `TBD`.
6. **`dashboard/cerf_analysis_flex.Rmd`** packages step 4's independent-sampling model as a `flexdashboard`: an editable `reactable` table of frameworks (probability, amount, status) drives the same sampling logic live, alongside a payout histogram and an exceedance-probability `gt` table. Published by hand to a personal shinyapps.io account.

## Outputs

- `aa_historical/monthly/cadc_aa_historical_monthly.csv` and `aa_historical/yearly/cadc_aa_historical_yearly.csv` — blob, `projects` container.
- The Shiny dashboard itself: https://zackarno.shinyapps.io/fin_exposure_explore/.
- Self-contained Quarto HTML + PNG plots under `outputs/` — git-ignored, rendered and shared locally/by hand only.
- No DB writes, no Listmonk emails.

## Dependencies

- R + [`box`](https://klmr.me/box/) modules (no `renv.lock`/package manifest found — dependencies are whatever's installed locally).
- **`AzureStor`** (R) for blob access, called directly — this repo does **not** use `ocha-stratus`/`ocha-lens`/`ocha-relay`, unlike the team's Python pipelines.
- `simstudy` (correlated binary simulation), `flexdashboard` + `shiny` + `datamods` (editable UI) + `reactable`, `gghdx`/`gt`/`glue` (viz/formatting).
- Secret: `DSCI_AZ_SAS_DEV` (blob SAS token — see dev-only caveat below).
- shinyapps.io hosting under a named individual's personal account (not the team's Azure resource group).

## Failure modes & debugging

- **No automation at all**: no GHA workflow, no `databricks.yml`, nothing in `infrastructure/pipeline-registry.md`. Everything here is triggered by a person running a script or re-publishing the app — there's no "breaks at 2am" pager, but also no automated staleness signal if the input CSV or historical blobs go stale.
- **Hard-coded to the dev storage account (dev-slot only).** `azure_endpoint_url()` (in both `R/blob_utils.R` and `R/utils.R`) defaults `stage = c("dev", "prod")` to `"dev"`, and `load_proj_containers()`/`load_proj_contatiners()` never override it — every blob read/write in this repo goes to `imb0chddev`, never prod, via `DSCI_AZ_SAS_DEV`. There is no coded path to prod at all.
- **Duplicate, drifting blob helpers.** `R/blob_utils.R` exports `load_proj_containers()`; `R/utils.R` exports an independently-defined, typo'd `load_proj_contatiners()` (extra "t"). `data-raw/01_input_data.R` imports the `R/utils.R` version; every other script imports `R/blob_utils.R`. A fix/rename applied to one silently doesn't reach the other.
- **Bus factor / hosting risk.** The dashboard is deployed to a named team member's personal shinyapps.io account, not team infra. README explicitly flags this: *"Currently app is deployed on my shiny.io... Eventually for production it would need to be dockerized and put on Azure."* If that account lapses, the app disappears with no redeploy path documented.
- **Branch mismatch.** Cloned/current HEAD is `correlated_sampling` (`a61ecda`), which is exploratory-only (`exploration/02_correlated_simulation_case_study.qmd` ends "Discussion/Conclusion: TBD"). `main` reflects only the independent-sampling model (step 4) — the published dashboard has **not** been updated to use correlated sampling.
- **No validation on hand-edited inputs.** Probabilities/amounts are edited directly in the Shiny table (`datamods::edit_data_server`) with no bounds checking or audit trail beyond whatever the app persists — a bad edit silently changes every subsequent simulation.
- **Cross-check against the registry**: this repo does not appear in `infrastructure/pipeline-registry.md` (no Databricks/GHA job to register) or `infrastructure/deployments.md`'s Azure app table — confirming it runs entirely outside the team's monitored infra. (There's an unrelated-looking `ds-aa-cerf-allocations` Azure webapp in `deployments.md` with an unknown repo; nothing in this repo's code points at it, so treat as a separate app pending further investigation — `<!-- TODO: confirm if ds-aa-cerf-allocations Azure app relates to this repo -->`.)

## Downstream consumers

None automated — no pipeline or app in this KB reads its blob outputs. The dashboard is a decision-support tool presented directly to CERF colleagues to inform pre-arranged AA financing conversations (portfolio envelope sizing, and premium/deductible design for a hypothetical CERF AA insurance mechanism); per the README, "all feedback received up to 2024-06-10 has been implemented into the App."
