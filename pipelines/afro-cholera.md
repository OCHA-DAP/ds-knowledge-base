---
content_type: pipeline
name: afro-cholera
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group:
  jobs:
    - { name: "Daily Cholera Alert", ref: ".github/workflows/daily_alerts.yml", schedule: "0 6 * * * (06:00 UTC daily); + workflow_dispatch (manual)", status: live }
inputs:
  - "WHO CBPF/AFRO cholera bulletin — https://raw.githubusercontent.com/CBPFGMS/pfbi-data/refs/heads/main/final_data_for_powerbi_with_kpi.csv (live HTTP fetch, no local copy)"
  - "monitoring/last_alerts.csv — git-committed state file tracking last watch/warning alert date per country (read before run, written after)"
outputs:
  - "monitoring/last_alerts.csv — updated alert-date log committed back to main via git push in the GHA step"
  - "plots/watch_alert_<ISO3>.png — per-country watch-alert chart (local to runner, embedded in email)"
  - "plots/warning_alert_<ISO3>.png — per-country warning-alert chart (local to runner, embedded in email)"
  - "Listmonk campaign — list 18, template 8 — HTML email with embedded plots sent on any new alert"
dependencies:
  - "R packages (no Python/uv): box, readr, dplyr, purrr, lubridate, ggplot2, ggtext, janitor, stringr, zoo, gghdx, whisker, emayili, countrycode, AzureStor, glue, scales, httr2, arrow, logger, memoise, jsonlite, sf, rlang"
  - "Listmonk — list_id 18, template_id 8; env vars DSCI_LISTMONK_URL / DSCI_LISTMONK_API_UID / DSCI_LISTMONK_API_KEY"
  - "AWS SES (SMTP fallback for failure notification) — DSCI_AWS_EMAIL_ADDRESS / _USERNAME / _PASSWORD / _HOST / _PORT"
  - "Azure Blob (dev endpoint) — DSCI_AZ_BLOB_DEV_SAS / DSCI_AZ_BLOB_DEV_SAS_WRITE / DSCI_AZ_ENDPOINT_DEV — used by distribution_list.R (currently commented out in email.R)"
  - "Azure Blob (prod endpoint) — DSCI_AZ_BLOB_PROD_SAS — available in env, not actively used in main path"
downstream:
  - "No downstream automated consumers identified; alerts are the terminal output (Listmonk email to subscribers)"
depends_on:
  - "listmonk"
source_repo: ocha-dap/ds-afro-cholera
source_branch: main
source_sha: 8c925a0
code_ref:
  - "monitoring.R — entrypoint: fetches data, applies both alert methods, dispatches email"
  - "monitoring/cleaning.R — data_cleaning() — WHO CSV parse, ISO3 coding, decimal-scaling correction, linear interpolation"
  - "monitoring/alert_check.R — watch (Method 3: 12-month peak) and warning (Method 1: p99) alert detection + plot generation"
  - "monitoring/email.R — send_email() — Listmonk campaign create + run; emayili/SMTP path is commented out"
  - "monitoring/distribution_list.R — get_distribution_list() — loads CSV from Azure Blob dev; commented out in email.R (list 18 used directly)"
  - ".github/workflows/daily_alerts.yml — GHA schedule, env secret injection, failure-mail step, last_alerts.csv commit"
extra:
  alert_thresholds: "min_cases=500, min_cfr=0. Watch: highest weekly case increase in past 12 months AND >=500 new cases AND gap >90 days since last watch alert. Warning: weekly increase >= p99 of historical positives AND >=500 new cases."
  state_mechanism: "Alert state persisted as monitoring/last_alerts.csv committed to git by the GHA job itself after each run. New alert = computed last alert date > stored last alert date."
  llm_branch_note: "origin/shifting-to-llm-scraper branch exists (last commit 2026-03-03) — same commit date as main; appears to be a WIP alternative scraper approach, not deployed."
  email_path_note: "emayili SMTP path in email.R is fully commented out. Active path is Listmonk API only (list 18, template 8)."
  data_source_note: "Input URL is from the CBPFGMS/pfbi-data GitHub repo (CERF PowerBI data). Despite README saying 'WHO AFRO bulletin', the actual source is this CBPF GitHub CSV which includes cholera event rows."
  r_project: true
