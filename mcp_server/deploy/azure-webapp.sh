#!/usr/bin/env bash
# Deploy the KB MCP server as an Azure Web App for Containers.
# Reference script — set the vars below and run ONE subcommand at a time:
#
#   ./azure-webapp.sh build      # build + push the image to ACR
#   ./azure-webapp.sh create     # plan + web app + base app settings (KB-only, infra OFF)
#   ./azure-webapp.sh auth-on    # require Entra ID auth (Layer A — do before going wider)
#   ./azure-webapp.sh firewall   # print the app's outbound IPs to allowlist on PG
#   ./azure-webapp.sh secrets    # Gate 2: managed identity + KV refs + KB_MCP_ENABLE_INFRA=1
#   ./azure-webapp.sh verify     # connect to the live /mcp endpoint and list tools
#
# It does NOT run end-to-end; each subcommand is explicit. See mcp_server/DEPLOY.md.
set -euo pipefail

# ---- configure -----------------------------------------------------------------
RG="IMB-CHD-DataScience-EastUS2"
LOCATION="eastus2"
APP="chd-ds-kb-mcp"
PLAN="chd-ds-kb-mcp-plan"
ACR="${ACR:-}"                       # existing ACR name, or leave blank to create one
ACR_NAME_IF_NEW="chddskbmcpacr"      # used only if ACR is blank
KEYVAULT="${KEYVAULT:-}"             # Key Vault holding the DSCI-AZ-* read secrets
ENTRA_TENANT="${ENTRA_TENANT:-}"     # tenant id for EasyAuth
ENTRA_CLIENT_ID="${ENTRA_CLIENT_ID:-}"  # app registration (audience) for EasyAuth
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
IMAGE=""  # set in _resolve_acr

_resolve_acr() {
  if [[ -z "$ACR" ]]; then
    ACR="$ACR_NAME_IF_NEW"
    az acr show -n "$ACR" >/dev/null 2>&1 || \
      az acr create -g "$RG" -n "$ACR" --sku Basic --admin-enabled true
  fi
  IMAGE="$ACR.azurecr.io/kb-mcp:$TAG"
}

cmd_build() {
  _resolve_acr
  az acr login --name "$ACR"
  docker build -f "$REPO_ROOT/mcp_server/Dockerfile" -t "$IMAGE" "$REPO_ROOT"
  docker push "$IMAGE"
  echo "pushed $IMAGE"
}

cmd_create() {
  _resolve_acr
  az appservice plan create -g "$RG" -n "$PLAN" --is-linux --sku B1 --location "$LOCATION"
  az webapp create -g "$RG" -p "$PLAN" -n "$APP" --deployment-container-image-name "$IMAGE"
  # Let the app pull from ACR via its managed identity (admin creds also enabled above).
  az webapp config appsettings set -g "$RG" -n "$APP" --settings \
    WEBSITES_PORT=8000 PORT=8000 KB_MCP_TRANSPORT=streamable-http PGSSLMODE=require
  echo "created https://$APP.azurewebsites.net (MCP at /mcp) — infra OFF, KB-only"
}

cmd_auth_on() {
  # Layer A: require Entra ID; reject unauthenticated requests.
  : "${ENTRA_TENANT:?set ENTRA_TENANT}"; : "${ENTRA_CLIENT_ID:?set ENTRA_CLIENT_ID}"
  az webapp auth update -g "$RG" -n "$APP" \
    --enabled true \
    --action RequireAuthentication \
    --redirect-provider azureActiveDirectory \
    --aad-allowed-token-audiences "api://$ENTRA_CLIENT_ID" \
    --aad-client-id "$ENTRA_CLIENT_ID" \
    --issuer "https://sts.windows.net/$ENTRA_TENANT/"
  echo "EasyAuth (Entra) blocks unauthenticated browser traffic, but does NOT satisfy the"
  echo "claude.ai connector OAuth handshake — it is not the connector auth. For a usable"
  echo "connector use FastMCP AzureProvider/OAuthProxy in app code — see DEPLOY.md §Auth."
}

cmd_firewall() {
  echo "Add these outbound IPs to the prod & dev Postgres firewall rules:"
  az webapp show -g "$RG" -n "$APP" --query outboundIpAddresses -o tsv | tr ',' '\n'
}

cmd_secrets() {
  # Gate 2: only run once the endpoint is behind working auth.
  : "${KEYVAULT:?set KEYVAULT}"
  az webapp identity assign -g "$RG" -n "$APP"
  PRINCIPAL_ID="$(az webapp identity show -g "$RG" -n "$APP" --query principalId -o tsv)"
  KV_ID="$(az keyvault show -n "$KEYVAULT" --query id -o tsv)"
  az role assignment create --assignee "$PRINCIPAL_ID" \
    --role "Key Vault Secrets User" --scope "$KV_ID"
  kv() { echo "@Microsoft.KeyVault(SecretUri=https://$KEYVAULT.vault.azure.net/secrets/$1)"; }
  # READ creds only — no *_WRITE.
  az webapp config appsettings set -g "$RG" -n "$APP" --settings \
    DSCI_AZ_DB_PROD_HOST="$(kv DSCI-AZ-DB-PROD-HOST)" \
    DSCI_AZ_DB_PROD_UID="$(kv DSCI-AZ-DB-PROD-UID)" \
    DSCI_AZ_DB_PROD_PW="$(kv DSCI-AZ-DB-PROD-PW)" \
    DSCI_AZ_DB_DEV_HOST="$(kv DSCI-AZ-DB-DEV-HOST)" \
    DSCI_AZ_DB_DEV_UID="$(kv DSCI-AZ-DB-DEV-UID)" \
    DSCI_AZ_DB_DEV_PW="$(kv DSCI-AZ-DB-DEV-PW)" \
    DSCI_AZ_BLOB_PROD_SAS="$(kv DSCI-AZ-BLOB-PROD-SAS)" \
    DSCI_AZ_BLOB_DEV_SAS="$(kv DSCI-AZ-BLOB-DEV-SAS)" \
    KB_MCP_ENABLE_INFRA=1
  echo "infra enabled with read-only KV-backed secrets. Don't forget the PG firewall (./azure-webapp.sh firewall)."
}

cmd_verify() {
  python "$REPO_ROOT/mcp_server/deploy/check_remote.py" "https://$APP.azurewebsites.net/mcp"
}

case "${1:-}" in
  build) cmd_build ;;
  create) cmd_create ;;
  auth-on) cmd_auth_on ;;
  firewall) cmd_firewall ;;
  secrets) cmd_secrets ;;
  verify) cmd_verify ;;
  *) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
