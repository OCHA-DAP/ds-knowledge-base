---
content_type: library
name: ds-toolkit
status: superseded
purpose: "Reusable Python (and R stub) utilities for Azure Blob Storage I/O and PostgreSQL access on the team's internal infrastructure"
language: python
source_repo: ocha-dap/ds-toolkit
source_branch: python-functions
source_sha: 78800ef
version: "none"
install: "git+https://github.com/OCHA-DAP/ds-toolkit.git@python-functions#subdirectory=python"
auth_env:
  - DS_AZ_BLOB_DEV_SAS
  - DS_AZ_BLOB_PROD_SAS
  - DS_AZ_DB_DEV_HOST
  - DS_AZ_DB_PROD_HOST
  - DS_AZ_DB_DEV_UID
  - DS_AZ_DB_PROD_UID
  - DS_AZ_DB_DEV_PW
  - DS_AZ_DB_PROD_PW
key_api:
  - get_container_client
  - load_parquet_from_blob
  - upload_parquet_to_blob
  - load_csv_from_blob
  - upload_csv_to_blob
  - load_shp_from_blob
  - upload_shp_to_blob
  - open_blob_cog
  - upload_cog_to_blob
  - list_container_blobs
  - get_engine
  - postgres_upsert
depends_on: []
used_by: []
visibility: public
last_synced: "2026-06-22"
---

## Summary

`ds-toolkit` is an early-stage internal utility library providing thin wrappers around Azure Blob Storage and Azure PostgreSQL for the OCHA DS team. It covers the common I/O operations the team repeats project-to-project: load/save DataFrames (parquet, CSV), GeoDataFrames (zipped shapefile), and rasters (Cloud-Optimized GeoTIFF) to/from blob; get a SQLAlchemy engine for dev or prod Postgres; and a pandas-compatible upsert helper.

**Note:** `ds-toolkit` is the predecessor to `ocha-stratus`. For new projects, reach for `ocha-stratus` instead — it is the currently preferred library for all blob and DB access (see `infrastructure/conventions.md`). `ds-toolkit` is still recognisable in older repos and may be in use where `ocha-stratus` hasn't yet been adopted.

The repo also has an R stub (`r/R/`) but it contains only a placeholder file; the R side is not yet implemented.

## Install & auth

The package is not on PyPI. Install from git, pinning by branch or SHA:

```bash
pip install "git+https://github.com/OCHA-DAP/ds-toolkit.git@python-functions#subdirectory=python"
# or with uv:
uv add "git+https://github.com/OCHA-DAP/ds-toolkit.git@python-functions#subdirectory=python"
```

Auth is entirely via environment variables (loaded automatically with `python-dotenv`). Set these in a `.env` file or in your environment:

| Variable | Purpose |
|---|---|
| `DS_AZ_BLOB_DEV_SAS` | SAS token for dev blob account |
| `DS_AZ_BLOB_PROD_SAS` | SAS token for prod blob account |
| `DS_AZ_DB_DEV_HOST` | Dev Postgres hostname |
| `DS_AZ_DB_PROD_HOST` | Prod Postgres hostname |
| `DS_AZ_DB_DEV_UID` | Dev Postgres username |
| `DS_AZ_DB_PROD_UID` | Prod Postgres username |
| `DS_AZ_DB_DEV_PW` | Dev Postgres password |
| `DS_AZ_DB_PROD_PW` | Prod Postgres password |

Blob endpoints are hardcoded: dev = `imb0chd0dev.blob.core.windows.net`, prod = `imb0chd0prod.blob.core.windows.net`. The default container is `projects`.

## Key API

Two modules; the package registers as `src` in `setup.cfg`, so imports are `from src import blob_utils` / `from src import database`. Signatures and defaults live in the code (`code_ref`) — this is a pointer, not a spec. Shape is essentially the `ocha-stratus` blob/DB surface that succeeded it.

- **`blob_utils`** — blob I/O keyed on `stage` (`dev`/`prod`) and `container_name` (default `projects`): `load_parquet_from_blob` / `upload_parquet_to_blob`, `load_csv_from_blob` / `upload_csv_to_blob`, `load_shp_from_blob` / `upload_shp_to_blob` (zipped shapefile ↔ `gpd.GeoDataFrame`), `open_blob_cog` / `upload_cog_to_blob` (COG ↔ `xr.DataArray`, lazy via rioxarray), `list_container_blobs`, and the low-level `get_container_client`.
- **`database`** — `get_engine(stage)` returns a SQLAlchemy `Engine` for dev/prod Postgres; `postgres_upsert` is a `DataFrame.to_sql(method=...)` callback doing `INSERT … ON CONFLICT DO UPDATE` (see gotchas for the constraint-name and SQLAlchemy-2.x caveats).

## Used by

No KB pages currently list `ds-toolkit` as a dependency. It predates the current `ocha-stratus`-first convention; older project repos may import it directly without a KB page.

## Gotchas & conventions

- **Superseded by `ocha-stratus`** for new work. The team convention (see `infrastructure/conventions.md`) is to reach for `ocha-stratus` first. `ds-toolkit` uses a different env var naming scheme (`DS_AZ_*` vs `DSCI_AZ_*`) and direct SAS-token auth rather than stratus's managed patterns.
- **Package name collision.** `setup.cfg` registers the package as `src`, not `ds-toolkit`. In a project that also has a local `src/` package, installing this library will shadow or be shadowed by the project's own `src`. This is a known structural problem inherited from the early scaffold.
- **Active branch is `python-functions`, not `main`.** `main` only has the empty scaffold; all actual functions live on `python-functions`. The `chore/uv-regen` branch (2026-06-18, the most recent by date) dropped the functional modules (`blob_utils.py`, `database.py`), leaving only an empty `python/src/__init__.py`, and just regenerated the requirements file — it is not the functional branch.
- **No version tag.** There are no git tags; pin by SHA or branch name.
- **`load_shp_from_blob` extracts to `./temp`** (relative CWD), not a proper `tempfile.TemporaryDirectory`. This can leave detritus and will break in read-only filesystems.
- **`postgres_upsert` requires SQLAlchemy 2.x.** The default constraint name is `<table>_unique`; pass `constraint=` explicitly if yours differs.
- **Azure PostgreSQL needs SSL.** The connection URL does not include `sslmode=require`. Set `PGSSLMODE=require` in the environment (see `infrastructure/` memory note on this).
- **`python-dotenv` loads `.env` at import time.** Env vars set after import will not be picked up.

## Source

- Repo: [github.com/OCHA-DAP/ds-toolkit](https://github.com/OCHA-DAP/ds-toolkit) (branch: `python-functions`, SHA: `78800ef`)
- Key files: `python/src/blob_utils.py`, `python/src/database.py`, `python/examples/blob.md`
