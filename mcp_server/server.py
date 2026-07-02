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
    KB_MCP_ENABLE_PYTHON '1' to expose run_python — sandboxed Python for analysis (scrubbed
                         env, no creds, resource/time limits). Same auth gate as infra.
    KB_MCP_AUTH          'token' (shared bearer secret KB_MCP_STATIC_TOKEN) | 'azure'
                         (Entra OAuth) | unset (no auth — local/dev only)
      KB_MCP_STATIC_TOKEN      shared secret when KB_MCP_AUTH=token; callers send
                               `Authorization: Bearer <secret>` (locks an infra HTTP
                               endpoint without OAuth, for a trusted server-side caller)
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

from . import code_tools, infra_tools, kb_tools

KB_ROOT = Path(os.environ.get("KB_ROOT", Path(__file__).resolve().parent.parent))
ENABLE_INFRA = os.environ.get("KB_MCP_ENABLE_INFRA", "").strip().lower() in ("1", "true", "yes")
ENABLE_PYTHON = os.environ.get("KB_MCP_ENABLE_PYTHON", "").strip().lower() in ("1", "true", "yes")
AUTH = os.environ.get("KB_MCP_AUTH", "").strip().lower()

# claude.ai (web/desktop/mobile) + claude.com + Claude Code loopback. These are the MCP
# *client* redirects FastMCP must allow; the Entra app's own redirect is base_url/auth/callback.
_DEFAULT_REDIRECTS = (
    "https://claude.ai/api/mcp/auth_callback,https://claude.com/api/mcp/auth_callback,"
    "http://localhost/callback,http://127.0.0.1/callback"
)


def _build_auth():
    """Return a FastMCP auth verifier per KB_MCP_AUTH:
      'token' — a shared bearer secret (KB_MCP_STATIC_TOKEN). Callers must send
                `Authorization: Bearer <secret>`. Lets an infra-enabled HTTP endpoint be
                locked down WITHOUT Entra/OAuth — for a trusted server-to-server caller
                (e.g. the password-gated KB chatbot) that can set the header itself.
                NOT usable by claude.ai connectors (they require full OAuth).
      'azure' — Entra OAuth (the claude.ai-connector path).
      unset   — no auth (local/dev only).
    """
    if AUTH == "token":
        from fastmcp.server.auth import StaticTokenVerifier

        token = os.environ.get("KB_MCP_STATIC_TOKEN", "").strip()
        if not token:
            raise SystemExit("KB_MCP_AUTH=token requires KB_MCP_STATIC_TOKEN (a shared secret).")
        return StaticTokenVerifier(tokens={token: {"client_id": "kb-internal", "scopes": ["kb"]}})
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


# ---- Code-navigation tools (no credentials; Claude-Code-style over the repo) ----

@mcp.tool
def glob(pattern: str, max_results: int = 200) -> str:
    """Find files in the repo by glob (e.g. '**/*.py', 'scripts/*.py', '*drought*.md').
    Returns repo-relative paths."""
    return code_tools.glob(KB_ROOT, pattern, max_results=max_results)


@mcp.tool
def grep(pattern: str, path: str = "", glob: str = "", ignore_case: bool = True,
         max_results: int = 200) -> str:
    """Regex content search across the repo (ripgrep-style). Optionally scope to a
    subtree (`path`, e.g. 'scripts') and/or filter files by `glob` (e.g. '*.py').
    Returns `relpath:line: text`; open hits with read_file."""
    return code_tools.grep(KB_ROOT, pattern, path=path or None, glob=glob or None,
                           ignore_case=ignore_case, max_results=max_results)


@mcp.tool
def read_file(path: str, offset: int = 1, limit: int = 400) -> str:
    """Read any repo file with line numbers, from line `offset` for up to `limit`
    lines (markdown, Python in scripts/, raw/ framework full-text, etc.)."""
    return code_tools.read_file(KB_ROOT, path, offset=offset, limit=limit)


@mcp.tool
def list_dir(path: str = ".") -> str:
    """List a directory in the repo."""
    return code_tools.list_dir(KB_ROOT, path)


@mcp.tool
def fetch_repo_file(repo: str, path: str, ref: str = "main") -> str:
    """Follow a KB page's code_ref/source_repo into the ACTUAL code: fetch a file from
    a PUBLIC GitHub repo (default org OCHA-DAP). `repo` is 'owner/name' or just 'name';
    `ref` is a branch/tag/sha (use the page's source_branch if 'main' 404s). Only public
    repos are reachable."""
    return code_tools.fetch_repo_file(repo, path, ref=ref)


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


# ---- Sandboxed Python for analysis (gated; KB_MCP_ENABLE_PYTHON) ---------------

if ENABLE_PYTHON:
    from . import exec_tools

    @mcp.tool
    def run_python(code: str, timeout_s: int = 30) -> str:
        """Execute Python for data analysis in a locked-down sandbox and return its output.

        pandas / numpy and the scientific stack are importable. The sandbox has a scrubbed,
        credential-free environment, an isolated temp working dir, and CPU/memory/process/time
        limits. It has outbound internet access (useful for pulling public reference data) but
        NO credentials, so it cannot reach the team DB/blob/Drive — fetch that with run_sql /
        read_blob first, then pass/recompute it here. Use print() to return results. Each call
        is independent (no variables or files persist between calls)."""
        return exec_tools.run_python(code, timeout_s=timeout_s)


def main() -> None:
    transport = os.environ.get("KB_MCP_TRANSPORT", "stdio").strip().lower()
    print(f"[ds-knowledge-base mcp] root={KB_ROOT} transport={transport} "
          f"infra={'on' if ENABLE_INFRA else 'off'} "
          f"python={'on' if ENABLE_PYTHON else 'off'} auth={AUTH or 'none'}",
          file=sys.stderr, flush=True)
    if transport in ("streamable-http", "http"):
        # Fail closed by default: never expose the gated read-only infra tools on a public
        # HTTP endpoint without auth. Deliberate, loud opt-out for short-lived insecure
        # testing only (KB_MCP_ALLOW_INSECURE_INFRA) — the endpoint then runs infra tools
        # UNAUTHENTICATED; anyone who reaches the URL can query the DB via the server's creds.
        if (ENABLE_INFRA or ENABLE_PYTHON) and AUTH not in ("azure", "token"):
            if os.environ.get("KB_MCP_ALLOW_INSECURE_INFRA", "").strip().lower() in ("1", "true", "yes"):
                print("WARNING: infra/python tools are exposed on an UNAUTHENTICATED endpoint "
                      "(KB_MCP_ALLOW_INSECURE_INFRA). Short-lived testing only — shut it down after.",
                      file=sys.stderr, flush=True)
            else:
                raise SystemExit(
                    "Refusing to start: KB_MCP_ENABLE_INFRA/KB_MCP_ENABLE_PYTHON is set on an HTTP "
                    "endpoint but KB_MCP_AUTH is not 'azure' or 'token'. Set KB_MCP_AUTH=token + "
                    "KB_MCP_STATIC_TOKEN (shared-secret lockdown), enable Entra auth, unset the "
                    "feature flag, or (insecure test only) KB_MCP_ALLOW_INSECURE_INFRA=1.")
        mcp.run(transport="http", show_banner=False,
                host=os.environ.get("HOST", "0.0.0.0"),
                port=int(os.environ.get("PORT", "8000")),
                path=os.environ.get("KB_MCP_PATH", "/mcp"))
    else:
        mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
