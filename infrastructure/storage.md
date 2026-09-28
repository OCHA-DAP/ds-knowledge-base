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

## Network access

The team storage accounts (`imb0chd0prod`, `imb0chd0dev`, `imb0chd0collab`, and `imb0chd0confidint0prod` at `10.208.11.233`) each have an approved private endpoint in `ocha-eastus2-vnet` (checked 2026-09-25). Public access is still enabled on all of them; if OICT disables it the way it did for the dev database on 2026-09-22, laptops and GitHub-hosted runners lose blob access and only VNet-connected runtimes (Databricks, VNet-integrated App Services) keep it — see the database page's [network access](database.md#network-access-verified-2026-09-25) section for the pattern. <!-- TODO: record the blob endpoint IPs and verify stratus blob access from a Databricks job the day public access is cut -->

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
