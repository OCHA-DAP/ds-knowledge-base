---
content_type: pipeline
name: acled-conflict-index
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Weekly ACLED conflict index scrape", ref: ".github/workflows/main.yml", schedule: "0 9 * * 1 (Monday 09:00 UTC) + workflow_dispatch", status: live }
inputs:
  - "ACLED OAuth2 token endpoint (https://acleddata.com/oauth/token)"
  - "ACLED weekly conflict index results page (https://acleddata.com/results/weekly-conflict-index-results)"
  - "Parses .xlsx download link from results page HTML"
outputs:
  - "blob: projects/ds-acled-conflict-index/raw/acled/<filename>.xlsx (DEV stage only; container is stratus default 'projects')"
dependencies:
  - ocha-stratus
  - requests
  - beautifulsoup4
  - "Secret: ACLED_USERNAME (ACLED OAuth account email) — repo-level, NOT an org secret"
  - "Secret: ACLED_PASSWORD (ACLED OAuth account password) — repo-level, NOT an org secret"
  - "Secret: DSCI_AZ_BLOB_DEV_SAS_WRITE (Azure blob write SAS token) — inherited from OCHA-DAP org"
downstream: []
depends_on: []
discrepancies:
  - "[gap] Not yet listed in infrastructure/deployments.md GHA pipelines table — registry has no row for this repo. Deployment block here is the only home for the runtime fact until the registry is updated."
  - "[gap] Writes to DEV blob only (stage='dev'); no prod write path coded. No downstream consumer exists yet — raw .xlsx is not transformed into any DB table or further stage."
  - "[gap] Fallback file selection: _find_xlsx_url falls back to ANY .xlsx link if the 'weekly_index_scores*.xlsx' pattern is absent, so a page restructure could silently fetch the wrong file."
source_repo: ocha-dap/ds-acled-conflict-index
source_branch: main
source_sha: ce16d73
code_ref:
  - pipelines/run_scrape.py
  - src/scraper.py
  - src/constants.py
  - .github/workflows/main.yml
extra:
  dev_slot_note: "run_scrape.py uses stratus.get_container_client(stage='dev', write=True) — output goes to DEV blob only; no prod write path exists yet. Intentional for the initial scraper; confirm target stage before treating as production-grade. See Discrepancies."
  schedule_note: "Cron fires Mondays 09:00 UTC from main. Until 2026-07-28 the repo default branch was feat/initial-scraper and the cron fired from there; main was empty. The branch was merged (PR #1) and the default switched to main on 2026-07-28."
  auth_note: "ACLED uses OAuth2 password grant (grant_type=password, client_id=acled). The same bearer token also authenticates the Drupal results page — verified working 2026-07-28, despite the page being role-gated (anonymous requests get 'access denied')."
  outage_note: "Every run from repo creation (2026-06-01) to 2026-07-27 failed with 400 at the token endpoint: ACLED_USERNAME/ACLED_PASSWORD were never set on the repo, os.getenv returned None, and requests silently drops None values from a form body — so ACLED received a password grant with no credentials. Secrets set 2026-07-28; first green run 30344264974."
visibility: internal
last_synced: "2026-07-28"
---

# ACLED Conflict Index

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Weekly (Monday 09:00 UTC): authenticate with ACLED → scrape weekly conflict index results page → parse .xlsx link → upload to Azure blob (dev stage).*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Weekly ACLED conflict index scrape | `.github/workflows/main.yml` | `0 9 * * 1` (Monday 09:00 UTC) | live |

The workflow also supports `workflow_dispatch` for manual runs. Not yet in `infrastructure/deployments.md`.

**Branch history (corrected 2026-07-28).** An earlier version of this page said the cron was inert because `main` was empty and the workflow lived only on `feat/initial-scraper`. That was wrong: `feat/initial-scraper` *was* the repo's default branch, so the cron did fire from it every Monday — and failed every time (see Failure modes). On 2026-07-28 the branch was merged to `main` via PR #1 and the default branch was switched to `main`, which is now the branch the cron runs from.

## Inputs

- **ACLED API / web scrape:** authenticates via OAuth2 password flow against `https://acleddata.com/oauth/token` with `ACLED_USERNAME` / `ACLED_PASSWORD` secrets, then fetches `https://acleddata.com/results/weekly-conflict-index-results` and parses the page for a `.xlsx` download link (preferring filenames matching `weekly_index_scores*.xlsx`).

## Steps

