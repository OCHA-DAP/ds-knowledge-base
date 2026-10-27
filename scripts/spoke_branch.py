#!/usr/bin/env python3
"""Pick the spoke branch a KB page is (re-)drafted from — shared by ingest_framework.py and
ingest_system.py.

Work is often not on `main` (D18), so a NEW page reads the most recently committed branch. A
RE-DRAFT keeps the page's recorded `source_branch` while that branch still exists: recency alone
re-sourced pages onto bot branches that get commits but never hold the work — pa-aa-tcd-flooding's
`keep-awake` (a weekly empty commit; KB #816 moved the page there from main) and
ds-aa-nga-flooding's `monitoring-status` (status files pushed by the monitor).
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

# Branches that receive automated commits but never carry the analysis or trigger code.
HEARTBEAT_BRANCHES = {"keep-awake", "monitoring-status", "gh-pages"}


def remote_branches(clone: Path) -> list[str]:
    """Remote branch names of a fresh clone, most recently committed first."""
    out = subprocess.run(["git", "-C", str(clone), "for-each-ref", "--sort=-committerdate",
                          "--format=%(refname:short)", "refs/remotes/origin"],
                         capture_output=True, text=True).stdout.splitlines()
    names = []
    for r in out:
        r = r.strip()
        if r in ("", "origin", "origin/HEAD"):   # the origin/HEAD symref (shown as bare 'origin' by newer git)
            continue
        names.append(re.sub(r"^origin/", "", r))
    return names


def default_branch(clone: Path) -> str:
    """The remote's default branch (the origin/HEAD symref a fresh clone sets), else main."""
    ref = subprocess.run(["git", "-C", str(clone), "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
                         capture_output=True, text=True).stdout.strip()
    return re.sub(r"^origin/", "", ref) or "main"


def pick_branch(clone: Path, recorded: str | None = None) -> str:
    """The page's recorded branch if it still exists on the remote and isn't a heartbeat branch;
    else the most recently committed non-heartbeat branch; else the remote's default branch."""
    names = remote_branches(clone)
    # first token only, as check_drift.py reads it — a few pages annotate the value
    # (e.g. "main (analysis) / exposure-plots (monitoring)")
    words = str(recorded or "").split()
    recorded = re.sub(r"^origin/", "", words[0]) if words else ""
    if recorded and recorded in names and recorded not in HEARTBEAT_BRANCHES:
        return recorded
    return next((n for n in names if n not in HEARTBEAT_BRANCHES), None) or default_branch(clone)
