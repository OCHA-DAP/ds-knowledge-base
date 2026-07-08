---
content_type: analysis
name: ait-lngo-research
analysis_type: other       # not an AA/hazard analysis at all — see "What it is"
status: active              # bulk run underway (priority countries done, rest in progress)
country_iso3: regional      # ~673 LNGO partners spread across many humanitarian contexts (CAR, Chad, DRC, Nigeria, Sudan prioritised; also Ukraine, Ethiopia, Haiti, Colombia, Venezuela, Myanmar, Syria, Lebanon, Mozambique, S. Sudan, Sahel CFA-zone, ...)
hazard: none                 # no hazard — this is partner financial-capacity research, not a trigger/AA analysis
summary: "Claude-Code-driven agentic research pipeline that establishes annual operating budget / income estimates for ~673 local & national NGO (LNGO) partners, feeding a colleague's downstream partner-capacity assessment; not an AA framework and has no hazard dimension."
data_sources: [UK-Charity-Commission, US-Form-990-ProPublica, EU-Transparency-Register-LobbyFacts, ICVA, NEAR, UNPP, ReliefWeb, Devex, Copilot-NGO-assessment]
feeds: []   # standalone — downstream consumer is a colleague's notebook (absorption_capacity.ipynb) outside this KB, not a KB pipeline/framework node
# --- source repo ---
source_repo: ocha-dap/ds-ait-lngo-research
source_branch: lngo-33-run
source_sha: 9fac894
code_ref:
  - CLAUDE.md
  - README.md
  - pipeline.py
  - DATA_DICTIONARY.md
  - worker_prompt_template.md
  - guess_prompt_template.md
  - adjudication_prompt_template.md
  - src/storage.py
  - src/copilot.py
  - src/unpp.py
  - src/money.py
  - src/constants.py
depends_on: []
discrepancies: []
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# LNGO partner budget research (AIT) — analysis

> **Analysis, not a framework.** This repo has no hazard, no trigger, and no published framework doc — it is not AA work at all. Captured here because it's an active OCHA/CHD data-science pipeline, comparable in shape (agentic + blob-state + resumable) to the team's other analysis repos, even though its subject (partner financial capacity) is orthogonal to the AA portfolio.

## What it is

`ds-ait-lngo-research` ("AIT" per the README — acronym otherwise undefined in the repo) is an **agentic research pipeline** that establishes the annual operating budget / total annual income for **~673 local and national NGOs (LNGOs)** that OCHA works with in humanitarian contexts (CBPF/HRP-type partners). Most of these organisations have no public financial data, so a **fixed multi-step search protocol** — one Claude subagent per partner, run via the Agent/Task tool inside a Claude Code session on the operator's Max-plan subscription (no API key, no per-token billing) — walks UK Charity Commission → US Form 990 (ProPublica) → EU Transparency Register (LobbyFacts) → ICVA/NEAR network directories → org website/annual reports → general financial search → org profile, and returns a strict JSON record per partner. It is not a framework or a living scheduled pipeline: there is no published framework doc (nothing to trigger, no hazard), and nothing runs on a schedule — a human/Claude-orchestrator drives each batch interactively, so it's an ad-hoc, human-in-the-loop research effort rather than an operational system.

The **canonical partner list** ("the spine") is a colleague's prior Copilot-assisted assessment, `raw/ngo_partners_with_un_validation.xlsx`, which already carries a heuristic budget band per partner (`budget_range`, `estimation_basis`, `confidence_level`) plus a manual UNPP capacity read. This pipeline's job is to **replace the weakest of those heuristic bands** with either a UN Partner Portal (UNPP) self-reported figure, a sourced web-research figure, or (as a last resort, offline reasoning) a Claude-guess banded estimate — while leaving genuinely sourced/high-confidence figures alone.

## What was analyzed / findings

