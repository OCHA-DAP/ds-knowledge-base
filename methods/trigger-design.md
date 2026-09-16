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

## Choosing the area a threshold is calibrated on

The unit a threshold is calibrated on — one national value, one per basin, one per district,
one per pixel — is a **design choice**, and all of them are used. A mechanism keyed to a single
river reach or a single lake has one threshold and needs no more. A national indicator can
carry a national threshold. The question is only whether the areas a trigger spans are similar
enough that one number means the same thing in each of them.

Where they are not, the usual move is to calibrate **per area, as a percentile or return period
of that area's own record**, so the trigger carries the same *rarity* everywhere while the
absolute values differ. Terrain, catchment size, rain climatology and a sensor's footprint all
change what an extreme value looks like locally, so different districts activating at different
absolute values is the expected outcome rather than an inconsistency to tidy away.

A few things worth keeping in mind whichever unit you pick:

- **Match the diagnostic to the threshold.** This is where it usually goes wrong. If the
  threshold would be relative to each area, then judge whether an indicator works there on
  relative evidence too — does the indicator sit high in *that area's own* record when
  something happened (share of events reaching its own 80th percentile, against the 20 %
  chance baseline), does it separate impact years from quiet ones (AUC). Judging an area by
  its absolute magnitude, when the threshold would have been a local percentile, compares the
  wrong things.
- **Small absolute values are not disqualifying on their own.** An area where a flood product
  only ever reaches 0.5 % extent can still be usable, if those small peaks land on the days
  people actually flooded. The things that do disqualify it are no relationship with the
  hazard record, or a series so flat there is no distribution left to take a percentile of.
- **A biased model can still be fine.** Derive the threshold from the model's own reforecast
  climatology — "model space" — rather than from observed values. Bias moves the *number*, not
  the *decision*. Correlation and forecast skill are the better guides to whether a point is
  usable; Kling-Gupta efficiency is dominated by bias and variance ratio and can reject points
  that would work.
- **Tie handling matters when a series has many zeros.** "Share of days strictly below" scores
  every zero day as percentile 0 even where zero is the modal value; midrank avoids that.
- **An absolute floor is usually a noise floor, not a threshold** — e.g. FloodScan SFED ≥ 0.05
  to suppress speckle before anything is computed. Worth saying which you mean.

*Worked example of the mismatch above:* the Uganda flood work initially judged districts on a
2-year flood extent under 1 %, calling them "blind", while the threshold itself would have been
a per-district percentile — which wrote off districts across Mount Elgon and Karamoja whose
relative signal was fine. Corrected in `ocha-dap/ds-aa-uga-flooding`
(`analysis/floodscan_vs_impact.py`); the same repo's backstop and exposure analyses were
unaffected because they had used per-district return periods throughout.

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
