---
content_type: method
last_reviewed: "2026-08-07"
---

# Absent data must not render as a benign value

A rule for anything we build that displays someone else's severity, needs or impact
data. It exists because we broke it, on a live product, in the most consequential way
available: **most of Sudan rendered as IPC Phase 1, "Minimal"**, in August 2026 — a
country with famine confirmed in El Fasher and Kadugli.

Nothing was corrupt. Every number was faithfully mirrored. The failure was entirely in
how absence was interpreted on the way to the screen.

## The failure mode

Classification rules are usually written as a search for a threshold:

```python
# IPC area rule: highest phase reaching >=20% of the analysed population
cum = 0
for phase in (5, 4, 3, 2, 1):
    cum += pop[phase]
    if cum / analysed >= 0.20:
        return phase
return 1          # <-- the bug: "found nothing" silently means "Phase 1"
```

When an area is genuinely *not assessed*, `pop[phase]` is all zeros, the loop finds
nothing, and the function returns the **mildest category it has**. Absence and safety
become indistinguishable, and the error is always in the reassuring direction.

The same shape appears well beyond IPC:

| pattern | absent renders as |
|---|---|
| `return 1` / `return 0` after a failed threshold search | lowest severity |
| `.get(key, 0)` on a caseload or exposure count | nobody affected |
| `fillna(0)` before a sum or a share | zero need |
| `COALESCE(x, 0)` in a severity or impact query | no impact |
| a colour ramp with no "no data" entry | the lightest colour on the ramp |

## The rules

1. **Distinguish "no data" from the lowest value, at every layer** — the classifier, the
   aggregate, the colour scale, and the legend. If a function can return a category, it
   must be able to return *nothing*.
2. **Test emptiness before classifying**, not after. `sum(parts) > 0` is usually the whole
   fix.
3. **Give "not assessed" a swatch.** An unlabelled grey reads as "nothing happening here"
   rather than "outside this analysis". Ours now says `not assessed` in the legend.
4. **Never blend vintages in one view.** If a source publishes several analysis periods,
   pick one for the whole country and blank what it does not cover — the way the source
   itself presents it. Choosing the "best available" period *per unit* looks helpful and
   produces a map no reader can interpret: a real product put four different analysis
   periods on one Sudan map under a single title, and 14 of 39 countries mixed at least
   two.
5. **Say which vintage is on screen**, in the control and in the chart title, and carry it
   in the URL so a shared link means one thing.
6. **If the honest default is sparse, make the fuller alternatives reachable.** Sudan's
   current-period map legitimately shows 49 of 189 units; Afghanistan's, 9 of 401. That is
   correct, but a default with no escape hatch is its own kind of dead end — list every
   published period, with the number of units each one classifies.

## How to catch it

Aggregate checks will not find this. A national total can be right while every unit is
wrong, and a country rendered entirely Phase 1 still sums to a plausible number if the
denominator is also wrong.

- **Check against the source's own published figures and its own map**, per period, not
  just the national headline. Ours matched IPC on totals while the map was badly wrong.
- **Look at the rendered product.** The Sudan bug was invisible in every dataframe we
  inspected and obvious the moment we compared our map with ipcinfo.org's side by side.
- **Count what you are *not* drawing.** "How many units did this view decline to
  classify, and why?" is a question worth answering out loud in the methodology.
- Ratios that land on suspiciously round numbers (an exact `2.00×`) are a duplication
  tell, not a coincidence.

## The same rule applies to your verification

A coverage check that counts what is *present* cannot see what is missing, so it will
happily confirm a product that is quietly broken.

Not hypothetical. While building the Forecast × HNRP tab we ran exactly such a check:

```
2026 per-country: units with PiN
  Afghanistan 401 · Colombia 1122 · Sudan 188 · Yemen 333 · …    (16 countries)
```

