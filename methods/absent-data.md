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

## Where this has bitten

- [infrastructure/datasets/ipc.md](../infrastructure/datasets/ipc.md) — the four concrete
  `population_admin` traps (partial projection coverage, missing phases, near-duplicate
  rows, national-only newest analyses).
- [apps/seas5-skill.md](../apps/seas5-skill.md) — the Forecast × HNRP tab, where all of
  this was found and fixed (OCHA-DAP/ds-seas5-skill #43–#46).
- [OCHA-DAP/ds-ipc-mirror#1](https://github.com/OCHA-DAP/ds-ipc-mirror/issues/1) — the
  duplicate-row defect filed upstream, with the reproduction query.
