---
name: trigger-design
description: Design, analyze, validate, or write up an anticipatory-action trigger the team's way — correct vocabulary (activated, mechanism vs specific triggers, readiness vs action), the spec→analysis→report process, and the mandatory historical validation. Use for ANY work on AA triggers, framework activations, or backtests.
---

# Trigger design & validation — the team discipline

Full method: KB `methods/trigger-design.md` (the typology of shapes we've actually
built: `methods/trigger-patterns.md`). This skill is the discipline a trigger
analysis must follow; read the KB pages for depth and worked patterns.

## Vocabulary — get it right or the analysis reads wrong

- A **trigger mechanism** is the whole system for a framework; it contains **specific
  triggers** that do different things (different amounts, different **windows**).
  Rapid onset is typically staged **readiness** (long lead) → **action** (short lead).
- A **readiness activation releases only ~5%** (mobilisation) — the bulk is
  authorized only when an action/observational trigger follows. (Technically the
  whole budget transfers up front with an obligation to return the unspent remainder.)
- Say **"activated"** — never "fired".
- **Threshold met ≠ framework activated.** Consecutive-month requirements, lab
  confirmation, no-objection windows may all apply — record the FULL activation
  condition, not just the threshold.

## Process (spec → analysis → report, iterative)

1. **Trigger spec** (working group + DS feasibility): WHAT shock (target RP, which
   historical events must it catch), WHEN (lead time), WHERE, and the fund's risk
   tolerance. 2. **Trigger analysis** proposing a trigger that meets it.
3. Meets spec → **trigger report**; doesn't → revisit the spec. Templates: the AA
   Manual (internal Drive; extracts in `ds-knowledge-base-internal`).

## Thresholds are normalised per area — never shared absolutes

Calibrate per district / basin / pixel as a **percentile or return period of that unit's own
record**. Same rarity everywhere, different absolute values — that is correct.

- Never gate an area out for having small absolute values. A product that only reaches 0.5 %
  there is usable if those peaks land on the days people flooded. What disqualifies an area
  is no relationship with the hazard record, or a series too flat to take a percentile of.
- Judge usability rank-based: share of events reaching the area's own 80th percentile (20 %
  is chance), and AUC on annual maxima. Both are magnitude-invariant.
- Biased model? Set thresholds in **model space** from its own reforecast climatology.
  Judge points on correlation and forecast skill, not KGE (dominated by bias/variance).
- Many tied zeros ⇒ use **midrank** percentiles; "share strictly below" scores every zero
  day as 0.
- An absolute floor is a **noise floor** (e.g. SFED ≥ 0.05), not a trigger threshold.

## Validation — mandatory, every trigger

- **Backtest each specific trigger** (not just the mechanism): list every historical
  activation — as **years/seasons** (slow onset), **dates** (continuous rapid, e.g.
  flood), or **events** (discrete rapid, e.g. cyclones) — plus average historical
  lead time and accuracy vs target events.
- **Two historical records, not one**: impact (e.g. people affected) AND the
  observational indicator (e.g. actual rainfall), alongside the forecast. Skill has
  two links (forecast→hazard, hazard→impact); validating one proves nothing about
  the chain.
- **Always report return periods** — per-trigger and combined: the `return-periods`
  skill in this plugin.
