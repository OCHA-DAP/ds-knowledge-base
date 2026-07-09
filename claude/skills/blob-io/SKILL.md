---
name: blob-io
description: Load or save team data — Azure blob storage or the Postgres DB — the standard way (ocha-stratus, blob naming convention, rasters-vs-stats split). Use whenever reading/writing parquet/CSV/COG/zarr from blob, querying dev/prod Postgres, or deciding where output data should live.
---

# Blob & DB I/O the team way

Everything goes through `ocha-stratus` — never raw Azure SDK, never raw psycopg2.

## Blob

```python
import ocha_stratus as stratus
from src.constants import PROJECT_PREFIX

df = stratus.load_parquet_from_blob(
    f"{PROJECT_PREFIX}/processed/seas5/2024-03_tercile_probs.parquet"
)
```

- Naming: `{PROJECT_PREFIX}/{raw|processed}/{datasource}/{filename}` — `raw/` for
  untouched source data, `processed/` for anything derived; `datasource` matches the
  source name (`chirps`, `seas5`, `ibtracs`, …); filenames descriptive, with
  date/version where applicable.
- `PROJECT_PREFIX` from `src.constants` — never inline the string.
- Most team data lives on the DEV storage account. Check the stratus README for current
  auth/init patterns and dev/prod switches — don't guess.

## Postgres

```python
engine = stratus.get_engine()  # stage/mode per the stratus docs
```

- Azure Postgres requires SSL — set `PGSSLMODE=require` if connections fail.
- SQLAlchemy 2.0: writes via `engine.connect()` need an explicit `conn.commit()`.
- The split: **rasters → blob; per-admin raster stats → DB** (ERA5, SEAS5, IMERG,
  Floodscan).

## Where is the data?

- DB schemas/tables/row counts: KB `infrastructure/db-schema.md` (+ `db-schema-dev.md`).
- What blob holds per project: KB `assets/<project>/` pages.
- Loader library details: KB `infrastructure/libs/ocha-stratus.md`; prefer `ocha-lens`
  for common processing before writing custom logic.
- CODAB boundaries: the repo's own loader if present, else FieldMaps via stratus;
  name/code-only metadata from DB `public.polygons` (limited countries).
