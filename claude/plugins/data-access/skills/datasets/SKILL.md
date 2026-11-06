---
name: datasets
description: Load third-party humanitarian data the team already knows — IPC/CH, HDX, HRP/HNRP, FEWS NET, EM-DAT, WorldPop, FAO ASI/VHI, GHSL, and the pipeline-ingested sources. Use BEFORE writing any scraper, downloader, or API client for an external source — the KB records the loader we use, its auth, resolution, and license.
---

# Third-party datasets — don't reinvent the loader

Before writing a fetcher for an external data source, check the KB — there is very
likely an existing access pattern:

- **`infrastructure/datasets/`** — one page per source we consume ad-hoc (IPC/CH,
  HDX, HRP/HNRP, FEWS NET, EM-DAT, WorldPop, FAO ASI/VHI, GHSL): access/API + auth,
  resolution, license, the loader we use, and which team pages depend on it.
- **Sources we ingest via our own pipelines** are documented on the pipeline page
  instead: IMERG, FloodScan, ACLED, NHC, IBTrACS/SEAS5/ERA5, GDACS/GloFAS —
  see `pipelines/` and `infrastructure/pipeline-registry.md`. If a pipeline already
  lands it in our blob/DB, read it from there (the `blob-io` skill), not from the
  upstream source.

## Rules

1. **Reuse the documented loader** (usually `hdx-python-api`, a source API client, or
   `ocha-stratus`/`ocha-lens`); follow the page's auth pattern (env vars, never
   hardcoded keys).
2. **Do NOT use `ocha-anticipy`** — deprecated. `hdx-python-api`, the FDW API,
   stratus, or lens instead.
3. **Check the license note** on the dataset page before redistributing or
   publishing derived outputs.
4. **No page for your source?** Write the fetcher, then leave a
   `<!-- TODO: dataset page -->` stub or open an issue on
   `OCHA-DAP/ds-knowledge-base` so the next person finds it.
