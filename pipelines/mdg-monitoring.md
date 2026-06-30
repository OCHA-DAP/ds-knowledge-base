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
  - "DB table: public.imerg (IMERG v7 daily raster stats per ADM1 pcode, prod)"
  - "DB table: public.polygon (MDG ADM1 pcodes and names, prod)"
outputs:
  - "Email: daily informational email (French) via Listmonk campaign (list 109 prod / 103 test)"
dependencies:
  - "ocha-relay @ v0.2.0 (ListmonkClient — campaign create/send)"
  - ocha-stratus==0.1.7
  - pandas==2.2.3
  - sqlalchemy==2.0.36
  - psycopg2-binary==2.9.10
  - matplotlib==3.10.0
  - scipy==1.17.0
  - azure-storage-blob==12.22.0
  - python-dotenv==1.2.2
  - "Listmonk (DSCI_LISTMONK_BASE_URL / API_USERNAME / API_KEY) — list 109 (prod), 103 (test)"
  - "Azure DB PROD credentials (DSCI_AZ_DB_PROD_HOST / UID / PW)"
  - "GHA workflow_dispatch input `test` (boolean) → --test flag → test list + [test] subject prefix"
downstream:
  - "frameworks/mdg-storms — Madagascar cyclone AA framework (this is its rainfall observational-monitoring email; recipients are the framework's ops team / partners)"
depends_on: [imerg, listmonk]
source_repo: ocha-dap/ds-aa-mdg-monitoring
source_branch: main
source_sha: b0ed64b
code_ref:
  - pipelines/monitor_imerg.py
  - .github/workflows/run_monitor_imerg.yml
  - src/constants.py
  - src/datasources/imerg.py
  - src/datasources/polygon.py
  - src/monitoring/emails.py
  - src/monitoring/plotting.py
  - src/utils/db_utils.py
extra:
  comms_channel: "Listmonk via ocha-relay ListmonkClient.from_env() (create_campaign + send_campaign skip_confirmation). Migrated FROM AWS SES + blob-CSV distribution list (see discrepancies)."
  listmonk_lists: "LISTMONK_LIST_ID = 109 (prod), LISTMONK_LIST_ID_TEST = 103 (src/constants.py)."
  email_language: French
  trigger_threshold: "RAIN_THRESH = 300 mm (src/constants.py): per-region 3-day sum of region-averaged precip, max across ADM1 regions. Code fires on strictly > 300 mm; README says >= 300 (see discrepancies)."
  test_toggle: "Now the --test CLI flag (workflow_dispatch boolean `test`), NOT the old TEST_LIST repo variable. Default (no flag) sends to the REAL list 109."
  email_body: "Email HTML is built inline as an f-string in src/monitoring/emails.py (_build_body); chart embedded as base64 PNG. The email_assets/templates/*.html (Jinja2) and email_assets/static/ are legacy and NOT used by the current code path."
  blob_unused_in_pipeline: "src/utils/blob_utils.py (raw azure-storage-blob SDK) is still present but NOT used by the scheduled pipeline — the distribution list is no longer a blob CSV. DSCI_AZ_BLOB_DEV_SAS_WRITE is still passed in the workflow env but unused by the email path."
  analyst_tooling: "notebooks/wind_exposure.ipynb + bubbles_template.ipynb and src/datasources/meteofr.py + src/utils/exposure.py + the plotting.py bullseye/bubble/wind-buffer plotters are manual analyst tools for cyclone events (Meteo France RSMC La Réunion tracks → wind exposure plots). NOT part of the scheduled Monitor IMERG job."
  discrepancies:
    - "[change] Comms channel migrated: previous ingestion (2026-06-22) recorded AWS SES (DSCI_AWS_EMAIL_*) + a blob-CSV distribution list (distribution_list.csv) toggled by the TEST_LIST repo var. Current code sends via Listmonk (ocha-relay, lists 109/103) and toggles with the --test flag. SES secrets and the blob CSV are no longer used."
    - "[conflict] Threshold operator: code uses strict greater-than (`df_grouped['mean'].max() > RAIN_THRESH`, src/monitoring/emails.py) so the trigger fires above 300 mm, but README states '>= 300 mm in any region'. Exactly 300.0 mm would NOT activate per the code."
    - "[stale] email_assets/ Jinja2 templates + static banner/logo are legacy; the current email body is inline HTML in emails.py. jinja2/html2text are no longer in requirements."
    - "[health] pipeline-registry.md flags this job 🔴 DOWN / OVERDUE(>48h) — silently stalled for weeks–months per deployments.md (2026-06-22 snapshot). Re-verify it is actually firing on schedule."
  deployment_registry: "deployments.md → GitHub Actions pipelines. GHA-only — not a Databricks job or Azure web app."
visibility: internal
last_synced: "2026-06-30"
---

# MDG Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Daily at 16:00 UTC: pull IMERG ADM1 raster stats for Madagascar → check the 3-day rainfall total against the 300 mm threshold → send a French-language informational email with a bar chart to the distribution list via a **Listmonk** campaign.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Monitor IMERG | `.github/workflows/run_monitor_imerg.yml` | `0 16 * * *` (daily 16:00 UTC) | live |

The workflow also has a `workflow_dispatch` trigger with two optional inputs: `date` (YYYY-MM-DD, the center date — for backfill/manual runs) and `test` (boolean → `--test`). The script is invoked as `python pipelines/monitor_imerg.py [--date YYYY-MM-DD] [--test]`. A separate `keep-alive` job pings on every run to stop GHA disabling the schedule. README: "To run on GH actions, use the main branch."

