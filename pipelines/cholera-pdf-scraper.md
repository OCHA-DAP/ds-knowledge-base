---
content_type: pipeline
name: cholera-pdf-scraper
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Download Latest WHO PDF", ref: ".github/workflows/download-latest-who-pdf.yml", schedule: "47 13 * * 2,5 (+ workflow_dispatch)", status: live }
    - { name: "Extract Data from WHO PDF", ref: ".github/workflows/extract-from-pdf.yml", schedule: "workflow_run on 'Download Latest WHO PDF' success (branch=main) + workflow_dispatch", status: live }
    - { name: "Rule-Based Extraction from WHO PDF", ref: ".github/workflows/rule-based-extract.yml", schedule: "workflow_run on 'Download Latest WHO PDF' success (branch=main) + workflow_dispatch", status: live }
    - { name: "Post-Process Extractions", ref: ".github/workflows/post-process-extractions.yml", schedule: "workflow_call (chained from both extraction jobs) + workflow_dispatch", status: live }
    - { name: "Test OpenAI Connection", ref: ".github/workflows/test-openai-connection.yml", schedule: "workflow_dispatch (manual only)", status: live }
inputs:
  - "WHO Cholera Outbreak Report PDFs (weekly bulletins, apps.who.int primary / iris.who.int Selenium fallback)"
  - "GitHub-hosted CSV metadata: https://github.com/CBPFGMS/pfbi-data/raw/main/who_download_log.csv"
  - "Azure Blob (dev stage, container 'projects'): ds-cholera-pdf-scraper/raw/monitoring/pdfs/ (PDF source for extraction jobs)"
  - "Azure Blob (dev stage, container 'projects'): ds-cholera-pdf-scraper/raw/monitoring/llm_extractions/ (raw LLM CSVs for post-processing)"
  - "Azure Blob (dev stage, container 'projects'): ds-cholera-pdf-scraper/raw/monitoring/rule_based_extractions/ (raw rule-based CSVs for post-processing)"
outputs:
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/raw/monitoring/pdfs/OEWxx-YYYY.pdf (downloaded PDFs)"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/raw/monitoring/llm_extractions/OEWxx-YYYY_<model>_<run_id>.csv (raw LLM extractions)"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/raw/monitoring/rule_based_extractions/OEWxx-YYYY_rule-based_<run_id>.csv (raw rule-based extractions)"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/monitoring/llm_extractions/OEWxx-YYYY_<model>_<run_id>_processed.csv"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/monitoring/rule_based_extractions/OEWxx-YYYY_rule-based_<run_id>_processed.csv"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/monitoring/master_extractions/OEWxx-YYYY_master.csv (production-ready master per week)"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/monitoring/comparisons/OEWxx-YYYY_comparison_summary.csv"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/monitoring/comparisons/OEWxx-YYYY_discrepancies.csv"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/logs/prompt_logs/run_<id>.parquet"
  - "Azure Blob (dev, container 'projects'): ds-cholera-pdf-scraper/processed/logs/tabular_preprocessing_logs/run_<id>.parquet"
dependencies:
  - ocha-stratus
  - openai (GPT-5 default; OpenRouter for non-OpenAI models)
  - tabula-py (requires Java, rule-based extraction)
  - pdfplumber
  - selenium + Chrome (iris.who.int URL resolution)
  - duckdb (local DuckDB parquet logs in GHA runner)
  - "Secret: DSCI_AZ_BLOB_DEV_SAS (read)"
  - "Secret: DSCI_AZ_BLOB_DEV_SAS_WRITE (write)"
  - "Secret: DSCI_AZ_OPENAI_API_KEY_WHO_CHOLERA"
