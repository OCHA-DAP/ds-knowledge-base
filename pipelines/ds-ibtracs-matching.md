---
content_type: pipeline
name: ibtracs-matching
type: matching   # manual identifier-matching, not an ingest/monitoring/exposure/alert system
status: live
deployment:
  platform: manual
  resource_group: null
  jobs:
    - { name: "cerf_sid_matching notebook", ref: "notebooks/cerf_sid_matching.ipynb", schedule: "on-demand", status: live }
    - { name: "cerf_api_excel_check notebook", ref: "notebooks/cerf_api_excel_check.ipynb", schedule: "on-demand", status: live }
inputs:
  - "CERF OneGMS API: https://cerfgms-webapi.unocha.org/v1/application/All.xml (all CERF applications, XML, via src/datasources/cerf.py)"
  - "DB table: storms.ibtracs_storms (via ocha-stratus, stage=prod)"
  - "Blob: cerf/AllocationsByYear.xlsx (container=global, via stratus.load_blob_data) — CERF allocations Excel export, cross-checked against the API"
outputs: []   # nothing persisted anywhere — see discrepancies
dependencies:
  - "ocha-stratus>=0.1.7 (DB engine + blob read)"
  - "openpyxl>=3.1.5 (Excel parsing)"
  - "matplotlib>=3.10.8"
  - "requests (CERF OneGMS API fetch, no timeout set)"
downstream: []
depends_on:
  - "storms-pipeline"   # reads storms.ibtracs_storms, produced by the Databricks 'Run IBTrACS' job (638351145729392) on ds-storms-pipeline
source_repo: ocha-dap/ds-ibtracs-matching
source_branch: cerf-notebook
source_sha: ab93116
code_ref:
  - "notebooks/cerf_sid_matching.ipynb — manual CERF-allocation-to-IBTrACS-sid matching"
  - "notebooks/cerf_api_excel_check.ipynb — CERF OneGMS API vs Excel-export consistency check"
  - "src/datasources/cerf.py — load_cerf_applications() OneGMS API fetch + XML parse"
discrepancies:
  - "[gap] Not deployed anywhere — no chd-* Azure app, no Databricks job, no GitHub Actions workflow (repo has no .github/workflows/). Runs ad hoc, locally, by an analyst in Jupyter. Not in infrastructure/deployments.md or pipeline-registry.md under any handle."
  - "[gap] No persistent output. The CERF-code-to-IBTrACS-sid crosswalk (`new_cerfcode2sid`) is a Python dict hardcoded in the notebook cell, not written to a DB table or blob — results only exist as notebook cell output/state until someone manually copies them elsewhere."
  - "[gap] The hardcoded `new_cerfcode2sid` dict has exactly 2 entries as of `cerf-notebook`@ab93116 (one resolved SID, one explicit `None`) — a small manual sample, not a completed crosswalk of all CERF Storm/Rapid-Response allocations."
  - "[conflict] Overlaps with the separately-ingested [`cerf-supplement`](cerf-supplement.md) pipeline (`ocha-dap/ds-cerf-supplement`, branch `initial-app`), which does the same CERF-allocation-to-IBTrACS-sid annotation task via a locally-run Streamlit app that persists to `global/dev/cerf/cerf_supplemental_data.parquet`. Unclear whether this notebook repo is an earlier exploration that `ds-cerf-supplement` superseded, a parallel one-off by a different analyst, or still actively used alongside it — no cross-reference between the two repos was found."
  - "[gap] `cerf.load_cerf_applications()` calls `requests.get(url)` with no timeout (unlike `ds-cerf-supplement`'s equivalent fetch, which sets a 120s timeout) — a slow/hung OneGMS API would hang the notebook indefinitely."
extra: {}
visibility: internal
last_synced: "2026-07-02"
---

# IBTrACS matching

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*Ad hoc, notebook-only: pull CERF Storm/Rapid-Response allocations from the OneGMS API, eyeball each against IBTrACS storms by basin/year, and hand-write the CERF-code → IBTrACS-`sid` match into a dict — no automation, no persisted output.*

## Jobs & schedule

Not a scheduled pipeline — two exploratory Jupyter notebooks (synced to `.md` via jupytext) run manually by an analyst, on-demand, with no CI/CD.

| job | ref | schedule | status |
|---|---|---|---|
| cerf_sid_matching notebook | `notebooks/cerf_sid_matching.ipynb` | on-demand | live |
| cerf_api_excel_check notebook | `notebooks/cerf_api_excel_check.ipynb` | on-demand | live |

## Inputs

