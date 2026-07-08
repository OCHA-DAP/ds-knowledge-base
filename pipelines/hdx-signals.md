---
content_type: pipeline
name: hdx-signals
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor ACLED conflict", ref: ".github/workflows/monitor_acled_conflict.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor ACAPS Inform Severity", ref: ".github/workflows/monitor_acaps_inform_severity.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor IDMC displacement conflict", ref: ".github/workflows/monitor_idmc_displacement_conflict.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor IDMC displacement disaster", ref: ".github/workflows/monitor_idmc_displacement_disaster.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor IPC food insecurity", ref: ".github/workflows/monitor_ipc_food_insecurity.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor JRC agricultural hotspots", ref: ".github/workflows/monitor_jrc_agricultural_hotspots.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor WFP market monitor", ref: ".github/workflows/monitor_wfp_market_monitor.yaml", schedule: "cron: 0 7 * * 1-5", status: live }
    - { name: "Monitor WHO cholera", ref: ".github/workflows/monitor_who_cholera.yaml", schedule: "on-demand (workflow_dispatch only, no cron)", status: live }
    - { name: "Triage Signals", ref: ".github/workflows/triage_signals.yaml", schedule: "event: push to any branch (+ workflow_dispatch)", status: live }
    - { name: "Post Slack update", ref: ".github/workflows/post_slack_update.yaml", schedule: "cron: 0 8 * * 1-5", status: live }
    - { name: "Backup Mailchimp audience", ref: ".github/workflows/backup_mailchimp.yaml", schedule: "cron: 0 8 * * 1", status: live }
    - { name: "Run user-analytics", ref: ".github/workflows/user_audience_analysis.yml", schedule: "cron: 0 8 * * 1", status: live }
    - { name: "Check CHANGES.md", ref: ".github/workflows/check_changes.yml", schedule: "event: pull_request to main", status: live }
    - { name: "Test HDX Signals", ref: ".github/workflows/test_signals.yml", schedule: "event: pull_request to main (+ workflow_dispatch)", status: live }
    - { name: "Lint", ref: ".github/workflows/lint.yaml", schedule: "event: push/pull_request to main", status: live }
    - { name: "Publish PROMPTS.md", ref: ".github/workflows/publish_prompts.yml", schedule: "event: pull_request to main", status: live }
    - { name: "Update indicator mapping", ref: ".github/workflows/update_indicator_mapping.yml", schedule: "on-demand (workflow_dispatch)", status: live }
    - { name: "Update data dictionary", ref: ".github/workflows/update_data_dictionary.yml", schedule: "on-demand (workflow_dispatch)", status: live }
    - { name: "Update ACLED info", ref: ".github/workflows/update_acled_info.yml", schedule: "on-demand (workflow_dispatch)", status: live }
    - { name: "Update locations data", ref: ".github/workflows/update_locations_data.yml", schedule: "on-demand (workflow_dispatch)", status: live }
    - { name: "Update ASAP code mapping", ref: ".github/workflows/update_asap_codes.yml", schedule: "on-demand (workflow_dispatch)", status: live }
inputs:
  - "ACLED API (acleddata.com, OAuth token) — conflict events"
  - "ACAPS INFORM Severity API (api.acaps.org)"
  - "IDMC IDU API (via {idmc} R package) — conflict + disaster displacement"
  - "IPC/CH API (via {ripc} R package, IPC_API_KEY) — food insecurity phase classifications"
  - "JRC Agricultural Hotspots (agricultural-production-hotspots.ec.europa.eu, zipped HTML/timeseries)"
  - "WFP Market Monitor data — provided directly by WFP into the `wfp` blob container (dev stage), not pulled from a public API"
  - "WHO AFRO cholera bulletins, pre-scraped by CERF and published to a CERF-hosted CSV link (`CERF_CHOLERA_DATA` env var)"
  - "Azure blob container `hdx-signals` (prod + dev) — static reference assets under `input/` (admin-0 polygons, centroids, cities, locations metadata, ASAP/GAUL mapping, indicator mapping, data dictionary) produced by the `src-static` scripts"
  - "Mailchimp audience `HDX Signals` — existing subscriber/segment state read during triage and analytics"
