---
content_type: analysis
analysis_type: pre-framework   # exploratory | ad-hoc-activation | pre-framework | regional-overview
feeds: []   # framework(s) this analysis supports
framework: caf-flooding
version: pre-development
status: pre-development
country_iso3: CAF
hazard: flood
admin_level: 3
geographic_scope: []
data_sources: [ERA5, OCHA-impact-data]
trigger_facets:
  basis: null
  calibration: null
  indicators: []
  n_windows: 0
  window_axes: []
supersedes: null
# --- funding & scope ---

prearranged_funding_usd: null
funding_by_source: {}
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: []
target_people: null
# --- documents, authority-ranked ---
framework_doc: null
framework_doc_date: null
framework_doc_annexes: []
languages: [fr]
model_report: null
raw_extract: []
# --- live system ---
operated_by: null
apps: []
depends_on: []
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-caf-flooding
source_branch: initial-analysis
source_sha: 51dc29d
code_ref: [exploration/ocha_impact.ipynb]
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No trigger logic exists anywhere in the repo — the README explicitly states 'Not currently for an anticipatory action framework'. The sole notebook is exploratory impact-data analysis, not a trigger design."
  - "[gap] No framework PDF found on ReliefWeb, OCHA publications, or CERF portfolio (as of Nov 2024 CERF update, CAF is not listed). The framework is not endorsed or published."
  - "[gap] No datasource modules in src/datasources/ — the directory is empty. Only ERA5 (country-level, from DB) and OCHA flood-impact Excel (from blob) have been loaded so far."
  - "[stale] setup.cfg (Feb 2024, predates both commits) is a leftover setuptools config naming the package 'src'; it is superseded by pyproject.toml, which names the project 'ds-aa-caf-flooding'. Not used by the live uv/pyproject build — informational."
  - "[stale] The live impact source is named '...DATA_COMPIL_2023OLDOK.xlsx' — the 'OLD' / 'OK' / '2023' tokens suggest it is a hand-versioned file, yet it carries 2021-2025 data. The filename is misleading but it is the file the notebook actually loads."
  - "[gap] exploration/ocha_impact.ipynb cell 46 is incomplete: 'df_impact_adm3_year = df_impact_adm3_year.merge()' is missing its right-hand frame, so the adm3-by-year aggregation pipeline does not run end-to-end as committed. Work-in-progress."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "n_windows is 0 because no trigger windows exist — this is pre-development. The trigger_facets block is intentionally empty."
  repo_note: "The exploration notebook correlates ERA5 monthly precipitation with OCHA flood-impact data (individuals affected, 2021-2025) at national and adm3 level. Strongest correlation is with cumulative annual ERA5 (r~0.97). This is scoping/hazard-characterisation work, not a trigger."
  impact_data_blob: "ds-aa-caf-flooding/raw/ocha/OCHA CAR_DONNEES-INONDATIONS_DATA_COMPIL_2023OLDOK.xlsx (sheet: DATA FOR PBI; 226 rows, 2021-2025)"
  zones: "[BANGUI-SUD, SUD-EST, OUEST, CENTRE, CENTRE-EST] — the ZONE column in the impact Excel, likely corresponding to informal OCHA operational zones rather than official pcodes."
visibility: internal
last_synced: 2026-06-17
---

# Central African Republic Flood — pre-development

> **Analysis, not a framework** (reclassified 2026-06-17): early analysis; the repo states it is not yet an AA framework. Page retains framework-style structure from its initial ingest; treat it as the analysis record.

> There is no published AA framework for this entry. This page documents the pre-development data-exploration work in the repo. The canonical reference is the notebook at `code_ref`; this page explains what has been done, not a trigger design.

## Summary

The Central African Republic (CAF) flood anticipatory action work is in the earliest scoping phase. As of January 2026 the only deliverable is a single exploratory notebook (`exploration/ocha_impact.ipynb`) that correlates country-level ERA5 precipitation with OCHA flood-impact records (individuals affected, 2021–2025). No trigger has been designed, no framework document exists on ReliefWeb or OCHA publications, and the repo README explicitly states the analysis is "not currently for an anticipatory action framework." CAF does not appear in the CERF anticipatory action portfolio (as of the November 2024 CERF Advisory Group update).

## Method

The notebook performs the following scoping steps:

1. Loads country-level ERA5 monthly precipitation from the production database (`public.era5`, pcode = 'CF').
2. Loads OCHA flood-impact data from blob storage (`ds-aa-caf-flooding/raw/ocha/OCHA CAR_DONNEES-INONDATIONS_DATA_COMPIL_2023OLDOK.xlsx`), covering 226 impact events from 2021 to 2025 across ~80 communes.
3. Geocodes impact records to adm3 boundaries (FieldMaps CODAB, 175 adm3 units) using name-matching with manual overrides.
4. Computes monthly and annual totals of individuals affected, then correlates these with ERA5 monthly individual and cumulative precipitation.
5. Produces spatial maps of total impact by adm3 and adm1 (prefecture) across the 2021–2025 period.

Key finding: cumulative annual ERA5 precipitation correlates strongly with annual flood impact (r ≈ 0.97), while individual month correlations are weaker. The highest-impact prefectures are Ombella-M'Poko and Bangui (capital region).

## Trigger logic

No trigger has been designed. There is no threshold, lead time, return-period calibration, or decision rule. All components are absent.

- **Keys off:** (not determined)
- **Decision rule:** none
- **Activation structure:** none
- **Calibration:** none
- **Authoritative source:** none — no framework PDF exists
- **Operated by:** n/a

## Trigger windows

No trigger windows exist. This framework is in pre-development.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| (none) | — | — | — | — | — | — |

## Sources & repo completeness

- **Trigger taken from:** repo (no framework doc exists)
- **Repo completeness:** partial — the hazard-characterisation (impact-data) analysis is present but a trigger design, model, and calibration are absent. The `src/datasources/` directory is empty.
- **Discrepancies:** See frontmatter `discrepancies` list. The key fact is that no trigger exists anywhere and no PDF has been published.

## Monitoring

No monitoring pipeline exists. There are no deployed apps, no scheduled jobs, and no companion repos. The repo has two commits.

## Historical activations

Never activated. No framework has been endorsed, so no activation is possible.

## Key decisions & rationale

The scoping notebook establishes that ERA5 cumulative annual precipitation is a plausible candidate indicator for a future trigger: the ~0.97 correlation with total individuals affected annually suggests the rainfall signal is strong at the national level. The highest-impact areas identified (Ombella-M'Poko, Bangui, Ouham prefectures) are candidate geographic scopes for a future framework. No design decisions have been taken.

## Changes from previous version

No previous version exists. This is the initial scoping entry.

## Open questions / known issues

- Is this analysis intended to eventually support a CERF-backed AA framework, or is it purely internal scoping? The README's disclaimer ("Not currently for an anticipatory action framework") suggests the latter.
- What forecast data source would be used for an actual trigger? ERA5 is observational; a forecast-based trigger (e.g., SEAS5 seasonal rainfall outlook, or GloFAS river discharge) would be needed.
- The impact data (`OCHA CAR_DONNEES-INONDATIONS_DATA_COMPIL_2023OLDOK.xlsx`) covers only 2021–2025 — too short for robust return-period calibration.
- adm3-level geographic scope: Bangui arrondissements (adm3) are mapped but the ZONE field in the impact data (BANGUI-SUD, OUEST, etc.) does not correspond to official pcode boundaries.
- The notebook has one incomplete cell (`df_impact_adm3_year = df_impact_adm3_year.merge()` missing the `right` argument), indicating work-in-progress state.
