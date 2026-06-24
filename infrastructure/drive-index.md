# Drive index — pointer (the catalog is internal)

The Data Science team shared-drive manifest is **internal**, not in this public repo.

A full crawl is ~9k entries (after dropping bulk-data folders) and includes
partner/collaboration filenames — more volume and exposure than a public catalog
should carry — so per [docs/PRIVACY.md](../docs/PRIVACY.md) (D44b/D45) it lives in
the **gitignored internal store**:

```
drive/drive-index.md       human catalog (grouped by folder path)
drive/.drive-index.json    machine-readable manifest
```

Generate / refresh it (read-only, headless — see the auth note in
[`scripts/README.md`](../scripts/README.md) → "Drive manifest"):

```sh
GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_drive_index.py
GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_drive_index.py --check   # drift guard
```

**Scope** (knowledge, not data): only the DS team shared drive
(`0AGYkOFcloQuyUk9PVA`); excludes the separate data-storage drive, the bulk-data
root folders (`HDX Signals`, `Climate Data`, `Collaborations`), and
`General - All AA projects / Data`.

Document **content** extraction is a further internal step (Phase 7c). Promoting
any individual item to the public repo is an explicit, per-item human decision.
