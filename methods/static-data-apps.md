---
content_type: method
last_reviewed: "2026-07-21"   # bump when a human verifies the page is still accurate
---

# Static data apps — pre-baked data on GH Pages or Azure SWA

Ship interactive data apps as **static JS + data**, instead of a Python server
(marimo/Streamlit/Dash on App Service). No runtime, no creds anywhere near the client, every
interaction instant (all client-side), and hosting is cheap or free. "Static data app" is not
one recipe, though — it's a choice on **two independent axes** that this page previously
conflated:

1. **Hosting platform** — **GitHub Pages** (free, public CDN, no Azure resource) or **Azure
   Static Web App** (SWA; Entra ID auth, PR previews — but IT-provisioned, see below).
2. **Where the data lives / how it reaches the browser** — baked into the build **artifact**,
   **committed to the repo**, **pre-rendered** into the output (no separate data store), or
   **fetched at runtime from blob** (via the [token issuer](../infrastructure/token-issuer.md)).

The axes are **genuinely independent**: the runtime-from-blob path in particular is *not*
SWA-only — the token issuer serves any client-side app, so **GitHub Pages + token-issuer +
blob** is a real option, better than baking data into the artifact when the data is
larger-than-JSON or fresher-than-deploy, whenever you don't need SWA's extra features (org-login
gating, PR previews, managed `/api/*` functions). Pick by data size, data sensitivity, and how
dynamic/fresh the visualisation has to be.

## When to use static at all

- The app reads **aggregate/tabular data** (admin-level stats, timeseries) that fits in tens of
  MB — not live rasters or per-request DB queries (unless you use a runtime-from-blob route
  below for larger-than-JSON data, on either GH Pages or SWA).
- The data is **non-sensitive** (GH Pages on a public repo is world-readable; SWA can gate).
- Freshness of "updated on a schedule" is acceptable (cron redeploys; hourly is fine in-season),
  **or** the analysis is a one-off snapshot (the pre-rendered route).

Stay on App Service when you need live DB queries, gated access, or heavy server-side
computation. (Python-in-the-browser via WASM/pyodide does **not** change the calculus: still
client-side, so still no secrets, no Postgres sockets, plus a 30–60 MB runtime.)

---

## GitHub Pages — four data modalities

All four publish to GitHub's free CDN, one Pages site per repo. They differ in **where the
data lives**, which is what drives the size / freshness / recommendation trade-off.

### a. Pages **artifact** storage — the recommended GH modality

Export the data at deploy time and ship it **inside the Pages artifact**, so it never enters
git. This is the reference pattern — `ds-storm-impact-harmonisation` (`app/`,
`export_app_data.py`, `.github/workflows/deploy-app.yml`), live at
<https://ocha-dap.github.io/ds-storm-impact-harmonisation/compare/> — see
[apps/storm-exposure-compare](../apps/storm-exposure-compare.md). Three pieces:

1. **Export script** (Python, runs in CI only): queries Postgres via `ocha-stratus`, does the
   joins once, writes JSON under `app/data/` (**gitignored** — data never enters git).
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

Use this when the data is refreshed on a schedule and is more than "very light" — it's the
cleanest fit for a live-ish dashboard.

### b. Repo storage — light data only, **not recommended** otherwise

Commit the exported data file(s) **into the repo** alongside the app and let Pages serve them
directly (classic Pages "branch" mode, no export-in-CI step needed). Simplest to stand up, but
every refresh is a commit, the data bloats git history, and there's no atomic deploy. Reserve
for **very light, rarely-changing** data (a small lookup table, a handful of KB of JSON). For
anything that refreshes on a schedule or is more than trivially large, prefer the **artifact**
modality (a) instead — keeping data out of git is the whole reason that pattern exists.

### c. Pre-rendered static site / book — **no separate data store**

