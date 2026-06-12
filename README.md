# ds-knowledge-base

**A single, searchable home for the OCHA Centre for Humanitarian Data — Data Science team's institutional knowledge:** how we build anticipatory-action frameworks, the triggers and monitoring behind them, the pipelines and apps that run them, and the infrastructure it all sits on.

Built to be read by **humans** (browse the markdown, or a docs site later) *and* by **Claude** (pointed at this repo, it can answer team questions and accelerate framework/pipeline work) — the same files serve both.

---

## Why this exists

Our knowledge is scattered across three forms — **documents** (mostly PDFs), **code** (dozens of `ocha-dap` repos), and **infrastructure** (Azure, Databricks, a database) — and it lives in people's heads. This repo gathers it into one place where any of it can be found by searching, so that:

- a teammate (or Claude) can answer *"how did the Niger drought trigger work, and why those thresholds?"* without spelunking through a repo;
- the routine 80% of producing a framework or debugging a pipeline can be accelerated;
- we can eventually **publish** the parts that should be public (frameworks, triggers, monitoring).

It is **not** a chatbot or a trained model. It's a structured markdown corpus; "the agent" is just Claude reading these files.

## How it works

**Hub-and-spoke.** This repo is the *hub* — summaries, cross-links, and the cross-framework comparison no single repo can hold. The individual `ocha-dap` repos are the *spokes*, holding the deep, code-adjacent detail. **One home per fact:** pages here link to the canonical code/PDF via `source_repo`/`code_ref` rather than copying it.

Five content types:

| Folder | What's in it |
|---|---|
| [`frameworks/`](frameworks/) | AA frameworks & their versions — design, trigger logic, rationale (one page per version) |
| [`pipelines/`](pipelines/) | Living operational systems — data ingests, monitoring, alerts (runbooks) |
| [`apps/`](apps/) | Deployed interactive surfaces (marimo / Dash / Quarto) on Azure / GH Pages |
| [`methods/`](methods/) | Cross-cutting "how we do it" — e.g. the trigger typology |
| [`infrastructure/`](infrastructure/) | Conventions: storage, database, deployments, comms |

A key design choice: **the latest published framework PDF is authoritative for the trigger**, and ingestion *reconciles* it against the repo (which can drift) — recording discrepancies rather than trusting either alone.

## Current stage

🚧 **Bootstrapping — Phase 2a.** The structure, schema, and conventions are settled and validated against a deliberately diverse 6-framework sample; we're now testing the automated ingestion workflow before fanning it out across the full ~100-repo corpus.

For the live, detailed status see **[docs/ROADMAP.md](docs/ROADMAP.md)**.

## Read more

| To understand… | Read |
|---|---|
| **Why** it's built this way — the rationale + full decision log | [docs/DESIGN.md](docs/DESIGN.md) |
| **What's next** — phases and current status | [docs/ROADMAP.md](docs/ROADMAP.md) |
| **How** to add or restructure a page — conventions & schema | [INGESTION.md](INGESTION.md) |
| How **Claude** should use this repo | [CLAUDE.md](CLAUDE.md) |
| What's in scope to ingest, and progress | [docs/repo-manifest.md](docs/repo-manifest.md) |

---

*Much of this repo is assembled and maintained with Claude working over the team's repos and the published framework documents — that workflow is itself part of what's being built here.*
