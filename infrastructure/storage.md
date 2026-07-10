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

## Storage accounts

Four accounts in resource group `IMB-CHD-DataScience-EastUS2` (all StorageV2):

| account | purpose |
|---|---|
| `imb0chd0dev` | **Public data, dev/testing** — no impact on live systems; free to create/delete containers (mirror the prod structure for better testing). |
| `imb0chd0prod` | **Public data, live systems** — use with caution; container/file creation and deletion are restricted. |
| `imb0chd0collab` | Public data shared via restricted access with collaborators. *Not currently in use.* |
| `imb0chd0confidint0prod` | **Confidential / non-public data** — accessible only from the Azure Virtual Desktop; handle with a higher level of caution. *Not currently in use.* |

Anything sensitive or confidential must go to `imb0chd0confidint0prod`, never the public-data accounts.

## Root buckets: raw / processed / tmp

Containers follow a project-level structure with three root buckets:

- **`raw/`** — unprocessed, straight-from-source data. **Not editable or removable in prod**; populate via automated pipelines wherever possible.
- **`processed/`** — anything derived. Version it to avoid data loss, especially during dev/testing.
- **`tmp/`** — temporary data, **liable to monthly deletion**. Use it habitually to keep only relevant data in cloud storage.

## Access tiers & cost

- **Hot tier** — for frequently accessed/modified data: highest storage cost, lowest access cost.
- **Cool tier** — for infrequently accessed data: cheap storage, expensive access, minimum **30-day** retention.
- Convention: **raw → Cool** (rarely re-read), **processed → Hot** (read often, e.g. feeding the DB).
- The tier is **set at write time**. Pipelines that don't set it explicitly default to **Hot**, which causes avoidable cost — check the tier when adding a new write path.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Path convention

```
{PROJECT_PREFIX}/{raw|processed}/{datasource}/{filename}
```

- `PROJECT_PREFIX` comes from `src.constants` — never hardcoded inline.
- `raw/` / `processed/` semantics: see [Root buckets](#root-buckets-raw--processed--tmp) above.
- `datasource` matches the source name (e.g. `chirps`, `seas5`, `ibtracs`).
- Filenames descriptive, with date/version where relevant.

Example: `ds-aa-bfa-drought/processed/seas5/2024-03_tercile_probs.nc`

## What lives where

For ERA5 (precip), SEAS5 (precip), IMERG, Floodscan: **rasters on the blob**, **raster stats (per admin division) in the DB**. See [database.md](database.md).

## Format decision: COGs over Zarr (2024)

Why every production raster is a Cloud-Optimized GeoTIFF — the 2024 evaluation for storing global gridded datasets (SEAS5/MARS, ERA5, IMERG, FloodScan):

**Requirements.** A cloud-optimized format (metadata in one read; small addressable chunks; lazy loading; integration with distributed-processing tooling), stored in Azure containers, accessible from **both R and Python**, supporting efficient per-dataset update pipelines, spatial clipping that retains temporal/forecast dims (leadtime, ensemble member), and zonal stats.

**COGs** — pros: wide geospatial adoption and interoperability (QGIS, GDAL, GEE); better R support; **better write performance for frequent updates** (matters for time-sensitive daily datasets like IMERG). Cons: no native high-dimensionality — GeoTIFFs are flat, so ensemble forecasts need one GeoTIFF per member.

**Zarr** — pros: arbitrary dimensions (ideal for ensembles); parallel I/O via xarray + Dask; rechunkable after creation. Disqualifiers: poor R interoperability; and **no partial-chunk writes** — appending along time to a spatially-chunked store rewrites the whole store each time. An IMERG append test grew non-linearly: after 5+ days it had produced only ~¼ of the dataset. For the team's access pattern — *write one timestep across the full spatial extent, read a spatial subset across the full time range* — "this will never work well in Zarr" (it would require chunking in time from the start, defeating the spatial reads).

**Outcome.** The original scoping proposed per-dataset choices ("no one-size-fits-all": Zarr as a nice-to-have for ensemble data); in practice **COGs became the standard for all production rasters** ([raster-pipelines](../pipelines/raster-pipelines.md)) and Zarr was not adopted. Test notebooks: `OCHA-DAP/ds-raster-explore` (`imerg-cogs.ipynb`, `imerg-zarr.ipynb`).

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).
