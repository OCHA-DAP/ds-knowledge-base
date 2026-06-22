---
content_type: pipeline
name: nga-flood-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "nga-gauge-monitor", ref: ".github/workflows/nga-gauge-monitor.yaml", schedule: "0 14 * * * (daily 14:00 UTC) + workflow_dispatch", status: live }
inputs:
  - "Google Flood Forecasting gauge discharge forecasts (Google Sheets, env GFF_GAUGE_URL)"
  - "HydroBASINS Level 4 basin polygons (Google Drive file ID 1AsB_Cf9QQb3vkp9ebIFvTPZ5gBYqYRJR)"
  - "HDX: West & Central Africa admin0 boundaries (dataset b20cd345-93fb-43bd-9c6e-7bc7d87b63eb)"
  - "HDX: Nigeria Admin 1 boundaries (dataset 81ac1d38-f603-4a98-804d-325c658599a3)"
  - "HDX: Nigeria river network (dataset 741c6f20-6956-420d-aae4-37015cdd1ad4)"
  - "Email recipient list (Google Drive CSV file ID 1A1WPSWBPJKFDBqZb1OXYHipsYxEErR-7)"
  - "Centre banner + OCHA logo PNGs (Google Drive, pulled at runtime)"
outputs:
  - "Daily HTML email report (blastula SMTP to recipient list from Google Drive CSV)"
dependencies:
  - "R 4.x"
  - "blastula (SMTP email rendering)"
  - "googlesheets4 + googledrive (Google API, service account key via GCP_CREDENTIALS secret)"
  - "rhdx (HDX data access)"
  - "gghdx (HDX ggplot2 theme, OCHA-DAP/gghdx)"
  - "tmap (mapping)"
  - "sf (spatial)"
  - "tidyverse suite"
  - "Secrets: GCP_CREDENTIALS, GFF_GAUGE_URL, CHD_DS_EMAIL_USERNAME, CHD_DS_EMAIL_PASSWORD, CHD_DS_HOST, CHD_DS_PORT"
downstream:
  - "Email recipients (humanitarian responders monitoring Nigeria riverine flood risk). No downstream KB pipeline/app/framework consumes this output — the email is the terminal product."
depends_on: []
discrepancies:
  - "[gap] Not in infrastructure/deployments.md → GitHub Actions pipelines table. This scheduled GHA pipeline (cron 0 14 * * *, repo ocha-dap/ds-nga-flood-monitoring) was missed during the systems-ingestion survey. The deployments.md GHA registry is acknowledged-incomplete (grows as repos are ingested); this pipeline should be added there."
  - "[gap] Upstream Google Flood Forecasting (GFF) gauge feed has no KB node — it is an external Google Sheets workbook (env GFF_GAUGE_URL), not a team pipeline/dataset. depends_on left [] because there is no canonical KB id to point at; the GFF dependency is documented in Inputs instead. Promote to an infrastructure/datasets node only if a second page depends on the same feed."
  - "[stale] Standard team infra stack is NOT used: no ocha-stratus / ocha-lens / ocha-relay / Listmonk, and no blob or DB read/write. All inputs are Google Drive/Sheets + HDX (rhdx); output is a stateless SMTP email. Recipient list is a Google Drive CSV (filtered by a `to` boolean column), not Listmonk. Informational — this pilot predates/sits outside the standard stack, not a live error."
  - "[gap] No failure alerting: a failed GHA run sends no external notification. Monitor via the Actions UI."
source_repo: ocha-dap/ds-nga-flood-monitoring
source_branch: main
source_sha: 6ab1dcf
code_ref:
  - "src/gauge_monitoring_email.R"
  - "R/email_funcs.R"
  - "src/email/email_utils.R"
  - "email_flood_monitoring.Rmd"
  - ".github/workflows/nga-gauge-monitor.yaml"
