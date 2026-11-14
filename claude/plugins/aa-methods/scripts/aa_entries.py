#!/usr/bin/env python3
"""Look up a framework's versions, and write a backtest to the AA tracking database NOW —
through the ds-aa-tracking proxy, from any repo.

    python aa_entries.py --versions UGA            # every framework version registered for UGA
    python aa_entries.py --versions HTI/storm      # one framework: status, role, seal, backtest
    python aa_entries.py FILE                      # dry run: checked on the live DB, rolled back
    python aa_entries.py FILE --write              # apply (a development version)
    python aa_entries.py FILE --write --endorsed HTI/storm/2024-08-23
                                                   # apply to an ENDORSED version: name it
    ... --endorsed KEY --seal "document link + page"   # and seal it (with or without FILE)

FILE is an entries file (the format of ds-aa-tracking's scripts/apply_entries.py: rows to
upsert, "delete" by full key, "op": "replace" of a version's rows). The proxy applies it in
one transaction and the database enforces the rules, so a bad file fails as a whole:
  - the version must be registered (aa.framework_version) — the label must match exactly;
  - an ENDORSED version is written only when --endorsed names it (and --endorsed naming a
    version in development is refused): work on a revision can't land on the endorsed record;
  - a SEALED backtest is refused — corrections to those are errata (a PR in ds-aa-tracking);
  - every simulated year lies inside its window's analysis span.
Every reply starts with the TARGET: which version(s) the file touches and their state.

Needs the tracking site's EDITOR token (the one its admin page asks for): env
AA_TRACKING_EDITOR_TOKEN, or ~/.config/ds-aa-tracking/editor-token (chmod 600).
Standard library only. Proxy URL: env AA_TRACKING_PROXY.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROXY = os.environ.get("AA_TRACKING_PROXY", "https://chd-ds-aa-extract.azurewebsites.net")
TOKEN_FILE = Path.home() / ".config" / "ds-aa-tracking" / "editor-token"
KEY_COLS = ("country_iso3", "hazard", "version")


def token():
    t = os.environ.get("AA_TRACKING_EDITOR_TOKEN") or (
        TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")
    if not t:
        sys.exit(f"no editor token: set AA_TRACKING_EDITOR_TOKEN or write it to {TOKEN_FILE} "
                 "(the token the tracking admin page asks for)")
    return t


def call(path, payload=None):
    """-> (http status, parsed body). Refusals come back as a body with 'error'."""
    req = urllib.request.Request(
        f"{PROXY}{path}", method="POST" if payload is not None else "GET",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"content-type": "application/json", "x-editor-token": token()})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, {"error": body[:500] or str(e)}
    except urllib.error.URLError as e:
        sys.exit(f"cannot reach the tracking proxy at {PROXY}: {e.reason}")


def years(ys):
    return ", ".join(str(y) for y in ys) if ys else "none"


def print_cards(pairs):
    """The version cards: the touched versions as TARGET, their siblings underneath."""
    for pair in pairs:
        head = f"{pair['country_iso3']} / {pair['hazard']}"
        targets = [v for v in pair["versions"] if v.get("target")]
        others = [v for v in pair["versions"] if not v.get("target")]
        for v in targets:
            print(f"TARGET   {head} / {v['version']}   —   {v['role'].upper()}"
                  + ("   [SEALED]" if v["sealed"] else ""))
            card_detail(v, "         ")
        if others:
            print(f"{'other versions of' if targets else 'versions of'} {head}:")
        for v in others:
            print(f"   {v['version']:<12} {v['role']}" + ("   [SEALED]" if v["sealed"] else ""))
            card_detail(v, "                ")
        print()


def card_detail(v, pad):
    bits = [f"valid from {v['valid_from'] or '—'}" + (f" until {v['valid_until']}" if v["valid_until"] else "")]
    if v.get("endorsed_by"):
        bits.append(f"endorsed by {v['endorsed_by']}")
    print(f"{pad}{' · '.join(bits)}")
    print(f"{pad}document: {v.get('doc_title') or v.get('doc_url') or 'none registered'}"
          + (f" ({v['doc_url']})" if v.get("doc_title") and v.get("doc_url") else ""))
    if v["sealed"]:
        print(f"{pad}sealed {v['sealed_at'][:10]} against: {v['sealed_against']}")
    if not v["windows"]:
        print(f"{pad}backtest recorded now: none")
    for w in v["windows"]:
        span = (f"{w['analysis_start']}–{w['analysis_end']}"
                if w["analysis_start"] is not None and w["analysis_end"] is not None else "no span")
        print(f"{pad}now: {w['window_name']} [{span}] {years(w['years'])}")


def show(row, skip=KEY_COLS):
    return ", ".join(f"{c}={v}" for c, v in row.items() if c not in skip and v is not None)


BACKTEST_TABLES = ("window", "simulated_activation", "version_performance_reported")


def print_plan(out):
    other = sorted({it["table"] for it in out["plan"]} - set(BACKTEST_TABLES))
    if other:
        print(f"NOTE: this file also changes {', '.join('aa.' + t for t in other)} — not backtest "
              "tables, so not covered by the TARGET above. Check those rows on their own.")
    print("changes:")
    for it in out["plan"]:
        if it["op"] == "replace":
            scope = "/".join(str(v) for v in it["scope"].values())
            print(f"  replace aa.{it['table']} [{scope}]: {len(it['before'])} row(s) out, "
                  f"{len(it['after'])} in")
            if it["table"] == "simulated_activation":   # the useful view: years per window
                def by_window(rows):
                    d = {}
                    for r in rows:
                        d.setdefault(r["window_name"], set()).add(r["event_year"])
                    return d
                old, new = by_window(it["before"]), by_window(it["after"])
                for w in sorted(set(old) | set(new)):
                    gone, added = sorted(old.get(w, set()) - new.get(w, set())), sorted(new.get(w, set()) - old.get(w, set()))
                    print(f"     {w}: " + (f"- {years(gone)}   " if gone else "")
                          + (f"+ {years(added)}" if added else "") + ("" if gone or added else "same years"))
            else:
                for b in it["before"]:
                    print("     -", show(b))
                for r in it["after"]:
                    print("     +", show(r))
        elif it["op"] == "update":
            ch = {k: v for k, v in it["after"].items() if str(it["before"].get(k)) != str(v)}
            print(f"  update aa.{it['table']} [{'/'.join(str(v) for v in it['key'].values())}]: "
                  + (", ".join(f"{k} {it['before'].get(k)} -> {v}" for k, v in ch.items()) or "no change"))
        else:
            print(f"  {it['op']} aa.{it['table']} [{'/'.join(str(v) for v in it['key'].values())}]")
    perf = out.get("performance") or {}
    if perf.get("windows"):
        print("backtest after these changes (Weibull: (analysed years + 1) / activations):")
        for w in perf["windows"]:
            rp = f"{w['return_period']:g}" if w["return_period"] is not None else "—"
            rep = f"{w['rp_reported']:g}" if w["rp_reported"] is not None else "—"
            span = (f"{w['analysis_start']}–{w['analysis_end']}, {w['analysis_years']} yrs"
                    if w["analysis_years"] is not None else "no span")
            print(f"  {w['version']} · {w['window_name']} [{span}]: {w['n_activations']} activation(s) "
                  f"({years(w['years'])}) -> RP {rp} (reported {rep})")
        for o in perf.get("overall") or []:
            if o["overall_return_period"] is not None:
                print(f"  {o['version']} · overall (any window): {o['n_activation_years']} year(s) "
                      f"-> RP {o['overall_return_period']:g}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--versions", metavar="ISO3[/hazard]", help="list the registered versions")
    ap.add_argument("--write", action="store_true", help="apply (default: dry run)")
    ap.add_argument("--endorsed", action="append", default=[], metavar="ISO3/hazard/version",
                    help="confirm that this ENDORSED version is the one to write (repeatable)")
    ap.add_argument("--seal", metavar="AGAINST", help="seal the --endorsed version: the document "
                    "(link) + page / table the record was checked against")
    ap.add_argument("--by", help="entered_by, when there is no FILE (a seal alone)")
    a = ap.parse_args()

    if a.versions:
        iso3, _, hazard = a.versions.partition("/")
        qs = urllib.parse.urlencode({"iso3": iso3.upper(), **({"hazard": hazard} if hazard else {})})
        _, out = call(f"/versions?{qs}")
        if out.get("error"):
            print(f"{out['error']}" + (f"\n{out['hint']}" if out.get("hint") else "") + "\n")
            print_cards(out.get("versions") or [])
            sys.exit(1)
        if not out["versions"]:
            sys.exit(f"nothing is registered for {a.versions}")
        print_cards(out["versions"])
        return

    if a.file:
        payload = json.loads(Path(a.file).read_text())
    elif a.seal:
        payload = {"entered_by": a.by, "rows": []}
    else:
        ap.error("give FILE, --versions, or --endorsed KEY --seal AGAINST")
    if a.by:
        payload["entered_by"] = a.by
    if not str(payload.get("entered_by") or "").strip():
        sys.exit("'entered_by' (who, from what) is required — in the file, or --by")
    if a.seal:
        if len(a.endorsed) != 1:
            sys.exit("--seal seals exactly one version: name it with --endorsed ISO3/hazard/version")
        payload["seal"] = {"version": a.endorsed[0], "against": a.seal}
    payload["confirm_endorsed"] = a.endorsed
    payload["dry_run"] = not a.write

    _, out = call("/entries", payload)
    if out.get("error"):
        print(f"REFUSED — nothing written.\n{out['error']}")
        for k in ("hint", "detail"):
            if out.get(k):
                print(f"{k}: {out[k]}")
        if out.get("versions"):
            print()
            print_cards(out["versions"])
        sys.exit(1)

    print_cards(out["versions"])
    print_plan(out)
    if out.get("sealed"):
        print(f"seal: {out['sealed']['version']} against: {out['sealed']['against']}")
    print()
    if out["applied"]:
        print(f"APPLIED to the database: {out['items']} item(s)"
              + (f"; {out['sealed']['version']} is now SEALED" if out.get("sealed") else "") + ".")
        return
    print("DRY RUN: every check passed against the live database; nothing was written.")
    need = [k for k in out.get("needs_confirm_endorsed") or [] if k not in a.endorsed]
    if need:
        print("To apply: this touches an ENDORSED version — its backtest is the record of what "
              "was endorsed.\n  If that is the version you mean: --write "
              + " ".join(f"--endorsed {k}" for k in need)
              + "\n  If you are iterating on a revision, write to the development version instead.")
    else:
        print("To apply: --write" + "".join(f" --endorsed {k}" for k in a.endorsed)
              + (" --seal …" if a.seal else ""))


if __name__ == "__main__":
    main()
