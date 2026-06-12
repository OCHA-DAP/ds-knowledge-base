# Roadmap & status

Living status of the KB build. Update the checkboxes and the "Now / Next" line as work lands. Rationale for the phasing is in [DESIGN.md](DESIGN.md).

**Now:** ready to ingest the diverse sample (Phase 1).
**Next:** review the sample → lock structure → broad ingestion.

## Phases

- [x] **Phase 0 — Scaffold.** Repo structure, conventions (`INGESTION.md`), templates, `CLAUDE.md` index, global-config pointer, `docs/repo-manifest.md` (109 in scope). _commit `be5829a`_
- [x] **Phase 0.5 — Recon & schema v2.** Portfolio + doc-home recon; PDF-authoritative model; structural audit (`docs/repo-audit.md`, 32 framework repos); PDF fetch+extract chain proven. _commit `d8422ae`_
- [ ] **Phase 1 — Diverse-sample ingestion (go/no-go).** Hand-ingest ~6 frameworks spanning the variance; refine schema against reality. Sample: `ds-aa-ner-drought`, `ds-aa-nga-flooding`, `ds-aa-hti-hurricanes`, `ds-aa-moz-cyclones` + `-monitoring`, `ds-aa-lac-dry-corridor`, `pa-aa-bfa-drought`. **Checkpoint: schema sign-off before scaling.**
- [ ] **Phase 1.5 — Repo→doc crosswalk + deep completeness.** Match each repo to its authoritative latest PDF; rate `repo_completeness` against it.
- [ ] **Phase 2 — Lock structure + build ingestion workflow.** Freeze schema; write the fan-out script; validate it reproduces the hand-done sample.
- [ ] **Phase 3 — Broad ingestion (billable; explicit go-ahead).** Fan out over in-scope repos → reviewable PRs. Generate `catalog.md` + version lineage.
- [ ] **Phase 4 — Wire tiers + curate methods.** Add up-pointers to source-repo `CLAUDE.md`s; write `methods/` (trigger typology) now patterns are visible.
- [ ] **Phase 5 — Drift automation.** `source_sha` diff → PR safety net. Only once a real corpus exists.
- [ ] **Phase 6 — Front door + live tools.** Read-only DB/blob MCP; claude.ai Project or Slack bot (`ds-slack-bot`/`ds-claude-config`).

## Tracking artifacts

- `docs/repo-manifest.md` — what's in scope / cloned / ingested.
- `docs/repo-audit.md` — structural completeness per repo.
- `docs/DESIGN.md` — decisions & open questions.
