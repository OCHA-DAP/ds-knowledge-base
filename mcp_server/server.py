"""The MCP server: registers KB tools (always) and infra tools (gated).

Run locally over stdio (default) for development, or over Streamable HTTP for the
hosted deployment that claude.ai custom connectors require.

    python -m mcp_server.server                          # stdio, KB-only
    KB_MCP_ENABLE_INFRA=1 python -m mcp_server.server     # also expose read-only infra
    KB_MCP_TRANSPORT=streamable-http PORT=8000 python -m mcp_server.server

Environment:
    KB_ROOT              path to the KB repo (default: this file's repo root)
    KB_MCP_TRANSPORT     'stdio' (default) or 'streamable-http'
    KB_MCP_ENABLE_INFRA  set to 1/true to expose run_sql/list_blobs/read_blob
    HOST / PORT          bind address for streamable-http (default 0.0.0.0:8000)

Infra tools stay OFF by default on purpose: do not expose them until the endpoint
is behind auth (see README — auth is the real access boundary, not the creds).
"""
from __future__ import annotations

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import infra_tools, kb_tools

KB_ROOT = Path(os.environ.get("KB_ROOT", Path(__file__).resolve().parent.parent))
ENABLE_INFRA = os.environ.get("KB_MCP_ENABLE_INFRA", "").strip().lower() in ("1", "true", "yes")

mcp = FastMCP(
    "ds-knowledge-base",
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
)


# ---- KB tools (no credentials) -------------------------------------------------

@mcp.tool()
def search_kb(query: str, max_results: int = 20, regex: bool = False) -> str:
    """Search the DS knowledge base markdown for a term and return matching pages
    with line snippets, ranked by match count. Use this first to find the right page,
    then open it with read_kb_page. Set regex=True to search by regular expression."""
    return kb_tools.search_kb(KB_ROOT, query, max_results=max_results, regex=regex)


@mcp.tool()
def read_kb_page(path: str) -> str:
    """Return the full markdown of one KB page given its repo-relative path
    (e.g. 'frameworks/lac-dry-corridor/2026-04-04.md' or 'infrastructure/databricks.md')."""
    return kb_tools.read_kb_page(KB_ROOT, path)


@mcp.tool()
def get_index(which: str) -> str:
    """Return a generated orientation index verbatim. `which` is one of:
    'catalog', 'dependency-graph', 'db-schema', 'db-schema-dev', 'pipeline-registry'.
    Read these to orient before searching."""
    return kb_tools.get_index(KB_ROOT, which)


# ---- Read-only infra tools (gated; require DSCI_AZ_* read env) ------------------

if ENABLE_INFRA:

    @mcp.tool()
    def run_sql(query: str, stage: str = "prod", row_limit: int = 1000) -> str:
        """Run a read-only SELECT/WITH query against the team Postgres ('prod' or 'dev')
        and return the rows. Non-read queries are rejected; results are row-capped and
        time-bounded. Consult get_index('db-schema') for the schema first."""
        return infra_tools.run_sql(query, stage=stage, row_limit=row_limit)

    @mcp.tool()
    def list_blobs(prefix: str, stage: str = "prod", container: str = "projects") -> str:
        """List blob names under a prefix in a container
        ('projects' | 'raster' | 'polygon' | 'global')."""
        return infra_tools.list_blobs(prefix, stage=stage, container=container)

    @mcp.tool()
    def read_blob(blob_name: str, stage: str = "prod", container: str = "projects") -> str:
        """Preview a tabular blob (.parquet or .csv): its shape, columns, and first rows."""
        return infra_tools.read_blob(blob_name, stage=stage, container=container)


def main() -> None:
    transport = os.environ.get("KB_MCP_TRANSPORT", "stdio").strip().lower()
    infra = "on" if ENABLE_INFRA else "off"
    # stderr so it never corrupts the stdio JSON-RPC stream
    print(f"[ds-knowledge-base mcp] root={KB_ROOT} transport={transport} infra={infra}",
          flush=True, file=__import__("sys").stderr)
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
