# Roadmap & status

Living status of the KB build. Update the checkboxes, the "Now / Next" line, and the **Ingestion progress** table as work lands. Rationale for the phasing is in [DESIGN.md](DESIGN.md).

**Now:** Phase 2b — finishing broad ingestion. Merged to `main`: **27 framework-versions**, 8 pipelines, 4 apps, all v4-conformant. Cross-cutting layers built: dependency graph + blast radius, the `methods/trigger-patterns` typology, 4 index generators. Drift + PDF-freshness checks live (Phase 5).
**Next:** finish ingestion — framework **batch 3** (~9 mostly repo-only), then the systems back-catalogue (~51 pipelines, ~12 apps) → then generalize the spoke-pointer fan-out (Phase 4) → front door (Phase 6).

## Ingestion progress

| content type | ingested | in scope | remaining | how |
|---|--:|--:|--:|---|
| frameworks | 26 | ~35 | **~9** | `workflows/ingest-frameworks.mjs` — batch 3 (caf, eth-drought, ken, mmr, plw, syr, vut, bgd-storms, yem; most repo-only → `development`) |
| pipelines | 8 | ~59 | **~51** | `workflows/ingest-systems.mjs` (type pipeline) — monitoring companions + data backbones |
| apps | 4 | ~16 | **~12** | `workflows/ingest-systems.mjs` (type app) |
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
  - [ ] **Frameworks batch 3** (~9 remaining) ← in progress.
  - [ ] Systems back-catalogue (~51 pipelines, ~12 apps).
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
