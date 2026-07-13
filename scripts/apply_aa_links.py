#!/usr/bin/env python3
"""Apply maintainer replies on the kb-aa-links issue to aa.activation_allocation.

The write half of the confirm flow (propose_aa_links.py is the read half): the proposer
posts gaps + proposed links to the `kb-aa-links` issue; the maintainer replies in plain
language ("confirm", "confirm the Nepal one", "it's actually 22-RR-NPL-53977", "not
CERF-funded — FHRAOC", "ad-hoc"). This script:

  1. finds the open kb-aa-links issue and collects maintainer comments newer than the
     last ✅-marker bot comment (nothing new → exit 0, no tokens burned);
  2. has headless Claude (same pattern as aa_watch.py) interpret the replies against the
     issue body's proposals → a strict-JSON decisions file. Claude only interprets — it
     has no DB access;
  3. deterministically validates each decision (activation exists in aa.actual_activation,
     code exists in the aa.cerf_allocation mirror, country matches) and upserts the valid
     ones into aa.activation_allocation;
  4. posts a ✅ comment listing applied/rejected (the marker that fences the next run).

Issue refresh/close is left to the propose step that runs right after in aa-links.yml.

Usage:  python scripts/apply_aa_links.py [--model sonnet] [--dry-run]
Exit:   0 = applied / nothing to do · 1 = error.
Needs:  gh CLI (GH_TOKEN), claude CLI (CLAUDE_CODE_OAUTH_TOKEN / Max), ocha-stratus
        (dev DB read + WRITE creds), pyyaml. PGSSLMODE=require.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("PGSSLMODE", "require")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_aa_cerf import parse_activations  # noqa: E402
from propose_aa_links import load_links, load_mirror  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LABEL = "kb-aa-links"
MARKER = "✅"


def gh(*args) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])}… failed: {r.stderr[-400:]}")
    return r.stdout


def get_issue():
    """(number, body) of the open kb-aa-links issue, or (None, None)."""
    out = gh("issue", "list", "--label", LABEL, "--state", "open",
             "--json", "number,body", "--limit", "1")
    items = json.loads(out or "[]")
    return (items[0]["number"], items[0]["body"]) if items else (None, None)


def new_user_comments(number) -> list[str]:
    """Maintainer comments newer than the last ✅-marker bot comment."""
    out = gh("issue", "view", str(number), "--json", "comments")
    comments = json.loads(out)["comments"]
    last_marker = max((i for i, c in enumerate(comments)
                       if c["body"].strip().startswith(MARKER)), default=-1)
    return [c["body"] for c in comments[last_marker + 1:]
            if not c["author"]["login"].endswith("[bot]")
            and not c["body"].strip().startswith((MARKER, "🤖"))]


PROMPT = """You are interpreting a maintainer's replies on a curation issue that links CERF
anticipatory-action allocations to AA-framework activations. The issue body below lists the
outstanding gaps, each with ranked candidate allocations and a proposed resolution. The
maintainer's replies are AUTHORITATIVE — your only job is to translate them into structured
decisions. Do not invent decisions for gaps the replies don't address.

Write to the file {out} a JSON array. Each element is one of:
  {{"action": "link", "kb_framework": "<fw>", "event_date": "<date as shown>",
    "application_code": "<code>", "flag": null_or_"SHARED_APP", "note": null_or_string}}
  {{"action": "no_cerf", "kb_framework": "<fw>", "event_date": "<date>", "note": "<how it was funded>"}}
  {{"action": "adhoc", "application_code": "<code>", "note": "<one-line what it was>"}}
  {{"action": "skip", "reason": "<why you couldn't act on part of a reply>"}}

Rules:
- "confirm" with no qualifier = accept every **Proposed:** line in the body.
- A qualified confirm ("confirm the Nepal one") = accept only the matching proposal(s).
- A named code overrides the proposal for that gap.
- kb_framework / event_date / application_code must be copied EXACTLY from the issue body.
- If a reply is ambiguous, emit a skip with the reason — never guess.
- Write ONLY the JSON array to {out}. No prose.

=== ISSUE BODY (the gaps and proposals) ===
{body}