extra:
  pilot_status: "Described in README as 'initial pilot implementation' in collaboration with Google Flood Forecasting Initiative"
  basins_monitored: ["Benue", "Lower Niger", "Niger Delta", "Upper Niger"]
  gauge_count: 55
  gauges_excluded: 5
  alert_threshold: ">=80% of gauges within a basin exceed 2-year return period discharge on any forecast day"
visibility: internal
last_synced: "2026-06-22"
---

# Nigeria Flood Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Daily: pull Google Flood Forecasting gauge discharge data from Google Sheets → assess 4 HydroBASINS Level 4 basins in Nigeria against 2-year return-period thresholds → render and email an HTML flood-status report via SMTP.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| nga-gauge-monitor | `.github/workflows/nga-gauge-monitor.yaml` | daily 14:00 UTC (`0 14 * * *`); also `workflow_dispatch` (manual) | live |

GitHub Actions only — no Databricks job, no Azure web app. The single internal job (`monitor`) runs on `main`. **Not yet listed in `infrastructure/deployments.md`** — see `discrepancies` (registry is acknowledged-incomplete).

## Inputs

- **Google Flood Forecasting gauge data** — a Google Sheets workbook (URL from env `GFF_GAUGE_URL`). Contains one sheet per gauge (`hybas_*` sheets) plus a `metadata` sheet with gauge coordinates and 2-year / 5-year / 20-year return period values. Read via `googlesheets4`.
- **HydroBASINS Level 4 basin polygons** — an `.rds` file on Google Drive (file ID `1AsB_Cf9QQb3vkp9ebIFvTPZ5gBYqYRJR`). Filtered to 4 named basins: Benue (`hybas_id=1040909900`), Lower Niger (`1040909890`), Niger Delta (`1040022420`), Upper Niger (`1040760290`).
- **HDX spatial layers** (loaded via `rhdx`):
  - West & Central Africa admin0 boundaries (HDX dataset `b20cd345`)
  - Nigeria Admin 1 boundaries (HDX dataset `81ac1d38`)
  - Nigeria river network / DCW ESRI (HDX dataset `741c6f20`)
- **Email recipient list** — a CSV on Google Drive (file ID `1A1WPSWBPJKFDBqZb1OXYHipsYxEErR-7`). Rows with `to == TRUE` receive the email.
- **Branding assets** (banner, logo) pulled from Google Drive at runtime.

5 gauges are hardcoded as excluded (`GAUGES_TO_REMOVE`), presumably unreliable historical gauges.

## Steps

1. **Authenticate** Google APIs using a service account JSON (written from the `GCP_CREDENTIALS` GHA secret).
2. **Load static spatial layers** from HDX (West Africa boundaries, Nigeria admin1, rivers) and basin polygons from Google Drive.
3. **Read live gauge data** from Google Sheets: metadata sheet (gauge locations + return-period thresholds) and per-gauge forecast sheets.
4. **Join gauges to basins** via spatial join of gauge points to basin polygons.
5. **Compute alert status**: for each gauge and forecast day, flag whether discharge exceeds the 2-year return period. Accumulate breach percentage per basin over the forecast window. A basin reaches **Warning** status when ≥80% of its gauges are predicted to breach threshold on any day.
6. **Generate visualizations**: a `tmap` choropleth map of basin warning status with gauge point overlay, and a `ggplot2` time-series of average discharge (as % of 2-year RP) by basin.
7. **Render email** from `email_flood_monitoring.Rmd` using `blastula::render_email()`, which embeds both plots as inline images.
8. **Send email** via SMTP (`blastula::smtp_send`) from `data.science@humdata.org` to recipient list. Subject line includes date and warning status.

See `src/gauge_monitoring_email.R` for the full orchestration; `R/email_funcs.R` for basin filtering, gauge-data reading, and alert aggregation logic; `src/email/email_utils.R` for Outlook-compatible inline-image HTML helpers.

## Outputs

