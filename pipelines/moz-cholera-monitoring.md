---
content_type: pipeline
name: moz-cholera-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Cholera Monitoring", ref: ".github/workflows/monitor.yml", schedule: "0 8 * * 2", status: live }
inputs:
  - "blob: projects/ds-aa-moz-cholera-monitoring/monitoring/Mozambique Cholera Data*.xlsx (WHO weekly Excel, manually uploaded)"
  - "blob: projects/ds-aa-moz-cholera-monitoring/monitoring/adm2_population_totals.csv (district populations)"
  - "blob: projects/ds-aa-moz-cholera-monitoring/monitoring/district thresholds.xlsx (province 99th-percentile per-100k thresholds)"
  - "blob: projects/ds-aa-moz-cholera-monitoring/monitoring/.last_processed (JSON state file)"
outputs:
  - "Listmonk campaign email to list 102 (alert) or 103 (test)"
  - "blob: projects/ds-aa-moz-cholera-monitoring/monitoring/.last_processed (updated JSON state file)"
dependencies:
  - ocha-stratus
  - "ocha-relay @ git+https://github.com/OCHA-DAP/ocha-relay.git@v0.2.0"
  - openpyxl
  - pandas
  - "Listmonk list 102 (production alerts)"
  - "Listmonk list 103 (test emails)"
  - "GitHub secrets: DSCI_AZ_BLOB_DEV_SAS, DSCI_AZ_BLOB_DEV_SAS_WRITE, DSCI_LISTMONK_BASE_URL, DSCI_LISTMONK_API_USERNAME, DSCI_LISTMONK_API_KEY"
downstream:
  - "frameworks/moz-cholera (2026-05-22, endorsed) — this pipeline IS the operational monitoring for the MOZ cholera AA framework; the trigger logic here implements that framework's district + province pathways"
  - "Mozambique AA response teams / humanitarian partners subscribed to Listmonk list 102"
depends_on: [listmonk]
source_repo: ocha-dap/ds-aa-moz-cholera-monitoring
source_branch: main
source_sha: d4d3af1
code_ref:
  - run_monitoring.py
  - src/blob.py
  - src/thresholds.py
  - src/alert.py
  - src/constants.py
  - src/state.py
  - src/parse.py
  - src/validate.py
  - src/compare.py
  - .github/workflows/monitor.yml
extra:
  blob_stage: dev
  who_upload_note: "WHO Excel must be manually renamed to start with 'Mozambique Cholera Data' and uploaded to the blob folder before the pipeline runs"
  exit_codes: "0=OK/no trigger, 2=trigger activated, 3=no new file (check-new mode), 1=error"
  not_in_deployments_md: true
visibility: internal
last_synced: "2026-06-17"
---

# Mozambique Cholera Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Weekly (Tuesday 08:00 UTC): ingest manually uploaded WHO cholera Excel from blob → validate → parse new weeks → check per-province AA thresholds → email summary campaign via Listmonk.

## Jobs & schedule

A single GitHub Actions workflow covers both the automated schedule and manual dispatch.

| job | ref | schedule | status |
|---|---|---|---|
| Cholera Monitoring | `.github/workflows/monitor.yml` | `0 8 * * 2` (Tuesday 08:00 UTC) + `workflow_dispatch` | live |

This pipeline is **not** in the Databricks jobs registry and has no Azure web app. It runs purely on GitHub Actions.

## Inputs

**Primary data (manual step required):**
- WHO weekly Excel report: uploaded manually to `projects/ds-aa-moz-cholera-monitoring/monitoring/` in Azure Blob (dev stage). Filename must start with `Mozambique Cholera Data`. The pipeline detects the lexicographically latest file.

**Reference files (static, in the same blob folder):**
- `adm2_population_totals.csv` — district populations (ADM2_PCODE, ADM1_PT, sum_population) for per-100k calculations.
- `district thresholds.xlsx` — province-level 99th-percentile per-100k case thresholds.

**State file:**
- `.last_processed` (JSON) — tracks `last_file_processed`, `last_week_analyzed`, and `activated_provinces` (province → activation week label). Read at start, written at end of every run.

**Excel format expected:**
Sheet named `{YEAR} - Casos` (e.g. `2026 - Casos`), columns: `província`, `distrito`, `adm2_pcode`, then `Semana 1` through `Semana 53`. The WHO file is cumulative — all weeks from Semana 1 are present in each file.

## Steps

