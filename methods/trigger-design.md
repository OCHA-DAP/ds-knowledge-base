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
  For rapid onset this is typically staged as a **readiness trigger** (longer lead time, start
  mobilising) and an **action trigger** (shorter lead time, main release).
  - **What a readiness trigger actually releases.** A readiness activation does **not** authorize
    spending the whole envelope — typically only a small fraction (~5%), for mobilisation/readiness
    activities. The bulk (~95%, sometimes 100%) is authorized only when the **action** or an
    **observational** trigger is subsequently met. Technically the readiness trigger usually
    transfers the *whole* budget to the agencies up front, but obliges them to **return the unspent
    remainder** (~95%) if no action/observational trigger follows. Because of this, rapid-onset
    frameworks are generally **not** ["all-in"](return-periods.md) (see there).
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
   time-vs-certainty trade-off). The **Trigger Specification Form** (template on the team Drive)
   is filled in collaboratively with the working group **after the framework is approved but
   before any significant technical work**, then circulated so everyone agrees on what the
   trigger will target.
2. **Trigger analysis** — propose a trigger meeting the spec.
3. If it meets the spec, write the **trigger report**; if not, revisit the spec and iterate.
   **CERF requires a standard reporting table of trigger statistics in every framework
   document's Executive Summary** — a dedicated spreadsheet (team Drive) generates these tables.

**Portfolio bookkeeping.** The **Framework Development Tracker** (a sheet on the team Drive) is
the master list of AA frameworks; update it at three milestones — **approved for development**,
**endorsed**, and **triggered**. The public
[CHD AA webpage](https://centre.humdata.org/anticipatory-action/) is driven by another team-Drive
sheet and updates near-instantly when that sheet is edited.
Digested from the retired DSCI Confluence space (archive: `confluence/` in
`ds-knowledge-base-internal`).

Design principles the Manual anchors on: **lead time** (information at the right time),
**uncertainty** (bound the forecast and financial exposure), **local buy-in** (build on existing
systems where possible), and **scientific robustness** — the forecast must be a good predictor of
the hazard, *and* the hazard a good predictor of impact.

## Thresholds are normalised per area, never shared absolutes

A threshold belongs to the area it governs. Calibrate it **per district, per basin, per
pixel — whatever unit the trigger acts on** — as a percentile or return period of *that
unit's own* record. Two districts in the same zone will legitimately activate at different
absolute values, and that is correct, not a bug to be tidied away.

This follows from what a trigger is for: we want the same **rarity** everywhere (a 1-in-3-year
flood for this district, a 1-in-3-year flood for that one), not the same millimetres or the
same flood fraction. Terrain, catchment size, rain climatology and the sensor's own footprint
all change what an extreme value looks like locally.

The practical consequences:

- **Never gate an area out because its absolute values are small.** A district where a flood
  product only ever reaches 0.5 % extent is perfectly usable if those small peaks land on the
  days people actually flooded. What disqualifies an area is *no relationship* with the
  hazard record, or a series so flat there is no distribution left to take a percentile of.
- **Judge usability on rank-based evidence**: does the indicator sit high in that area's own
  record when something happened (share of events reaching its own 80th percentile, against
  the 20 % chance baseline); does it separate impact years from quiet ones (AUC). Both are
  invariant to the units and the local magnitude — which is the point.
- **Set model-space thresholds against biased models.** A hydrological model running 1.7×
  wet is fine: derive the threshold from the model's own reforecast climatology, not from
  observed discharge. Bias matters to the *number*, not to the *decision*. Correlation and
  forecast skill are what decide whether a point is usable; Kling-Gupta efficiency is
  dominated by bias and variance ratio and will reject perfectly usable points.
- **Watch tie handling when the series has many zeros.** "Share of days strictly below" scores
  every zero day as percentile 0 even where zero is the modal value; use midrank.

Where an absolute floor *is* appropriate, it is a noise floor, not a trigger threshold — e.g.
FloodScan SFED ≥ 0.05 to suppress speckle before computing anything. Say which you mean.

**Worked example of getting this wrong:** the Uganda flood work initially gated districts on
a 2-year flood extent under 1 %, calling them "blind", and wrote off districts across Mount
Elgon and Karamoja whose *relative* signal was fine. Corrected in
`ocha-dap/ds-aa-uga-flooding` (`analysis/floodscan_vs_impact.py`); the same repo's
backstop and exposure analyses were unaffected because they had used Weibull return periods
per district from the start.

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
