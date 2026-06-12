# ds-knowledge-base — read this first

The OCHA Centre for Humanitarian Data, Data Science team knowledge base. The single searchable home for our methods, frameworks, pipelines, and infrastructure — the institutional knowledge that otherwise lives in people's heads, scattered repos, and PDFs.

This is the **hub**. Individual `ocha-dap` repos are the **spokes** (deep, code-adjacent detail). This KB holds summaries, cross-links, and the comparative layer no single repo can have.

## How to use this when answering

1. **Search before answering.** Grep/read this repo for methods, past frameworks, pipeline runbooks, and infra conventions. Don't answer team-knowledge questions from memory.
2. **Pull only what you need.** Read the specific page, not everything — keep context lean. Follow `code_ref` / `source_repo` *down* into the actual repo when you need depth the summary doesn't have.
3. **Raw is always reachable.** Every page links its sources (`code_ref`, `pdf`). If the summary is insufficient, open the linked code or PDF full-text and read it.
4. **If something's missing or stale, leave a stub** (`<!-- TODO: ... -->`) rather than moving on silently. Using the KB is how we find its gaps.
5. **After real work, update the affected page** (capture-as-you-go). Repo `CLAUDE.md` first, summary here second.

## Map

- `frameworks/` — AA frameworks & their versions (design + rationale). One folder per framework, one page per version.
- `pipelines/` — living operational systems (ingests, monitoring, exposure, apps). Runbooks.
- `methods/` — cross-cutting how-we-work. The trigger typology lives here.
- `infrastructure/` — storage, DB, stratus/lens, GHA conventions.
- `catalog.md` — generated index of all framework-versions (filterable).
- `docs/repo-manifest.md` — the ingestion work-list (what's in scope, what's done).
- `glossary.md` — terms.

## Conventions

All conventions — frontmatter schemas, the one-home-per-fact rule, tag vocabularies, PDF handling, visibility, drift sync — are in **[INGESTION.md](INGESTION.md)**. Read it before adding or restructuring pages.
