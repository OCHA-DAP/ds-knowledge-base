# OCHA CHD Data Science — team config

<!-- Single source of the team's always-loaded Claude config (supersedes ds-claude-config).
     Loaded into every session via the @import that scripts/setup_team_claude.sh adds to
     ~/.claude/CLAUDE.md; the session-start hook keeps the clone — and so this file — on
     current main. Change via PR. CI (scripts/check_claude_assets.py) enforces a token
     budget: link to KB pages rather than inlining detail. -->

## Team knowledge base

This file sits in the `claude/` dir of your `ds-knowledge-base` clone — the team KB (hub),
organized as `frameworks/`, `pipelines/`, `apps/`, `analysis/`, `methods/`,
`infrastructure/`, `assets/`.

- **Search the KB first** for team questions (frameworks/triggers, what feeds a pipeline,
  blob/DB conventions, past decisions) — grep/read it rather than answering from memory.
  Follow each page's `code_ref`/`source_repo` into the actual repo for depth. Internal
  material (Drive extracts, style-reference mirror) is in the sibling
  `ds-knowledge-base-internal` clone.
- **Capture-as-you-go**: after real framework/pipeline work, update the affected KB page.
- To change the KB: open an issue on OCHA-DAP/ds-knowledge-base — the steward drafts it as
  a PR. If a lookup finds nothing or something stale, leave a `<!-- TODO -->` stub.
- If `.kb-sync-stuck` exists at the KB clone root, auto-update is failing on this machine —
  tell the user (fix: commit/stash local changes in the clone, `git pull --ff-only`, delete
  the marker; or re-run the setup script — see the KB's `docs/USING.md`).

## Team skills

`ds-team:*` skills ship from this repo (`claude/skills/`). Use **ds-team:blob-io** whenever
loading/saving blob or DB data, and **ds-team:hdx-brand** before styling anything
(charts, apps, reports). **ds-team:kb-doctor** checks this machine's KB setup.

## Data conventions (always apply)

- `ocha-stratus` for ALL blob + Postgres access — never raw Azure SDK or psycopg2.
  Rasters live in blob; per-admin raster stats in the DB (ERA5, SEAS5, IMERG, Floodscan).
  → `infrastructure/libs/ocha-stratus.md`
- Blob paths: `{PROJECT_PREFIX}/{raw|processed}/{datasource}/{filename}`;
  `PROJECT_PREFIX` comes from `src.constants`, never hardcoded.
- Try `ocha-lens` before writing custom processing. → `infrastructure/libs/ocha-lens.md`
- `valid_time` for observation/forecast validity, `issued_time` for publication;
  issued month + leadtime = valid month.
- CRS is EPSG:4326 unless noted; `xarray` for gridded, `geopandas` for vector,
  `rioxarray` for raster I/O and clipping.
- CODAB boundaries: use the repo's loader if present, else FieldMaps via stratus;
  name/code-only metadata from DB `public.polygons` (limited countries).

## Python

Python 3.11+ · `uv` (not pip) · type hints on signatures · f-strings · never silently
suppress exceptions. Typical layout: `src/constants.py` (PROJECT_PREFIX),
`src/datasources/`, `src/utils/` — a guide, not a rule; check the repo first.

## Marimo

Bare expression on the cell's last line to display (`_fig`, not `return _fig`);
`_`-prefix cell-local variables; `print()` is invisible in `marimo run` — use
`mo.md(...)`, `mo.ui.table(df)`, or bare expressions.
