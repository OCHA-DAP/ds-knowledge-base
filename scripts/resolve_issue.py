#!/usr/bin/env python3
"""Attempt to resolve ONE GitHub issue — or revise ONE PR — with headless Claude (Max plan).

Issue mode (--issue N): fetches the issue + its full comment thread, hands them to `claude -p`
together with the KB conventions (scripts/kb_steward_prompt.md), and lets Claude edit the repo
in place. The caller (`.github/workflows/kb-steward.yml`) turns any resulting working-tree
change into a PR that closes the issue.

PR mode (--pr N): the working tree is already checked out on the PR's HEAD branch; fetches the
PR (title/body/diff), its conversation comments AND inline review comments, and lets Claude
apply the maintainers' feedback to the branch. The caller commits/pushes to the same branch.

Either way this script makes **no git commits** — it only edits files (or leaves the tree
clean if Claude can't confidently act).

Usage:  python scripts/resolve_issue.py (--issue 123 | --pr 456) [--model opus]
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


DIFF_CAP = 60_000   # chars of `gh pr diff` fed to Claude; beyond this it reads files itself


def build_pr_context(pr: dict, num: str) -> str:
    thread = "\n\n".join(
        f"--- comment by @{(c.get('author') or {}).get('login', '?')} "
        f"({c.get('createdAt', '')}):\n{c.get('body', '').strip()}"
        for c in (pr.get("comments") or [])
    ) or "(no conversation comments)"
    # inline review comments live on the pulls API, not in `gh pr view`
    inline = gh_json("api", f"repos/{{owner}}/{{repo}}/pulls/{num}/comments") or []
    inline_txt = "\n\n".join(
        f"--- inline comment by @{(c.get('user') or {}).get('login', '?')} "
        f"on `{c.get('path', '?')}` line {c.get('line') or c.get('original_line', '?')}:\n"
        f"{(c.get('body') or '').strip()}"
        for c in inline
    ) or "(no inline review comments)"
    d = subprocess.run(["gh", "pr", "diff", num], capture_output=True, text=True)
    diff = (d.stdout or "")[:DIFF_CAP]
    if len(d.stdout or "") > DIFF_CAP:
        diff += "\n… (diff truncated — read the files in the working tree for the rest)"
    return (
        f"# PR #{pr['number']} (REVISION REQUEST): {pr['title']}\n"
        f"URL: {pr.get('url', '')}\n\n"
        f"## PR body\n{(pr.get('body') or '(empty)').strip()}\n\n"
        f"## Current diff vs base\n```diff\n{diff}\n```\n\n"
        f"## Conversation comments (the LATEST maintainer comment is the work request)\n{thread}\n\n"
        f"## Inline review comments\n{inline_txt}\n\n"
        "## PR-REVISION MODE — how this differs from an issue\n"
        "The working tree IS this PR's branch, already checked out. Your job is to APPLY the\n"
        "maintainers' feedback to it — revise the draft, don't start over.\n"
        "- You may move/rename/delete files this PR itself ADDED (e.g. reclassify a page to another\n"
        "  content type, fixing the frontmatter and body to that type's _TEMPLATE). Never delete a\n"
        "  file that exists on main.\n"
        "- Keep everything else about the draft that the feedback doesn't dispute.\n"
        "- If the feedback is a question rather than a change request, make no edits and ANSWER it.\n"
        "- Your final message is posted as a PR comment: state briefly what you changed and why, or\n"
        "  your answer / what you need.\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--issue", help="issue number")
    g.add_argument("--pr", help="PR number (revision mode: working tree = the PR's HEAD branch)")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--summary-out", help="write Claude's final PR-body summary (what it changed / "
                    "verified / to check) here, for the workflow to fold into the PR body")
    args = ap.parse_args()

    if args.pr:
        pr = gh_json("pr", "view", args.pr,
                     "--json", "number,title,body,comments,url,headRefName")
        if not pr:
            sys.exit(f"resolve_issue: could not fetch PR #{args.pr}")
        context, target = build_pr_context(pr, args.pr), f"PR #{args.pr}"
    else:
        issue = gh_json("issue", "view", args.issue,
                        "--json", "number,title,body,labels,comments,url")
        if not issue:
            sys.exit(f"resolve_issue: could not fetch issue #{args.issue}")
        context, target = build_context(issue), f"issue #{args.issue}"

    prompt = PROMPT_FILE.read_text(encoding="utf-8") + "\n\n---\n\n" + context

    # Headless Claude on the Max plan; it edits the working tree directly. `--output-format json` lets us
    # capture its final message as the PR-body summary (so a human reviewer sees what changed and why).
    cmd = ["claude", "-p", prompt, "--allowedTools", *ALLOWED_TOOLS,
           "--output-format", "json", "--model", args.model]
    safe_env = {k: v for k, v in os.environ.items() if k not in SCRUB_ENV}
    print(f"resolve_issue: running Claude over {target} (model={args.model}; "
          f"{len(os.environ) - len(safe_env)} credential env vars scrubbed)…")
    r = subprocess.run(cmd, env=safe_env, capture_output=True, text=True)
    # A non-zero from claude is logged but not fatal — the caller decides based on `git status`.
    if r.returncode != 0:
        print(f"::warning::claude exited {r.returncode} for {target}: {(r.stderr or '')[-300:]}")
    summary = ""
    try:
        summary = (json.loads(r.stdout).get("result") or "").strip()
    except (json.JSONDecodeError, AttributeError):
        summary = ""
    if summary:
        print(f"--- Claude summary for {target} ---\n{summary}\n---")
    if args.summary_out:
        Path(args.summary_out).write_text(summary + "\n" if summary else "")
    sys.exit(0)


if __name__ == "__main__":
    main()
