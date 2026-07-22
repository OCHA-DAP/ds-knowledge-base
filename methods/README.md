---
content_type: method
last_reviewed: "2026-06-12"   # bump when a human verifies the page is still accurate
---

# methods/

Cross-cutting "how we actually do it" — the knowledge that isn't tied to one framework or repo: trigger calibration, return-period selection, skill verification, monitoring design, framework review.

These pages **emerge bottom-up** from ingestion, not top-down. When a pattern recurs across ≥2 frameworks, it earns a page here and the framework pages link to it instead of re-explaining.

- [style-guide.md](style-guide.md) — the HDX v2 design system as the default style reference for everything we build: tokens/components mirror (internal repo), usage rules for humans + agents.
- [trigger-design.md](trigger-design.md) — how we develop & validate triggers: vocabulary ("activated", mechanism vs specific triggers, readiness/action), onset classes, the spec→analysis→report process, mandatory historical analysis, the two-historical-records rule. Anchored on the AA Manual (2024, internal Drive).
- [return-periods.md](return-periods.md) — Weibull RP; individual vs **overall** vs **effective** RP (and the ≤/≥ relations); all-in vs split funding; where RPs are published.
- [trigger-patterns.md](trigger-patterns.md) — the trigger typology, derived bottom-up from the ingested frameworks
- [static-data-apps.md](static-data-apps.md) — the static-data-app deployment pattern: pre-baked JSON exported from the DB at deploy time, served as static JS on GH Pages (or SWA) instead of a Python server on App Service. Reference impl: [apps/storm-exposure-compare](../apps/storm-exposure-compare.md).
- [pcode-matching.md](pcode-matching.md) — joining admin-level datasets on p-codes without silently losing or mis-attributing population: the four mismatch classes (code style, admin reforms incl. **code reuse across vintages** — Mali `ML09`, placeholders, population-group semantics), the audit recipe, the fix ladder. Reference impl: `ds-seas5-skill/pipeline/export_hnrp_drought.py`.
