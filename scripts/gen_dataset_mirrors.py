#!/usr/bin/env python3
"""Inject the dataset-mirror wishlist into infrastructure/datasets/README.md.

The chatbot/MCP reads our blob + DB, not the live internet, so it can only *see*
an external source once a copy lives in our infra. Each `infrastructure/datasets/`
page records that state in `mirror:` (automated | manual | none | n/a). This script
derives the **wishlist** — the sources that aren't yet `automated` (and aren't `n/a`
platforms) — ranked by `mirror_priority` then demand (`len(used_by)`), and writes it
between the MIRRORS markers in the folder README. Never hand-edit the block: flip a
page's `mirror:` when a mirror lands and it drops off here.

Same shape as gen_doc_counts.py: no date in the block, so it only commits when the
derived table actually changes.

Usage:  python scripts/gen_dataset_mirrors.py [--check]   (run from repo root)
        --check : exit 2 if the block is out of date; write nothing (CI guard).
Needs:  pyyaml.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml  (or pip install pyyaml)")

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "infrastructure" / "datasets"
README = DATASETS / "README.md"
START, END = "<!-- MIRRORS:START -->", "<!-- MIRRORS:END -->"

PRIORITY_RANK = {"high": 0, "med": 1, "low": 2}
# States that still need a mirror. `automated` = done; `n/a` = not a mirrorable dataset.
WISHLIST_STATES = {"none", "manual"}
STATE_LABEL = {
    "none": "❌ not in our infra",
    "manual": "⚠️ manual refresh (stale risk)",
}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return None


def rows() -> list[dict]:
    out = []
    for path in sorted(DATASETS.glob("*.md")):
        if path.name == "README.md":
            continue
        fm = parse_frontmatter(path)
        if not fm or fm.get("content_type") != "dataset":
            continue
        state = str(fm.get("mirror", "none")).strip()
        if state not in WISHLIST_STATES:
            continue  # automated / n/a — not a candidate
        out.append({
            "name": fm.get("name", path.stem),
            "file": path.name,
            "state": state,
            "priority": str(fm.get("mirror_priority", "low")).strip(),
            "demand": len(fm.get("used_by") or []),
            "code_ref": fm.get("code_ref"),
        })
    out.sort(key=lambda r: (PRIORITY_RANK.get(r["priority"], 9), -r["demand"], r["name"]))
    return out


def block(rs: list[dict]) -> str:
    if not rs:
        return (f"{START}\n"
                "_Nothing to mirror — every dataset page is `automated` or `n/a`._\n"
                f"{END}")
    lines = [START,
             f"**{len(rs)} mirror candidate(s)** — ranked by priority, then demand "
             "(pages that reference the source):",
             "",
             "| dataset | current state | priority | demand | note |",
             "|---|---|---|---|---|"]
    for r in rs:
        note = "already in blob, no fresh loop" if r["state"] == "manual" else \
               ("has a loader; needs a copy" if r["code_ref"] else "no copy, no loader")
        lines.append(
            f"| [{r['name']}]({r['file']}) | {STATE_LABEL[r['state']]} "
            f"| {r['priority']} | {r['demand']} pages | {note} |")
    lines += ["", END]
    return "\n".join(lines)


def apply(body: str) -> bool:
    text = README.read_text(encoding="utf-8")
    i, j = text.find(START), text.find(END)
    if i == -1 or j == -1 or j < i:
        sys.exit(f"No MIRRORS markers in {README.relative_to(ROOT)}")
    new = text[:i] + body + text[j + len(END):]
    if new == text:
        return False
    README.write_text(new, encoding="utf-8")
    return True


def is_current(body: str) -> bool:
    text = README.read_text(encoding="utf-8")
    i, j = text.find(START), text.find(END)
    if i == -1 or j == -1:
        return True
    return text[i:j + len(END)].strip() == body.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 2 if the wishlist block is out of date; write nothing")
    args = ap.parse_args()

    body = block(rows())
    if args.check:
        if is_current(body):
            print("✅ dataset-mirror wishlist current.")
        else:
            print("Out-of-date wishlist — run `python scripts/gen_dataset_mirrors.py`.")
            sys.exit(2)
        return

    changed = apply(body)
    print(f"{'Updated' if changed else 'No change to'} MIRRORS block in "
          f"{README.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
