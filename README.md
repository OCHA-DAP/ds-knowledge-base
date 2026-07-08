# ds-knowledge-base

**A single, searchable home for the OCHA Centre for Humanitarian Data — Data Science team's institutional knowledge:** how we build anticipatory-action frameworks, the triggers and monitoring behind them, the pipelines and apps that run them, and the infrastructure it all sits on.

Built to be read by **humans** (browse the markdown) *and* by **Claude** — point Claude at a clone, or connect to the team's hosted **[MCP connector](infrastructure/mcp-connectors.md)** and query the KB from Claude with no clone at all. The same files serve both.

---

## Why this exists

Our knowledge is scattered across three forms — **documents** (mostly PDFs), **code** (dozens of `ocha-dap` repos), and **infrastructure** (Azure, Databricks, a database) — and it lives in people's heads. This repo gathers it into one place where any of it can be found by searching, so that:

- a teammate (or Claude) can answer *"how did the Niger drought trigger work, and why those thresholds?"* without spelunking through a repo;
- the routine 80% of producing a framework or debugging a pipeline can be accelerated;
- we can eventually **publish** the parts that should be public (frameworks, triggers, monitoring).

It is **not** a chatbot or a trained model. It's a structured markdown corpus; "the agent" is just Claude reading these files.

## How it works

**Hub-and-spoke.** This repo is the *hub* — summaries, cross-links, and the cross-framework comparison no single repo can hold. The individual `ocha-dap` repos are the *spokes*, holding the deep, code-adjacent detail. **One home per fact:** pages here link to the canonical code/PDF via `source_repo`/`code_ref` rather than copying it.

Six content types:

| Folder | What's in it |
|---|---|
| [`frameworks/`](frameworks/) | AA frameworks & their versions — design, trigger logic, rationale (one page per version) |
| [`pipelines/`](pipelines/) | Living operational systems — data ingests, monitoring, alerts (runbooks) |
| [`apps/`](apps/) | Deployed interactive surfaces (marimo / Dash / Quarto) on Azure / GH Pages |
| [`analysis/`](analysis/) | Analysis repos that aren't frameworks or pipelines — regional overviews, ad-hoc activations, pre-framework exploration |
| [`methods/`](methods/) | Cross-cutting "how we do it" — e.g. the trigger typology |
| [`infrastructure/`](infrastructure/) | Conventions + registries: storage, database, deployments, the [pipeline registry](infrastructure/pipeline-registry.md), shared [libraries](infrastructure/libs/), the [MCP connector](infrastructure/mcp-connectors.md) |

A key design choice: **the latest published framework PDF is authoritative for the trigger**, and ingestion *reconciles* it against the repo (which can drift) — recording discrepancies rather than trusting either alone.

## Use it from Claude

- **Hosted MCP connector (no clone).** The KB is exposed as a remote MCP server; add it as a custom connector in claude.ai and query the KB from Claude directly — search, read, and Claude-Code-style code navigation across the frameworks/pipelines/infra pages and the generator code. Setup + URL: **[infrastructure/mcp-connectors.md](infrastructure/mcp-connectors.md)**. A separate, auth-gated tier will add read-only DB/blob access.
- **Point Claude Code at a clone.** Clone the repo and run Claude in it — same files, full grep/read over everything.

## Current stage

The corpus is substantially built. The **framework set is complete** (see [`catalog.md`](catalog.md)), the **systems back-catalogue** is ingested (pipelines, apps, shared libraries) alongside pre-framework / regional **[`analysis/`](analysis/)**, and the cross-cutting layers are in place: the [dependency graph + blast radius](infrastructure/dependency-graph.md), the [trigger typology](methods/), and a generated [pipeline registry with live health](infrastructure/pipeline-registry.md). Automation runs daily [drift](.github/workflows/drift-check.yml) + weekly PDF-freshness checks, and public framework-PDF full-text is persisted in [`raw/`](raw/) for grepping. The **public MCP connector is live** (above); ingesting the team's documents / Google Drive is in progress (under [PRIVACY.md](docs/PRIVACY.md)).

For the authoritative live status see **[docs/ROADMAP.md](docs/ROADMAP.md)**.

## Read more

| To understand… | Read |
|---|---|
| **Why** it's built this way — the rationale + full decision log | [docs/DESIGN.md](docs/DESIGN.md) |
| **What's next** — phases and current status | [docs/ROADMAP.md](docs/ROADMAP.md) |
| **How** to add or restructure a page — conventions & schema | [INGESTION.md](docs/INGESTION.md) |
| How **Claude** should use this repo | [CLAUDE.md](CLAUDE.md) |
| How to **connect Claude** to the KB (MCP connector + tiers) | [infrastructure/mcp-connectors.md](infrastructure/mcp-connectors.md) |
| What's in scope to ingest, and progress | [docs/repo-manifest.md](docs/repo-manifest.md) |

## Want to change or add something? (the simple way)

The pages are machine-ingested and reviewed but **not infallible** — flagging mistakes is how the KB earns trust.

- **Just open an issue** ([the *KB error or feedback* form](../../issues/new/choose)) describing what you want changed or added. The **KB steward** (headless Claude) reads the issue **and its comments** and drafts the change as a review PR — or, if it needs a source/decision it doesn't have, **comments asking you**. For an error, point to the authoritative source; for a decision, just **comment the answer on the issue** and the next run applies it. You review the PR; **nothing auto-merges**.
  - No label needed — any issue a **team member** (repo write/admin) opens is picked up automatically. Add a `discuss` (or `no-autofix`) label if you just want to talk it through without a draft.
  - **From outside the team?** Your feedback is welcome and read by a maintainer first — for safety the steward doesn't auto-act on issues from non-members; a maintainer triages it (replies or tags `kb-autofix`) and then it's drafted the same way.
- **Prefer to do it yourself?** Edit the page and open a PR (each page links its sources — `code_ref`, the framework PDF — so corrections can be checked).
- **Automated checks** also file issues the steward resolves — `kb-validity` (a framework past its validity period), `kb-docs` (the how-it-works docs drifted), `kb-new-repos` / `kb-coverage` / `kb-aa-watch` (new things to bring in). (Deterministic re-syncs like a moved source or a newer PDF go straight to a `kb-ingest` PR instead.) See [infrastructure/automation.md](infrastructure/automation.md) for the full self-maintenance map.

---

*Much of this repo is assembled and maintained with Claude working over the team's repos and the published framework documents — that workflow is itself part of what's being built here.*
