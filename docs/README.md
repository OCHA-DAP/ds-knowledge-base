# Docs — how the KB works

Meta-documentation for the knowledge base itself: the conventions, the reasoning, and the
status. (The *content* lives in `frameworks/`, `pipelines/`, `apps/`, `analysis/`,
`methods/`, and `infrastructure/`.)

## What's here

| Page | What it's for |
|---|---|
| **[INGESTION.md](INGESTION.md)** | *How* knowledge enters the KB — frontmatter schemas, the one-home-per-fact rule, tag vocabularies, document authority & reconciliation, PDF handling, visibility. **Read this before adding or restructuring pages.** |
| **[DESIGN.md](DESIGN.md)** | *Why* — the architecture rationale and the dated **decision log** (every choice and what it rejected). Read before changing the approach; add a dated entry when you do. |
| **[ROADMAP.md](ROADMAP.md)** | *What's next* — the phases, current status, and the ingestion-progress table. |
| **[PRIVACY.md](PRIVACY.md)** | *Public vs internal* — classification follows the **source**; public-source full-text is in-repo, internal-source content lives in the private companion repo. Read before ingesting any new source. |
| **[glossary.md](glossary.md)** | Terms and acronyms. |
| **[repo-manifest.md](repo-manifest.md)** | The ingestion work-list — what's in scope, cloned, and done, per repo. |
| **[repo-audit.md](repo-audit.md)** | Structural completeness per repo. |
| **[repo-doc-crosswalk.md](repo-doc-crosswalk.md)** | Which repo maps to which published framework doc. |
| **[PHASE2-SCOPE.md](PHASE2-SCOPE.md)** | Scope notes from the broad-ingestion phase. |
| **[global-claude-pointer.md](global-claude-pointer.md)** | The global-config pointer that sends Claude here for team-knowledge questions. |

## The shape of it, in one line

Markdown in git, **hub-and-spoke**: this KB is the hub (summaries, cross-links, the
cross-framework comparison no single repo can hold); the `ocha-dap` repos are the spokes
(deep, code-adjacent detail). **One home per fact** — pages point via `source_repo`/`code_ref`,
never copy. See [DESIGN.md](DESIGN.md) for the full reasoning.
