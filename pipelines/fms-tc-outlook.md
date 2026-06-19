---
content_type: pipeline
name: fms-tc-outlook
type: alert
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Send FMS Outlook update email", ref: ".github/workflows/run_update_fms_outlook.yml", schedule: "0 5 * * * (daily 05:00 UTC)", status: live }
    - { name: "Keep Repo Awake", ref: ".github/workflows/keep_awake.yml (on keep-awake branch only)", schedule: "0 12 * * 1 (Monday 12:00 UTC)", status: paused }
inputs:
  - "FMS website: https://www.met.gov.fj/fiji-weather/5-day-tc-outlook/ (scrape PDF URL)"
  - "FMS 5-day TC Outlook PDF (downloaded from FMS site on each run)"
outputs:
  - "Listmonk campaign email to list ID 9 (FMS TC Outlook subscriber list)"
dependencies:
  - "beautifulsoup4 (HTML scraping)"
  - "pdfplumber (PDF text extraction)"
  - "pandas"
  - "requests"
  - "Listmonk instance: listmonk-demo-afhcg8e2hde0fxca.eastus2-01.azurewebsites.net"
  - "Listmonk list ID 9 (main FMS TC Outlook list)"
  - "Listmonk list ID 5 (test/Tristan-only list)"
  - "Listmonk campaign template ID 8"
  - "GHA secrets: DSCI_LISTMONK_API_KEY, DSCI_LISTMONK_API_USERNAME"
downstream:
  - "FMS TC Outlook email subscribers (external; Listmonk list ID 9)"
  - "fji-storms-app (related Fiji storms surface — shared TC context only, not a direct consumer of this email)"
depends_on:
  - "listmonk"
source_repo: ocha-dap/ds-fms-tc-outlook
source_branch: setup-email
source_sha: cae5228
code_ref:
  - "pipelines/update_fms_outlook.py"
  - "src/datasources/fms_outlook.py"
  - "src/email/listmonk.py"
  - ".github/workflows/run_update_fms_outlook.yml"
extra:
  active_code_branch: setup-email
  default_branch: main
  deployed_branch_vs_code_branch: "[conflict] The scheduled run fires from `run_update_fms_outlook.yml` on the DEFAULT branch `main` (GHA only schedules workflows present on the default branch). That workflow hardcodes `ref: setup-email` for checkout, so the run executes pipeline code from `setup-email` even though the workflow file driving the schedule lives on `main`. The same workflow file also exists on `setup-email`, `keep-awake`, and `add-yml` branches, but only the copy on `main` is what GHA schedules."
  keep_awake_not_firing: "[conflict] `keep_awake.yml` exists ONLY on the `keep-awake` branch, which is NOT the default branch. GitHub Actions only evaluates `schedule:` crons on workflows present on the default branch, so the Monday keep-alive cron does NOT actually fire as configured. The keep-awake guard is therefore not operative; the repo relies on the `setup-email`-checkout daily job (scheduled from main) to stay active."
  listmonk_instance: "Uses the listmonk-demo Azure web app (same instance as ds-storms-alerts)"
  keep_awake_branch: "keep-awake branch exists to accept Monday keep-alive empty commits, intended to prevent GHA from disabling scheduled workflows on inactive repos — but see keep_awake_not_firing"
  not_in_deployments_md: "[gap] This repo is not listed in infrastructure/deployments.md GHA pipelines table; should be added during the next deployments refresh"
visibility: internal
last_synced: "2026-06-17"
---

# FMS TC Outlook

> Runbook. Daily: scrape FMS website for the current 5-day TC outlook PDF, parse it, and email a formatted HTML summary to subscribers via Listmonk.

## One-liner

Daily: fetch Fiji Meteorological Services (FMS) 5-day TC outlook PDF → extract per-day risk text → compose HTML email → send via Listmonk campaign to list ID 9.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Send FMS Outlook update email | `.github/workflows/run_update_fms_outlook.yml` (scheduled from default branch `main`; checks out `ref: setup-email`) | `0 5 * * *` (daily 05:00 UTC) | live |
| Keep Repo Awake | `.github/workflows/keep_awake.yml` (on `keep-awake` branch only) | `0 12 * * 1` (Monday 12:00 UTC) | paused (not firing) |

The keep-awake job is *intended* to push an empty commit to the `keep-awake` branch each Monday to prevent GitHub from disabling scheduled workflows on repos with no recent pushes. **But `keep_awake.yml` lives only on the `keep-awake` branch, not the default branch `main` — GitHub Actions only schedules crons from workflows on the default branch, so this job does not actually fire.** See `extra.keep_awake_not_firing`.

The daily email job runs because `run_update_fms_outlook.yml` IS present on the default branch `main`; that workflow then checks out `ref: setup-email` so the run executes the pipeline code from the `setup-email` branch (where the active code lives, SHA `cae5228`).

Not currently listed in [infrastructure/deployments.md](../infrastructure/deployments.md) GHA pipelines table — a tracking gap to close on next refresh.

