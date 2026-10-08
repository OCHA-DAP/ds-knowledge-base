#!/usr/bin/env python3
"""Auto-merge the steward's deterministic re-sync PRs after a quiet period (D119).

The detect → Claude-draft → PR loop produces drafts faster than people merge them; drift
compounds while drafts age. Most drift re-syncs change nothing a person needs to judge:
the spoke moved, so `source_sha` / `code_ref` / sync stamps move with it and the body is
untouched. Those merge themselves here. Anything that touches prose, a trigger, a
decision, a PDF, or a second file still waits for a human.

A PR auto-merges only when ALL of these hold:
  - opened by the steward bot (`app/chd-ds-kb-steward`), label `kb-ingest`, not a draft
  - older than --min-age-days (default 3) with NO human review or comment (bot/app
    comments don't count; any human word parks the PR)
  - mergeStateStatus CLEAN and every status check green
  - exactly ONE file changed, under apps/ | pipelines/ | analysis/ | frameworks/ |
    external-frameworks/
  - the page BODY is byte-identical before and after; the only frontmatter keys that
    differ are in ALLOWED_KEYS (bookkeeping the spoke dictates)

Usage:  python scripts/automerge_resyncs.py [--dry-run] [--min-age-days 3] [--pr N ...]
Needs:  `gh` authenticated with a token that may merge (the KB bot app token in CI).
Exit 0 always; prints one line per PR with the decision and the reason.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("needs pyyaml")

REPO = "OCHA-DAP/ds-knowledge-base"
BOT = "app/chd-ds-kb-steward"
BOT_LOGINS = {"chd-ds-kb-steward", "chd-ds-kb-steward[bot]", "github-actions", "github-actions[bot]"}
PAGE_DIRS = ("apps/", "pipelines/", "analysis/", "frameworks/", "external-frameworks/")
# Frontmatter keys a re-sync may move on its own. Everything else is content.
ALLOWED_KEYS = {"source_sha", "source_branch", "source_commit", "last_synced", "synced_at",
                "last_checked", "drift_checked", "code_ref", "ingested_at", "ingest_run"}
OK_CHECKS = {"SUCCESS", "SKIPPED", "NEUTRAL"}


def gh(*args: str) -> str:
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"gh {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def split_page(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    try:
        fm = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return None, text
    return fm, text[end + 5:]


def file_at(path: str, ref: str) -> str | None:
    try:
        raw = gh("api", f"repos/{REPO}/contents/{path}?ref={ref}", "--jq", ".content")
    except RuntimeError:
        return None
    import base64
    return base64.b64decode(raw).decode("utf-8")


def classify(pr: dict) -> tuple[bool, str]:
    if pr["author"]["login"] != BOT:
        return False, f"author {pr['author']['login']} is not the steward"
    if pr["isDraft"]:
        return False, "draft"
    if "kb-ingest" not in {l["name"] for l in pr["labels"]}:
        return False, "no kb-ingest label"
    age_d = (datetime.now(timezone.utc) - datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))).days
    humans = [c["author"]["login"] for c in pr["comments"] if c["author"]["login"] not in BOT_LOGINS]
    humans += [r["author"]["login"] for r in pr["reviews"] if r["author"]["login"] not in BOT_LOGINS]
    if humans:
        return False, f"human touched it ({', '.join(sorted(set(humans)))})"
    if pr["mergeStateStatus"] != "CLEAN":
        return False, f"mergeStateStatus {pr['mergeStateStatus']}"
    bad = [c.get("name") or c.get("context") for c in pr["statusCheckRollup"]
           if (c.get("conclusion") or c.get("state") or "").upper() not in OK_CHECKS]
    if bad:
        return False, f"checks not green: {bad}"
    files = [f["path"] for f in pr["files"]]
    if len(files) != 1 or not files[0].startswith(PAGE_DIRS) or not files[0].endswith(".md"):
        return False, f"files {files} (need exactly one page)"
    path = files[0]
    old, new = file_at(path, pr["baseRefName"]), file_at(path, pr["headRefOid"])
    if old is None or new is None:
        return False, "page is new or deleted (not a re-sync)"
    ofm, obody = split_page(old)
    nfm, nbody = split_page(new)
    if ofm is None or nfm is None:
        return False, "frontmatter unparseable"
    if obody != nbody:
        return False, "body text changed"
    changed = {k for k in set(ofm) | set(nfm) if ofm.get(k) != nfm.get(k)}
    extra = changed - ALLOWED_KEYS
    if extra:
        return False, f"content keys changed: {sorted(extra)}"
    if not changed:
        return False, "no change at all"
    if age_d < ARGS.min_age_days:
        return False, f"only {age_d}d old (needs {ARGS.min_age_days}) — eligible: {sorted(changed)}"
    return True, f"re-sync of {sorted(changed)}, {age_d}d quiet"


def main() -> None:
    fields = ("number,title,author,isDraft,labels,createdAt,comments,reviews,mergeStateStatus,"
              "statusCheckRollup,files,baseRefName,headRefOid,headRefName")
    prs = json.loads(gh("pr", "list", "-R", REPO, "--label", "kb-ingest", "--state", "open",
                        "--limit", "100", "--json", fields))
    if ARGS.pr:
        prs = [p for p in prs if p["number"] in ARGS.pr]
    merged = 0
    for pr in sorted(prs, key=lambda p: p["number"]):
        ok, why = classify(pr)
        tag = "MERGE" if ok else "wait "
        print(f"#{pr['number']:<5} {tag}  {why}")
        if ok and not ARGS.dry_run:
            gh("pr", "comment", str(pr["number"]), "-R", REPO, "--body",
               f"Auto-merged (D119): a deterministic re-sync — {why}; the page body is unchanged and no one commented for {ARGS.min_age_days} days.")
            gh("pr", "merge", str(pr["number"]), "-R", REPO, "--merge", "--delete-branch")
            merged += 1
    print(f"{merged} merged" if not ARGS.dry_run else "dry run — nothing merged")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-age-days", type=int, default=3)
    ap.add_argument("--pr", type=int, nargs="*", help="only these PR numbers")
    ARGS = ap.parse_args()
    main()
