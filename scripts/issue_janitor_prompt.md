You are resolving ONE GitHub issue for this knowledge base by editing the repo in place. The issue
(title, body, labels) and its full comment thread are appended below. Another step turns whatever you
change in the working tree into a PR that closes the issue — so **just make the edits; do not commit**.

## First, understand the rules
Read these before editing: `CLAUDE.md`, `docs/INGESTION.md`, `docs/PRIVACY.md`. Key ones:
- **One home per fact** — fix the fact where it lives; don't duplicate.
- **Framework trigger authority is the published PDF**; reconcile, record discrepancies, don't smooth over.
- **OCHA/CERF ownership** gates what counts as a framework (D53).
- **PRIVACY**: never add internal-sourced content to this public repo.
- Counts/indexes are generated — if you change framework/page data, you may run the matching generator
  (`scripts/gen_catalog.py`, `scripts/gen_doc_counts.py`, etc.) so indexes stay consistent.

## How to resolve
1. Work out what the issue asks: an error correction (kb-feedback), code/doc drift (kb-drift,
   kb-pdf-freshness, kb-docs), a framework past validity (kb-validity), coverage/discovery, etc.
2. **The comment thread may carry the authoritative answer or a maintainer's decision** — prefer the
   most recent maintainer instruction over the original body. If a maintainer says "the correct value
   is X, source: <link>", apply exactly that.
3. **Verify before you change a fact.** Every factual edit must be backed by a source named in the
   issue/comments, or one you confirm via the repo / WebSearch / WebFetch. If a claimed error has no
   verifiable source and no maintainer decision, do **not** guess.

## When NOT to edit (leave the tree clean)
- You can't verify the change from a cited/authoritative source or a maintainer decision.
- It needs a human judgment call that hasn't been made in the comments (e.g. "renew / supersede /
  retire?" with no answer yet).
- It requires drafting a whole new page from a repo/PDF you can't access in this run (that's the
  `kb-ingest` path, not this one) — note that, but make no partial/fabricated page.
- It's out of repo scope, or would require adding internal content to this public repo.

Making NO edits is a valid, expected outcome — the janitor will flag the issue as needing a human
(or more info) rather than open a low-confidence PR. **Never invent figures, thresholds, dates, or
sources.** Keep edits minimal and scoped to exactly what the issue calls for.
