# Deploying the KB MCP server (Azure App Service)

Target: an Azure **Web App for Containers** in the team's resource group
**`IMB-CHD-DataScience-EastUS2`** (eastus2) — same place as the other ~20 `chd-*` apps
(see `infrastructure/deployments.md`). The container reuses `mcp_server/Dockerfile`, so
the same image runs locally, here, and (if you prefer) on Azure Container Apps.

The companion script `mcp_server/deploy/azure-webapp.sh` runs every `az` command below
with variables at the top — read it, set the vars, run it yourself. Nothing here is
auto-executed; it touches your cloud account.

> **Connector URL once live:** `https://chd-ds-kb-mcp.azurewebsites.net/mcp`
> (App Service gives HTTPS for free; the MCP endpoint is at `/mcp`.)

---

## Deployed instance (2026-06-24) — KB-only, locked

A KB-only instance is **already live** to prove hosting:

- **App:** `chd-ds-kb-mcp` on the existing **`DsciAppServicePlan-Dev`** (no new plan cost),
  RG `IMB-CHD-DataScience-EastUS2`. Endpoint: `https://chd-ds-kb-mcp.azurewebsites.net/mcp`.
- **Infra OFF** (`KB_MCP_ENABLE_INFRA` unset) — no `DSCI_AZ_*` creds on the box.
- **Locked down:** one Allow access-restriction (a single IP) + default Deny, so internal KB
  content is not publicly reachable. This also blocks claude.ai until auth is added (see § Auth).
