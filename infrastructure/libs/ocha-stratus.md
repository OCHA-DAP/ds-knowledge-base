---
content_type: library
name: ocha-stratus
status: active
purpose: "Unified access layer for the DS team's Azure blob storage and PostgreSQL database, plus shared datasource loaders and email helpers"
language: python
source_repo: ocha-dap/ocha-stratus
source_branch: listmonk-transactional
source_sha: a3bac64
version: "0.1.8"
install: "uv add ocha-stratus  # PyPI; or: pip install ocha-stratus"
auth_env:
  - DSCI_AZ_BLOB_DEV_SAS
  - DSCI_AZ_BLOB_PROD_SAS
  - DSCI_AZ_BLOB_DEV_SAS_WRITE
  - DSCI_AZ_BLOB_PROD_SAS_WRITE
  - DSCI_AZ_DB_DEV_HOST
  - DSCI_AZ_DB_PROD_HOST
  - DSCI_AZ_DB_DEV_UID
  - DSCI_AZ_DB_PROD_UID
  - DSCI_AZ_DB_DEV_PW
  - DSCI_AZ_DB_PROD_PW
  - DSCI_AZ_DB_DEV_UID_WRITE
  - DSCI_AZ_DB_PROD_UID_WRITE
  - DSCI_AZ_DB_DEV_PW_WRITE
  - DSCI_AZ_DB_PROD_PW_WRITE
  - PGSSLMODE
  - DSCI_LISTMONK_API_USERNAME
  - DSCI_LISTMONK_API_KEY
key_api:
  - load_parquet_from_blob
  - upload_parquet_to_blob
  - load_geoparquet_from_blob
  - load_csv_from_blob
  - upload_csv_to_blob
  - open_blob_cog
  - upload_cog_to_blob
  - list_container_blobs
  - get_container_client
  - get_engine
  - postgres_upsert
  - stack_cogs
  - codab.load_codab_from_fieldmaps
  - codab.load_codab_from_hdx
  - codab.load_codab_from_blob
  - cerf.load_cerf_from_blob
  - emdat.load_emdat_from_blob
  - listmonk.send_transactional
depends_on: []
used_by:
  - pipelines/storms-pipeline.md
  - pipelines/storms-alerts.md
  - pipelines/floodexposure-monitoring.md
  - pipelines/glb-tropicalcyclones.md
  - pipelines/bgd-cyclone-monitoring.md
  - pipelines/moz-cyclones-monitoring.md
  - pipelines/nhc-forecast.md
  - pipelines/imerg.md
  - pipelines/raster-pipelines.md
  - pipelines/seasonal-bulletin.md
  - pipelines/glb-cyclones-impactmodel.md
  - pipelines/hti-hurricanes-impactmodel.md
  - apps/floodexposure-monitoring-app.md
  - apps/glb-tropicalcyclones-app.md
  - apps/data-validation-app.md
  - frameworks/bgd-flooding/2025-04-25.md
  - frameworks/phl-storms/2025-10-03.md
  - frameworks/tcd-drought/2025-03-03.md
visibility: public
last_synced: "2026-07-09"
---

## Summary

`ocha-stratus` is the team-standard Python library for all blob storage and database access.
Every project that reads from or writes to the DS team's Azure infrastructure goes through
stratus — **never** raw Azure SDK calls or raw `psycopg2`. In addition to the core I/O
helpers, stratus ships shared datasource loaders (CODAB boundaries, CERF, EM-DAT) and a
Listmonk transactional email helper. It is a hard dependency of almost every pipeline,
framework, and app in the portfolio.

