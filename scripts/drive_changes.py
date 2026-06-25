#!/usr/bin/env python3
"""Diff two Drive manifests → a human "what changed" summary (added/removed/modified files).

Used by the daily sync (private repo) to turn a re-crawl into a readable change log:
the commit message headline + a `drive/CHANGES.md` snapshot. Keyed on Drive file id
(stable across renames) + `modified` date.

Note: the manifest stores `modified` at DAY granularity, so two edits to the same file
on the same day read as one change — fine for a daily cadence.

Usage:  drive_changes.py OLD.json NEW.json [--out CHANGES.md]
Prints a one-line headline (for a commit subject) on the LAST stdout line.
"""
from __future__ import annotations
import json, sys, collections
from pathlib import Path


def files(manifest_path):
    nodes = json.loads(Path(manifest_path).read_text())["nodes"]
    return {n["id"]: n for n in nodes if n["type"] != "folder" and not n.get("excluded")}


def top(n):
    return (n.get("path", "") or "(root)").split("/")[0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        sys.exit("usage: drive_changes.py OLD.json NEW.json [--out CHANGES.md]")
    old, new = files(args[0]), files(args[1])
    added = [new[i] for i in new if i not in old]
    removed = [old[i] for i in old if i not in new]
    modified = [new[i] for i in new if i in old and new[i].get("modified") != old[i].get("modified")]

    lines = [f"# Drive changes", "",
             f"- **{len(added)}** added · **{len(modified)}** modified · **{len(removed)}** removed",
             ""]
    for label, rows in (("Added", added), ("Modified", modified), ("Removed", removed)):
        if not rows:
            continue
        lines.append(f"## {label} ({len(rows)})")
        by = collections.defaultdict(list)
        for n in rows:
            by[top(n)].append(n)
        for folder in sorted(by):
            lines.append(f"- **{folder}** ({len(by[folder])})")
            for n in sorted(by[folder], key=lambda x: x.get("path", ""))[:25]:
                lines.append(f"  - `{n.get('path','')}/{n['title']}` ({n['type']}, {n.get('modified','')})")
            if len(by[folder]) > 25:
                lines.append(f"  - …and {len(by[folder]) - 25} more")
        lines.append("")

    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        Path(out).write_text("\n".join(lines))

    print("\n".join(lines))
    # headline LAST (callers read the last line for a commit subject)
    n_changes = len(added) + len(modified) + len(removed)
    print(f"drive-sync: {len(added)} added, {len(modified)} modified, {len(removed)} removed"
          if n_changes else "drive-sync: no changes")


if __name__ == "__main__":
    main()