outputs:
  - "Azure blob `hdx-signals` container, `output/{indicator_id}/signals.parquet` (+ `/test/` dry-run variant) — staged alert content per indicator"
  - "Azure blob `hdx-signals` container, `output/signals.parquet` — approved/triaged Signals dataset, the source pushed to HDX"
  - "HDX dataset `hdx-signals` (via repository_dispatch webhook to `OCHA-DAP/hdx-signals-alerts`, which pulls from Azure and pushes to HDX — no data leaves Azure via this repo directly)"
  - "Mailchimp campaigns/templates/images in the `HDX Signals` audience — drafted on signal generation, sent on triage approval"
  - "Slack notifications to `hdx-signals-bot` (and `hdx-signals-bot-testing`) channels — daily run-status + signal-generated updates"
  - "`docs/PROMPTS.md`, indicator mapping / data dictionary parquet, ACLED/ASAP/locations reference assets — repo-committed or blob-published static assets"
dependencies:
  - "R + {box} for module structure, {renv} for package management (not the team's Python stack)"
  - "own Azure Blob client (`src/utils/cloud_storage.R`, {AzureStor}) — bespoke to this repo, not `ocha-stratus`"
  - "own Mailchimp REST client (`src/email/mailchimp/*.R`, {httr2}) — bespoke to this repo, not `ocha-relay`/Listmonk or the Python `ocha-mailchimp` library"
  - "{ripc} R package — IPC API client"
  - "{idmc} R package — IDMC IDU client"
  - "Azure OpenAI (`AzureOpenAI` client, deployment `gpt-5`, chat completions) via `{reticulate}` → `src/python_scripts/azure_script.py` — AI-generated summary text for signal emails (no plain-OpenAI code path)"
  - "`ocha-dap/hdx-signals-actions@v3` — shared composite GitHub Action that provisions the R/renv environment for every workflow in this repo"
  - "`OCHA-DAP/hdx-signals-alerts` — downstream repo/pipeline that actually pushes the Azure output to the HDX platform, triggered via `repository_dispatch`"
  - "Secrets: `DSCI_AZ_BLOB_PROD_SAS_WRITE`, `DSCI_AZ_BLOB_DEV_SAS_WRITE`, `MAILCHIMP_API_KEY`, `HS_HDX_BEARER`, `HS_SLACK_URL`(+`_TEST`), `GH_TOKEN`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`/`_ENDPOINT`/`_API_VERSION`, `ACLED_EMAIL_ADDRESS`/`ACLED_PASSWORD`, `IDMC_API`, `IPC_API_KEY`, `CERF_CHOLERA_DATA`, `HS_EMAIL`, `HS_SURVEY_LINK`, `HS_ADMIN_NAME`"
downstream:
  - "HDX Signals website (data.humdata.org/signals) — public signup + signal archive"
  - "HDX dataset `hdx-signals` on data.humdata.org — published resource, via `hdx-signals-alerts`"
  - "GitBook methodology docs (un-ocha-centre-for-humanitarian.gitbook.io/hdx-signals) — public trigger/methodology documentation per dataset"
  - "Mailchimp `HDX Signals` email subscriber list — external recipients of signal alert emails"
depends_on:
  - "ipc"
source_repo: ocha-dap/hdx-signals
source_branch: main
source_sha: e2cd8d3
code_ref:
  - "src/indicators/README.md"
  - "src/signals/README.md"
  - "src/utils/cloud_storage.R"
  - "src/utils/push_hdx.R"
  - "src/email/mailchimp"
  - "src/run/run_triage_signals.R"
extra:
  db: "no Postgres/DB tables — all storage is Azure Blob (`hdx-signals` container) plus Mailchimp; not part of the team's `ocha-stratus`/DB conventions"
  indicator_ids: [acled_conflict, acaps_inform_severity, idmc_displacement_conflict, idmc_displacement_disaster, ipc_food_insecurity, jrc_agricultural_hotspots, wfp_market_monitor, who_cholera]
