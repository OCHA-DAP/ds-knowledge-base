---
content_type: pipeline
name: acled-conflict-index
type: dataset-ingest
status: in-development
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Weekly ACLED conflict index scrape", ref: ".github/workflows/main.yml", schedule: "0 9 * * 1 (NOT firing — workflow only on feat/initial-scraper, not default branch; effectively manual workflow_dispatch only)", status: paused }
inputs:
  - "ACLED OAuth2 token endpoint (https://acleddata.com/oauth/token)"
  - "ACLED weekly conflict index results page (https://acleddata.com/results/weekly-conflict-index-results)"
  - "Parses .xlsx download link from results page HTML"
outputs:
  - "blob: ds-acled-conflict-index/raw/acled/<filename>.xlsx (DEV stage only)"
dependencies:
  - ocha-stratus
  - requests
  - beautifulsoup4
  - "Secret: ACLED_USERNAME (ACLED OAuth account email)"
  - "Secret: ACLED_PASSWORD (ACLED OAuth account password)"
  - "Secret: DSCI_AZ_BLOB_DEV_SAS_WRITE (Azure blob write SAS token)"
  - "Secret: DSCI_AZ_ENDPOINT (Azure blob endpoint URL)"
downstream: []
depends_on: []
discrepancies:
  - "[conflict] The schedule is NOT actually running. origin/main is empty — the entire pipeline (workflow + scraper) lives ONLY on branch feat/initial-scraper. GitHub Actions `schedule:` cron fires only against the workflow file on the DEFAULT branch (main), so the Monday 09:00 UTC cron will not trigger until this branch is merged. Today it runs only via manual workflow_dispatch from the feature branch. status is dev/in-development, not live."
  - "[gap] Not yet listed in infrastructure/deployments.md GHA pipelines table — registry has no row for this repo (ingested 2026-06-22). Deployment block here is the only home for the runtime fact until the registry is updated."
  - "[gap] Writes to DEV blob only (stage='dev'); no prod write path coded. No downstream consumer exists yet — raw .xlsx is not transformed into any DB table or further stage."
source_repo: ocha-dap/ds-acled-conflict-index
source_branch: feat/initial-scraper
source_sha: a6c4aa8
code_ref:
  - pipelines/run_scrape.py
  - src/scraper.py
  - src/constants.py
  - .github/workflows/main.yml
extra:
  dev_slot_note: "run_scrape.py uses stratus.get_container_client(stage='dev', write=True) — output goes to DEV blob only; no prod write path exists yet. Intentional for the initial scraper; confirm target stage before treating as production-grade. See Discrepancies."
  schedule_note: "GHA schedule cron is inert: origin/main is empty, workflow lives only on feat/initial-scraper. Default-branch-only schedule semantics mean the Monday cron does not fire until merged. Runs only via workflow_dispatch today."
  auth_note: "ACLED uses OAuth2 password grant (grant_type=password, client_id=acled). Falls back to any .xlsx link if the preferred 'weekly_index_scores*.xlsx' pattern is not found — may silently pick up the wrong file if ACLED restructures the page."
visibility: internal
last_synced: "2026-06-22"
---

# ACLED Conflict Index

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Weekly (intended Monday 09:00 UTC): authenticate with ACLED → scrape weekly conflict index results page → parse .xlsx link → upload to Azure blob (dev stage). **In-development:** see Discrepancies — the cron is not actually firing yet.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Weekly ACLED conflict index scrape | `.github/workflows/main.yml` | `0 9 * * 1` (Monday 09:00 UTC) — **not firing** | dev |

The workflow also supports `workflow_dispatch` for manual runs. **The scheduled cron is currently inert:** GitHub Actions only runs `schedule:` triggers from the workflow file on the default branch, and `main` is empty — the workflow lives only on `feat/initial-scraper`. Until that branch is merged to `main`, the pipeline runs only via manual `workflow_dispatch`. Not yet in `infrastructure/deployments.md`.

## Inputs

