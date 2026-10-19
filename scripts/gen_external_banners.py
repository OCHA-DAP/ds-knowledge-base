#!/usr/bin/env python3
"""(Re)write the not-OCHA banner on every external-frameworks page (D105).

Each `external-frameworks/<org>/<iso3-hazard>.md` carries, directly under its H1, a
blockquote saying it is NOT an OCHA/CERF framework and linking OCHA's own framework(s)
for the country — so neither a reader nor a model takes IFRC's Nigeria EAP for OCHA's
Nigeria framework. The text is computed by `mcp_server.kb_tools.external_page_banner`
(the same producer the MCP server, `gen_hub_stubs.py` and the `NO-EXTERNAL-BANNER` lint
in `check_docs.py` use), matching OCHA frameworks on their pages' `country_iso3`
frontmatter — so a region-named multi-country framework (lac-dry-corridor → SLV/GTM/HND)
is found too.

Idempotent: inserts a missing banner, replaces a stale one, leaves a current one alone.
Run after a new `frameworks/` folder lands (the lint tells you when).

Usage:  python scripts/gen_external_banners.py [--check]   (repo root; needs pyyaml)
Exit:   0 · with --check: 2 if any page would change
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mcp_server.kb_tools import PAGE_BANNER_MARK, _frontmatter, external_page_banner  # noqa: E402


def _apply(text: str, banner: str) -> str | None:
    """Return the updated page text, or None when already current."""
    end = text.find("\n---", 3)
    if not text.startswith("---") or end == -1:
        return None
    body_start = end + 4
    lines = text[body_start:].split("\n")
    # replace an existing banner (any blockquote line carrying the marker)
    for i, ln in enumerate(lines):
        if ln.startswith(">") and PAGE_BANNER_MARK in ln:
            if ln == banner:
                return None
            lines[i] = banner
            return text[:body_start] + "\n".join(lines)
    # else insert after the H1
    m = re.search(r"^# .+$", text[body_start:], re.M)
    if not m:
        return None
    ins = body_start + m.end()
    return text[:ins] + "\n\n" + banner + text[ins:]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report, don't write")
    args = ap.parse_args()
    changed = []
    for p in sorted(ROOT.glob("external-frameworks/*/*.md")):
        if p.name.startswith("_"):
            continue
        text = p.read_text(encoding="utf-8")
        fm = _frontmatter(text)
        org, iso3 = fm.get("org") or p.parent.name, str(fm.get("country_iso3") or "")
        new = _apply(text, external_page_banner(ROOT, org, iso3))
        if new is None:
            continue
        changed.append(p.relative_to(ROOT).as_posix())
        if not args.check:
            p.write_text(new, encoding="utf-8")
    verb = "would change" if args.check else "updated"
    print(f"{len(changed)} page(s) {verb}" + (":\n  " + "\n  ".join(changed) if changed else ""))
    sys.exit(2 if (args.check and changed) else 0)


if __name__ == "__main__":
    main()
