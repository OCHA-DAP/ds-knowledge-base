# raw/ — full-text extracts of public source documents

Greppable plain-text extractions of **already-public** source documents, kept in-repo so a buried detail is always reachable (`grep -r foo raw/`) without re-fetching. This honours the KB's "raw is always reachable" rule.

**Everything here is public by construction** — it is the text of documents already published openly. Per [docs/PRIVACY.md](../docs/PRIVACY.md), classification follows the source: these come from public PDFs (ReliefWeb / unocha), so their extracts are public. **Internal-source extracts (e.g. Google Drive) do NOT go here** — they live in the gitignored `drive/` cache + private store.

## What's here

- `raw/frameworks/<framework>/<version>.txt` — `pdftotext` of each framework's published `framework_doc` PDF. The page at `frameworks/<framework>/<version>.md` points to it via `raw_extract`.

## Canonical source & refresh

The **canonical** document is still the `framework_doc` URL on the page — this is a *cache*, not the source of truth. Regenerate / refresh it from the published PDFs:

```bash
python3 scripts/gen_framework_extracts.py          # re-extract all public framework PDFs
python3 scripts/gen_framework_extracts.py --check  # report missing extracts, write nothing
```

Skipped (correctly absent here): repo-only/development versions (`framework_doc: null`) and the **non-public-doc** frameworks (mmr/vut/yem — `extra.doc_status`), whose extracts are internal.
