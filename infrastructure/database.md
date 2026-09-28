---
content_type: infrastructure
last_reviewed: "2026-09-25"   # bump when a human verifies the page is still accurate
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

## Network access

**The network configuration of the database servers is not documented in this repo.** Firewall and public-access state, private endpoints, which runtime can reach which server, and the September 2026 lockdown and outage are in the private companion repo (access-gated):

- configuration and reachability — [internal KB → `infrastructure/db-network-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/db-network-access.md)
- addresses — [internal KB → `infrastructure/network-addresses.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/network-addresses.md)
- the incident — [internal KB → `incidents/2026-09-db-network-lockdown.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/incidents/2026-09-db-network-lockdown.md)

What you need to operate, without opening those:

- **Prod is `chd-rasterstats-prod`; dev is `chd-rasterstats-dev`.** A third server, `ocha-chd-ds-prod`, is a diverged clone — **do not use it**, whatever its name suggests.
- **Jobs take the host from the environment.** Databricks jobs get `DSCI_AZ_DB_{PROD,DEV}_HOST` from the `dsci` secret scope through the Job Compute policy, and `ocha-stratus` builds the connection from it. Never hard-code a server hostname (the fixes for repos that did: [ds-raster-stats#51](https://github.com/OCHA-DAP/ds-raster-stats/pull/51), [hdx-floodscan#24](https://github.com/OCHA-DAP/hdx-floodscan/pull/24)).
- **Do not repoint the `dsci` host secrets without the team lead's say-so.** A `relation "…" does not exist` failure across many jobs at once is the signature of a wrong host, not of a schema bug.
- **A connection that times out is a network-path question, not a credentials one** — check the internal page for what that runtime can currently reach before changing anything.
- `chd-rasterstats-prod` has `max_connections = 50` — a job that opens an engine per query exhausts it on its own (see [hti-hurricanes-monitoring](../pipelines/hti-hurricanes-monitoring.md) and the fix in [ds-aa-hti-hurricanes#24](https://github.com/OCHA-DAP/ds-aa-hti-hurricanes/pull/24): one engine per process via `lru_cache`).
