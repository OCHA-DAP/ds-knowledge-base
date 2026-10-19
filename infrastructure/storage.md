---
content_type: infrastructure
last_reviewed: "2026-09-30"   # bump when a human verifies the page is still accurate
---

# Blob storage

Use **`ocha-stratus`** for all blob access — never raw Azure SDK calls. Check the stratus README for current auth/init patterns; don't guess.

```python
import ocha_stratus as stratus
df = stratus.load_parquet_from_blob(f"{PROJECT_PREFIX}/example_blob")
```

## Network access

**Blob on the general accounts (`imb0chd0prod`, `imb0chd0dev`, `imb0chd0collab`) works from everywhere** — Databricks, GitHub Actions, App Services, laptops, browsers via the [token issuer](token-issuer.md) — (checked 2026-09-30). This is unlike the databases, which are private-endpoint only since 2026-09-30 (see [database.md](database.md) → Network access). Whether blob access changes is an open point with OICT. The confidential account `imb0chd0confidint0prod` can't be reached from outside the Azure network.

The network configuration itself is documented in the [internal KB → `infrastructure/db-network-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/db-network-access.md), not here.

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
