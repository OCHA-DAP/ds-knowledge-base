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
| framework | `frameworks/` | An AA framework + its versions — **only if it has its own published framework doc** | structured frontmatter + consistent headings |
| pipeline | `pipelines/` | A living operational system: dataset ingest, monitoring, exposure | runbook |
| app | `apps/` | A deployed interactive surface (marimo/Dash/Quarto) on Azure or GH Pages | structured frontmatter + what-it-shows |
| analysis | `analysis/` | A repo that is analysis — NOT a framework or pipeline (regional overview, ad-hoc activation, pre-framework exploration) | structured frontmatter + findings |
| library | `infrastructure/libs/` | A shared Python library the team builds on (`ocha-stratus/lens/relay/anticipy`, `ds-toolkit`, …) | API/usage reference: purpose, install + auth, key API, used-by |
| method | `methods/` | Cross-cutting how-we-do-it (trigger typology, calibration, monitoring design) | free prose, emerges bottom-up |
| infrastructure | `infrastructure/` | Conventions: storage, DB, stratus/lens, GHA patterns | reference |

Apps are deliverables/deployments, distinct from pipelines (which transform data on a schedule). The deployment *inventory* is `infrastructure/deployments.md`; `apps/` pages add the per-app prose.

**framework vs analysis — the rule.** A page is a `framework` **only if a published framework doc exists for that specific thing** (`trigger_source: framework_doc`). Frameworks with a real-but-**non-public** doc still count — note it in `extra.doc_status` (e.g. mmr/vut/yem). Everything else analytical → `analysis/`: a **regional overview** whose components are the frameworks (sahel), an **ad-hoc activation** (ssd), or **exploration** that never became an endorsed framework (caf/syr/cod-flooding/eth-flooding/nga-cholera). When ingesting: no framework doc for *this* thing ⇒ it is **not** a framework — produce an `analysis/` page.

Datasets are **tags**, not pages by default (`data_sources: [SEAS5]`, `inputs: [...]`). A dataset graduates to a thin `infrastructure/datasets/<name>.md` page **only** when a shared fact would otherwise be duplicated across pages (resolution, leadtime/CRS convention, licensing). Promote on the second duplication, not before.

## Structure only what helps you *find* things

Frontmatter = facets for lookup, **not** a spec you could execute from. Triggers especially: capture coarse `trigger_facets` to find similar ones, then describe the actual logic in prose + `code_ref`. Do not try to normalize a trigger into fields — the variation is the asset.

Tag vocabularies (`hazard`, `data_sources`, `trigger_facets.*`, pipeline `type`) are **open** — extend them as ingestion surfaces new values. Keep the *questions* (headings) consistent across pages; let the *answers* be as idiosyncratic as the work.

## Document authority & reconciliation

A framework's knowledge lives in several places with **different authority**. Rank them:

1. **Latest framework PDF** (`framework_doc`, ReliefWeb/unocha) — **authoritative for the trigger.** Dated, versioned, often bilingual (translations are the same version, not new ones).
2. **Repo** (code + `exploration/` + README) — the analysis that *derives/implements* the trigger. Should match the PDF, but the analysis sometimes gets lost.
3. **Older framework PDFs** — version history (`supersedes` chain).
4. **Model report** (`model_report`, HDX) — **legacy, index only.** Not authoritative; link it for discoverability and move on.

**Ingestion is reconciliation, not transcription.** Take the trigger from the latest PDF, then check the repo: is the analysis present (`repo_completeness: full|partial|lost`)? Does it match? Record any gaps in `discrepancies` — don't smooth them over; the mismatch *is* useful knowledge.

**README is unreliable** — only ~half document the trigger and few link the PDF. Read across README + `exploration/*.md` + `pipelines/` + `src/`, not the README alone.

**Work is usually NOT on `main`, and a newer trigger may be unpublished.** Survey branches (`git branch -a`, sort by commit date) — the current/operational analysis is frequently on a feature branch, with `main` up to a year stale. Read the **active** branch and record `source_branch`; never assume `main`. A trigger version newer than the latest published PDF can exist on a branch but not yet be endorsed → ingest it as a separate `status: in-development` page (`trigger_source: repo`, `framework_doc: null`), clearly marked not-yet-authoritative. The published PDF stays authoritative only for the *endorsed* trigger.

