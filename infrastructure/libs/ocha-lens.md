---
content_type: library
name: ocha-lens
status: active
purpose: "Reusable loaders and geometry utilities for tropical-cyclone datasources (IBTrACS, NHC, ECMWF-storm, GDACS, ADAM) used across OCHA DS storm pipelines"
language: python
source_repo: OCHA-DAP/ocha-lens
source_branch: main
source_sha: 8a80911
version: "0.5.1"
install: "uv add git+https://github.com/OCHA-DAP/ocha-lens.git@0.5.1"
auth_env:
  - DSCI_AZ_BLOB_DEV_SAS_WRITE
  - DSCI_AZ_BLOB_PROD_SAS_WRITE
key_api:
  - ibtracs.download_ibtracs
  - ibtracs.load_ibtracs
  - ibtracs.get_storms
  - ibtracs.get_tracks
  - nhc.download_nhc
  - nhc.load_nhc
  - nhc.get_storms
  - nhc.get_tracks
  - nhc.get_wsp
  - ecmwf_storm.download_forecasts
  - ecmwf_storm.load_forecasts
  - ecmwf_storm.get_storms
  - ecmwf_storm.get_tracks
  - gdacs.get_events
  - gdacs.get_timeline
  - gdacs.get_exposure_adm0
  - gdacs.get_exposure_adm1
  - gdacs.match_to_atcf
  - adam.get_events
  - adam.get_exposure
  - utils.storm.interpolate_track
  - utils.storm.calculate_wind_buffers_gdf
  - utils.storm.match_wsp_to_tracks
depends_on:
  - ocha-stratus
used_by:
  - pipelines/storms-pipeline
  - pipelines/storm-impact-harmonisation
visibility: public
last_synced: "2026-06-22"
---

# ocha-lens

Shared Python library of loaders and geometry helpers for the standard tropical-cyclone datasources used by OCHA Data Science storm pipelines. Each datasource module provides a consistent `download → load → get_storms / get_tracks` pattern; the `utils/storm` module provides the shared geometric primitives (wind buffers, track interpolation, antimeridian handling) that those pipelines consume.

Check it before writing custom TC data-loading or wind-buffer logic — if you are touching IBTrACS, NHC, ECMWF TIGGE, GDACS, or ADAM for storms, this library almost certainly has what you need.

## Summary

ocha-lens wraps five TC datasources under a common schema (pandera-validated DataFrames / GeoDataFrames, EPSG:4326, `valid_time`/`issued_time` column naming) and provides geometry utilities used by ds-storms-pipeline: quadrant-radius wind buffers, track interpolation, antimeridian-safe projections, and NHC WSP track matching. The package `__init__.py` exports the five datasource sub-modules directly — `ibtracs`, `nhc`, `ecmwf_storm`, `gdacs`, `adam` — so `import ocha_lens as lens; lens.ibtracs.get_tracks(...)`. The geometry helpers are **not** re-exported at top level; import them from their module: `from ocha_lens.utils.storm import calculate_wind_buffers_gdf`.

No auth is required at import time. The ECMWF-storm module can optionally write to Azure blob via `ocha-stratus` (when called with `stage="dev"`/`"prod"`); all other datasources fetch from public HTTP/FTP endpoints.

## Install & auth

```bash
# pin to a tag (the library is not on PyPI)
uv add git+https://github.com/OCHA-DAP/ocha-lens.git@0.5.1
```

Or in `pyproject.toml` / `databricks.yml` dependency list:

```
git+https://github.com/OCHA-DAP/ocha-lens.git@0.5.1
```

**Auth:** none required for most usage (the default stage is `"local"`). The `ecmwf_storm.download_forecasts`/`load_forecasts` functions can read/write raw cxml files to Azure blob when called with `stage="dev"`/`"prod"`; that path goes through `ocha-stratus`, so the relevant blob SAS env vars must be set — `DSCI_AZ_BLOB_DEV_SAS_WRITE` / `DSCI_AZ_BLOB_PROD_SAS_WRITE` (and the read SAS for loads). These are stratus's own variables; see [storage.md](../storage.md) for the full set. All other datasources use public unauthenticated endpoints (NCEI HTTPS for IBTrACS, NHC FTP/JSON for NHC, UCAR/RDA TIGGE for ECMWF, GDACS REST API, WFP ADAM API).

## Key API

