---
content_type: pipeline
name: eth-drought-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - name: Ethiopia Drought Monitoring
      ref: .github/workflows/run_monitoring.yml
      schedule: "0 6 6 2,4,5 *"
      status: live
inputs:
  - "DB table: public.seas5 (prod Azure PostgreSQL) — SEAS5 precipitation forecasts per ADM2 pcode"
  - "Blob: ds-aa-eth-drought/exploration/Ethiopia MAM zones.csv (container=projects, stage=dev, via ocha-stratus.load_csv_from_blob)"
  - "Blob: ds-aa-eth-drought/exploration/Ethiopia JJAS zones.csv (container=projects, stage=dev, via ocha-stratus.load_csv_from_blob)"
  - "Blob: ds-aa-eth-drought/processed/eth_adm2_pop.csv (ADM_POP_BLOB in constants, not imported in live run path)"
  - "Blob: ds-aa-eth-drought/processed/eth_asi_mam_jjas_ond.csv (ASI_BLOB in constants, not imported in live run path)"
outputs:
  - "Listmonk campaign: MAM alert email (list ID 104, test list ID 103)"
  - "Listmonk campaign: JJAS alert email (list ID 104, test list ID 103)"
dependencies:
  - ocha-stratus
  - "ocha-relay @ git+https://github.com/OCHA-DAP/ocha-relay.git@v0.2.0"
  - pandas
  - sqlalchemy
  - psycopg2-binary
  - matplotlib
  - python-dotenv
  - "Listmonk list ID 104 (prod Ethiopia drought subscribers)"
  - "Listmonk list ID 103 (test list)"
  - "Secrets: DSCI_AZ_DB_PROD_UID/PW/HOST, DSCI_AZ_DB_DEV_UID/PW/HOST, DSCI_AZ_BLOB_DEV_SAS, DSCI_LISTMONK_BASE_URL/API_USERNAME/API_KEY"
downstream:
  - "Ethiopia drought AA framework decision-makers (email subscribers via Listmonk)"
depends_on:
  - "public.seas5"
  - "listmonk"
discrepancies:
  - "[conflict] DB access uses a custom src/utils/db_utils.get_engine() (raw SQLAlchemy + psycopg2), not stratus.get_engine() — deviates from team convention (feedback_use_stratus_for_db.md). Engine has no sslmode in the URL; Azure PostgreSQL requires SSL, so a local/CI run may need PGSSLMODE=require (feedback_pgsslmode.md)."
  - "[conflict] Mixed stage: SEAS5 read from PROD DB (get_engine(stage='prod')), but zone CSVs read from the DEV blob (STAGE='dev' hardcoded in constants.py). A prod pipeline depending on a dev-stage blob is a fragility."
  - "[stale] ADM_POP_BLOB and ASI_BLOB plus the ERA5/ASI observational thresholds (MAM_ERA5_MARCH_THRESHOLD, JJAS_ERA5_*, *_ASI_THRESHOLD) are defined in constants.py but NOT imported by any live analysis/alert path — placeholders for a future observational trigger; only the SEAS5 predictive triggers actually fire."
  - "[gap] Historical baseline is hardcoded 1997–2025 (N_HIST_YEARS=29, HIST_END_YEAR=2025). The pool does not advance with calendar years; needs a manual constants bump after 2025 or the baseline silently goes stale."
source_repo: ocha-dap/ds-aa-eth-drought-monitoring
source_branch: main
source_sha: 45b35fe
code_ref:
  - run_monitoring.py
  - src/analysis/mam.py
  - src/analysis/jjas.py
  - src/alert/email.py
  - src/datasources/seas5.py
  - src/constants.py
  - .github/workflows/run_monitoring.yml