**Don't default `activations: []` without hunting.** `activations` records **real** activations (AA fired / funds released), and the framework PDF often references them only generically ("previous AA activations"). Before recording `[]`, check: the `## Historical activations` and CERF/funding sections of the PDF, the repo (activation notebooks, `exploration/`, dated trigger-fired notes), and — when the PDF implies past activations but doesn't name them — a quick web/ReliefWeb/CERF-allocation search for the country+hazard. An endorsed framework with confirmed past activations stays `status: endorsed` — there is **no `triggered` status**. Two lifecycle states are *derived* at generation time (see `frameworks/_TEMPLATE.md` and `scripts/gen_*.py`), both persisting until a human next updates the version: **`recently-triggered`** (an activation fired under this version's reign — date ≥ version) and **`expired`** (the version's `valid_until` passed without it ever firing). So getting the **activation dates** and **`valid_until`** right is what drives the lifecycle. `[]` is a real claim ("never activated"); only assert it once you've looked.

**Multi-country frameworks: NAME every activating country in each activation note.** The public site (`gen_public_site.py`) splits a multi-country framework into one row/marker **per country**, and attributes an activation to a country **only if that country's ISO3 _or_ full name appears in the activation's `note`/`window` text** (`acts_for_country`). A joint activation written as "GTM + SLV" therefore leaves the third country looking un-activated. Source/press reporting is lead-country-centric and routinely names only the headline country — **do not trust it**: when an activation spans several countries, web-search/CERF-check each member country and write the ISO3 **and** name of *every* country that activated into the note. (Real miss: the LAC Dry Corridor 5 Mar 2026 activation was GTM + SLV + **HND** but was recorded as GTM + SLV, with the body even asserting "Honduras did not activate".)

**All-in vs. partial-window activation.** Only a **full ("all-in") activation flips a framework to `recently-triggered`.** Where a single window firing releases the **whole** envelope (e.g. mrt-drought, either window → full CERF), that's all-in → record it normally. Where windows release **partial, per-window** amounts (e.g. tcd-drought W1 $3.05M / W2 $1.33M / W3 $3.62M), one window firing is **not** a whole-framework activation: record it in `activations` with **`full_activation: false`** so it is captured (and shown, tagged "(window)") **without** flipping the status — the framework stays `endorsed` (shown publicly as **"Active"**). The lifecycle deriver (`own_activation_ym`) ignores `full_activation: false` entries.

**Funding & scope facets.** `prearranged_funding_usd` is the TOTAL pre-arranged (the headline comparative number); break it down by source in `funding_by_source` (e.g. `{CERF: 12000000, AHF: 10000000}`) — the total should equal the sum. **Co-financing is separate:** partner/government money arranged *alongside* the trigger envelope goes in `cofinancing_usd` + `cofinancing_sources` (the framework doc states it when present) — don't fold it into the pre-arranged total. Also capture `implementing_agencies` and total `target_people`. Per-window/per-country splits stay in `extra` or the Per-country table. `null`/`[]`/`{}` when the doc doesn't state it; development-stage repos with no published doc have no funding.

**Indicators are per-window and plural.** A window may key off one or several indicators (wind AND rainfall); list them all in the Trigger-windows `indicator` cell. Do NOT designate a single "primary" indicator. `trigger_facets.indicators` is just the flat union of indicators across windows, for search.

**Monitoring period — when the framework can fire.** `monitoring_period.months` is the set of calendar months (ints 1–12) during which the framework can **possibly** trigger — the live window when a check/decision can fire, taken as the **union across all windows**. It answers "which frameworks could activate in March?". Two cases:
- **Rapid-onset** (cyclone, hurricane, flood): the hazard-**season span** the doc states (e.g. SW Indian Ocean cyclone season Nov–Apr → `[11,12,1,2,3,4]`). `source: stated`.
- **Slow-onset** (drought, dry-corridor): the doc rarely states a "season", so **infer** the specific decision/check months from the trigger wording — the forecast **issue-months** or seasonal-monitoring windows that drive an activation decision, **not** the months being forecast about (a March-issued forecast of JJAS rainfall is monitored in March, not Jun–Sep). `source: inferred`. Put the per-window timing in `note` (e.g. "readiness on Mar SEAS5, action on Jul update").

