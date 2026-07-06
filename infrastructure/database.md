---
content_type: infrastructure
last_reviewed: "2026-06-12"   # bump when a human verifies the page is still accurate
---

# Database

Use **`ocha-stratus`** for all DB access (`stratus.get_engine()`) — including DDL. Never fall back to raw `psycopg2`.

```python
import ocha_stratus as stratus
engine = stratus.get_engine()
```

## Gotchas (learned the hard way)

- **SSL required.** Azure PostgreSQL requires SSL but the stratus connection URL doesn't set `sslmode`. Set `PGSSLMODE=require` in the environment, or connections fail.
- **Explicit commit.** SQLAlchemy 2.0 does not autocommit. After any write with `engine.connect()`, call `conn.commit()` or the write is silently rolled back.

## What's in the DB

- **Raster stats** (per administrative division) for ERA5 (precip), SEAS5 (precip), IMERG, Floodscan — load these from the DB, not by recomputing from rasters.
- **`public.polygons`** — admin metadata (name, code, total area) for certain countries.

Pipelines that populate these tables: see `pipelines/` (e.g. raster-stats, raster-pipelines).
