# KB MCP server

An [MCP](https://modelcontextprotocol.io/) server that lets a Claude client answer
team-knowledge questions over this knowledge base — and, when explicitly enabled,
query our infra read-only. The intended surface is a **claude.ai custom connector**
(Team/Enterprise): each teammate adds the hosted server in their own Claude.

The server holds the `DSCI_AZ_*` **read** credentials server-side; they are never
exposed to the user or the model. Access control is therefore entirely *who can reach
the endpoint* — see [Auth](#auth-the-real-boundary).

## Tools

| Tool | Creds? | What it does |
|---|---|---|
| `search_kb(query, …)` | no | Grep the KB markdown; ranked pages + line snippets |
| `read_kb_page(path)` | no | Return one page verbatim (repo-relative path) |
| `get_index(which)` | no | A generated index: `catalog` / `dependency-graph` / `db-schema` / `db-schema-dev` / `pipeline-registry` |
| `run_sql(query, stage, row_limit)` | **yes**, gated | SELECT/WITH-only Postgres query (`prod`/`dev`), row-capped + time-bounded |
| `list_blobs(prefix, stage, container)` | **yes**, gated | List blob names under a prefix |
| `read_blob(blob_name, stage, container)` | **yes**, gated | Shape + head of a `.parquet`/`.csv` blob |

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
| `KB_MCP_TRANSPORT` | `stdio` | `stdio` or `streamable-http` |
| `KB_MCP_ENABLE_INFRA` | unset (off) | Set `1`/`true` to register infra tools |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Bind for streamable-http |
| `DSCI_AZ_DB_{PROD,DEV}_{HOST,UID,PW}` | — | DB **read** creds (no `_WRITE`) |
| `DSCI_AZ_BLOB_{DEV,PROD}_SAS` | — | Blob **read** SAS (no `_WRITE`) |
| `PGSSLMODE` | `require` | Azure PG requires it |

## Auth (the real boundary)

claude.ai custom connectors speak OAuth 2.1. The credentials being server-side means
the **only** thing stopping a stranger who learns the URL is the endpoint's own auth —
so **do not deploy with `KB_MCP_ENABLE_INFRA` on until the endpoint is behind auth**.
Recommended: front it with an OAuth/SSO-aware proxy (Azure API Management or an
identity-aware proxy tied to OCHA SSO). Org-level connector visibility in claude.ai is
*not* a substitute — it controls who sees the connector in the UI, not who can hit the wire.

## Status

- **Phase 1 — KB tools, local:** done. Verified over both stdio and streamable-http.
- **Phase 2 — read-only infra:** done & validated against the live **dev** DB + blob
  (`run_sql`, `list_blobs`, `read_blob`). Prod reads work the same way but are intentionally
  left to explicit, allowlisted use.
- **Remaining:** deploy the container on Azure, put it behind OAuth/SSO, then register
  `https://<host>/mcp` as a claude.ai Team custom connector. A KB page under `infrastructure/`
  documenting the deployed server lands once it's live.
