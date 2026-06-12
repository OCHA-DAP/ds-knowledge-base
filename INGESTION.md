# Ingestion spec

How knowledge enters this repo. Both humans and the ingestion workflow follow this. If you change a convention here, it must hold across **all** pages (see "Adapting the structure").

## The one rule

**One home per fact; everything else links to it.**

- Deep, operational, code-adjacent detail lives in the **source repo** (its own `CLAUDE.md`/`docs/`), versioned with the code so it can't drift.
- Cross-cutting, comparative, institutional knowledge lives **here**.
- Neither copies the other. Pages point via `source_repo` / `code_ref`. The canonical trigger is the **code**, not a field in this KB.

If you're about to write the same fact on a second page, stop — give it one home and link.

## Content types

| Type | Folder | What it is | Page shape |
|---|---|---|---|
| framework | `frameworks/` | An AA framework + its versions (design & rationale) | structured frontmatter + consistent headings |
| pipeline | `pipelines/` | A living operational system: dataset ingest, monitoring, exposure, app | runbook |
| method | `methods/` | Cross-cutting how-we-do-it (trigger typology, calibration, monitoring design) | free prose, emerges bottom-up |
| infrastructure | `infrastructure/` | Conventions: storage, DB, stratus/lens, GHA patterns | reference |

Datasets are **tags**, not pages by default (`data_sources: [SEAS5]`, `inputs: [...]`). A dataset graduates to a thin `infrastructure/datasets/<name>.md` page **only** when a shared fact would otherwise be duplicated across pages (resolution, leadtime/CRS convention, licensing). Promote on the second duplication, not before.

## Structure only what helps you *find* things

Frontmatter = facets for lookup, **not** a spec you could execute from. Triggers especially: capture coarse `trigger_facets` to find similar ones, then describe the actual logic in prose + `code_ref`. Do not try to normalize a trigger into fields — the variation is the asset.

Tag vocabularies (`hazard`, `data_sources`, `trigger_facets.*`, pipeline `type`) are **open** — extend them as ingestion surfaces new values. Keep the *questions* (headings) consistent across pages; let the *answers* be as idiosyncratic as the work.

## Source pointers (every page)

Every page is a card in a catalog over the raw sources. Mandatory:

- `source_repo` — local path and/or `ocha-dap/<repo>`.
- `source_sha` — the commit the page was generated from (the drift anchor; Phase 5).
- `code_ref: []` — repo paths (+ line/commit where useful) to the canonical implementation.
- `pdf: []` — links to source documents.

### PDFs: full-text + summary, not summary alone

For each source PDF, store **both**:
1. A markdown **full-text extraction** under the repo or `docs/raw/` (greppable, lossless-ish) — so a buried detail is always reachable.
2. The curated **summary** in the page body.

Summarization must never strand a fact: if the summary omits something, the linked raw must still surface it via grep/read. No semantic/RAG index for now — grep + open-the-source covers it. Add one later only if summaries prove too lossy in practice.

## Visibility

Every page carries `visibility: internal | public`. Set it honestly at creation — retrofitting a redaction pass across 100+ pages is the thing we're avoiding. `public` = safe to publish (frameworks/triggers/monitoring we intend to share). Default `internal` when unsure.

## The two tiers

This KB is the **hub**; source repos are the **spokes**.

- **Hub → spoke**: framework/pipeline pages link down via `code_ref`/`source_repo` for depth.
- **Spoke → hub**: each source repo's `CLAUDE.md` gets a pointer up to this KB (conventions, the trigger typology, sibling frameworks). Added in Phase 4.

A repo can't know about its siblings — cross-framework comparison is the hub's job. Depth stays in the repo.

## How the KB is kept current

1. **Capture-as-you-go** (primary): finishing real work → update the affected page as the last step. Repo `CLAUDE.md` first (closest to code), summary propagates up.
2. **Gaps surface through use**: looked something up and it's missing/stale → leave a stub or `<!-- TODO -->`, don't silently move on.
3. **Drift automation** (Phase 5, safety net): scheduled job compares each repo's `HEAD` to the page's `source_sha`, opens a **PR** (never auto-commits) for stale pages. Build only once a real corpus exists.

## Adapting the structure

The format follows the findings. Expect the schema to shift during ingestion. Discipline:
- Stabilize the **core** (shared fields/headings); let the **edges** flex.
- Adapt in deliberate **sweeps** across all pages, not page-by-page drift (drift → inconsistency → broken lookup).
- It's all markdown in git: a restructure is a bulk edit + a `git diff` you review, not a migration.