## Inputs

- **`public.imerg`** (prod DB): daily IMERG v7 raster stats per MDG ADM1 pcode, queried for the 3-day window (`src/datasources/imerg.py`).
- **`public.polygon`** (prod DB): ADM1 polygon metadata (pcode, name) for MDG, filtered `iso3='MDG'` and `adm_level=1` (`src/datasources/polygon.py`).

Default center `date` = `today − 2 days` (T-2), ensuring raster stats exist (stats run ~15:00 UTC; email at 16:00). There is **no backfilling** of missed past dates on the schedule.

The recipient list is **no longer a blob CSV** — it is the Listmonk list (see Outputs/Dependencies).

## Steps

1. **Parse args** (`pipelines/monitor_imerg.py`): determine `run_date` (default T-2) and compute `dates` = 3-day window ending at `run_date + 1 day`.
2. **Fetch polygon data**: query `public.polygon` for MDG ADM1 pcodes.
3. **Fetch IMERG data**: query `public.imerg` for those pcodes over the 3-day range.
4. **Validate**: raise `ValueError` if any of the 3 dates is missing from the result.
5. **Plot** (`src/monitoring/plotting.py → plot_rainfall`): stacked bar chart of 3-day precipitation per ADM1 region, crimson dashed threshold line at 300 mm, totals labelled above bars.
6. **Send email** (`src/monitoring/emails.py → send_info_email`): group by pcode and sum the 3 days; `obsv_trigger` = "ACTIVÉ" if `df_grouped["mean"].max() > RAIN_THRESH` else "PAS ACTIVÉ" (strict greater-than). Build inline HTML body (base64-embedded chart) and create + send a **Listmonk campaign** via `ListmonkClient.from_env()` (`create_campaign` then `send_campaign(skip_confirmation=True)`). Returns the campaign ID.

## Outputs

- **Email / Listmonk campaign**: French-language informational email, subject `"[test ]Action anticipatoire Madagascar – précipitations autour de {middle_date}"`, campaign name `mdg-cyclone-rainfall-{middle_date}-{EAT timestamp}`, sent to list **109** (prod) or **103** (test, with `[test]` prefix). Body embeds the 3-day rainfall bar chart and the trigger status.
- **No DB writes, no blob writes** from the scheduled pipeline.

## Dependencies

| dependency | detail |
|---|---|
| Listmonk (`ocha-relay` v0.2.0) | `ListmonkClient.from_env()` reads `DSCI_LISTMONK_BASE_URL` / `DSCI_LISTMONK_API_USERNAME` / `DSCI_LISTMONK_API_KEY`. Lists `109` (prod) / `103` (test) in `src/constants.py`. |
| Azure DB PROD | `DSCI_AZ_DB_PROD_HOST/UID/PW` — `public.imerg` and `public.polygon`. SQLAlchemy + psycopg2 (`src/utils/db_utils.py`). |
| `--test` flag | workflow_dispatch boolean `test` → test list `103` + `[test]` subject prefix. Default (no flag) sends to the **real** list `109`. |
| matplotlib / pandas | chart rendering and data shaping. |
| ocha-stratus 0.1.7, scipy, azure-storage-blob | installed; used by analyst notebooks / legacy helpers, not the scheduled email path. |

## Failure modes & debugging

- **Missing IMERG dates**: script raises `ValueError` with the missing dates. Root cause: the upstream IMERG pipeline ([pipelines/imerg](imerg.md)) ran late or failed. Check that job's logs first.
- **Job silently stalled**: `pipeline-registry.md` flags this workflow 🔴 **DOWN / OVERDUE(>48h)** — per the 2026-06-22 `deployments.md` snapshot it had been stalled for weeks–months without surfacing in `pipelines-status`. **First check: is the schedule actually firing?** Re-enable via `workflow_dispatch` and confirm GHA hasn't disabled it (the `keep-alive` job is meant to prevent this).
- **DB connection / SSL failure**: `db_utils.get_engine` builds a raw `postgresql+psycopg2://…/postgres` URL and does **not** set `sslmode`. Azure PostgreSQL needs `PGSSLMODE=require` — set it as a GHA env var if you see SSL handshake errors.
- **Listmonk send failure**: bad/missing `DSCI_LISTMONK_*` secrets, unreachable base URL, or wrong list id. The campaign is created then sent with `skip_confirmation=True`; a failure at either step aborts the run. Check the campaign in the Listmonk UI.
- **Accidental real-list send**: the safety toggle is now the `--test` flag, **not** an env var — omitting it sends to the real list `109`. Double-check the `test` input on manual `workflow_dispatch` runs.
- **Logs**: GHA Actions tab on `ocha-dap/ds-aa-mdg-monitoring`, workflow "Monitor IMERG".

## Downstream consumers

- **Madagascar cyclone AA framework operations** ([frameworks/mdg-storms](../frameworks/mdg-storms/README.md)): the Listmonk list recipients (humanitarian partners, national authorities). This is the framework's rainfall observational-monitoring channel — a terminal notification step; no downstream pipeline consumes it.
- The analyst exposure notebooks (`notebooks/wind_exposure.ipynb`, `bubbles_template.ipynb`) feed ad-hoc wind-exposure reports to the same stakeholders during active cyclone events, using Meteo France RSMC La Réunion track forecasts (`src/datasources/meteofr.py`). These are manual, not part of the scheduled job.
