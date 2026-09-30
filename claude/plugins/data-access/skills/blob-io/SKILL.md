---
name: blob-io
description: Load or save team data — Azure blob storage or the Postgres DB — the standard way (ocha-stratus, blob naming convention, rasters-vs-stats split), plus the semantics needed to read team tables correctly (valid_time vs issued_time, CRS, boundaries). Use whenever reading/writing parquet/CSV/COG/zarr from blob, querying dev/prod Postgres, or deciding where output data should live.
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

- The servers are **private-endpoint only** (public access off since 2026-09-30).
  Databricks jobs reach them as-is. From a laptop, open the Databricks SSH tunnel
  (internal KB `infrastructure/local-db-access.md`) and point stratus at it with
  `DSCI_AZ_DB_{DEV,PROD}_HOST=127.0.0.1:<tunnel port>`. GitHub Actions cannot reach
  them: do the database step on Databricks and hand data to the workflow through blob.
  A timeout means no network path, not bad credentials. No `PGSSLMODE` needed.
- SQLAlchemy 2.0: writes via `engine.connect()` need an explicit `conn.commit()`.
- The split: **rasters → blob; per-admin raster stats → DB** (ERA5, SEAS5, IMERG,
  Floodscan).

## Reading team data correctly (semantics, not style)

- `valid_time` = when the observation/forecast is FOR; `issued_time` = when it was
  published. Issued month + leadtime = valid month. Mixing these up silently corrupts
  any forecast-skill or trigger analysis.
- CRS is **EPSG:4326** unless a page says otherwise.
- CODAB admin boundaries: the repo's own loader if present, else FieldMaps via
  stratus; name/code-only metadata from DB `public.polygons` (limited countries).

## Where is the data?

- DB schemas/tables/row counts: KB `infrastructure/db-schema.md` (+ `db-schema-dev.md`).
- What blob holds per project: KB `assets/<project>/` pages.
- Loader library details: KB `infrastructure/libs/ocha-stratus.md`.
- Third-party sources (IPC, FEWS NET, EM-DAT, …): the `datasets` skill in this plugin.
