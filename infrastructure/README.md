# infrastructure/

Team-wide conventions and the shared services everything sits on. Reference material, stable, few pages.

- [conventions.md](conventions.md) — naming, time/leadtime, CRS, admin boundaries, Python
- [storage.md](storage.md) — blob access & path convention (`ocha-stratus`)
- [database.md](database.md) — DB access, SSL/commit gotchas, what's in the DB
- [deployments.md](deployments.md) — runtime registry: Azure web apps + Databricks jobs, cross-linked to repos
- [comms-listmonk.md](comms-listmonk.md) — email/alerts: self-hosted Listmonk + the `ocha-relay` library

Datasets get a thin page under `datasets/` here **only** when a shared fact (resolution, leadtime/CRS quirk, licensing) would otherwise be duplicated across pages — otherwise they stay as tags. See [../docs/INGESTION.md](../docs/INGESTION.md).
