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
- Full schema→table→column snapshots: [db-schema.md](db-schema.md) (prod) / [db-schema-dev.md](db-schema-dev.md) (dev), generated daily.
- **ER diagrams + relationships** for the two relational schemas (`aa` — the AA portfolio/CERF-funding schema, incl. how it mirrors OneGMS — and `storms`): [db-erd.md](db-erd.md).

Pipelines that populate these tables: see `pipelines/` (e.g. raster-stats, raster-pipelines). **Who reads and writes what, on one screen:** the generated [database network map](https://ocha-dap.github.io/ds-knowledge-base/db-network/) (`scripts/gen_db_network.py`, curated layer in [`db-network.yml`](db-network.yml)) — built for "what breaks if a database loses its network path?".

> **Network access:** the `chd-rasterstats-dev` server had its public network access disabled on 2026-09-22 with no private endpoint (see [storms-pipeline](../pipelines/storms-pipeline.md)); everything that still pointed at dev died on a connection timeout and the storms jobs were cut over to prod the same day. <!-- TODO: record the intended end-state for prod's network access (private endpoint? VNet-integrated runners and apps?) once decided. -->

> **In progress (as of April 2026):** the separate `chd-rasterstats-dev` / `chd-rasterstats-prod` flexible servers are being consolidated onto a single flexible server hosting `dev` and `prod` databases. <!-- TODO: confirm the migration completed and update this page + raster-stats.md accordingly -->
