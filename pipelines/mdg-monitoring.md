---
content_type: pipeline
name: mdg-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Monitor IMERG", ref: ".github/workflows/run_monitor_imerg.yml", schedule: "0 16 * * *", status: live }
inputs:
  - "DB table: public.imerg (IMERG v7 daily raster stats, prod)"
  - "DB table: public.polygon (MDG ADM1 pcodes and names, prod)"
  - "Blob: ds-aa-mdg-monitoring/monitoring/distribution_list.csv (or test_distribution_list.csv)"
outputs:
  - "Email: daily informational email (French) to distribution list via AWS SES"
dependencies:
  - azure-storage-blob==12.22.0
  - sqlalchemy==2.0.36
  - psycopg2-binary==2.9.10
  - ocha-stratus==0.1.7
  - jinja2==3.1.6
  - matplotlib==3.10.0
  - html2text==2024.2.26
  - python-dotenv==1.0.1
  - "AWS SES (DSCI_AWS_EMAIL_HOST / USERNAME / PASSWORD / ADDRESS)"
  - "Azure Blob DEV SAS (DSCI_AZ_BLOB_DEV_SAS_WRITE)"
  - "Azure DB PROD credentials (DSCI_AZ_DB_PROD_HOST / UID / PW)"
  - "GHA repo var: TEST_LIST (False = real list; anything else = test list)"
downstream:
  - "frameworks/mdg-storms — Madagascar cyclone AA framework (this is its rainfall observational-monitoring email; recipients are the framework's ops team)"
depends_on: [imerg]
source_repo: ocha-dap/ds-aa-mdg-monitoring
source_branch: main
source_sha: e80df48
code_ref:
  - pipelines/monitor_imerg.py
  - .github/workflows/run_monitor_imerg.yml
  - src/datasources/imerg.py
  - src/datasources/polygon.py
  - src/monitoring/emails.py
  - src/monitoring/plotting.py
  - src/datasources/meteofr.py
  - src/utils/exposure.py
extra:
  exposure_plots_branch: "Manual wind-exposure notebooks and meteofr track-parsing utilities (src/datasources/meteofr.py, src/utils/exposure.py, src/monitoring/plotting.py bullseye/bubble plotters) — merged into main via the exposure-plots work (PR #10, then the exposure-plots branch was deleted). These are NOT part of the scheduled pipeline — they are analyst tools for running during cyclone events. The scheduled Monitor IMERG job runs off main."
  email_language: French
  trigger_threshold: "RAIN_THRESH = 300 mm (3-day sum, region-averaged, any ADM1 region). Code fires on strictly > 300 mm (README says >= 300; see discrepancies)."
  blob_uses_raw_sdk: "blob_utils.py uses raw azure-storage-blob SDK (not ocha-stratus). Flag for future migration."
  deployment_registry: "Listed in deployments.md → GitHub Actions pipelines (added during 2026-06-17 ingestion). GHA-only — not a Databricks job or Azure web app."
  discrepancies:
    - "[stale] (resolved 2026-06-22) Previously the analyst exposure-plots branch was the repo HEAD while the scheduled workflow ran off main. The exposure-plots work has since merged into main (PR #10, branch deleted), so this page now pins main (source_sha e80df48) and deployed branch == checked-out branch. Kept as a note in case older references to the exposure-plots branch resurface."
    - "[conflict] Threshold operator: code uses strict greater-than (`df_grouped['mean'].max() > RAIN_THRESH`, src/monitoring/emails.py) so the trigger fires above 300 mm, but README states '>= 300 mm in any region'. Exactly 300.0 mm would NOT activate per the code."
    - "[stale] blob_utils.py uses the raw azure-storage-blob SDK rather than ocha-stratus (which is installed and used only in analyst notebooks). Informational — flagged for future migration, not a live error."
visibility: internal
last_synced: "2026-06-22"
---

# MDG Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Daily at 16:00 UTC: pull IMERG ADM1 raster stats for Madagascar → check 3-day rainfall total against 300 mm threshold → send French-language informational email with bar chart to distribution list via AWS SES.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor IMERG | `.github/workflows/run_monitor_imerg.yml` | `0 16 * * *` (daily 16:00 UTC) | live |

The workflow also has a `workflow_dispatch` trigger accepting an optional `date` parameter (YYYY-MM-DD) for backfill/manual runs. The script is invoked as `python pipelines/monitor_imerg.py [--date YYYY-MM-DD]`.

