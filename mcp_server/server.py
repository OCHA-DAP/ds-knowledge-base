"""The MCP server: KB tools (always), infra tools (gated), Entra OAuth (gated).

Uses the standalone `fastmcp` package — its AzureProvider is what lets a claude.ai
custom connector authenticate against Microsoft Entra (Entra alone can't be a connector
auth server; the provider fronts it). Same tool set over stdio (local) or Streamable
HTTP (hosted).

    python -m mcp_server.server                                   # stdio, KB-only, no auth
    KB_MCP_ENABLE_INFRA=1 python -m mcp_server.server              # + read-only infra tools
    KB_MCP_TRANSPORT=streamable-http PORT=8000 python -m mcp_server.server   # remote, no auth
    KB_MCP_TRANSPORT=streamable-http KB_MCP_AUTH=azure ... python -m mcp_server.server  # connector

Environment:
    KB_ROOT              path to the KB repo (default: this file's repo root)
    KB_MCP_TRANSPORT     'stdio' (default), 'streamable-http' / 'http'
    KB_MCP_PATH          HTTP path for the MCP endpoint (default '/mcp')
    HOST / PORT          bind for HTTP transport (default 0.0.0.0:8000)
    KB_MCP_ENABLE_INFRA  '1' to expose run_sql/list_blobs/read_blob (needs DSCI_AZ_* read env)
    KB_MCP_AUTH          'azure' to require Entra OAuth (else no auth — local/dev only)
      AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET   the Entra app registration
      KB_MCP_BASE_URL          public https base, e.g. https://chd-ds-kb-mcp.azurewebsites.net
      KB_MCP_AZURE_SCOPES      comma-sep required scopes, e.g. api://<client_id>/mcp.access
      KB_MCP_ALLOWED_REDIRECTS comma-sep client redirect URIs (defaults cover claude.ai + Claude Code)

Two safety gates, both default-off: infra tools require KB_MCP_ENABLE_INFRA, and the
endpoint is unauthenticated unless KB_MCP_AUTH=azure. Never run the hosted endpoint with
infra on and auth off (see DEPLOY.md § Auth).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from fastmcp import FastMCP

from . import infra_tools, kb_tools

KB_ROOT = Path(os.environ.get("KB_ROOT", Path(__file__).resolve().parent.parent))
ENABLE_INFRA = os.environ.get("KB_MCP_ENABLE_INFRA", "").strip().lower() in ("1", "true", "yes")
AUTH = os.environ.get("KB_MCP_AUTH", "").strip().lower()

# claude.ai (web/desktop/mobile) + claude.com + Claude Code loopback. These are the MCP
# *client* redirects FastMCP must allow; the Entra app's own redirect is base_url/auth/callback.
_DEFAULT_REDIRECTS = (
    "https://claude.ai/api/mcp/auth_callback,https://claude.com/api/mcp/auth_callback,"
    "http://localhost/callback,http://127.0.0.1/callback"
)


def _build_auth():
    """Return an AzureProvider when KB_MCP_AUTH=azure, else None (no auth)."""
    if AUTH != "azure":
        return None
    from fastmcp.server.auth.providers.azure import AzureProvider

    scopes = [s.strip() for s in os.environ.get("KB_MCP_AZURE_SCOPES", "").split(",") if s.strip()]
    if not scopes:
        raise SystemExit("KB_MCP_AUTH=azure requires KB_MCP_AZURE_SCOPES (e.g. api://<client_id>/mcp.access)")
    allowed = [u.strip() for u in os.environ.get("KB_MCP_ALLOWED_REDIRECTS", _DEFAULT_REDIRECTS).split(",") if u.strip()]
    try:
        return AzureProvider(
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
            tenant_id=os.environ["AZURE_TENANT_ID"],
            required_scopes=scopes,
            base_url=os.environ["KB_MCP_BASE_URL"].rstrip("/"),
            allowed_client_redirect_uris=allowed,
        )
    except KeyError as e:
        raise SystemExit(f"KB_MCP_AUTH=azure missing required env: {e}")


mcp = FastMCP("ds-knowledge-base", auth=_build_auth())


# ---- KB tools (no credentials) -------------------------------------------------

@mcp.tool
def search_kb(query: str, max_results: int = 20, regex: bool = False) -> str:
    """Search the DS knowledge base markdown for a term and return matching pages
    with line snippets, ranked by match count. Use this first to find the right page,
    then open it with read_kb_page. Set regex=True to search by regular expression."""
    return kb_tools.search_kb(KB_ROOT, query, max_results=max_results, regex=regex)


@mcp.tool
def read_kb_page(path: str) -> str:
    """Return the full markdown of one KB page given its repo-relative path
    (e.g. 'frameworks/lac-dry-corridor/2026-04-04.md' or 'infrastructure/databricks.md')."""
    return kb_tools.read_kb_page(KB_ROOT, path)


@mcp.tool
def get_index(which: str) -> str:
    """Return a generated orientation index verbatim. `which` is one of:
    'catalog', 'dependency-graph', 'db-schema', 'db-schema-dev', 'pipeline-registry'.
    Read these to orient before searching."""
    return kb_tools.get_index(KB_ROOT, which)


# ---- Read-only infra tools (gated; require DSCI_AZ_* read env) ------------------

if ENABLE_INFRA:

    @mcp.tool
    def run_sql(query: str, stage: str = "prod", row_limit: int = 1000) -> str:
        """Run a read-only SELECT/WITH query against the team Postgres ('prod' or 'dev')
        and return the rows. Non-read queries are rejected; results are row-capped and
        time-bounded. Consult get_index('db-schema') for the schema first."""
        return infra_tools.run_sql(query, stage=stage, row_limit=row_limit)

    @mcp.tool
    def list_blobs(prefix: str, stage: str = "prod", container: str = "projects") -> str:
        """List blob names under a prefix in a container
        ('projects' | 'raster' | 'polygon' | 'global')."""
        return infra_tools.list_blobs(prefix, stage=stage, container=container)

    @mcp.tool
    def read_blob(blob_name: str, stage: str = "prod", container: str = "projects") -> str:
        """Preview a tabular blob (.parquet or .csv): its shape, columns, and first rows."""
        return infra_tools.read_blob(blob_name, stage=stage, container=container)


def main() -> None:
    transport = os.environ.get("KB_MCP_TRANSPORT", "stdio").strip().lower()
    print(f"[ds-knowledge-base mcp] root={KB_ROOT} transport={transport} "
          f"infra={'on' if ENABLE_INFRA else 'off'} auth={AUTH or 'none'}",
          file=sys.stderr, flush=True)
    if transport in ("streamable-http", "http"):
        mcp.run(transport="http",
                host=os.environ.get("HOST", "0.0.0.0"),
                port=int(os.environ.get("PORT", "8000")),
                path=os.environ.get("KB_MCP_PATH", "/mcp"))
    else:
        mcp.run()


if __name__ == "__main__":
    main()
