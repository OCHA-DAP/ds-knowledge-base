---
content_type: pipeline
name: cems-flood-archive
type: dataset-ingest
status: live
deployment:
  platform: manual
  resource_group: null
  jobs:
    - { name: "discovery/harvest/silver/gold (pipelines/cems_flood/*)", ref: "ocha-dap/ds-geospatial-impact-estimates", schedule: on-demand, status: live }
inputs:
  - "CEMS archive portal API — https://mapping.emergency.copernicus.eu/activations/api/activations/ (all activations 2012+)"
  - "CEMS archive activation pages (server-rendered HTML) -> product zips on cems-mapping-website S3 (EMSR001-655)"
  - "CEMS new-portal dashboard API via ocha-lens (EMSR656+, Mar 2023+; per-image acquisitionTime)"
outputs:
  - "blob global/copernicus_ems/flood/bronze/code={EMSRnnn}/*.zip (2,884 original product zips, 31.5 GB, sha256-verified; stage: dev)"
  - "blob global/copernicus_ems/flood/bronze/_meta/ (products.parquet ledger incl. explicitly-unavailable targets, zip_contents.parquet, transfers.jsonl, activations.parquet, archived JRC manual + data-model docs)"
  - "blob global/copernicus_ems/flood/silver/{observed_event,coverage,sources}/code=*/data.parquet (4.14 M flood polygons, all five CEMS naming eras normalized; per-polygon acquisition datetime 91% minute/date precision)"
  - "blob global/copernicus_ems/flood/gold/label_index.parquet (2,715 ML label sets: bbox, day, sensor, method, area) + gold/labels/code=*/data.parquet (dissolved flood extent + valid mask per acquisition, 3.6 GB)"
surfaces: []
dependencies:
  - ocha-lens
  - ocha-stratus
  - "gie.blobio / gie.config (host repo)"
downstream:
  - "university ML collaboration (flood-label training data: FloodScan/GFDS/GFM/VIIRS fusion)"
depends_on:
  - ocha-lens
source_repo: ocha-dap/ds-geospatial-impact-estimates
source_branch: cems-flood
code_ref:
  - "pipelines/cems_flood/README.md (ops + diagrams)"
  - "pipelines/cems_flood/ACQUISITION.md (every endpoint, provenance)"
  - "pipelines/cems_flood/DATA_DICTIONARY.md (all columns, CEMS-native definitions per JRC121741)"
extra: {container: "global (NOT projects) — general historical corpus, not event-scoped"}
visibility: internal
last_synced: 2026-09-03
---

# CEMS flood archive (bronze/silver/gold label corpus)

## One-liner
One-time (plus backfill) harvest of **every Copernicus EMS Rapid Mapping flood
activation 2012→present** into blob, harmonized into ML-ready flood-extent
labels with per-polygon imagery acquisition timestamps.

## What it is
302 flood activations (EMSR009–EMSR927), 2,884 product zips archived
byte-identical (bronze), 4.14 M extent/coverage polygons normalized across
five CEMS schema eras (silver), and a two-table label system (gold):
`label_index` (2,715 sets; sampling catalog, no geometry) + `labels`
(dissolved flood extent + valid mask = footprint ∩ AOI − not-analysed).
Container **`global`**, dev stage: `copernicus_ems/flood/{bronze,silver,gold}`.

## Non-obvious facts (the tribal knowledge)
- CEMS history needs **two portals**: ocha-lens's backend serves only
  EMSR656+ (2023+); pre-2023 comes from the archive portal API + HTML pages.
  Both need a browser-ish User-Agent (default python UA → 403).
- Acquisition datetimes come from a **geometry-less `source` DBF** inside
  every 2017+ package (`dmg_src_id` → `src_id` join, minute precision);
  2012–16 carries per-feature `src_date`. Don't scan `.shp` members only.
- Upstream **loses data**: 7 legacy activations never migrated, 2 S3 objects
  are HTML-as-zip, 2 advertised URLs 404. All recorded in the bronze ledger
  (`products.parquet`) with explicit statuses — absence is data, not error.
- ~68 % of modern label imagery is SAR (S1 27 %) — GFM-circularity is
  flaggable via `sources`; label-quality tiering ingredients (sensor, gsd,
  det_method) ship in `label_index` rather than a baked tier.
- Monitoring products may report **cumulative** extent (JRC manual §3.2.9);
  a shrinking series proves snapshots.

## Runbook
```sh
uv run --group etl --group api python pipelines/cems_flood/discovery.py       # refresh ledger (backfill)
uv run --group etl --group api python pipelines/cems_flood/harvest.py         # transfer new zips (resumable)
uv run --group etl --group api python pipelines/cems_flood/silver.py          # harmonize (parallel, resumable)
uv run --group etl --group api python pipelines/cems_flood/gold.py            # rebuild label tables
uv run --group etl --group api python pipelines/cems_flood/audit.py           # invariants; emits stale-code list
uv run --group etl --group api python pipelines/cems_flood/inspect_labels.py --overview --codes EMSRnnn  # sense-check maps
```
Needs the host repo's `.env` (`DSCI_AZ_BLOB_*`). Defect-fix loop and all
design decisions: repo `pipelines/cems_flood/README.md` + ADR-0029.

## Failure modes
- Blob store is the resume truth; kill anything anytime, rerun resumes.
- Serial passes are single-stream network-bound from a laptop (~1.6 MB/s) —
  use `--workers`; long passes belong in Azure compute (open proposal).
- New CEMS naming era / status value ⇒ loud failure by design; fix pattern,
  run `audit.py`, reprocess the emitted stale list.

## Downstream consumers
University ML collaboration (flood labels for FloodScan/GFDS/GFM/VIIRS
fusion model). Sharing route: read-only SAS on `global/copernicus_ems/flood/`
(gold ≈ 3.6 GB + index < 1 MB).
