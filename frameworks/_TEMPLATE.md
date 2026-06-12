---
content_type: framework
framework:          # stable id grouping versions, e.g. bfa-drought
version:            # v1 | 2024 | season label
status:            # active | piloted | retired | superseded
country_iso3:      # e.g. BFA
hazard:            # drought | flood | tropical-cyclone | cholera | ...  (open vocab)
admin_level:       # int or null
geographic_scope: []   # regions / pcodes in scope
data_sources: []       # tags, e.g. [SEAS5, CHIRPS]  (open vocab)
trigger_facets:        # coarse tags to FIND similar triggers — NOT a spec
  basis:           # forecast | observational | mixed
  structure:       # single | multi-window | readiness-activation | cascade | other
  calibration:     # return-period | percentile | absolute | bespoke
  primary_indicator:   # e.g. tercile-prob | SPI | discharge-RP | wind-buffer
supersedes:        # prior version id or null
date_published:    # YYYY-MM-DD or null
source_repo:       # local path and/or ocha-dap/<repo>
source_sha:        # commit this page was generated from
code_ref: []       # repo paths to the canonical trigger code
pdf: []            # links to source docs (+ full-text extraction path)
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
- **Canonical code:** see `code_ref`.

## Monitoring
What's monitored, cadence, where it's published. Link the `pipelines/` page if a live pipeline does this.

## Key decisions & rationale
Why this threshold / source / scope. The judgment that isn't obvious from the code.

## Changes from previous version
What changed vs `supersedes`, and **why**. (Highest-value section across versions.)

## Open questions / known issues
