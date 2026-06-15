# Roadmap & status

Living status of the KB build. Update the checkboxes and the "Now / Next" line as work lands. Rationale for the phasing is in [DESIGN.md](DESIGN.md).

**Now:** Phase 2b underway — batch 1 of the broad run landed (10 frameworks, 10/10 valid; 16 framework-versions total in `catalog.md`).
**Next:** continue 2b in batches (~35 frameworks remaining, ~3 more batches) → harden the workflow with a YAML parse self-check → wire `methods/` once the corpus is broad enough.

## Phases

- [x] **Phase 0 — Scaffold.** Repo structure, conventions (`INGESTION.md`), templates, `CLAUDE.md` index, global-config pointer, `docs/repo-manifest.md` (109 in scope). _commit `be5829a`_
- [x] **Phase 0.5 — Recon & schema v2.** Portfolio + doc-home recon; PDF-authoritative model; structural audit (`docs/repo-audit.md`, 32 framework repos); PDF fetch+extract chain proven. _commit `d8422ae`_
- [x] **Phase 1 — Diverse-sample ingestion (go/no-go).** 6 frameworks ingested (ner/nga/hti/moz/lac/bfa) + 2 pipeline pages + catalog. Drove **schema v3** (D17). Verdict: schema holds; PDF-authority vindicated (every repo drifted from its PDF). _commit `20a8d24`_ **← awaiting schema sign-off before scaling.**
- [ ] **Phase 1.5 — Repo→doc crosswalk + deep completeness.** Match each repo to its authoritative latest PDF; rate `repo_completeness` against it.
- [x] **Phase 2a — Build & validate ingestion workflow.** `workflows/ingest-frameworks.mjs` (ingest Sonnet → review-and-fix Opus). Re-ran on the 6 hand-done frameworks: **6/6 valid**, reference-or-better (found real code bugs + PDF inconsistencies). Locked the `n_windows` counting convention (D24). _commit pending_
- [~] **Phase 2b — Broad ingestion (billable; explicit go-ahead).** Clone ~40 missing repos + repo→doc crosswalk ✅, then fan out over in-scope repos in batches → reviewable PRs. **Batch 1 done (2026-06-15):** 10 frameworks (afg/bgd/cod/cub/moz-cholera/tcd/mrt/fji/phl/npl), 10/10 valid, ~15.6 min, ~58M raw tokens (92.8% cache reads) ≈ $44 API-list-equiv. `catalog.md` regenerated via `scripts/gen_catalog.py` (16 versions). **Remaining: ~35 frameworks (~3 batches).**
- [ ] **Phase 3 — Broad ingestion (billable; explicit go-ahead).** Fan out over in-scope repos → reviewable PRs. Generate `catalog.md` + version lineage.
- [ ] **Phase 4 — Wire tiers + curate methods.** Add up-pointers to source-repo `CLAUDE.md`s; write `methods/` (trigger typology) now patterns are visible.
- [ ] **Phase 5 — Drift automation.** `source_sha` diff → PR safety net. Only once a real corpus exists.
- [ ] **Phase 6 — Front door + live tools.** Read-only DB/blob MCP; claude.ai Project or Slack bot (`ds-slack-bot`/`ds-claude-config`).

## Tracking artifacts

- `docs/repo-manifest.md` — what's in scope / cloned / ingested.
- `docs/repo-audit.md` — structural completeness per repo.
- `infrastructure/deployments.md` — runtime registry (Azure apps ✅; **Databricks jobs pending token re-auth** → `databricks auth login --profile CHD-Databricks-Dev`).
- `docs/DESIGN.md` — decisions & open questions.
