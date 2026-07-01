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
| framework | `frameworks/` | An AA framework + its versions. **Scope = the full OCHA/CERF AA portfolio** (D51), incl. historical pilots and frameworks with no DS repo and no modern published doc — draft from whatever public OCHA/CERF material exists (`source_repo`/`framework_doc` may be `null`). The [`kb-aa-watch`](../infrastructure/automation.md) axis surfaces missing ones. | structured frontmatter + consistent headings |
| pipeline | `pipelines/` | A living operational system: dataset ingest, monitoring, exposure | runbook |
| app | `apps/` | A deployed interactive surface (marimo/Dash/Quarto) on Azure or GH Pages | structured frontmatter + what-it-shows |
| analysis | `analysis/` | A repo that is analysis — NOT a framework or pipeline (regional overview, ad-hoc activation, pre-framework exploration) | structured frontmatter + findings |
| library | `infrastructure/libs/` | A shared Python library the team builds on (`ocha-stratus/lens/relay/anticipy`, `ds-toolkit`, …) | API/usage reference: purpose, install + auth, key API, used-by |
| dataset | `infrastructure/datasets/` | A **third-party** data source we consume regularly but don't produce (IPC/CH, HDX, HRP/HNRP, FEWS NET, EM-DAT, WorldPop, FAO ASI/VHI, GHSL) | reference: access/API + auth, resolution, license, loader (`code_ref`), used-by (see the folder [README](../infrastructure/datasets/README.md)) |
| method | `methods/` | Cross-cutting how-we-do-it (trigger typology, calibration, monitoring design) | free prose, emerges bottom-up |
| infrastructure | `infrastructure/` | Conventions: storage, DB, stratus/lens, GHA patterns | reference |

Apps are deliverables/deployments, distinct from pipelines (which transform data on a schedule). The deployment *inventory* is `infrastructure/deployments.md`; `apps/` pages add the per-app prose.

**Rendered static sites (Quarto/RMarkdown books, marimo-WASM exports, docs/maps sites).** Many repos publish a rendered "nice version" via **GitHub Pages or Netlify**, often off a feature branch's `docs/`, not `main`. These are not full `apps/` pages — capture them two ways: (1) put the URL in the owning page's `apps:` frontmatter list, and (2) add a row to the **GitHub Pages & Netlify** table in `infrastructure/deployments.md` (record the serving branch — the published site can lag `main`). Don't invent a new frontmatter key (`netlify_app:` etc.); `apps:` + the registry is the one home.

**framework vs analysis — the rule.** A page is a `framework` if it **was an endorsed AA framework in the OCHA/CERF portfolio** (D51) — preferably evidenced by a framework doc (`trigger_source: framework_doc`), but a historical pilot whose only surviving public record is an OCHA/CERF *learning/portfolio* report still counts (e.g. som-drought 2019, cf. the eth-drought 2020 pilot): set `framework_doc` to that report and draft via `ingest_framework_web.py`. Frameworks with a real-but-**non-public** doc also count — note it in `extra.doc_status` (e.g. mmr/vut/yem). `analysis/` is for things that **never were an endorsed framework**: a **regional overview** whose components are the frameworks (sahel), or **exploration** that never became one (caf/syr/cod-flooding/eth-flooding/nga-cholera). **Judgment call** for a real pilot that activated but you can't confirm a standalone framework (e.g. ssd flood 2022) — if it was a CERF AA *framework* it's a `framework`, if a one-off anticipatory allocation it's `analysis`; record which in `extra`.

**Framework IDENTITY — one framework per country+hazard; new versions SUPERSEDE (D62).** A framework *is* the **country–hazard combo**. There is never more than one framework for the same country and hazard, and a newly published version does not create a second framework — it is a **new version that supersedes** the previous one (the older flips to `status: superseded`; the new one carries `supersedes:` and becomes the endorsed version). So a fresh PDF for a country+hazard we already hold is **not a "new framework"** — it's a version bump of the existing framework's folder. (The folder slug may not literally read `<iso3>-<hazard>` — e.g. DR Congo cholera lives in `cod-infectious-disease/` — so **match on the `country_iso3` + `hazard` fields, not the folder name**, when deciding whether we already hold a framework.) This is why the discovery axes must catch a **newer published version** of a framework we hold, not just brand-new country+hazard combos or *older* back-catalogue versions.

