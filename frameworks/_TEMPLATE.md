---
content_type: framework
framework:          # stable id grouping versions, e.g. bfa-drought
version:            # dated published version, e.g. 2026-04-17 (framework-doc date, NOT git history). development/pre-development (no published doc): use the branch name or draft-<label>.
status:            # pre-development | development | endorsed | triggered | superseded | retired
                   #   pre-development = scoped, not yet built (often INTERNAL info — not on the OCHA AA map; hard to tell from repo/public sources, default to development);
                   #   development = being built (may be ahead of the published PDF, repo/branch only);
                   #   endorsed = officially approved/published; triggered = endorsed AND has activated (real trigger fired — see activations);
                   #   superseded = replaced by a newer version; retired = discontinued
country_iso3:      # e.g. BFA — may be a LIST for multi-country frameworks, e.g. [SLV, GTM, HND]
hazard:            # drought | flood | tropical-cyclone | cholera | ...  (open vocab)
admin_level:       # int or null
geographic_scope: []   # regions / pcodes in scope
data_sources: []       # tags, e.g. [SEAS5, CHIRPS]  (open vocab)
trigger_facets:        # coarse tags to FIND similar triggers — NOT a spec
  basis:           # forecast | observational | mixed
  calibration:     # return-period | percentile | absolute | bespoke
  indicators: []   # ALL indicators used across the windows, as a flat set for search, e.g. [CDI, SEAS5-tercile-prob]. NO "primary" — a framework/window may use one or several. The per-window mapping is the Trigger windows table (a window can list multiple). [] only if genuinely none.
  n_windows:       # int — rows in the Trigger windows table. A "window" = a distinct activation window/component; redundant data sources for the SAME activation collapse into ONE row (e.g. two gauge stations for one riverine trigger = 1 window). Discriminating + queryable; staging *pattern* → methods/trigger-patterns.md.
  window_axes: []  # how the windows differ: time (readiness/action, issued-month, season) | space (which area) | severity. Usually [time]; forecast-vs-obs folds into time. [] if single window.
monitoring_period:   # the months during which the framework can POSSIBLY trigger (the live window when a check/decision can fire). Union across all windows.
  months: []         # ints 1-12, e.g. [11,12,1,2,3,4]. Rapid-onset: the hazard-season SPAN stated in the doc (cyclone/flood/hurricane season). Slow-onset (drought): the specific decision/check months — INFER from the trigger wording (which forecast issue-months / seasonal windows drive an activation decision), NOT the months being forecast about. [] only if genuinely indeterminable (leave a note).
  source:            # stated | inferred — stated = the doc gives an explicit season span or monitoring months; inferred = derived from trigger wording / lead times (typical for slow-onset).
  note:              # one line: season name + provenance (doc section or the wording it was inferred from) + any per-window nuance (e.g. "readiness Mar, action Jul").
supersedes:        # prior dated version or null
# --- funding & scope ---
prearranged_funding_usd:   # TOTAL pre-arranged funding committed in advance, USD int (= sum of funding_by_source). Headline comparative number. null if none/development-stage.
funding_by_source: {}      # pre-arranged amounts by source, USD ints, e.g. {CERF: 12000000, AHF: 10000000}. {} if a single unspecified source or unknown.
cofinancing_usd:           # additional CO-FINANCING arranged alongside the trigger (partner/government top-up beyond the pre-arranged envelope), USD int. null if none/not stated. Stated in the framework doc when present.
cofinancing_sources: []    # who co-finances, e.g. [WFP, government]. [] if none.
implementing_agencies: []  # UN/partner agencies receiving the funds, e.g. [FAO, WFP, UNICEF] (open vocab). [] if not stated.
target_people:             # total population targeted, int. Per-region / per-window / per-country splits stay in extra or the Per-country table.
# --- documents, authority-ranked ---
framework_doc:     # URL of the AUTHORITATIVE latest framework PDF (ReliefWeb/unocha)
framework_doc_date:  # date of that PDF
framework_doc_annexes: []  # per-country / technical annex PDFs when the doc is split (e.g. multi-country umbrella + country annexes)
languages: [en]    # framework-doc languages (en/fr/es); translations are NOT separate versions
model_report:      # HDX URL — LEGACY/supporting technical note, index only, not authoritative
raw_extract: []    # path(s) to full-text markdown extraction of the PDF(s)
# --- live system (apps are DEPLOYMENTS, not documents — full inventory in infrastructure/deployments.md) ---
operated_by:       # who runs the LIVE trigger if not this repo — e.g. IRI Maproom, INAM/PRISM, INSIVUMEH. null if OCHA/CHD.
apps: []           # deployed app URL(s) — Azure web app and/or GH Pages. Cross-ref to deployments.md.
depends_on: []     # canonical KB node ids this framework DIRECTLY needs (upstream): its monitoring pipeline(s), shared data pipelines, comms (listmonk). Use page ids (framework folder / pipeline|app filename) or a shared-infra id. Reverse edges (what depends on this) are computed by scripts/gen_dependency_graph.py → infrastructure/dependency-graph.md.
# --- source repo & reconciliation ---
source_repo:       # local path and/or ocha-dap/<repo> (+ subpath if pipeline in a subdir)
source_branch:     # which branch this page reflects — work is OFTEN NOT on main (main can be a year stale)
source_sha:        # commit this page was generated from
code_ref: []       # repo paths to the canonical trigger code
trigger_source:    # framework_doc | repo  — where the authoritative trigger was taken from
repo_completeness: # full | partial | lost — OR a layered map when it differs by layer, e.g. {analysis: full, deployed_code: stale}
discrepancies: []  # where repo and authoritative doc disagree, or analysis is missing. PREFIX each entry to mark its KIND — distinguish "old" from "wrong":
                   #   [stale]    = legacy/superseded code or values still present but NOT the live trigger (informational; don't act on it). e.g. "old 2025 R scripts left in repo".
                   #   [conflict] = repo and the authoritative doc actually DISAGREE about the live trigger (needs attention / may be a bug).
                   #   [gap]      = the analysis behind the trigger is missing or can't be found in the repo.
