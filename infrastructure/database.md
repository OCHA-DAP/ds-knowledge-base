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

> **Which server is prod (decided 2026-09-24): `chd-rasterstats-prod`.** A second flexible server, `ocha-chd-ds-prod` (created 2026-02-20, Standard_B1ms, **private endpoint only**, public access disabled — the consolidation target below), also exists in the same resource group. On 2026-09-23/24 the Databricks `dsci` secrets `DSCI_AZ_DB_DEV_HOST` (21:35 UTC) and `DSCI_AZ_DB_PROD_HOST` were repointed at it; every storms job then failed from 03:30 to 18:30 UTC on 2026-09-24 with `relation "storms.…" does not exist` (the storms tables live only on `chd-rasterstats-prod`) and three Storm Alert sends were lost. `DSCI_AZ_DB_PROD_HOST` was pointed back at `chd-rasterstats-prod` at 20:46 UTC. **Do not repoint those secrets without the team lead's say-so**; a "table does not exist" failure across many jobs at once is the signature of this, not of a schema bug. Note also that `chd-rasterstats-prod` has `max_connections = 50` — a job that opens an engine per query exhausts it on its own (see [hti-hurricanes](../pipelines/hti-hurricanes.md) if it exists, else ds-aa-hti-hurricanes#24).

> **In progress (as of April 2026):** the separate `chd-rasterstats-dev` / `chd-rasterstats-prod` flexible servers are being consolidated onto a single flexible server hosting `dev` and `prod` databases — presumably `ocha-chd-ds-prod` above, reachable only over its private endpoint (Databricks can reach it; laptops and GitHub Actions cannot). <!-- TODO: confirm the migration completed and update this page + raster-stats.md accordingly -->
