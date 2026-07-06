# Drive index — pointer (the catalog is in the private repo)

The Data Science team shared-drive manifest is **internal**, not in this public repo.

A full crawl is ~9.7k file entries (the whole team drive minus obvious data) and
includes partner/collaboration filenames — more volume and exposure than a public
catalog should carry — so per [docs/PRIVACY.md](../docs/PRIVACY.md) (D44b/D45/D46) it lives in
the **private companion repo**, versioned and access-controlled:

**→ [`OCHA-DAP/ds-knowledge-base-internal`](https://github.com/OCHA-DAP/ds-knowledge-base-internal)** · `drive/drive-index.md` (+ `drive-index.json`)

That link is access-gated: a public visitor sees that the internal catalog exists and
where; only someone with access to that repo can open it. (Same model as the Drive
share-links themselves.)

Generate / refresh it from this repo (read-only, headless — writes into the private
repo clone; see [`scripts/README.md`](../scripts/README.md) → "Drive manifest" for auth):

```sh
GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_drive_index.py
scripts/drive_refresh.sh        # crawl + commit to the private repo (git diff = the drift record)
```

**Scope** (knowledge, not data): the **whole** DS team shared drive
(`0AGYkOFcloQuyUk9PVA`) **except obvious data**. Excluded: the separate
data-storage drive; any folder literally named `data` (its whole subtree — this
catches `General - All AA projects / Data` and nested `*/data/` pockets inside
collaborations, present and future); and a short list of data-only subtrees that
aren't named `data` (a couple of dataset-only collaboration folders and
`Climate Data / Other datasets`). Everything else is catalogued — including the
`HDX Signals` and `Climate Data` **project** folders (docs, slides, meeting notes;
"Climate Data" is a program folder, not rasters) and the rest of `Collaborations`
(mostly slides/PDFs/docs). The exact exclusion list lives in `scripts/gen_drive_index.py`
(`EXCLUDE_SEGMENT_NAMES` + `EXCLUDE_PATHS`).

Document **content** extraction is a further internal step (Phase 7c), also in the
private repo. Promoting any individual item to this public repo is an explicit,
per-item human decision.
