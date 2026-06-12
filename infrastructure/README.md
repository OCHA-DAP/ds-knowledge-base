# infrastructure/

Team-wide conventions and the shared services everything sits on. Reference material, stable, few pages.

- [conventions.md](conventions.md) — naming, time/leadtime, CRS, admin boundaries, Python
- [storage.md](storage.md) — blob access & path convention (`ocha-stratus`)
- [database.md](database.md) — DB access, SSL/commit gotchas, what's in the DB

Datasets get a thin page under `datasets/` here **only** when a shared fact (resolution, leadtime/CRS quirk, licensing) would otherwise be duplicated across pages — otherwise they stay as tags. See [../INGESTION.md](../INGESTION.md).
