"""Knowledge-base tools: search and read the repo's markdown.

These need no credentials — they read the checked-out KB. The design intentionally
relies on grep + open-the-source rather than a semantic index (see docs/DESIGN.md),
so `search_kb` is a content grep and `read_kb_page` returns a page verbatim.

All functions take the KB repo root explicitly so they stay pure and testable;
the server wires in the configured root.
"""
from __future__ import annotations

import re
from pathlib import Path

from ._paths import safe_resolve

# search_kb intentionally walks ALL markdown (rglob), not a fixed content-dir list —
# it's a grep, and code-nav callers want hits anywhere. (No scoping constant: a prior
# one was dead + listed a dir twice, implying scoping the code didn't do.)
_SNIPPETS_PER_FILE = 3
_MAX_LINE = 200


# VCS internals + any bundled virtualenv. `antenv` is Azure Oryx's venv name; without
# it search_kb surfaces dependency READMEs from site-packages. Mirror code_tools._SKIP_DIRS.
_SKIP_DIRS = {".git", "__pycache__", ".venv", "antenv", "venv", "site-packages", "node_modules"}


def _iter_md(root: Path):
    """All KB markdown files, skipping VCS internals and bundled virtualenvs."""
    for path in sorted(root.rglob("*.md")):
        if _SKIP_DIRS.intersection(path.parts):
            continue
        yield path


def search_kb(root: Path, query: str, max_results: int = 20, regex: bool = False) -> str:
    """Grep KB markdown for `query`; return matching pages with line snippets.

    Case-insensitive. Set `regex=True` to treat `query` as a regular expression.
    Results are ranked by match count. Use `read_kb_page` to open a full page.
    """
    root = root.resolve()
    if not query.strip():
        return "Empty query."
    try:
        pattern = re.compile(query if regex else re.escape(query), re.IGNORECASE)
    except re.error as e:
        return f"Invalid regex: {e}"

    hits = []  # (match_count, rel_path, [snippet lines])
    for path in _iter_md(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines()
        matched = [(i + 1, ln) for i, ln in enumerate(lines) if pattern.search(ln)]
        if not matched:
            continue
        snippets = [f"  L{n}: {ln.strip()[:_MAX_LINE]}" for n, ln in matched[:_SNIPPETS_PER_FILE]]
        if len(matched) > _SNIPPETS_PER_FILE:
            snippets.append(f"  … +{len(matched) - _SNIPPETS_PER_FILE} more match(es)")
        hits.append((len(matched), path.relative_to(root).as_posix(), snippets))

    if not hits:
        return f"No matches for {query!r}."
    hits.sort(key=lambda h: -h[0])
    total = len(hits)
    hits = hits[:max_results]

    out = [f"{total} page(s) match {query!r}" + (f" (showing top {max_results})" if total > max_results else "") + ":", ""]
    for count, rel, snippets in hits:
        out.append(f"### {rel}  ({count} match{'es' if count != 1 else ''})")
        out.extend(snippets)
        out.append("")
    out.append("Open a page with read_kb_page(path).")
    return "\n".join(out)


def read_kb_page(root: Path, path: str) -> str:
    """Return the full markdown of a KB page (frontmatter + body).

    `path` is repo-relative, e.g. 'frameworks/lac-dry-corridor/2026-04-04.md'
    or a generated index like 'catalog.md' / 'infrastructure/db-schema.md'.
    """
    try:
        target = safe_resolve(root, path)
    except ValueError as e:
        return str(e)
    if not target.is_file():
        return f"No such page: {path}"
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return f"Could not read {path}: {e}"


def get_index(root: Path, which: str) -> str:
    """Return a generated orientation index verbatim.

    `which` is one of: 'catalog' (all framework-versions), 'dependency-graph'
    (cross-type deps + blast radius), 'db-schema' / 'db-schema-dev' (DB snapshots),
    'pipeline-registry' (deployed jobs + health). Read these first to orient.
    """
    index_paths = {
        "catalog": "catalog.md",
        "dependency-graph": "infrastructure/dependency-graph.md",
        "db-schema": "infrastructure/db-schema.md",
        "db-schema-dev": "infrastructure/db-schema-dev.md",
        "pipeline-registry": "infrastructure/pipeline-registry.md",
    }
    rel = index_paths.get(which)
    if rel is None:
        return f"Unknown index {which!r}. Options: {', '.join(index_paths)}."
    return read_kb_page(root, rel)