visibility: public
last_synced: "2026-07-07"
---

# HDX Signals

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*daily (weekdays): scan 8 humanitarian indicator datasets for significant negative changes → generate an AI-summarized alert email + map/plot → stage to Azure → human triages/approves → send via Mailchimp + push the approved dataset to HDX.*

## Jobs & schedule

A pipeline repo is often several jobs/workflows with different schedules. All are GitHub Actions (GHA-only; no Databricks). One indicator = one monitoring job, all scheduled together at `07:00 UTC` weekdays, plus supporting jobs for triage, comms, and static-asset maintenance.

| job | ref | schedule | status |
|---|---|---|---|
| Monitor ACLED conflict | `monitor_acled_conflict.yaml` | `0 7 * * 1-5` | live |
| Monitor ACAPS Inform Severity | `monitor_acaps_inform_severity.yaml` | `0 7 * * 1-5` | live |
| Monitor IDMC displacement (conflict) | `monitor_idmc_displacement_conflict.yaml` | `0 7 * * 1-5` | live |
| Monitor IDMC displacement (disaster) | `monitor_idmc_displacement_disaster.yaml` | `0 7 * * 1-5` | live |
| Monitor IPC food insecurity | `monitor_ipc_food_insecurity.yaml` | `0 7 * * 1-5` | live |
| Monitor JRC agricultural hotspots | `monitor_jrc_agricultural_hotspots.yaml` | `0 7 * * 1-5` | live |
| Monitor WFP market monitor | `monitor_wfp_market_monitor.yaml` | `0 7 * * 1-5` | live |
| Monitor WHO cholera | `monitor_who_cholera.yaml` | workflow_dispatch only (**no cron**) | live |
| Triage Signals | `triage_signals.yaml` | `push` to any branch + workflow_dispatch | live |
| Post Slack update | `post_slack_update.yaml` | `0 8 * * 1-5` | live |
| Backup Mailchimp audience | `backup_mailchimp.yaml` | `0 8 * * 1` (Mon) | live |
| Run user-analytics | `user_audience_analysis.yml` | `0 8 * * 1` (Mon) | live |
| Check CHANGES.md | `check_changes.yml` | PR to `main` | live |
| Test HDX Signals | `test_signals.yml` | PR to `main` + dispatch | live |
| Lint | `lint.yaml` | push/PR to `main` | live |
| Publish PROMPTS.md | `publish_prompts.yml` | PR to `main` (auto-commits) | live |
| Update indicator mapping / data dictionary / ACLED info / locations data / ASAP codes | `update_*.yml` | workflow_dispatch only | live |

Every monitoring job accepts `HS_FIRST_RUN`/`HS_DRY_RUN`/`HS_LOCAL`/`LOG_LEVEL` dispatch inputs so a run can be forced into dry-run/local mode manually; on schedule they default to a live run (`HS_LOCAL=FALSE`, `HS_DRY_RUN=FALSE`).

## Inputs

Eight indicators, each with its own upstream data source (see `dependencies` and `code_ref: src/indicators/*/utils/raw_*.R` for exact pulls):

- **`acled_conflict`** — ACLED API (`acleddata.com`), OAuth-token auth.
- **`acaps_inform_severity`** — ACAPS INFORM Severity Index API.
- **`idmc_displacement_conflict` / `idmc_displacement_disaster`** — IDMC's Internal Displacement Update (IDU) via the `{idmc}` R package; one shared indicator module (`src/indicators/idmc_displacement/`) with `conflict/` and `disaster/` sub-entrypoints.
- **`ipc_food_insecurity`** — IPC/CH API via the `{ripc}` R package (see [`infrastructure/datasets/ipc`](../infrastructure/datasets/ipc.md) for the shared API reference).
- **`jrc_agricultural_hotspots`** — JRC's agricultural production hotspots timeseries (zipped download).
- **`wfp_market_monitor`** — not pulled from a public API; WFP writes data directly into a dedicated `wfp` blob container (dev stage) that this repo reads from.
- **`who_cholera`** — not from WHO directly; CERF scrapes WHO AFRO outbreak bulletins and exposes a CSV via a link stored in `CERF_CHOLERA_DATA`.

