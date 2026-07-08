# Roadmap & status

Living status of the KB build. Update the checkboxes, the "Now / Next" line, and the **Ingestion progress** table as work lands. Rationale for the phasing is in [DESIGN.md](DESIGN.md).

**Now:** Phase 2b — **framework corpus complete** (34 frameworks / 35 versions on `main` after batch 3, all v4-conformant). Cross-cutting layers built: dependency graph + blast radius, the `methods/trigger-patterns` typology, 4 index generators. Drift + PDF-freshness checks live (Phase 5). **Phase 8 started** — blob data inventory (`assets/` content type); pilot GloFAS page for `ds-aa-nga-flooding` on `feat/blob-inventory`.
**Next:** **systems back-catalogue largely ingested** — 33 pipelines + 10 apps + 6 shared **libraries** (`infrastructure/libs/`, new `library` content-type + `ingest-libs.mjs`). Deferred by choice: the one-off **analysis/support** repos (BSGI, JIAF, contingency, pa-anticipatory-action, mapaction-ecmwf, sdn/som analysis, pa-*-support) and `ds-claude-config`. Two open cleanups: backfill `infrastructure/deployments.md` registry rows for the ~9 newly-ingested GHA pipelines (each flags it as `[gap]`); refresh stale `ocha-relay` version refs (v0.2.0→v0.3.0). Then generalize the spoke-pointer fan-out (Phase 4) → front door (Phase 6). Next for Phase 8: FloodScan coverage parser, GeoGLOWS (NPL), CHIRPS-GEFS (MOZ storms), and the NGA analysis-outputs catch-all.

## Ingestion progress

| content type | ingested | in scope | remaining | how |
|---|--:|--:|--:|---|
| frameworks | **32** | ~27 | 0 | ✅ real frameworks only (have a published — incl. non-public — framework doc). 7 reclassified to `analysis/` (D40); `bgd-storms` pending (a dedup with `bgd-cyclone`). +5 **in-development successor versions** ingested from dev branches (eth/cub/hti/ner-drought/nga-flooding — `framework_doc:null`, `trigger_source:repo`) via `workflows/ingest-dev-versions.mjs`, resolving issues #11/#13/#14/#15. |
| analysis | **7** | — | — | repos that are analysis, not frameworks/pipelines (regional overviews, ad-hoc, pre-framework). New content type (D40). |
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
  - [x] Systems back-catalogue — 3 batches (23 pipelines + 4 apps) + 6 libraries ingested → 33 pipelines, 10 apps, 6 libs total. One-off analysis/support repos deferred; deployments.md registry backfill + ocha-relay version refresh outstanding.
