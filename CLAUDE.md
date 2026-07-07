# ds-knowledge-base — read this first

The OCHA Centre for Humanitarian Data, Data Science team knowledge base. The single searchable home for our methods, frameworks, pipelines, and infrastructure — the institutional knowledge that otherwise lives in people's heads, scattered repos, and PDFs.

This is the **hub** (public). Individual `ocha-dap` repos are the **spokes** (deep, code-adjacent detail). This KB holds summaries, cross-links, and the comparative layer no single repo can have. Internal-sourced material (the Google Drive manifest, content extracts, and slide-visual captions, kept current by a daily sync) lives in the **private companion repo `ds-knowledge-base-internal`**, which this public repo references by access-gated pointer — never inlines (see [docs/PRIVACY.md](docs/PRIVACY.md)).

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
- `analysis/` — repos that are analysis, **not** frameworks or pipelines (regional overviews, ad-hoc activations, pre-framework exploration). A page is a `framework` only if it's an **OCHA/CERF-owned** AA framework in the portfolio (D51/D53) — a published doc is preferred but not required (historical pilots count); IFRC/government early action and plain CERF allocations do not.
- `methods/` — cross-cutting how-we-work: **trigger design & validation** (vocabulary — "activated", mechanism vs specific triggers, readiness/action; the spec→analysis→report process; mandatory historical analysis with BOTH impact and indicator records), **return periods** (Weibull; individual vs overall vs effective RP and their ≤/≥ relations; all-in vs split funding), and the **trigger typology**.
- `infrastructure/` — storage, DB, stratus/lens, GHA conventions.
- `infrastructure/libs/` — reference pages for the shared Python libraries (`ocha-stratus/lens/relay/anticipy`, `ds-toolkit`, `ocha-mailchimp`): purpose, install + auth, key API, used-by.
- `infrastructure/datasets/` — reference pages for **third-party data sources we consume but don't produce** (IPC/CH, HDX, HRP/HNRP, FEWS NET, EM-DAT, WorldPop, FAO ASI/VHI, GHSL): access/API + auth, resolution, license, the loader we use, used-by. Sources we ingest via our own pipeline live on the pipeline page, not here.
- `catalog.md` — generated index of all framework-versions (filterable).
- `infrastructure/dependency-graph.md` — generated cross-type dependency graph + **blast radius** ("if X breaks, what's affected"), from `depends_on` edges + DB tables (pipelines write, apps read).
- `infrastructure/databricks.md` — the compute platform: workspace, compute policies, clusters, **the two-axis dev/prod model** (deployment target vs data-plane `--mode`), DAB conventions.
- `infrastructure/pipeline-registry.md` — **generated** authoritative registry + **live health** of every deployed scheduled pipeline (Databricks + GHA), one row per job, keyed by runtime handle; last-success-vs-cadence health "keeps the trains on the tracks". Supersedes the `pipelines-status` dashboard.
- `infrastructure/db-schema.md` (+ `db-schema-dev.md`) — generated daily read-only snapshots of the Postgres **prod** / **dev** DBs (schemas → tables → columns + row counts + sizes).
- `infrastructure/spoke-repos.md` — generated registry of every spoke `source_repo` and its GitHub visibility; **marks the private/internal spokes** (the ones the drift bot can't read with the default CI token).
- `infrastructure/automation.md` — **how the KB keeps itself current**: the four axes (deterministic generators that auto-commit · drift/freshness · discovery · **usage**), the **detect→Claude-draft→PR** fix loop (`kb-ingest`, headless Claude on the Max plan), the tracking-issue labels, schedules, secrets, and the **comprehensiveness scope** (full OCHA/CERF AA portfolio, incl. historical pilots).
- `infrastructure/usage.md` — **the usage axis**: per-tool-call telemetry from the MCP (`kb_usage.events`) → weekly improvement digest (`analyze_usage.py` → `kb-usage` issue). Zero-result searches → missing/mis-titled pages; routes to KB-organisation *and* MCP-behaviour fixes. Write path uses a dedicated INSERT-only role (read-only MCP posture preserved); no-ops until enabled.
- `docs/repo-manifest.md` — the ingestion work-list (what's in scope, what's done).
- `docs/repo-audit.md` — structural completeness per repo.
- `docs/glossary.md` — terms.

## Approach, conventions & status

- **[INGESTION.md](docs/INGESTION.md)** — *how*: frontmatter schemas, one-home-per-fact, tag vocabularies, document authority & reconciliation, PDF handling, visibility, drift sync. Read before adding or restructuring pages.
- **[docs/DESIGN.md](docs/DESIGN.md)** — *why*: architecture rationale, the dated decision log, open questions. Read before changing the approach; add a dated entry when you do.
- **[docs/ROADMAP.md](docs/ROADMAP.md)** — *what's next*: phases and current status. Update as work lands.
- **[docs/PRIVACY.md](docs/PRIVACY.md)** — *public vs internal*: classification follows the source; public-source full-text → in-repo `raw/`. Google Drive **content and the bulk manifest are internal** — they live in the **private companion repo `ds-knowledge-base-internal`** (the ~9k-entry catalog of partner/project filenames is too much aggregate exposure for the public repo); the public repo carries only a **pointer** at `infrastructure/drive-index.md`. Read before ingesting any new source.
