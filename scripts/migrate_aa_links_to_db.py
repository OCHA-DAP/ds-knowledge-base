#!/usr/bin/env python3
"""One-off: move the curated activation↔allocation crosswalk from scripts/aa_cerf_links.csv
into aa.activation_allocation (DB-as-source), and finish the pure-OneGMS-mirror split.

In one transaction:
  1. drop the aa.v_* views + the old NOT-NULL activation_allocation table;
  2. recreate the new-shape table + views (DDL imported from load_aa_cerf.py);
  3. insert every CSV row in its native kind:
       link     kb_framework, event_date, application_code [, SHARED_APP]
       NO_CERF  kb_framework, event_date, code=NULL
       ADHOC_AA kb_framework/event_date=NULL, application_code
  4. drop aa_adhoc / aa_note from aa.cerf_allocation → the mirror is now PURE feed columns
     (+ deterministic aa_keyword), owned entirely by ds-cerf-supplement's refresh_mirror.py.

Afterwards: `git rm scripts/aa_cerf_links.csv` (history keeps it); curation happens via the
kb-aa-links issue (propose_aa_links.py → your reply → apply_aa_links.py).

Run:  python scripts/migrate_aa_links_to_db.py [--dry-run]
"""
from __future__ import annotations
import argparse
import csv
import os
import sys
from pathlib import Path

os.environ.setdefault("PGSSLMODE", "require")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_aa_cerf import DDL  # noqa: E402  (new-shape table + views)

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "scripts" / "aa_cerf_links.csv"


def read_rows():
    rows = []
    for r in csv.DictReader(open(CSV)):
        code = (r.get("application_code") or "").strip() or None
        fw = (r.get("kb_framework") or "").strip() or None
        ed = (r.get("event_date") or "").strip() or None
        flag = (r.get("flag") or "").strip() or None
        note = (r.get("note") or "").strip() or None
        if fw and not code:
            flag = "NO_CERF"
        elif code and not fw:
            flag = "ADHOC_AA"
        rows.append(dict(kb_framework=fw, event_date=ed, application_code=code,
                         flag=flag, note=note))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CSV.exists():
        sys.exit(f"{CSV} not found — already migrated?")
    rows = read_rows()
    kinds = {"link": 0, "NO_CERF": 0, "ADHOC_AA": 0}
    for r in rows:
        kinds["NO_CERF" if r["flag"] == "NO_CERF" else
              "ADHOC_AA" if r["flag"] == "ADHOC_AA" else "link"] += 1
    print(f"CSV: {len(rows)} rows — {kinds['link']} links, {kinds['NO_CERF']} NO_CERF, "
          f"{kinds['ADHOC_AA']} ADHOC_AA")
    if args.dry_run:
        for r in rows:
            print("  ", r)
        return

    import ocha_stratus as stratus
    from sqlalchemy import text

    eng = stratus.get_engine(stage="dev", write=True)
    with eng.begin() as c:
        c.execute(text("drop view if exists aa.v_aa_allocation"))
        c.execute(text("drop view if exists aa.v_activation_funding"))
        c.execute(text("drop table if exists aa.activation_allocation"))
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        c.execute(text(
            "insert into aa.activation_allocation "
            "(kb_framework, event_date, application_code, flag, note) "
            "values (:kb_framework, :event_date, :application_code, :flag, :note)"), rows)
        c.execute(text("alter table aa.cerf_allocation drop column if exists aa_adhoc"))
        c.execute(text("alter table aa.cerf_allocation drop column if exists aa_note"))
        n = c.execute(text("select count(*) from aa.activation_allocation")).scalar()
        if n != len(rows):
            raise RuntimeError(f"row count mismatch: {n} in DB vs {len(rows)} in CSV")
    with eng.connect() as c:
        v = c.execute(text("select count(*) from aa.v_aa_allocation")).scalar()
        f = c.execute(text("select count(*) from aa.v_activation_funding")).scalar()
    print(f"migrated ✓  activation_allocation={len(rows)} · v_aa_allocation={v} rows · "
          f"v_activation_funding={f} rows · aa_adhoc/aa_note dropped from the mirror")
    print(f"now: git rm {CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
