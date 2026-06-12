# Design — rationale & decision log

The *why* behind this KB. `INGESTION.md` holds the *how* (conventions); this holds the reasoning, the decisions, and what we deliberately rejected. **Keep it updated:** when an approach changes, add a dated entry rather than silently editing — the history is the point.

## Purpose

Take the team's disparate knowledge — documents (mostly PDFs), code, infrastructure — and make it **easily lookup-able** by both humans and Claude. The end state: Claude can answer most routine questions people bring the team, and accelerate framework/pipeline work, grounded in a cited, maintainable corpus. Not a know-it-all bot; a searchable substrate with a thin agent layer on top.

## Architecture in one paragraph

Markdown in git. **Hub-and-spoke:** this KB is the hub (summaries, cross-links, the cross-framework comparison no single repo can hold); the `ocha-dap` repos are the spokes (deep, code-adjacent detail, versioned with the code). **One home per fact** — pages point via `source_repo`/`code_ref`, never copy. Four content types (`frameworks/`, `pipelines/`, `methods/`, `infrastructure/`) + datasets-as-tags. The "agent" is just Claude Code pointed here via a global-config pointer; live data + a human front door come later as additive layers.

## Decision log

Lightweight ADRs. Each: the decision, why, and what it rejects. Dated.

### 2026-06 — foundational
- **D1 · Markdown corpus, not a trained model.** Rejected fine-tuning and a monolithic "knows-everything" bot: can't cite, goes stale, can't publish, hallucinates specifics. A searchable corpus + retrieval beats it on every axis we care about.
- **D2 · Hub-and-spoke, one-home-per-fact.** Deep detail stays in repos (can't drift from code); cross-cutting/comparative knowledge lives here. Bidirectional links, no duplication.
- **D3 · Four content types + datasets-as-tags.** `frameworks` (design), `pipelines` (living systems/runbooks), `methods` (cross-cutting), `infrastructure` (conventions). A dataset graduates from tag → page only when a shared fact would otherwise be duplicated.
- **D4 · Structure only for findability.** Frontmatter = facets to *find* things, not a spec. Triggers especially: coarse `trigger_facets` + prose + `code_ref`; do **not** normalize a trigger into fields — the variation is the asset.
- **D5 · Consistent questions, idiosyncratic answers; open vocabularies.** Headings stay fixed across pages; tag vocabularies extend during ingestion. Structure adapts to findings, but in deliberate sweeps (git bulk-edits), never page-by-page drift.

### 2026-06 — from recon
- **D6 · Latest framework PDF is authoritative for the trigger** (user, 2026-06-12). The repo *derives/implements* it but the analysis sometimes gets lost. So ingestion is **reconciliation**: take the trigger from the PDF, cross-check the repo, record `repo_completeness` + `discrepancies`. Don't smooth over mismatches.
- **D7 · HDX "model reports" are legacy** (user). Team stopped using them (may revive). Index-only, not authoritative. (HDX dataset `2048a947-5714-4220-905b-e662cbcd14c8`.)
- **D8 · Website = whole OCHA AA portfolio; repos = the DS-built subset.** Some published frameworks were built by other actors. The KB spine centers on frameworks where a repo (and analysis) exists.
- **D9 · PDF acquisition.** unocha publication page (fetch with a browser User-Agent — the site 403s default fetchers) → extract `unocha.org/attachments/*.pdf` → `pdftotext`. ReliefWeb v2 API exists but needs a registered appname. PDFs are dated/versioned and bilingual (FR/ES translations = same version, not new ones).
- **D10 · PDFs stored as full-text extraction + curated summary.** Summarization must never strand a fact; raw stays greppable. No RAG/semantic index until grep proves insufficient.
- **D11 · `visibility: internal|public` from day one.** Cheaper than retrofitting redaction across 100+ pages.
- **D12 · Updates: capture-as-you-go is primary; drift automation is a safety net.** Scheduled `source_sha` diff → PR (never auto-commit), built only once a real corpus exists.
- **D13 · Front door is a later additive layer.** Read-only DB/blob MCP + claude.ai Project or Slack bot. `ds-slack-bot` and `ds-claude-config` already exist as a head start.
- **D14 · Exclude legacy by default.** `pa-anticipatory-action` (big old monorepo) and pre-2024 `pa-*` (COVID-era) are out of default scope; opt back in per repo.
- **D15 · Validate schema on a diverse sample before broad fan-out.** High variance across frameworks means one example misleads — design against ~6 deliberately diverse frameworks, then scale.
- **D16 · Track the runtime/deployment layer, not just code** (user, 2026-06-12). Where things *run* is its own knowledge: marimo apps as **Azure web apps** (RG `IMB-CHD-DataScience-EastUS2`, OCHA-PROD, ~20 apps, `chd-<repo>` naming) and pipelines as **Databricks jobs** (CLI profile `default`, workspace `adb-6009046713167663`). Captured two ways: a `deployment` block on each pipeline/app page, and a generated `infrastructure/deployments.md` registry (both auto-pullable via `az` / `databricks`). Auto-refresh fits the Phase-5 drift job.
- **D17 · Schema v3, from the diverse-sample ingestion** (2026-06-12). The 6-framework sample (ner/nga/hti/moz/lac/bfa) surfaced four consistent strains, now handled: (a) **every framework is multi-window** → a structured `## Trigger windows` body table (windows in the body, not normalized into frontmatter — preserves D4); (b) **the live trigger often runs outside the repo** (IRI Maproom, INAM/PRISM, INSIVUMEH) → `operated_by` field; the repo is then a derivation, not the production system; (c) **repo-drift-from-PDF is the norm** (moz repo = old two-threshold design; bfa repo = 3 generations + stale CLI) → vindicates PDF-authority + `discrepancies`; `repo_completeness: partial` is the common verdict; (d) **multi-country** (LAC umbrella + country annexes) → multi-valued `country_iso3`, `framework_doc_annexes`, a `## Per-country variants` table, and implementation-scope may exceed framework-scope (LAC repo carries Nicaragua, dropped from the framework).

## Open questions

- **Repo → latest-published-doc crosswalk.** How to reliably match each repo to its authoritative PDF given dated + bilingual versions on the portfolio. (Building by hand for the sample; needs a repeatable method for broad ingestion.)
- **Best source for current authoritative PDFs** — unocha vs ReliefWeb vs an internal Drive folder of latest framework docs? (unocha attachment links work today.)
- **Companion-repo typing** — `ds-aa-*-app` / `-monitoring` / `-impactmodel` are pipelines/apps, not frameworks; confirm how they attach to their parent framework.
- **Active non-cloned frameworks to prioritize** — eth-drought, ken-drought, moz-cholera, npl-flooding are recently active but not local.
- **Public-vs-internal default** per content type before publishing.
- **Broad ingestion mechanism** — a Workflow fan-out (billable, multi-agent) needs explicit user go-ahead before launch.