**Framework OWNERSHIP — a framework page is OCHA/CERF-owned (D53).** Scope is the OCHA-facilitated, **CERF-financed** AA portfolio. A framework run by another body is **out of scope even when OCHA-CHD does supporting analysis**: **IFRC/Red Cross Early Action Protocols (EAPs)**, **FAO/WFP/government** early action, and **plain CERF allocations** (rapid-response / underfunded / top-ups that aren't a triggered AA-framework release). **The operational framework and OCHA's are often different things** — e.g. the framework that triggers in **Kenya** is the IFRC/KRCS **EAP2022KE02** (its activations are the Red Cross's), while **OCHA's** Kenya drought framework is the *separate, in-development* trigger in the repo. When OCHA only does exploratory analysis of another body's framework, ingest **OCHA's** as `status: development` / `trigger_source: repo` / `framework_doc: null`, record the operational (e.g. IFRC) framework as context in `extra.operational_*`, and **never put the other body's activation in `activations:`** (that derives a false `recently-triggered`). If a candidate isn't OCHA/CERF-owned, it's not a framework page.

Datasets are **tags**, not pages by default (`data_sources: [SEAS5]`, `inputs: [...]`). A dataset graduates to a **`dataset` page** at `infrastructure/datasets/<name>.md` in either of two cases: (1) a shared fact (resolution, leadtime/CRS convention, licensing, access pattern) would otherwise be duplicated across pages — **promote on the second duplication, not before**; or (2) it's a **third-party source we rely on regularly** and want a single home for *where the API is, how we access it, and how we use it* — the trusted-external-source registry the folder [README](../infrastructure/datasets/README.md) governs. **Don't duplicate a source we already ingest via a pipeline** — the pipeline page is its reference (IMERG, FloodScan, ACLED, NHC, IBTrACS/SEAS5/ERA5, GDACS/GloFAS); at most leave a one-line stub pointing there. Country/partner one-offs stay tags until a second page duplicates their facts.

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

**Always extract `valid_until` from the framework doc.** The validity period is stated in the PDF — look for a "Validity"/"Validité" section or the CERF financing wording ("for a period of two years from… pre-approval", "pre-arranged for two cyclone seasons 2025/2026 and 2026/2027", "until the end of 2025"). Convert it to the END date (`YYYY` | `YYYY-MM` | `YYYY-MM-DD`) and add a `# doc: …` comment with the quote. Only set `null` if the doc genuinely states no period (e.g. an early pilot) — and add a comment saying so. `scripts/check_validity.py` (CI: `.github/workflows/validity-check.yml`, on push to `frameworks/**` + weekly) flags **expired-but-still-endorsed** versions (review → renew/supersede/retire), plus missing/malformed `valid_until`.

**Multi-country frameworks: NAME every activating country in each activation note.** The public site (`gen_public_site.py`) splits a multi-country framework into one row/marker **per country**, and attributes an activation to a country **only if that country's ISO3 _or_ full name appears in the activation's `note`/`window` text** (`acts_for_country`). A joint activation written as "GTM + SLV" therefore leaves the third country looking un-activated. Source/press reporting is lead-country-centric and routinely names only the headline country — **do not trust it**: when an activation spans several countries, web-search/CERF-check each member country and write the ISO3 **and** name of *every* country that activated into the note. (Real miss: the LAC Dry Corridor 5 Mar 2026 activation was GTM + SLV + **HND** but was recorded as GTM + SLV, with the body even asserting "Honduras did not activate".)

**All-in vs. partial-window activation.** Only a **full ("all-in") activation flips a framework to `recently-triggered`.** Where a single window firing releases the **whole** envelope (e.g. mrt-drought, either window → full CERF), that's all-in → record it normally. Where windows release **partial, per-window** amounts (e.g. tcd-drought W1 $3.05M / W2 $1.33M / W3 $3.62M), one window firing is **not** a whole-framework activation: record it in `activations` with **`full_activation: false`** so it is captured (and shown, tagged "(window)") **without** flipping the status — the framework stays `endorsed` (shown publicly as **"Active"**). The lifecycle deriver (`own_activation_ym`) ignores `full_activation: false` entries.

**`all_in` and "able to trigger" (capacity).** Separate from lifecycle *status*, the map derives whether a framework **can still fire now** — the **"able to trigger" ring**: **pulsing orange** = able & in monitoring season this month; **pale orange** = able & off-season; **no ring = cannot trigger**. (Colour semantics: **red = a real trigger** — the activation dots and the *recently-triggered* pin; **orange = able to trigger**.) A framework becomes **not able** after a full activation (its envelope is spent) — **except** cholera (recurring) and **multi-window SPLIT** frameworks. Set the **`all_in`** frontmatter field: **`true`/omitted** = one envelope released on any trigger (spent after firing → not able until renewed); **`false`** = each window has its own budget and fires independently (stays able after one window fires). Set `all_in: false` only for genuinely independent-budget multi-window frameworks. **Spent/expired → in development:** a framework whose endorsed version has fired or expired **and** has a newer in-development version is shown on the map as that **development** version (rebuilt for the next cycle) — it still carries the prior version's activation dots. Logic: `gen_public_site.py` (`able_to_trigger`/`retriggerable` + the `current`-version selection).

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

**The full classification model + where each kind of content lives is [docs/PRIVACY.md](PRIVACY.md).** Key rules: classification follows the **source**, not the content type (a full-text extract of a *public* framework PDF is public; *Google Drive content* is **internal**). And a second **metadata-vs-data** axis: a manifest is *less* sensitive than content, but at scale not automatically public — the **bulk Drive manifest is internal** (~9k aggregated partner/project filenames), so both it and the content live in the gitignored `drive/` store; the public repo carries only a **pointer** at `infrastructure/drive-index.md`. Public-source full-text → in-repo `raw/`. Promoting any individual Drive row/extract to public is a deliberate, per-item human decision.

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

1. **Capture-as-you-go** (primary): finishing real work → update the affected page as the last step. Repo `CLAUDE.md` first (closest to code), summary propagates up. **After editing any page, run the post-batch generators** (`scripts/README.md` → "Post-batch routine") — they rebuild the indexes and double as the YAML validator, so a bad frontmatter break fails loudly instead of silently rotting `catalog.md`.
2. **Gaps surface through use**: looked something up and it's missing/stale → leave a stub or `<!-- TODO -->`, don't silently move on.
3. **Drift automation** (safety net): scheduled job compares each repo's `HEAD` to the page's `source_sha`, opens a **PR** (never auto-commits) for stale pages. The full self-maintenance system is mapped in [infrastructure/automation.md](../infrastructure/automation.md).
4. **The meta-docs maintain themselves too** (this file, DESIGN, ROADMAP, automation, the READMEs):
   - **Never hand-type counts** — they're generated by `scripts/gen_doc_counts.py` into the `<!-- COUNTS -->` block (run it in the post-batch routine).
   - `scripts/check_docs.py` (weekly, `kb-docs` issue) flags stale counts + dangling script/workflow refs; `lint-docs.yml` (`mkdocs build --strict`) fails on broken internal links; a monthly `docs-audit.yml` Claude pass fixes prose staleness → PR.
   - **When you ship a phase or change the approach, update ROADMAP/DESIGN in the _same_ PR** — and add a *dated* DESIGN entry rather than silently editing (the history is the point).

## Adapting the structure

The format follows the findings. Expect the schema to shift during ingestion. Discipline:
- Stabilize the **core** (shared fields/headings); let the **edges** flex.
- Adapt in deliberate **sweeps** across all pages, not page-by-page drift (drift → inconsistency → broken lookup).
- It's all markdown in git: a restructure is a bulk edit + a `git diff` you review, not a migration.
- Use the **`extra: {}` escape hatch** to stash data that doesn't fit a field *yet* (incl. ingestion `SCHEMA_STRAIN` notes) — this keeps the structured core clean instead of loosening it. When the same key keeps showing up in `extra`, that's the signal to promote it to a real field.