When the visualisation **doesn't need to be dynamic or continuously refreshed**, skip the
data-export layer entirely: a GH Action renders a **Quarto/RMarkdown book, rendered docs site,
or a marimo notebook exported to WASM** at build time, with the data baked straight into the
rendered output. Nothing to store or fetch at runtime. This is the right call for a
point-in-time analysis write-up or an explorer over a fixed dataset. Many team sites already do
this on GH Pages (see the [Pages table in deployments.md](../infrastructure/deployments.md#github-pages--netlify--rendered-sites--wasm-apps)):
the COD IDSR data-evaluation Quarto book, the `ds-teleconnections` docs/maps site, `ds-c3s-viz`,
and the marimo-WASM explorers (`ds-seas5-skill`, `ds-aa-ner-drought`, `ds-aa-vut-cyclones`).
(A pre-rendered book can equally be served from the shared App Service Plan when it needs
org-login gating — see the self-serve section; e.g. the `pa-aa-nga-cholera` book.)

### d. Runtime from blob via the token issuer — data lives outside the deploy

Host the static build on GH Pages exactly as in (a)/(b), but instead of shipping the data in
the artifact, **fetch it at runtime from blob storage** — the same
[token-issuer](../infrastructure/token-issuer.md) path the SWA route uses. The frontend calls
the shared **Azure Function App** (`chd-ds-token-issuer`) once on load; its managed identity
mints an ephemeral, scoped, read-only user-delegation SAS (keyless, ~24h, folder-scoped), and
the browser then reads PMTiles/Parquet/JSON **directly from blob** (browser→blob; the storage
account needs CORS for the `github.io` origin). No secret in the app, and `allowBlobPublicAccess`
stays `False`. The token issuer is **not SWA-specific** — it explicitly serves any client-side
app including GitHub Pages (see [token-issuer.md](../infrastructure/token-issuer.md#hosting-context--swas-and-the-it-resource-constraint)).

Reach for this when the data is **larger-than-JSON or needs to refresh independently of the
build** (so artifact storage (a) doesn't fit) **but you don't need SWA's extras** — org-login
gating, PR previews, or managed `/api/*` functions. It's the "something better than artifact
storage without standing up a SWA" middle ground: free public hosting on Pages + keyless
runtime blob reads. If you *do* need the whole site gated behind Entra logins or PR preview
environments, that's the SWA section below (only the hosting platform changes — the blob data
path is identical). Not yet used in a reference app; register the app in the issuer's allow-list
first (see token-issuer.md).

### GitHub Pages gotchas (all hit in the reference implementation)

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

---

## Azure Static Web App — when you need what Pages can't do

Reach for a **Static Web App** when you need something GitHub Pages structurally can't give you:
**Entra ID auth** (Standard tier gates the whole site behind org logins — Pages on public repos
can't), **PR preview environments**, or **managed `/api/*` functions** with DB creds
server-side. The static-app architecture is the same as the GH-Pages routes; what changes is the
hosting platform and the deploy target (`Azure/static-web-apps-deploy`, deployment token as a
GitHub secret — day-to-day CI publishing doesn't depend on anyone's Azure RBAC/PIM state).

**Note the runtime-from-blob data path is _not_ a reason to pick SWA over Pages** — it's the
same token-issuer pattern GH Pages modality (d) uses, so "I have larger-than-JSON data" alone
does *not* require a SWA. Choose SWA for the auth / preview / managed-function features; choose
GH Pages + token issuer if you only need the blob data path.

> **Status (2026-07-15):** the team's first purpose-built SWA is live —
> `chd-ds-satellite-impact-viewer` (satellite impact viewer, ADR-0023 in
> `ds-geospatial-impact-estimates`), Free tier, **PRs get preview environments** on a staging
> data tier. (`dsci-monitor`, the pipelines-status dashboard, was already an SWA but predates
> this page's pattern.) Reference-implementation apps still run on GitHub Pages.

**How the data reaches the browser — an Azure Function App handles the tokens** (identical to
GH Pages modality (d) above; the platform is the only difference). Team storage accounts have
`allowBlobPublicAccess=False`, so the data container is *not* public. Instead of baking a
long-lived SAS into config, the app calls the shared **[token issuer](../infrastructure/token-issuer.md)**
— an **Azure Function App** (`chd-ds-token-issuer`, Consumption/Linux/Py 3.11) whose managed
identity mints **ephemeral, scoped, read-only user-delegation SAS** tokens (keyless, ~24h,
folder-scoped). The frontend fetches a token once on load and reads PMTiles/Parquet/JSON
directly from blob (browser→blob; the storage account needs CORS for the app's origin). No
secret in the app. Reference: `chd-ds-satellite-impact-viewer`; see
[token-issuer.md](../infrastructure/token-issuer.md). (SWA also supports **managed functions**
`/api/*` with DB creds server-side — the hybrid for live/gated data, no CORS — if you need
server-side logic rather than just token-brokered blob reads.) Limits: 250 MB app (Free) /
500 MB (Standard) — that's the *app bundle*; the data lives in blob, not the bundle.

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

---

## Self-serve alternative: deploy into the shared App Service Plan

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
