#!/usr/bin/env python3
"""Opus-review a freshly drafted KB page IN PLACE, before the PR is opened.

The interactive ingest (workflows/ingest-systems.mjs) runs an Opus QA agent over each draft.
The headless kb-ingest workflow lost that gate when it switched to "draft → open PR for human
review". This restores it: after a draft is written but BEFORE the PR is created, run Opus over
the changed page(s) to verify against the template + public sources, FIX what it can in place,
and emit a short review summary. The PR then arrives PRE-REVIEWED, so the human reviewer has a
simpler job — read the summary, spot-check, merge. (Keeps ingestion "as simple as possible for
human review.")

Operates on whatever the draft step changed (git working tree), restricted to the KB content
paths the workflow PRs: apps/ pipelines/ frameworks/ infrastructure/deployments.md analysis/.

Usage:  python scripts/ingest_review.py [--model opus] [--summary-out .kb-ingest-review.md] [--dry-run]
Exit:   0 = reviewed (summary written) or nothing to review · non-zero = claude failed
Needs:  claude CLI (Max auth / CLAUDE_CODE_OAUTH_TOKEN), git, pyyaml.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
# the content paths the workflow stages into the PR
CONTENT_PATHS = ["apps/", "pipelines/", "frameworks/", "analysis/", "infrastructure/deployments.md"]


def changed_pages() -> list[str]:
    """Markdown pages with working-tree changes under the KB content paths."""
    r = subprocess.run(["git", "status", "--porcelain", "--", *CONTENT_PATHS],
                       cwd=str(ROOT), capture_output=True, text=True, check=True)
    out = []
    for line in r.stdout.splitlines():
        # porcelain: XY<space>path  (rename shows "orig -> new")
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        if path.endswith(".md"):
            out.append(path)
    return sorted(set(out))


def build_prompt(pages: list[str]) -> str:
    files = "\n".join(f"  - {p}" for p in pages)
    is_fw = any(p.startswith("frameworks/") for p in pages)
    template = "frameworks/_TEMPLATE.md" if is_fw else "pipelines/_TEMPLATE.md (or apps/_TEMPLATE.md, matching the page type)"
    return f"""You are the QA reviewer for the OCHA Centre for Humanitarian Data knowledge base. A page was just
auto-drafted by another Claude run; review it carefully and FIX it IN PLACE before it goes to a human.
Edit ONLY the file(s) below — do NOT create new files, and do NOT touch any other page.

PAGE(S) UNDER REVIEW:
{files}

STEP 0 — LEARN THE SCHEMA. Read in full:
  - {ROOT}/{template}   (EXACT frontmatter fields + body headings)
  - {ROOT}/docs/INGESTION.md   (conventions; one-home-per-fact; document authority & reconciliation; multi-country rule; visibility)

STEP 1 — VERIFY & CORRECT each page (use Edit to fix in place):
  - CONFORMANCE: every template frontmatter field present and correctly typed; every body heading present; no leftover template placeholder text. status/valid_until/all_in set per the INGESTION.md rules.
  - INTERNAL CONSISTENCY: frontmatter agrees with the body (funding totals, n_windows vs the Trigger windows table, activations vs "Historical activations", dates). Fix contradictions.
  - SOURCED CLAIMS: cross-check substantive facts (trigger design, thresholds, funding amounts, activation dates/allocations, implementing agencies, status) against PUBLIC sources with WebSearch — prefer unocha.org, cerf.un.org, reliefweb.int, anticipation-hub.org. Correct anything the draft got wrong; where a claim cannot be sourced, replace the guess with null/[]/{{}} rather than leave an unsupported value, and note it.
  - DISCREPANCIES: ensure real repo-vs-doc disagreements / gaps are captured with the right [stale]/[conflict]/[gap] prefix; remove hedging the evidence doesn't support.
  - YAML PARSE GATE: after editing, confirm each page's frontmatter still parses (python3 -c "import yaml; t=open(PATH).read(); yaml.safe_load(t.split(chr(10)+'---',1)[0].lstrip('-'))").

STEP 2 — SUMMARISE. Your FINAL message is the review summary that goes verbatim into the PR body, so a
human reviewer can merge with confidence. Write GitHub-flavoured markdown, concise, with these sections:
  **Verdict:** one line — ready to merge / needs human attention.
  **Checked:** the key facts you verified and against which sources (with URLs).
  **Changed:** bullets of every correction you made (or "no changes — draft was accurate").
  **Still verify:** bullets of anything a human must confirm (facts you could not source, judgement calls).
Keep it tight. Do not restate the whole page."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="opus")
    ap.add_argument("--summary-out", default=".kb-ingest-review.md",
                    help="where to write the review summary (read into the PR body)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pages = changed_pages()
    if not pages:
        print("no drafted page in the working tree — nothing to review")
        return

    prompt = build_prompt(pages)
    if args.dry_run:
        print(f"would review:\n" + "\n".join(pages) + "\n--- DRY RUN ---\n" + prompt[:1500] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "WebSearch Read Edit",
           "--permission-mode", "acceptEdits", "--add-dir", str(ROOT), "--output-format", "json",
           "--model", args.model]
    print(f"Opus-reviewing {len(pages)} page(s) with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude review failed (rc={r.returncode}): {r.stderr[-500:]}")

    # extract the final text as the review summary
    summary = ""
    try:
        summary = (json.loads(r.stdout).get("result") or "").strip()
    except json.JSONDecodeError:
        summary = r.stdout.strip()
    if not summary:
        summary = "_(Opus review ran but produced no summary — review the diff manually.)_"

    Path(ROOT / args.summary_out).write_text(summary + "\n")
    print(f"wrote review summary to {args.summary_out} ✅")

    # post-review YAML gate (don't open a PR with a broken page)
    for p in pages:
        fp = ROOT / p
        if not fp.exists():
            continue
        t = fp.read_text(); e = t.find("\n---", 3)
        try:
            yaml.safe_load(t[3:e])
        except Exception as ex:
            sys.exit(f"::error::after review, {p} frontmatter doesn't parse: {ex}")
    print("post-review YAML gate passed ✅")


if __name__ == "__main__":
    main()
