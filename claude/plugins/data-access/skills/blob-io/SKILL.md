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
- **Never list a container without a prefix** — `list_container_blobs(...)` over a
  full container hangs for minutes. Always pass `name_starts_with=` (e.g. a project
  prefix); to explore, list one level at a time.
- Most team data lives on the DEV storage account. Check the stratus README for current
  auth/init patterns and dev/prod switches — don't guess.

## Postgres

```python
engine = stratus.get_engine()  # stage/mode per the stratus docs
```

- Azure Postgres requires SSL — set `PGSSLMODE=require` if connections fail.
- SQLAlchemy 2.0: writes via `engine.connect()` need an explicit `conn.commit()`.
- The split: **rasters → blob; per-admin raster stats → DB** (ERA5, SEAS5, IMERG,
  Floodscan). Per-table semantics (units, product variant, record start): the 📝
  notes in KB `infrastructure/db-schema.md` / `db-table-notes.json`.

### Recipe: seasonal zonal series from a daily stats table

The stats tables are per-pcode; for an arbitrary zone (e.g. "Niger south of 17°N"),
area-weight the admin units' overlap with the zone — don't filter whole units in/out:

```python
import geopandas as gpd, pandas as pd
adm2 = stratus.codab.load_codab_from_blob("ner", admin_level=2).to_crs(4326)
part = adm2.geometry.intersection(zone_geom)           # zone_geom: shapely, EPSG:4326
w = gpd.GeoSeries(part, crs=4326).to_crs("ESRI:54034").area  # equal-area weights
df = pd.read_sql("""SELECT pcode, valid_date, mean FROM public.imerg
    WHERE iso3='NER' AND adm_level=2
      AND EXTRACT(month FROM valid_date) IN (6,7)""", stratus.get_engine(stage="prod"))
df["year"] = pd.to_datetime(df.valid_date).dt.year
tot = df.groupby(["year", "pcode"])["mean"].agg(["sum", "count"]).reset_index()
tot = tot[tot["count"] >= 55]                          # drop partial seasons (61 days here)
tot["w"] = tot.pcode.map(pd.Series(w.values, index=adm2.ADM2_PCODE.values))
zone = tot.groupby("year").apply(lambda g: (g["sum"] * g.w).sum() / g.w.sum())
```

Same shape works for `era5`/`floodscan`; for `seas5` group by `issued_date`+`leadtime`.

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
