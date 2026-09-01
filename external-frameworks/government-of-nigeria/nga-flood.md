---
content_type: framework-external
framework: government-of-nigeria-nga-flood
org: Government of Nigeria
org_type: government
country_iso3: NGA
hazard: flood
status: in-development
valid_until: null
trigger_summary: >-
  In design — no framework document, and the candidate trigger below is an
  UNREVIEWED FIRST DRAFT by OCHA-CHD, not approved by the government or anyone
  else. Per-state multi-gauge riverine consensus triggers across the 14 states
  along the Niger and Benue rivers: a state triggers when its tuned consensus
  fraction of selected Google GRRR gauges (plus 4 GloFAS stations) simultaneously
  exceed their per-gauge return-period thresholds on the same day. Every state is
  calibrated to a uniform activation frequency of 6 fire-seasons in 26 (~4.5-yr
  return period), scored against 4-yr Floodscan flood events. Extends the method
  of OCHA's endorsed Adamawa framework nationally.
data_sources: [Google-GRRR, GloFAS, FloodScan-SFED, NiHSA]
prearranged_funding_usd: null
funding_by_source: {}
target_people: null
framework_doc: null
framework_doc_date: null
sources: []
activations: []
last_checked: "2026-08-03"
extra:
  org_note: >-
    Multi-agency government framework; no single owning agency confirmed yet
    (NiHSA's Annual Flood Outlook at-risk-community data feeds the design).
    If a single agency owner emerges, revisit the org / framework id.
  coordination: >-
    A national-level framework, NOT an OCHA/CERF instrument. Relationship to
    OCHA's own Nigeria flood framework (frameworks/nga-flooding, endorsed 2026
    Adamawa CERF design): the national framework covers Adamawa as one of its
    14 states and pins Adamawa's trigger to the endorsed OCHA configuration
    (same LGAs, gauge set, thresholds and activation frequency), so the OCHA
    framework is effectively a subset of / referenced by the national one.
  design_analysis: >-
    Unlike other external-frameworks pages this is not web-sourced: the trigger
    design is OCHA-CHD's own supporting analysis, in repo
    ocha-dap/ds-aa-nga-flooding — full method and per-state results in
    analysis/nga-niger-benue-multistate.md.
visibility: internal
---

# Nigeria flood — national-level AA framework (Government of Nigeria)

A national-level anticipatory action framework for riverine flooding in Nigeria,
in design as of mid-2026. It is a **government framework** (`org_type: government`
— multi-agency; not yet attributed to a single agency), a distinct category from
the org-programme frameworks that fill the rest of this layer: national frameworks
sit above individual programmes and may include or reference the OCHA/CERF
framework as a subset. It is **not** an OCHA/CERF framework — which is why it
lives here rather than in `frameworks/` (D53/D77). OCHA-CHD is doing the
supporting trigger design work.

> ⚠️ **Draft.** Everything below the scope line is an unreviewed first-pass
> draft analysis by OCHA-CHD. No part of the 14-state trigger design has been
> reviewed, endorsed, or approved — by the government, the working group, or
> internally. Treat the per-state configurations and performance numbers as
> exploratory.

**Scope:** the 14 states along the Niger and Benue main channels — Adamawa,
Anambra, Bayelsa, Benue, Delta, Edo, Imo, Kebbi, Kogi, Kwara, Nasarawa, Niger,
Rivers, Taraba — with ~89 riverine LGAs derived from a 10 km buffer of the main
channels.

**Trigger design (draft, in progress):** each state gets a multi-gauge consensus trigger
in the style of OCHA's endorsed 2026 Adamawa framework
([frameworks/nga-flooding/2026-06-18](../../frameworks/nga-flooding/2026-06-18.md)):
a tuned fraction of that state's selected Google GRRR gauges (plus 4 surviving
GloFAS stations) must exceed their individual return-period thresholds on the same
day. All states are tuned to the same activation frequency as the endorsed Adamawa
trigger (6 fire-seasons in 26, ~4.5-yr RP). The full methodology, per-state
performance (F1 0.50–0.91 on a small event sample), monitoring app, and open
issues are documented in
[analysis/nga-niger-benue-multistate](../../analysis/nga-niger-benue-multistate.md).

**Relationship to the OCHA framework:** national-level AA frameworks sometimes
include the corresponding OCHA framework as a subset, or at least reference it.
Here Adamawa's configuration is pinned to the endorsed OCHA design throughout the
national analysis, so activations in Adamawa would be consistent across both.

**Status:** purely in design — no framework document, funding envelope, or
governance arrangement exists yet, and the trigger analysis itself is a simple
unreviewed draft. `visibility: internal` because this page
describes unpublished, internally-known design work rather than public web
sources; flip to public if/when the framework is published.
