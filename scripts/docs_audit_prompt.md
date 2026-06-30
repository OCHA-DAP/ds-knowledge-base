You are auditing this knowledge base's *how-it-works* documentation for staleness, then fixing what is VERIFIABLY out of date. Scope is ONLY these meta-docs:

- README.md, CLAUDE.md
- docs/DESIGN.md, docs/INGESTION.md, docs/ROADMAP.md, docs/PRIVACY.md, docs/README.md, docs/glossary.md
- infrastructure/automation.md, scripts/README.md

Do NOT edit content pages (frameworks/, pipelines/, apps/, analysis/, methods/, or infrastructure/* other than automation.md).

The deterministic checker has already run; its findings are in `docs-report.md` (read it first). `gen_doc_counts.py` has already refreshed the COUNTS block — do not hand-edit counts.

Check each meta-doc against the ACTUAL repo state (use Bash/Grep/Read to verify — never guess):

- **ROADMAP phases / Now / Next:** is a phase marked todo that has actually shipped? a status that no longer holds? Cross-check against `scripts/`, `.github/workflows/`, and the generated indexes.
- **DESIGN "Open questions":** any now resolved by a later decision? Mark them RESOLVED (do not delete).
- **Dangling references** (see MISSING-REF in the report): a `scripts/`/`workflows/`/file path named in prose that no longer exists → fix the path.
- **Cross-references** between docs that point at the wrong place.

HARD RULES:

- The DESIGN decision log is APPEND-ONLY history — never delete or rewrite past decisions.
- Only change what you can verify is stale. If a statement is still true, leave it EXACTLY as is.
- This is not a copy-edit / restyle pass — minimal, surgical edits only.
- If nothing is verifiably stale, make NO edits at all.

Make the edits directly with the Edit tool.
