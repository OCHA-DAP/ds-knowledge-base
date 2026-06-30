#!/usr/bin/env python3
"""Drain the framework-ingest backlog (`infrastructure/.aa-backlog.json`), a few per run.

A true queue: each run dispatches up to --cap entries via `kb-ingest.yml` (headless Claude web
ingest) and REMOVES them from the file (committed by the workflow), so the list shrinks to empty over
weeks without ever re-dispatching. Entries whose target page already exists are dropped silently
(already done). Populate the backlog by hand or by promoting items from the `kb-aa-watch` issue.

Usage:  python scripts/drain_aa_backlog.py [--cap 2] [--dry-run]
Exit:   0 always (best-effort). Needs: gh (workflow dispatch), pyyaml not required.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "infrastructure" / ".aa-backlog.json"


def sh(args: list[str]) -> int:
    return subprocess.run(args, capture_output=True, text=True).returncode


def page_exists(slug: str, version: str) -> bool:
    return bool(version) and (ROOT / "frameworks" / slug / f"{version}.md").exists()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=2, help="max ingests to dispatch this run (trickle)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not BACKLOG.exists():
        print("no backlog file"); return
    data = json.loads(BACKLOG.read_text())
    entries = data.get("entries", [])

    kept, dispatched, done = [], 0, 0
    for e in entries:
        country = (e.get("country") or "").upper()
        hazard = (e.get("hazard") or "").lower()
        slug = e.get("slug") or f"{country.lower()}-{hazard}"
        version = str(e.get("version") or "")
        if not (country and hazard):
            kept.append(e); continue                      # malformed → keep, skip
        if page_exists(slug, version):
            done += 1; continue                            # already ingested → drop
        if dispatched >= args.cap:
            kept.append(e); continue                       # over cap → defer to next run
        cmd = ["gh", "workflow", "run", "kb-ingest.yml",
               "-f", "kind=framework", "-f", f"country={country}", "-f", f"hazard={hazard}",
               "-f", f"slug={slug}"]
        if version:
            cmd += ["-f", f"version={version}"]
        if e.get("doc"):
            cmd += ["-f", f"doc={e['doc']}"]
        label = f"{slug} {version}".strip()
        if args.dry_run:
            print(f"[dry-run] would dispatch {label}")
            dispatched += 1; continue
        if sh(cmd) == 0:
            print(f"dispatched {label}"); dispatched += 1   # drop from queue (don't keep)
        else:
            print(f"::warning::dispatch failed for {label}"); kept.append(e)

    data["entries"] = kept
    if not args.dry_run:
        BACKLOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"dispatched {dispatched}, already-done {done}, remaining {len(kept)}")


if __name__ == "__main__":
    main()
