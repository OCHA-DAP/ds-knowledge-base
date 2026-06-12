---
content_type: framework
framework:          # stable id grouping versions, e.g. bfa-drought
version:            # dated published version, e.g. 2026-04-17 (the framework-doc date — NOT git history)
status:            # piloted | endorsed | active | retired | superseded
country_iso3:      # e.g. BFA — may be a LIST for multi-country frameworks, e.g. [SLV, GTM, HND]
hazard:            # drought | flood | tropical-cyclone | cholera | ...  (open vocab)
admin_level:       # int or null
geographic_scope: []   # regions / pcodes in scope
data_sources: []       # tags, e.g. [SEAS5, CHIRPS]  (open vocab)
trigger_facets:        # coarse tags to FIND similar triggers — NOT a spec
  basis:           # forecast | observational | mixed
  structure:       # single | multi-window | readiness-activation | cascade | other
  calibration:     # return-period | percentile | absolute | bespoke
  primary_indicator:   # e.g. tercile-prob | SPI | discharge-RP | wind-buffer
supersedes:        # prior dated version or null
# --- documents, authority-ranked ---
framework_doc:     # URL of the AUTHORITATIVE latest framework PDF (ReliefWeb/unocha)
framework_doc_date:  # date of that PDF
framework_doc_annexes: []  # per-country / technical annex PDFs when the doc is split (e.g. multi-country umbrella + country annexes)
languages: [en]    # framework-doc languages (en/fr/es); translations are NOT separate versions
model_report:      # HDX URL — LEGACY/supporting technical note, index only, not authoritative
apps: []           # deployed marimo app URL(s) — increasingly the deliverable
operated_by:       # who runs the LIVE trigger if not this repo — e.g. IRI Maproom, INAM/PRISM, INSIVUMEH. null if OCHA/CHD.
raw_extract: []    # path(s) to full-text markdown extraction of the PDF(s)
# --- source repo & reconciliation ---
source_repo:       # local path and/or ocha-dap/<repo> (+ subpath if pipeline in a subdir)
source_sha:        # commit this page was generated from
code_ref: []       # repo paths to the canonical trigger code
trigger_source:    # framework_doc | repo  — where the authoritative trigger was taken from
repo_completeness: # full | partial | lost — does the repo actually contain the analysis?
discrepancies: []  # where repo and PDF disagree, or analysis is missing
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
Almost every framework has 2–3 windows/triggers, each with its own threshold, lead time, and return period. Structure them here (drop columns that don't apply):

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

## Key decisions & rationale
Why this threshold / source / scope. The judgment that isn't obvious from the code.

## Changes from previous version
What changed vs `supersedes`, and **why**. (Highest-value section across versions.)

## Open questions / known issues
