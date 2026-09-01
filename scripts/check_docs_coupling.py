#!/usr/bin/env python3
"""PR-time docs-coupling nudge: machinery changed → did its doc change too?

The Aug-2026 freshness sweep (PR #521) found the dominant drift mode was
ship-the-feature-forget-the-docs: workflows, MCP server code, and plugins all
changed without the meta-doc that describes them. The drift detectors only
notice *afterwards* (weekly/monthly); this closes the loop at the moment the
change is made, when the author still has the context.

Given the list of files a PR changes, checks each machinery path against the
path→doc map below. If a machinery area changed and none of its mapped docs
did, prints a markdown reminder (for a **non-blocking** PR comment). Prints
nothing when clean. ALWAYS exits 0 — this is a nudge, not a gate (a PR can
legitimately not need doc changes; the author judges).

Usage:  git diff --name-only origin/main...HEAD | python scripts/check_docs_coupling.py
        python scripts/check_docs_coupling.py file1 file2 ...
"""
from __future__ import annotations
import sys

# area-prefix(es) → the docs that describe that area (any one changing satisfies it).
COUPLING: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = [
    ("GitHub Actions workflows",
     (".github/workflows/",),
     ("infrastructure/automation.md",)),
    ("the MCP server",
     ("mcp_server/",),
     ("infrastructure/mcp-connectors.md", "infrastructure/usage.md", "mcp_server/README.md",
      "mcp_server/DEPLOY.md")),
    ("the ds-team plugins",
     ("claude/", ".claude-plugin/"),
     ("claude/README.md", "docs/USING.md")),
    ("scripts (generators / detectors / ingest)",
     ("scripts/",),
     ("scripts/README.md",)),
]


def main() -> None:
    changed = [a for a in sys.argv[1:]] or [ln.strip() for ln in sys.stdin if ln.strip()]
    changed_set = set(changed)
    reminders = []
    for label, prefixes, docs in COUPLING:
        hits = sorted({f for f in changed
                       if any(f.startswith(p) for p in prefixes) and f not in docs})
        if hits and not (changed_set & set(docs)):
            shown = ", ".join(f"`{h}`" for h in hits[:5]) + (" …" if len(hits) > 5 else "")
            wants = " / ".join(f"`{d}`" for d in docs)
            reminders.append(f"- **{label}** changed ({shown}) but none of {wants} did.")
    if reminders:
        print("<!-- docs-coupling -->")
        print("**Docs check** — this PR touches machinery whose describing doc didn't change:\n")
        print("\n".join(reminders))
        print("\nIf the docs genuinely don't need an update (internal refactor, comment fix), "
              "ignore this — it's a reminder, not a gate. Capture-as-you-go: the author has "
              "the context now; the drift bots only catch it weeks later.")


if __name__ == "__main__":
    main()
