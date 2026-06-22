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
- `pipelines/` — living operational systems (ingests, monitoring, exposure). Runbooks.
- `apps/` — deployed interactive surfaces (marimo/Dash/Quarto) on Azure / GH Pages.
- `analysis/` — repos that are analysis, **not** frameworks or pipelines (regional overviews, ad-hoc activations, pre-framework exploration). A page is a `framework` only if it has its own published framework doc.
- `methods/` — cross-cutting how-we-work. The trigger typology lives here.
- `infrastructure/` — storage, DB, stratus/lens, GHA conventions.
- `infrastructure/libs/` — reference pages for the shared Python libraries (`ocha-stratus/lens/relay/anticipy`, `ds-toolkit`, `ocha-mailchimp`): purpose, install + auth, key API, used-by.
- `catalog.md` — generated index of all framework-versions (filterable).
- `infrastructure/dependency-graph.md` — generated cross-type dependency graph + **blast radius** ("if X breaks, what's affected"), from `depends_on` edges + DB tables (pipelines write, apps read).
- `infrastructure/db-schema.md` (+ `db-schema-dev.md`) — generated daily read-only snapshots of the Postgres **prod** / **dev** DBs (schemas → tables → columns + row counts + sizes).
- `infrastructure/spoke-repos.md` — generated registry of every spoke `source_repo` and its GitHub visibility; **marks the private/internal spokes** (the ones the drift bot can't read with the default CI token).
- `docs/repo-manifest.md` — the ingestion work-list (what's in scope, what's done).
- `docs/repo-audit.md` — structural completeness per repo.
- `docs/glossary.md` — terms.

## Approach, conventions & status

- **[INGESTION.md](docs/INGESTION.md)** — *how*: frontmatter schemas, one-home-per-fact, tag vocabularies, document authority & reconciliation, PDF handling, visibility, drift sync. Read before adding or restructuring pages.
- **[docs/DESIGN.md](docs/DESIGN.md)** — *why*: architecture rationale, the dated decision log, open questions. Read before changing the approach; add a dated entry when you do.
- **[docs/ROADMAP.md](docs/ROADMAP.md)** — *what's next*: phases and current status. Update as work lands.
