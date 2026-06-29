#!/usr/bin/env python3
"""Watch the web for NEW OCHA/CERF anticipatory-action frameworks and recent activations.

Discovery via headless Claude Code (Max plan, WebSearch) — the fuzzy counterpart to the
deterministic sweeps. Claude is given our current framework inventory, then web-searches the OCHA
Anticipatory Action portal / CERF AA pages / recent reporting for:
  1. AA **frameworks** (OCHA- or CERF-anticipatory-action, i.e. the kind this team builds) that are
     NOT in our `frameworks/` folder;
  2. AA **activations / triggers / CERF AA disbursements** in roughly the last 60 days that are not
     yet recorded on the relevant framework page.
It writes a markdown report whose FIRST line is `FINDINGS: <n>` (n = count of new items); the caller
posts the rest to the `kb-aa-watch` issue and uses n for the exit code.

Conservative by design: only flag items with a credible source link; when unsure, leave it out and
say so. This flags candidates for a human/`kb-ingest` to act on — it never edits pages itself.

Usage:  python scripts/aa_watch.py [--out aa-report.md] [--model opus] [--dry-run]
Exit:   0 = nothing new (or dry-run) · 2 = ≥1 new framework/activation found
Needs:  claude CLI (Max auth / CLAUDE_CODE_OAUTH_TOKEN), pyyaml.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent


def inventory() -> str:
    """One line per framework version we already have: ISO3 hazard version (status)."""
    rows = []
    for p in sorted((ROOT / "frameworks").rglob("*.md")):
        if p.name in ("_TEMPLATE.md", "README.md"):
            continue
        t = p.read_text(encoding="utf-8")
        if not t.startswith("---"):
            continue
        e = t.find("\n---", 3)
        try:
            fm = yaml.safe_load(t[3:e]) or {}
        except yaml.YAMLError:
            continue
        if fm.get("content_type") != "framework":
            continue
        iso = fm.get("country_iso3"); iso = iso[0] if isinstance(iso, list) else iso
        rows.append(f"  {iso} {fm.get('hazard','?')} {fm.get('version','?')} ({fm.get('status','?')})")
    return "\n".join(sorted(set(rows)))


def build_prompt(out: str, inv: str) -> str:
    return f"""You are a discovery watcher for the OCHA Centre for Humanitarian Data anticipatory-action (AA) knowledge base. Find NEW OCHA/CERF AA frameworks and recent AA activations that we have not captured. Use WebSearch. Be CONSERVATIVE — only report items backed by a credible source URL; when unsure, omit and note it.

OUR CURRENT FRAMEWORK INVENTORY (country_iso3 · hazard · version · status):
{inv}

These are CERF/OCHA-style anticipatory-action frameworks (a pre-agreed trigger releases pre-arranged CERF financing before a shock). IGNORE other agencies' AA (IFRC/Red Cross EAPs, WFP/FAO AA) unless OCHA/CERF is the framework owner — those are out of scope.

TASK:
1. NEW FRAMEWORKS — WebSearch the OCHA Anticipatory Action portal (unocha.org/anticipatory-action), CERF anticipatory-action pages, and recent reporting for OCHA/CERF AA frameworks **launched / endorsed in roughly the last 18 months** for a country+hazard NOT in the inventory above (or a clearly new version of one we have). For each: country, hazard, ~date, and the source URL.
2. RECENT ACTIVATIONS — WebSearch for OCHA/CERF AA **activations / triggers / disbursements in roughly the last 60 days** (e.g. "CERF anticipatory action allocation", "anticipatory action triggered <country>"). For each: country, hazard, ~date, allocation if stated, source URL. Cross-check the inventory — a framework we HAVE that just activated is still worth flagging (its page may not record the activation yet).

OUTPUT — Write a markdown file to {out}. The VERY FIRST LINE must be exactly:
FINDINGS: <n>
where <n> is the total count of new frameworks + new activations you are reporting (0 if none). Then:

# KB AA watch
_What the web shows that the KB may be missing. Verify before acting; this watcher does not edit pages._

## New OCHA/CERF AA frameworks (not in our inventory)
| country | hazard | ~date | source |
|---|---|---|---|
(rows, or "_none found this run_")

## Recent AA activations (~last 60 days)
| country | hazard | ~date | allocation | source | in KB? |
|---|---|---|---|---|---|
(rows; "in KB?" = whether we have a framework page for that country+hazard, or "_none found_")

Write ONLY {out}. Keep it tight; link every claim."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="aa-report.md")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    out = (ROOT / args.out).as_posix() if not Path(args.out).is_absolute() else args.out
    prompt = build_prompt(out, inventory())
    if args.dry_run:
        print("--- DRY RUN ---\n" + prompt[:1600] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "WebSearch Read Write",
           "--permission-mode", "acceptEdits", "--output-format", "json", "--model", args.model]
    print(f"running aa-watch with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")

    rep = Path(out)
    if not rep.exists():
        sys.exit(f"::error::claude finished but {out} was not written.")
    first = rep.read_text(encoding="utf-8").splitlines()[0] if rep.read_text().strip() else ""
    n = 0
    if first.upper().startswith("FINDINGS:"):
        try:
            n = int(first.split(":", 1)[1].strip())
        except ValueError:
            n = 1   # unparseable → surface to be safe
    else:
        n = 1       # missing sentinel → surface to be safe
    print(f"aa-watch: {n} finding(s) → {out}")
    sys.exit(2 if n > 0 else 0)


if __name__ == "__main__":
    main()
