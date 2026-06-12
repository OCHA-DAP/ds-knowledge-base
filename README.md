# ds-knowledge-base

The OCHA Centre for Humanitarian Data, Data Science team's institutional knowledge base — the single searchable home for our **methods, frameworks, pipelines, and infrastructure**. Built to be read by humans *and* by Claude.

It's the **hub**: summaries, cross-links, and the comparative view across all our work. Depth lives in the individual `ocha-dap` repos (the spokes); pages here link down to them.

## Layout

| Folder | Contents |
|---|---|
| `frameworks/` | AA frameworks & their versions — design and rationale |
| `pipelines/` | Living operational systems — ingests, monitoring, exposure (runbooks) |
| `apps/` | Deployed interactive surfaces (marimo/Dash/Quarto) on Azure / GH Pages |
| `methods/` | Cross-cutting how-we-work (the trigger typology lives here) |
| `infrastructure/` | Storage, DB, stratus/lens, GHA conventions |
| `catalog.md` | Generated index of all framework-versions |
| `docs/repo-manifest.md` | Ingestion work-list — what's in scope, what's ingested |

## Start here

- **Using/answering from the KB:** [CLAUDE.md](CLAUDE.md)
- **Adding or restructuring pages:** [INGESTION.md](INGESTION.md) — conventions, schemas, the one-home-per-fact rule
- **Pointing your local Claude Code at this:** [docs/global-claude-pointer.md](docs/global-claude-pointer.md)

## Status

Bootstrapping. Phase 0 (scaffold) complete; diverse-sample ingestion next. See `docs/repo-manifest.md` for progress.