All indicators also read static reference assets (admin boundaries, location metadata, indicator mapping, data dictionary) from the `hdx-signals` Azure container's `input/` prefix, produced by the `src-static` update scripts (own on-demand workflows).

## Steps

Each indicator's `__init__.R` re-exports a common function surface (`raw()`, `wrangle()`, `alert()`, `plot()`, `map()`, `summary()`) and calls `generate_signals()` (`src/signals`) when run directly, so all 8 monitoring jobs share one orchestration path:

1. Download + wrangle the indicator's raw data (`raw()`/`wrangle()`).
2. Detect new alerts against the indicator's threshold/change logic (`alert()`).
3. On a new alert: build maps/plots (`src/images`), generate an AI-written summary (Azure OpenAI, `gpt-5` deployment, prompts in `src/indicators/{id}/prompts/*.txt`), assemble the HTML email (`src/email/components`), and create (but not send) a Mailchimp template + draft campaign.
4. Stage everything — content, Mailchimp IDs, campaign URLs — to `output/{indicator_id}/signals.parquet` (or `.../test/...` under `HS_DRY_RUN`).
5. **Triage Signals** (`src/run/run_triage_signals.R`, human-driven via `workflow_dispatch` with `USER_COMMAND=APPROVE|DELETE|ARCHIVE` + an explicit confirmation input): on approve, moves the row from the per-indicator staging file into the final `output/signals.parquet`, sends the Mailchimp campaign, and calls `push_hdx()` to fire a `repository_dispatch` webhook at `OCHA-DAP/hdx-signals-alerts`, which pulls the updated dataset from Azure and publishes it to HDX. On delete, all associated Mailchimp assets (template/campaign/images) are removed programmatically before the staged row is dropped.
6. Supporting jobs independently post daily Slack digests of what ran/what alerted (`post_slack_update.yaml`), back up the Mailchimp audience weekly, and compute subscriber/campaign analytics weekly.

