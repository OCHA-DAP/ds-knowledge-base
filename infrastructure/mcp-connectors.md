# MCP servers & claude.ai custom connectors

How to expose a tool to Claude as a **remote MCP server** that the team adds as a **custom
connector in claude.ai** (Team/Enterprise). Captured while building the KB MCP server
(`mcp_server/` — search/read the KB + read-only DB/blob); the implementation + deploy runbook
live there (`mcp_server/README.md`, `mcp_server/DEPLOY.md`). Researched mid-2026 against
Anthropic's connector docs + the MCP authorization spec (2025-06-18 / 2025-11-25) — re-verify,
this area moves.

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

## Where things run — two tiers

Both run on **Azure App Service** in RG `IMB-CHD-DataScience-EastUS2` (see
[deployments.md](deployments.md)) from one codebase (`mcp_server/`), env-gated:

- **Public tier — `chd-ds-kb-mcp` · LIVE · authless.** `https://chd-ds-kb-mcp.azurewebsites.net/mcp`.
  Serves the **public** `OCHA-DAP/ds-knowledge-base` repo with KB + Claude-Code-style code-nav
  tools (`search_kb` / `grep` / `glob` / `read_file` / `list_dir` / `get_index` + `fetch_repo_file`
  into public spokes). **No credentials; infra OFF.** Add it in claude.ai (Team): *Organization
  settings → Connectors → Add → Custom → Web →* the URL above *→ no auth*. Teammates then query the
  KB from Claude without cloning the repo.
  - **What it cannot reach (by design):** it has no creds and only serves *this public repo* +
    *public* GitHub. It **cannot** read the private companion repo
    [`OCHA-DAP/ds-knowledge-base-internal`](https://github.com/OCHA-DAP/ds-knowledge-base-internal)
    (the Drive manifest/content) — `fetch_repo_file` is unauthenticated, so private repos 404 — nor
    the gitignored `drive/` store (never in the deploy archive). The only Drive-related thing it
    serves is the public pointer `infrastructure/drive-index.md`. See [docs/PRIVACY.md](../docs/PRIVACY.md).
- **Internal tier — pending.** Full KB + read-only Postgres/blob (read-only `DSCI_AZ_*`, server-side,
  gated behind `KB_MCP_ENABLE_INFRA`) + later Drive, behind Entra OAuth. Blocked on the Entra app
  registration. A fail-closed guard refuses to run infra tools on an HTTP endpoint without auth
  (override `KB_MCP_ALLOW_INSECURE_INFRA` exists only for explicit, short-lived insecure tests).

Full requirements, the Entra app-registration checklist, and deploy commands:
[`mcp_server/DEPLOY.md`](../mcp_server/DEPLOY.md).
