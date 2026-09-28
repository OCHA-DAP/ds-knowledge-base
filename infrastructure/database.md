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

## Network access (verified 2026-09-25)

Three flexible servers exist in `IMB-CHD-DataScience-EastUS2`. Each has a private endpoint in `ocha-eastus2-vnet`; what matters day to day is whether a given runtime can reach it. This table was verified from a Databricks job cluster (Job Compute policy) by TCP connect **and** an authenticated `pg_control_system()` fingerprint, so "works" means the same Postgres cluster the laptop sees, not just an open port:

| Server | Private endpoint | Reachable from Databricks? | Public access (2026-09-25) | Role |
|---|---|---|---|---|
| `chd-rasterstats-prod` | `10.208.11.18` (`chd-rasterstats-prod`, added 2026-09-24) | **yes** | Enabled, `0.0.0.0/0` firewall rule | **prod** — `system_identifier 7423171368645697576`, 31 GB, 24 `storms.*` tables |
| `chd-rasterstats-dev` | `10.208.11.20` (`ch-rasterstast-dev2`, prod-backend subnet) | **yes** | Enabled again since 2026-09-24, `0.0.0.0/0` rule | **dev** — `system_identifier 7410505393597231147`, 30 GB, all schemas (`aa`, `cbpf`, `hpc`, `ipc`, `pop`, `storms`, …) |
| `chd-rasterstats-dev` | `10.208.11.164` (`chd-rasterstats-dev-pep`, dev-backend subnet) | **no** — TCP timeout (NSG, see [comms-listmonk](comms-listmonk.md)) | — | dead endpoint; ignore |
| `ocha-chd-ds-prod` | `10.208.11.14` (`ocha-chd-ds-prod-pep`) | yes | Disabled, no firewall rules | **DO NOT USE** — a physical restore of `chd-rasterstats-prod` (same `system_identifier`, created 2026-02-20) that has diverged: 28 GB, only the 6 base `storms.*` tables created during the 2026-09-24 wrong-host window |

Consequences:

