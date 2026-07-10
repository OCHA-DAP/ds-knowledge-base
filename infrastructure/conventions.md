---
content_type: infrastructure
last_reviewed: "2026-06-15"   # bump when a human verifies the page is still accurate
---

# Data conventions

Team-wide conventions that hold regardless of project. Seeded from the team's global Claude config; this is now the shared home for them. The working-practice sections further down (git/PR workflow, notebooks, language choice, results-sharing, repo hygiene) are digested from the team's 2024 coding guidelines — they predate some newer tooling, and where they conflict with the tooling conventions on this page (e.g. `uv`), **this page's conventions win**.

## Naming / time

- **`valid_time`** (or `valid_date`) — the valid time of a forecast, i.e. what it's a forecast *for*. Also called reference time or just "time". Use this for observational data too.
- **`issued_time`** — the issue/publication time of a forecast.
- **Leadtime convention:** `issued_time + leadtime = valid_time`. A forecast issued in March with leadtime 1 month is valid for April.

## Spatial

- **CRS is always EPSG:4326** unless explicitly noted.
- `xarray` for gridded data, `geopandas` for vector, `rioxarray` for raster I/O and clipping.

## Admin boundaries (CODABs)

- Prefer an existing repo function to load the CODAB from blob. Otherwise load from **FieldMaps via `ocha-stratus`**.
- For metadata only (admin name, code, total area), use the DB `public.polygons` table via `ocha-stratus` — available for certain countries only.

## Python

- Python 3.11+. `uv` for env management, not pip directly.
- Type hints on all signatures. f-strings. Don't suppress exceptions silently.

## Libraries to reach for first

- **`ocha-stratus`** — all blob & DB access. See [database.md](database.md) / [storage.md](storage.md).
- **`ocha-lens`** — common data processing; check it before writing custom logic.
- **`ocha-relay`** — comms (Listmonk email). See [comms-listmonk.md](comms-listmonk.md).

**Deprecated — don't use for new work:**

- **`ocha-anticipy`** — superseded; **not used for new frameworks**. Still relevant when reading/maintaining older frameworks that imported it, so worth recognising, but reach for `ocha-stratus`/`ocha-lens` instead.

## Language choice

- **Python is favoured for automated scripts**, with flexibility to use another language where it clearly fits better.
- **Keep the language consistent within a project** — if it started in Python, continue in Python.
- If a specific challenging task is much easier in another tool, fine — but **avoid tools nobody else on the team knows**.

## R

For the occasional R project:

- Document functions with **roxygen**.
- Follow the **Tidyverse** style guide.
- Format with **styler**; lint with **lintr**.

## Git / PR workflow

- Work on a **feature branch**: lowercase, hyphen-separated, name describes the functionality (e.g. `new-branch`).
- **Small, discrete commits** with **present-tense imperative** messages (e.g. *Update folder structure*).
- Open a **PR to `main`** when done; **every PR is reviewed by someone else** before merge.

## Notebooks vs scripts

- **One-off analyses** may live in notebooks, with descriptive text accompanying each step.
- Keep notebooks clean by **importing heavy functions from separate `.py` files**.
- **Repeated analyses belong in scripts** runnable from the command line — not notebooks.
- **Commit notebooks as markdown** (via `jupytext`), not `.ipynb`, so diffs are reviewable on GitHub.

## Sharing results

- **Another team member reviews** results before anything goes external.
- Document **technical limitations and disclaimers**, and the **significance/potential impact** — don't assume the figures speak for themselves.
- Tailor documentation and communications to the **audience's technical literacy**.

## Repo hygiene checklist

Before considering a repo in good shape:

- **README** is up to date and covers: the repo's **purpose**; the **entry point** (where to start to rerun the analysis / run the pipeline); required **environment variables**; and steps to **create the environment and install dependencies**.
- **Stale branches** merged into `main` or deleted.
- **Unused files** cleaned up, or moved to an `archive/` directory.
- Every notebook has at least a **title and a 1–2 sentence summary** of what it accomplishes.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).
