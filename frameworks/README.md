# frameworks/

> **The AA portfolio record lives in [ds-aa-tracking](https://github.com/OCHA-DAP/ds-aa-tracking), not here** (the KB flip, 2026-09-28; D115). These pages were imported into its database (`aa.version_page`) and are edited there; nothing on these pages reaches the database any more — not `activations:`, `funding_rows:`, `valid_until:`, nor the backtest. Correct a framework, a version, an activation or a backtest through ds-aa-tracking (entry / admin pages, entries files). **New frameworks and versions are entered there too: framework documents come in only through ds-aa-tracking (D124).** KB automation re-syncs only the code layer of the pages already here (`source_branch`/`source_sha`, `code_ref`, discrepancies). What happens to this folder — moved, or generated from that database — is still open.

One folder per framework (`{iso3}-{hazard}/`), one page per version inside it, plus a `README.md` indexing the versions and their lineage.

Each folder `README.md` is **generated** by `scripts/gen_framework_readmes.py` (run after each ingest batch, alongside `scripts/gen_catalog.py`) — edit the version pages, not the README.

```
frameworks/
  bfa-drought/
    README.md          # the framework + version index + lineage (supersedes chain)
    v1/index.md
    v2/index.md
```

Copy `_TEMPLATE.md` for each new version page. See [../docs/INGESTION.md](../docs/INGESTION.md) for the schema and rules. The canonical trigger is the code at `code_ref` — these pages explain and compare, they don't redefine.