Set `source` honestly — it marks whether the months are authoritative (from the doc) or our reading of the trigger. `[]` + a note only when genuinely indeterminable.

**Tag discrepancies by kind — "old" vs "wrong".** Prefix every `discrepancies` entry: `[stale]` (legacy/superseded code or values still in the repo but NOT the live trigger — informational, don't act on it), `[conflict]` (the repo and the authoritative doc actually disagree about the live trigger — needs attention), or `[gap]` (the analysis can't be found). This stops "old code lying around" from reading like a live error.

## Source pointers (every page)

Every page is a card in a catalog over the raw sources. Mandatory: `source_repo`, `source_sha` (drift anchor, Phase 5), `code_ref`, and the authority-ranked document links above (`framework_doc`, `model_report`, `apps`).

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
- **Spoke → hub**: each source repo gets a generated README `KB-POINTER` header + a thin agent-facing `CLAUDE.md` pointing up to its KB page (status, active branch, conventions, sibling frameworks). Added in Phase 4.

A repo can't know about its siblings — cross-framework comparison is the hub's job. Depth stays in the repo.

### How much goes in the hub vs the spoke

**The hub is the *complement* of the spoke, not a copy of it.** One-home-per-fact: each fact has a single home, and the other side *links*.

- **Push detail down by default.** Operational, code-coupled, volatile facts — exact commands, DB schemas, env vars, job configs, failure playbooks, step-by-step runbooks — live in the **spoke**, next to the code they can't drift from. A rich spoke README (e.g. `ds-storms-pipeline`, ~300 lines) is a *feature*; don't restate it.
- **The hub carries only what the spoke structurally can't:** the **comparative** layer (`catalog.md`, "all drought triggers", the `methods/` typology), the **reconciliation** layer (PDF-vs-code `discrepancies` — a synthesis with no single other home), a **consistent summary schema** so every unit is scannable/queryable, and **pointers** to the raw sources. Plus anything with no repo home (infra conventions, portfolio facts).
- **Hub depth ∝ 1 / spoke quality.** Where the spoke is an excellent runbook, the hub page is a thin summary + "for the full detail, see the repo." Where the repo is thin, stale, or a multi-branch mess (common for framework repos), the hub page legitimately carries more — it's often the best summary that exists.
- **The test:** would someone comparing *across* units need this, and is it stable? → hub. Does it change whenever the code changes? → spoke; the hub links.
- **Never duplicate a fact you intend to keep accurate** — duplication = drift. The one allowed exception is a deliberately-frozen *summary*, which is explicitly secondary to the code (`> The canonical X is the code at code_ref; this page explains it`). For the irreducible overlap, the `source_sha`/`code_ref` drift check (Phase 5) flags when the summarised code has moved.

## How the KB is kept current

1. **Capture-as-you-go** (primary): finishing real work → update the affected page as the last step. Repo `CLAUDE.md` first (closest to code), summary propagates up.
2. **Gaps surface through use**: looked something up and it's missing/stale → leave a stub or `<!-- TODO -->`, don't silently move on.
3. **Drift automation** (Phase 5, safety net): scheduled job compares each repo's `HEAD` to the page's `source_sha`, opens a **PR** (never auto-commits) for stale pages. Build only once a real corpus exists.

## Adapting the structure

The format follows the findings. Expect the schema to shift during ingestion. Discipline:
- Stabilize the **core** (shared fields/headings); let the **edges** flex.
- Adapt in deliberate **sweeps** across all pages, not page-by-page drift (drift → inconsistency → broken lookup).
- It's all markdown in git: a restructure is a bulk edit + a `git diff` you review, not a migration.
- Use the **`extra: {}` escape hatch** to stash data that doesn't fit a field *yet* (incl. ingestion `SCHEMA_STRAIN` notes) — this keeps the structured core clean instead of loosening it. When the same key keeps showing up in `extra`, that's the signal to promote it to a real field.
