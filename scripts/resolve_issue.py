#!/usr/bin/env python3
"""Attempt to resolve ONE GitHub issue with headless Claude (Max plan).

Fetches the issue + its full comment thread, hands them to `claude -p` together with the
KB conventions (scripts/kb_steward_prompt.md), and lets Claude edit the repo in place.
The caller (`.github/workflows/kb-steward.yml`) turns any resulting working-tree change
into a PR that closes the issue. This script makes **no git commits** — it only edits files
(or leaves the tree clean if Claude can't confidently resolve the issue).

Usage:  python scripts/resolve_issue.py --issue 123 [--model opus]
Needs:  gh (authenticated) + the `claude` CLI on PATH (CLAUDE_CODE_OAUTH_TOKEN in env).
Exit:   0 if Claude ran (whether or not it changed files); non-zero only on a hard error.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = ROOT / "scripts" / "kb_steward_prompt.md"
ALLOWED_TOOLS = ["Read", "Edit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch"]
# SECURITY: the issue body/comments are partly untrusted input driving an agent with Bash + web access.
# Scrub every GitHub credential from the Claude subprocess's environment so a prompt-injected run can't
# read a token and exfiltrate it / push elsewhere. Claude only keeps CLAUDE_CODE_OAUTH_TOKEN (which it
# needs to run). The workflow does all git push / PR / issue ops itself, AFTER Claude exits, with the
# token in the *shell* env (never the Claude subprocess). Pair with `persist-credentials: false` on
# checkout so the token isn't readable from .git/config either.
SCRUB_ENV = ("GH_TOKEN", "GITHUB_TOKEN", "INGEST_GH_PAT", "DISCOVER_GH_PAT",
             "KB_BOT_APP_ID", "KB_BOT_APP_PRIVATE_KEY")


def gh_json(*args: str):
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def build_context(issue: dict) -> str:
    labels = ", ".join(l["name"] for l in issue.get("labels", [])) or "(none)"
    comments = issue.get("comments", []) or []
    thread = "\n\n".join(
        f"--- comment by @{(c.get('author') or {}).get('login', '?')} "
        f"({c.get('createdAt', '')}):\n{c.get('body', '').strip()}"
        for c in comments
    ) or "(no comments yet)"
    return (
        f"# Issue #{issue['number']}: {issue['title']}\n"
        f"Labels: {labels}\n"
        f"URL: {issue.get('url', '')}\n\n"
        f"## Body\n{(issue.get('body') or '(empty)').strip()}\n\n"
        f"## Comment thread (a maintainer reply may hold the authoritative answer)\n{thread}\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, help="issue number")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--summary-out", help="write Claude's final PR-body summary (what it changed / "
                    "verified / to check) here, for the workflow to fold into the PR body")
    args = ap.parse_args()

    issue = gh_json("issue", "view", args.issue,
                    "--json", "number,title,body,labels,comments,url")
    if not issue:
        sys.exit(f"resolve_issue: could not fetch issue #{args.issue}")

    prompt = PROMPT_FILE.read_text(encoding="utf-8") + "\n\n---\n\n" + build_context(issue)

    # Headless Claude on the Max plan; it edits the working tree directly. `--output-format json` lets us
    # capture its final message as the PR-body summary (so a human reviewer sees what changed and why).
    cmd = ["claude", "-p", prompt, "--allowedTools", *ALLOWED_TOOLS,
           "--output-format", "json", "--model", args.model]
    safe_env = {k: v for k, v in os.environ.items() if k not in SCRUB_ENV}
    print(f"resolve_issue: running Claude over issue #{args.issue} (model={args.model}; "
          f"{len(os.environ) - len(safe_env)} credential env vars scrubbed)…")
    r = subprocess.run(cmd, env=safe_env, capture_output=True, text=True)
    # A non-zero from claude is logged but not fatal — the caller decides based on `git status`.
    if r.returncode != 0:
        print(f"::warning::claude exited {r.returncode} for issue #{args.issue}: {(r.stderr or '')[-300:]}")
    summary = ""
    try:
        summary = (json.loads(r.stdout).get("result") or "").strip()
    except (json.JSONDecodeError, AttributeError):
        summary = ""
    if summary:
        print(f"--- Claude summary for #{args.issue} ---\n{summary}\n---")
    if args.summary_out:
        Path(args.summary_out).write_text(summary + "\n" if summary else "")
    sys.exit(0)


if __name__ == "__main__":
    main()
