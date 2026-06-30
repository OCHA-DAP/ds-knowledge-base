#!/usr/bin/env python3
"""Deterministic drift check for the KB's *how-it-works* docs (the meta-docs).

The content layer self-maintains (drift / freshness / discovery → kb-ingest). The
meta-docs — DESIGN, ROADMAP, INGESTION, automation, the READMEs — had no detector
and rotted silently (stale counts, dangling script refs). This is their drift axis.

It is the *mechanical* half (high-signal, no judgment); the prose-staleness half
(shipped phases still marked todo, superseded rationale) is the monthly Claude
audit in `docs-audit.yml`. Two checks here:

  MISSING-REF   a meta-doc mentions a `scripts/<x>.py|.sh` or `.github/workflows/<x>.yml`
                that no longer exists on disk (renamed/deleted but the doc still names it).
  STALE-COUNTS  a doc's <!-- COUNTS --> block disagrees with the live corpus
                (someone added pages but didn't run gen_doc_counts.py).

Broken *markdown* links are covered by `lint-docs.yml` (mkdocs --strict), so they're
not re-checked here.

Usage:  python scripts/check_docs.py [--report docs-report.md]
Exit:   0 = clean · 2 = at least one finding
Needs:  pyyaml.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_doc_counts as gdc  # noqa: E402  (sibling module; reuse its COUNTS logic)

# The meta-docs: "how the KB works", not the content pages.
META_DOCS = [
    "README.md", "CLAUDE.md",
    "docs/DESIGN.md", "docs/INGESTION.md", "docs/ROADMAP.md", "docs/PRIVACY.md",
    "docs/README.md", "docs/glossary.md", "docs/PHASE2-SCOPE.md",
    "docs/repo-manifest.md", "docs/repo-audit.md", "docs/repo-doc-crosswalk.md",
    "infrastructure/automation.md", "scripts/README.md",
]

# Path-qualified references to project machinery. Anchored to the known dirs so we
# don't false-positive on prose. Trailing punctuation/backticks are trimmed.
REF_RE = re.compile(r"(scripts/[A-Za-z0-9_./-]+\.(?:py|sh)|\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml)")

# Machinery that lives in the PRIVATE companion repo (ds-knowledge-base-internal), not here —
# the docs reference it correctly but the file is absent from this repo by design (D46).
EXTERNAL_REFS = {".github/workflows/drive-sync.yml"}


def find_missing_refs() -> list[tuple[str, str, str]]:
    rows = []
    for rel in META_DOCS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        seen = set()
        for m in REF_RE.finditer(text):
            ref = m.group(1).rstrip(".,)`")
            if ref in seen or ref in EXTERNAL_REFS:
                continue
            seen.add(ref)
            if not (ROOT / ref).exists():
                rows.append((rel, "MISSING-REF", ref))
    return rows


def find_stale_counts() -> list[tuple[str, str, str]]:
    rows = []
    body = gdc.block(gdc.counts())
    for path in gdc.TARGETS:
        if path.exists() and not gdc.is_current(path, body):
            rows.append((path.relative_to(ROOT).as_posix(), "STALE-COUNTS",
                         "COUNTS block disagrees with the live corpus — run `python scripts/gen_doc_counts.py`"))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="write the markdown report to this file")
    args = ap.parse_args()

    rows = find_stale_counts() + find_missing_refs()

    lines = ["# KB meta-doc check", ""]
    if rows:
        lines.append(f"**{len(rows)} finding(s).**")
        lines += ["", "| doc | issue | detail |", "|---|---|---|"]
        lines += [f"| `{d}` | **{k}** | {v} |" for d, k, v in rows]
        lines += [
            "",
            "_Fix: `STALE-COUNTS` → run `python scripts/gen_doc_counts.py`. "
            "`MISSING-REF` → update the doc to the new path, or restore the file. "
            "Prose staleness (shipped phases, superseded rationale) is handled by the monthly "
            "`docs-audit.yml` Claude pass._",
        ]
    else:
        lines.append("✅ Meta-docs clean: counts current, all script/workflow references resolve.")
    report = "\n".join(lines) + "\n"

    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    sys.exit(2 if rows else 0)


if __name__ == "__main__":
    main()
