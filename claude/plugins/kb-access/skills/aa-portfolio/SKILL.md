---
name: aa-portfolio
description: Answer questions about OCHA's anticipatory action (AA) portfolio — which frameworks exist and their status, versions, triggers, pre-arranged funding, co-financing, activations, money released, people reached — from the AA tracker (ds-aa-tracking), the single authoritative AA record. Use it instead of the KB's frameworks/ pages or catalog.md for any current AA fact or total; those are a frozen copy.
---

# AA portfolio questions → the AA tracker

**The AA tracker is the authoritative AA record** (KB D115, D124, D125). The KB's
`frameworks/` pages and `catalog.md` are a copy frozen on 2026-09-28: use them for a
framework's design write-up and links to its analysis code, never for current status,
versions, funding or activations, and **never add up their funding columns**. Summing them
on 2026-11-06 gave "30 active, $82.5M CERF"; the tracker said 17 active (29 on the map) and
$158.7M CERF.

## Where to read it, in this order

1. **The `aa_*` MCP tools**, if connected: on the `ds-knowledge-base` connector (KB MCP,
   either tier), or on their own at `https://chd-ds-kb-mcp.azurewebsites.net/aa-tracker/mcp`.
   - `aa_overview()` first: the map's headline figures and the counting rules.
   - `aa_framework(country_iso3, hazard)`: one framework (versions, trigger tables,
     windows and backtests, activations, funding, partners).
   - `aa_data(file, country_iso3=, hazard=, year=, layer=)`: rows of frameworks, versions,
     activations, prearranged-funding, cofinancing or funds.
   - `aa_guide(section)`: field meanings and vocabulary.
2. **No MCP:** read the open files directly. They are published for programs and AI
   assistants, need no password, and are rebuilt nightly:
   - `https://ocha-dap.github.io/ds-aa-tracking/llms.txt`: the counting rules and the
     list of files, column by column. Read it before totalling anything.
   - `…/aa-map.md`: the headline figures as the map shows them.
   - `…/aa-frameworks|aa-versions|aa-activations|aa-prearranged-funding|aa-cofinancing|aa-funds`
     `.json` / `.csv`, and `…/aa-map-data.json` (every framework's panel).
3. **Detail the open files don't carry:** the tracker's other pages are still behind a
   password, but their data is in the dev `aa` schema. Reach it through ocha-stratus (the
   `blob-io` skill) or the internal KB MCP's `run_sql(stage="dev")`. The KB page
   `pipelines/aa-tracking.md` § *Answering portfolio questions* maps questions to views.
   Headline figures still come from the open files: the map's totals are computed in the
   site build, so raw SQL sums don't match them.

## Counting rules (the short form; `llms.txt` is the source)

- Pre-arranged funding is a **stock** per framework and year: never sum it across years,
  never add it to released money.
- Some tropical-cyclone frameworks allow two activations a year, and their CERF envelope is
  **already counted twice**: never multiply again.
- **Co-financing** is a separate stock from outside the OCHA-managed funds: never add it to
  pre-arranged.
- A framework is one **(country, hazard)** pair: there are no regional frameworks. Count
  frameworks by `lifecycle` (active, updating, development, pipeline, retired), not by
  version `status`.
- Every figure depends on the map **layer** (current frameworks, retired,
  non-framework): say which layers a total includes.

## Reporting

- Cite the **data snapshot time** each answer carries, and link the map
  (`https://ocha-dap.github.io/ds-aa-tracking/`).
- The tracker calls itself under development ("the figures may be incorrect"). Say so
  whenever figures leave the team.
- **Corrections and new frameworks or versions go into the tracker** (its entry page or an
  entries file), never into the KB's `frameworks/` (D124).
