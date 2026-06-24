# Roadmap & status

Living status of the KB build. Update the checkboxes, the "Now / Next" line, and the **Ingestion progress** table as work lands. Rationale for the phasing is in [DESIGN.md](DESIGN.md).

**Now:** Phase 2b — **framework corpus complete** (34 frameworks / 35 versions on `main` after batch 3, all v4-conformant). Cross-cutting layers built: dependency graph + blast radius, the `methods/trigger-patterns` typology, 4 index generators. Drift + PDF-freshness checks live (Phase 5).
**Next:** **systems back-catalogue largely ingested** — 33 pipelines + 10 apps + 6 shared **libraries** (`infrastructure/libs/`, new `library` content-type + `ingest-libs.mjs`). Deferred by choice: the one-off **analysis/support** repos (BSGI, JIAF, contingency, pa-anticipatory-action, mapaction-ecmwf, sdn/som analysis, pa-*-support) and `ds-claude-config`. Two open cleanups: backfill `infrastructure/deployments.md` registry rows for the ~9 newly-ingested GHA pipelines (each flags it as `[gap]`); refresh stale `ocha-relay` version refs (v0.2.0→v0.3.0). Then generalize the spoke-pointer fan-out (Phase 4) → front door (Phase 6).

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
- [ ] **Phase 7 — Documents: extracts + Google Drive.** Make document knowledge greppable, under the [PRIVACY.md](PRIVACY.md) classification (D44: public/internal by **source**; metadata public, content per-source).
  - [x] **7a · Public framework-PDF full-text → in-repo `raw/`.** ✅ Extracted all **24** public-doc framework versions to `raw/frameworks/<fw>/<version>.txt` (1.7 MB), wired every `raw_extract`, and cleared the two dead `/tmp` pointers. Repeatable via `scripts/gen_framework_extracts.py` (`--check` to audit). Non-public docs (mmr/vut/yem) + repo-only/dev versions correctly skipped.
  - [x] **7b · Drive manifest (internal metadata catalog).** Target = **only the DS team shared drive** (`0AGYkOFcloQuyUk9PVA`; NOT the data-storage drive; exclude the bulk-data root folders **HDX Signals / Climate Data / Collaborations** and **`General - All AA projects / Data`**) → `drive/drive-index.md` (+ `.drive-index.json`): per-item folder-path, title, type, dates, size, link (PII stripped — no owner emails). **The full crawl is the whole drive (1,941 folders / 53k files); after the bulk-data excludes it's ~9k entries — and at that scale the catalog of partner/project filenames is too much aggregate exposure for the public repo, so the manifest is _internal_** — its home is the **private companion repo [`ds-knowledge-base-internal`](https://github.com/OCHA-DAP/ds-knowledge-base-internal)** (D44b/D45/D46); the public repo carries a **pointer** (`infrastructure/drive-index.md`). **Full recursive crawl working & headless** via `scripts/gen_drive_index.py` (writes into the private repo via `KB_INTERNAL_DIR`; `--render-only` re-renders; `git diff` there is the drift record). **Auth journey (resolved):** the read-only **service-account** path is a dead end here — adding an SA to the shared drive needs you to be a drive Manager *and* the org to allow non-domain members (locked down), and gcloud's own OAuth client is **blocked by org policy for sensitive Drive scopes** ("app is blocked"). Solution: a **dedicated internal OAuth client we own** (`ocha-ds-kb` GCP project, **Internal** consent → exempt from the third-party-app block) + **your** read-only Drive ADC (`gcloud auth application-default login --client-id-file=~/.config/ds-kb/oauth-client.json --scopes=…drive.readonly`), run from an isolated venv (`~/.config/ds-kb/venv`; do **not** `pip install --user` — it shadows gcloud's bundled protobuf and breaks the CLI). The SA (`ds-kb-drive-reader@ocha-ds-kb…`) is kept, dormant, for the eventual domain-wide-delegation upgrade (needs a Workspace super-admin). _Next: 7c content extraction into the same private repo._
  - [ ] **7c · Drive content extraction (private).** Export text of the useful/archival docs (Docs/Slides/key Sheets/PDFs) → the **private repo** `ds-knowledge-base-internal/drive/extracts/` (greppable, versioned). **Internal** — never the public repo. Sensitivity triage: skip/redact restricted (PII/HR/security/budget); prioritise content over logistics junk.
  - [~] **7d · Query + refresh + drift.** Querying = local grep over the manifest + extract cache in the private repo clone (no live API in the hot path). **Refresh is headless and self-versioning:** `scripts/drive_refresh.sh` re-crawls (via the internal OAuth client) and **commits to the private repo** — so durability + history + drift are all just git (`git diff` = the drift record). No blob (it's the data-plane tool, wrong fit for small versioned text — the earlier dev-blob copy + `drive_index_to_blob.py` were removed, D46) and no custom drift job (git replaces the `--check`/launchd/issue stack). *Content* extraction still uses the interactive Drive MCP connector (session-bound) for the per-doc text. **Schedule (optional):** wire `drive_refresh.sh` to weekly launchd/cron (zero secrets — local ADC); the clean long-term is the dormant SA + **domain-wide delegation** (super-admin) so a CI refresh runs as a non-user identity. Public exposure of any *content* item stays an explicit per-item human promotion.

## Generators (post-batch routine — run all four; see `scripts/README.md`)

`gen_catalog.py` · `gen_framework_readmes.py` · `gen_issue_form.py` · `gen_dependency_graph.py`

## Tracking artifacts

- `docs/repo-manifest.md` — what's in scope / cloned / ingested (per-repo).
- `catalog.md` — generated index of all framework-versions.
- `infrastructure/dependency-graph.md` — cross-type dependencies + blast radius.
- `infrastructure/deployments.md` — runtime registry (Azure apps + Databricks jobs + GitHub Actions pipelines).
- `infrastructure/drive-index.md` — **pointer** to the internal DS-drive manifest (the catalog itself lives in the private repo `ds-knowledge-base-internal` — see `docs/PRIVACY.md`). Generated by `scripts/gen_drive_index.py` (full headless crawl working; `scripts/drive_refresh.sh` = crawl + commit).
- `docs/PRIVACY.md` — public/internal classification (by source; metadata vs data). Read before ingesting any new source.
- `docs/DESIGN.md` — decisions & open questions. Open enhancements tracked as GitHub issues (`enhancement` label).