=== MAINTAINER REPLIES (authoritative, oldest first) ===
{replies}
"""


def run_claude(body: str, replies: list[str], out: Path, model: str):
    prompt = PROMPT.format(out=out.as_posix(), body=body,
                           replies="\n\n---\n\n".join(replies))
    cmd = ["claude", "-p", prompt, "--allowedTools", "Read Write",
           "--permission-mode", "acceptEdits", "--output-format", "json", "--model", model]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")
    if not out.exists():
        sys.exit(f"::error::claude finished but {out} was not written.")
    return json.loads(out.read_text())


def validate_and_apply(decisions, dry_run=False):
    """Deterministic gate + upsert. Returns (applied, rejected) description lists."""
    acts = {(a["kb_framework"], a["event_date"]): a
            for a in parse_activations(ROOT / "frameworks")}
    mirror = {a["application_code"]: a for a in load_mirror()}
    applied, rejected, rows = [], [], []

    for d in decisions:
        act = d.get("action")
        if act == "skip":
            rejected.append(f"skipped (Claude): {d.get('reason')}")
            continue
        if act == "link":
            key = (d.get("kb_framework"), d.get("event_date"))
            code = d.get("application_code")
            a, m = acts.get(key), mirror.get(code)
            if a is None:
                rejected.append(f"link {key} → {code}: no such activation in frontmatter")
            elif m is None:
                rejected.append(f"link {key} → {code}: code not in the OneGMS mirror")
            elif a["country_iso3"] and m["country_iso3"] not in a["country_iso3"].split("+"):
                rejected.append(f"link {key} → {code}: country mismatch "
                                f"({a['country_iso3']} vs {m['country_iso3']})")
            else:
                flag = d.get("flag") if d.get("flag") == "SHARED_APP" else None
                rows.append(dict(fw=key[0], ed=key[1], code=code, flag=flag, note=d.get("note")))
                applied.append(f"link `{key[0]}` · {key[1]} → `{code}`"
                               + (" (SHARED_APP)" if flag else ""))
        elif act == "no_cerf":
            key = (d.get("kb_framework"), d.get("event_date"))
            if key not in acts:
                rejected.append(f"no_cerf {key}: no such activation in frontmatter")
            else:
                rows.append(dict(fw=key[0], ed=key[1], code=None, flag="NO_CERF", note=d.get("note")))
                applied.append(f"NO_CERF `{key[0]}` · {key[1]} ({d.get('note') or 'no note'})")
        elif act == "adhoc":
            code = d.get("application_code")
            if code not in mirror:
                rejected.append(f"adhoc {code}: code not in the OneGMS mirror")
            else:
                rows.append(dict(fw=None, ed=None, code=code, flag="ADHOC_AA", note=d.get("note")))
                applied.append(f"ADHOC_AA `{code}` ({d.get('note') or 'no note'})")
        else:
            rejected.append(f"unknown action: {d}")

    if rows and not dry_run:
        import ocha_stratus as stratus
        from sqlalchemy import text
        eng = stratus.get_engine(stage="dev", write=True)
        with eng.begin() as c:
            c.execute(text("""
                insert into aa.activation_allocation
                    (kb_framework, event_date, application_code, flag, note)
                values (:fw, :ed, :code, :flag, :note)
                on conflict (coalesce(kb_framework,''), coalesce(event_date,''),
                             coalesce(application_code,''))
                do update set flag = excluded.flag, note = excluded.note, updated_at = now()
            """), rows)
    return applied, rejected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--dry-run", action="store_true", help="interpret + validate; no DB write, no comment")
    args = ap.parse_args()

    number, body = get_issue()
    if number is None:
        print("no open kb-aa-links issue — nothing to apply")
        return
    replies = new_user_comments(number)
    if not replies:
        print(f"issue #{number}: no new maintainer replies since the last {MARKER} marker")
        return

    print(f"issue #{number}: {len(replies)} new repl{'y' if len(replies) == 1 else 'ies'} — interpreting…")
    out = Path("/tmp/aa-links-decisions.json")
    out.unlink(missing_ok=True)
    decisions = run_claude(body, replies, out, args.model)
    applied, rejected = validate_and_apply(decisions, dry_run=args.dry_run)

    lines = [f"{MARKER} Applied {len(applied)} decision(s) from your repl"
             f"{'y' if len(replies) == 1 else 'ies'}:"] if applied else \
            [f"{MARKER} No decisions applied from your repl{'y' if len(replies) == 1 else 'ies'}."]
    lines += [f"- {a}" for a in applied]
    if rejected:
        lines.append("\nNot applied (needs another reply):")
        lines += [f"- {r}" for r in rejected]
    comment = "\n".join(lines)
    print(comment)
    if not args.dry_run:
        subprocess.run(["gh", "issue", "comment", str(number), "--body", comment],
                       capture_output=True, text=True, timeout=60)


if __name__ == "__main__":
    main()
