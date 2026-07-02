#!/usr/bin/env python3
"""Coverage audit: which in-scope ocha-dap repos have NO KB page yet (the backfill backlog).

Unlike check_new_repos.py (forward-only: new repos since a baseline), this reconciles the CURRENT
estate against CURRENT pages — it surfaces the EXISTING backlog. A repo is "ingested" if any KB page
carries it as `source_repo:`. In-scope = non-archived `ds-*` / `pa-aa-*` (the team's framework /
pipeline / app repos), minus templates and pre-2024 `pa-*` (COVID-era, excluded per repo-manifest).
Each un-ingested repo is classified (app / pipeline / framework) so it can be fed to kb-ingest.

Note: this finds framework *repos* without a page. Frameworks that exist on the OCHA site with NO
repo (e.g. Dry Corridor GTM/HND/NIC) are the aa-watch axis (`kb-aa-watch`), not this one.

Usage:  python scripts/check_coverage.py [--report f.md] [--emit PATH]
Exit:   0 = full coverage · 2 = at least one un-ingested in-scope repo
Needs:  gh (org read), git.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORG = "ocha-dap"
SLUG_RE = re.compile(r"((?:ocha-dap|OCHA-DAP)/[A-Za-z0-9._-]+)")
SCOPE_RE = re.compile(r"^(ds-|pa-aa-)", re.I)
# Not real ingestion targets even though they match the prefix (templates + meta/self repos).
DENY = re.compile(r"(cookiecutter|template|-test$|^ds-test|sandbox|playground"
                  r"|^ds-knowledge-base|^ds-claude-config)", re.I)
# Tokens that mark a repo as analysis/ad-hoc (→ analysis/ page, not an operational pipeline).
ANALYSIS = re.compile(r"(analysis|research|-support|adhoc|contingency|thresholds|displacement"
                      r"|risk|jiaf|bsgi|lngo|mapaction|teleconnections|-explore$|earthquake)", re.I)
# Deferred BY CHOICE (ROADMAP § Ingestion progress): in scope, but consciously not ingested —
# one-off analysis/support repos. Shown collapsed, not counted as gaps. Un-defer by removing here.
DEFERRED = re.compile(r"(^pa-anticipatory-action$|^pa-.*-support$|bsgi|jiaf|contingency"
                      r"|mapaction|sdn-displacement|som-risk-analysis)", re.I)


def sh(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


def ingested_slugs() -> set[str]:
    """Every repo that HAS a KB page — i.e. appears as `source_repo:` anywhere (lower-cased slug).
    Scans the whole tree (frameworks/pipelines/apps/analysis/infrastructure/libs/methods)."""
    out = set()
    for p in ROOT.rglob("*.md"):
        sp = str(p)
        if "/raw/" in sp or "/node_modules/" in sp or "/.git/" in sp:
            continue
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("source_repo:"):
                m = SLUG_RE.search(line)
                if m:
                    out.add(m.group(1).lower())
    return out


def classify(name: str) -> str:
    n = name.lower()
    if n.endswith("-app"):
        return "app"
    if ANALYSIS.search(n):
        return "analysis"
    if "monitoring" in n or n.endswith(("-pipeline", "-scraper", "-fetcher")):
        return "pipeline"
    if re.match(r"^(ds-aa-|pa-aa-)[a-z]{3}-", n):
        return "framework"
    return "pipeline"   # default for ds-* utilities/pipelines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report")
    ap.add_argument("--emit", help="write '<kind> <slug>' lines for the backlog")
    args = ap.parse_args()

    have = ingested_slugs()
    raw = sh(["gh", "repo", "list", ORG, "--limit", "2000", "--no-archived",
              "--json", "name,createdAt,visibility,description"])
    repos = json.loads(raw) if raw.strip() else []

    backlog = {"framework": [], "pipeline": [], "app": [], "analysis": []}
    deferred: list[tuple[str, str]] = []
    for r in repos:
        name = r["name"]
        if not SCOPE_RE.match(name) or DENY.search(name):
            continue
        if name.lower().startswith("pa-") and (r.get("createdAt") or "")[:4] < "2024":
            continue   # pre-2024 pa-* COVID-era, excluded per repo-manifest
        if f"{ORG}/{name}".lower() in have:
            continue
        if DEFERRED.search(name):
            deferred.append((name, (r.get("description") or "").strip()))
            continue
        backlog[classify(name)].append((name, (r.get("description") or "").strip()))

    total = sum(len(v) for v in backlog.values())
    lines = ["# KB coverage audit — un-ingested in-scope repos", "",
             f"_`scripts/check_coverage.py` — in-scope repos referenced by NO KB page. {total} un-ingested "
             f"({len(backlog['framework'])} framework · {len(backlog['pipeline'])} pipeline · "
             f"{len(backlog['app'])} app · {len(backlog['analysis'])} analysis/ad-hoc)._", "",
             "Frameworks that exist on the OCHA site with **no repo** are the separate "
             "[`kb-aa-watch`](../../issues?q=label%3Akb-aa-watch) axis. `analysis`/ad-hoc repos belong "
             "in `analysis/` (lighter than a pipeline runbook). Classification is heuristic — verify.", ""]
    for kind in ("framework", "pipeline", "app", "analysis"):
        items = sorted(backlog[kind])
        if not items:
            continue
        lines += [f"## {kind} ({len(items)})", "", "| repo | description | ingest |", "|---|---|---|"]
        for name, desc in items:
            if kind in ("app", "pipeline"):
                cmd = f"`gh workflow run kb-ingest.yml -f kind={kind} -f target={name}`"
            elif kind == "framework":
                cmd = "_PDF ingest (human)_"
            else:
                cmd = "_manual `analysis/` page (or out of scope)_"
            lines.append(f"| [`{name}`](https://github.com/{ORG}/{name}) | {desc[:70]} | {cmd} |")
        lines.append("")
    if deferred:
        lines += [f"<details><summary>Deferred by choice ({len(deferred)}) — one-off analysis/support repos "
                  "per ROADMAP § Ingestion progress; not counted as gaps (un-defer in check_coverage.py DEFERRED)</summary>", ""]
        lines += [f"- [`{n}`](https://github.com/{ORG}/{n}) {('— ' + d[:70]) if d else ''}" for n, d in sorted(deferred)]
        lines += ["", "</details>", ""]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    if args.emit:
        Path(args.emit).write_text(
            "\n".join(f"{k} {ORG}/{n}" for k in ("app", "pipeline") for n, _ in sorted(backlog[k])),
            encoding="utf-8")
    sys.exit(2 if total else 0)


if __name__ == "__main__":
    main()
