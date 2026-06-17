# Roadmap & status

Living status of the KB build. Update the checkboxes, the "Now / Next" line, and the **Ingestion progress** table as work lands. Rationale for the phasing is in [DESIGN.md](DESIGN.md).

**Now:** Phase 2b — **framework corpus complete** (34 frameworks / 35 versions on `main` after batch 3, all v4-conformant). Cross-cutting layers built: dependency graph + blast radius, the `methods/trigger-patterns` typology, 4 index generators. Drift + PDF-freshness checks live (Phase 5).
**Next (paused to save tokens):** continue the **systems back-catalogue** (~43 pipelines, ~10 apps left) via `ingest-systems.mjs`, in batches → then generalize the spoke-pointer fan-out (Phase 4) → front door (Phase 6).

## Ingestion progress

| content type | ingested | in scope | remaining | how |
|---|--:|--:|--:|---|
| frameworks | **34** | ~35 | **~1** | ✅ batches 1–3 done; only `bgd-storms` pending (a dedup with `bgd-cyclone`, not a new page). Batch 3 added several `pre-development`/`development` repo-only frameworks (caf, syr, mmr, vut, plw). |
| pipelines | **16** | ~59 | **~43** | `workflows/ingest-systems.mjs` (type pipeline). Batch 2 added floodscan-ingest, glb-tropicalcyclones, flood-gfm, fms-tc-outlook, glb-cyclones-impactmodel + moz-cholera/bgd-cyclone/mdg monitoring companions. |
| apps | **6** | ~16 | **~10** | `workflows/ingest-systems.mjs` (type app). Batch 2 added seas5-skill, seas5-viz. |
| libs | 0 | 6 | 6 | ocha-stratus / ocha-lens / ocha-relay etc. → `infrastructure/` notes (later) |

_Excluded from the counts: archived repos (cmr-drought, etc.) and the `pa-anticipatory-action` monorepo. Historical framework versions are deferred — see issue #6._

## Phases

- [x] **Phase 0 — Scaffold.** Repo structure, conventions, templates, `CLAUDE.md` index, `docs/repo-manifest.md`. _be5829a_
- [x] **Phase 0.5 — Recon & schema v2.** Portfolio recon; PDF-authoritative model; structural audit; PDF fetch+extract chain.
- [x] **Phase 1 — Diverse-sample ingestion (go/no-go).** 6 frameworks + pipeline pages; drove schema v3. PDF-authority vindicated.
- [x] **Phase 2a — Build & validate ingestion workflow.** `ingest-frameworks.mjs` (Sonnet draft → Opus review-fix); 6/6 valid, found real bugs. Locked `n_windows` (D24).
- [~] **Phase 2b — Broad ingestion.**
  - [x] Frameworks batch 1 (10) · batch 2 (10) → 27 versions, all v4-conformant (schema v4: indicators, funding-by-source, discrepancy kind-tags).
  - [x] Systems batch 1 — `ingest-systems.mjs` built; 4 pipelines + 3 apps (code+deployment authoritative).
  - [x] Frameworks batch 3 (8) → corpus complete (34 frameworks; several pre-dev/dev repo-only).
  - [ ] Systems back-catalogue (~51 pipelines, ~12 apps) ← next.
- [~] **Phase 4 — Wire tiers + curate methods.**
  - [x] `methods/trigger-patterns.md` populated from the corpus (D38).
  - [x] Cross-type **dependency graph + blast radius** (`infrastructure/dependency-graph.md`, D37).
  - [~] Per-repo spoke→hub pointers prototyped on `ds-aa-tcd-drought` ([PR #8](https://github.com/OCHA-DAP/ds-aa-tcd-drought/pull/8)); **next: generalize a generator + one PR per repo** (awaiting sign-off on the prototype shape).
- [~] **Phase 5 — Drift automation.** `check_drift.py` (daily, code drift) + `check_pdf_freshness.py` (weekly, doc-version drift) → `kb-drift` / `kb-pdf-freshness` issues; never auto-edits. _Next: flag → auto re-ingest PR._
- [ ] **Phase 6 — Front door + live tools.** Read-only DB/blob MCP; claude.ai Project or Slack bot (`ds-slack-bot` / `ds-claude-config`).

## Generators (post-batch routine — run all four; see `scripts/README.md`)

`gen_catalog.py` · `gen_framework_readmes.py` · `gen_issue_form.py` · `gen_dependency_graph.py`

## Tracking artifacts

- `docs/repo-manifest.md` — what's in scope / cloned / ingested (per-repo).
- `catalog.md` — generated index of all framework-versions.
- `infrastructure/dependency-graph.md` — cross-type dependencies + blast radius.
- `infrastructure/deployments.md` — runtime registry (Azure apps + Databricks jobs + GitHub Actions pipelines).
- `docs/DESIGN.md` — decisions & open questions. Open enhancements tracked as GitHub issues (`enhancement` label).
