# MCP servers & claude.ai custom connectors

How to expose a tool to Claude as a **remote MCP server** that the team adds as a **custom
connector in claude.ai** (Team/Enterprise). Captured while building the KB MCP server
(`mcp_server/` — search/read the KB + read-only DB/blob); the implementation + deploy runbook
live there (`mcp_server/README.md`, `mcp_server/DEPLOY.md`). Researched mid-2026 against
Anthropic's connector docs + the MCP authorization spec (2025-06-18 / 2025-11-25) — re-verify,
this area moves.

## Connect to the live server (public tier)

**Endpoint:** `https://chd-ds-kb-mcp.azurewebsites.net/mcp` — public, **no auth**, **read-only**.

- **claude.ai (Team/Enterprise):** an org **Owner** → *Settings → Connectors → Add custom
  connector* → name `ds-knowledge-base`, paste the URL, choose **No authentication**, save.
  Members then toggle it on. (Authless = a shared URL works for anyone who has it — acceptable
  here because everything it serves is already public on GitHub.)
- **Claude Code (CLI):** `claude mcp add --transport http ds-kb https://chd-ds-kb-mcp.azurewebsites.net/mcp`
  (no token). `search_kb` / `read_kb_page` / `get_index` / `grep` / `glob` / `read_file` /
  `list_dir` / `fetch_repo_file` then become available.
- **Verify it's up:** `python mcp_server/deploy/check_remote.py https://chd-ds-kb-mcp.azurewebsites.net/mcp`
  (prints the tool list + a sample `search_kb`).

## What it can and cannot access (verified 2026-06-26)

The live public tier runs with **infra OFF and no credentials of any kind** — the Azure app
settings carry only `KB_MCP_TRANSPORT` (no `DSCI_AZ_*`, no `KB_MCP_ENABLE_INFRA`, no
`KB_MCP_AUTH`), and the access-restriction is open (the earlier IP lock was removed). Confirmed
two ways: reading the live app config, **and** driving the server's own tools against itself.

**CAN reach (read-only):**
- The **public** `OCHA-DAP/ds-knowledge-base` repo tree — every KB page, generated index,
  `scripts/`, and the public-source full-text under `raw/` (all already on GitHub).
- **Public** GitHub files via `fetch_repo_file` (default org OCHA-DAP) — to follow a page's
  `code_ref` / `source_repo` into spoke code.

**CANNOT reach (by design, probe-confirmed):**
- **No database, no blob.** `run_sql` / `list_blobs` / `read_blob` are **not even registered**
  (infra gate off), and the box holds **no `DSCI_AZ_*` creds** — nothing to query with.
- **The private companion repo** `OCHA-DAP/ds-knowledge-base-internal` (Drive manifest + content):
  `fetch_repo_file` is unauthenticated, so private repos 404.
- **The gitignored `drive/` store**: never in the deploy archive (`glob drive/**` → none).
- **Secrets / `.env` / `.git`**: none on the box (`read_file('.env')` / `.git/config` →
  "No such file"). The only `*secret*` / `*.pem` / `PRIVATE KEY` hits are public PyPI packages in
  the deployed venv; every `AZURE_CLIENT_SECRET` / `DSCI_AZ_*` hit is a variable **name** in
  docs/code, never a value.
- **Anything outside the repo root**: all file tools resolve through a path-traversal guard
  (`mcp_server/_paths.safe_resolve`); `../` and absolute escapes are rejected.

The only Drive-related thing it serves is the public pointer `infrastructure/drive-index.md`.
Full classification rules: [docs/PRIVACY.md](../docs/PRIVACY.md).

## What claude.ai actually requires (the load-bearing facts)

claude.ai's connector client is a **full MCP-native OAuth client**. It will **not** accept a
static token, a custom header, or a cookie/header identity-aware proxy — **App Service "Easy
Auth" and plain Cloudflare Access fail the handshake.** To connect with org login the endpoint
must speak the spec:

- **Streamable HTTP over public HTTPS**, reachable from Anthropic's IP ranges (you allowlist
  *them* — a VPN-only or you-IP-locked server can't be a connector).
- On an unauthenticated call, **`401` + `WWW-Authenticate: Bearer … resource_metadata="…"`** (RFC 9728).
- **Protected Resource Metadata** at `/.well-known/oauth-protected-resource[/<path>]` naming the AS.
- **AS discovery** via RFC 8414 or OIDC; **OAuth 2.1 + PKCE**, **RFC 8707** resource indicators.
- **Client registration** via DCR (RFC 7591), CIMD, or a pre-configured client (claude.ai UI:
  Advanced → OAuth Client ID/Secret). You can't paste a bare client_id and skip OAuth.
