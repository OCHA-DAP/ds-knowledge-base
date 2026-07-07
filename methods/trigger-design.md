---
content_type: method
last_reviewed: "2026-07-07"   # bump when a human verifies the page is still accurate
---

# Trigger design & validation

How the team develops and validates AA triggers — the cross-framework process and vocabulary.
The *typology* of trigger shapes we've actually built is [trigger-patterns.md](trigger-patterns.md);
the return-period math and reporting requirements are [return-periods.md](return-periods.md).
Source of record: DS-team practice (maintainer, 2026-07) + the **AA Manual (2024)** — see
[Where this comes from](#where-this-comes-from).

## What a trigger is

A trigger releases **pre-arranged funding, generally automatically**: a pre-agreed condition on a
forecast or observational indicator that, when met, disburses CERF (or other pre-arranged)
financing without a fresh allocation decision. The automation is the point — the negotiation
happens at design time, not at crisis time.

## Vocabulary — say it the way the team says it

- A **trigger mechanism** is the whole system for a framework; it can contain **many specific
  triggers** that do different things — e.g. release different amounts, in different **windows**.
  For rapid onset this is typically staged as a **readiness trigger** (longer lead time, smaller
  release, start mobilising) and an **action trigger** (shorter lead time, main release).
- We say a trigger / a window / a framework is **"activated"** — not "fired".
- **An indicator meeting its threshold does not by itself mean the framework is activated.**
  There can be further requirements: the threshold met in **consecutive months**, laboratory
  confirmation, a convened meeting or no-objection window to confirm the activation, etc. Record
  the *full* activation condition, not just the threshold.

## Hazard onset classes

- **Slow onset** — drought. Seasonal-forecast triggers, windows spread over months.
- **Rapid onset** — cyclones, floods (generally). Short lead times; readiness/action staging.
- **Cholera** — we also do disease outbreaks: observational epidemiological triggers
  (case counts/rates against historical baselines), a family of its own.

The historical-activation bookkeeping differs by class (per the AA Manual): slow onset →
**years or seasons**; continuous rapid onset (flooding) → **dates**; discrete rapid onset
(cyclones) → **specific events**.

## The development process (spec → analysis → report)

Iterative, per the AA Manual:

1. **Trigger spec** — agreed by the working group (with early DS feasibility input): WHAT shock
   (which target return period? which historical events must it catch?), WHEN (lead time needed),
   WHERE (operational presence, vulnerability), and the fund's **risk tolerance** (the
   time-vs-certainty trade-off).
2. **Trigger analysis** — propose a trigger meeting the spec.
3. If it meets the spec, write the **trigger report**; if not, revisit the spec and iterate.

Design principles the Manual anchors on: **lead time** (information at the right time),
**uncertainty** (bound the forecast and financial exposure), **local buy-in** (build on existing
systems where possible), and **scientific robustness** — the forecast must be a good predictor of
the hazard, *and* the hazard a good predictor of impact.

## Validation requirements — every trigger, always

- **Historical analysis is mandatory.** For **each specific trigger** (not just the mechanism as
  a whole), backtest against the historical record and list every past time it would have
  activated — the events/years/dates per its onset class, and from the dates, the **average
  historical lead time** plus an accuracy metric against the target events.
- **Two historical records, not one.** You need both a historical record of **impact** (e.g.
  people affected) *and* of the **observational indicator** (e.g. how much it actually rained) —
  plus the trigger indicator (forecast) itself. Skill has two links: forecast→hazard and
  hazard→impact; validating only one proves nothing about the chain.
- **Always report return periods** — per-trigger *and* combined (overall / effective). The math,
  definitions and where they're published: [return-periods.md](return-periods.md).

## Where this comes from

The **AA Manual (2024)** — internal, on the team Drive under
`CERF Anticipatory Action/General - All AA projects/AA Manual - 2024/` (greppable extracts in
`ds-knowledge-base-internal`; key modules: *Trigger Development*, *Data Sources*, and the
*Trigger Spec* / *Trigger Report* templates). It's older but still the reference for trigger
design and validation. This page carries the public-safe method; open the Manual for the
templates and worked examples.