downstream: []
depends_on: []
discrepancies:
  - "[gap] Not yet listed in infrastructure/deployments.md GitHub Actions registry table — that table indexes floodexposure-monitoring, nhc-forecast, imerg, hurricanes-monitoring, mdg-monitoring but not this pipeline. Registry needs a row added (repo ds-cholera-pdf-scraper, GHA, dev stage)."
  - "[conflict] All GHA workflows hardcode STAGE=dev (download/extract/rule-based/post-process). There is NO prod deployment despite README listing 'Production Pipeline' and 'Database integration' as goals — outputs land only on the dev blob (imb0chd0dev), so this is a dev-slot deployment, not production."
  - "[stale] Legacy historical-backfill path ds-cholera-pdf-scraper/raw/pdfs/ (276 PDFs, via scripts/download_historical_pdfs.py) differs from the live monitoring path ds-cholera-pdf-scraper/raw/monitoring/pdfs/. The legacy path is not part of the scheduled pipeline."
  - "[gap] No downstream consumer wired up: the per-week master CSV is the intended production output but README flags integration as in-progress; no DB table or downstream pipeline/app currently reads it."
source_repo: ocha-dap/ds-cholera-pdf-scraper
source_branch: main
source_sha: 61fd916
code_ref:
  - ".github/workflows/download-latest-who-pdf.yml"
  - ".github/workflows/extract-from-pdf.yml"
  - ".github/workflows/rule-based-extract.yml"
  - ".github/workflows/post-process-extractions.yml"
  - "scripts/run_llm_extraction_gha.py"
  - "scripts/run_rule_based_extraction_gha.py"
  - "scripts/process_raw_extractions.py"
  - "src/config.py"
  - "src/post_processing.py"
  - "src/monitoring/comparisons.py"
extra:
  stage: dev
  note: "All GHA workflows run STAGE=dev — no prod deployment exists. The pipeline is in active development; 'Production Pipeline' is listed as in-progress in the README."
  historical_pdfs: "276 historical PDFs backfilled to ds-cholera-pdf-scraper/raw/pdfs/ (legacy path, container 'projects'; distinct from the live raw/monitoring/pdfs/ path)"
  blob_config: "BLOB_PROJ_DIR=ds-cholera-pdf-scraper, BLOB_CONTAINER=projects, STAGE=dev (src/config.py). Blob path prefix is the proj dir, NOT 'projects/<projdir>' — 'projects' is the container."
  registry_status: "Pending addition to infrastructure/deployments.md GHA pipelines table."
  prompt_versions: "v1.1.x series (legacy); v1.4.x series (current GHA default v1.4.8)"
  accuracy: "91.09% field-level accuracy at v1.1.2; current GHA default model is gpt-5 with prompt v1.4.8"
visibility: internal
last_synced: "2026-06-22"
---

# Cholera PDF Scraper

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