# --- activation history ---
activations: []    # REAL activations that occurred: [{date, window, note}]. [] = never activated. NOT backtested/simulated.
# --- escape hatch ---
extra: {}          # free-form: anything the schema doesn't capture YET (incl. ingestion schema_strain notes). NOT for things that already have a field.
visibility:        # internal | public
last_synced:       # YYYY-MM-DD or null
---

# {Country} {Hazard} — {version}

> Fill the headings below. Keep the **questions** even when the answer is "n/a".
> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary
One paragraph: what this framework triggers on and what it activates.

## Method
How it works end to end. Data → indicator → decision.

## Trigger logic
- **Keys off:** (data/forecast + indicator)
- **Decision rule (plain language):** a paragraph a non-coder could follow.
- **Activation structure:** stages / windows / AND-OR logic.
- **Calibration:** how the threshold was chosen, and against what (return period? historical events?).
- **Authoritative source:** the latest framework PDF (`framework_doc`). The repo (`code_ref`) implements/derives it.
- **Operated by:** if the live trigger runs outside this repo (IRI Maproom, INAM/PRISM, INSIVUMEH…), say so — the repo is then an analysis/derivation, not the production system.

## Trigger windows
Almost every framework has 2–3 windows/triggers, each with its own threshold, lead time, and return period. Structure them here (drop columns that don't apply).

**Counting rule:** one row per distinct activation window/trigger component. Redundant data sources feeding the SAME activation (e.g. two gauge stations for one riverine trigger) are **one** row, noted inline — not separate windows. `n_windows` = the row count.

**Indicators:** a window may key off **one or several** indicators (e.g. wind AND rainfall) — list all in the `indicator` cell. There is no single "primary" indicator; the frontmatter `trigger_facets.indicators` is just the flat union across windows, for search.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| e.g. readiness | forecast | … | … | … | … | … |

## Per-country variants
*(multi-country frameworks only — delete otherwise)* One shared design, per-country calibration. Note where the implementation scope differs from the framework scope.

| country | AOI | forecast source | threshold | budget |
|---|---|---|---|---|

## Sources & repo completeness
- **Trigger taken from:** `framework_doc` (default authority) — note if instead from repo.
- **Repo completeness:** full / partial / lost — is the analysis behind this trigger actually present in the repo?
- **Discrepancies:** anywhere the repo and the PDF disagree, or the analysis can't be found. (Don't paper over — flag it.)

## Monitoring
What's monitored, cadence, where it's published. Link the `pipelines/` page if a live pipeline does this.

## Historical activations
**REAL** activations that occurred (AA triggered / funds released) — date, which window fired, outcome. Keep DISTINCT from the simulated/backtested record (the return-period analysis under *Trigger windows*, i.e. "would have fired in years X, Y, Z"). "Never activated" is itself a fact worth stating.

## Key decisions & rationale
Why this threshold / source / scope. The judgment that isn't obvious from the code.

## Changes from previous version
What changed vs `supersedes`, and **why**. (Highest-value section across versions.)

## Open questions / known issues
