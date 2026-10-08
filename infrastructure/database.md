---
content_type: infrastructure
last_reviewed: "2026-09-30"   # bump when a human verifies the page is still accurate
---

# Database

Use **`ocha-stratus`** for all DB access (`stratus.get_engine()`) — including DDL. Never fall back to raw `psycopg2`.

```python
import ocha_stratus as stratus
engine = stratus.get_engine()
```

## Gotchas (learned the hard way)

- **No `PGSSLMODE` needed.** Connections through `ocha-stratus` negotiate SSL on their own; they were verified with `PGSSLMODE` unset on dev and prod, including through the SSH tunnel (2026-09-30).
- **Explicit commit.** SQLAlchemy 2.0 does not autocommit. After any write with `engine.connect()`, call `conn.commit()` or the write is silently rolled back.

## What's in the DB

- **Raster stats** (per administrative division) for ERA5 (precip), SEAS5 (precip), IMERG, Floodscan — load these from the DB, not by recomputing from rasters.
- **`public.polygons`** — admin metadata (name, code, total area) for certain countries.
- Full schema→table→column snapshots: [db-schema.md](db-schema.md) (prod) / [db-schema-dev.md](db-schema-dev.md) (dev), generated daily.
- **ER diagrams + relationships** for the two relational schemas (`aa` — the AA portfolio/CERF-funding schema, incl. how it mirrors OneGMS — and `storms`): [db-erd.md](db-erd.md).

Pipelines that populate these tables: see `pipelines/` (e.g. raster-stats, raster-pipelines). **Who reads and writes what, on one screen:** the generated [database network map](https://ocha-dap.github.io/ds-knowledge-base/db-network/) (`scripts/gen_db_network.py`, curated layer in [`db-network.yml`](db-network.yml)) — built for "what breaks if a database loses its network path?".

## Network access

**Since 2026-09-30 both servers are reachable only through their private endpoints.** Public network access is off on `chd-rasterstats-dev` and `chd-rasterstats-prod` for good; it will not be switched back on.

Where you can reach the databases from:

| From | Works? | How |
|---|---|---|
| Databricks jobs (Job Compute policy) | yes | the `dsci` host secrets hold the private-endpoint addresses; nothing to do in code |
| Your laptop | only through the tunnel | a personal Databricks SSH tunnel cluster, then point stratus at it — [internal KB → `infrastructure/local-db-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/local-db-access.md). Direct connections time out on every network |
| App Service apps with VNet integration | yes | prod works by hostname; **dev must use the private-endpoint address, not the hostname** (inside the VNet the dev hostname resolves to an endpoint that doesn't work, and that is not being fixed for now). Addresses: [internal KB → `infrastructure/network-addresses.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/network-addresses.md) |
| App Service apps without VNet integration | **no** | they need OICT to add VNet integration; the list is in the internal KB |
| GitHub Actions (GitHub-hosted runners) | **no** | run the database step on Databricks and hand data over through blob (below) |

**The pattern for GitHub Actions that need database data:** a Databricks job reads the database and writes files to blob; the workflow reads blob. Working examples: the [aa-tracking](../pipelines/aa-tracking.md) snapshot, the site data of the four mirrors ([hnrp](../pipelines/hnrp-mirror.md), [fewsnet](../pipelines/fewsnet-mirror.md), [ipc](../pipelines/ipc-mirror.md), [population](../pipelines/population-mirror.md)), [hdx-floodscan](../pipelines/hdx-floodscan.md) (prepare on Databricks, publish on GitHub Actions) and [cerf-supplement](../pipelines/cerf-supplement.md). Workflows that still connect directly now fail: this repo's `db-schema.yml`, `aa-links.yml` and `usage-review.yml`, and [pipelines-status](../pipelines/pipelines-status.md) loses its table-freshness stats. The dormant GitHub Actions monitors for Afghanistan drought (next run 2027-03-05), Ethiopia drought (2027-02-06), the LAC dry corridor and the Cuba observational check will fail when next triggered unless they move to Databricks first.

**Blob storage is unchanged:** its public network access is still on, so blob works from everywhere. Whether that changes is an open point with OICT, tracked in the internal KB.

The network configuration itself (addresses, firewall and endpoint detail, which apps are VNet-integrated) and the September 2026 incident are in the private companion repo (access-gated):

- configuration and reachability — [internal KB → `infrastructure/db-network-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/db-network-access.md)
- addresses — [internal KB → `infrastructure/network-addresses.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/network-addresses.md)
- querying from your laptop — [internal KB → `infrastructure/local-db-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/local-db-access.md)
- the incident — [internal KB → `incidents/2026-09-db-network-lockdown.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/incidents/2026-09-db-network-lockdown.md)

What you need to operate, without opening those:

- **Prod is `chd-rasterstats-prod`; dev is `chd-rasterstats-dev`.** A third server, `ocha-chd-ds-prod`, is a diverged clone — **do not use it**, whatever its name suggests.
- **Jobs take the host from the environment.** Databricks jobs get `DSCI_AZ_DB_{PROD,DEV}_HOST` from the `dsci` secret scope through the Job Compute policy, and `ocha-stratus` builds the connection from it. Never hard-code a server hostname (the fixes for repos that did: [ds-raster-stats#51](https://github.com/OCHA-DAP/ds-raster-stats/pull/51), [hdx-floodscan#24](https://github.com/OCHA-DAP/hdx-floodscan/pull/24)).
- **Do not repoint the `dsci` host secrets without the team lead's say-so.** A `relation "…" does not exist` failure across many jobs at once is the signature of a wrong host, not of a schema bug.
- **A connection that times out is a network-path question, not a credentials one** — check the table above for what that runtime can reach before changing anything.
- `chd-rasterstats-prod` has `max_connections = 50` — a job that opens an engine per query exhausts it on its own (see [hti-hurricanes-monitoring](../pipelines/hti-hurricanes-monitoring.md) and the fix in [ds-aa-hti-hurricanes#24](https://github.com/OCHA-DAP/ds-aa-hti-hurricanes/pull/24): one engine per process via `lru_cache`).