- **Daily HTML email** sent to a managed recipient list. Subject: `"Nigeria Riverine Flood Monitoring: {date}"`. Body: map + discharge plot + plain-language warning/no-warning status.
- No blob writes, no DB writes, no dashboards. This pipeline is entirely stateless — it reads, computes, and emails, without persisting anything.

## Dependencies

**R packages:**
- `googlesheets4`, `googledrive` — Google Sheets/Drive API access
- `blastula` — email rendering (R Markdown → HTML) and SMTP dispatch
- `rhdx` — HDX dataset API (installed from GitHub: `dickoa/rhdx`)
- `gghdx` — HDX ggplot2 theme (installed from GitHub: `OCHA-DAP/gghdx`)
- `tmap` (v3-style API — note: a v4 install is commented out)
- `sf` — spatial operations
- `tidyverse`, `lubridate`, `janitor`, `ggtext`, `glue`, `here`, `showtext`

**Secrets (GHA):**
- `GCP_CREDENTIALS` — Google service account JSON (written to `auth.json` at runtime)
- `GFF_GAUGE_URL` — Google Sheets URL for gauge forecast data
- `CHD_DS_EMAIL_USERNAME`, `CHD_DS_EMAIL_PASSWORD` — SMTP credentials
- `CHD_DS_HOST`, `CHD_DS_PORT` — SMTP server config

**Not used:** `ocha-stratus`, `ocha-lens`, `ocha-relay`, Listmonk. This pipeline predates or operates outside the standard team infrastructure stack.

## Failure modes & debugging

**Logs:** GitHub Actions run log under `ocha-dap/ds-nga-flood-monitoring` → Actions → `nga-gauge-monitor`.

**Common failure scenarios:**
- **Google auth failure** (`GCP_CREDENTIALS` secret expired or rotated): the `drive_auth`/`gs4_auth` calls at the top of `gauge_monitoring_email.R` will fail. Check the secret is a valid service account JSON and has access to the relevant Sheets/Drive files.
- **Google Sheets data missing or malformed**: `read_gauge_googlesheets()` iterates all non-`Sheet1` sheets; if Google's Flood Hub stops writing to the workbook, the forecast data will be empty/stale. No explicit freshness check — downstream computations may silently produce a misleading "no warning" result.
- **HDX layer unavailable**: `rhdx` calls may fail if HDX is down or dataset IDs change. No retry logic. R will throw on `get_resource()` / `read_resource()`.
- **SMTP failure**: `smtp_send()` fails if SMTP credentials are wrong or the mail server is down. There is no retry or fallback — the GHA run will fail.
- **tmap v3/v4 API mismatch**: a `tmap@v4` install is commented out; the code uses v3-style API (`tm_polygons(col=...)`, `tm_borders()`). Installing v4 would break the map step.
- **R package cache miss**: the GHA workflow caches `$R_LIBS_USER` keyed on `.github/depends.R`. If that file changes or the cache is evicted, a full reinstall (including GitHub-sourced `rhdx`/`gghdx`) may hit rate limits or fail silently.
- **Recipient CSV empty or all `to == FALSE`**: `smtp_send()` would send to an empty `to` vector; behavior depends on blastula — likely an error or silent no-op.

**No alerting on failure** — the pipeline has no external notification if the GHA run itself fails. Monitor via GitHub Actions UI or set up GHA failure notifications.

## Downstream consumers

This pipeline's output is an **email to humanitarian responders** monitoring riverine flood risk in Nigeria (Niger and Benue river basins). There is no downstream application, dashboard, or DB table that depends on it — the email is the terminal product.

The pilot is described as a collaboration between OCHA CHD and the Google Flood Forecasting Initiative. See the [slide deck](https://docs.google.com/presentation/d/1rB8aOX8XntChfCqIH0wm7Xwf-JXfpQz68sNGk-RifVw/edit) referenced in the README for more context.
