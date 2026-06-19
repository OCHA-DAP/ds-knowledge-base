# analysis/

Repos that are **analysis, not frameworks or pipelines** — captured so the work is findable and linked to the frameworks it supports.

A page is a **framework** only if it has its own published framework doc for that specific thing. Everything else that's analytical lands here:

- **regional-overview** — a regional doc whose country components are the real frameworks (e.g. `sahel-drought` → bfa/ner/mrt/tcd drought).
- **ad-hoc-activation** — one-off anticipatory action without a framework (e.g. `ssd-flooding`).
- **pre-framework** — early analysis that isn't yet (or never became) an endorsed framework.
- **exploratory** — repo-only exploration, no published framework.

One page per subject (`analysis/<name>.md`). Copy `_TEMPLATE.md`. Use `feeds:` to link the framework(s) an analysis supports — those edges show up in `infrastructure/dependency-graph.md`.

> Note (2026-06-17): the initial set was reclassified from `frameworks/`; those pages retain framework-style body sections from their first ingest — a re-shape to this template's structure can come on a future re-ingest.