Code detail: [`src/indicators/README.md`](https://github.com/OCHA-DAP/hdx-signals/blob/main/src/indicators/README.md), [`src/signals/README.md`](https://github.com/OCHA-DAP/hdx-signals/blob/main/src/signals/README.md).

## Outputs

- `output/{indicator_id}/signals.parquet` (+ `/test/` dry-run copy) per indicator — staged, pre-triage alert content, in the Azure `hdx-signals` container.
- `output/signals.parquet` — the approved, published Signals dataset; this is what `hdx-signals-alerts` reads and pushes to the **HDX `hdx-signals` dataset**.
- Mailchimp campaigns/templates/images in the `HDX Signals` audience (drafted on alert, sent on triage approval).
- Slack messages to the `hdx-signals-bot` channel (run status + new-signal notices) and `hdx-signals-bot-testing` for test runs.
- Static/reference outputs from the on-demand `update_*` workflows: `indicator_mapping.parquet`, data dictionary, `acled_info.parquet`, locations/adm0/centroids/cities spatial files, ASAP↔ISO3 mapping, `docs/PROMPTS.md`.

## Dependencies

- **Language/tooling**: R with `{box}` for module imports and `{renv}` for package locking — this repo does not use the team's Python `ocha-stratus`/`ocha-lens`/`ocha-relay` stack at all.
- **Storage**: its own Azure Blob helpers (`src/utils/cloud_storage.R`, `{AzureStor}`) against the `hdx-signals` container (prod/dev) plus a separate `wfp` container (dev stage) for externally-supplied WFP data.
- **Email**: its own Mailchimp REST client built on `{httr2}` (`src/email/mailchimp/`) — **not** Listmonk/`ocha-relay` (the team's newer comms convention) and **not** the Python `ocha-mailchimp` library ([`infrastructure/libs/ocha-mailchimp`](../infrastructure/libs/ocha-mailchimp.md)); this predates both.
- **AI summaries**: Azure OpenAI only — the `AzureOpenAI` client (deployment `gpt-5`) in `src/python_scripts/azure_script.py`, sourced into R via `{reticulate}` (`src/utils/python_setup.R`). `OPENAI_API_KEY` is still declared as a workflow secret but the summary code reads only the `AZURE_OPENAI_*` vars.
- **Indicator-specific R packages**: `{ripc}` (IPC), `{idmc}` (IDMC IDU).
- **CI plumbing**: `ocha-dap/hdx-signals-actions@v3`, a shared composite Action that sets up the R/renv environment for every workflow in this repo.
- **Downstream trigger**: `OCHA-DAP/hdx-signals-alerts` repo, invoked via a `repository_dispatch` webhook (`HS_HDX_BEARER`) — the actual Azure→HDX transfer happens there, not in this repo.
- Full secret/env inventory: [`ENVIRONMENT.md`](https://github.com/OCHA-DAP/hdx-signals/blob/main/ENVIRONMENT.md) in the repo.

## Failure modes & debugging

- **Not yet in `infrastructure/pipeline-registry.md` or `infrastructure/spoke-repos.md`.** This ingestion is the first KB pass over `hdx-signals`; health/visibility tracking for its GHA jobs isn't wired into the generated registry yet. <!-- TODO: add hdx-signals' GHA jobs to the pipeline registry sweep -->
- **`who_cholera` has no schedule** — it's `workflow_dispatch`-only (no `schedule:` block), unlike the other 7 indicators which all run `0 7 * * 1-5`. If cholera alerts look stale, this is why — someone must trigger it manually, or the cron needs adding.
- **Retries**: every monitoring job wraps its `Rscript` call in `nick-fields/retry@v3` (2 attempts, 20 min timeout, 120s wait) — a single flaky API call won't fail the run outright, but 2 consecutive failures will.
- **`HS_FIRST_RUN` misuse**: `generate_signals()` throws if a first run is attempted when historical data already exists, or if monitoring is attempted before a first run has ever been done for an indicator — check `HS_FIRST_RUN` wasn't left `TRUE` on a scheduled run.
- **Triage is destructive and manual**: `USER_COMMAND=DELETE` removes Mailchimp templates/campaigns/images by ID before dropping the staged parquet row — always use the repo's triage script rather than manually deleting Mailchimp assets, or the staged parquet and Mailchimp state can desync.
- **CERF cholera feed is an external dependency two hops removed from WHO** — `CERF_CHOLERA_DATA` points at a CERF-hosted scrape of WHO AFRO bulletins, not an official WHO API; if it goes stale or the link rotates, cholera monitoring silently has nothing new to alert on (no schedule to notice either, per above).
- **WFP market monitor data is push-based, not pulled** — WFP writes into the `wfp` dev blob container externally; if WFP stops publishing, the monitor job runs successfully but simply finds no new data (not a code failure).
- **`HS_LOCAL=TRUE`** suppresses all Azure/Mailchimp/OpenAI writes — useful to confirm this is set correctly when a manual dispatch run "succeeded" but nothing shows up staged.
- **Logs**: GitHub Actions run logs per workflow in `OCHA-DAP/hdx-signals`; `LOG_LEVEL` dispatch input controls verbosity (`DEBUG`/`INFO`/`WARNING`/`ERROR`). Slack (`hdx-signals-bot`) carries a daily digest but is not a substitute for checking the Action run itself on failure.
- **Lint is a hard gate**: `lintr::lint_dir()` runs with `LINTR_ERROR_ON_LINT: true` on every push/PR to `main` — a lint violation fails CI outright.

## Downstream consumers

- **HDX Signals** public website and signup (data.humdata.org/signals) — the product this pipeline powers end-to-end.
- **HDX dataset `hdx-signals`** on data.humdata.org — published via the sibling `OCHA-DAP/hdx-signals-alerts` repo.
- **GitBook methodology docs** — public per-indicator trigger/methodology documentation referenced from the README; the `who_cholera` methodology is the exception, documented in-repo (`src/indicators/who_cholera/README.md`) since it isn't publicly subscribable in the same way.
- **Mailchimp `HDX Signals` subscriber audience** — the actual alert-email recipients.
