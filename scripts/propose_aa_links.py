#!/usr/bin/env python3
"""Propose CERF-allocation links for AA activations that aren't curated yet (D77c).

The deterministic auto-proposer sitting between aa-watch (discovers activations → they get
recorded in framework frontmatter) and the curated `scripts/aa_cerf_links.csv` (the ground
truth `load_aa_cerf.py` loads). It recomputes the loader's gap report against the
**`aa.cerf_allocation` OneGMS mirror** — refreshed daily by ds-cerf-supplement's
refresh-mirror workflow — so the moment a new activation lands in frontmatter (or a new AA
allocation appears in the feed), the gap shows up with ranked candidates and a paste-ready
CSV row. It proposes; it never edits the CSV — a human pastes the row, and the aa-links
workflow re-runs the loader on push.

Reports two gap kinds (same definitions as load_aa_cerf.report_gaps):
  1. UNLINKED activations — in frontmatter, but no CSV row (neither linked nor NO_CERF).
     Candidates: mirror allocations matching country, Rapid Response, ranked AA-keyword
     first then month-distance (an AA application is often endorsed months BEFORE the
     trigger; FirstProjectApprovedDate ≈ disbursement, so distance uses the nearer of the
     two dates).
  2. ORPHAN AA-keyword allocations — in the mirror with an anticipatory/early-action title,
     but neither linked nor curated ADHOC_AA. Proposes the nearest activation, else an
     ADHOC_AA row.

Output: markdown report whose FIRST line is `FINDINGS: <n>`; the aa-links workflow posts
the rest to the `kb-aa-links` tracking issue and closes it when clean.

Usage:  python scripts/propose_aa_links.py [--out report.md] [--links PATH]
Exit:   0 = fully curated · 2 = ≥1 gap · 1 = error (DB unreachable etc.)
Needs:  ocha-stratus (dev DB read: DSCI_AZ_DB_DEV_HOST/_UID/_PW, PGSSLMODE=require), pyyaml.
"""
from __future__ import annotations
import argparse
import csv
import os
import sys
from datetime import date, datetime
from pathlib import Path

os.environ.setdefault("PGSSLMODE", "require")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_aa_cerf import LINKS_CSV, _ym, parse_activations  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MAX_CANDIDATES = 5
NEAR_MONTHS = 6          # non-keyword allocations only count as candidates within this window
ORPHAN_NEAR_MONTHS = 9   # an orphan allocation proposes an activation within this window


def cerf_url(code: str, year) -> str:
    return f"https://cerf.un.org/what-we-do/allocation/{year}/summary/{code}"


def load_mirror():
    """All allocations from the aa.cerf_allocation mirror (list of dicts)."""
    import ocha_stratus as stratus
    from sqlalchemy import text
    q = """select application_code, year, country_iso3, country_name, window_name,
                  emergency_type, title, aa_keyword, amount_approved,
                  erc_endorsement_date, first_project_approved_date
           from aa.cerf_allocation"""
    with stratus.get_engine(stage="dev").connect() as c:
        rows = [dict(r._mapping) for r in c.execute(text(q))]
    if not rows:
        sys.exit("aa.cerf_allocation is empty — has the refresh-mirror workflow run?")
    return rows


def load_links(path: Path):
    """(linked act keys, NO_CERF act keys, used codes, ADHOC_AA codes) from the curated CSV."""
    linked, no_cerf, used, adhoc = set(), set(), set(), set()
    for r in csv.DictReader(open(path)):
        code = (r.get("application_code") or "").strip()
        if not r["kb_framework"]:
            adhoc.add(code)
            continue
        key = (r["kb_framework"], r["event_date"])
        (linked if code else no_cerf).add(key)
        if code:
            used.add(code)
    return linked, no_cerf, used, adhoc


def month_dist(d, eym) -> int | None:
    """Distance in months between a date (or None) and an (y, m) tuple."""
    if d is None or eym is None:
        return None
    if isinstance(d, datetime):
        d = d.date()
    return abs((d.year - eym[0]) * 12 + d.month - eym[1])


def alloc_dist(a, eym) -> int:
    """Nearest month-distance over the allocation's endorsement/first-project dates.
    AA applications are often pre-arranged well before the trigger fires, so take the
    minimum; 999 when the allocation has no usable date."""
    ds = [month_dist(a["erc_endorsement_date"], eym), month_dist(a["first_project_approved_date"], eym)]
    ds = [x for x in ds if x is not None]
    return min(ds) if ds else 999


def candidates_for(act, allocs, used):
    """Ranked mirror candidates for an unlinked activation."""
    isos = (act["country_iso3"] or "").split("+")
    eym = _ym(act["event_date"])
    out = []
    for a in allocs:
        if a["window_name"] != "Rapid Response":
            continue
        if act["country_iso3"] and a["country_iso3"] not in isos:
            continue
        d = alloc_dist(a, eym)
        if not a["aa_keyword"] and d > NEAR_MONTHS:
            continue
        out.append((not a["aa_keyword"], a["application_code"] in used, d, a))
    out.sort(key=lambda t: t[:3])
    return out[:MAX_CANDIDATES]


