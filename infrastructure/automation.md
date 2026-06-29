# Automation — how the KB keeps itself current

The KB maintains itself on three axes. The rule: **deterministic regeneration auto-commits; anything
needing judgment is detected, then Claude drafts the fix on the Max plan and opens a PR / issue for
human review.** Claude never writes to `main` directly. All the moving parts live in `scripts/` and
`.github/workflows/`; this page is the map. (Per-script detail: [`scripts/README.md`](../scripts/README.md).)

## The three axes

### 1. Generators — deterministic, auto-commit
Pure functions of live state; no judgment, so they regenerate and commit straight to `main`.

| What | Script | Workflow | Cadence |
|---|---|---|---|
| Postgres schema snapshots (+ dep graph) | `gen_db_schema.py`, `gen_dependency_graph.py` | `db-schema.yml` | daily |
| Pipeline registry + health | `gen_pipeline_registry.py` | `pipeline-registry.yml` ⏸ | (local runner) |
| Framework PDF text + visual captions | `gen_framework_extracts.py`, `gen_framework_captions.py` | `framework-sync.yml` | weekly |
| Catalog, framework READMEs, public site | `gen_catalog.py`, `gen_framework_readmes.py`, `gen_public_site.py` | `refresh-site.yml` | monthly |
| Spoke-repo registry | `gen_spoke_repos.py` | (local) | on demand |

### 2. Drift / freshness — watch what's *already* in the KB
Detect staleness in existing pages; **never auto-fix**. Each maintains a labelled tracking issue and,
where a clean fix exists, dispatches the **detect→fix→PR loop** (below).

| Axis | Script | Workflow | Issue | Fix |
|---|---|---|---|---|
| **Code** drift (spoke moved) | `check_drift.py` | `drift-check.yml` (daily) | `kb-drift` | re-ingest stale page → PR |
| **Doc** freshness (PDF aging/newer) | `check_pdf_freshness.py` | `pdf-freshness.yml` (weekly) | `kb-pdf-freshness` | re-ingest framework → PR |
| **Estate** drift (Azure/dbx changed) | `check_infra_drift.py` | `infra-drift.yml` ⏸ (daily) | `kb-infra-drift` | draft page for new app → PR |

### 3. Discovery — find net-new things to ingest
Watch the *outside* (the org, the OCHA AA portfolio) for things the KB doesn't have yet.

| What | Script | Workflow | Issue |
|---|---|---|---|
| New/removed **ocha-dap repos** | `check_new_repos.py` | `discover-repos.yml` (weekly) | `kb-new-repos` |
| **Existing** un-ingested in-scope repos (backfill) | `check_coverage.py` | (on demand) | `kb-coverage` |
| **OCHA/CERF AA frameworks + activations** (full portfolio, any age) + **missing older versions** of held frameworks | `aa_watch.py` | `aa-watch.yml` (weekly) | `kb-aa-watch` |
| **Backlog fill** — drains the framework wishlist into kb-ingest, trickled | `drain_aa_backlog.py` | `aa-backlog-fill.yml` (weekly) | (commits the queue) |

The **framework-ingest backlog** (`infrastructure/.aa-backlog.json`) is a queue of frameworks / older
versions to ingest later (e.g. Nepal/Philippines/Bangladesh older versions found by `aa-watch`).
`aa-backlog-fill.yml` dispatches a few per run via `kb-ingest` and removes them from the file, so the
list drains to empty over weeks without re-dispatching. Add entries by hand or promote them from the
`kb-aa-watch` issue.

The two framework-coverage tools are complementary: `check_coverage.py` is **repo-based** (a framework
with a `ds-aa-*` repo and no page); `aa_watch.py` is **portfolio-based** (a framework that exists on the
OCHA/CERF site with *no repo at all* — e.g. the 2020–21 CERF pilots). Somalia drought is the canonical
example only the portfolio axis can catch.

## The detect→fix→PR loop

The shared "fix" half of every drift axis is **`.github/workflows/kb-ingest.yml`** → headless
`claude -p` on the **Max plan** (`CLAUDE_CODE_OAUTH_TOKEN`, same mechanism as the framework captions):

- `ingest_system.py` — draft a NEW app/pipeline page, or re-ingest a STALE one in place (`--page`).
- `ingest_framework.py` — re-draft a framework version from its PDF extract (authority) + code.
- `ingest_framework_web.py` — draft a **repo-less** framework page from public OCHA/CERF sources via
  Claude **WebSearch** (the comprehensiveness path for historical pilots — Somalia drought etc.).
  Dispatch: `kb-ingest.yml -f kind=framework -f country=SOM -f hazard=drought [-f doc=<url>]`.
- `aa_watch.py` — Claude **WebFetch + WebSearch** discovery (frameworks/activations/older-versions we
  lack), **grounded on a deterministic backbone**: it fetches the authoritative CERF AA portfolio
  sources (`CERF_SOURCES` — the portal + portfolio-update PDF) and enumerates from those (with CERF's
  published ~19–20-framework count as a completeness check), not free search from memory.

Each detector **emits** the affected items (`--emit-stale` / `--emit-due` / `--emit-new-apps`) and
dispatches `kb-ingest`, which opens a PR that **closes the tracking issue** on merge. The human review
on that PR replaces the Opus QA agent of the interactive `workflows/ingest-systems.mjs`. Two safeties:
the loops **trickle** (cap re-ingests/run — drift 6, freshness 4) and **dedup** (skip a page that
already has an open `kb-ingest` PR). `kb-ingest.yml` never runs on `pull_request` (keeps the Max token
off fork PRs).

## Scope — comprehensive of the OCHA AA portfolio

The KB aims to be **as comprehensive as possible of the OCHA/CERF anticipatory-action portfolio — not
only the frameworks the DS team built.** Historical pilots (the 2020–21 cohort: Somalia drought, South
Sudan flood, Madagascar plague, Malawi dry spells, …) and frameworks with **no DS repo and no modern
published doc** are still in scope; they are drafted from public OCHA/CERF sources via the web-research
path. There is therefore **no out-of-scope ignore-list** on `aa-watch` — it reconciles the whole
portfolio every run. (See [INGESTION.md](../docs/INGESTION.md) for the framework-page rule.)

## Running it / secrets

- **CI dormancy:** `pipeline-registry.yml` and `infra-drift.yml` are ⏸ until their secrets exist; until
  then [`scripts/run_local_updaters.sh`](../scripts/run_local_updaters.sh) runs them from a local
  checkout (launchd agent, daily) on local `az`/`databricks` auth. See [local-updaters in
  scripts/README](../scripts/README.md#local-updaters-scheduled-on-your-machine--for-the-dormant-ci-workflows).
- **Secrets:** `CLAUDE_CODE_OAUTH_TOKEN` (set — the Max-plan token) powers every Claude path.
  `INGEST_GH_PAT` / `DISCOVER_GH_PAT` (org `repo:read`, not yet set) let the fix loop clone PRIVATE
  spokes and the sweep see PRIVATE repos; without them those halves degrade safely (public-only). The
  same PAT would also close the `check_drift.py` private-spoke blind spot.

## Issue labels (one per signal)
`kb-drift` · `kb-pdf-freshness` · `kb-infra-drift` · `kb-new-repos` · `kb-coverage` · `kb-aa-watch` ·
`kb-ingest` (the review PRs).
