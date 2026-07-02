# KB MCP server

An [MCP](https://modelcontextprotocol.io/) server that lets a Claude client answer
team-knowledge questions over this knowledge base — and, when explicitly enabled,
query our infra read-only. The intended surface is a **claude.ai custom connector**
(Team/Enterprise): each teammate adds the hosted server in their own Claude.

## Two servers: public + internal (both live)

**Two** deployments of this one codebase, separated by what they can reach (env-gated —
see [Environment](#environment)). Both are live.

| | **Public — `chd-ds-kb-mcp`** | **Internal — `chd-ds-kb-mcp-internal`** |
|---|---|---|
| Status | ✅ **LIVE** · `https://chd-ds-kb-mcp.azurewebsites.net/mcp` | ✅ **LIVE** (2026-06-29) · `https://chd-ds-kb-mcp-internal.azurewebsites.net/mcp` |
| Auth | none (authless) | **`KB_MCP_AUTH=token`** (shared bearer) — 401 without it |
| Tools | KB + code-nav only | the same **+** read-only DB/blob (`run_sql`/`list_blobs`/`read_blob`) + internal Drive extracts |
| Can reach | the **public** repo + **public** GitHub | the above **+** the team Postgres/blob (read role) + internal Drive content |
| Credentials on box | **none** | `DSCI_AZ_*` **read** creds (server-side) |
| `KB_MCP_ENABLE_INFRA` | off | on |
| Reached by | claude.ai connector / Claude Code | the KB chatbot's `/private` page (holds the token) |

The public tier holds **no credentials**, so it's safe to run authless — everything it serves is
already public on GitHub. The internal tier is infra-on (DB/blob + internal content), so it sits
behind the shared-bearer token (a fail-closed guard refuses to start `infra on + auth off`); the
`DSCI_AZ_*` **read** creds live server-side, never exposed to the user or model. A claude.ai
*custom connector* to the internal tier would still need Entra OAuth (`AzureProvider`) — that path
remains blocked on the Entra app registration — but the token path covers the trusted
server-side caller (the chatbot).

## Tools

| Tool | Creds? | What it does |
|---|---|---|
| `search_kb(query, …)` | no | Grep the KB markdown; ranked pages + line snippets |
| `read_kb_page(path)` | no | Return one page verbatim (repo-relative path) |
| `get_index(which)` | no | A generated index: `catalog` / `dependency-graph` / `db-schema` / `db-schema-dev` / `pipeline-registry` |
| `glob(pattern)` | no | Find repo files by glob (`**/*.py`, `*drought*.md`) |
| `grep(pattern, path, glob, …)` | no | Regex content search across the repo (ripgrep-style) |
| `read_file(path, offset, limit)` | no | Read any repo file with line numbers + ranges (markdown, `scripts/` code, `raw/` text) |
| `list_dir(path)` | no | List a repo directory |
| `fetch_repo_file(repo, path, ref)` | no | Follow `code_ref`/`source_repo` into a **public** GitHub spoke repo (private → 404) |
| `run_sql(query, stage, row_limit)` | **yes**, gated | SELECT/WITH-only Postgres query (`prod`/`dev`), row-capped + time-bounded |
| `list_blobs(prefix, stage, container)` | **yes**, gated | List blob names under a prefix |
| `read_blob(blob_name, stage, container)` | **yes**, gated | Shape + head of a `.parquet`/`.csv` blob |
| `run_python(code, timeout_s)` | **gated** (`KB_MCP_ENABLE_PYTHON`) | Sandboxed Python for analysis — scrubbed/credential-free env, isolated temp cwd, CPU/mem/process/time limits, privilege drop. pandas/numpy importable. Has outbound internet (public data) but **no credentials** (can't reach the DB/blob/Drive). See `exec_tools.py`. |

The infra tools are registered **only** when `KB_MCP_ENABLE_INFRA` is set. Read access
is via `ocha-stratus` with the read role (`stratus.get_engine(stage, write=False)`),
never the `_WRITE` creds — same path as `scripts/gen_db_schema.py`.

## Run locally (KB-only, stdio)

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r mcp_server/requirements.txt          # or just `mcp pyyaml` for KB-only
python -m mcp_server.server                          # stdio
```

Point a stdio MCP client at it (Claude Desktop config, or `mcp` dev inspector). To
also expose the read-only infra tools (needs the `DSCI_AZ_*` read env + `PGSSLMODE=require`):

```bash
KB_MCP_ENABLE_INFRA=1 python -m mcp_server.server
```

## Run as a remote server (Streamable HTTP)

```bash
KB_MCP_TRANSPORT=streamable-http PORT=8000 python -m mcp_server.server
# or: docker build -f mcp_server/Dockerfile -t kb-mcp . && docker run -p 8000:8000 kb-mcp
```

Streamable HTTP is the transport claude.ai custom connectors use. The MCP endpoint
is served at **`/mcp`** — the connector URL is `https://<your-host>/mcp`.

## Environment

| Var | Default | Notes |
|---|---|---|
| `KB_ROOT` | repo root | Where the KB markdown lives (image sets `/app`) |
| `KB_MCP_TRANSPORT` | `stdio` | `stdio`, or `streamable-http`/`http` (served at `KB_MCP_PATH`, default `/mcp`) |
| `KB_MCP_ENABLE_INFRA` | unset (off) | Set `1`/`true` to register infra tools |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Bind for the HTTP transport |
| `KB_MCP_AUTH` | unset (no auth) | `azure` → require Entra OAuth (connector mode). Needs the four below. |
| `AZURE_TENANT_ID` / `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` | — | The Entra app registration (the connector auth) |
| `KB_MCP_BASE_URL` | — | Public https base, e.g. `https://chd-ds-kb-mcp.azurewebsites.net` |
| `KB_MCP_AZURE_SCOPES` | — | Required scope(s), e.g. `api://<client_id>/mcp.access` |
| `DSCI_AZ_DB_{PROD,DEV}_{HOST,UID,PW}` | — | DB **read** creds (no `_WRITE`) |
| `DSCI_AZ_BLOB_{DEV,PROD}_SAS` | — | Blob **read** SAS (no `_WRITE`) |
| `PGSSLMODE` | `require` | Azure PG requires it |

## Auth (the real boundary)

claude.ai custom connectors are **MCP-native OAuth clients** — a static token, custom header,
or cookie/header proxy (App Service "Easy Auth", plain Cloudflare Access) does **not** work.
The credentials being server-side means the endpoint's own auth is the entire boundary, so
**do not deploy with `KB_MCP_ENABLE_INFRA` on until real connector-grade auth is in place**.
Recommended path: **FastMCP's `AzureProvider`/`OAuthProxy` in front of one Entra app** (Entra
itself lacks DCR/RFC-8414/RFC-8707, so claude.ai can't point straight at it). Full requirements,
the Entra setup, and alternatives are in **[DEPLOY.md](DEPLOY.md) § Auth**. Org-level connector
visibility in claude.ai is *not* a substitute — it controls who sees the connector, not who can
hit the wire.

## Status

- **Phase 1 — KB tools, local:** done. Verified over both stdio and streamable-http.
- **Phase 2 — read-only infra:** done & validated against the live **dev** DB + blob
  (`run_sql`, `list_blobs`, `read_blob`). Prod reads work the same way but are intentionally
  left to explicit, allowlisted use.
- **Phase 3 — public tier LIVE (2026-06-24):** **`chd-ds-kb-mcp`** (App Service in
  `IMB-CHD-DataScience-EastUS2`, on the existing `DsciAppServicePlan-Dev`), **authless** at
  `https://chd-ds-kb-mcp.azurewebsites.net/mcp`. Serves the **public** `OCHA-DAP/ds-knowledge-base`
  repo with KB + Claude-Code-style code-nav tools (search / grep / glob / read_file / list_dir +
  fetch_repo_file into public spokes). **No credentials; infra OFF.** Safe to expose authless
  because the repo is public — the `visibility: internal` flag only governs the *generated public
  site*, not GitHub visibility. **By design** the public tier also serves the committed
  `db-schema*.md` / `pipeline-registry.md` snapshots: they're public-repo content, and it's *live*
  DB/blob access (gated behind `KB_MCP_ENABLE_INFRA` + auth) — not these static snapshots — that's
  protected.
- **Phase 4 — hosted internal tier (not currently running; was proven once).** A hosted,
  shareable HTTP endpoint with infra on. **`chd-ds-kb-mcp-dbtest` was deployed and tested
  (queried the live DB from a Claude app) on 2026-06-24, then deleted the same day** over the
  "internet-reachable DB endpoint" worry (it's in `az webapp deleted list`, recoverable). So it's
  **proven-deployable** — not blocked in principle. Lock it down with Entra OAuth **or**
  `KB_MCP_AUTH=token` (shared bearer; added 2026-06) — the latter directly fixes the security
  concern that caused the teardown and needs no Entra. Entra registration is still the blocker
  for the *OAuth* path only.

### Credentials (DB/blob)

`ocha-stratus.get_engine` builds `postgresql+psycopg2://uid:pw@host/postgres` **purely from env
vars** — `DSCI_AZ_DB_{DEV,PROD}_{HOST,UID,PW}` (+ `DSCI_AZ_BLOB_{DEV,PROD}_SAS`). **There is no
managed-identity / `az login` fallback** — the creds must be in the process environment, so a
hosted app must have them set as app settings (prefer Key Vault refs; **read creds only, never
`*_WRITE`**).