1. `get_token()` — POST to ACLED OAuth token endpoint with username/password; returns bearer token.
2. GET the results page with the bearer token; `BeautifulSoup` parses HTML to find the `.xlsx` URL (primary: `weekly_index_scores*.xlsx` pattern; fallback: any `.xlsx` link).
3. Download the `.xlsx` file to a `tempfile.TemporaryDirectory`.
4. Upload to Azure blob via `stratus.get_container_client(stage="dev", write=True)` at path `ds-acled-conflict-index/raw/acled/<filename>.xlsx`.

See `src/scraper.py` and `pipelines/run_scrape.py` for full detail.

## Outputs

- **Blob (dev):** `projects/ds-acled-conflict-index/raw/acled/<filename>.xlsx`
  - `projects` is the `ocha-stratus` default container; the code passes only the path below it.
  - Filename comes directly from the ACLED download URL (observed: `weekly_index_scores_2026-07-22.xlsx`).
  - Written to the **dev** storage account only (`imb0chd0dev`) — no prod write path is currently coded.

## Dependencies

| dependency | role |
|---|---|
| `ocha-stratus` | blob storage client (`get_container_client`) |
| `requests` | HTTP calls to ACLED OAuth + download |
| `beautifulsoup4` | HTML parse of the results page to find .xlsx link |
| `ACLED_USERNAME` / `ACLED_PASSWORD` | ACLED OAuth2 credentials — **repo-level secrets, not org-level** |
| `DSCI_AZ_BLOB_DEV_SAS_WRITE` | SAS token for dev blob write access — inherited from the `OCHA-DAP` org |

`ACLED_USERNAME` / `ACLED_PASSWORD` are **not** among the `OCHA-DAP` org secrets, so every repo needing ACLED sets its own copy — `ds-acled-fetcher` keeps a separate pair of the same credentials. A new ACLED repo that assumes it inherits them from the org will fail exactly as this one did.

## Failure modes & debugging

- **`400 Bad Request` at the token endpoint — check the secrets first.** This took out every run from 2026-06-01 to 2026-07-27. If `ACLED_USERNAME` / `ACLED_PASSWORD` are unset, `os.getenv` returns `None` and `requests` **silently drops `None` values from a form body** — ACLED then receives a password grant with no credentials and returns a bare `400`, which reads like rejected credentials rather than absent ones. Confirm with `gh secret list -R <repo>`; note that org-inherited secrets need `gh api repos/<owner>/<repo>/actions/organization-secrets`. Since `675fdb1` the scraper fails fast naming the missing variables and logs ACLED's response body, so this should now be self-diagnosing.
- **`400` with `{"error":"invalid_grant"}`:** credentials are present but wrong/expired — the response body is now logged and distinguishes this from the case above.
- **Results page `401`/`403`:** the page is role-gated Drupal content (anonymous requests get "content not available at your access level"). The API bearer token does authenticate it today, but if ACLED decouples website auth from API auth, this step will need a session cookie or the account will need an entitlement on the weekly conflict index.
- **No .xlsx found on page (`RuntimeError: No .xlsx download link found`):** ACLED restructured the results page. Check `src/scraper.py` `_find_xlsx_url`.
- **Wrong file downloaded:** Fallback logic picks any `.xlsx` on the page. If ACLED adds other Excel links, the fallback could grab the wrong file. Prefer the primary regex `weekly_index_scores.*\.xlsx?`.
- **Blob write failure:** Check `DSCI_AZ_BLOB_DEV_SAS_WRITE`. Note: writes go to the **dev** blob — do not expect files in prod. `ocha-stratus` hardcodes the storage host, so there is no endpoint variable to misconfigure (an unused `DSCI_AZ_ENDPOINT` was removed from the workflow on 2026-07-28).
- **Logs:** GitHub Actions run logs in the repo's Actions tab. No Databricks involvement.

## Downstream consumers

No downstream consumers identified in the codebase as of source_sha `ce16d73`. Downstream processing (transforming the raw Excel into DB tables or further pipeline stages) has not yet been built.

## Discrepancies

- **[gap] Not in the deployment registry.** No row in `infrastructure/deployments.md` GitHub Actions table for this repo. Add one now that the cron is live.
- **[gap] Dev blob only, no downstream.** Output is written to the `dev` storage account (`stage="dev"`); no prod write path is coded and no consumer transforms the raw `.xlsx`. Confirm intended target stage before treating output as production data.
- **[gap] Fallback file selection.** `_find_xlsx_url` falls back to *any* `.xlsx` link if the `weekly_index_scores*.xlsx` pattern is absent — could silently grab the wrong file if ACLED restructures the results page.
- **[gap] No alerting.** The pipeline failed silently every Monday for eight weeks and nothing surfaced it. There is no notification on workflow failure.
