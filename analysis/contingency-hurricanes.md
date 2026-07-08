---
content_type: analysis
name: contingency-hurricanes
analysis_type: ad-hoc-activation
status: one-off
country_iso3: [JAM, VCT, GRD]
hazard: tropical-cyclone
summary: "Real-time CERF contingency check for Hurricane Beryl (Jul 2024) — compared Beryl's observed wind/rainfall against Haiti's historical CERF-activation scatter to gauge whether Jamaica/SVG/Grenada warranted a similar CERF contingency; frozen, single-storm, no schedule or deployment."
data_sources: [NHC, IMERG, CODAB, IBTrACS]
feeds: []
# --- source repo ---
source_repo: "ocha-dap/ds-contingency-hurricanes"
source_branch: "initial-analysis"
source_sha: "1b0b45e"
code_ref:
  - "exploration/codab.md"
  - "exploration/current_tracks.md"
  - "exploration/imerg_proc.md"
  - "src/datasources/nhc.py"
  - "src/datasources/codab.py"
  - "src/utils/blob.py"
  - "src/utils/raster.py"
depends_on: [storms-pipeline, imerg]
discrepancies:
  - "[stale] README says the scope is 'Jamaica and St. Vincent and the Grenadines' only, but exploration/codab.md, current_tracks.md and imerg_proc.md all download and process CODAB + IMERG for Grenada (grd) too, alongside jam/vct. Scope is really three countries, not two — the README was never updated when Grenada was added."
  - "[stale] codab.load_codab's type hint only allows Literal[\"jam\", \"vct\"], but it is called with \"grd\" in all three exploration notebooks (download_codab already allows \"grd\") — the load_codab annotation was never updated when Grenada was added, though the function works at runtime since Python doesn't enforce Literal types."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Contingency: hurricanes (JAM/VCT/GRD) — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-contingency-hurricanes` is a small, single-purpose repo ("CERF contingency: hurricanes" per its README) built to answer one live question during Hurricane Beryl in July 2024: given Beryl's track, wind, and rainfall as it passed the Eastern Caribbean, would a CERF anticipatory contingency be warranted for Jamaica, St. Vincent and the Grenadines, and Grenada? It is not a framework — there is no published framework doc, no trigger definition, and no endorsed threshold — and it is not a pipeline — there is no schedule, no deployment, nothing refreshes the inputs. It's a one-time, storm-specific piece of desk analysis: three short jupytext notebooks (`exploration/codab.md`, `current_tracks.md`, `imerg_proc.md`) and a handful of thin data-access helpers (`src/datasources/`, `src/utils/`), all hardcoded to a single named storm ("Beryl").

## What was analyzed / findings

- **`codab.md`** — downloads and loads CODAB admin-0 boundaries for Jamaica, St. Vincent and the Grenadines, and Grenada from FieldMaps (`https://data.fieldmaps.io/cod/originals/<iso3>.shp.zip`) and plots them. No analysis beyond a sanity-check plot.
- **`current_tracks.md`** — loads NHC observed-track data for Beryl (filtered to `basin == "al"`, `name == "Beryl"`), interpolates the track to 30-minute resolution, computes each country's distance to the storm over time, and for a sweep of distance thresholds (0–500 km, step 10) computes the max observed wind (`intensity`) within that threshold, per country (JM/VC/GD). This produces a simple "how close did it get, how strong was it at that distance" table per country — no threshold is picked or endorsed, the sweep is left as exploratory output.
- **`imerg_proc.md`** — the substantive comparison. For each day of Beryl's track, pulls the IMERG daily-late COG from blob, clips/upsamples it to each country's boundary, and computes mean areal rainfall. It then plots Beryl's max-wind (131 kt, `current_s`) and max-rolling-2-day rainfall (91 mm, `current_p`) as a single point against a **scatter of Haiti's historical CERF-activation storms** (Matthew, Ike, Gustav, Hanna, Fay, Sandy — read from `ds-aa-hti-hurricanes/processed/stats_{D_THRESH}km.csv` on blob, borrowed directly from the [hti-hurricanes](../frameworks/hti-hurricanes/) framework repo's processed outputs) to visually judge whether Beryl's impact signature was CERF-activation-scale by Haiti's own historical trigger geometry. The plot is explicitly annotated "(pour St-Vincent, pas pour Haïti)" — i.e. it's re-purposing Haiti's historical wind/rain-vs-impact relationship as a stand-in benchmark for SVG, since SVG/JAM/GRD have no such historical CERF-activation record of their own. No new threshold is derived; the conclusion is visual/comparative, not a fitted rule.

## Relation to frameworks

Standalone (`feeds: []`) — it does not feed any endorsed or in-development framework. It **borrows** the [hti-hurricanes](../frameworks/hti-hurricanes/) framework's historical impact/trigger scatter (`ds-aa-hti-hurricanes/processed/stats_20km.csv`) as an analogy benchmark, since none of JAM/VCT/GRD has its own historical hurricane-impact dataset or CERF trigger. It is also thematically adjacent to the [cub-hurricanes](../frameworks/cub-hurricanes/) framework (same wind+rainfall CERF-trigger design pattern for a Caribbean hurricane) and to the [hurricanes-monitoring](../pipelines/hurricanes-monitoring.md) pipeline (same NHC/IMERG inputs, same Caribbean proximity-monitoring idea) — but it is a separate, unscheduled, one-off repo, not a consumer or feeder of either. No JAM/VCT/GRD hurricane framework exists in the KB catalog today; this repo is the closest thing to pre-framework groundwork for one, though it was never picked back up.

## Sources & status

- **Repo**: `ocha-dap/ds-contingency-hurricanes`, active branch `initial-analysis` (sha `1b0b45e`). The repo has no `main`-vs-feature-branch split visible from the clone — everything lives on `initial-analysis`.
- **Data**: NOAA NHC observed/forecast tracks (`noaa/nhc/observed_tracks.csv`, `global` container, **dev** stage — written upstream by [storms-pipeline](../pipelines/storms-pipeline.md)); IMERG daily-late COGs (`imerg/v7/imerg-daily-late-<date>.tif`, `global` container, **dev** stage — written by the [imerg](../pipelines/imerg.md) pipeline); CODAB admin-0 boundaries for jam/vct/grd (pulled live from FieldMaps and cached to `ds-contingency-hurricanes/raw/codab/<iso3>.shp.zip` on the **dev** `projects` container); and a borrowed processed stats CSV from `ds-aa-hti-hurricanes`. All blob I/O uses raw `azure-storage-blob` `ContainerClient` + SAS tokens (`DEV_BLOB_SAS`/`PROD_BLOB_SAS` env vars) — not `ocha-stratus`, a deviation from team convention (see [conventions.md](../infrastructure/conventions.md)).
- **Completeness**: all three notebooks are filled in (not stubs), but are hardcoded to Beryl/2024 — no parametrization for a different storm, no re-run since. Nothing refreshes these inputs; the NHC/IMERG pulls are frozen at whatever was live during Beryl's passage in July 2024.
- **Status**: `one-off` / dormant in practice — built for a single real-time event, never generalized or revisited. Not deployed anywhere (no GHA workflow, no Databricks job, no entry in [deployments.md](../infrastructure/deployments.md)).
