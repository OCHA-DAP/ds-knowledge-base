---
name: data-conventions
description: The team's opinionated defaults for writing data code in OCHA CHD DS repos — Python tooling (uv, ruff), processing-library preferences (ocha-lens), geo stack. Use when writing or reviewing data-loading, processing, or analysis code in a team repo. Advisory — the repo's own conventions always win.
---

# Team data conventions (opinionated house style)

**Advisory, not law** (last reviewed 2026-07): these are the team's defaults. The
repo you're in wins — check its CLAUDE.md and existing code first, and don't retrofit
a deliberately-divergent project. If a default here has drifted from practice, say so
and open an issue on `OCHA-DAP/ds-knowledge-base`.

(For *access* to team data — stratus, blob naming, `valid_time` semantics, third-party
loaders — see the `data-access` plugin; those are facts, not style.)

**Every item below carries its reason.** That is the test for belonging here: a default
whose only justification is "that's how we did it" is habit, not a convention, and gets
cut at the next review rather than inherited by the next repo (D93).

## Processing

- **Try `ocha-lens` before writing custom processing** — it already covers the team's
  recurring shapes, and a bespoke reimplementation is one more thing to keep correct.
  → KB `infrastructure/libs/ocha-lens.md`
- Geo stack: `xarray` for gridded, `geopandas` for vector, `rioxarray` for raster I/O
  and clipping — the stack these libraries' own ecosystems assume, so going off-piste
  costs interoperability rather than buying anything.

## Python

- **3.11+**, and **`uv`, not pip** — real lockfiles, and fast enough that a clean
  environment is never the reason to skip one.
- **Type hints on signatures** — with less code read by a human, annotations are what
  let tooling do the checking instead. They earn their keep at boundaries (what goes
  in, what comes out); interior locals rarely need them.
- **Never silently suppress exceptions** — a swallowed error in a pipeline resurfaces
  as a quietly wrong number weeks later. Ruff catches the crude forms (bare `except`,
  `try/except/pass`); catching a specific exception and continuing without saying so is
  a judgement call it can't see, so that one is on you.

Formatting and lint rules are deliberately **not** prose here — they live in one shared
config so they are enforced rather than remembered. → KB `infrastructure/python-tooling.md`

## Interactive surfaces

Default to **generated static output** over a served app. The decision rule, the
escalation triggers (auth, live DB reads, data size, user-driven compute) and the
hosting modalities live on one page → KB `methods/static-data-apps.md`

No default framework is named here on purpose. Dash/Streamlit/marimo largely existed to
spare humans from writing HTML and JS — the labour that got cheap — so naming a
successor before there is a real case to test it against is how the last set of
defaults turned into habit.
