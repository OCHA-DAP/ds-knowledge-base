---
content_type: analysis
name: ibtracs-matching
analysis_type: exploratory     # manual CERF-allocation ↔ IBTrACS-sid identifier matching; not a framework, not a scheduled pipeline
status: dormant                # 2 hand-matched entries as of cerf-notebook@ab93116; overlaps ds-cerf-supplement, no evidence of active use
country_iso3: global           # all CERF Storm/Rapid-Response allocations, not country-scoped
hazard: tropical-cyclone       # CERF "Storm" emergencies matched to IBTrACS tropical cyclones
summary: "Exploratory notebooks that hand-match CERF Storm/Rapid-Response allocations to IBTrACS storm `sid`s by basin/year, plus a CERF OneGMS-API-vs-Excel-export consistency check. No trigger, no schedule, nothing deployed or persisted — analyst work, not a pipeline."
data_sources: [cerf-allocations, ibtracs]
feeds: []                      # nothing consumes it; the crosswalk lives only in a notebook dict
# --- source repo ---
source_repo: ocha-dap/ds-ibtracs-matching
source_branch: cerf-notebook
source_sha: ab93116
code_ref:
  - "notebooks/cerf_sid_matching.ipynb — manual CERF-allocation-to-IBTrACS-sid matching"
  - "notebooks/cerf_api_excel_check.ipynb — CERF OneGMS API vs Excel-export consistency check"
  - "src/datasources/cerf.py — load_cerf_applications() OneGMS API fetch + XML parse"
depends_on:
  - "storms-pipeline"          # reads storms.ibtracs_storms, produced by the Databricks 'Run IBTrACS' job (638351145729392) on ds-storms-pipeline
discrepancies:
  - "[gap] Nothing deployed — no chd-* Azure app, no Databricks job, no GitHub Actions workflow (repo has no .github/workflows/). Runs ad hoc, locally, by an analyst in Jupyter; absent from infrastructure/deployments.md and pipeline-registry.md, as it should be."
  - "[gap] No persistent output. The CERF-code → IBTrACS-sid crosswalk (`new_cerfcode2sid`) is a Python dict hardcoded in the notebook cell, not written to a DB table or blob — results only exist as notebook cell state until someone copies them elsewhere."
  - "[gap] The hardcoded `new_cerfcode2sid` dict has exactly 2 entries as of `cerf-notebook`@ab93116 (one resolved SID, one explicit `None`) — a small manual sample, not a completed crosswalk of all CERF Storm/Rapid-Response allocations."
  - "[conflict] Overlaps with the [`cerf-supplement`](../pipelines/cerf-supplement.md) work (`ocha-dap/ds-cerf-supplement`, branch `initial-app`), which does the same CERF-allocation → IBTrACS-sid annotation via a locally-run Streamlit app that persists to `global/dev/cerf/cerf_supplemental_data.parquet`. Unclear whether this notebook repo is an earlier exploration that `ds-cerf-supplement` superseded, a parallel one-off, or still used alongside it — no cross-reference between the two repos was found."
  - "[gap] `cerf.load_cerf_applications()` calls `requests.get(url)` with no timeout (unlike `ds-cerf-supplement`'s equivalent fetch, which sets a 120s timeout) — a slow/hung OneGMS API would hang the notebook indefinitely. `requests` is third-party but undeclared in `pyproject.toml` (transitive via `ocha-stratus`)."
extra: {}
visibility: internal
last_synced: "2026-07-02"
---

# IBTrACS matching — analysis

> **Analysis, not a framework — and not a pipeline.** No published framework doc, no trigger logic, no schedule, no deployment, no persisted output. This is exploratory analyst work — hand-matching CERF allocations to storm identifiers — captured so it's findable. (Ingested first as a pipeline page; reclassified to `analysis/` per maintainer review, 2026-07-06.)

## What it is

Two exploratory Jupyter notebooks (synced to `.md` via jupytext, run manually, on-demand, no CI/CD) that build a crosswalk between CERF allocations and IBTrACS tropical-cyclone identifiers:

- **`cerf_sid_matching.ipynb`** — the core task: pull CERF Storm/Rapid-Response allocations from the OneGMS API, load `storms.ibtracs_storms`, and hand-write each CERF `ApplicationCode` → IBTrACS `sid` match into a dict.
- **`cerf_api_excel_check.ipynb`** — a separate consistency check comparing the CERF OneGMS API against a CERF allocations Excel export.

It is not a framework (no trigger, windows, funding, or published doc) and not a pipeline (nothing scheduled, deployed, or persisted — no `.github/workflows/`, no Databricks job, correctly absent from `infrastructure/pipeline-registry.md`).

## What was analyzed / findings

**`cerf_sid_matching.ipynb`** — load CERF Storm/Rapid-Response applications from the OneGMS API (`https://cerfgms-webapi.unocha.org/v1/application/All.xml`, parsed by `cerf.load_cerf_applications()`), filtered to `EmergencyTypeName == "Storm"` and `WindowFullName == "Rapid Response"`; load `storms.ibtracs_storms` via `ocha_stratus.get_engine(stage="prod")`, filtered to `season >= 2006`; build lookup URLs for both (CERF allocation summary page, IBTrACS `ncics.org` storm page). The analyst then reads each allocation's `CN_Summary`, finds the matching cyclone on the IBTrACS by-year-by-basin browser, and adds an entry (`ApplicationCode -> sid`, or `None` if no TC match) to the hardcoded `new_cerfcode2sid` dict. Any code not yet in the dict is printed for triage.

- Result so far: **2 entries** in `new_cerfcode2sid` (`07-RR-SDN-13738`→`None`, `07-RR-DOM-13362`→`2007345N18298`) — an unfinished manual sample, not a completed crosswalk. The single resolved match is the analyst's own hand-work, not independently verified against IBTrACS.

**`cerf_api_excel_check.ipynb`** (separate, unrelated check) — loads the CERF `AllocationsByYear.xlsx` export (blob `cerf/AllocationsByYear.xlsx`, container `global`, via `stratus.load_blob_data`) and the OneGMS API in parallel, casts types (`CN_ERC_EndorsementDate`, `TotalAmountApproved`, `CN_AmountRequested`), and does an outer merge on `(Country, Amount in US$, Allocation date)` vs `(CountryName, TotalAmountApproved, CN_ERC_EndorsementDate)` for a test country (`Afghanistan`) to spot mismatches between the two CERF sources. Ends mid-exploration — no asserted conclusion recorded.

## Relation to frameworks

Standalone (`feeds: []`) — nothing consumes the crosswalk, which exists only as a notebook dict. Its nearest neighbour is the [`cerf-supplement`](../pipelines/cerf-supplement.md) work (`ocha-dap/ds-cerf-supplement`), which performs the same CERF-allocation ↔ IBTrACS-`sid` annotation but persists to blob (`global/dev/cerf/cerf_supplemental_data.parquet`). Whether any matches from these notebooks were carried into `ds-cerf-supplement` is not evidenced in either repo (see the `[conflict]` discrepancy). Upstream, it reads `storms.ibtracs_storms` from [`storms-pipeline`](../pipelines/storms-pipeline.md) (Databricks `Run IBTrACS` job `638351145729392`, **currently failing every run** — so the storm table may be stale; check `infrastructure/pipeline-registry.md` before trusting the storm list).

## Sources & status

Repo `ocha-dap/ds-ibtracs-matching`, branch `cerf-notebook` @ `ab93116` (see `code_ref`). Runs under Python ≥3.11.4 with `uv`; deps `ocha-stratus>=0.1.7` (prod DB engine + blob read), `openpyxl>=3.1.5` (Excel), `matplotlib` (declared, not visibly used), and `requests` (transitive, no timeout — see discrepancies). Env vars for `stage="prod"` DB/blob access are inherited from shared `ocha-stratus` config, not set in this repo.

**Dormant**: only 2 hand-matched entries exist, nothing is persisted, and the overlapping `ds-cerf-supplement` app appears to cover the same task with real output — no evidence this notebook repo is actively used. Re-running from a fresh checkout reproduces only the 2 hardcoded entries; any further matching lives in an analyst's local notebook edits until committed.