1. **Check for new file** (scheduled runs only): compare latest blob file against `last_file_processed`; skip if unchanged.
2. **Download + validate**: sheet names, required columns (`província`, `distrito`, `adm2_pcode`), pcode format (`MZxxxx`).
3. **Parse**: year-aware sheet selection (picks highest year's `{YEAR} - Casos` sheet). Extracts all populated week columns.
4. **Determine new weeks**: compares populated weeks to `last_week_analyzed`; handles year rollover.
5. **Load reference data**: population CSV + thresholds Excel from blob (failures are non-fatal; falls back to floor-only mode).
6. **Threshold evaluation** (per new week, in chronological order):
   - **District trigger**: per province, >= 2 districts meet all of: (a) cases >= floor (100/week non-capital, 300 capital) in all 3 consecutive weeks; AND (b) in each week, cases >= 4x prior week OR cases/100k >= province 99th percentile threshold.
   - **Province RED trigger**: province total >= 2,500 cases for 3 consecutive weeks.
   - **Maputo City**: all districts summed into a synthetic total; applies capital-floor + 4x/per-100k trigger logic.
   - **6-month cooldown**: provinces that triggered within the past 180 days are skipped (reported in email but not re-triggered).
   - Processes weeks in order; records first crossing per province across the batch.
7. **Week-on-week comparison**: top 10 district increases, counts of increases/decreases.
8. **Email via Listmonk** (`ocha-relay`): creates and immediately sends a campaign to list 102 (production) or 103 (test). Subject: `Mozambique Cholera Monitoring | Week N`.
9. **Save state**: updates `.last_processed` blob with new `last_file_processed`, `last_week_analyzed`, `activated_provinces`.

## Outputs

- **Listmonk email campaign** to list 102 (alert) or 103 (test): HTML email with trigger status badge, per-province triggered district tables (with cases by week, per-100k, and thresholds), cooldown table, and week-on-week comparison.
- **State file** (blob): updated `.last_processed` JSON — persists progress and cooldown state across runs.
- The pipeline writes **no DB tables** and no additional blob files beyond the state.

## Dependencies

| Library / service | Role |
|---|---|
| `ocha-stratus` | Blob read/write (`load_blob_data`, `upload_blob_data`, `list_container_blobs`) using `stage="dev"`, `container_name="projects"` |
| `ocha-relay` v0.2.0 | Listmonk email (`ListmonkClient.from_env()`) |
| `openpyxl` | Excel parsing |
| `pandas` | Data manipulation |
| Listmonk list 102 | Production alert recipients |
| Listmonk list 103 | Test email recipients |

**Secrets required (org-level GitHub secrets):**

| Secret | Purpose |
|---|---|
| `DSCI_AZ_BLOB_DEV_SAS` | Blob read SAS token |
| `DSCI_AZ_BLOB_DEV_SAS_WRITE` | Blob write SAS token (for state file) |
| `DSCI_LISTMONK_BASE_URL` | Listmonk API base URL (include `/api` suffix) |
| `DSCI_LISTMONK_API_USERNAME` | Listmonk API username |
| `DSCI_LISTMONK_API_KEY` | Listmonk API key |

## Failure modes & debugging

**Most common failure — no new file processed silently:** On scheduled runs, the pipeline exits 0 if no new file is found. Check the GitHub Actions log for "No new file detected." If the WHO file has arrived but not been uploaded (or uploaded with the wrong filename prefix), the run skips processing entirely. The filename must start with `Mozambique Cholera Data`.

**Validation failure (exit 1):** Check Actions logs for "VALIDATION FAILED" lines. Common causes: wrong sheet name (must match `{YEAR} - Casos`), missing required columns, or malformed pcodes (must be `MZxxxx`).

**Email failure (non-fatal):** If Listmonk is unreachable, the script prints a WARNING and continues. The state is still saved. Check the log for "Failed to send alert email". Verify `DSCI_LISTMONK_*` secrets and Listmonk service health.

**State file corruption:** If `.last_processed` is malformed JSON, `load_state()` falls back to `{}` (empty state) and the pipeline re-processes from the beginning. This is safe but will re-send emails for already-processed weeks unless `--no-email` is used. Use `--force` + `--no-email` to re-process without emailing, then inspect state.

**Cooldown prevents expected trigger:** The `activated_provinces` dict in `.last_processed` tracks when each province last triggered. If a province that should trigger is in cooldown, use `--ignore-cooldown` to bypass for testing (does not modify state), or `--reset-cooldown` to clear all cooldown dates.

**Re-processing a specific file:** Use `workflow_dispatch` with the `filename` input, or locally:
```bash
python run_monitoring.py --filename "Mozambique Cholera Data 2026 W22.xlsx" --no-email --verbose
```

**Logs:** GitHub Actions run logs at `Actions → Cholera Monitoring`. Exit codes: 0=OK/no trigger, 2=trigger activated, 1=error, 3=no new file (check-new mode only).

**Note on blob stage:** `STAGE = "dev"` is hardcoded in `src/constants.py`. The pipeline reads/writes from the dev blob even in production GHA runs. This is intentional for this pipeline (no prod/dev separation for blob storage).

## Downstream consumers

This pipeline is the **operational monitoring** for the endorsed **MOZ cholera AA framework** ([`frameworks/moz-cholera` 2026-05-22](../frameworks/moz-cholera/2026-05-22.md), framework repo `ocha-dap/ds-aa-moz-cholera`). The district + province trigger logic here implements that framework's two pathways; a trigger here (exit 2) is the signal that the framework's AA activation criteria have been met (CERF releases on activation).

Alert emails go to humanitarian partners and Mozambique AA response teams subscribed to Listmonk list 102. No downstream **pipeline or app** reads this pipeline's machine outputs — the email + state file are the terminal outputs; the human/framework decision is the consumer.

## Discrepancies

- `[gap]` **Not in the deployments registry.** This GitHub Actions pipeline is not listed in `infrastructure/deployments.md` (GHA table only covers floodexposure-monitoring, nhc-forecast, imerg, hurricanes-monitoring). The deployment here is verified directly against `.github/workflows/monitor.yml` (single `monitor` job, cron `0 8 * * 2` + `workflow_dispatch`, active/unpaused). The registry should grow to include it. Flagged via `extra.not_in_deployments_md`.
- `[stale]` **Dev blob in production.** `STAGE = "dev"` is hardcoded in `src/constants.py`; the pipeline reads/writes the **dev** blob (`projects` container) even on scheduled production GHA runs. Intentional for this repo (no prod/dev blob split), but it means prod state and reference files live under the dev SAS — note when auditing dev-stage storage. Captured in `extra.blob_stage: dev`.
- `[gap]` **Manual upstream step.** The WHO Excel is **not** ingested automatically — it must be manually renamed to begin `Mozambique Cholera Data` and uploaded to the blob before the scheduled Tuesday run; otherwise the scheduled run exits 0 ("No new file detected") and silently does nothing. Captured in `extra.who_upload_note`.
