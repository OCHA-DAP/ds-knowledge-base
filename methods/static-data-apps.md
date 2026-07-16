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

Stay on App Service when you need live DB queries, gated access, or heavy server-side
computation. For a *static* site that needs **org-login gating**, two routes exist — a
purpose-built **Static Web App** (now live; best when you want PR preview environments or Entra
auth, but standing one up is an IT request) or a **deployment on the shared App Service Plan**
(self-serve, no IT request) — both covered below.
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

## Richer hosting: Static Web Apps (IT-provisioned) or the App Service Plan (self-serve)

Two ways past GitHub Pages when you need Entra ID auth, server-side secrets, or PR preview
environments. They differ mainly in **who provisions the resource**.

### Azure Static Web Apps (now live)

> **Status update 2026-07-15:** the team's first purpose-built SWA is live —
> `chd-ds-satellite-impact-viewer` (satellite impact viewer, ADR-0023 in
> `ds-geospatial-impact-estimates`), Free tier, deploying via `Azure/static-web-apps-deploy`
> with the deployment token as a GitHub secret, **PRs get preview environments** on a staging
> data tier. (`dsci-monitor`, the pipelines-status dashboard, was already an SWA but predates
> this page's pattern.) Reference-implementation apps still run on GitHub Pages.

Same architecture, swap the last workflow steps for `Azure/static-web-apps-deploy` (deployment
token as secret — day-to-day CI publishing doesn't depend on anyone's Azure RBAC/PIM state).
Reach for SWA when you need **Entra ID auth** (Standard tier gates the whole
site behind org logins — Pages on public repos can't), **managed functions** (`/api/*` with
DB creds server-side = the hybrid for live/gated data, no CORS), or **PR preview
environments**. Limits: 250 MB app (Free) / 500 MB (Standard). Team storage accounts have
`allowBlobPublicAccess=False`, so "public blob container" is not an alternative for the data —
but for *larger-than-JSON* data (PMTiles/Parquet read client-side), pair the SWA with the
shared **[token issuer](../infrastructure/token-issuer.md)**: ephemeral scoped read-only SAS,
no secret in the app.

**The catch — we can't create SWAs ourselves yet (as of 2026-07).** Each SWA is its own Azure
resource, and the DS team's standing role (`Website Contributor`) **lacks
`Microsoft.Web/staticSites/write`** — `az staticwebapp create` returns `AuthorizationFailed`
(confirmed twice, incl. for the `adm.tdowning` account). The SWAs that *do* exist
(`chd-ds-satellite-impact-viewer`, `dsci-monitor`) were provisioned by someone with elevated
(Owner/User-Access-Administrator or PIM) access, not through a routine self-serve path — and
**no established IT process for getting a new one exists yet**. So treat a new SWA as
**currently blocked / an open ask with IT**, not a quick request. Until that access is sorted,
use the **[shared App Service Plan](#self-serve-alternative-deploy-into-the-shared-app-service-plan)**
(self-serve, no per-app resource) — see also
[token-issuer.md](../infrastructure/token-issuer.md#hosting-context--swas-and-the-it-resource-constraint).
Once a SWA resource *does* exist, day-to-day deploys are self-serve via its deployment token.

### Self-serve alternative: deploy into the shared App Service Plan

When you don't want to wait on an IT request, the **App Service Plan is a single,
already-blessed resource**, and `Website Contributor` lets us create web-app **deployments
inside it**. So host a static site (or a gated app) by creating an `az webapp` on the existing
plan rather than a new SWA — this is how the `pa-aa-nga-cholera` cholera book is served, and the
route most `chd-*` apps in [deployments.md](../infrastructure/deployments.md) already use.

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
hosts it with a gunicorn/uvicorn startup command.

**Making it org-login-internal — Entra Easy Auth** gates the App Service site to UN-tenant
logins, but it needs an Entra **app registration**, which requires identity-object creation
rights *not* in `Website Contributor`. Easiest path is the Portal Express flow (auto-creates the
registration under your identity): web app → **Authentication** → **Add identity provider** →
**Microsoft** → *Create new app registration*, **single tenant**, **Require authentication**.
Until that's on, the site is public; a client-side password prompt (obfuscation, not real auth)
is the only self-serve interim gate.

> **First worked example (self-serve route):** `pa-aa-nga-cholera` cholera analysis book —
> `chd-pa-aa-nga-cholera` on `DsciAppServicePlan`, static `_book` via `pm2 serve`.
