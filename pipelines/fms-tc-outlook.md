---
content_type: pipeline
name: fms-tc-outlook
type: alert
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Send FMS Outlook update email", ref: ".github/workflows/run_update_fms_outlook.yml", schedule: "0 5 * * * (daily 05:00 UTC; FMS issues at 04:00 UTC; GHA starts ~50-70 min late)", status: live }
    - { name: "Keep Repo Awake", ref: ".github/workflows/keep_awake.yml", schedule: "0 12 * * 1 (Monday 12:00 UTC; empty commit to the keep-awake branch)", status: live }
inputs:
  - "FMS website: https://www.met.gov.fj/fiji-weather/5-day-tc-outlook/ (scrape the 'Preview PDF' link)"
  - "FMS 5-day TC Outlook PDF (downloaded on each run)"
outputs:
  - "Listmonk campaign: list 9 'FMS TC outlook' when TEST_EMAIL=false; test list 5 when TEST_EMAIL=true"
dependencies:
  - "ocha-relay v0.3.0 (Listmonk client)"
  - "beautifulsoup4 (HTML scraping)"
  - "pdfplumber (PDF text extraction)"
  - "pandas"
  - "requests"
  - "Listmonk lists 9 (real) and 5 (test); campaign template 8"
  - "OCHA-DAP org Actions secrets: DSCI_LISTMONK_API_URL, DSCI_LISTMONK_API_USERNAME, DSCI_LISTMONK_API_KEY"
  - "Repo variables TEST_EMAIL, DRY_RUN"
downstream:
  - "FMS TC Outlook email subscribers (Listmonk list 9)"
depends_on: [listmonk]
source_repo: ocha-dap/ds-fms-tc-outlook
source_branch: main
source_sha: 0225f85
code_ref:
  - "pipelines/update_fms_outlook.py"
  - "src/datasources/fms_outlook.py"
  - "src/flags.py"
  - ".github/workflows/run_update_fms_outlook.yml"
extra:
  season: "Runs only in the South Pacific cyclone season (1 Nov - 30 Apr). The send workflow is disabled by hand at the end of the season and enabled again in November."
  revived: "2026-11-05 (PR #5): code moved from the setup-email branch onto main, ocha-relay + org secrets, TEST_EMAIL/DRY_RUN run modes, send-once. Restarted on the test list (5) only; first send 2026-11-05 (campaign 2843), a re-run skipped as already sent."
visibility: internal
last_synced: "2026-11-05"
---

# FMS TC Outlook

> Runbook. Daily in the cyclone season: scrape the Fiji Meteorological Service (RSMC Nadi) 5-day tropical cyclone outlook PDF and email the risk for each day through Listmonk.

## One-liner

Daily at 05:00 UTC: fetch the FMS 5-day TC outlook PDF → extract the cyclone formation risk for each day → HTML email → Listmonk campaign to list 9 (real) or list 5 (test).

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Send FMS Outlook update email | `.github/workflows/run_update_fms_outlook.yml` on `main` | `0 5 * * *` (daily 05:00 UTC) | live |
| Keep Repo Awake | `.github/workflows/keep_awake.yml` on `main` | `0 12 * * 1` (Monday 12:00 UTC) | live |

FMS issues the outlook at 04:00 UTC every day of the South Pacific cyclone season (1 November to 30 April). GitHub usually starts the 05:00 UTC cron 50 to 70 minutes late, so emails go out at about 06:00 UTC.

