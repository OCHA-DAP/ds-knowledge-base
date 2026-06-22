---
content_type: pipeline
name: cerf-supplement
type: annotation
status: live
deployment:
  platform: manual
  resource_group: null
  jobs:
    - { name: "cerf-supplement app", ref: "app.py (streamlit run)", schedule: "on-demand", status: live }
inputs:
  - "OneGMS API: https://cerfgms-webapi.unocha.org/v1/application/All.xml (CERF allocations, all, XML, cached 1h)"
  - "DB table: storms.ibtracs_storms (sid, name, season — via ocha-stratus, cached 24h)"
  - "Blob: blob_name=cerf/cerf_supplemental_data.parquet, container=global, stage=dev (existing user annotations, read on startup via stratus.load_parquet_from_blob)"
outputs:
  - "Blob: blob_name=cerf/cerf_supplemental_data.parquet, container=global, stage=dev (supplemental storm SIDs + drought period metadata, written on user save via stratus.upload_parquet_to_blob)"
dependencies:
  - "ocha-stratus (blob read/write, DB engine)"
  - "streamlit>=1.35"
  - "anthropic>=0.40 (claude-opus-4-8, used in src/claude_assist.py — not wired into the main app UI as of initial-app branch)"
  - "DSCI_AZ_BLOB_DEV_SAS (read access to dev blob)"
  - "DSCI_AZ_BLOB_DEV_SAS_WRITE (write access to dev blob)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
  - "ANTHROPIC_API_KEY (for claude_assist; not required if AI assist feature is disabled)"
downstream: []   # no confirmed consumer yet. NB the apps/glb-tropicalcyclones-app repo is the seed SOURCE (its data/cerf-storms-with-sids-2024-02-27.csv populates SIDs via scripts/seed_from_existing.py), not a consumer of this blob — relationship is one-directional upstream, so not listed here.
depends_on:
  - "storms-pipeline"   # reads storms.ibtracs_storms, produced by the Databricks 'Run IBTrACS' job (638351145729392) on ds-storms-pipeline
discrepancies:
  - "[gap] Not deployed anywhere in infrastructure/deployments.md — no chd-* Azure web app, no Databricks job, no GitHub Actions workflow (.github/workflows/ is absent). Runs on-demand locally (`streamlit run app.py`) by an analyst with the right env vars. There is no scheduled/hosted instance to monitor; logs are local stdout only."
  - "[gap] Operational branch is `initial-app` (HEAD 69c375d), NOT `main`. `main` is one initial-state behind; all current app + scripts/seed work lives on `initial-app`. Do not read `main`."
  - "[stale] `src/claude_assist.py` (calls `claude-opus-4-8` to suggest IBTrACS SID / drought months from allocation text) is scaffolded but NOT wired into the app.py UI as of `initial-app` — dead code; ANTHROPIC_API_KEY is unused by the running app."
  - "[conflict] Python version: pyproject.toml declares `requires-python = >=3.11`, but CLAUDE.md/README say 3.12 is REQUIRED (psycopg2-binary, pulled in by ocha-stratus, fails to build on 3.14+ which dropped distutils). Use `uv venv --python 3.12`; the >=3.11 pin is too loose."
  - "[stale] pyproject pins `ocha-stratus = { path = \"../ocha-stratus\", editable = true }` (local editable sibling checkout), not a published/version-pinned release — reproducibility depends on the local ../ocha-stratus working copy."
  - "[gap] Blob writes are silent on read-failure: load_supplemental() catches ALL exceptions and returns an empty DataFrame (missing/expired DSCI_AZ_BLOB_DEV_SAS looks identical to a genuinely empty blob), so existing annotations can silently vanish from the UI on reload."
source_repo: ocha-dap/ds-cerf-supplement
source_branch: initial-app
source_sha: 69c375d
code_ref:
  - "app.py — Streamlit entrypoint, data editor, save logic"
  - "src/cerf_api.py — OneGMS API fetch + XML parse"
  - "src/db.py — storms.ibtracs_storms query"
  - "src/storage.py — blob read/write for supplemental parquet"
  - "src/claude_assist.py — Claude API suggestion helper (not yet wired into main app UI)"
  - "scripts/seed_from_existing.py — one-off script to pre-populate SIDs from ds-glb-tropicalcyclones-app CSV"
extra:
  claude_assist_status: "src/claude_assist.py exists and calls claude-opus-4-8 to suggest IBTrACS SID or drought months from allocation text, but is NOT wired into the main app.py UI as of the initial-app branch — it is scaffolded/unused"
  blob_stage: dev
  blob_container: global
  python_version: "3.12 required (psycopg2-binary fails on 3.14+)"
  not_in_deployments_md: true
visibility: internal
last_synced: "2026-06-22"
---

# CERF Supplement

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

On-demand Streamlit app: pull all CERF allocations from the OneGMS API → editable table for analysts to tag each allocation with a storm IBTrACS SID and/or drought period → write supplemental metadata to blob.

## Jobs & schedule

This is an interactive Streamlit app with no scheduled job. It runs on-demand by analysts.

| job | ref | schedule | status |
|---|---|---|---|
| cerf-supplement app | `streamlit run app.py` | on-demand | live |

Not present in the Azure web apps registry or Databricks jobs registry (`infrastructure/deployments.md`). As of ingestion the app runs locally by analysts with the correct env vars.

## Inputs

