---
name: kb-update
description: >-
  Add or update a page in this knowledge base (ds-knowledge-base) — a framework,
  pipeline, app, analysis, method, or infrastructure page. Use for capture-as-you-go
  after finishing framework/pipeline work, for fixing a page flagged stale by the
  drift/PDF-freshness bots (kb-drift / kb-pdf-freshness issues), or for ingesting a
  new source. This is the WRITE procedure; the read-first rules are in the repo's
  top-level CLAUDE.md.
---

# Updating the knowledge base

This skill is the **procedure** for writing a page correctly and leaving the repo
consistent. It does **not** restate the schema or conventions — those have one home
each, and you read them as part of the procedure:

- **`docs/INGESTION.md`** — the *how*: one-home-per-fact, document authority &
  reconciliation, branch handling, activations, discrepancy prefixes, visibility.
  **Read this before adding or restructuring any page.**
- **`<type>/_TEMPLATE.md`** — the frontmatter schema + locked headings for that
  content type (`frameworks/`, `pipelines/`, `apps/`, `analysis/`). Copy the
  matching template; keep every heading even when the answer is "n/a".
- **`docs/DESIGN.md`** — the *why*. Read before changing the *approach* (not a
  single page); add a dated decision-log entry if you do.
- **`scripts/README.md`** — what each generator/check produces.

If a rule below seems to conflict with `INGESTION.md`, `INGESTION.md` wins — fix
this skill.

## Procedure

1. **Pick the content type → copy its template.** Decide framework vs pipeline vs
   app vs analysis vs method/infrastructure using the table in `INGESTION.md`.
   `frameworks/`, `pipelines/`, `apps/`, `analysis/` each have a `_TEMPLATE.md` —
   copy it. `methods/` and `infrastructure/` are free prose with no template. The
   distinction that trips people up: a page is a `framework` **only if a published
   framework doc exists for that specific thing** — otherwise it's `analysis/`.

2. **Decide hub vs spoke before writing a word** (one-home-per-fact). Operational,
   code-coupled detail belongs in the **source repo** (its `CLAUDE.md`/`docs/`),
   not here. This hub carries the comparative + reconciliation layer and links
   down via `source_repo`/`code_ref`. For capture-as-you-go: **update the source
   repo's `CLAUDE.md` first, this hub page second.** If you're about to write the
   same fact on a second page, stop and link instead.

3. **Read the authoritative source, not the README.** For frameworks the latest
   framework PDF is authoritative for the trigger; the repo derives/implements it.
   **Survey branches (`git branch -a`, sort by date) — work is usually NOT on
   `main`.** Read the active branch; record `source_branch` and `source_sha`.
   Ingestion is *reconciliation, not transcription* — record where repo and doc
   disagree, don't smooth it.

4. **Fill the template honestly.**
   - Set `visibility` (`internal`/`public`) at creation — default `internal` when
     unsure (see `docs/PRIVACY.md`).
   - Prefix every `discrepancies` entry `[stale]` / `[conflict]` / `[gap]`.
   - Don't default `activations: []` without hunting (PDF + repo + CERF/web). For
     multi-country, name **every** activating country (ISO3 **and** full name) in
     the note, and set `full_activation: false` for a partial-window trigger.
   - Leave `<!-- TODO: ... -->` stubs for facts you can't source — never assert or
     silently omit.

5. **Validate + regenerate (don't hand-edit generated files).** From repo root run
   the post-batch routine in `scripts/README.md`:
   ```bash
   python scripts/gen_catalog.py            # also parses every page's YAML — fails loudly on bad frontmatter
   python scripts/gen_framework_readmes.py
   python scripts/gen_issue_form.py
   python scripts/gen_dependency_graph.py
   ```
   If you touched a framework's status/activations, also regenerate the public site
   (`python scripts/gen_public_site.py`) and **confirm the endorsed version still
   drives the map** — see the two activation-hiding invariants in
   `scripts/README.md` / `INGESTION.md`.

6. **If you adapt the schema itself**, do it as a deliberate sweep across all pages
   (not page-by-page drift), and log it in `docs/DESIGN.md`.

## Not this skill

- *Reading* the KB to answer a question → top-level `CLAUDE.md`, no skill needed.
- *Detecting* staleness → the `drift-check` / `pdf-freshness` GHAs already file
  `kb-drift` / `kb-pdf-freshness` issues. This skill is how you *fix* one.
- Bulk re-ingestion of many sources → the `workflows/ingest-*.mjs` orchestration.