- [~] **Phase 4 — Wire tiers + curate methods.**
  - [x] `methods/trigger-patterns.md` populated from the corpus (D38).
  - [x] Cross-type **dependency graph + blast radius** (`infrastructure/dependency-graph.md`, D37).
  - [~] Per-repo spoke→hub pointers prototyped on `ds-aa-tcd-drought` ([PR #8](https://github.com/OCHA-DAP/ds-aa-tcd-drought/pull/8)); **next: generalize a generator + one PR per repo** (awaiting sign-off on the prototype shape).
- [~] **Phase 5 — Drift + pipeline-health automation.** `check_drift.py` (daily, code drift) + `check_pdf_freshness.py` (weekly, doc-version drift) → `kb-drift` / `kb-pdf-freshness` issues; never auto-edits. Drift issue #20 actioned: mdg-monitoring repointed `exposure-plots`→`main`. **Pipeline registry + live health built (D43):** `gen_pipeline_registry.py` → `infrastructure/pipeline-registry.md` (Databricks + GHA, one row per deployed job, cadence-vs-last-success health) — supersedes the `pipelines-status` dashboard; first run caught 6 down (2 failing storm jobs, dead NHC GHA workflow, 3 stalled monitoring pipelines). `pipeline-registry.yml` is **parked manual-only (dormant)** until the `DSCI_DATABRICKS_*` secrets are added to the repo/org (reuse the ones `ds-pipelines-status` uses) — then uncomment its `schedule` for the daily auto-refresh; meanwhile run the generator locally on demand. _Next: flag → auto re-ingest PR; pipeline-health → issue/alert._
- [ ] **Phase 6 — Front door + live tools.** Read-only DB/blob MCP; claude.ai Project or Slack bot (`ds-slack-bot` / `ds-claude-config`).
- [~] **Phase 7 — Documents: extracts + Google Drive.** Make document knowledge greppable, under the [PRIVACY.md](PRIVACY.md) classification (D44: public/internal by **source**; metadata public, content per-source).
  - [x] **7a · Public framework-PDF full-text → in-repo `raw/`.** ✅ Extracted all **24** public-doc framework versions to `raw/frameworks/<fw>/<version>.txt` (1.7 MB), wired every `raw_extract`, and cleared the two dead `/tmp` pointers. Repeatable via `scripts/gen_framework_extracts.py` (`--check` to audit). Non-public docs (mmr/vut/yem) + repo-only/dev versions correctly skipped.
  - [ ] **7b · Drive manifest (public metadata).** Crawl **only the Data Science team shared drive** (NOT the data-storage drive; **exclude `General - All AA projects / Data`**) → `infrastructure/drive-index.md` (+ `.drive-index.json`): per-file folder-path, title, type, owner-coarse, dates, link, tags. Metadata only → **public**. Drive share-links are access-gated, so publishing them exposes nothing. Strip PII.
  - [ ] **7c · Drive content extraction (private).** Export text of the useful/archival docs (Docs/Slides/key Sheets/PDFs) → gitignored `drive/raw/` (local grep cache) + blob `{PROJECT_PREFIX}/processed/drive/` and/or a private repo. **Internal** — never the public repo (`.gitignore` blocks `drive/`). Sensitivity triage: skip/redact restricted (PII/HR/security/budget); prioritise content over logistics junk.
  - [ ] **7d · Query + refresh.** Querying = local grep over the manifest + extract cache (no live API in the hot path). The Drive MCP is **interactive/session-bound** (not headless/cron) → extraction runs in a live session; refresh = re-run periodically. Public exposure of any *content* item is an explicit per-item human promotion.

- [~] **Phase 8 — Blob data inventory (`assets/`).** Coverage reports answering "what do we have stored, and is it sufficient?" `scripts/gen_blob_inventory.py` → `assets/<project>/<datasource>.md`. **Pilot done:** `assets/ds-aa-nga-flooding/glofas.md` (raw GRIB + processed Parquet coverage: 9 gauge stations, year ranges 1979–2024, leadtime windows, gap detection). Design: per-datasource pages + one `analysis-outputs.md` catch-all per project; `datasource_type` + `coverage_axes` + `framework_ref` frontmatter fields (see D45). **Next:** `--filter floodscan` coverage parser (HFR pattern, cross-project); `--filter geoglows` (NPL); `--filter chirps-gefs` (MOZ storms); generic parquet-inventory mode; NGA analysis-outputs page.

## Generators (post-batch routine — run all four; see `scripts/README.md`)

`gen_catalog.py` · `gen_framework_readmes.py` · `gen_issue_form.py` · `gen_dependency_graph.py`

## Tracking artifacts

- `docs/repo-manifest.md` — what's in scope / cloned / ingested (per-repo).
- `catalog.md` — generated index of all framework-versions.
- `infrastructure/dependency-graph.md` — cross-type dependencies + blast radius.
- `infrastructure/deployments.md` — runtime registry (Azure apps + Databricks jobs + GitHub Actions pipelines).
- `infrastructure/drive-index.md` — _(Phase 7b, planned)_ public manifest of the DS team shared drive (metadata only; content is internal — see `docs/PRIVACY.md`).
- `docs/PRIVACY.md` — public/internal classification (by source; metadata vs data). Read before ingesting any new source.
- `docs/DESIGN.md` — decisions & open questions. Open enhancements tracked as GitHub issues (`enhancement` label).