## Inputs

- **FMS 5-day TC Outlook page** — `https://www.met.gov.fj/fiji-weather/5-day-tc-outlook/` scraped via BeautifulSoup to find the "Preview PDF" link.
- **FMS TC Outlook PDF** — downloaded fresh on each run from the URL found above.

No blob storage or database reads. All inputs are live scrapes of the FMS website.

## Steps

1. `get_tc_outlook_pdf_url()` — GET the FMS outlook page, parse HTML, find `<a href="*.pdf">` with text "Preview PDF", return absolute URL. Falls back to any `<a>` with "Preview PDF" text. Raises `RuntimeError` if not found.
2. `download_pdf_bytes()` — Download the PDF (60s timeout).
3. `extract_date_sections_from_pdf()` — Parse PDF pages with `pdfplumber`. Each section begins with a weekday + ordinal date line (e.g. "Monday 2nd"). Text under each date is joined into one block. Returns a DataFrame with columns `date`, `text`.
4. `df_to_simple_html()` — Render the DataFrame as HTML `<p>` blocks with bold date headers.
5. `create_campaign()` — POST to Listmonk API: create a regular campaign targeting list ID 9, HTML content type, template ID 8.
6. `send_campaign()` — PUT campaign status to "running" to dispatch it.

See `pipelines/update_fms_outlook.py` and `src/datasources/fms_outlook.py` for the full code.

## Outputs

- **Listmonk email campaign** — sent to list ID 9 (FMS TC Outlook subscriber list). Subject: `"FMS TC Outlook issued YYYY-MM-DD"`. Body: plain HTML intro + indented per-day risk blocks + sign-off. Includes a link to the specific PDF and to the FMS website.
- No blob writes, no DB writes.

## Dependencies

| dependency | detail |
|---|---|
| Listmonk | `listmonk-demo-afhcg8e2hde0fxca.eastus2-01.azurewebsites.net` (Azure web app, same instance as ds-storms-alerts) |
| Listmonk list ID 9 | Main FMS TC Outlook recipient list |
| Listmonk list ID 5 | Test list (Tristan-only); referenced in `src/email/listmonk.py` but not used by the live script |
| Listmonk template ID 8 | Campaign template |
| `DSCI_LISTMONK_API_USERNAME` | GHA var (`vars.`) |
| `DSCI_LISTMONK_API_KEY` | GHA secret (`secrets.`) |
| beautifulsoup4 | FMS page scraping |
| pdfplumber | PDF text extraction |
| pandas, requests | Data handling, HTTP |

**No ocha-stratus, ocha-lens, or ocha-relay.** Direct `requests` calls to Listmonk API.

## Failure modes & debugging

**FMS website structure change** — most likely break point. `get_tc_outlook_pdf_url()` raises `RuntimeError("Could not find 'Preview PDF' link on the page.")`. Check if FMS changed their page layout; update the CSS selector in `src/datasources/fms_outlook.py`.

**PDF parsing returns empty DataFrame** — `extract_date_sections_from_pdf()` finds no date-like lines (weekday + ordinal). The PDF format may have changed. Check the raw PDF at the FMS URL manually; update `WEEKDAY_RE` / `ORDINAL_RE` regexes if needed.

**Listmonk auth failure (401/403)** — check that GHA secrets `DSCI_LISTMONK_API_KEY` and `DSCI_LISTMONK_API_USERNAME` are set and match the listmonk-demo instance credentials. The Listmonk instance must be running (check Azure web app state).

**GHA workflow disabled** — GitHub disables scheduled workflows on repos with no recent activity. The keep-awake workflow was *meant* to guard against this with a Monday empty commit, but it sits only on the `keep-awake` branch (not the default `main`), so its cron never fires and provides no protection. If the daily job stops running, check the repo's Actions settings and whether the schedule was auto-disabled; a manual `workflow_dispatch` or any push to `main` re-activates it.

**Branch mismatch** — the daily run is scheduled by `run_update_fms_outlook.yml` on the **default branch `main`** (that's the copy GHA actually schedules). That workflow checks out `ref: setup-email`, so the run uses pipeline code from `setup-email` (active branch, SHA `cae5228`) — *not* `main`. Copies of the same workflow also exist on `setup-email` and `add-yml`, but they don't drive the schedule. Consequence: code changes must land on `setup-email` to take effect, and any schedule/workflow edit must land on `main` to take effect. This split (scheduled-from-`main`, code-from-`setup-email`) is the most confusing operational trap here.

**Logs** — GitHub Actions run history for the `ocha-dap/ds-fms-tc-outlook` repo, "Send FMS Outlook update email" workflow.

## Downstream consumers

Email subscribers on Listmonk list ID 9 (external humanitarian stakeholders monitoring Fiji TC activity). No internal pipeline reads the output. Related deployed app: [`chd-pa-aa-fji-storms-app`](../apps/pa-aa-fji-storms-app.md) (Fiji storms dashboard — shares the Fiji TC context but consumes different data).