- **Anti-fabrication discipline is the core design constraint**, enforced in the worker prompt (`worker_prompt_template.md`): a budget figure may only come from a named regulatory filing, the org's own published accounts, a donor publication, or a sourced news article — never inferred from beneficiary counts, staff counts, or a single project grant. An **aggregator rule** explicitly downgrades any figure sourced only from a business-registry/aggregator site (ZoomInfo, einforma, Kompass, etc.) from `found` to `partial`.
- **Flagging:** a result is pulled out of the main file into a flagged file if confidence is `low`, the figure is hedged ("estimated"/"approximately"/"up to"), or the year is pre-2015.
- **Yield so far:** the repo's own expectation is that only **~36%** of searched partners yield a sourced figure; the rest land as `partial`/`not_found` because no public financials exist for small LNGOs. The DATA_DICTIONARY snapshot recorded 27 `searched`-tier partners, 98 `unpp`-tier, and 549 still on the `copilot_guess` fallback — i.e. most partners still rely on the colleague's original heuristic band pending more search/guess passes.
- **UNPP enrichment:** partner names are fuzzy-matched (rapidfuzz `WRatio` ≥ 88, with length/word-count guards) against UN Partner Portal exports dropped into blob `raw/unpp/`; as of the snapshot, 480/673 (71%) partners matched, but only 99 (15%) carry a usable self-reported budget band — UNPP presence and UNPP *budget data* are very different coverage rates.
- **Claude-guess pass** (offline, no web search): for partners with search context but no sourced figure, a second reasoning-only Sonnet pass turns gathered context (own scale signals → same-country peer anchors → global/sector sanity range as last resort) into a banded estimate, explicitly ranked above the Copilot fallback but below anything sourced.
- **Comparison/adjudication:** `pipeline.py compare` reconciles pipeline results against the Copilot record and flags genuine conflicts (>10× disagreement, unmatched, unparsed) for a small, capped set of Opus adjudication subagents — a real example cited in the repo is correcting Cáritas de Venezuela's budget via the EU Transparency Register (~€7.86M) after the org's own website yielded nothing.
- **A known past failure mode** is recorded in `CLAUDE.md`: an operator once searched ~150 partners but never ran `ingest`, losing all of that work because state only persists to blob on `ingest`, not on search — hence the "ingest after every batch" rule and a documented transcript-recovery procedure.
- Status per the README: the **bulk run is underway** — priority countries (CAR, Chad, DRC, Nigeria, Sudan) are complete; remaining non-priority countries are still being searched.

## Relation to frameworks

**Standalone — feeds no AA framework or pipeline in this KB.** It is unrelated to any hazard, trigger, or CERF anticipatory-action mechanism. Its only stated downstream consumer is a colleague's `notebooks/absorption_capacity.ipynb` (outside this repo, not itself a KB node), which loads `lngo_budget_estimates.csv` and derives further columns (confidence tiers, risk-score numerics, plotting helpers) at load time. The closest KB neighbours are other `analysis/` pages that are similarly repo-only/ad-hoc (e.g. `ibtracs-matching`) in that none has a deployed app or scheduled job — but none of those share its subject matter (partner financial capacity vs. hazard triggers).

## Sources & status

- **Repo:** `ocha-dap/ds-ait-lngo-research`, active branch `lngo-33-run` (`9fac894`). The repo is **code + prompts + docs only** — no data is committed; all canonical state (`raw_results.json`, the batch outputs, the consolidated CSVs) lives on **Azure blob** (`ocha-stratus`, container `projects`, prefix `ds-ait-lngo-research/`, stage `dev` by default) so two operators' Claude sessions can share and resume progress. `./data` is a git-ignored local scratch dir that only exists transiently while a batch is staged for `ingest`.
- **Key code (`code_ref`):** `CLAUDE.md` (the orchestrating-Claude runbook — critical rules, the search/guess loops, two-operator sharding, recovery procedure), `pipeline.py` (deterministic Python: resume tracking, blob I/O via `src/storage.py`, matching via `src/copilot.py`/`src/unpp.py`, figure parsing via `src/money.py`), and the three prompt templates (`worker_prompt_template.md`, `guess_prompt_template.md`, `adjudication_prompt_template.md`).
- **Data inputs are frozen extracts, not refreshed by anything:** the Copilot spine (`raw/ngo_partners_with_un_validation.xlsx`) and the UNPP exports (`raw/unpp/*.xlsx|csv`) are one-off files dropped into blob by hand; nothing in the repo re-pulls them. `src/money.py`'s FX table is pinned "as of 2024-07 (approximate, mid-market, for magnitude only)" and is explicitly not authoritative.
- **Status:** **active** — this is genuinely in-progress human-in-the-loop research (not dormant/frozen code), but it has no schedule, no deployment, and no CI; it only runs when an operator opens a Claude Code session in the repo and drives it. There is nothing to find in `infrastructure/deployments.md` or the pipeline registry for this repo, and that absence is correct — it isn't meant to be there.
