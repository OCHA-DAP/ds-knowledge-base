---
content_type: analysis
name: bsgi-support
analysis_type: other
status: dormant
country_iso3: UKR
hazard: conflict
summary: "AIS/MarineTraffic vessel-tracking support for OCHA's Black Sea Grain Initiative (BSGI) Support Office — maps and animates ship arrivals/departures at Greater Odesa; a one-off IM/reporting exercise, not an AA trigger analysis."
data_sources: [MarineTraffic, UNGP-AIS, IHO-sea-areas]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-bsgi-support
source_branch: initial-exploration
source_sha: a8c60d2
code_ref:
  - README.md
  - exploration/query_ais.md
  - exploration/marinetraffic.md
  - exploration/blacksea_plot.md
  - exploration/animation.md
  - exploration/ais.md
  - src/datasources/iho.py
  - src/datasources/marinetraffic.py
  - src/datasources/ungp.py
  - src/utils/blob.py
  - migrate_blob.py
depends_on: []
discrepancies:
  - "[gap] exploration/ais.md is an empty stub — it installs a private AIS python package (GitLab code.officialstatistics.org, read-only AIS Task Team token) and opens a Spark session, but performs no analysis beyond that."
  - "[gap] No notebook or README states a finding, threshold, or conclusion — the repo is entirely descriptive/visualization tooling (query, validate, plot, animate), not an analytical write-up."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Black Sea Grain Initiative (BSGI) support — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-bsgi-support` is a small, one-off data-engineering/visualization toolkit built to support OCHA's **BSGI Support Office** (the team backing the Black Sea Grain Initiative — the UN-brokered trilateral arrangement that enabled Ukrainian grain exports through Black Sea shipping corridors during the Russia-Ukraine war) with its 2024 reporting and information management. Note the timeline: the BSGI itself ran 1 Aug 2022 – 17 Jul 2023, when Russia withdrew and all corridor activity was halted; the analyzed window here is **March 2024**, so the vessel traffic it maps is *post*-BSGI Black Sea shipping (via Ukraine's unilateral maritime corridor), even though OCHA's support office retained the BSGI name. It reconstructs and visualizes vessel (ship) traffic in and out of the Greater Odesa area from AIS (Automatic Identification System) positional data, cross-referenced against commercial MarineTraffic port-call exports. It is not a framework — there is no trigger, no threshold, and no anticipatory-action decision logic anywhere in the repo; it is purely descriptive mapping/animation support for an operational IM/reporting need, built around a single frozen data snapshot rather than a recurring pipeline.

## What was analyzed / findings

The repo has no write-up of conclusions — it is a chain of processing/plotting notebooks (jupytext `.md` pairs under `exploration/`), each doing one mechanical step:

- **`marinetraffic.md`** (`src/datasources/marinetraffic.py::mt_export_to_jupyter_csv`) — takes a raw MarineTraffic "Arrivals/departures" export CSV (e.g. `MarineTraffic_Arrivals_departures_Export_2024-03-06.csv`) and reshapes it into per-day MMSI (vessel ID) lists, to drive the date-by-date AIS query batches downstream.
- **`query_ais.md`** — the core extraction step. Runs in a PySpark/Spark-backed notebook (a `spark` session is assumed to exist, e.g. Databricks), reads the MarineTraffic export for the **Greater Odesa area, arrivals/departures 2024-03-01 to 2024-03-10, vessels >1 DWT**, and for each date pulls matching AIS pings from the UN Global Pulse (UNGP) historical archive (±3 days around arrivals, ±30 days around departures). It classifies each vessel's voyage as `ARRIVAL` / `DEPARTURE` / `INTERNAL` (both an arrival and departure in-window) and uploads the joined AIS+port-call table back to blob storage.
- **`blacksea_plot.md`** (`src/datasources/iho.py`) — loads the IHO Sea Areas shapefile, isolates the Black Sea + Sea of Azov polygons (ids `30`/`31`), builds a 50 km buffer, and spatially flags which AIS points fall inside vs. outside that buffer as a simple validity/sanity check (static matplotlib scatter, blue = in, red = out).
- **`animation.md`** (`src/datasources/ungp.py::process_ungp`) — applies a two-pass speed filter (flags a point invalid if both its incoming and outgoing implied speed exceed 25, and any `(0,0)` coordinate), resamples each vessel's track to 6h (animation frames) and 2h (line tracks), and renders an animated Plotly `scattermapbox` of arrival (orange) vs. departure (blue) vessel movement around Odesa. Output is a static HTML file checked into `plots/` (`greater-odesa-arrivals-departures-2024-03-01-2024-03-10-more-than-1-dwt_ais_processed_plot.html`).
- **`ais.md`** — an **empty stub**: installs a private `ais` Python package from a GitLab "Trade Task Team" repo using a personal read-only token, and opens a Spark session, but does nothing further.

No candidate triggers, thresholds, or comparisons are explored — this is entirely reporting/QA tooling for a single fixed window of shipping activity, not trigger design.

## Relation to frameworks

Standalone (`feeds: []`). This is not pre-figuring or feeding any AA framework or living pipeline in the KB — it supports OCHA's own BSGI reporting/IM function directly, outside the AA framework portfolio. There is no obvious KB neighbour; the closest thing structurally is `ibtracs-matching.md` (another one-off analysis repo doing data reconciliation rather than trigger design), but the hazard/subject matter is unrelated.

## Sources & status

- **Repo**: `ocha-dap/ds-bsgi-support`, branch `initial-exploration` @ `a8c60d2`.
- **Data**: commercial **MarineTraffic** port-call exports (manual CSV, e.g. `MarineTraffic_Arrivals_departures_Export_2024-03-06.csv`); **UN Global Pulse (UNGP)** historical AIS archive at `s3a://ungp-ais-data-historical-backup/exact-earth-data/transformed/prod/` (partitioned `year=/month=/day=`, read via Spark); **IHO Sea Areas** shapefile (Black Sea/Azov polygons) for spatial filtering. Raw/processed AIS extracts stage in an Azure Blob container `bsgi` on `imb0chd0dev.blob.core.windows.net` (SAS-token auth via `BSGI_CONTAINER_SAS`, `src/utils/blob.py`) under `raw/marinetraffic/`, `raw/ungp/`, `processed/ungp/`; IHO shapefiles and other inputs sync locally from a SharePoint folder (`OCHA BSGI Support Office / 2024 / Reporting and IM / Data`) via the `BSGI_DATA_DIR` env var. `migrate_blob.py` is a one-off script to pull the whole blob container down locally.
- **Freshness**: nothing refreshes automatically — the entire analysis is scoped to a single fixed window (MarineTraffic export dated 2024-03-06, AIS query 2024-03-01–2024-03-10). No schedule, no CI, no deployed app.
- **Completeness**: partial — `ais.md` is an unfinished stub (see discrepancies); the rest of the chain (fetch → validate → plot/animate) is functional but was run once against one snapshot.
- **Status**: `dormant` — frozen single-window inputs, no scheduling, and no further commits building on the exploration branch beyond this initial pass.
