---
content_type: method
last_reviewed: "2026-07-07"   # bump when a human verifies the page is still accurate
---

# Return periods — calculation, definitions, reporting

The one number every trigger must carry. How we compute it, the three levels we report, and
where they're published. Companion to [trigger-design.md](trigger-design.md).

## Calculation — Weibull

We generally estimate the return period with the **Weibull** plotting position over the
backtest record:

```
RP = (n_years + 1) / n_activations
```

e.g. a trigger that would have activated 6 times in a 26-year record has RP ≈ (26+1)/6 ≈ 4.5 yr.
The annual activation probability is its reciprocal. Portfolio norm: thresholds are calibrated to
roughly **1-in-3 to 1-in-5 years** (see [trigger-patterns.md](trigger-patterns.md)).

## The three levels — always report all that apply

**We always report the return period of each trigger, and the combined return periods.**
A framework with several specific triggers (windows) has three distinct numbers:

| level | meaning | relation |
|---|---|---|
| **Individual RP** | one specific trigger's own activation frequency | — |
| **Overall RP** | the years in which **at least one** trigger activated | **≤ every individual RP** (by definition — more ways to activate can only be more frequent) |
| **Effective RP** | the return period of **spending the maximum amount in a year** | **≥ the overall RP** (by definition — the max spend requires the most demanding combination) |

So: `overall RP ≤ individual RPs` and `effective RP ≥ overall RP`.

The gap between overall and effective is set by the **funding structure**:

- **all-in** — any activation releases the full envelope → effective RP = overall RP.
- **split** — the envelope is divided across windows, so spending the maximum in one year
  requires *multiple* triggers to activate that year → effective RP > overall RP (often much
  greater).

Interpretation guide: the **overall RP** answers "how often does this framework do *something*";
the **effective RP** answers "how often does the fund face the *maximum* bill". A donor sizing a
pre-arranged envelope needs both.

## Where they live

- **Framework pages** — each version's *Trigger windows* table carries per-window RPs;
  `trigger_facets` records the calibration.
- **The `aa` DB** — per-window `return_period` / `rp_reported` and per-framework
  `overall_return_period` / `overall_rp_reported` (reported values from the framework PDF win
  over derived ones).
- **The public trigger-statistics page**
  ([anticipatory-action/stats](https://ocha-dap.github.io/ds-knowledge-base/anticipatory-action/stats.html),
  regenerated daily from the DB) — per-trigger RPs, the per-framework **Overall RP** with its
  annual probability, the all-in/split funding column, and the backtested activation years each
  RP is derived from.

## Gotchas

- **Reported vs derived**: when the published framework PDF states an RP, that's the reported
  number; a backtest can disagree (record the conflict on the framework page, don't silently
  substitute).
- **Short records**: a 7-year reforecast archive cannot support a confident 1-in-5 claim — say
  so (see e.g. nga-flooding's reforecast-length discrepancy).
- **RP of the trigger ≠ RP of the hazard**: the trigger's activation frequency is a property of
  the indicator + threshold; validate separately that activation years line up with impact years
  ([trigger-design.md](trigger-design.md) — two historical records).
