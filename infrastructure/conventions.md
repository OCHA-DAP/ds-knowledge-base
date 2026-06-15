# Data conventions

Team-wide conventions that hold regardless of project. Seeded from the team's global Claude config; this is now the shared home for them.

## Naming / time

- **`valid_time`** (or `valid_date`) — the valid time of a forecast, i.e. what it's a forecast *for*. Also called reference time or just "time". Use this for observational data too.
- **`issued_time`** — the issue/publication time of a forecast.
- **Leadtime convention:** `issued_time + leadtime = valid_time`. A forecast issued in March with leadtime 1 month is valid for April.

## Spatial

- **CRS is always EPSG:4326** unless explicitly noted.
- `xarray` for gridded data, `geopandas` for vector, `rioxarray` for raster I/O and clipping.

## Admin boundaries (CODABs)

- Prefer an existing repo function to load the CODAB from blob. Otherwise load from **FieldMaps via `ocha-stratus`**.
- For metadata only (admin name, code, total area), use the DB `public.polygons` table via `ocha-stratus` — available for certain countries only.

## Python

- Python 3.11+. `uv` for env management, not pip directly.
- Type hints on all signatures. f-strings. Don't suppress exceptions silently.

## Libraries to reach for first

- **`ocha-stratus`** — all blob & DB access. See [database.md](database.md) / [storage.md](storage.md).
- **`ocha-lens`** — common data processing; check it before writing custom logic.
- **`ocha-relay`** — comms (Listmonk email). See [comms-listmonk.md](comms-listmonk.md).

**Deprecated — don't use for new work:**

- **`ocha-anticipy`** — superseded; **not used for new frameworks**. Still relevant when reading/maintaining older frameworks that imported it, so worth recognising, but reach for `ocha-stratus`/`ocha-lens` instead.