Each datasource module follows the same shape; the geometry helpers live in `utils.storm`. Exact signatures change with the code — **for current signatures and defaults, see the [readthedocs reference](https://ocha-lens.readthedocs.io/en/latest/) or the module source** (`source_repo`). This is the orientation map, not the signature spec.

| Module | Pattern / entry points |
|---|---|
| `ibtracs` | `download_ibtracs` → `load_ibtracs` → `get_storms` / `get_tracks(track_type="best"\|"provisional"\|"all")`. NetCDF from NCEI. |
| `nhc` | `download_nhc` / `load_nhc` (current `CurrentStorms.json` vs archive ATCF A-deck, by `year`) → `get_storms` / `get_tracks`; `get_wsp` for wind-speed-probability footprints. |
| `ecmwf_storm` | `download_forecasts` / `load_forecasts` (TIGGE cxml; `stage` controls local vs Azure blob) → `get_storms` / `get_tracks` / `get_forecasts`. |
| `gdacs` | `get_events` → `get_timeline` (per-advisory positions/wind/exposure) → `get_exposure_adm0` / `get_exposure_adm1` (per-buffer impact rollups); `match_to_atcf` to attach an ATCF id. |
| `adam` | `get_events` (WFP ADAM TC events) → `get_exposure` (per-event population CSV, ADM0/1/2). |
| `utils.storm` | `interpolate_track` (PCHIP to a regular grid, antimeridian-safe), `calculate_wind_buffers_gdf` (merged 34/50/64 kt quadrant buffers, dateline-aware), `match_wsp_to_tracks` (NHC WSP ↔ ATCF tracks). |

**Shared schemas** (pandera, per module): `STORM_SCHEMA`, `TRACK_SCHEMA`, plus the wind-buffer/exposure schemas. Downstream pipelines import these to validate the data they write — see the module source for the full set per datasource.

## Used by

- **[pipelines/storms-pipeline](../../pipelines/storms-pipeline.md)** — primary consumer; pins `ocha-lens==0.5.1`. Uses IBTrACS, NHC, ECMWF-storm loaders and all geometry utilities (wind buffers, antimeridian, WSP matching)
- **[pipelines/storm-impact-harmonisation](../../pipelines/storm-impact-harmonisation.md)** — `source_diagnostics.py` imports `ocha_lens` (from the ds-storms-pipeline venv)

(`pipelines/glb-tropicalcyclones` lists ocha-lens as available but its page states it is **not currently used** — stratus's `datasources.codab` is used directly — so it is not a genuine consumer.)

## Gotchas & conventions

- **Not on PyPI** — always install from git with a pinned tag: `git+https://github.com/OCHA-DAP/ocha-lens.git@<tag>`. Floating `@main` will break reproducibility.
- **`BUFFER_SPEEDS = [34, 50, 64]` is the single source of truth** for wind thresholds across all modules. Import from `ocha_lens.utils.storm` — don't hardcode elsewhere. (The geometry helpers are not top-level exports; reach them via `ocha_lens.utils.storm`.)
- **Provisional vs best tracks**: IBTrACS provisional tracks contain USA-agency data only with different wind-averaging periods — don't mix with best-track wind speeds in the same analysis. `get_tracks(ds, track_type="all")` concatenates both; use `"best"` or `"provisional"` to separate them.
- **NHC archive mode vs current mode**: `load_nhc()` with no `year` argument fetches `CurrentStorms.json` (realtime, only active storms). Pass `year=` to load historical ATCF A-deck files via FTP. The FTP archive for the previous year may not be populated until spring — the module falls back to `aid_public/` for recent years.
- **Antimeridian**: `utils.storm.calculate_wind_buffers_gdf` projects through a basin-appropriate CRS (`EPSG:3832` for EP/WP/SP, `EPSG:3857` for NA/NI/SI/SA) and runs `antimeridian.fix_polygon` (with a per-part fallback) **before** `make_valid`. Do not run `make_valid` first — it misinterprets dateline-crossing rings as self-intersections.
- **GDACS timeline availability**: only available from 2015 onward. Impact buffers (ADM0/ADM1 exposure) only from ~2022.
- **ADAM admin-name-only**: ADAM CSVs use FAO GAUL 2015 admin names, not OCHA pcodes. No crosswalk exists yet — pcode enrichment requires a geometric join pass in the downstream pipeline.
- **`ocha-stratus` is a hard dependency** (listed in `pyproject.toml`). Installing ocha-lens will install stratus; stratus credentials are only needed if you call `ecmwf_storm.download_forecasts` with `stage="dev"` or `"prod"`.
- **Schema validation is strict** (`strict=True, coerce=True`). If upstream data changes column names or value ranges, pandera will raise at the validate call, not silently produce wrong output.

## Source

- Repo: <https://github.com/OCHA-DAP/ocha-lens>
- Docs: <https://ocha-lens.readthedocs.io/en/latest/>
- Latest tag: `0.5.1` (SHA `8a80911`)
- Active branch: `main`
