---
content_type: infrastructure
last_reviewed: "2026-06-29"   # bump when a human verifies the page is still accurate
---

# infrastructure/

Team-wide conventions and the shared services everything sits on. Reference material, stable, few pages.

- [conventions.md](conventions.md) — naming, time/leadtime, CRS, admin boundaries, Python, git/PR workflow
- [storage.md](storage.md) — blob access & path convention (`ocha-stratus`)
- [database.md](database.md) — DB access, SSL/commit gotchas, what's in the DB
- [deployments.md](deployments.md) — runtime registry: Azure web apps, Function Apps/SWAs + Databricks jobs, cross-linked to repos
- [token-issuer.md](token-issuer.md) — `chd-ds-token-issuer`: shared keyless SAS minter for client-side-blob web apps (ephemeral, scoped, rotating tokens)
- [comms-listmonk.md](comms-listmonk.md) — email/alerts: self-hosted Listmonk + the `ocha-relay` library
- [automation.md](automation.md) — how the KB keeps itself current: generators (auto-commit) · drift/freshness · discovery, and the detect→Claude-draft→PR fix loop

Datasets get a thin page under `datasets/` here **only** when a shared fact (resolution, leadtime/CRS quirk, licensing) would otherwise be duplicated across pages — otherwise they stay as tags. See [../docs/INGESTION.md](../docs/INGESTION.md).