1. **OneGMS CERF API** (`https://cerfgms-webapi.unocha.org/v1/application/All.xml`) — all CERF allocations as XML; parsed to DataFrame with fields: `ApplicationID`, `ApplicationCode`, `ApplicationTitle`, `CountryName`, `Year`, `EmergencyTypeName`, `TotalAmountApproved`, `CN_ERC_EndorsementDate`, `WindowFullName`, `AllocationStatus`, `CN_Summary`, `OverviewoftheHumanitarianSituation`, `RationaleforCERFAllocation`. Cached 1h via `@st.cache_data`.
2. **DB table `storms.ibtracs_storms`** — columns `sid`, `name`, `season`; used to build the storm dropdown (`"NAME YEAR (SID)"` labels). Loaded via `ocha_stratus.get_engine()`, cached 24h.
3. **Blob `global/dev/cerf/cerf_supplemental_data.parquet`** — existing user annotations keyed by `ApplicationID`; loaded on startup and merged left onto the CERF allocations table.

## Steps

1. `fetch_cerf_allocations()` (`src/cerf_api.py`) — HTTP GET to OneGMS, parse XML, return DataFrame.
2. `load_storms()` (`src/db.py`) — SQL query to `storms.ibtracs_storms`, return sid/name/season.
3. `load_supplemental()` (`src/storage.py`) — `stratus.load_parquet_from_blob` from `global/dev/cerf/cerf_supplemental_data.parquet`; returns empty DataFrame with correct schema on first run or blob miss.
4. App merges CERF allocations with existing annotations (left join on `ApplicationID`), builds an editable `st.data_editor` table. Sidebar filters: emergency type, annotation status (All / Needs annotation / Annotated).
5. On user save, changed rows are upserted or removed from the in-memory supplemental DataFrame, then written back to blob via `save_supplemental()` (`stratus.upload_parquet_to_blob`).
6. `src/claude_assist.py` is scaffolded — calls `claude-opus-4-8` to suggest SID or drought period from allocation text — but is not wired into the main UI as of the `initial-app` branch.
7. `scripts/seed_from_existing.py` — a one-off migration script to pre-populate storm SIDs from `ds-glb-tropicalcyclones-app/data/cerf-storms-with-sids-2024-02-27.csv` (58 SIDs), matching on country + date + amount (with a country + amount fallback). Does not overwrite existing annotations.

For the editor state-management internals (the `baseline_df` / `editor_version` rebuild pattern, the `.values` index-alignment gotcha), see the spoke runbook `CLAUDE.md` — not restated here.

## Outputs

- **Blob `global/dev/cerf/cerf_supplemental_data.parquet`** (container `global`, stage `dev`): supplemental annotation table. Schema: `ApplicationID`, `sid`, `valid_month_start`, `valid_year_start`, `valid_month_end`, `valid_year_end`, `notes`, `updated_at`. One row per annotated CERF allocation. A row is deleted when all editable fields are cleared.

## Dependencies

- **`ocha-stratus`** — blob read/write (`load_parquet_from_blob`, `upload_parquet_to_blob`) and DB access (`get_engine()`).
- **`streamlit>=1.35`** — UI framework; uses `st.data_editor`, `@st.cache_data`.
- **`anthropic>=0.40`** — Claude API client, used only in the scaffolded `src/claude_assist.py` (not live in UI).
- **`DSCI_AZ_BLOB_DEV_SAS`** — read SAS token for dev blob. Without it, `load_supplemental` falls back to empty DataFrame silently.
- **`DSCI_AZ_BLOB_DEV_SAS_WRITE`** — write SAS token; saves will fail without it (Streamlit shows `st.error`).
- **`PGSSLMODE=require`** — set via `os.environ.setdefault` in `src/db.py`; required for Azure Postgres.
- **`ANTHROPIC_API_KEY`** — only needed if `claude_assist.get_suggestion()` is called; not required for the main app as of `initial-app`.
- Python 3.12 required (`psycopg2-binary` fails on 3.14+ which dropped `distutils`).

## Failure modes & debugging

| Symptom | Likely cause | Check |
|---|---|---|
| Storm dropdown empty / warning banner | DB unreachable or `PGSSLMODE` not set | Confirm `PGSSLMODE=require` in env; check `stratus.get_engine()` connectivity |
| Save fails (`st.error`) | `DSCI_AZ_BLOB_DEV_SAS_WRITE` not set or expired | Check env var; refresh SAS token |
| All annotations gone on reload | Blob miss (first run, or `DSCI_AZ_BLOB_DEV_SAS` unset) | `load_supplemental` silently returns empty on any exception; check read SAS and blob path `global/dev/cerf/cerf_supplemental_data.parquet` |
| CERF table empty | OneGMS API timeout or outage (120s timeout set) | Check `https://cerfgms-webapi.unocha.org/v1/application/All.xml` directly; cache is 1h so a Refresh clears it |
| Schema mismatch on load | Blob written by older code missing new columns | `load_supplemental` adds missing columns with `None` — check `_COLUMNS` list in `src/storage.py` is complete |

Logs: stdout of `streamlit run app.py`. No structured logging. No GHA or Databricks job logs — this runs locally.

## Downstream consumers

- No confirmed downstream consumer yet (`downstream: []`). [`apps/glb-tropicalcyclones-app`](../apps/glb-tropicalcyclones-app.md) is the seed *source*, not a consumer — its `data/cerf-storms-with-sids-2024-02-27.csv` populated SIDs via `scripts/seed_from_existing.py` (one-directional, upstream). Future consumers TBD.
- The supplemental parquet blob (`global/dev/cerf/cerf_supplemental_data.parquet`) is the deliverable; any framework or dashboard that needs CERF allocations enriched with storm SIDs or drought periods should read from it.