def fmt_alloc(a, dist=None, reused=False) -> str:
    amt = f"${float(a['amount_approved']) / 1e6:.1f}M" if a["amount_approved"] else "—"
    bits = [
        f"[`{a['application_code']}`]({cerf_url(a['application_code'], a['year'])})",
        f"{a['year']}", amt,
        f"endorsed {a['erc_endorsement_date'] or '?'}",
        f"first-proj {a['first_project_approved_date'] or '?'}",
    ]
    if a["aa_keyword"]:
        bits.append("**AA-keyword**")
    if dist is not None and dist != 999:
        bits.append(f"±{dist}mo")
    if reused:
        bits.append("_already linked elsewhere — SHARED_APP?_")
    title = (a["title"] or "")[:90]
    return " · ".join(bits) + f"\n  {title}"


def build_report(acts, allocs, linked, no_cerf, used, adhoc) -> tuple[int, str]:
    unlinked = [a for a in acts if (a["kb_framework"], a["event_date"]) not in linked | no_cerf]
    by_code = {a["application_code"]: a for a in allocs}
    orphans = [a for a in allocs
               if a["aa_keyword"] and a["application_code"] not in used | adhoc]
    n = len(unlinked) + len(orphans)

    L = [f"FINDINGS: {n}"]
    L.append(f"_Generated {date.today()} from framework frontmatter + `scripts/aa_cerf_links.csv` "
             f"+ the `aa.cerf_allocation` OneGMS mirror ({len(allocs)} allocations, refreshed daily "
             f"by [ds-cerf-supplement](https://github.com/OCHA-DAP/ds-cerf-supplement)). "
             f"Deterministic gap report — candidates are ranked suggestions, not decisions._\n")

    if unlinked:
        L.append(f"## Unlinked activations ({len(unlinked)})\n")
        L.append("Recorded in framework frontmatter but not yet in `aa_cerf_links.csv`.\n")
        for act in sorted(unlinked, key=lambda a: (a["kb_framework"], a["event_date"])):
            fw, ed = act["kb_framework"], act["event_date"]
            L.append(f"### `{fw}` · {ed} ({act['country_iso3'] or '?'}"
                     + (f", {act['window_name']}" if act.get("window_name") else "") + ")")
            cands = candidates_for(act, allocs, used)
            if cands:
                L.append("Candidates from the mirror:")
                for _, reused, d, a in cands:
                    L.append(f"- {fmt_alloc(a, d, reused)}")
                top = cands[0][3]["application_code"]
                L.append("\nPaste into `scripts/aa_cerf_links.csv` (top candidate pre-filled — check it!):")
                L.append(f"```csv\n{fw},{ed},{top},,\n```")
            else:
                L.append("_No mirror candidate (country + Rapid Response + AA-keyword-or-near-date). "
                         "The allocation may not be published yet — or the activation wasn't CERF-funded._")
            L.append(f"_Not CERF-funded? add:_ `{fw},{ed},,NO_CERF,<how it was funded>`\n")

    if orphans:
        L.append(f"## Orphan AA-keyword allocations ({len(orphans)})\n")
        L.append("Anticipatory/early-action titles in the mirror, neither linked to an activation "
                 "nor curated `ADHOC_AA`.\n")
        for a in sorted(orphans, key=lambda x: x["application_code"]):
            code = a["application_code"]
            L.append(f"- {fmt_alloc(a)}")
            eyms = [(alloc_dist(a, _ym(act["event_date"])), act)
                    for act in acts
                    if a["country_iso3"] in (act["country_iso3"] or "").split("+")]
            near = sorted(eyms, key=lambda t: t[0])
            if near and near[0][0] <= ORPHAN_NEAR_MONTHS:
                d, act = near[0]
                L.append(f"  Nearest activation: `{act['kb_framework']}` · {act['event_date']} (±{d}mo) → "
                         f"`{act['kb_framework']},{act['event_date']},{code},,`")
            else:
                L.append(f"  No nearby activation → likely ad-hoc: `,,{code},ADHOC_AA,<why no framework>`")
        L.append("")

    if n:
        L.append("## How to resolve")
        L.append("1. Edit `scripts/aa_cerf_links.csv` — the rows above are paste-ready "
                 "(verify against the linked CERF pages first).")
        L.append("2. Push — the `aa-links` workflow re-runs `load_aa_cerf.py` and refreshes/closes "
                 "this issue automatically.")
        L.append("\nLocal double-check: `python scripts/load_aa_cerf.py --propose`. New activations "
                 "are discovered by the weekly `kb-aa-watch` issue; once ingested into frontmatter "
                 "they appear here with mirror candidates.")
    else:
        L.append("Fully curated — every activation is linked (or NO_CERF) and every AA-keyword "
                 "allocation is linked or ADHOC_AA. ✓")
    return n, "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write the report here (default: stdout)")
    ap.add_argument("--links", default=str(LINKS_CSV))
    args = ap.parse_args()

    acts = parse_activations(ROOT / "frameworks")
    allocs = load_mirror()
    linked, no_cerf, used, adhoc = load_links(Path(args.links))
    n, report = build_report(acts, allocs, linked, no_cerf, used, adhoc)

    if args.out:
        Path(args.out).write_text(report)
        print(f"{n} gap(s) -> {args.out}")
    else:
        print(report)
    sys.exit(2 if n else 0)


if __name__ == "__main__":
    main()
