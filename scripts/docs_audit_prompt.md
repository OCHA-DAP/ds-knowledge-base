You are auditing this knowledge base's *how-it-works* documentation for staleness, then fixing what is VERIFIABLY out of date. Scope is ONLY these meta-docs:

- README.md, CLAUDE.md
- docs/DESIGN.md, docs/INGESTION.md, docs/ROADMAP.md, docs/PRIVACY.md, docs/README.md, docs/glossary.md, docs/USING.md, docs/I18N.md
- infrastructure/automation.md, scripts/README.md
- infrastructure/mcp-connectors.md, infrastructure/usage.md, infrastructure/deployments.md, infrastructure/drive-index.md
- claude/README.md

Do NOT edit content pages (frameworks/, pipelines/, apps/, analysis/, methods/, or infrastructure/* other than the pages listed above).

The deterministic checker has already run; its findings are in `docs-report.md` (read it first). `gen_doc_counts.py` has already refreshed the COUNTS block — do not hand-edit counts.

Check each meta-doc against the ACTUAL repo state — **verify against ground truth, don't just read the docs for internal consistency** (the Aug-2026 sweep, PR #521, found ~50 stale claims that pure doc-reading missed; use Bash/Grep/Read — never guess):

- **What shipped recently:** `git log --oneline -60` and recently merged PRs. Anything the docs describe as future/planned/"will add"/"not yet" that has since landed is the highest-value fix — forward-looking claims rot fastest.
- **Workflows vs automation.md:** `.github/workflows/*.yml` (names, active vs commented-out `schedule:` crons, what each step runs) against the "every automation at a glance" table AND the prose sections. The deterministic checker diffs names/cadences; you check the *descriptions* (does the row still say what the workflow does?).
- **Live-state snapshots as evidence:** the generated `infrastructure/db-schema*.md`, `infrastructure/pipeline-registry.md`, and `infrastructure/deployments.md` are fresh ground truth — e.g. a table with rows in the DB snapshot disproves any "not yet enabled" claim about it.
- **Counts and enumerations stated in prose:** "N plugins", "N content types", "the four axes" — recount against disk (`.claude-plugin/marketplace.json`, top-level dirs, automation.md's own axis list). Docs disagreeing with *each other* on a count means at least one is wrong.
- **Self-contradictions within one page:** a heading disagreeing with its body, a sentence disagreeing with the table below it. These are always bugs — fix the stale side.
- **ROADMAP phases / Now / Next:** is a phase marked todo that has actually shipped? a "Next" that promises something already live? Cross-check against `scripts/`, `.github/workflows/`, and the generated indexes.
- **DESIGN "Open questions":** any now resolved by a later decision? Mark them RESOLVED (do not delete).
- **Dangling references** (see MISSING-REF in the report): a `scripts/`/`workflows/`/file path named in prose that no longer exists → fix the path.
- **Cross-references** between docs that point at the wrong place.

When you substantively re-verify one of the `infrastructure/` pages above against reality, bump its `last_reviewed` frontmatter date.

HARD RULES:

- The DESIGN decision log is APPEND-ONLY history — never delete or rewrite past decisions. (An inline "*→ superseded by Dnn*" marker on a stale sub-point is allowed.)
- Only change what you can verify is stale. If a statement is still true, leave it EXACTLY as is.
- This is not a copy-edit / restyle pass — minimal, surgical edits only.
- If nothing is verifiably stale, make NO edits at all.

Make the edits directly with the Edit tool.
