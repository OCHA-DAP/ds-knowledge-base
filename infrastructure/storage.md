---
content_type: infrastructure
last_reviewed: "2026-06-12"   # bump when a human verifies the page is still accurate
---

# Blob storage

Use **`ocha-stratus`** for all blob access — never raw Azure SDK calls. Check the stratus README for current auth/init patterns; don't guess.

```python
import ocha_stratus as stratus
df = stratus.load_parquet_from_blob(f"{PROJECT_PREFIX}/example_blob")
```

## Path convention

```
{PROJECT_PREFIX}/{raw|processed}/{datasource}/{filename}
```

- `PROJECT_PREFIX` comes from `src.constants` — never hardcoded inline.
- `raw/` = unmodified source data; `processed/` = anything derived.
- `datasource` matches the source name (e.g. `chirps`, `seas5`, `ibtracs`).
- Filenames descriptive, with date/version where relevant.

Example: `ds-aa-bfa-drought/processed/seas5/2024-03_tercile_probs.nc`

## What lives where

For ERA5 (precip), SEAS5 (precip), IMERG, Floodscan: **rasters on the blob**, **raster stats (per admin division) in the DB**. See [database.md](database.md).
