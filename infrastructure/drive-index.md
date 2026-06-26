# Drive index — pointer (the catalog is in the private repo)

The Data Science team shared-drive manifest is **internal**, not in this public repo.

A full crawl is ~9k entries (after dropping bulk-data folders) and includes
partner/collaboration filenames — more volume and exposure than a public catalog
should carry — so per [docs/PRIVACY.md](../docs/PRIVACY.md) (D44b/D45/D46) it lives in
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

**Scope** (knowledge, not data): only the DS team shared drive
(`0AGYkOFcloQuyUk9PVA`); excludes the separate data-storage drive, the bulk-data
root folders (`HDX Signals`, `Climate Data`, `Collaborations`), and
`General - All AA projects / Data`.

Document **content** extraction is a further internal step (Phase 7c), also in the
private repo. Promoting any individual item to this public repo is an explicit,
per-item human decision.