The send workflow is turned off by hand at the end of the season (Actions → Disable workflow; last season's last send was 2026-05-05) and on again in November. The keep-awake workflow runs from `main` and pushes an empty commit to the `keep-awake` branch each Monday, so GitHub does not disable the scheduled workflow over the off-season.

Until 2026-11 the pipeline code lived on the `setup-email` branch and the workflow on `main` checked that branch out. Since PR #5 everything runs from `main`; `setup-email` is historical.

## Run modes

Team convention: [email-testing](../infrastructure/email-testing.md). Both flags default to `true` in the code and in the workflow; scheduled runs take the repository variables, a manual run takes the dispatch inputs.

| variable | `true` | `false` |
|---|---|---|
| `TEST_EMAIL` | test list 5; campaign name and subject tagged `[TEST]` | real list 9 |
| `DRY_RUN` | print the email, no Listmonk calls | send |

Since the 2026-11-05 restart the repo variables are `TEST_EMAIL=true`, `DRY_RUN=false`: it sends to the test list only. To send to the real list, set the repo variable `TEST_EMAIL=false`.

## Inputs

- **FMS 5-day TC Outlook page**: `https://www.met.gov.fj/fiji-weather/5-day-tc-outlook/`, scraped with BeautifulSoup for the "Preview PDF" link.
- **FMS TC Outlook PDF**, downloaded on each run.

No blob storage or database reads, which is why this stays on GitHub Actions (GitHub runners cannot reach the team databases; this pipeline doesn't need them).

## Steps

1. `get_tc_outlook_pdf_url()`: GET the FMS page, find the `<a>` whose text is "Preview PDF", return its absolute URL. Raises `RuntimeError` if not found.
2. `download_pdf_bytes()` + `pdf_lines()`: download the PDF and read its text lines with `pdfplumber`.
3. `parse_issue_time()`: the outlook's issue time from its `Issue Time: 0400 UTC Thursday 5th November 2026` line (the colon was missing in March 2026). If no such line can be read, the run fails and sends nothing: the issue date keys send-once. An outlook issued more than a day before the run is skipped as stale (e.g. the season's last outlook, still on the site in May).
4. `extract_date_sections()`: each day starts with a line that is only a day heading (`Friday 6th November`); the text under it is one block. The wrapped `till Wednesday 3rd December, 2025:` header line is not a day. If there are no day headings (the season's last outlook, 30 April), the text after the `Issued by:` line is sent as one block; if that is empty too, the run fails rather than sending an empty email.
5. Send-once: the campaign name is `FMS TC Outlook issued <issue date>` (`[TEST] ` prefix in test mode). The run searches Listmonk campaigns for the plain word `Outlook` and skips if a sent campaign with that exact name exists. A re-run, or a run before FMS has posted the day's outlook, sends nothing.
6. `ListmonkClient.create_campaign()` (template 8) + `send_campaign(skip_confirmation=True)` from [ocha-relay](../infrastructure/libs/ocha-relay.md).

## Outputs

- **Listmonk email campaign**: subject = campaign name. The body has an intro with links to that day's PDF and to the FMS page, the risk for each day in italics, and a sign-off.
- No blob writes, no DB writes.

## Dependencies

| dependency | detail |
|---|---|
| Listmonk | the team instance ([comms-listmonk](../infrastructure/comms-listmonk.md)) |
| Listmonk list 9 | "FMS TC outlook", the real recipients (private, untagged) |
| Listmonk list 5 | "Tristan only", the test list |
| Listmonk template 8 | `base_campaign`; a `[test]` campaign name adds the red test banner |
| `DSCI_LISTMONK_API_URL` / `_USERNAME` / `_KEY` | OCHA-DAP org Actions secrets; the workflow maps the URL to `DSCI_LISTMONK_BASE_URL` for ocha-relay |
| `TEST_EMAIL`, `DRY_RUN` | repo variables (see Run modes) |
| ocha-relay v0.3.0, beautifulsoup4, pdfplumber, pandas, requests | `pyproject.toml` / `uv.lock`; the workflow runs `uv sync --locked` with Python 3.11 |

## Failure modes & debugging

**FMS website structure change.** `get_tc_outlook_pdf_url()` raises `RuntimeError("Could not find 'Preview PDF' link on the page.")`. Check the FMS page layout and update the selector in `src/datasources/fms_outlook.py`.

**PDF format change.** No day headings and no `Issued by:` line → `RuntimeError`, no email. The unit tests in `tests/test_fms_outlook.py` hold the line formats seen in the 2025/26 season; the run log prints the parsed table.

**FMS late.** If the 05:00 UTC run finds the previous day's PDF, send-once skips it (that outlook was already sent), so that day gets no email. The run log says `Already sent ... skipping`.

**Listmonk auth failure (401/403).** Check the org secrets. A repo-level secret with the same name overrides the org one; the repo-level `DSCI_LISTMONK_API_KEY` secret and `DSCI_LISTMONK_API_USERNAME` variable from 2025 were deleted at the 2026-11-05 restart, so the repo should have none.

**GHA workflow disabled.** Either turned off at season end (expected) or auto-disabled by GitHub after 60 days without activity (the keep-awake guards against this). Re-enable it under Actions.

**Logs.** GitHub Actions run history for `ocha-dap/ds-fms-tc-outlook`, workflow "Send FMS Outlook update email".

## Downstream consumers

Email subscribers on Listmonk list 9 (humanitarian staff following Fiji and Pacific TC activity). No pipeline reads the output. Related: [fji-storms-monitoring](fji-storms-monitoring.md) (the Fiji AA trigger, fed by FMS forecast emails, not by this outlook).
