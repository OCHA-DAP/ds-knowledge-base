---
content_type: infrastructure
last_reviewed: "2026-07-16"   # bump when a human verifies the page is still accurate
source_repo: ocha-dap/ds-geospatial-impact-estimates
code_ref:
  - token-issuer/function_app.py
  - token-issuer/deploy.sh
  - token-issuer/README.md
  - docs/decisions/0022-keyless-sas-token-issuer.md
---

# chd-ds-token-issuer — shared keyless SAS token issuer

> The canonical reference is the spoke: `token-issuer/README.md` + ADR-0022 in
> `ds-geospatial-impact-estimates` (see `code_ref`). This page is the KB summary — trust the
> spoke where they diverge.

A **shared, team-wide** Azure Function App that mints **ephemeral, scoped, read-only SAS
tokens** for our web apps — so a browser can read data (PMTiles, Parquet, …) **directly from
blob storage** with **no long-lived secret stored anywhere** (no account key, no hand-rotated
SAS in app settings). Built for the satellite impact viewer (Venezuela earthquake response,
ADR-0022 in `ds-geospatial-impact-estimates`) but deliberately **multi-app**: registering a
new app is one allow-list entry. Use it for any client-side-blob app instead of baking a SAS
into config.

- **Endpoint:** `GET https://chd-ds-token-issuer.azurewebsites.net/api/token?app=<id>&tier=<staging|prod>`
- **Resource:** Function App `chd-ds-token-issuer` (Consumption plan, Linux, Python 3.11),
  RG `IMB-CHD-DataScience-EastUS2` (OCHA-PROD). Runtime storage `chd0tokenissuer` (bookkeeping
  only, no project data). Effectively **free** at our traffic (Consumption; ~one call per
  page-load, not per tile; free up to ~1M hits/month).

## How it works

The Function's **system-assigned managed identity** (principal
`ab58f738-0a28-4b2c-a69f-96800e6630d8`) calls `getUserDelegationKey` and mints a
**user-delegation SAS** — keyless (never touches the account key), **read-only**,
**directory-scoped**, **~24h expiry**. A config **allow-list** (`ALLOWLIST` dict in
`token-issuer/function_app.py`) maps each `?app=` id to a storage account + folder, and each
`?tier=` to a directory (e.g. the viewer's `platinum` staging vs `platinum-prod` data split);
unknown `app`/`tier` → HTTP 400. So there is **no arbitrary-path minting** — you can only get
a token for a folder someone deliberately registered.

Response JSON gives the frontend everything it needs:
`{account, container, base_url, platinum_dir, sas, mode, expires}` — `mode:
"delegation-platinum"` means keyless user-delegation (the intended path); a `scoped-*` mode
would indicate a fallback. Frontend pattern: fetch once on load, keep in memory, build URLs as
`` `${base_url}/${dir}/…?${sas}` ``, re-fetch before expiry. All actual data bytes go
browser→blob directly; the storage account needs **CORS** for the app's origin.

## Registering a new app

1. Add an entry to `ALLOWLIST` in `token-issuer/function_app.py` (account, container,
   `project_prefix`, and the `dirs` its `?tier=` values map to).
2. If the app's data lives in a storage account the issuer doesn't already cover, the MI needs
   **`Storage Blob Data Reader` at account scope** there (required for `getUserDelegationKey`).
   Role assignment needs Owner/User-Access-Administrator — an **IT/admin step**, plain
   Contributor can't. Currently granted on `imb0chd0dev`. Gotcha: management-plane "Reader" is
   **not** "Storage Blob Data Reader" — only the data-plane role works.
3. Redeploy: `token-issuer/deploy.sh` (handles the Linux-Consumption-Python quirks — `func`
   Core Tools not assumed, deps vendored, external run-from-package). Verify:
   `curl -s https://chd-ds-token-issuer.azurewebsites.net/api/token | jq .mode`.

## Security model

The endpoint is **anonymous by design**: the SAS it hands out is read-only, folder-scoped, and
short-lived — it grants nothing a normal visitor to the app couldn't already read, and it is
not the account key (can't write, delete, or reach other folders). **If an app serves
sensitive data**, gate the endpoint (API key / allowed-origins / Entra sign-in) *before*
registering it — or isolate that data in a storage account the issuer's MI has no grant on.

## Consumers

| app | how it uses the issuer |
|---|---|
| Satellite impact viewer — **SWA** `chd-ds-satellite-impact-viewer` (supersedes the App Service version) | browser calls the issuer **directly** (`VITE_TOKEN_URL` build-time config → issuer endpoint incl. `app`/`tier`); data read client-side (PMTiles/hyparquet) per ADR-0011/0023 |
| Satellite impact viewer — App Service `chd-ds-geospatial-impact-viewer` (classic URL / fallback) | **indirect**: browser calls same-origin `/api/token`; the FastAPI route proxies the issuer server-side (cached, refreshed when <6h left) with a graceful fallback chain — issuer → own-MI-minted delegation SAS → legacy `GIE_PLATINUM_SAS` app setting → `mode: unavailable` (`api/main.py`) |

(Add a row when you register an app.) See [apps/chd-ds-geospatial-impact-viewer.md](../apps/chd-ds-geospatial-impact-viewer.md)
and [deployments.md](deployments.md#azure-function-apps--static-web-apps).

## Hosting context — SWAs and the IT resource constraint

The issuer pairs naturally with **Azure Static Web Apps** as the team's emerging pattern for
client-side data apps: SWA (Free tier) hosts the static build, the issuer vends tokens, blob
serves the bytes — no always-on server. SWAs also support Entra ID password-protection if ever
needed. **But note the issuer is not SWA-specific** — it serves any client-side-blob app
(App Service, GitHub Pages, or SWA); the App Service viewer consumes it too (see Consumers).

**The catch — the DS team can't create SWAs yet (as of 2026-07).** Each SWA is its own Azure
resource, and our standing `Website Contributor` role **lacks `Microsoft.Web/staticSites/write`**
(`az staticwebapp create` → `AuthorizationFailed`). The existing team SWAs were stood up via
elevated (Owner/UAA or PIM) access; there is **no routine self-serve or established IT path for
a new one yet**, so treat a new SWA as currently blocked. The shared `DsciAppServicePlan` App
Service Plan is the **self-serve** alternative: the *plan* is the resource, so we can create
deployments inside it without a per-app resource request — see
[static-data-apps.md](../methods/static-data-apps.md#self-serve-alternative-deploy-into-the-shared-app-service-plan).
Free-tier SWAs deploy via a **deployment token** (GitHub secret), so day-to-day CI publishing
doesn't depend on anyone's Azure RBAC/PIM state once the resource exists.
