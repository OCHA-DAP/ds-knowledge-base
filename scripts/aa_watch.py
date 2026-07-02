#!/usr/bin/env python3
"""Watch the web for NEW OCHA/CERF anticipatory-action frameworks and recent activations.

Discovery via headless Claude Code (Max plan, WebFetch + WebSearch). Grounded on a **deterministic
backbone** — it WebFetches the authoritative CERF AA portfolio sources (`CERF_SOURCES`: the portal +
the portfolio-update PDF) and enumerates the framework list from those, using CERF's published count
(~19–20 frameworks / 16–17 countries) as a completeness check, rather than free-searching from memory.
Given our current framework inventory, it then reports:
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

# Authoritative CERF AA portfolio sources — the deterministic BACKBONE the watcher enumerates from
# (rather than free-searching). CERF reports ~19–20 frameworks across ~16–17 countries — a built-in
# completeness check. Update if CERF moves these.
CERF_SOURCES = [
    "https://cerf.un.org/anticipatory-action",                                          # portal (framework list)
    "https://cerf.un.org/sites/default/files/resources/CERF_AA_Portfolio_Update.pdf",   # portfolio update
    "https://cerf.un.org/sites/default/files/resources/CERF_Atforefront_AA.pdf",        # at-the-forefront
]


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
        iso = fm.get("country_iso3")
        iso = ",".join(str(x) for x in iso) if isinstance(iso, list) else iso  # multi-country: list ALL
        rows.append(f"  {iso} {fm.get('hazard','?')} {fm.get('version','?')} ({fm.get('status','?')})")
    return "\n".join(sorted(set(rows)))


def build_prompt(out: str, inv: str) -> str:
    cerf_sources = "\n".join(f"  - {u}" for u in CERF_SOURCES)
    return f"""You are a discovery watcher for the OCHA Centre for Humanitarian Data anticipatory-action (AA) knowledge base. Find NEW OCHA/CERF AA frameworks and recent AA activations that we have not captured. Be CONSERVATIVE — only report items backed by a credible source URL; when unsure, omit and note it.

OUR CURRENT FRAMEWORK INVENTORY (country_iso3 · hazard · version · status):
{inv}

OWNERSHIP GATE — strict. In scope ONLY: an **OCHA-facilitated, CERF-financed AA framework** (a pre-agreed trigger releases **CERF pre-arranged** financing, with an OCHA Humanitarian Coordinator / CERF framework doc). For EACH framework you report, you MUST be able to cite a CERF/OCHA source confirming CERF pre-arranged financing — if you cannot, OMIT it (don't guess).
EXCLUDE (these are NOT OCHA frameworks, even when OCHA/CHD does supporting work):
  - **IFRC / Red Cross Early Action Protocols (EAPs)** — e.g. the framework that **triggered** in Kenya (Sep 2025) is the **KRCS EAP2022KE02**, an IFRC EAP — its activation is the Red Cross's, NOT OCHA's. (OCHA does have its own Kenya drought framework, but it is **in development**; never credit an IFRC EAP's activation to an OCHA framework.)
  - **FAO / WFP / government** anticipatory/early action.
  - **plain CERF allocations** (rapid-response, underfunded-emergency, top-ups) that are NOT a triggered AA-framework release — e.g. a one-off **CERF drought top-up to Timor-Leste** is an allocation, not an AA framework.
When in doubt about ownership, OMIT and add a one-line "lower-confidence, verify" note rather than reporting it as a framework.

BACKBONE — START HERE. **WebFetch these authoritative CERF portfolio sources and build the full framework list from them** (do NOT enumerate from memory or free search):
{cerf_sources}
CERF reports its AA portfolio at roughly **19–20 frameworks across 16–17 countries** — use that as a COMPLETENESS CHECK: if your enumerated list is far short, fetch/search more before concluding. Supplement with the OCHA portal (unocha.org/anticipatory-action) and WebSearch only to fill gaps the CERF sources leave.

TASK:
1. MISSING FRAMEWORKS (FULL PORTFOLIO — any age) — diff the CERF portfolio list (from the backbone above) against the inventory. List EVERY country+hazard AA framework OCHA/CERF has established that is NOT in the inventory — **including older pilots** (the 2020–21 cohort) and new versions. For each: country, hazard, ~date/era, whether it ever activated, and the source URL. (A historical pilot the DS team may not have modelled is still worth flagging for a human to scope in/out.)
2. MISSING VERSIONS — NEWER *or* older (a framework = the country+hazard combo, so a new version supersedes; there's never a second framework for the same country+hazard). Frameworks are revised ~annually, so for the country+hazard frameworks we DO hold, check the OCHA/ReliefWeb/CERF publication history for BOTH: (a) **a NEWER published version than the one we hold** — this is the common miss: e.g. we hold `COD · cholera · 2025-03-11` but OCHA published a revised DRC cholera framework dated June 2026 — the newer version SUPERSEDES ours and we're stale, so **flag it**; and (b) **earlier/intermediate versions we're missing** (e.g. we hold ETH drought 2020 + 2026 but maybe not the 2021–2025 revisions). Match on the inventory's `country_iso3 · hazard` (NOT the folder slug — DRC cholera lives under `cod-infectious-disease`), and compare the latest published date against the version date(s) we list. Note the multi-country `SLV,GTM,HND` line is ONE framework covering all three (not three gaps).

3. RECENT ACTIVATIONS — WebSearch for OCHA/CERF AA **activations / triggers / disbursements in roughly the last 60 days** (e.g. "CERF anticipatory action allocation", "anticipatory action triggered <country>"). For each: country, hazard, ~date, allocation if stated, source URL. Cross-check the inventory — a framework we HAVE that just activated is still worth flagging (its page may not record the activation yet).

OUTPUT — Write a markdown file to {out}. The VERY FIRST LINE must be exactly:
FINDINGS: <n>
where <n> is the total count of (missing frameworks + missing versions [newer or older] + new activations) you are reporting (0 if none). Then:

# KB AA watch
_What the web shows that the KB may be missing. Verify before acting; this watcher does not edit pages._

## OCHA/CERF AA frameworks missing from our inventory (any age)
| country | hazard | ~date/era | ever activated? | source |
|---|---|---|---|---|
(rows, or "_none found this run_")

## Missing versions of frameworks we hold (NEWER = we're stale/superseded · older = back-catalogue)
| framework (country/hazard) | version we lack | ~date | newer or older? | source |
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

    cmd = ["claude", "-p", prompt, "--allowedTools", "WebSearch WebFetch Read Write",
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
