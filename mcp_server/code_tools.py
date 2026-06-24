"""Code-navigation tools over the bundled repo — Claude-Code-style glob/grep/read,
plus fetch_repo_file to follow code_ref/source_repo into PUBLIC spoke repos on GitHub.

All local tools are read-only and confined to the KB repo root (the repo is public, so
this exposes nothing not already on GitHub). fetch_repo_file hits raw.githubusercontent
with no auth, so private repos simply 404 — it can never read non-public code.
"""
from __future__ import annotations

import fnmatch
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from ._paths import safe_resolve

_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".github/workflows/.cache"}
_MAX_MATCHES = 200
_MAX_FILE_BYTES = 600_000
_MAX_LINE = 300
_DEFAULT_ORG = "OCHA-DAP"


def _iter_files(root: Path, under: Path | None = None):
    base = under or root
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for f in filenames:
            yield Path(dirpath) / f


def _is_binary(sample: bytes) -> bool:
    return b"\x00" in sample


def glob(root: Path, pattern: str, max_results: int = 200) -> str:
    """Find files whose repo-relative path or name matches a glob (e.g. '**/*.py',
    'scripts/*.py', '*drought*.md'). Returns matching paths."""
    root = root.resolve()
    out = []
    for p in _iter_files(root):
        rel = p.relative_to(root).as_posix()
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(p.name, pattern):
            out.append(rel)
    if not out:
        return f"No files match glob {pattern!r}."
    out.sort()
    total = len(out)
    body = "\n".join(out[:max_results])
    if total > max_results:
        body += f"\n… +{total - max_results} more"
    return f"{total} file(s) match {pattern!r}:\n{body}"


def grep(root: Path, pattern: str, path: str | None = None, glob: str | None = None,
         ignore_case: bool = True, max_results: int = 200) -> str:
    """Regex content search across the repo (like ripgrep). Optionally scope to a
    subtree (`path`) and/or filter files by a glob (e.g. '*.py'). Returns
    `relpath:line: text` matches. Use read_file to open a hit with context."""
    root = root.resolve()
    try:
        rx = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
    except re.error as e:
        return f"Invalid regex: {e}"
    under = None
    if path:
        try:
            under = safe_resolve(root, path)
        except ValueError as e:
            return str(e)
        if not under.exists():
            return f"No such path: {path}"
    hits, scanned = [], 0
    for p in _iter_files(root, under if under and under.is_dir() else None):
        if under and under.is_file() and p != under:
            continue
        rel = p.relative_to(root).as_posix()
        if glob and not (fnmatch.fnmatch(rel, glob) or fnmatch.fnmatch(p.name, glob)):
            continue
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        if _is_binary(raw[:1024]):
            continue
        scanned += 1
        for i, line in enumerate(raw.decode("utf-8", "replace").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{rel}:{i}: {line.strip()[:_MAX_LINE]}")
                if len(hits) >= max_results:
                    return (f"{len(hits)}+ matches for {pattern!r} (capped; narrow with path/glob):\n"
                            + "\n".join(hits))
    if not hits:
        return f"No matches for {pattern!r} (scanned {scanned} files)."
    return f"{len(hits)} match(es) for {pattern!r}:\n" + "\n".join(hits)


def read_file(root: Path, path: str, offset: int = 1, limit: int = 400) -> str:
    """Read a file from the repo with line numbers, starting at line `offset`
    (1-based) for up to `limit` lines. Works on any file: markdown, Python in
    scripts/, raw/ framework full-text, etc."""
    try:
        target = safe_resolve(root, path)
    except ValueError as e:
        return str(e)
    if not target.is_file():
        return f"No such file: {path}"
    raw = target.read_bytes()
    if len(raw) > _MAX_FILE_BYTES:
        return f"{path} is {len(raw)//1024} KB — too large to read whole. Use grep, or pass offset/limit."
    if _is_binary(raw[:1024]):
        return f"{path} looks binary; not shown."
    lines = raw.decode("utf-8", "replace").splitlines()
    start = max(1, offset)
    chunk = lines[start - 1: start - 1 + max(1, limit)]
    if not chunk:
        return f"{path}: no lines at offset {offset} (file has {len(lines)} lines)."
    width = len(str(start + len(chunk) - 1))
    out = "\n".join(f"{start+i:>{width}}\t{ln[:_MAX_LINE]}" for i, ln in enumerate(chunk))
    more = "" if start - 1 + len(chunk) >= len(lines) else f"\n… ({len(lines) - (start-1+len(chunk))} more lines; raise offset/limit)"
    return out + more


def list_dir(root: Path, path: str = ".") -> str:
    """List the entries of a directory in the repo (dirs marked with a trailing /)."""
    try:
        target = safe_resolve(root, path)
    except ValueError as e:
        return str(e)
    if not target.is_dir():
        return f"Not a directory: {path}"
    entries = []
    for c in sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name)):
        if c.name in _SKIP_DIRS:
            continue
        entries.append(c.name + ("/" if c.is_dir() else ""))
    rel = target.resolve().relative_to(root.resolve()).as_posix()
    return f"{rel or '.'}/ ({len(entries)} entries):\n" + "\n".join(f"  {e}" for e in entries)


def fetch_repo_file(repo: str, path: str, ref: str = "main", max_bytes: int = 200_000) -> str:
    """Fetch a file from a PUBLIC GitHub repo (default org OCHA-DAP) — follow a KB page's
    code_ref/source_repo into the actual code. `repo` is 'owner/name' or just 'name'.
    `ref` is a branch/tag/sha (try the page's source_branch if 'main' 404s). Private
    repos return not-found (this tool only reaches public code)."""
    if "/" not in repo:
        repo = f"{_DEFAULT_ORG}/{repo}"
    if not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", repo):
        return f"Invalid repo {repo!r} (expected owner/name)."
    url = f"https://raw.githubusercontent.com/{repo}/{ref}/{path.lstrip('/')}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            raw = r.read(max_bytes + 1)
    except urllib.error.HTTPError as e:  # subclass of URLError — must come first
        if e.code == 404:
            return (f"Not found: {repo}@{ref}/{path}. Most likely a wrong ref/branch or path — "
                    f"check the page's source_branch and code_ref. (If those are right, the repo "
                    f"may be private; only public code is reachable.)")
        return f"Fetch failed (HTTP {e.code})."
    except (urllib.error.URLError, TimeoutError) as e:
        return f"Fetch failed (transient network error: {e}) — a retry may succeed."
    except Exception as e:  # noqa: BLE001
        return f"Fetch failed ({type(e).__name__}: {e})."
    if _is_binary(raw[:1024]):
        return f"{repo}/{path} looks binary; not shown."
    truncated = len(raw) > max_bytes
    text = raw[:max_bytes].decode("utf-8", "replace")
    return f"{repo}@{ref}/{path}:\n\n{text}" + ("\n… (truncated)" if truncated else "")
