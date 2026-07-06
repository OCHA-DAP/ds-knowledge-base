---
content_type: analysis
name: sahel-flashflooding
analysis_type: pre-framework   # due-diligence data-gathering for a possible flash-flood AA framework
status: dormant                # manual extracts frozen 2024-11; no commits toward the branch's stated next step
country_iso3: [BFA, NER, TCD, NGA, CMR]
hazard: flood                  # flash flooding (Sahel + Lake Chad basin AOI)
summary: "Scoping notebooks for a possible multi-country Sahel/Lake-Chad flash-flood AA framework: CODAB boundaries + historical CERF flood allocations + EM-DAT flood events for BFA/NER/TCD/NGA/CMR. No trigger, no doc, nothing deployed — not (yet) a framework."
data_sources: [codab, cerf-allocations, emdat]
feeds: []                      # nothing consumes it yet; plausible groundwork for a future flash-flood framework
source_repo: ocha-dap/ds-sahel-flashflooding
source_branch: seasonal-forecasts
source_sha: 64e4c6c
code_ref:
  - src/datasources/codab.py
  - src/datasources/cerf.py
  - src/datasources/emdat.py
  - src/utils/blob_utils.py
  - src/constants.py
  - exploration/codab.md
  - exploration/cerf.md
  - exploration/emdat.md
depends_on: []
discrepancies:
  - "[stale] Manual CERF + EM-DAT extracts are frozen at 2024-11-22 and no code refreshes them — a re-run today analyses >1-year-old allocation/event data unless both spreadsheets are re-downloaded and re-staged by hand."
  - "[stale] Active branch is `seasonal-forecasts`, but no seasonal-forecast code (SEAS5/ECMWF/IRI or similar) exists anywhere in src/ or exploration/ — the name reflects an intended next step, not current content."
  - "[gap] `exploration/emdat.md` is an empty stub (loads the extract, one blank code cell) — the EM-DAT analysis was never written."
extra:
  aoi_note: "NGA and CMR are restricted to a Lake-Chad-basin AOI (Yobe/Borno/Adamawa; Extrême-Nord) via AOI_ADM1_PCODES — not whole-country."
  non_stratus_blob: "Uses raw azure-storage-blob via src/utils/blob_utils.py (PROD_BLOB_SAS/DEV_BLOB_SAS env vars) — predates/bypasses ocha-stratus, the current team convention. src/utils/db_utils.py wires a chd-rasterstats Postgres engine that nothing calls (dead code)."
  cerf_effective_year: "CERF loader derives an `effective_year` — an allocation dated before May is attributed to the previous year, aligning allocations with the rainy season that caused them."
visibility: internal
last_synced: "2026-07-02"
---

# Sahel Flash Flooding — analysis

> **Analysis, not a framework — and not a pipeline.** No published framework doc, no trigger logic, no schedule, no deployment, no DB/comms output. This is early pre-framework exploration, captured so the work is findable. (Ingested first as a pipeline page; reclassified to `analysis/` per maintainer review, 2026-07-06.)

## What it is

Manual, on-demand due-diligence for a possible **multi-country flash-flood AA framework** covering the central Sahel (BFA, NER, TCD) plus the Nigeria/Cameroon Lake Chad basin states: pull CODAB admin boundaries, historical CERF flood allocations, and EM-DAT flood events → stage in dev blob → eyeball plots in jupytext notebooks. It isn't a framework because none of the framework substance exists yet — no trigger design, no windows, no funding, no doc; it isn't a pipeline because nothing is scheduled or deployed (no `.github/workflows/`, no `databricks.yml`, no entrypoint — correctly absent from `infrastructure/pipeline-registry.md` and `deployments.md`).

## What was analyzed / findings

- **`exploration/codab.md`** — for each of the 5 ISO3s, `codab.download_codab_to_blob()` fetches the FieldMaps shapefile (`data.fieldmaps.io/cod/originals/{iso3}.shp.zip`) into dev blob (`projects/ds-sahel-flashflooding/raw/codab/`), then `load_all_codabs(admin_level, aoi_only=True)` concatenates them — with NGA/CMR cut to the Lake-Chad AOI (Yobe/Borno/Adamawa; Extrême-Nord). Output: a quick geometry plot of the AOI.
- **`exploration/cerf.md`** — `cerf.load_cerf()` reads a manually staged `AllocationsByYear_2024-11-22.xlsx`, filters to the 5 countries where `Emergency == "Flood"` and `Window == "Rapid Response"`, derives an `effective_year` (pre-May allocations → previous year, to align with the causal rainy season), and bar-charts CERF flood money by country/year — the "how often has CERF paid for floods here" scoping question.
- **`exploration/emdat.md`** — loads a manually staged EM-DAT Africa-floods extract; the analysis itself was never written (empty stub).

No conclusions/thresholds were recorded in the repo — the CERF-history scoping chart is the only substantive output so far.

## Relation to frameworks

Standalone (`feeds: []`). The closest neighbours are **`frameworks/bfa-flooding`** — a different, BFA-only *fluvial*-flood plan (PNAAI) triggered on SEAS5 seasonal rainfall, not flash floods — and the drought-focused **`analysis/sahel-drought`** regional overview. This repo's CERF-history and AOI scoping is plausible groundwork for a future flash-flood framework, but nothing currently consumes it.

## Sources & status

Repo `ocha-dap/ds-sahel-flashflooding`, branch `seasonal-forecasts` @ `64e4c6c` (see `code_ref`). **Dormant**: the two spreadsheet inputs are frozen point-in-time extracts from 2024-11-22 with no refresh code; the branch name promises seasonal-forecast work that hasn't started; the EM-DAT notebook is a stub. Re-running requires `DEV_BLOB_SAS`/`PROD_BLOB_SAS` env vars (raw `azure-storage-blob`, pre-stratus — see `extra.non_stratus_blob`) and a local Jupyter kernel; FieldMaps is fetched live with no retry, so a moved shapefile URL hard-fails.
