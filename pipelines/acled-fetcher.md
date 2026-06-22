---
content_type: pipeline
name: acled-fetcher
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "main.yml / run-script", ref: ".github/workflows/main.yml", schedule: "0 8 * * * (daily 08:00 UTC) + workflow_dispatch (manual)", status: live }
  registry_note: "NOT yet listed in infrastructure/deployments.md GitHub Actions table — registry gap, should be added there."
inputs:
  - "ACLED API (https://acleddata.com/api/acled/read) — all events with event_date > 2026-02-27"
  - "OAuth2 token endpoint (https://acleddata.com/oauth/token)"
  - "blob: projects/acled-conflict/acled_conflict/download_date.parquet (dev stage) — idempotency guard"
outputs:
  - "blob: projects/acled-conflict/raw.csv — full ACLED event records from API"
  - "blob: projects/acled-conflict/download_date.csv — today's download date (idempotency stamp)"
dependencies:
  - ocha-stratus==0.1.7
  - requests==2.32.5
  - pandas==3.0.1
  - python-dotenv==1.2.2 (+ dotenv==0.9.9)
  - "secrets: ACLED_USERNAME, ACLED_PASSWORD (GitHub Actions secrets; OAuth2 password-grant)"
  - "secrets: DSCI_AZ_BLOB_DEV_SAS_WRITE, DSCI_AZ_BLOB_PROD_SAS (blob write access)"
downstream:
  - "Any pipeline/app consuming ACLED conflict event data from the acled-conflict blob container — no known named downstream as of ingestion"
depends_on: []
discrepancies:
  - "[gap] Not registered in infrastructure/deployments.md GitHub Actions pipelines table — this page's deployment block is currently the only home for its GHA schedule; add a registry row."
  - "[stale] extra.no_databricks notes 'not in deployments.md Databricks table' — true but irrelevant; the real omission is the GHA table, not the Databricks one."
  - "[conflict] event_date cutoff is hardcoded to '2026-02-27' in utils.py — fixed literal, not derived from last-run/config, so the daily run re-fetches a growing fixed-start window every day rather than incremental new events."
  - "[conflict] Idempotency guard is a no-op: get_raw_data() reads download_date.parquet but the date-match branch only logs (no early return), and the except branch falls through — every run re-downloads regardless."
  - "[conflict] Stage mismatch: idempotency read uses stage='dev'; both uploads use stratus default stage (prod) — read and writes are not on the same stage."
  - "[stale] Output blob paths are flat (raw.csv, download_date.csv at container root projects/acled-conflict) — does not follow the team {PREFIX}/{raw|processed}/{datasource}/{filename} convention."
source_repo: ocha-dap/ds-acled-fetcher
source_branch: main
source_sha: "004404d1d19065779194705e2a1cc1e19710ec39"
code_ref:
  - "utils.py — get_token(), get_raw_data() (all logic)"
  - "main.py — entrypoint (calls get_raw_data())"
  - "constant.py — API_BASE_URL, TOKEN_URL, credential env vars"
  - ".github/workflows/main.yml — GHA schedule + secrets injection"
extra:
  idempotency_note: "get_raw_data() checks download_date.parquet before fetching; if today's date matches the stored date, it logs and proceeds anyway (the except branch continues regardless — idempotency guard is effectively a no-op due to missing early return)"
  hardcoded_cutoff: "event_date filter is hardcoded to '2026-02-27' in utils.py — not derived from config or last-run date; only fetches events after that fixed date"
  blob_stage_inconsistency: "date check uses stage='dev'; uploads use default stage (likely prod); the CSV output path lacks a subdirectory (raw.csv, not acled_conflict/raw.csv)"
  no_databricks: "GHA-only; not a Databricks job. The relevant registry gap is the deployments.md GitHub Actions table (see discrepancies), not the Databricks table."
visibility: internal
last_synced: "2026-06-22"
---

# acled-fetcher

> Runbook. What feeds it, what it emits, and what to do when it breaks at 2 am.

## One-liner

Daily: authenticate to ACLED API via OAuth2 password grant → fetch all conflict events since 2026-02-27 → write raw CSV + download-date stamp to the `acled-conflict` blob container.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| `main.yml` (job `run-script`, step "Run script") | `.github/workflows/main.yml` | `0 8 * * *` (daily 08:00 UTC) + `workflow_dispatch` (manual) | live |

