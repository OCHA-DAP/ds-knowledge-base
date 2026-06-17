# frameworks/

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
