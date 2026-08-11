#!/usr/bin/env python3
"""Detect a stale deployed KB MCP server (the drift axis for the *served* KB).

The MCP apps serve whatever was in the deploy zip (`git archive HEAD` at deploy
time) — they never pull. Pages merged to main after the last redeploy are
invisible to every consumer of the server (claude.ai connectors, the chatbot's
public page, Claude Code `ds-kb`), which then answers "I don't know about X"
for work the KB documents. Discovered 2026-08-11: ipc-mirror / hnrp-mirror /
population-mirror were all on main but absent from the live box.

Compares, against the current checkout (run from a clean checkout of main):
  1. the full served page list (`glob('*.md')` — the server matches bare
     filenames, so this returns every .md in its tree) vs `git ls-files '*.md'`;
  2. the served content of the N most recently committed .md files
     (catches edited-in-place pages even when the file list matches).

Exit 0 = box matches main; exit 2 = drift (report written); exit 1 = probe
failed (server unreachable — that's an outage, not staleness).

Needs the `mcp` package. Probes the PUBLIC app by default; for the internal
app pass --url and set MCP_BEARER (the internal tier 401s without it).

    python scripts/check_mcp_staleness.py --report mcp-staleness.md
"""
from __future__ import annotations

import argparse
import asyncio
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from mcp import ClientSession
    from mcp.client import streamable_http as _sh
except ImportError:
    sys.exit("Needs the MCP client:  pip install mcp")
_MCP_V2 = hasattr(_sh, "streamable_http_client")  # renamed + resignatured in mcp 2.0


def _transport(url: str, bearer: str | None):
    headers = {"Authorization": f"Bearer {bearer}"} if bearer else None
    if _MCP_V2:
        client = _sh.create_mcp_http_client(headers=headers)
        return _sh.streamable_http_client(url, http_client=client)
    return _sh.streamablehttp_client(url, headers=headers)

PUBLIC_URL = "https://chd-ds-kb-mcp.azurewebsites.net/mcp"
_LINENO = re.compile(r"^\s*\d+\t", re.M)  # read_file returns cat -n style
_MORE = re.compile(r"\n… \(\d+ more lines.*$")  # read_file trailer past `limit`
_SERVER_MAX_LINE = 300  # code_tools.py truncates each served line to this
CONNECT_ATTEMPTS = 3  # cold App Service boxes can drop the first request


def _normalize_served(text: str) -> str | None:
    """Served read_file output → comparable text. '' if the box lacks the file
    (differs from any local content → flagged); None if the server refuses to
    serve it whole (too large) — uncomparable, skip."""
    if text.startswith("No such file"):
        return ""
    if " too large to read whole" in text[:200]:
        return None
    return _LINENO.sub("", _MORE.sub("", text))


def _normalize_local(path: Path) -> str:
    """Local file → what the server would serve for it (line-truncated)."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(ln[:_SERVER_MAX_LINE] for ln in lines)


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def local_md_files() -> set[str]:
    return {p for p in _git("ls-files", "*.md").splitlines() if p}


def recent_md_files(n: int) -> list[str]:
    """The n tracked .md files most recently touched on this branch."""
    seen: list[str] = []
    for path in _git("log", "--name-only", "--pretty=format:", "--", "*.md").splitlines():
        if path and path.endswith(".md") and path not in seen and Path(path).exists():
            seen.append(path)
            if len(seen) >= n:
                break
    return seen


async def _call(session: ClientSession, tool: str, args: dict) -> str:
    res = await session.call_tool(tool, args)
    return res.content[0].text


async def probe(url: str, samples: list[str]) -> tuple[set[str], dict[str, str | None]]:
    """Return (served .md paths, {sample path: served text or ''})."""
    token = os.environ.get("MCP_BEARER")
    last_err: Exception | None = None
    for attempt in range(CONNECT_ATTEMPTS):
        try:
            async with _transport(url, token) as streams:
                read, write = streams[0], streams[1]  # mcp 1.x yields a 3-tuple, 2.0 a 2-tuple
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    listing = await _call(session, "glob", {"pattern": "*.md", "max_results": 10000})
                    served = {
                        line for line in listing.splitlines()[1:]
                        if line.endswith(".md") and not line.startswith("…")
                    }
                    contents: dict[str, str | None] = {}
                    for path in samples:
                        text = await _call(session, "read_file", {"path": path, "limit": 10000})
                        contents[path] = _normalize_served(text)
                    return served, contents
        except Exception as e:  # noqa: BLE001 — retry any transport hiccup
            last_err = e
            await asyncio.sleep(15 * (attempt + 1))
    raise SystemExit(f"Could not reach {url} after {CONNECT_ATTEMPTS} attempts: {last_err}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=PUBLIC_URL)
    ap.add_argument("--report", default=None, help="write a markdown report here on drift")
    ap.add_argument("--content-samples", type=int, default=5,
                    help="N most-recently-committed pages to content-compare (default 5)")
    args = ap.parse_args()

    local = local_md_files()
    samples = recent_md_files(args.content_samples)
    served, served_content = asyncio.run(probe(args.url, samples))

    missing = sorted(local - served)          # on main, not on the box → stale deploy
    extra = sorted(served - local)            # on the box, not on main (renamed/removed since deploy)
    changed = [
        p for p in samples
        if p not in missing
        and served_content.get(p) is not None
        and _normalize_local(Path(p)) != served_content[p]
    ]

    if not (missing or extra or changed):
        print(f"OK: {args.url} serves all {len(local)} .md pages at current content.")
        return

    lines = [
        f"# Deployed KB MCP server is stale — `{args.url}`",
        "",
        f"The live box lags `main`: **{len(missing)} page(s) missing**, "
        f"{len(extra)} removed-on-main still served, "
        f"{len(changed)} of {len(samples)} sampled recent pages differ in content. "
        "Everything the server misses is invisible to the chatbot and every "
        "claude.ai / Claude Code connector.",
        "",
        "Runtime self-refresh (`mcp_server/refresh.py`) should have prevented this — "
        "call the server's `kb_version` tool for the served sha and `last error`. "
        "If this fired within ~15 min of a merge it may just be a pending tick; otherwise "
        "**fix (human, needs `az` login):** `bash mcp_server/deploy/redeploy_public.sh` "
        "(and `redeploy_internal.sh` — the internal app runs the same code). "
        "Then re-run this check.",
        "",
    ]
    for title, items in (("Missing from the box", missing),
                         ("Served but no longer on main", extra),
                         ("Content differs (recent-page sample)", changed)):
        if items:
            lines.append(f"## {title} ({len(items)})\n")
            lines += [f"- `{p}`" for p in items]
            lines.append("")
    report = "\n".join(lines)
    print(report)
    if args.report:
        Path(args.report).write_text(report)
    sys.exit(2)


if __name__ == "__main__":
    main()
