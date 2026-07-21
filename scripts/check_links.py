#!/usr/bin/env python3
"""CI link check: relative markdown links to .md files that don't exist.

Replaces the `mkdocs build --strict` check that left with the MkDocs mirror (D87).
It enforces exactly the one class mkdocs.yml enforced (`links.not_found`) — a
relative link to a doc file that isn't on disk, the class that hides real rot.
Everything else is ignored on purpose, same as before: external URLs, anchors,
directory links (`frameworks/`, sibling `../bfa-flooding` folders in generated
READMEs), and non-doc assets — they resolve fine on the GitHub interface, which
is now the browsing surface.

Usage:  python scripts/check_links.py   (from repo root)
Exit:   0 = clean · 2 = at least one broken link (printed as file:line)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories whose .md files aren't part of the browsable corpus.
SKIP_PARTS = {".git", ".claude", "site", "__pycache__", "node_modules", ".pdf-cache"}

# Inline [text](target) and reference-style [label]: target definitions.
INLINE = re.compile(r"\[[^\]]*\]\(\s*<?([^)<>\s]+)[^)]*\)")
REFDEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+<?(\S+?)>?\s*$")


def targets(line: str):
    yield from INLINE.findall(line)
    m = REFDEF.match(line)
    if m:
        yield m.group(1)


def main() -> int:
    broken = []
    for md in sorted(ROOT.rglob("*.md")):
        rel = md.relative_to(ROOT)
        if SKIP_PARTS & set(rel.parts):
            continue
        in_fence = False
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            for t in targets(line):
                t = t.split("#", 1)[0]
                if not t or "://" in t or t.startswith(("mailto:", "/", "#")):
                    continue
                if not t.endswith(".md"):
                    continue
                if not (md.parent / t).exists():
                    broken.append(f"{rel}:{lineno}: broken link → {t}")
    if broken:
        print(f"{len(broken)} broken markdown link(s):")
        print("\n".join(broken))
        return 2
    print("links: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