- **ACLED API / web scrape:** authenticates via OAuth2 password flow against `https://acleddata.com/oauth/token` with `ACLED_USERNAME` / `ACLED_PASSWORD` secrets, then fetches `https://acleddata.com/results/weekly-conflict-index-results` and parses the page for a `.xlsx` download link (preferring filenames matching `weekly_index_scores*.xlsx`).

## Steps

1. `get_token()` — POST to ACLED OAuth token endpoint with username/password; returns bearer token.
2. GET the results page with the bearer token; `BeautifulSoup` parses HTML to find the `.xlsx` URL (primary: `weekly_index_scores*.xlsx` pattern; fallback: any `.xlsx` link).
3. Download the `.xlsx` file to a `tempfile.TemporaryDirectory`.
4. Upload to Azure blob via `stratus.get_container_client(stage="dev", write=True)` at path `ds-acled-conflict-index/raw/acled/<filename>.xlsx`.

See `src/scraper.py` and `pipelines/run_scrape.py` for full detail.

## Outputs

- **Blob (dev):** `ds-acled-conflict-index/raw/acled/<filename>.xlsx`
  - Filename comes directly from the ACLED download URL (e.g. `weekly_index_scores_2024_05_06.xlsx`).
  - Written to the **dev** storage account only — no prod write path is currently coded.

## Dependencies

| dependency | role |
|---|---|
| `ocha-stratus` | blob storage client (`get_container_client`) |
| `requests` | HTTP calls to ACLED OAuth + download |
| `beautifulsoup4` | HTML parse of the results page to find .xlsx link |
| `ACLED_USERNAME` / `ACLED_PASSWORD` | ACLED OAuth2 credentials (GHA secrets) |
| `DSCI_AZ_BLOB_DEV_SAS_WRITE` | SAS token for dev blob write access |
| `DSCI_AZ_ENDPOINT` | Azure blob storage endpoint |

## Failure modes & debugging

- **OAuth failure (`401`/`403`):** ACLED credentials expired or revoked. Check `ACLED_USERNAME` / `ACLED_PASSWORD` in GitHub repo secrets. ACLED password-grant tokens are short-lived; check if the account needs renewal.
- **No .xlsx found on page (`RuntimeError: No .xlsx download link found`):** ACLED restructured the results page (auth gating via cookie rather than bearer, or URL pattern changed). Check `src/scraper.py` `_find_xlsx_url` logic. The code comments note: "The page may require cookie-based auth — check the URL structure."
- **Wrong file downloaded:** Fallback logic picks any `.xlsx` on the page. If ACLED adds other Excel links, the fallback could grab the wrong file. Prefer the primary regex `weekly_index_scores.*\.xlsx?`.
- **Blob write failure:** Check `DSCI_AZ_BLOB_DEV_SAS_WRITE` and `DSCI_AZ_ENDPOINT` secrets. Note: writes go to the **dev** blob — do not expect files in prod.
- **Logs:** GitHub Actions run logs in the repo's Actions tab. No Databricks involvement.

## Downstream consumers

No downstream consumers identified in the codebase as of source_sha `a6c4aa8`. The pipeline is in its initial scraper phase (`feat/initial-scraper` branch) — downstream processing (transforming the raw Excel into DB tables or further pipeline stages) has not yet been built.

## Discrepancies

- **[conflict] The schedule is not actually running.** `origin/main` is empty; the workflow + scraper exist only on `feat/initial-scraper`. GitHub Actions fires `schedule:` crons only from the default branch's workflow file, so the Monday 09:00 UTC cron is inert until this branch is merged to `main`. Today the pipeline runs only via manual `workflow_dispatch`. Status is therefore `dev`, not `live`.
- **[gap] Not in the deployment registry.** No row in `infrastructure/deployments.md` GitHub Actions table for this repo (as of 2026-06-22). Add one when/if the branch merges and the cron goes live.
- **[gap] Dev blob only, no downstream.** Output is written to the `dev` storage account (`stage="dev"`); no prod write path is coded and no consumer transforms the raw `.xlsx`. Confirm intended target stage before treating output as production data.
- **[gap] Fallback file selection.** `_find_xlsx_url` falls back to *any* `.xlsx` link if the `weekly_index_scores*.xlsx` pattern is absent — could silently grab the wrong file if ACLED restructures the results page.