GitHub Actions only — no Databricks job. **Registry gap:** this pipeline is not yet listed in the GitHub Actions pipelines table in `infrastructure/deployments.md` (it should be added). The workflow `name:` is literally `main.yml` and the single job id is `run-script`; both scheduled (daily 08:00 UTC) and manually dispatchable.

## Inputs

- **ACLED REST API** (`https://acleddata.com/api/acled/read`) — paginated JSON, `limit=0` (all records), filtered to `event_date > 2026-02-27`.
- **ACLED OAuth2 token endpoint** (`https://acleddata.com/oauth/token`) — password-grant flow using `ACLED_USERNAME` / `ACLED_PASSWORD`.
- **Blob idempotency guard** — reads `projects/acled-conflict/acled_conflict/download_date.parquet` (dev stage) to check if today was already downloaded. Caution: the guard is effectively a no-op — the `except` branch continues rather than returning early, so a re-run always re-downloads.

## Steps

1. Load `.env` (local dev) or rely on GHA secrets for `ACLED_USERNAME`, `ACLED_PASSWORD`, and SAS tokens.
2. `get_token()` — POST to token endpoint with password grant; extract `access_token`.
3. `get_raw_data()` — attempt to read `download_date.parquet`; regardless of result, proceed.
4. GET `acleddata.com/api/acled/read` with `limit=0`, `event_date_where=">", event_date="2026-02-27"`.
5. Parse JSON response field `"data"` into a DataFrame.
6. Upload `download_date.csv` and `raw.csv` to `container_name="projects/acled-conflict"` via `stratus.upload_csv_to_blob`.

Full logic in `utils.py`. See `code_ref`.

## Outputs

| artifact | path | format | notes |
|---|---|---|---|
| ACLED raw events | `projects/acled-conflict/raw.csv` | CSV | all event columns returned by API |
| Download date stamp | `projects/acled-conflict/download_date.csv` | CSV | single-row, column `acled_download_date` |

Note: blob container is `projects/acled-conflict`; the paths written are flat (no `raw/` prefix), inconsistent with the team blob-naming convention (`{PREFIX}/{raw|processed}/{datasource}/{filename}`).

## Dependencies

- `ocha-stratus==0.1.7` — blob read (`load_blob_data`) and write (`upload_csv_to_blob`)
- `requests` — HTTP calls to ACLED API and OAuth2 token endpoint
- `pandas` — DataFrame construction and parquet/CSV handling
- `python-dotenv` — local `.env` loading
- **GitHub secrets:** `ACLED_USERNAME`, `ACLED_PASSWORD`, `DSCI_AZ_BLOB_DEV_SAS_WRITE`, `DSCI_AZ_BLOB_PROD_SAS`

No Listmonk, no DB writes, no ocha-relay.

## Failure modes & debugging

**Common failures:**

1. **Auth failure** — `requests.post` to token endpoint raises `HTTPError`. Check that `ACLED_USERNAME` / `ACLED_PASSWORD` secrets are set and the ACLED account is active. Logs nothing helpful before raising.

2. **API rate-limit / large payload** — `limit=0` fetches the entire dataset every run. If ACLED changes rate-limit policy or the dataset grows large, this can timeout or get 429'd. No retry logic exists.

3. **Hardcoded cutoff date** — `event_date` is hardcoded to `"2026-02-27"` in `utils.py`. After that date has been in the past for a while the dataset will grow unboundedly. To update the cutoff, edit `utils.py` directly.

4. **Idempotency guard silently skipped** — the `except` block in `get_raw_data` catches all exceptions and continues; if `download_date.parquet` is missing, the job re-downloads. This is fine functionally but means the guard provides no protection.

5. **Blob stage mismatch** — the date check uses `stage="dev"` but uploads use the default stratus stage. In a prod context, the idempotency read and writes may not be on the same stage.

**Logs:** GitHub Actions run logs — check the `Run script` step. No structured logging beyond `logging.debug` / `logging.info` calls.

**Manual re-run:** the workflow has `workflow_dispatch`, so it can be triggered on demand from the Actions tab (no need to wait for the 08:00 UTC cron).

## Downstream consumers

No named downstream pipeline or app identified in this repo or the KB at ingestion time. The `projects/acled-conflict/raw.csv` blob is the handoff point — any consumer reads that container.

<!-- TODO: identify which frameworks or monitoring pipelines consume acled-conflict blob data -->