- **Laptops and GitHub-hosted runners reach dev and prod only over the public hostnames** while public access stays enabled; the private IPs do not route from outside the VNet (no VPN/bastion exists). Both servers still carry the `AllowAll 0.0.0.0–255.255.255.255` firewall rule that triggered the 2026-09-22 dev lockdown, so expect either to be locked down again without notice.
- **Databricks reaches the private endpoints by IP but cannot resolve them by name.** From a job cluster the public hostnames resolve to the public IPs (the `privatelink` DNS zone is not linked to the Databricks VNet) and a TCP connect to a public-access-disabled server's public IP times out. So once OICT disables public access on a server, Databricks keeps working **only if the `dsci` host secret for that stage is the private IP** (`10.208.11.18` for prod, `10.208.11.20` for dev) — or once OICT links the private DNS zone to the Databricks VNet. Repointing those secrets is a team-lead decision (see the 2026-09-24 outage below); do it *before* a lockdown, not during one.
- **Status 2026-09-25 18:51 UTC — both `dsci` host secrets now hold the private-endpoint IPs** (team-lead decision, ahead of the public-access shutdown): `DSCI_AZ_DB_PROD_HOST = 10.208.11.18`, `DSCI_AZ_DB_DEV_HOST = 10.208.11.20`. Before the flip a job cluster resolved the prod FQDN to the public `52.184.192.12`. Verified after the flip on fresh Job Compute clusters: HTI Hurricane Monitoring (`dry_run`, prod plane) and a dev NHC Pipeline copy both green. Every Databricks job gets the host from the Job Compute policy (`spark_env_vars` → `{{secrets/dsci/DSCI_AZ_DB_*_HOST}}`) and every team repo builds the URL with `ocha-stratus` (all versions 0.1.2–0.1.7 read that variable; no `sslmode` is set, so a bare IP passes libpq's checks), so no code changed. **Flip back to the FQDNs once OICT links a `privatelink.postgres.database.azure.com` zone to the Databricks and `ocha-eastus2` VNets** — there is no such zone in the subscription today (`az network private-dns zone list` and Resource Graph both empty), which is also why App Service apps resolve the FQDN publicly (next bullet). Repos that hard-code the FQDN bypass the secret: see [ds-raster-stats#51](https://github.com/OCHA-DAP/ds-raster-stats/pull/51) and [hdx-floodscan#24](https://github.com/OCHA-DAP/hdx-floodscan/pull/24).
- **App Service apps are NOT on the private endpoints either (checked 2026-09-25 via `pg_stat_activity.client_addr`).** The flood-exposure app's production slot is VNet-integrated (`ocha-eastus2-webapp` subnet, route-all off) and configured with the prod FQDN, yet its connections arrive at the server's *public* endpoint from an Azure SNAT address (`172.182.212.56`, not one of the app's listed outbound IPs); private-endpoint traffic shows up as `fd40:…` IPv6 addresses instead. Cause is the same missing DNS zone (the VNet's DNS is OICT's `10.208.0.132/.133`). Per-app fix until the zone exists: set the app's `DSCI_AZ_DB_*_HOST` setting to the PE IP (private ranges route through the VNet; the PE subnet `ocha-eastus2-prod-backend` has `privateEndpointNetworkPolicies = Disabled`, so the NSG does not filter it — unlike the dead `.164` endpoint in `dev-backend`). Apps that use the DB with **no VNet integration at all** (need OICT to integrate them first): `chd-ds-seas5-skill`, `chd-ds-seasonality`, `chd-ds-data-validation` (prod), `chd-ds-storms-alerts`, `chd-ds-storms-explore` (dev), `chd-ds-cub-trigger` (dev+prod), and the flood-exposure app's `development` and `sudan` slots. VNet-integrated: flood-exposure production slot, `chd-ds-kb-mcp-internal`, `chd-ds-aa-extract`, `listmonk-demo` (route-all on). Survey method: app settings whose value contains `postgres.database.azure.com` on every app in `DsciAppServicePlan`, so an app that carries its host some other way (e.g. baked into an image) is not listed.
- **Current `dsci` host secrets (checked 2026-09-25):** both `DSCI_AZ_DB_PROD_HOST` and `DSCI_AZ_DB_DEV_HOST` hold the **public hostnames** of `chd-rasterstats-prod` / `chd-rasterstats-dev` (fingerprints match: prod `7423171368645697576`, dev `7410505393597231147`). Pipelines therefore work today *because* public access is enabled — a lockdown of either server breaks every Databricks job on that stage until the host secret is switched to the private IP.
- Storage accounts `imb0chd0prod`, `imb0chd0dev`, `imb0chd0collab` and `imb0chd0confidint0prod` (10.208.11.233) also have approved private endpoints, so the same by-IP path exists for blob if its public access is cut (see [storage.md](storage.md)).

> **Which server is prod (decided 2026-09-24): `chd-rasterstats-prod`.** The second flexible server, `ocha-chd-ds-prod` (created 2026-02-20, Standard_B1ms, private endpoint only, public access disabled), is a diverged restore clone — see the table above. On 2026-09-23/24 the Databricks `dsci` secrets `DSCI_AZ_DB_DEV_HOST` (21:35 UTC) and `DSCI_AZ_DB_PROD_HOST` were repointed at it; every storms job then failed from 03:30 to 18:30 UTC on 2026-09-24 with `relation "storms.…" does not exist` (the storms tables live only on `chd-rasterstats-prod`) and three Storm Alert sends were lost. `DSCI_AZ_DB_PROD_HOST` was pointed back at `chd-rasterstats-prod` at 20:46 UTC. **Do not repoint those secrets without the team lead's say-so**; a "table does not exist" failure across many jobs at once is the signature of this, not of a schema bug. Note also that `chd-rasterstats-prod` has `max_connections = 50` — a job that opens an engine per query exhausts it on its own (see [hti-hurricanes-monitoring](../pipelines/hti-hurricanes-monitoring.md) and the fix in [ds-aa-hti-hurricanes#24](https://github.com/OCHA-DAP/ds-aa-hti-hurricanes/pull/24): one engine per process via `lru_cache`).

> **Consolidation plan (April 2026) — status unknown.** The dev/prod servers were to be consolidated onto one flexible server hosting `dev` and `prod` databases, presumably `ocha-chd-ds-prod`. As of 2026-09-25 nothing has been migrated: the team's data is still on `chd-rasterstats-{dev,prod}` and `ocha-chd-ds-prod` is a stale clone. <!-- TODO: confirm with OICT whether the consolidation is still planned; until then treat ocha-chd-ds-prod as off-limits -->