- Org **Owner** enables connectors org-wide and adds the URL; each member authenticates
  individually (per-user delegated OAuth — Claude inherits their permissions). No URL allowlist;
  a private self-hosted connector needs no directory listing or review.

There is also a truly **authless** mode (no auth on any method) that does connect — fine for
non-sensitive tooling where a secret URL is acceptable, useless when you need to know *who*.

## Entra is the constraint → FastMCP's OAuth proxy in front of it

Microsoft **Entra ID has no DCR, doesn't serve the RFC 8414 path, and rejects the RFC 8707
`resource` param**, so claude.ai **cannot point straight at Entra**. The working pattern (what
the KB server uses): run **FastMCP's `AzureProvider` / `OAuthProxy`** (standalone `fastmcp`
package ≥3) as the server's auth layer. It presents spec-compliant OAuth (DCR + PRM + PKCE) to
claude.ai while holding **one pre-registered Entra app** behind it and issuing its own
short-lived tokens. Key gotchas:

- The Entra app's **redirect URI is the FastMCP server's callback** — `<base_url>/auth/callback`
  — **not** claude.ai's. claude.ai's redirect (`https://claude.ai/api/mcp/auth_callback`) is
  configured in the provider's `allowed_client_redirect_uris`, not on the Entra app.
- Deploy as normal **app code** (uvicorn serving `fastmcp`'s `http_app`), **not** Easy Auth.
- The bundled `mcp.server.fastmcp` ships only a token *verifier*; `AzureProvider` is in the
  standalone `fastmcp` package.

Least-code alternative: a hosted MCP-OAuth gateway (WorkOS AuthKit / Stytch / Descope /
Scalekit) as the AS, federating to Entra — adds a third-party identity broker.

## Two servers — public (live) + internal (not yet)

There will be **two** KB MCP servers from one codebase (`mcp_server/`), separated by what
they can reach (env-gated). **The public one is live now; the internal one isn't deployed
yet** (blocked on the Entra app registration). Both run on **Azure App Service** in RG
`IMB-CHD-DataScience-EastUS2` (see [deployments.md](deployments.md)):

- **Public tier — `chd-ds-kb-mcp` · LIVE · authless.** `https://chd-ds-kb-mcp.azurewebsites.net/mcp`.
  Serves the **public** repo with KB + Claude-Code-style code-nav tools; **no credentials, infra
  OFF.** How to connect and the verified access boundary are above
  ([Connect](#connect-to-the-live-server-public-tier) · [What it can and cannot access](#what-it-can-and-cannot-access-verified-2026-06-26)).
- **Internal tier (HOSTED) — LIVE (2026-06-29): `chd-ds-kb-mcp-internal`.** A *hosted,
  shareable* streamable-HTTP endpoint on B2 `DsciAppServicePlan-Dev` with **infra ON**
  (`run_sql`/`list_blobs`/`read_blob` over read-only `DSCI_AZ_*` against prod+dev) **+ Drive
  extracts** (`KB_ROOT` = bundled internal repo). Locked by **`KB_MCP_AUTH=token`** (shared bearer
  `KB_MCP_STATIC_TOKEN`) — internet-reachable but 401 without the token. Reached only by the
  password-gated KB chatbot's `/private` page (which holds the token); not a claude.ai connector
  (those need OAuth, still Entra-blocked). Verified end-to-end: a `/private` question ran `run_sql`
  against the prod DB.
  - **Creds are env-var, no managed identity:** `ocha-stratus.get_engine` reads
    `DSCI_AZ_DB_{DEV,PROD}_{HOST,UID,PW}` (+ blob SAS) from the environment — set as app settings
    (read creds only, never `*_WRITE`). `ocha-stratus` pulls a heavy stack
    (pandas/pyarrow/geopandas/dask/xarray) → large build; raise `WEBSITES_CONTAINER_START_TIME_LIMIT`.
  - *Precedent:* `chd-ds-kb-mcp-dbtest` did this briefly on 2026-06-24 then was deleted for being
    unauthenticated (in `az webapp deleted list`). The `KB_MCP_AUTH=token` lockdown is what made
    redoing it safe.

Full requirements, the Entra app-registration checklist, and deploy commands:
[`mcp_server/DEPLOY.md`](../mcp_server/DEPLOY.md).
