# Docs — how the KB works

Meta-documentation for the knowledge base itself: the conventions, the reasoning, and the
status. (The *content* lives in `frameworks/`, `pipelines/`, `apps/`, `analysis/`,
`methods/`, and `infrastructure/`.)

## Living docs — keep these current

| Page | What it's for |
|---|---|
| **[INGESTION.md](INGESTION.md)** | *How* knowledge enters the KB — frontmatter schemas, the one-home-per-fact rule, tag vocabularies, document authority & reconciliation, PDF handling, visibility. **Read this before adding or restructuring pages.** |
| **[DESIGN.md](DESIGN.md)** | *Why* — the architecture rationale and the dated **decision log** (every choice and what it rejected; the index at the top groups it by theme). Read before changing the approach; add a dated entry when you do. |
| **[ROADMAP.md](ROADMAP.md)** | *What's next* — the phases and current status. (Live counts live in the generated indexes, not here.) |
| **[PRIVACY.md](PRIVACY.md)** | *Public vs internal* — classification follows the **source**; public-source full-text is in-repo, internal-source content lives in the private companion repo. Read before ingesting any new source. |
| **[glossary.md](glossary.md)** | Terms and acronyms. |
| **[global-claude-pointer.md](global-claude-pointer.md)** | The global-config pointer that sends Claude here for team-knowledge questions. |

For automation (drift/freshness/discovery → `kb-ingest` PRs) see **[infrastructure/automation.md](../infrastructure/automation.md)**; the live status of the corpus is in the generated indexes (`catalog.md`, the pipeline registry, the dependency graph).

## Historical / reference snapshots — frozen, not auto-updated

Build-time artifacts from the ingestion phases. Kept because they're still useful to query (especially the repo→doc crosswalk), but they describe a phase that's complete — don't read them as current status.

| Page | What it's for |
|---|---|
| **[repo-doc-crosswalk.md](repo-doc-crosswalk.md)** | Which repo maps to which published framework doc — still the quickest repo→doc lookup. |
| **[repo-manifest.md](repo-manifest.md)** | The original ingestion work-list — scope decisions + per-repo last-push/ingested dates. |
| **[archive/](archive/README.md)** | Completed planning / one-time docs (phase-2 scope, repo audit) — history only. |

## The shape of it, in one line

Markdown in git, **hub-and-spoke**: this KB is the hub (summaries, cross-links, the
cross-framework comparison no single repo can hold); the `ocha-dap` repos are the spokes
(deep, code-adjacent detail). **One home per fact** — pages point via `source_repo`/`code_ref`,
never copy. See [DESIGN.md](DESIGN.md) for the full reasoning.
