# Phase 2 — broad ingestion: scope & cost

Estimate for automating the branch-aware ingestion the sample proved by hand, across the in-scope corpus. **Not yet approved — this is the scoping artifact.**

## What Phase 2 does

The workflow automates exactly what the 8 sample agents did: per unit → **survey branches → read the active branch → resolve + extract the latest PDF → reconcile PDF vs repo → emit a schema-conformant page** (+ folder README / catalog entry). Then a verification pass lints each page (frontmatter parses, required fields, `n_windows` matches the table) and adversarially spot-checks triggers/discrepancies.

## Sub-phases

| | What | Size | Cost |
|---|---|---|---|
| **2a — build & validate** | Write the workflow; run it on the **6 frameworks we did by hand**; diff against the hand-authored pages; fix the prompt until it reproduces them | ~6 agents | small (~0.5M tokens) |
| **2b — broad run** *(the billable bulk)* | Fan out across the in-scope corpus → reviewable PRs | ~75–90 agents | see below |
| **2c — review** | Human-review PRs; regenerate catalog + lineage | human time | — |

## Work-list (from `docs/repo-manifest.md`)

109 in default scope. Resolved into ingestion units:

| Type | Units | Notes |
|---|---|---|
| Frameworks (current version) | ~38 | 44 repos − ~6 `-app`/`-monitoring`/`-impactmodel` companions (→ pipeline/app pages) |
| Pipelines + apps + other | ~30 | of 59 "pipeline/other"; ~29 are ad-hoc/support/legacy → defer or quick-stub |
| Libs | 6 | → infrastructure / methods pages |
| **Core total** | **~74–90** | |

**Deferred (not in this run):** historical framework *versions* (the deep "100+ versions" history — current version only for now), archived/COVID-era `pa-*`, full GH Pages app inventory, semantic-search index. First: **clone the ~40 missing in-scope repos** (cheap git op).

## Token & cost estimate

Empirical anchor: sample agents averaged **~62k tokens** (range 40–100k).

- **Core run:** ~80 agents × ~80k ≈ **~6M tokens**
- **+ verification** (~80 lighter agents × ~25k) ≈ **~2M**
- **+ synthesis / catalog / orchestration** ≈ **~2M**
- **Total ≈ 8–12M tokens** (toward the high end if agents read deeply or we add history)

### Two delivery models

**A) In-session Workflow** *(recommended — what we validated)*. Runs as a Claude Code workflow spawning the agents in this session. Cost = Claude Code usage against your plan, **no separate API bill**; ~the same token volume (8–12M).

**B) Standalone API pipeline.** A Python script (Anthropic SDK) you run; billed per-token, so **Batches API (−50%)** and **prompt caching (≈0.1× on the shared schema/spec prefix)** apply. Rough $ for the full ~10M-token run *before* those discounts:

| Model (bulk agents) | ~$ before discounts | with Batches −50% |
|---|---|---|
| Haiku 4.5 ($1/$5) | ~$20–40 | ~$10–20 |
| **Sonnet 4.6 ($3/$15)** | **~$45–90** | **~$25–45** |
| Opus 4.8 ($5/$25) | ~$80–170 | ~$40–85 |

(Caching on the shared prefix knocks input cost down further — the per-agent system prompt + schema + INGESTION spec is identical across all ~80 agents.)

## Model recommendation

**Sonnet 4.6 for the bulk extraction/reconciliation agents** (structured, well-specified work it handles well at ~40% less than Opus), **Opus / me for the schema-sensitive synthesis + the adversarial verification pass**. This is a cost call that's yours to make — default would be Opus throughout (higher quality, ~2× the cost).

## Cost drivers / uncertainty

The estimate swings on: how many files each agent reads (deep repos cost more), whether we include historical versions (multiplies framework count ~3×), and verification depth. Ranges above assume current-version-only + single-vote verification.

## The ask

Approve **2a (build & validate, ~free)** to de-risk, then a go/no-go on **2b** with a chosen model tier and delivery model before the billable fan-out launches.
