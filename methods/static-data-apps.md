---
content_type: method
last_reviewed: "2026-07-16"   # bump when a human verifies the page is still accurate
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

Stay on App Service when you need live DB queries, **gated (org-login) access**, or heavy
server-side computation — and note a *static* site that needs org-login gating also goes to
App Service, not SWA (we can't self-create SWA resources; see
[the App Service Plan workaround below](#when-you-need-org-login-gating-deploy-into-the-app-service-plan-not-a-new-swa)).
(Python-in-the-browser via WASM/pyodide does **not** change the
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

## When you need org-login gating: deploy into the App Service Plan (not a new SWA)

Reach past GitHub Pages when you need **Entra ID auth** (gate the whole site behind UN-tenant
logins — Pages on public repos can't) or **server-side secrets** (live DB queries without
exposing creds to the browser).

**The catch, and the workaround (confirmed 2026-07):** IT does not grant us rights to create
new Azure **resources**, and **each Azure Static Web App is its own resource** — so
`az staticwebapp create` fails with `AuthorizationFailed` for the DS team's `Website
Contributor` role (it lacks `Microsoft.Web/staticSites/write`). SWA is therefore **not a path
we can self-serve.** What we *can* do: the **App Service Plan is a single, already-blessed
resource**, and `Website Contributor` lets us create web-app **deployments inside it**. So to
host a static site or a gated app, **create an `az webapp` on the existing plan** rather than
a new SWA. (This is why the ds-geospatial-impact-estimates viewer runs on App Service, not its
vestigial SWA resource.)

Plans in RG `IMB-CHD-DataScience-EastUS2`: **`DsciAppServicePlan`** (P0v3 Linux, prod) /
**`DsciAppServicePlan-Dev`** (B2). Recipe for a **static site** (e.g. a rendered Quarto book):

```bash
RG=IMB-CHD-DataScience-EastUS2; APP=chd-<repo>
az webapp create -n $APP -g $RG -p DsciAppServicePlan --runtime "NODE:22-lts"
az webapp config appsettings set -n $APP -g $RG --settings SCM_DO_BUILD_DURING_DEPLOYMENT=false
az webapp config set -n $APP -g $RG --startup-file "pm2 serve /home/site/wwwroot --no-daemon --spa"
# deploy a zip of the built site's CONTENTS (index.html at the zip root -> wwwroot)
az webapp deploy -n $APP -g $RG --type zip --src-path site.zip
```

Repeat deploys via GitHub Actions `azure/webapps-deploy@v3` with the web app's **publish
profile** as a repo secret (no resource creation, no deployment token) — reference workflow
`ds-geospatial-impact-estimates/.github/workflows/azure-deploy.yml` (builds once → staging slot
→ reviewer-gated production slot). For a **dynamic app** (marimo/Dash/FastAPI) the same plan
hosts it with a gunicorn/uvicorn startup command; most `chd-*` apps in
[deployments.md](../infrastructure/deployments.md) are exactly this.

**Making it internal — Entra Easy Auth** gates the App Service site to UN-tenant logins, but it
needs an Entra **app registration**, which requires identity-object creation rights *not* in
`Website Contributor`. Easiest path is the Portal Express flow (auto-creates the registration
under your identity): web app → **Authentication** → **Add identity provider** → **Microsoft**
→ *Create new app registration*, **single tenant**, **Require authentication**. Until that's
on, a site is public; a client-side password prompt (obfuscation, not real auth) is the only
self-serve interim gate.

> **First worked example:** `pa-aa-nga-cholera` cholera analysis book — `chd-pa-aa-nga-cholera`
> on `DsciAppServicePlan`, static `_book` via `pm2 serve`. If we later want true SWA
> (managed `/api` functions, per-site isolation), that needs an IT/admin resource-creation
> request; the App Service Plan route avoids it. Team storage accounts have
> `allowBlobPublicAccess=False`, so a "public blob container" is never an alternative for data.
