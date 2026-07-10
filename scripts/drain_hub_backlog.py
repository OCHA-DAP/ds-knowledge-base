#!/usr/bin/env python3
"""Dispatch the next N external-framework stub enrichments (the Hub backlog, D77).

Stateless drainer: the queue IS the set of pages still marked `extra.hub_stub: true`
(gen_hub_stubs.py), prioritized IFRC → WFP → FAO → START (2026-07-09 direction), then
by people targeted. A stub leaves the queue when its enrichment PR merges (the rewrite
removes the marker) — so, to avoid re-dispatching work that's still in review, any page
whose `kb-ingest/<slug>` branch already exists on the remote is skipped.

Run by .github/workflows/hub-backlog-fill.yml (daily cron) or by hand.

Usage:  python scripts/drain_hub_backlog.py --cap 5 [--model sonnet] [--dry-run]
Needs:  gh (authed), pyyaml.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "external-frameworks"
PRIORITY = {"ifrc": 0, "wfp": 1, "fao": 2, "start-network": 3}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    try:
        return yaml.safe_load(text[3:end]) or {} if end != -1 else None
    except yaml.YAMLError:
        return None


def ingest_branch(page_rel: str) -> str:
    # mirror kb-ingest.yml:  slug="$(printf '%s' "$label" | tr -c 'a-zA-Z0-9_.-' '-')"
    return "kb-ingest/" + re.sub(r"[^a-zA-Z0-9_.-]", "-", page_rel)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=5, help="max enrichments to dispatch this run")
    ap.add_argument("--model", default="sonnet", help="draft model (Opus review always runs)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    queue = []
    for p in sorted(EXT.glob("*/*.md")):
        fm = parse_frontmatter(p)
        if fm and (fm.get("extra") or {}).get("hub_stub"):
            queue.append((PRIORITY.get(p.parent.name, 9),
                          -(fm.get("target_people") or 0),
                          p.relative_to(ROOT).as_posix()))
    queue.sort()
    if not queue:
        print("hub backlog empty — nothing to dispatch")
        return

    remote = subprocess.run(["git", "ls-remote", "--heads", "origin", "kb-ingest/*"],
                            capture_output=True, text=True, cwd=ROOT).stdout
    open_branches = set(re.findall(r"refs/heads/(\S+)", remote))

    dispatched = 0
    for _, _, rel in queue:
        if dispatched >= args.cap:
            break
        if ingest_branch(rel) in open_branches:
            print(f"  skip {rel} (enrichment PR branch already open)")
            continue
        print(f"  dispatch {rel}")
        if not args.dry_run:
            r = subprocess.run(["gh", "workflow", "run", "kb-ingest.yml",
                                "-f", f"page={rel}", "-f", f"model={args.model}"],
                               capture_output=True, text=True, cwd=ROOT)
            if r.returncode != 0:
                print(f"::warning::dispatch failed for {rel}: {r.stderr.strip()[:200]}")
                continue
        dispatched += 1
    print(f"{dispatched} dispatched · {len(queue)} stubs remain in queue"
          f"{' (dry-run)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