- Deployed via the **code/Oryx zip path** (Docker wasn't available), not the container script.

Reproduce the code path (no Docker) — from a clean tree of this branch:

```bash
RG=IMB-CHD-DataScience-EastUS2; APP=chd-ds-kb-mcp; PLAN=DsciAppServicePlan-Dev
az webapp create -g "$RG" -p "$PLAN" -n "$APP" --runtime "PYTHON:3.11"
# lock to your IP BEFORE deploying content (adding an Allow rule makes the default Deny):
az webapp config access-restriction add -g "$RG" -n "$APP" \
  --rule-name allow-me --priority 100 --action Allow --ip-address "$(curl -s https://api.ipify.org)/32"
az webapp config set -g "$RG" -n "$APP" --startup-file "python -m mcp_server.server"
az webapp config appsettings set -g "$RG" -n "$APP" --settings \
  KB_MCP_TRANSPORT=streamable-http SCM_DO_BUILD_DURING_DEPLOYMENT=true
# zip = repo tree with a root requirements.txt (mcp, pyyaml for KB-only); then:
az webapp deploy -g "$RG" -n "$APP" --src-path app.zip --type zip
python mcp_server/deploy/check_remote.py https://$APP.azurewebsites.net/mcp
```

The Oryx build needs `requirements.txt` at the **deploy root** (KB-only: `mcp`, `pyyaml`).
To open it to the claude.ai connector later, the IP lock must come off and be replaced by
real auth — do **not** just remove the lock. To stop/remove the instance:
`az webapp stop -g "$RG" -n "$APP"` / `az webapp delete -g "$RG" -n "$APP"`.

---

## Go-live order (this matters)

Deploy in two gates so live infra is never on an unauthenticated endpoint:

1. **Gate 1 — KB-only, behind auth.** Deploy with `KB_MCP_ENABLE_INFRA` **unset**. Turn on
   App Service authentication (Entra ID). Validate the remote transport + that only OCHA
   users get in. The KB content is the bulk of the value and carries no live-infra risk.
2. **Gate 2 — enable infra.** Only after the endpoint is behind working auth *and* the
   connector-OAuth story is confirmed (see [Auth](#auth)), set `KB_MCP_ENABLE_INFRA=1` and
   add the read secrets. This is the step that exposes `run_sql`/blob reads.

---

## 1. Build & push the image

App Service for Containers pulls from a registry. Use the team ACR if one exists, else
create one in the RG (the script does `az acr create` if `$ACR` is unset). From the repo root:

```bash
az acr login --name "$ACR"
docker build -f mcp_server/Dockerfile -t "$ACR.azurecr.io/kb-mcp:$(git rev-parse --short HEAD)" .
docker push  "$ACR.azurecr.io/kb-mcp:$(git rev-parse --short HEAD)"
```

(The build runs from the repo root so the KB content is bundled — the `Dockerfile` does
`COPY . /app` and sets `KB_ROOT=/app`.)

## 2. Create the web app (container)

```bash
az appservice plan create -g "$RG" -n "$PLAN" --is-linux --sku B1
az webapp create -g "$RG" -p "$PLAN" -n "$APP" \
  --deployment-container-image-name "$ACR.azurecr.io/kb-mcp:$TAG"
az webapp config appsettings set -g "$RG" -n "$APP" --settings \
  WEBSITES_PORT=8000 PORT=8000 KB_MCP_TRANSPORT=streamable-http PGSSLMODE=require
# Gate 1: do NOT set KB_MCP_ENABLE_INFRA yet.
```

`WEBSITES_PORT=8000` tells App Service which port the container listens on (the Dockerfile
EXPOSEs 8000 and the server binds `0.0.0.0:8000`).

## 3. Secrets — read-only, via Key Vault references (Gate 2)

**Only the read credentials. Never the `_WRITE` variants.** The recommended way is Key Vault
references so secrets aren't sitting in plain app settings:

```bash
# Give the app a managed identity and grant it KV get access, then reference each secret:
az webapp identity assign -g "$RG" -n "$APP"
# (grant the identity 'Key Vault Secrets User' on $KEYVAULT — see the script)
az webapp config appsettings set -g "$RG" -n "$APP" --settings \
  DSCI_AZ_DB_PROD_HOST="@Microsoft.KeyVault(SecretUri=https://$KEYVAULT.vault.azure.net/secrets/DSCI-AZ-DB-PROD-HOST)" \
  DSCI_AZ_DB_PROD_UID="@Microsoft.KeyVault(...DSCI-AZ-DB-PROD-UID)" \
  DSCI_AZ_DB_PROD_PW="@Microsoft.KeyVault(...DSCI-AZ-DB-PROD-PW)" \
  DSCI_AZ_DB_DEV_HOST="@Microsoft.KeyVault(...DSCI-AZ-DB-DEV-HOST)" \
  DSCI_AZ_DB_DEV_UID="@Microsoft.KeyVault(...DSCI-AZ-DB-DEV-UID)" \
  DSCI_AZ_DB_DEV_PW="@Microsoft.KeyVault(...DSCI-AZ-DB-DEV-PW)" \
  DSCI_AZ_BLOB_PROD_SAS="@Microsoft.KeyVault(...DSCI-AZ-BLOB-PROD-SAS)" \
  DSCI_AZ_BLOB_DEV_SAS="@Microsoft.KeyVault(...DSCI-AZ-BLOB-DEV-SAS)" \
  KB_MCP_ENABLE_INFRA=1
```

Quicker but less safe (values readable by anyone with portal/CLI access to the app): set the
read values directly with `az webapp config appsettings set`. Fine for a first private test;
move to Key Vault before sharing.

**Required read vars** (the set the server uses): `DSCI_AZ_DB_{PROD,DEV}_{HOST,UID,PW}`,
`DSCI_AZ_BLOB_{PROD,DEV}_SAS`, `PGSSLMODE=require`. Deliberately **absent**: every `*_WRITE`.

## 4. DB firewall — allowlist the app's outbound IPs

The Azure Postgres servers are IP-gated (that's why CI allowlists the runner IP). The web
app's **outbound** IPs must be added to each PG server's firewall or `run_sql` will hang then
time out:

```bash
az webapp show -g "$RG" -n "$APP" --query outboundIpAddresses -o tsv
# add each to the prod & dev PG servers' firewall rules (portal or `az postgres ... firewall-rule create`)
```

Blob uses SAS over HTTPS/443 and is generally **not** IP-gated, so `list_blobs`/`read_blob`
usually work without this step.

## 5. Verify the deployment

Transport + tools, from anywhere (mirrors the local check):

```bash
python mcp_server/deploy/check_remote.py https://$APP.azurewebsites.net/mcp
```

It connects with the MCP streamable-HTTP client, lists tools, and calls `search_kb`. Behind
auth it should be rejected without a token and succeed with one.

---

## Auth

**Researched mid-2026 against Anthropic's connector docs + the MCP authorization spec
(2025-06-18 / 2025-11-25).** claude.ai custom connectors are **MCP-native OAuth clients**.
A static token, a custom header, or a cookie/header identity-aware proxy — **including App
Service "Easy Auth" and plain Cloudflare Access** — does **not** work; those fail the
handshake. (Earlier drafts of this doc suggested Easy Auth as a first layer — that was wrong.)

### What the endpoint must implement for claude.ai to connect with org login

- Streamable HTTP over **public HTTPS**, reachable from Anthropic's IP ranges. You allowlist
  *them*; a private/VPN-only or you-IP-locked server **cannot** be a connector (so the current
  IP lock on `chd-ds-kb-mcp` must come off — replaced by the auth below, not just removed).
- **`initialize` must succeed with NO token** — gate only `tools/list` / `tools/call`. (The #1 failure mode.)
- On an unauthenticated tools call: **`401` + `WWW-Authenticate: Bearer
  resource_metadata="…/.well-known/oauth-protected-resource"`** (RFC 9728).
- Serve **Protected Resource Metadata** at `/.well-known/oauth-protected-resource` naming your AS.
- Authorization-server discovery via **RFC 8414** or **OIDC** (`/.well-known/openid-configuration`).
- **OAuth 2.1 + PKCE (S256)**, **RFC 8707 resource indicators**, audience-validated tokens.
- Client registration via **DCR (RFC 7591)**, **CIMD**, or a pre-configured OAuth client
  (claude.ai UI exposes Advanced → OAuth Client ID/Secret — you cannot paste a bare client_id
  and skip OAuth).
- Register Anthropic's redirect URI **`https://claude.ai/api/mcp/auth_callback`** (+ loopback
  `http://localhost/callback` for Claude Code).
- **Org side:** an Owner enables connectors org-wide and adds the URL; each member then
  authenticates individually (per-user delegated OAuth). No general server-URL allowlist; a
  private self-hosted connector needs no directory listing or review.

### Entra is the deciding constraint → FastMCP's OAuth proxy in front of it (recommended)

Microsoft Entra ID **has no DCR, doesn't serve the RFC 8414 path, and rejects the RFC 8707
`resource` param** — so claude.ai **cannot point straight at Entra**. Run **FastMCP's
`AzureProvider` / `OAuthProxy`** (the standalone `fastmcp` package, ≥2.12) as the server's auth
layer: it presents spec-compliant OAuth (DCR + PRM + PKCE) to claude.ai while holding **one
pre-registered Entra app** behind it and issuing its own short-lived tokens (sidestepping
Entra's 8707 gap). Deploy as normal App Service **app code** — not Easy Auth.

Setup: one Entra app registration in the OCHA tenant (token v2; redirect
`https://claude.ai/api/mcp/auth_callback`; a custom scope; consent/assignment restricted to
OCHA users) → `AzureProvider(client_id, client_secret, tenant_id, base_url, required_scopes=[…])`
→ `FastMCP(auth=…)`.

**Alternative (least code, third-party dependency):** a hosted MCP-OAuth gateway
(WorkOS AuthKit, Stytch, Descope, Scalekit) as the AS, federating to Entra for SSO.

> **Code impact:** our server uses the `mcp` SDK's bundled `mcp.server.fastmcp`, which ships
> only a token *verifier*. The `AzureProvider`/`OAuthProxy` bridge lives in the standalone
> `fastmcp` package — adopting it is a small migration (same tool-decorator style). Test the
> handshake with MCP Inspector / Claude Code first; the claude.ai web client is the strictest.
>
> Sources: claude.com/docs/connectors/building; modelcontextprotocol.io spec 2025-11-25;
> learn.microsoft.com (Entra: no DCR, Aug 2025); gofastmcp.com/integrations/azure. Re-verify at
> build time — this area is moving.

---

## Connector auth — concrete Entra setup

The server implements the connector OAuth flow via FastMCP's `AzureProvider` when
`KB_MCP_AUTH=azure` (see `server.py`). Verified locally: it publishes RFC 9728 PRM at
`/.well-known/oauth-protected-resource/mcp`, RFC 8414 AS metadata with a DCR
`registration_endpoint`, and returns `401` + `WWW-Authenticate: Bearer … resource_metadata=…`
on unauthenticated calls. (`requirements.txt` now includes `fastmcp`.)

**1. One Entra app registration** (OCHA tenant; you, as admin):
- **Redirect URI (Web):** `https://chd-ds-kb-mcp.azurewebsites.net/auth/callback`
  — this is the **FastMCP server's** callback (`base_url` + `/auth/callback`), **not** claude.ai's.
  claude.ai's own redirect (`https://claude.ai/api/mcp/auth_callback`) is allowed inside the
  server via `KB_MCP_ALLOWED_REDIRECTS` (sensible defaults are built in) — do **not** add it to the Entra app.
- **Token version v2:** manifest `requestedAccessTokenVersion: 2`.
- **Expose an API / scope:** e.g. `api://<client_id>/mcp.access` → this is `KB_MCP_AZURE_SCOPES`.
- **Restrict to OCHA:** require assignment / limit consent so only OCHA users get through.
- Note the **client_id**, **tenant_id**, and a **client secret**.

**2. App settings** (read secrets from Key Vault as in §3; these are the auth additions):
```bash
az webapp config appsettings set -g "$RG" -n "$APP" --settings \
  KB_MCP_AUTH=azure \
  KB_MCP_BASE_URL=https://chd-ds-kb-mcp.azurewebsites.net \
  KB_MCP_AZURE_SCOPES="api://<client_id>/mcp.access" \
  AZURE_TENANT_ID="@Microsoft.KeyVault(...AZURE-TENANT-ID)" \
  AZURE_CLIENT_ID="@Microsoft.KeyVault(...AZURE-CLIENT-ID)" \
  AZURE_CLIENT_SECRET="@Microsoft.KeyVault(...AZURE-CLIENT-SECRET)"
```

**3. Remove the IP lock** (auth now replaces it — do not just delete it and leave it open):
```bash
az webapp config access-restriction remove -g "$RG" -n "$APP" --rule-name allow-sandbox
# the default becomes Allow-all, but the endpoint is now gated by Entra OAuth, not the network
```

**4. Verify** the discovery surface is public and the challenge is correct, then connect:
```bash
curl -s https://chd-ds-kb-mcp.azurewebsites.net/.well-known/oauth-protected-resource/mcp   # 200 PRM
curl -s https://chd-ds-kb-mcp.azurewebsites.net/.well-known/oauth-authorization-server      # 200 + registration_endpoint
python mcp_server/deploy/check_remote.py https://chd-ds-kb-mcp.azurewebsites.net/mcp        # 401 challenge without a token
```
Test the full handshake in **Claude Code** / MCP Inspector first (lenient), then have an org
**Owner enable connectors** and add the URL in claude.ai (Team); each member authenticates once.

**5. Only then enable infra** (`KB_MCP_ENABLE_INFRA=1` + the read secrets from §3 + the PG firewall).

> Don't `auth-on` (Easy Auth) from `azure-webapp.sh` — that's browser SSO, not the connector flow.

---

## Teardown

```bash
az webapp delete -g "$RG" -n "$APP"
az appservice plan delete -g "$RG" -n "$PLAN" -y
# remove the app's outbound IPs from the PG firewall rules you added
```

## CI (optional, later)

A `.github/workflows/deploy-kb-mcp.yml` can build+push the image and `az webapp` update on push
to `main` — modeled on the repo's existing workflows that already hold `DSCI_AZ_*` secrets.
Defer until the manual deploy + auth are proven.