extra:
  note_db_access: "Uses a custom db_utils.get_engine() (src/utils/db_utils.py) with raw SQLAlchemy + psycopg2, not stratus.get_engine(). This is a known deviation from team conventions (see feedback_use_stratus_for_db.md)."
  note_blob_stage: "Blob reads use stage='dev' hardcoded in constants.py (STAGE = 'dev'). The prod DB is used for SEAS5, but blob zone CSVs come from the dev container."
  note_constants_unused: "ASI_BLOB and ADM_POP_BLOB are defined in constants.py but not imported or used in the live analysis/alert code paths. They are likely placeholders for future observational trigger checks."
  exit_codes: "0 = no trigger reached; 2 = trigger reached; 1 = error. GHA workflow treats exit 2 as success (continue-on-error: true + explicit fail-on-error step)."
  analysis_reference: "Logic mirrors ds-aa-eth-drought notebooks: 05_4_drought_trigger_summary_mam.ipynb (MAM) and 05_5_drought_trigger_summary_jjas.ipynb (JJAS)."
  historical_baseline: "Fixed 1997-2025 (29 years). Current year is ranked against this pool without being added to it."
visibility: internal
last_synced: "2026-06-22"
---

# Ethiopia Drought Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Three times a year (Feb, Apr, May), pull SEAS5 forecast data from the prod DB, compute MAM and JJAS season trigger indicators against a 1997-2025 baseline, and email a summary (with bar charts) to subscribers via Listmonk.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Ethiopia Drought Monitoring | `.github/workflows/run_monitoring.yml` | `0 6 6 2,4,5 *` (6th at 06:00 UTC, Feb/Apr/May) | live |

The workflow also supports `workflow_dispatch` with optional `year` and `test` inputs for manual runs.

## Inputs

- **`public.seas5` (prod DB):** SEAS5 precipitation forecasts per ADM2 pcode and issued/valid date. Queried via `src/datasources/seas5.py` → `fetch_seas5_data()` using a raw SQLAlchemy engine (`src/utils/db_utils.py`), not `stratus.get_engine()`.
- **`ds-aa-eth-drought/exploration/Ethiopia MAM zones.csv`** (container `projects`, stage `dev`): `adm2_pcode` column defining the MAM season zone set, loaded via `stratus.load_csv_from_blob(MAM_ZONES_BLOB, stage="dev", container_name="projects")`.
- **`ds-aa-eth-drought/exploration/Ethiopia JJAS zones.csv`** (container `projects`, stage `dev`): `adm2_pcode` column defining the JJAS season zone set, loaded the same way.
- ASI and population blobs are defined in `constants.py` but not wired into the live code paths yet (placeholders for future observational triggers).

## Steps

1. **Season routing** (`run_monitoring.py`): month determines which season(s) to run — February runs MAM only, April runs JJAS only (Apr forecast), May runs JJAS only (Apr + May forecasts).
2. **Load zone pcodes** from blob CSVs via `ocha-stratus`.
3. **Fetch SEAS5 historical data** (1997–2025) from `public.seas5` prod DB, filter by issued/valid month for the season.
4. **Compute return periods** against the fixed 29-year baseline (`N_HIST_YEARS = 29`). Current year ranked against that pool without being added to it.
5. **Count trigger zones** (pcodes with return period ≥ 5-year) and compare to thresholds.
6. **Build HTML email** with embedded base64 bar charts (`src/alert/email.py`).
7. **Send via Listmonk** using `ocha-relay.ListmonkClient.from_env()` — one campaign per season.

Trigger thresholds:

| Season | Forecast | Threshold |
|---|---|---|
| MAM | SEAS5 Feb issued | ≥ 15 zones at 5yr RP |
| JJAS | SEAS5 Apr issued | ≥ 35 zones at 5yr RP |
| JJAS | SEAS5 May issued | ≥ 35 zones at 5yr RP |

Exit codes: `0` = no trigger, `2` = trigger reached, `1` = error.

## Outputs