**Note:** README says "To run on GH Actions, use the main branch." The GHA workflow is on main; the analyst exposure-plots notebooks (now merged into main, PR #10) add analyst tooling only and do not alter the scheduled workflow.

## Inputs

- **`public.imerg`** (prod DB): daily IMERG v7 raster stats per MDG ADM1 pcode, queried for a 3-day window centered on `run_date`. Populated upstream by the IMERG pipeline (`Run IMERG` Databricks job).
- **`public.polygon`** (prod DB): ADM1 polygon metadata (pcode, name) for MDG, filtered by `iso3='MDG'` and `adm_level=1`.
- **Blob `ds-aa-mdg-monitoring/monitoring/distribution_list.csv`** (or `test_distribution_list.csv`): recipient list with columns `email`, `name`, `info` (to/cc). Loaded from the DEV blob container using the raw Azure SDK (`blob_utils.py`).

Default `run_date` = `today - 2 days`, ensuring raster stats are available (stats run at ~15:00 UTC; email at 16:00).

## Steps

1. **Parse args**: determine `run_date` (default: T-2) and compute `dates` = 3-day window ending at `run_date + 1 day`.
2. **Fetch polygon data** (`src/datasources/polygon.py`): query `public.polygon` for MDG ADM1 pcodes.
3. **Fetch IMERG data** (`src/datasources/imerg.py`): query `public.imerg` for those pcodes over the 3-day date range.
4. **Validate**: raise `ValueError` if any of the 3 dates is missing from the result.
5. **Plot** (`src/monitoring/plotting.py → plot_rainfall`): stacked bar chart of 3-day precipitation per ADM1 region, with a red dashed threshold line at 300 mm. Labels show totals above bars.
6. **Send email** (`src/monitoring/emails.py → send_info_email`): load distribution list; evaluate `obsv_trigger` = "ACTIVÉ" if `df_grouped["mean"].max() > RAIN_THRESH` else "PAS ACTIVÉ" (strict greater-than); render Jinja2 HTML template; send via `smtplib.SMTP_SSL` (port 465, `DSCI_AWS_EMAIL_PORT` overridable) to AWS SES. Chart attached as inline PNG.

## Outputs

- **Email**: French-language informational email, subject line `"Action anticipatoire Madagascar – précipitations autour de {center_date}"`, with embedded 3-day rainfall bar chart and trigger status. Sent to distribution list via AWS SES.
- **No DB writes, no blob writes** from the scheduled pipeline.

The exposure-plots work (merged into main, PR #10) adds analyst-facing outputs (local CSV export of ADM1 wind exposure per speed band), but these are manual notebook runs, not pipeline outputs.

## Dependencies

| dependency | detail |
|---|---|
| AWS SES | `DSCI_AWS_EMAIL_HOST/USERNAME/PASSWORD/ADDRESS` GHA secrets; port 465 SSL |
| Azure Blob DEV | `DSCI_AZ_BLOB_DEV_SAS_WRITE` — distribution list CSVs |
| Azure DB PROD | `DSCI_AZ_DB_PROD_HOST/UID/PW` — IMERG and polygon tables |
| `TEST_LIST` GHA var | `False` → real distribution list; any other value → test list |
| ocha-stratus 0.1.7 | used in analyst notebooks (codab, blob access); prod pipeline uses raw SDK |
| azure-storage-blob 12.22.0 | raw SDK in `blob_utils.py` (not stratus — flag for future migration) |
| Jinja2 + email_assets/ | HTML email templates in `email_assets/templates/informational.html` |

## Failure modes & debugging

- **Missing IMERG dates**: script raises `ValueError` with the missing dates. Root cause: upstream IMERG pipeline (`Run IMERG`, Databricks job `666239885322861`) ran late or failed. Check Databricks job logs first.
- **DB connection failure**: raw psycopg2 + SQLAlchemy. `PGSSLMODE=require` is needed for Azure PostgreSQL — not set in `db_utils.py`, must be set as env var or in the connection string. Add `PGSSLMODE=require` to GHA environment if seeing SSL handshake errors.
- **Email send failure**: AWS SES credentials or sending quota. Check `DSCI_AWS_EMAIL_*` secrets are set in the repo. If `TEST_LIST` is not set to `"False"`, emails go to the test list (silent failure for real recipients — intentional).
- **Invalid emails in distribution list**: script prints a warning and skips invalid entries (does not fail). Check the blob CSV for malformed addresses.
- **GHA schedule drift**: workflow has a `keep-alive` job to prevent GHA from disabling the schedule. If the schedule stops firing, check GHA has not disabled it and re-enable via `workflow_dispatch`.
- **Logs**: GHA Actions tab on `ocha-dap/ds-aa-mdg-monitoring`, workflow "Monitor IMERG".

## Downstream consumers

- **Madagascar cyclone AA framework operations** ([frameworks/mdg-storms](../frameworks/mdg-storms/README.md)): email recipients (humanitarian partners, national authorities). This is the framework's rainfall observational-monitoring channel. No downstream pipelines consume this output directly — it is a terminal notification step.
- The exposure-plots analyst notebooks (merged into main, PR #10) feed ad-hoc wind exposure reports to the same stakeholder group during active cyclone events, using Meteo France RSMC La Réunion track forecasts (`meteofr` blob container).
