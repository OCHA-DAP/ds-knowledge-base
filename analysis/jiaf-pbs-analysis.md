---
content_type: analysis
name: jiaf-pbs-analysis
analysis_type: exploratory
status: one-off
country_iso3: CAF
hazard: needs-analysis
summary: "One-off methods comparison for aggregating JIAF multi-sector severity into a single overall PiN-by-severity figure for the CAR 2025 JIAF2 cycle; not an AA framework or pipeline."
data_sources: [JIAF, CODAB]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-jiaf-pbs-analysis
source_branch: caf-analysis
source_sha: 82bd45e
code_ref: [exploration/caf_jiaf.md, exploration/codab.md, src/datasources/jiaf.py, src/datasources/codab.py]
depends_on: []
discrepancies:
  - "[gap] exploration/caf_jiaf.md ends after the sector/severity comparison plots with no concluding cell or written recommendation — the six aggregation methods are compared visually but no method is selected as final."
  - "[gap] exploration/codab.md loads and plots CAF admin boundaries but is never joined back to the JIAF severity table in the visible notebooks — its role (mapping candidate) is inferred, not shown."
  - "[gap] src/datasources/jiaf.py has no download function — the source workbook ('CAR PiN and Severity Worksheet .xlsx') must have been uploaded to blob by hand; there is no record in the repo of when or by whom."
extra: {}
visibility: internal
last_synced: 2026-07-08
---

# JIAF PiN-by-Severity analysis (CAR) — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

Analytical support for the **2025 JIAF 2.0 PiN-by-Severity workstream** in the Central African Republic (CAR/CAF) — a one-off methodological exercise, not an anticipatory-action framework or a living pipeline. The JIAF (Joint Intersectoral Analysis Framework) 2.0 methodology classifies population severity per sector (education, health, WASH, nutrition, etc.) and per admin area, but leaves open *how* to collapse those several sector-severity distributions into one overall PiN (People in Need)-by-severity figure per area. This repo tests several candidate aggregation methods against the CAR JIAF worksheet and visualizes how much each changes the national PiN-by-severity total. It is not a framework because there is no trigger, hazard, or CERF-financed AA envelope involved at all — it is humanitarian-needs-assessment methodology, not anticipatory action. It is not a pipeline because nothing runs on a schedule: there are two exploratory notebooks, one frozen input file, and no CI/workflow files in the repo (`find … -name "*.yml"` turns up only `.pre-commit-config.yaml`).

## What was analyzed / findings

The core notebook, `exploration/caf_jiaf.md`, loads the CAR JIAF sectoral-severity worksheet (`src/datasources/jiaf.py::load_jiaf_sectoral_severity`, which parses the multi-header "3.3 PiN par gravité" sheet into a tidy `ADM2_PCODE × sector × severity → pop_count` table) and, per ADM2, compares **six methods** for collapsing per-sector severity distributions into one overall severity distribution:

- **Method 2** — take the sector with the maximum PiN (severity ≥ 3) and use its full severity distribution for the area.
- **Method 3** — for each severity level independently, take the max across sectors (i.e. the sector driving that specific severity level, which can differ level-to-level).
- **Method 4a/4b** — mean population count across sectors per severity level, with vs. without zero-count sectors included.
- **Method 4c/4d** — median population count across sectors per severity level, with vs. without zero-count sectors included.

Findings are presented as stacked bar charts of national total PiN by severity (3/4/5) across the six methods, first "ignoring the total PiN constraint" (methods disagree on the row-sum total) and then with an explicit adjustment forcing each method's total back to a reference total PiN (derived from Method 2, severity ≥ 3). A further pair of charts shows which **sector** drives the selected severity per ADM2 under Methods 2 vs. 3, and the national PiN-by-severity breakdown per sector. The notebook stops after these comparison plots — there is no concluding cell or written recommendation of which method to adopt; it is a comparison, not a decision record.

`exploration/codab.md` is a short support notebook that downloads and plots the CAF admin boundaries (via `src/datasources/codab.py`, FieldMaps CODAB) — useful for a future choropleth of the severity results, but it is not joined to the JIAF table anywhere in the visible code.

## Relation to frameworks

Standalone — `feeds: []`. This is JIAF/HNO needs-assessment methodology, unrelated in substance to any AA trigger design. The only other CAR/CAF-focused KB page is [analysis/caf-flooding](caf-flooding.md) (pre-development flood-hazard scoping in a different repo, `ds-aa-caf-flooding`) — there is no functional overlap; they happen to share a country, not a workstream.

## Sources & status

- **Repo:** `ocha-dap/ds-jiaf-pbs-analysis`, active branch `caf-analysis` (sha `82bd45e`). No README beyond dev-setup instructions; the substance is only in the two notebooks under `exploration/`.
- **Data:** the JIAF worksheet ("CAR PiN and Severity Worksheet .xlsx", sheet "3.3 PiN par gravité") is loaded from Azure Blob at `ds-jiaf-pbs-analysis/raw/jiaf/` (dev stage, container `projects`) — there is no downloader for it, so it is a frozen, manually-uploaded extract of unknown vintage. CAF admin boundaries are pulled from FieldMaps (`https://data.fieldmaps.io/cod/originals/caf.shp.zip`) and cached to blob at `ds-jiaf-pbs-analysis/raw/codab/caf.shp.zip` (dev stage) via `src/datasources/codab.py`.
- **Completeness:** the aggregation-methods comparison is fully worked (six methods, both unconstrained and PiN-constrained views); no final method selection, no write-up, and no downstream use of the boundary data are present in the repo.
- **Status:** `one-off` — scoped to the 2025 JIAF2 CAR PiN-by-severity workstream, single branch, no schedule, no deployment. Treat as dormant unless a future JIAF cycle explicitly revives it.
