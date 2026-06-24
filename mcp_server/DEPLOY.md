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

The credentials live server-side, so **who can reach the endpoint is the entire security
boundary.** Two layers, for two different jobs:

### Layer A — block unauthenticated traffic (do this at Gate 1)

Turn on **App Service Authentication (EasyAuth) with Entra ID**, set to *require*
authentication and reject unauthenticated requests. This ties access to OCHA identities and
is a one-command-ish toggle (see the script's `auth-on` section). With this on, a stranger
who learns the URL gets a 401 — which is the floor you need before Gate 2.

### Layer B — make claude.ai's custom connector authenticate (needed to actually use it)

claude.ai remote MCP custom connectors authenticate via the **MCP OAuth 2.1 flow**
(authorization-server / protected-resource metadata discovery, and typically dynamic client
registration). EasyAuth's browser redirect login is **not guaranteed** to satisfy that flow —
it secures the endpoint but may not expose the metadata/registration endpoints the connector
probes. So Layer A alone may block the connector too.

Realistic routes, best-aligned first:

1. **Entra ID as the authorization server + MCP auth in the server.** The MCP Python SDK can
   act as an OAuth *resource server*: it serves protected-resource metadata pointing at Entra
   and validates Entra-issued tokens. This keeps SSO with OCHA identity. The friction is
   dynamic client registration — Entra's support is limited, so you may need to pre-register
   the connector as an app or front Entra with a small bridge.
2. **A dedicated MCP-OAuth gateway** in front of the app (a proxy that implements the MCP auth
   spec and federates to Entra/SSO). Most moving parts; cleanest separation.
3. **Interim for a closed pilot:** keep infra **off**, leave EasyAuth on (Layer A), and test
   the *connector* against a tiny authless or token-gated KB-only deployment to confirm the
   transport, before investing in full OAuth. Don't put infra behind anything less than Layer B.

> ⚠️ **Verify against current docs before building Layer B.** claude.ai's custom-connector auth
> requirements evolve; confirm the exact OAuth/metadata/registration expectations in Anthropic's
> connector documentation at build time rather than trusting this note. This is the one genuinely
> uncertain piece of the whole plan — everything else is standard App Service.

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
