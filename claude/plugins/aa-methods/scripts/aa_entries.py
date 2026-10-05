#!/usr/bin/env python3
"""Send an entries file to the AA tracking database NOW, through the ds-aa-tracking proxy.

The proxy's POST /entries applies the file in one transaction with the same item format
as ds-aa-tracking's scripts/apply_entries.py (upsert / op: delete / op: replace). The
database enforces the rules — a sealed backtest refuses every change, simulated years must
lie inside their window's analysis span — so a bad file fails as a whole and nothing is
written. This client only carries the file; the semantics live in ds-aa-tracking.

    python aa_entries.py FILE            # dry run: checked against the live DB, rolled back
    python aa_entries.py FILE --write    # apply

Needs the tracking site's EDITOR token (the one the admin page asks for): env
AA_TRACKING_EDITOR_TOKEN, or the file ~/.config/ds-aa-tracking/editor-token (chmod 600).
Standard library only, so it runs from any repo. Proxy URL: env AA_TRACKING_PROXY.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROXY = os.environ.get("AA_TRACKING_PROXY", "https://chd-ds-aa-extract.azurewebsites.net")
TOKEN_FILE = Path.home() / ".config" / "ds-aa-tracking" / "editor-token"


def token():
    t = os.environ.get("AA_TRACKING_EDITOR_TOKEN") or (
        TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")
    if not t:
        sys.exit(f"no editor token: set AA_TRACKING_EDITOR_TOKEN or write it to {TOKEN_FILE} "
                 "(the token the tracking admin page asks for)")
    return t


def show(row, keys=None):
    cols = keys or list(row)
    return ", ".join(f"{c}={row[c]}" for c in cols if row.get(c) is not None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file")
    ap.add_argument("--write", action="store_true", help="apply (default: dry run)")
    a = ap.parse_args()
    payload = json.loads(Path(a.file).read_text())
    if not str(payload.get("entered_by") or "").strip() or not payload.get("rows"):
        sys.exit("the file needs 'entered_by' (who, from what) and 'rows'")
    payload["dry_run"] = not a.write
    req = urllib.request.Request(
        f"{PROXY}/entries", data=json.dumps(payload).encode(), method="POST",
        headers={"content-type": "application/json", "x-editor-token": token()})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body)
            msg = err.get("error", body) + (f"\nhint: {err['hint']}" if err.get("hint") else "")
        except ValueError:
            msg = body[:500]
        sys.exit(f"REFUSED ({e.code}) — nothing written:\n{msg}")
    for it in out["plan"]:
        if it["op"] == "replace":
            print(f"replace aa.{it['table']} {show(it['scope'])}: "
                  f"{len(it['before'])} row(s) out, {len(it['after'])} in")
            for b in it["before"]:
                print("   -", show(b, [k for k in b if k not in ("country_iso3", "hazard", "version")]))
            for r in it["after"]:
                print("   +", show(r, [k for k in r if k not in ("country_iso3", "hazard", "version")]))
        elif it["op"] == "update":
            changed = {k: v for k, v in it["after"].items() if str(it["before"].get(k)) != str(v)}
            print(f"update aa.{it['table']} {show(it['key'])}: "
                  + (", ".join(f"{k} {it['before'].get(k)} -> {v}" for k, v in changed.items())
                     or "no change"))
        elif it["op"] == "insert":
            print(f"insert aa.{it['table']} {show(it['key'])}")
        else:
            print(f"delete aa.{it['table']} {show(it['key'])}"
                  + ("" if it.get("before") else " (already absent)"))
    print(f"\n{out['items']} item(s) — " + ("APPLIED to the database." if out["applied"] else
          "dry run: every check passed against the live database; nothing written "
          "(--write to apply)."))


if __name__ == "__main__":
    main()