> **Rendered analysis book:** [llm-data-sraping.netlify.app](https://llm-data-sraping.netlify.app) (Quarto `book_cholera_scraping/`, published to Netlify; URL has a typo — "sraping" — but is the live address; see `infrastructure/deployments.md`).

## One-liner

*Twice-weekly (Tue/Fri): download latest WHO Cholera Bulletin PDF → run LLM (GPT-5) and rule-based (Tabula) extractions in parallel → post-process and standardize → write per-week master CSV and comparison report to Azure Blob (dev stage only).*

## Jobs & schedule

The pipeline is a chained set of GitHub Actions workflows. The download triggers the two extraction jobs in parallel; each extraction then chains to the shared post-process workflow which optionally generates comparisons.

| job (workflow `name:`) | ref | schedule | status |
|---|---|---|---|
| Download Latest WHO PDF | `.github/workflows/download-latest-who-pdf.yml` | `47 13 * * 2,5` (Tue & Fri 13:47 UTC) + `workflow_dispatch` | live |
| Extract Data from WHO PDF (LLM) | `.github/workflows/extract-from-pdf.yml` | `workflow_run` on Download success (branch=main) + `workflow_dispatch` | live |
| Rule-Based Extraction from WHO PDF | `.github/workflows/rule-based-extract.yml` | `workflow_run` on Download success (branch=main) + `workflow_dispatch` | live |
| Post-Process Extractions | `.github/workflows/post-process-extractions.yml` | `workflow_call` (chained from both extraction jobs) + `workflow_dispatch` | live |
| Test OpenAI Connection | `.github/workflows/test-openai-connection.yml` | `workflow_dispatch` (manual only) | live |

The LLM extraction workflow's actual `name:` is **"Extract Data from WHO PDF"** (the "(LLM)" qualifier is added here to disambiguate from the rule-based job). Both extraction jobs can also be triggered manually via `workflow_dispatch`. The two extraction workflows chain to `post-process-extractions.yml` via `workflow_call` (`uses: ./.github/workflows/post-process-extractions.yml`), each gated on `workflow_run.conclusion == 'success'` (branch `main`).

**Deployment note:** This pipeline is GitHub-Actions-only on `main`, all jobs `STAGE=dev`. It is **not yet listed in `infrastructure/deployments.md`** (GHA pipelines table) — registry row pending.

## Inputs

- **WHO Cholera Bulletin PDFs** — weekly reports scraped from `apps.who.int` (primary) and `iris.who.int` (JavaScript-heavy fallback via Selenium/Chrome). URL list read from a GitHub-hosted CSV at `https://github.com/CBPFGMS/pfbi-data/raw/main/who_download_log.csv`.
- **Azure Blob (dev) — existing PDFs**: `projects/ds-cholera-pdf-scraper/raw/monitoring/pdfs/` — extraction jobs pull the latest PDF from here rather than downloading fresh.

## Steps

1. **Download** (`download-latest-who-pdf.yml`): hits `apps.who.int` for the latest bulletin, falls back to Selenium for iris.who.int URLs. Uploads to `raw/monitoring/pdfs/OEWxx-YYYY.pdf`. On scheduled runs, always uploads; on manual dispatch, respects an `upload_to_blob` toggle.

2. **LLM extraction** (`extract-from-pdf.yml` → `scripts/run_llm_extraction_gha.py`): downloads the latest PDF from blob, runs `src/pdf_upload_extract.py` (direct PDF upload to OpenAI, preprocessor `none-pdf-upload`) with GPT-5 and prompt `v1.4.8`. Raw CSV uploaded to `raw/monitoring/llm_extractions/`. Outputs `EXTRACTION_WEEK` and `EXTRACTION_YEAR` for downstream chaining.

3. **Rule-based extraction** (`rule-based-extract.yml` → `scripts/run_rule_based_extraction_gha.py`): runs Tabula (lattice table detection, requires Java) on the same PDF. Raw CSV uploaded to `raw/monitoring/rule_based_extractions/`.

4. **Post-processing** (`post-process-extractions.yml` → `scripts/process_raw_extractions.py`): downloads raw CSVs, applies `src/post_processing.py` pipeline (clean numerics, standardize CFR, event/country names, column names, harmonize nulls), uploads processed CSVs. For LLM source, also writes a `master_extractions/OEWxx-YYYY_master.csv`. Optionally generates LLM-vs-rule-based comparison reports via `src/monitoring/comparisons.py`.

5. **Comparison generation** (within post-process job): if both LLM and rule-based processed data exist for the same week/year, produces `comparisons/OEWxx-YYYY_comparison_summary.csv` and `_discrepancies.csv`.

## Outputs

All blob paths below are relative to the blob-project dir `ds-cholera-pdf-scraper/`, in container **`projects`** on the **dev** stage account (`imb0chd0dev.blob.core.windows.net`). Note `projects` is the container, not a path segment — the path prefix is `ds-cholera-pdf-scraper/...`. There is no prod deployment (all workflows hardcode `STAGE=dev`).

| output | path |
|---|---|
| Downloaded PDF | `raw/monitoring/pdfs/OEWxx-YYYY.pdf` |
| Raw LLM extraction | `raw/monitoring/llm_extractions/OEWxx-YYYY_<model>_<run_id>.csv` |
| Raw rule-based extraction | `raw/monitoring/rule_based_extractions/OEWxx-YYYY_rule-based_<run_id>.csv` |
| Processed LLM extraction | `processed/monitoring/llm_extractions/OEWxx-YYYY_<model>_<run_id>_processed.csv` |
| Processed rule-based extraction | `processed/monitoring/rule_based_extractions/OEWxx-YYYY_rule-based_<run_id>_processed.csv` |
| Master dataset (prod-ready) | `processed/monitoring/master_extractions/OEWxx-YYYY_master.csv` |
| Comparison summary | `processed/monitoring/comparisons/OEWxx-YYYY_comparison_summary.csv` |
| Discrepancy report | `processed/monitoring/comparisons/OEWxx-YYYY_discrepancies.csv` |
| Prompt run log | `processed/logs/prompt_logs/run_<id>.parquet` |
| Preprocessing log | `processed/logs/tabular_preprocessing_logs/run_<id>.parquet` |

## Dependencies

- **ocha-stratus** — all blob reads/writes (`load_blob_data`, `load_csv_from_blob`, `upload_csv_to_blob`, `upload_parquet_to_blob`).
- **openai** — GPT-5 via OCHA's organizational key (`DSCI_AZ_OPENAI_API_KEY_WHO_CHOLERA`). Non-OpenAI models route through OpenRouter (`OPENROUTER_API_KEY`).
- **tabula-py** — rule-based PDF table extraction; requires Java (`default-jre`) on the runner. Sensitive to PDF structure changes.
- **pdfplumber** — text extraction for LLM preprocessing modes other than `none-pdf-upload`.
- **selenium + Google Chrome** — resolves iris.who.int URLs using DSpace 7 API; installed in download job only.
- **duckdb + pyarrow** — local parquet logging of LLM prompt runs on the GHA runner.
- **Secrets required**: `DSCI_AZ_BLOB_DEV_SAS`, `DSCI_AZ_BLOB_DEV_SAS_WRITE`, `DSCI_AZ_OPENAI_API_KEY_WHO_CHOLERA`.

## Failure modes & debugging

- **Download fails (WHO server)**: WHO rate-limits `iris.who.int`; pipeline uses `apps.who.int` as primary. If both fail, no PDF is uploaded and extraction jobs are skipped (they check `workflow_run.conclusion == 'success'`). Check the GHA run summary — metadata.json shows `status: already_exists` if the bulletin hadn't changed.
- **LLM extraction returns 0 records**: JSON parsing failed from GPT-5 response. The parquet log (`processed/logs/prompt_logs/run_<id>.parquet`) contains the raw LLM response for debugging. Query with `src.cloud_logging.DuckDBCloudQuery`.
- **Rule-based extraction fails**: Usually Java missing or Tabula failing on changed PDF table structure. Check the "Common Issues" step in the GHA summary. The workflow explicitly notes Java as a dependency.
- **Post-processing skipped**: If `EXTRACTION_WEEK`/`EXTRACTION_YEAR` outputs are missing from the extraction job (regex match on output log failed), post-processing may run but comparison generation will be skipped.
- **All workflows run STAGE=dev** — there is no prod path. If the raw/processed split on the blob looks inconsistent, note that the legacy historical download path (`raw/pdfs/`) differs from the current monitoring path (`raw/monitoring/pdfs/`).
- **Blob auth**: Uses SAS tokens; `DSCI_AZ_BLOB_DEV_SAS_WRITE` is passed as both `DSCI_AZ_BLOB_DEV_SAS` and `DSCI_AZ_BLOB_DEV_SAS_WRITE` in several workflow steps — this is intentional (the pipeline needs write for both read-listing and upload).

## Downstream consumers

No downstream pipelines or apps are currently registered as consumers of the master extractions. The master CSV (`OEWxx-YYYY_master.csv`) is the intended production-ready output, but the README notes production pipeline integration as in-progress. Analysts can manually download the master file from blob and create `OEWxx-YYYY_master_edit.csv` if corrections are needed.