visibility: internal
last_synced: "2026-06-22"
---

# Afro Cholera Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Daily: fetch WHO AFRO cholera data from CBPFGMS GitHub CSV → apply two alert methods (Watch: 12-month peak; Warning: p99 threshold) → if any new alerts, send Listmonk email (list 18) with embedded per-country PNG charts.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Daily Cholera Alert | `.github/workflows/daily_alerts.yml` | `0 6 * * *` (06:00 UTC daily) + `workflow_dispatch` (manual) | live |

GHA-only — **not** in the Databricks jobs registry. Deployed on `main` (the only branch with the live workflow). Also manually triggerable via `workflow_dispatch`. See [infrastructure/deployments.md](../infrastructure/deployments.md) — note this pipeline is **not yet listed** in the GHA registry table there (see Discrepancies).

## Inputs

1. **WHO AFRO cholera CSV** — live HTTP fetch from `https://raw.githubusercontent.com/CBPFGMS/pfbi-data/refs/heads/main/final_data_for_powerbi_with_kpi.csv`. Despite the name, this is the CBPFGMS PowerBI data file that contains cholera event rows for AFRO countries. No local copy; fetched fresh on every run.
2. **`monitoring/last_alerts.csv`** — git-committed state file. Columns: `iso3`, `last_watch_alert`, `last_warning_alert`. Read at the start of each run to determine which alerts are genuinely new.

## Steps

1. `monitoring.R` fetches the raw CSV via HTTP, calls `data_cleaning()` (`monitoring/cleaning.R`).
2. **Cleaning**: filter rows containing "cholera" (exclude shigellosis etc.), convert country names to ISO3 via `src/location_codes.R`, parse dates (multi-format handling), aggregate by `(iso3, date)`, apply decimal-scaling correction (handles WHO reporting inconsistency where cumulative counts reset or decimal errors occur), linear interpolation for gaps.
3. **Method 1 — Warning alert (p99)**: for each country, compute `weekly_increase` (cases minus previous row, only if gap ≤ 180 days). Compute p95/p975/p99 of positive increases. Flag `alert_level = "p99"` if `weekly_increase >= min_cases (500)` AND `weekly_increase >= p99`.
4. **Method 3 — Watch alert (12-month peak)**: flag rows where the weekly increase equals the maximum over the trailing 12-month window AND ≥ 500 cases AND the previous watch alert was > 90 days ago.
5. `monitoring/alert_check.R` compares computed latest alert dates to `last_alerts.csv`. For each country with a new alert, generate a `ggplot2` PNG saved to `plots/`.
6. `monitoring/last_alerts.csv` is overwritten with current computed values.
7. If any new alerts exist, `send_email()` (`monitoring/email.R`) creates a Listmonk campaign (list 18, template 8) with the rendered HTML body (whisker-templated, plots embedded as base64 data URIs) and immediately sets it to `running`.
8. GHA commits the updated `monitoring/last_alerts.csv` back to `main` and pushes.
9. On job failure, GHA sends a plain-text failure email to `pauline.ndirangu@un.org` via AWS SES.

## Outputs

| output | description |
|---|---|
| `monitoring/last_alerts.csv` | Updated alert-date log committed to git by GHA after each run |
| `plots/watch_alert_<ISO3>.png` | Per-country watch-alert chart (runner-local, embedded in email) |
| `plots/warning_alert_<ISO3>.png` | Per-country warning-alert chart (runner-local, embedded in email) |
| Listmonk campaign (list 18, template 8) | HTML email with embedded charts sent to subscribers on any new alert |

## Dependencies

- **R** (not Python). Package manager: `renv.lock` exists but GHA installs packages ad-hoc via `install.packages()` rather than restoring `renv`. This is a common drift risk.
- **Listmonk**: `DSCI_LISTMONK_URL`, `DSCI_LISTMONK_API_UID`, `DSCI_LISTMONK_API_KEY` — list ID 18, template ID 8.
- **AWS SES** (SMTP): `DSCI_AWS_EMAIL_ADDRESS/USERNAME/PASSWORD/HOST/PORT` — used only for failure notification email.
- **Azure Blob (dev)**: `DSCI_AZ_ENDPOINT_DEV`, `DSCI_AZ_BLOB_DEV_SAS`, `DSCI_AZ_BLOB_DEV_SAS_WRITE` — used by `distribution_list.R` to read a distribution CSV. This function is currently **commented out** in `email.R`; Listmonk list 18 is used directly instead.
- **Azure Blob (prod)**: `DSCI_AZ_BLOB_PROD_SAS` — injected as env var but not actively used in the main alert path.
- **`gghdx`**: OCHA HDX ggplot2 theme package.