1. **CERF OneGMS API** (`https://cerfgms-webapi.unocha.org/v1/application/All.xml`) — all CERF applications as XML, parsed to a DataFrame by `cerf.load_cerf_applications()` (`src/datasources/cerf.py`). Filtered in `cerf_sid_matching` to `EmergencyTypeName == "Storm"` and `WindowFullName == "Rapid Response"`.
2. **DB table `storms.ibtracs_storms`** — full table pulled via `ocha_stratus.get_engine(stage="prod")`, filtered to `season >= 2006`. Populated by the Databricks `Run IBTrACS` job in [`storms-pipeline`](storms-pipeline.md) (job id `638351145729392` — **currently failing every run**, see `infrastructure/pipeline-registry.md`).
3. **Blob `cerf/AllocationsByYear.xlsx`** (container `global`) — a CERF allocations Excel export, loaded via `stratus.load_blob_data`, used only in `cerf_api_excel_check.ipynb` to cross-check the OneGMS API's numbers/dates against the Excel export for a test country (`Afghanistan`).

## Steps

1. `cerf_sid_matching.ipynb`: load CERF Storm/Rapid-Response applications from the API; load `storms.ibtracs_storms` (season ≥ 2006); build lookup URLs for both (CERF allocation summary page, IBTrACS `ncics.org` storm page).
2. Analyst manually reads each CERF allocation's `CN_Summary` text, looks up the matching tropical cyclone on the IBTrACS by-year-by-basin browser, and adds an entry to the hardcoded `new_cerfcode2sid` dict (`ApplicationCode -> sid`, or `None` if no TC match).
3. Any `ApplicationCode` not yet in the dict is printed (code, summary, CERF URL) for the analyst to triage next.
4. `cerf_api_excel_check.ipynb` (separate, unrelated check): loads the Excel export and the API in parallel, casts types, and does an outer merge on `(Country, Amount in US$, Allocation date)` vs `(CountryName, TotalAmountApproved, CN_ERC_EndorsementDate)` to spot mismatches between the two CERF sources. Ends mid-exploration (no asserted conclusion in the notebook).

See `code_ref` for the actual cells — this is exploratory analyst work, not a maintained script; there is no CLI/entrypoint beyond running notebook cells in order.

## Outputs

None persisted. The `new_cerfcode2sid` mapping exists only as a Python dict literal inside `notebooks/cerf_sid_matching.ipynb` — it is not written to a DB table, blob, or file. Re-running the notebook from a fresh checkout reproduces only the 2 entries currently hardcoded; anything an analyst matches beyond that lives only in their local notebook edits unless committed to the repo.

## Dependencies

- **`ocha-stratus>=0.1.7`** — Postgres engine (`get_engine(stage="prod")`) and blob read (`load_blob_data`).
- **`openpyxl>=3.1.5`** — reads the `.xlsx` CERF export.
- **`matplotlib>=3.10.8`** — declared but not visibly used in either notebook as read.
- **`requests`** — third-party HTTP lib, not declared in `pyproject.toml` (pulled in transitively via `ocha-stratus`); imported directly in `cerf.py` for the OneGMS API fetch; no timeout set.
- Implicit: whatever env vars `ocha-stratus` needs for `stage="prod"` DB access and blob read (not set explicitly in this repo's code — inherited from the shared `ocha-stratus` config/env).
- Python ≥3.11.4, `uv` for env management (per `pyproject.toml`).

## Failure modes & debugging

| Symptom | Likely cause | Check |
|---|---|---|
| `cerf.load_cerf_applications()` hangs | No `timeout` on the `requests.get` call; OneGMS API slow/unresponsive | Interrupt and retry; consider adding a timeout (as `ds-cerf-supplement` does) |
| `df_storms` empty or missing recent storms | `storms.ibtracs_storms` stale — upstream Databricks `Run IBTrACS` job is failing (confirmed down as of the pipeline registry snapshot) | Check [`storms-pipeline`](storms-pipeline.md) / `infrastructure/pipeline-registry.md` job health before trusting the storm list |
| Excel/API merge in `cerf_api_excel_check` produces mostly unmatched rows | Column dtype mismatch (dates/amounts) between Excel and API — the notebook already casts dates and amounts before merging; check for uncast columns | Re-check `df_cerf_api[["TotalAmountApproved","CN_AmountRequested"]]` cast and `CN_ERC_EndorsementDate` dtype |
| Manually matched SIDs "disappear" | They were never persisted — only live in notebook cell state / uncommitted `new_cerfcode2sid` edits | Check `git diff` on the notebook before assuming loss; there is no blob/DB backup |

No logs, no monitoring, no scheduled run to check — this only "breaks" while an analyst is actively running it.

## Downstream consumers

None confirmed. The crosswalk produced here isn't written anywhere another system can read it — it exists only inside the notebook. The closest thing to a consumer is conceptual: [`cerf-supplement`](cerf-supplement.md) performs the same CERF-allocation ↔ IBTrACS-`sid` annotation task via a (locally-run) Streamlit app that *does* persist to blob (`global/dev/cerf/cerf_supplemental_data.parquet`); whether any matches from this notebook were ever carried over there is not evidenced in either repo.
