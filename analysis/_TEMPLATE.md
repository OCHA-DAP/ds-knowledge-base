---
content_type: analysis
name:              # stable id, e.g. sahel-drought
analysis_type:     # exploratory | ad-hoc-activation | pre-framework | regional-overview | other
status:            # active | dormant | one-off | superseded-by-framework
country_iso3:      # ISO3 or list, or "regional"
hazard:            # drought | flood | tropical-cyclone | cholera | ...
summary:           # one line — what this analysis is and why it isn't a framework
data_sources: []   # tags
feeds: []          # framework / pipeline node ids this analysis supports (regional-overview / pre-framework). [] if standalone
# --- source repo ---
source_repo:       # ocha-dap/<repo>
source_branch:
source_sha:
code_ref: []
depends_on: []     # canonical KB node ids it needs (powers the dependency graph)
discrepancies: []  # [stale]/[conflict]/[gap] tagged, as for frameworks
extra: {}
visibility:        # internal | public
last_synced:
---

# {Subject} — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is
One paragraph: what was analyzed and why it is not (or not yet) a framework.

## What was analyzed / findings
The substance — candidate triggers explored, thresholds, comparisons, conclusions.

## Relation to frameworks
Which real framework(s) this feeds or pre-figures (see `feeds`), or "standalone".

## Sources & status
Repo, key code (`code_ref`), how complete/current it is, and where it stands (active / dormant / superseded by a framework).