See the upstream docs at [ocha-stratus.readthedocs.io](https://ocha-stratus.readthedocs.io/)
and the [storage](../storage.md) + [database](../database.md) conventions pages for the
team-level rules that sit on top.

## Install & auth

```bash
# recommended (uv)
uv add ocha-stratus

# pip
pip install ocha-stratus

# pin to a tag (Databricks / requirements.txt)
pip install ocha-stratus==0.1.8
```

The package is on PyPI. There is no extra `[optional]` install needed for standard blob + DB
use; all heavy dependencies (geopandas, xarray, rioxarray, sqlalchemy, etc.) are included.

### Blob auth

Four SAS-token env vars are required (read and write, dev and prod):

```
DSCI_AZ_BLOB_DEV_SAS          # read-only SAS for dev container
DSCI_AZ_BLOB_PROD_SAS         # read-only SAS for prod container
DSCI_AZ_BLOB_DEV_SAS_WRITE    # write SAS for dev container
DSCI_AZ_BLOB_PROD_SAS_WRITE   # write SAS for prod container
```

Hosts are hardcoded in the library: `imb0chd0dev.blob.core.windows.net` (dev) and
`imb0chd0prod.blob.core.windows.net` (prod). The default container is `projects`; raster
COGs live in the `raster` container; CODAB/global datasets use `polygon` and `global`.

### Database auth

Eight env vars cover the four credentials (uid + pw, dev and prod, read and write):

```
DSCI_AZ_DB_DEV_HOST / DSCI_AZ_DB_PROD_HOST
DSCI_AZ_DB_DEV_UID  / DSCI_AZ_DB_PROD_UID
DSCI_AZ_DB_DEV_PW   / DSCI_AZ_DB_PROD_PW
DSCI_AZ_DB_DEV_UID_WRITE / DSCI_AZ_DB_DEV_PW_WRITE
DSCI_AZ_DB_PROD_UID_WRITE / DSCI_AZ_DB_PROD_PW_WRITE
```

**Also required: `PGSSLMODE=require`.** Azure PostgreSQL demands SSL but the connection URL
stratus builds does not embed `sslmode`. Without this env var the connection fails silently.

On Databricks these come from the `dsci` secret scope. On GHA they come from repo secrets.

### Listmonk email auth

```
DSCI_LISTMONK_API_USERNAME
DSCI_LISTMONK_API_KEY
```

Only needed if calling `listmonk.send_transactional`. The Listmonk instance URL is hardcoded
in the library (Azure Web App, eastus2).

## Key API

| Name | What it does |
|---|---|
| `load_parquet_from_blob(blob_name, stage, container_name)` | Read a Parquet blob → `pd.DataFrame` |
| `upload_parquet_to_blob(df, blob_name, stage, container_name)` | Write a DataFrame or GeoDataFrame as Parquet to blob |
| `load_geoparquet_from_blob(blob_name, stage, container_name)` | Read a GeoParquet blob → `gpd.GeoDataFrame` |
| `load_csv_from_blob(blob_name, stage, container_name)` | Read a CSV blob → `pd.DataFrame` |
| `upload_csv_to_blob(df, blob_name, stage, container_name)` | Write a DataFrame as CSV to blob |
| `open_blob_cog(blob_name, stage, container_name, chunks)` | Open a Cloud Optimized GeoTIFF via URL → `xr.DataArray` (lazy, dask-backed) |
| `upload_cog_to_blob(da, blob_name, stage, container_name)` | Write an `xr.DataArray` as a COG to blob |
| `list_container_blobs(name_starts_with, stage, container_name)` | List blob names, optionally filtered by prefix |
| `get_container_client(container_name, stage, write)` | Low-level: return an Azure `ContainerClient` |
| `get_engine(stage, write)` | Return a SQLAlchemy engine for the Postgres DB |
| `postgres_upsert(table, conn, keys, data_iter, constraint)` | `pandas.DataFrame.to_sql` method kwarg for INSERT … ON CONFLICT DO UPDATE |
| `stack_cogs(dataset, dates, stage, clip_gdf, mode)` | Fetch and stack multiple COGs for imerg/seas5/era5/floodscan into one `xr.Dataset` |
| `codab.load_codab_from_fieldmaps(iso3, admin_level)` | Load COD-AB admin boundaries live from FieldMaps GeoParquet |
| `codab.load_codab_from_hdx(iso3, admin_level, version)` | Load COD-AB boundaries from HDX's cloud-native mirror on Source Cooperative (`version` defaults to `"latest"`) — added in 0.1.8 |
| `codab.load_codab_from_blob(iso3, admin_level, stage)` | Load COD-AB boundaries from the blob cache (faster, offline-safe) |
| `cerf.load_cerf_from_blob(iso3, stage)` | Load CERF funding allocations from blob (HDX-sourced Parquet) |
| `emdat.load_emdat_from_blob(iso3, include_historic, stage)` | Load EM-DAT disaster data from blob |
| `listmonk.send_transactional(to_emails, subject, …)` | Send a transactional email via the team's Listmonk instance |

## Used by

ocha-stratus is a dependency of essentially all active pipelines, frameworks, and apps.
Representative consumers (see `used_by` frontmatter for the full list):

- **Pipelines:** storms-pipeline, floodexposure-monitoring, raster-pipelines, seasonal-bulletin, imerg, nhc-forecast, bgd-cyclone-monitoring, moz-cyclones-monitoring, glb-cyclones-impactmodel, hti-hurricanes-impactmodel
- **Apps:** floodexposure-monitoring-app, glb-tropicalcyclones-app, data-validation-app
- **Frameworks:** bgd-flooding, phl-storms, tcd-drought (and most others — stratus is how they read rasters and boundaries)

## Gotchas & conventions

- **`PGSSLMODE=require` is mandatory.** The connection URL built by `get_engine()` does not
  include `sslmode=require`. Azure PostgreSQL rejects unauthenticated SSL connections; the
  env var is the fix. Without it you get a silent failure. See [database.md](../database.md).
- **SQLAlchemy 2.0 does not autocommit.** After any write using `engine.connect()`, you must
  call `conn.commit()` explicitly or the write is rolled back without error.
- **`stage` defaults are inconsistent — check the signature.** Blob loaders/writers and
  `get_engine()` default to `stage="dev"`; but `stack_cogs()` and `codab.load_codab_from_blob()`
  default to `stage="prod"`. Always pass `stage` explicitly in production code rather than
  trusting the default.
- **Blob path convention.** Always use `{PROJECT_PREFIX}/{raw|processed}/{datasource}/{filename}`.
  `PROJECT_PREFIX` comes from `src.constants`, never hardcoded inline. See [storage.md](../storage.md).
- **CODAB: prefer blob cache over live FieldMaps.** `codab.load_codab_from_blob` is faster and
  does not depend on fieldmaps.io availability. Use `load_codab_from_fieldmaps` only when the
  blob cache might be stale.
- **CODAB source.coop mirror (`load_codab_from_hdx`, 0.1.8+).** A third option loads boundaries
  from HDX's cloud-native COD-AB mirror on Source Cooperative
  (`https://data.source.coop/hdx/cod-ab/{iso3}/{version}/adm{admin_level}/original.parquet`).
  It reads the official HDX/ArcGIS COD-AB rather than the FieldMaps derivation, and `version`
  (default `"latest"`) lets you pin a specific release — useful when you need the authoritative
  HDX boundaries or reproducibility, but it does depend on source.coop availability.
- **`upload_parquet_to_blob` handles GeoDataFrame correctly.** It detects `gpd.GeoDataFrame`
  and serialises via `BytesIO` to preserve geometry and CRS — the plain `to_parquet()` path
  does not work for GeoDataFrames.
- **`postgres_upsert` assumes a constraint named `{table}_unique` by default.** Pass an
  explicit `constraint` argument if the DB constraint has a different name.
- **`stack_cogs` reads from the `raster` container, not `projects`.** The `dataset` parameter
  must be one of `imerg`, `seas5`, `era5`, `floodscan`; it is used as the blob prefix.
- **No other ocha-* library dependency.** stratus has zero runtime dependency on `ocha-lens`
  or `ocha-relay`; it can be installed standalone.

## Source

- **Repo:** [github.com/OCHA-DAP/ocha-stratus](https://github.com/OCHA-DAP/ocha-stratus)
- **Docs:** [ocha-stratus.readthedocs.io](https://ocha-stratus.readthedocs.io/)
- **Latest release:** `0.1.8` (2026-07-09, on `main` via PR #32) — added `codab.load_codab_from_hdx`
- **Tracked branch:** `listmonk-transactional` (SHA `a3bac64`) — carries the not-yet-released
  `listmonk.send_transactional` work; it does **not** yet include the 0.1.8 `load_codab_from_hdx` change
- **Related KB pages:** [storage.md](../storage.md), [database.md](../database.md), [conventions.md](../conventions.md)
