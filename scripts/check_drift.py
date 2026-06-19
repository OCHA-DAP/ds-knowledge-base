#!/usr/bin/env python3
"""Flag hub pages whose spoke has moved since the page was written.

For every framework/pipeline page, compare the recorded `source_sha` against the
current HEAD of `source_branch` in the spoke repo (via `gh api`). If the spoke
moved AND the change touched any `code_ref` path, the page's summary may be
stale → flag it. Changes that don't touch `code_ref` are reported as low-signal.

This is *structural* drift detection: it tells you which pages to re-check (or
re-ingest), not whether the prose still semantically matches. It never edits
pages — fixing is a separate, reviewed step (re-run the ingest workflow).

Usage:  python scripts/check_drift.py [--report drift-report.md]
Exit:   0 = nothing stale · 2 = at least one STALE/BRANCH-GONE page
Needs:  gh CLI authenticated (or GH_TOKEN/GITHUB_TOKEN set); pyyaml.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SCAN = ["frameworks", "pipelines"]
SLUG_RE = re.compile(r"((?:ocha-dap|OCHA-DAP)/[A-Za-z0-9._-]+)")


def gh(*args: str) -> tuple[int, str]:
    """Run a gh command; return (returncode, stdout)."""
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def parse_frontmatter(path: Path) -> dict | None:
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return None
    end = t.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(t[3:end]) or {}
    except yaml.YAMLError:
        return None


def code_ref_prefixes(fm: dict) -> list[str]:
    """Reduce each code_ref entry to a matchable path prefix."""
    out = []
    for entry in (fm.get("code_ref") or []):
        s = str(entry)
        # strip inline comments and take the path token
        s = s.split("#", 1)[0].strip()
        if not s:
            continue
        # cut at the first glob/brace so dirs and {a,b} expansions become prefixes
        s = re.split(r"[\*\{]", s)[0]
        out.append(s)
    return out


_repo_ok: dict[str, bool] = {}


def repo_readable(slug: str) -> bool:
    """Can this token read the repo at all? Cached per slug.

    Distinguishes a deleted branch from an unreadable (usually private) spoke:
    in CI the default GITHUB_TOKEN is scoped to this repo only, so every private
    spoke 404s — that's a blind spot, not drift. Give it a PAT with org repo:read
    to actually monitor private spokes."""
    if slug not in _repo_ok:
        rc, out = gh("api", f"repos/{slug}", "--jq", ".full_name")
        _repo_ok[slug] = rc == 0 and bool(out)
    return _repo_ok[slug]


def head_sha(slug: str, branch: str) -> str | None:
    rc, out = gh("api", f"repos/{slug}/commits/{branch}", "--jq", ".sha")
    return out if rc == 0 and out else None


def changed_files(slug: str, base: str, head: str) -> list[str] | None:
    rc, out = gh("api", f"repos/{slug}/compare/{base}...{head}",
                 "--jq", "[.files[].filename]")
    if rc != 0 or not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="write the markdown report to this file")
    args = ap.parse_args()

    rows = []
    for d in SCAN:
        for path in sorted((ROOT / d).rglob("*.md")):
            if path.name in ("_TEMPLATE.md", "README.md"):
                continue
            fm = parse_frontmatter(path)
            if not fm:
                continue
            sr = str(fm.get("source_repo", ""))
            m = SLUG_RE.search(sr)
            branch = fm.get("source_branch")
            sha = fm.get("source_sha")
            rel = path.relative_to(ROOT).as_posix()
            if not (m and branch and sha):
                rows.append((rel, "NO-ANCHOR", "missing source_repo slug / branch / sha"))
                continue
            slug = m.group(1)
            branch = re.sub(r"^origin/", "", str(branch).split()[0])  # anchors sometimes keep the remote prefix
            sha = str(sha).split()[0]
            head = head_sha(slug, branch)
            if head is None:
                if not repo_readable(slug):
                    rows.append((rel, "NO-ACCESS",
                                 f"{slug} unreadable from this token (private spoke?) — drift not checked"))
                else:
                    rows.append((rel, "BRANCH-GONE", f"{slug}@{branch} not found (renamed/merged?)"))
                continue
            if head.startswith(sha) or sha.startswith(head):
                rows.append((rel, "OK", f"{slug}@{branch} {sha}"))
                continue
            files = changed_files(slug, sha, head)
            if files is None:
                rows.append((rel, "MOVED?", f"{slug}@{branch} moved to {head[:7]}; couldn't diff"))
                continue
            prefixes = code_ref_prefixes(fm)
            hit = sorted({f for f in files for p in prefixes if f.startswith(p)})
            if hit:
                detail = f"{slug}@{branch} {sha}→{head[:7]}; code_ref changed: " + ", ".join(hit[:6])
                rows.append((rel, "STALE", detail))
            else:
                rows.append((rel, "MOVED", f"{slug}@{branch} {sha}→{head[:7]}; {len(files)} files, none in code_ref"))

    order = {"STALE": 0, "BRANCH-GONE": 1, "MOVED": 2, "MOVED?": 3, "NO-ACCESS": 4, "NO-ANCHOR": 5, "OK": 6}
    rows.sort(key=lambda r: (order.get(r[1], 9), r[0]))
    counts = {}
    for _, st, _ in rows:
        counts[st] = counts.get(st, 0) + 1

    lines = ["# KB drift report", ""]
    lines.append(" · ".join(f"**{k}**: {counts[k]}" for k in sorted(counts, key=lambda k: order.get(k, 9))))
    lines.append("")
    flagged = [r for r in rows if r[1] in ("STALE", "BRANCH-GONE")]
    if flagged:
        lines += ["## Needs attention", "", "| page | status | detail |", "|---|---|---|"]
        lines += [f"| `{p}` | **{st}** | {d} |" for p, st, d in flagged]
        lines.append("")
        lines.append("_Fix: re-run `workflows/ingest-frameworks.mjs` for the flagged repo(s) and review the diff._")
    else:
        lines.append("✅ No pages with moved trigger code.")
    n_noaccess = counts.get("NO-ACCESS", 0)
    if n_noaccess:
        lines += ["", f"> ⚠️ **{n_noaccess} spoke(s) unreadable from this token** (private repos). "
                  "These are *not* checked for drift — a blind spot, not a clean bill of health. "
                  "Give the workflow a PAT with org `repo:read` to monitor private spokes.", ""]
    other = [r for r in rows if r[1] in ("MOVED", "MOVED?", "NO-ACCESS", "NO-ANCHOR")]
    if other:
        lines += ["", "<details><summary>Lower-signal (spoke moved but code_ref untouched / no access / no anchor)</summary>", "",
                  "| page | status | detail |", "|---|---|---|"]
        lines += [f"| `{p}` | {st} | {d} |" for p, st, d in other]
        lines += ["", "</details>"]
    report = "\n".join(lines) + "\n"

    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    sys.exit(2 if flagged else 0)


if __name__ == "__main__":
    main()