- **Listmonk email campaign (MAM):** sent to list ID 104 (prod) or 103 (test). Subject: `Ethiopia MAM Drought Monitoring - {year}`. Includes SEAS5 Feb bar chart and trigger status table.
- **Listmonk email campaign (JJAS):** sent to list ID 104 (prod) or 103 (test). Subject: `Ethiopia JJAS Drought Monitoring - {year}`. Includes SEAS5 Apr and/or May bar charts and trigger status table.
- No DB writes. No blob writes. Emails are the sole output.

## Dependencies

- `ocha-stratus` — blob reads (zone CSVs)
- `ocha-relay` v0.2.0 — Listmonk campaign creation + send
- `sqlalchemy` + `psycopg2-binary` — DB reads (SEAS5; direct, not via stratus)
- `matplotlib` — embedded bar charts in email HTML
- `python-dotenv` — `.env` loading for local dev
- GHA secrets: `DSCI_AZ_DB_PROD_*`, `DSCI_AZ_DB_DEV_*`, `DSCI_AZ_BLOB_DEV_SAS`, `DSCI_LISTMONK_*`

## Failure modes & debugging

- **Missing SEAS5 data for a season:** analysis returns `None` for zone count; that season's email is skipped silently (not an error). Check `public.seas5` table in prod DB for the relevant issued_date range.
- **DB connection failure:** script exits with code 1. Check `DSCI_AZ_DB_PROD_*` secrets in the repo and `PGSSLMODE=require` if connecting locally (Azure PostgreSQL requires SSL; the GHA environment may need this env var set — see `feedback_pgsslmode.md`).
- **Listmonk send failure:** logged as `WARNING` and execution continues; does not set exit code 1. Check `DSCI_LISTMONK_*` secrets and `ocha-relay` version.
- **Wrong blob stage:** `STAGE = 'dev'` is hardcoded in `src/constants.py`. Zone CSVs will always come from the dev blob container. If those blobs are missing or stale, the analysis will fail with a stratus load error.
- **Logs:** GitHub Actions run logs at `ocha-dap/ds-aa-eth-drought-monitoring` → Actions → `Ethiopia Drought Monitoring`.
- **Manual re-run:** trigger via GHA `workflow_dispatch` with `year` and optionally `test: true` to send to list 103 instead of 104.

## Downstream consumers

- **Ethiopia drought AA framework decision-makers** receive the monitoring email. There is no app or dashboard consuming this pipeline's output — email is the terminal deliverable.
- The upstream analysis notebooks in `ds-aa-eth-drought` define the trigger logic this pipeline implements; that repo is the analytical parent but not a runtime dependency.

## Discrepancies

Tagged per `INGESTION.md` ([stale] = old code lying around, not the live trigger; [conflict] = disagrees with convention/authority; [gap] = something missing/unfinished).

- **[conflict] Non-stratus DB engine.** `src/utils/db_utils.get_engine()` builds a raw SQLAlchemy/psycopg2 engine instead of `stratus.get_engine()` (deviation from team convention). URL has no `sslmode`; Azure PostgreSQL requires SSL, so a local/CI invocation may need `PGSSLMODE=require`.
- **[conflict] Mixed prod/dev stage.** SEAS5 is read from the **prod** DB (`get_engine(stage="prod")`) but zone CSVs come from the **dev** blob (`STAGE='dev'` hardcoded). A prod-facing pipeline depending on a dev-stage blob is a fragility — flagged in the deployments registry too.
- **[stale] Unused observational config.** `ADM_POP_BLOB`, `ASI_BLOB`, and the ERA5/ASI thresholds in `constants.py` are not imported by any live path. Only the SEAS5 predictive triggers (MAM Feb, JJAS Apr/May) actually fire; the observational pieces are placeholders.
- **[gap] Hardcoded baseline.** Return periods rank against a fixed 1997–2025 pool (`N_HIST_YEARS=29`, `HIST_END_YEAR=2025`). It does not advance automatically; after 2025 the baseline needs a manual constants bump or it silently goes stale.
- Deployment is registered in [infrastructure/deployments.md](../infrastructure/deployments.md) (GitHub Actions section). It was absent from that registry at ingestion time; added during this QA pass.
