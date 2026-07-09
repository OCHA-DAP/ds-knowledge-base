---
content_type: method
last_reviewed: "2026-07-08"   # bump when a human verifies the page is still accurate
---

# Static data apps — pre-baked JSON on GH Pages (or SWA)

Ship interactive data apps as **static JS + JSON exported from the DB at deploy time**, instead
of a Python server (marimo/Streamlit/Dash on App Service). No runtime, no creds anywhere near
the client, every interaction instant (all client-side), and hosting is free on GitHub's CDN.
Reference implementation: `ds-storm-impact-harmonisation` (`app/`, `export_app_data.py`,
`.github/workflows/deploy-app.yml`), live at
<https://ocha-dap.github.io/ds-storm-impact-harmonisation/compare/> — see
[apps/storm-exposure-compare](../apps/storm-exposure-compare.md).

## When to use

- The app reads **aggregate/tabular data** (admin-level stats, timeseries) that fits in tens of
  MB as JSON — not live rasters or per-request DB queries.
- The data is **non-sensitive** (it will be world-readable).
- Freshness of "updated on a schedule" is acceptable (cron redeploys; hourly is fine in-season).

Stay on App Service when you need live DB queries, gated access without SWA, or heavy
server-side computation. (Python-in-the-browser via WASM/pyodide does **not** change the
calculus: still client-side, so still no secrets, no Postgres sockets, plus a 30–60 MB runtime.)

## Architecture — three pieces

1. **Export script** (Python, runs in CI only): queries Postgres via `ocha-stratus`, does the
   joins once, writes JSON under `app/data/` (gitignored — data never enters git).
   Structure the output for lazy loading: one `core.json` loaded upfront (everything needed for
   the main interactions; keep it a few MB), plus per-entity files (`tracks/{iso3}.json`,
   `buffers/{storm}.json`) fetched on demand and cached client-side. Simplify geometries in
   PostGIS (`ST_SimplifyPreserveTopology` + `ST_AsGeoJSON(…, 2)`), and `dropna` key columns —
   `NaN` is invalid JSON.
2. **Static app**: plain `index.html` + `app.js` + `style.css`. Hand-rolled SVG charts (full
   control of axes/reflines; native `<input type=range>` gives live update-on-drag, which
   Streamlit sliders cannot do) and Leaflet from CDN for maps. Style per the team
   [style guide](style-guide.md) (HDX v2 design system).
3. **Deploy workflow** (GH Actions, Pages "workflow mode"): on schedule + `workflow_dispatch` +
   push-to-main touching `app/**`. Runs the export with **org-level `DSCI_AZ_DB_*` read
   secrets**, assembles the site, `actions/upload-pages-artifact` -> `actions/deploy-pages`.
   The artifact never touches git, deploys are atomic (a failed run leaves the old site up),
   and caching the export (`actions/cache`, key by run id + `restore-keys` prefix) makes
   app-only deploys ~20 s: refresh only on schedule, on opt-in dispatch input, or on cache miss.

## Gotchas (all hit in the reference implementation)

- One Pages site per repo. If the repo already serves one (check
  `gh api repos/OCHA-DAP/<repo>/pages`), bundle both into the artifact (existing site at root,
  new app under a subpath) rather than clobbering it.
- Switching Pages to workflow mode is a repo-settings change:
  `gh api -X PUT repos/…/pages -f build_type=workflow`.
- The `github-pages` **environment branch policy** may only allow old branches — add `main`
  (and any test branch) or deploys fail instantly.
- `workflow_dispatch`/`schedule` only register once the workflow is on the default branch;
  pre-merge testing needs a temporary `push:` trigger on the feature branch.
- Repo-level secrets **shadow** same-named org secrets — don't create empty repo ones.
- Limits: 1 GB site, ~100 GB/month bandwidth (soft). Browser only downloads core.json + what's
  clicked, so published size ≠ per-visit transfer.

## Azure Static Web Apps variant

Same architecture, swap the last workflow steps for `Azure/static-web-apps-deploy` (deployment
token as secret). Choose SWA when you need **Entra ID auth** (Standard tier gates the whole
site behind org logins — Pages on public repos can't) or **managed functions** (`/api/*` with
DB creds server-side = the hybrid for live/gated data, no CORS). Limits: 250 MB app (Free) /
500 MB (Standard). Note team storage accounts have `allowBlobPublicAccess=False`, so
"public blob container" is not an alternative for the data.
