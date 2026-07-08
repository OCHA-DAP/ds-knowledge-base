---
content_type: analysis
name: sdn-displacement-analysis
analysis_type: exploratory   # exploratory | ad-hoc-activation | pre-framework | regional-overview
status: one-off
country_iso3: SDN
hazard: conflict
summary: "One-off R scenario-building analysis for the April 2023 Sudan conflict/displacement crisis (DTM + ACLED + UNHCR) supporting HRP planning; no trigger, no framework, no schedule."
data_sources: [IOM-DTM, ACLED, UNHCR, OCHA-CODs]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-sdn-displacement-analysis
source_branch: main
source_sha: ec5eb93
code_ref: ["01_wrangle.R", "02_plotting.R"]
depends_on: []
discrepancies:
  - "[gap] No return-period, threshold, or trigger logic anywhere in the repo — this is descriptive scenario visualization for HRP/crisis planning, not AA trigger design. Confirms the analysis_type/status classification, not a defect."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Sudan displacement (2023 conflict) — analysis

> **Analysis, not a framework.** There is no published framework doc, no trigger, and no AA portfolio entry for Sudan in this KB. This repo is a one-off, ad hoc R analysis built during the April 2023 Sudan conflict to support displacement scenario-building for humanitarian planning — captured here so the work is findable.

## What it is

`ds-sdn-displacement-analysis` is a two-script R analysis built to support displacement scenario building during the 2023 Sudan conflict. It wrangles and cross-walks several independently-sourced Sudan datasets — IOM DTM displacement snapshots and DTM-provided forecast scenarios, ACLED conflict events, UNHCR refugee outflow figures, and OCHA administrative-boundary pcodes — into a common admin1/admin2 pcode structure, then produces a series of charts comparing early crisis-scenario projections against observed displacement. It is not a framework or a living pipeline: there is no trigger, no forecast-driven decision rule, no schedule, and no deployment — it is a reactive, descriptive exercise built for one crisis moment (outputs went to [a private Google Slides deck](https://docs.google.com/presentation/d/1XctpKpO0mYZIlNu84wqR4Ze4bYHm8YsvGCqWH8vsPIY/edit) for OCHA Sudan / IOM DTM), not a pre-framework trigger-design effort.

## What was analyzed / findings

**`01_wrangle.R`** — data assembly and admin-pcode reconciliation:
- Loads OCHA admin1/admin2 boundary tabular data (`sdn_adminboundaries_tabulardata.xlsx`) as the pcode reference, with a manual fix for the duplicate-named "Ar Rahad" locality (Gedaref vs North Kordofan).
- Pulls ACLED conflict events for Sudan from 2023-01-01 to present via `{acled.api}` (env vars `ACCESS_KEY`/`EMAIL_ADDRESS`), filtered to Battles, Violence against civilians, and Explosions/remote violence, then hand-maps ~15 ACLED admin1/admin2 name variants (e.g. "Al Jazirah" → "Aj Jazirah", "El Geneina" → "Ag Geneina") onto OCHA pcodes.
- Reads a DTM-provided "Scenarios (DTM Sudan locality).xlsx" workbook with 3 named scenarios, each spanning adm0/adm1/adm2 levels in one sheet (level inferred from Excel cell formatting via `{tidyxl}`), pivoted long by forecast month — the raw material for the worst-case/status-quo/best-case IDP trajectories.
- Reads a pre-crisis IDP/returnee baseline (HNO round 6, "MT R6-IDPs & Returnees PRE CRISES.xlsx") as the reference point for "% of pre-crisis" comparisons.
- Wrangles **23 successive DTM displacement snapshot workbooks** (27 Apr 2023 → 8 Oct 2023 — DTM situation reports through mid-Aug, then later weekly displacement snapshots), each with a different, hardcoded layout (header row 1 vs 2, hex-coded vs named columns, ~25 column-name variants for state/locality pcodes at origin vs displacement and idps/hhs counts) into one long panel of IDP/HH counts by date × admin2 × displacement-vs-origin location.
- Reads UNHCR refugee outflow figures from a CSV.
- Reads an updated post-September-2023 "IDPs by locality" scenario annex (one sheet per scenario, ~7 monthly values each spanning Sep 2023–Feb 2024), a later refresh of the original DTM scenarios.

**`02_plotting.R`** — scenario/observed comparison charts (`{gghdx}` styling):
- National displacement: initial (May 2023) worst/status-quo/best-case scenario lines vs. observed cumulative DTM displacement.
- Daily % growth rate of observed displacement vs. three parametrized compounding growth-rate scenarios (0.7×/1.2×/1.35× monthly).
- ACLED conflict events and fatalities per day (log scale for fatalities).
- Per-state IDP trajectories, calling out states with distinct patterns (East Darfur, River Nile rising; West Darfur, Northern declining).
- Latest DTM state-level IDP counts as a % of pre-crisis IDP baseline, by state.
- The September-2023 refreshed scenario annex re-plotted against observed data (worst/status-quo/best case of 10M/7.5M/3M nationally by March 2024).
- A hand-built illustrative "reduction / leveling / linear" continuation of displacement built from jittered synthetic deltas layered onto the last observed DTM point — an explicit what-if sketch, not a fitted model or forecast.

No return period, threshold, or trigger logic appears anywhere — this is pure descriptive/scenario visualization to support HRP planning during an unfolding conflict, not anticipatory-action trigger design.

## Relation to frameworks

Standalone (`feeds: []`). Sudan has no AA framework and no entry in the OCHA/CERF AA portfolio represented in this KB, and this repo does not derive or pre-figure a trigger for one — it is reactive crisis-response scenario support, not anticipatory. The closest KB neighbours are the other conflict/crisis- or displacement-adjacent `analysis/` pages (e.g. `caf-flooding`, `cod-flooding`) in that all are one-off or pre-development repos with no endorsed framework, though those are hazard (flood) exploration aimed at an eventual trigger, while this one is purely reactive scenario-building with no forward trigger intent.

## Sources & status

- **Repo:** `ocha-dap/ds-sdn-displacement-analysis`, single branch (`main`), two R scripts (`01_wrangle.R`, `02_plotting.R`) plus a `README.md`. No `exploration/`, `src/`, tests, or CI.
- **code_ref:** `01_wrangle.R` (data assembly), `02_plotting.R` (`source()`s `01_wrangle.R`, then builds the charts).
- **Data staging:** entirely local/manual — all inputs read from and outputs written to `$SDN_DISPLACEMENT_DIR/2023_displacement/data/{input,output}` (an `.Renviron`-configured drive path, not Azure blob or the project DB). Nothing in the repo refreshes these; the analysis is a fixed snapshot of 2023 files.
- **Frozen inputs:** DTM displacement snapshots dated 27 Apr 2023 – 8 Oct 2023 (23 files), the HNO round-6 pre-crisis baseline, a UNHCR refugee CSV through roughly mid-Aug 2023, and a September-2023 scenario annex projecting through March 2024. Nothing postdates early 2024.
- **Deployment/schedule:** none. No GitHub Actions, no Databricks job, no downstream DB writes or app. The only durable output is the linked private Google Slides deck plus local CSVs/PNGs.
- **Status:** **one-off** — built for the acute phase of the April 2023 Sudan conflict and not touched since; treat as a closed, dormant artifact rather than a live or resumable analysis.