and read it as "2026 coverage is good". The question never asked was **which of the 50
countries in the selector are absent from that 16, and what do they look like on
screen?** Myanmar was one. It drew 330 areas on the map beside an empty bar chart, and
shipped that way until someone picked it from the dropdown. Venezuela, Burkina Faso and
three others were in the same state, unnoticed for the same reason.

- **Enumerate the entities a user can select, not the rows you happen to have.** Loop
  over every country × mode × cycle and assert each renders something.
- **Mirror the product's own filter, not the data's shape.** The chart keyed on the
  needs analysis while the payload carried monitoring; a check written against the
  payload passes while the chart is empty.
- **Declare expected gaps explicitly, with a reason and a scope.** 27 countries have no
  HNRP at all; Guatemala has no 2026 workbook. Those belong in an allowlist keyed by
  `(country, cycle)`, so a *new* gap fails and today's exemption cannot silently cover
  next year.
- **Exit non-zero.** A build that reintroduces a gap should fail, not print into a log
  nobody reads.

Worked example:
[`pipeline/audit_site_coverage.py`](https://github.com/OCHA-DAP/ds-seas5-skill/blob/main/pipeline/audit_site_coverage.py).
Its first run found five more countries in the condition the reported one was in.

## A total you derived is not the total they published

The sibling failure: not absence rendering as zero, but a PARTIAL sum rendering
as a complete total.

Subnational rows in a humanitarian plan are an *attribution* of a national
caseload to areas, and that attribution is routinely incomplete. Summing them
gives a floor, not the figure — and the figure is what a reader will check you
against. On the Forecast × HNRP tab, every one of 20 countries came out short:

| country | summed from areas | published |
|---|---|---|
| Burkina Faso PiN | 3,560,047 | **4,474,321** |
| Chad PiN | 3,444,745 | **4,509,014** |
| DR Congo target | 7,092,871 | **10,735,805** |
| Ukraine / Syria / Venezuela | 0 | **full caseload** |

Chad's shortfall is not recoverable by better p-code work: the source itself
attributes 24% of its PiN to no area. Ukraine attributes none of anything —
so a country card built by summing showed nothing at all for a plan with a
published 10.8M PiN.

- **Mirror the publisher's own total; do not reconstruct it.** If the source
  prints a national figure, that is the national figure. Storing it costs one
  small table and removes a whole class of disagreement.
- **Reconcile the two, and say which is which.** Ours splits the gap into
  `published -> attributed by the source -> placed by us`. Only the last arrow
  is a defect; the first is a property of the source and belongs in the caption,
  not in a bug tracker.
- **Assert the published total exactly, with no tolerance,** and budget the
  placement gap separately. Conflating them lets a real regression hide inside
  an allowance made for the source's own reporting.
- **Never let a complete-looking total sit above an incomplete map in silence.**
  Ukraine's card was correct and its map empty; the fix was a sentence saying
  the plan reports no subnational breakdown. This is the absent-data rule again:
  the reader must be able to tell "nothing here" from "nothing reported here".
- **Rolling a unit up is only safe when it cannot double count.** Mogadishu's
  Daynile and Kahda fold onto Banadir because our vintage holds Banadir whole
  and the source publishes no other Banadir row. Haiti's ZMPP does not fold
  anywhere: it is a metro planning zone overlapping ten communes already drawn.

## Where this has bitten

- [infrastructure/datasets/ipc.md](../infrastructure/datasets/ipc.md) — the four concrete
  `population_admin` traps (partial projection coverage, missing phases, near-duplicate
  rows, national-only newest analyses).
- [apps/seas5-skill.md](../apps/seas5-skill.md) — the Forecast × HNRP tab, where all of
  this was found and fixed (OCHA-DAP/ds-seas5-skill #43–#46).
- [OCHA-DAP/ds-ipc-mirror#1](https://github.com/OCHA-DAP/ds-ipc-mirror/issues/1) — the
  duplicate-row defect filed upstream, with the reproduction query.