## Failure modes & debugging

**GHA run fails (any step):** GHA sends a failure email to `pauline.ndirangu@un.org` via the `dawidd6/action-send-mail@v2` step. Check the Actions tab in GitHub for the full log.

**R package installation fails:** The GHA step installs packages via `install.packages()` without `renv::restore()`. If CRAN is unavailable or a package API changes, this step fails. Fix: check the install step log; consider switching to `renv::restore()`.

**Listmonk API errors:** `send_email()` uses `httr2` without explicit error handling around `req_perform()`. A Listmonk outage or bad credentials will throw an uncaught R error and the GHA job will fail. Check `DSCI_LISTMONK_URL`, `DSCI_LISTMONK_API_UID`, `DSCI_LISTMONK_API_KEY` secrets.

**Alert state drift:** `monitoring/last_alerts.csv` is committed back to git. If two concurrent GHA runs occur (e.g., manual trigger + scheduled), the git push may conflict. Also if the commit step fails, the state file is not updated and the next run may re-send the same alerts.

**Source data unavailable:** `df_raw_link` is fetched directly from GitHub raw URL. If `CBPFGMS/pfbi-data` renames or restructures the file, the pipeline breaks silently (R will error reading the CSV). No fallback.

**WHO data format changes:** The `data_cleaning()` function handles multiple date format variants with heuristics. New format variants from the source will cause date parsing failures (`NA`s) for affected rows.

**`shifting-to-llm-scraper` branch:** An alternative approach exists on `origin/shifting-to-llm-scraper` (same commit date as `main`: 2026-03-03). It is not deployed; `main` is the live branch.

## Discrepancies

- **[gap]** This pipeline is **not listed in the GHA registry table** in `infrastructure/deployments.md`. The registry should carry a `afro-cholera` / `ds-afro-cholera` row (daily `06:00 UTC` Listmonk alert, GHA-only). Add it on the next registry refresh.
- **[stale]** `origin/shifting-to-llm-scraper` branch exists (last commit `2026-03-03`, same date as `main`'s `8c925a0`) — a WIP alternative LLM-based scraper approach. **Not deployed**; `main` is the live branch. Informational only.
- **[stale]** `renv.lock` is committed but the GHA workflow installs packages ad-hoc via `install_if_missing()`/`install.packages()` rather than `renv::restore()`. The pinned lockfile is not the source of truth for the runner — drift risk between `renv.lock` and what actually runs.
- **[stale]** The `emayili`/AWS-SES SMTP send path and the `distribution_list.R` Azure-Blob-dev distribution-list lookup are **fully commented out** in `email.R`. The live path is Listmonk only (list 18, template 8), with country headings rendered blank (`""`, the `countrycode` call is also commented out). `DSCI_AZ_*` and `DSCI_AWS_EMAIL_*` secrets are still injected but unused except SES for the failure-mail step.
- **[conflict]** README says the input is the "WHO AFRO cholera bulletin", but the actual source is the CBPFGMS PowerBI CSV (`CBPFGMS/pfbi-data` → `final_data_for_powerbi_with_kpi.csv`), filtered to cholera rows. The data ultimately derives from WHO, but the README's stated source URL/file is inaccurate.
- **[gap]** GHA installs packages without `renv::restore()` and `send_email()`/`req_perform()` have no error handling — a CRAN outage, source-CSV restructure, or Listmonk error throws an uncaught R error and fails the job (triggers the SES failure mail to `pauline.ndirangu@un.org`). No retry/fallback.

## Downstream consumers

No automated downstream consumers identified. The Listmonk email (list 18) is the terminal output. Subscribers receive alerts manually. There is no DB write, no blob output consumed by another pipeline or app.
