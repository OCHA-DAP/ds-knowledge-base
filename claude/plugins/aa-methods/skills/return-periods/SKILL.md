---
name: return-periods
description: Compute and report AA trigger return periods the team's way — Weibull plotting position, the three levels (individual, overall, effective) and their inequalities, all-in vs split funding. Use whenever calculating, reporting, or sanity-checking a return period or annual activation probability.
---

# Return periods — the one number every trigger must carry

Full method + where the numbers get published: KB `methods/return-periods.md`.

## Calculation

Weibull plotting position over the backtest record:

```
RP = (n_years + 1) / n_activations
```

(6 activations in 26 years → RP ≈ 4.5 yr; annual probability is the reciprocal.)
Portfolio norm: thresholds calibrated to roughly **1-in-3 to 1-in-5 years**.

## The three levels — report all that apply

| level | meaning | relation |
|---|---|---|
| **Individual** | one specific trigger's frequency | — |
| **Overall** | years where **at least one** trigger activated | **≤ every individual RP** |
| **Effective** | RP of spending the **maximum** in a year | **≥ overall RP** |

If a computed set violates `overall ≤ individual` or `effective ≥ overall`,
something is wrong — stop and check.

The overall↔effective gap is the **funding structure**: **all-in** (any activation
releases everything) → effective = overall; **split** (envelope divided across
windows) → effective > overall. Staged rapid-onset frameworks are generally **not**
all-in (readiness releases ~5%), so they behave as split.

## Gotchas

- **Reported vs derived**: an RP stated in the published framework PDF is the
  reported number; if a backtest disagrees, record the conflict — never silently
  substitute.
- **Short records**: a 7-year reforecast archive cannot support a confident 1-in-5
  claim — say so explicitly.
- **Trigger RP ≠ hazard RP**: activation frequency is a property of
  indicator + threshold; separately validate that activation years line up with
  impact years (see `trigger-design`).
