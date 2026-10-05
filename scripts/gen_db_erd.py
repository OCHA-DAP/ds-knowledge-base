#!/usr/bin/env python3
"""Generate the DATABASE ER MAP — one zoomable page of every table and view in the team's Postgres
databases (prod / dev), grouped by where the data comes from: the OneGMS mirrors (CERF, CBPF), the
Humanitarian Action / HPC mirror, IPC, FEWS NET, what our own pipelines calculate (by data source), and
the AA store. Built for the questions "what do we hold, whose data is it, and how does it join?".

Inputs (all committed — no network, no secrets; safe to run at Pages deploy time):
  infrastructure/.db-catalog.json      prod catalog: relations, columns, declared keys, view lineage
  infrastructure/.db-catalog-dev.json  dev catalog (both written by gen_db_schema.py)
  infrastructure/db-erd.yml            the CURATED overlay: provenance classes, upstream sources, the
                                       panels and groups, join-by-convention edges, what is left off
  scripts/db_erd_template.html         the page (markup, styles, layout and interaction code)

Output:
  db_erd.html   the page — site.yml copies it to /db-erd/index.html on the Pages site

The database declares only a handful of foreign keys, so most relationships on the map come from the
overlay. Nothing is dropped silently: a relation no group claims lands in an "Unclassified" panel, and
an overlay edge / key / group entry that names something the catalog no longer has is left out of the
drawing and listed in the page's notes (and on stderr here).

Usage:  python scripts/gen_db_erd.py [--check] [--dump]
        --check   exit 2 if db_erd.html on disk differs from what would be generated
        --dump    print the page's data as JSON instead of writing the page
Exit:   0 ok · 1 an input is missing/unparseable (nothing written) · 2 (--check) stale
Needs:  pyyaml.
"""
from __future__ import annotations
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "infrastructure" / "db-erd.yml"
CATALOGS = {"prod": ROOT / "infrastructure" / ".db-catalog.json", "dev": ROOT / "infrastructure" / ".db-catalog-dev.json"}
TEMPLATE = ROOT / "scripts" / "db_erd_template.html"
OUT = ROOT / "db_erd.html"
GH = "https://github.com/OCHA-DAP"
KB_BLOB = f"{GH}/ds-knowledge-base/blob/main"
MARK = "/*__DATA__*/null"

# column flags (bitmask) — mirrored in the template
PK, UNIQUE, FK, CONV_KEY, JOIN, NOTNULL = 1, 2, 4, 8, 16, 32
KIND = {"table": "t", "view": "v", "matview": "m"}
TYPE_SHORT = [(r"character varying", "varchar"), (r"character\b", "char"), (r"timestamp without time zone", "timestamp"),
              (r"timestamp with time zone", "timestamptz"), (r"double precision", "float8"), (r"\binteger\b", "int"),
              (r"\bboolean\b", "bool")]


def die(msg: str) -> None:
    sys.exit(f"ERROR: {msg}")


def load_json(path: Path) -> dict:
    if not path.exists():
        die(f"missing input {path.relative_to(ROOT)} (run scripts/gen_db_schema.py --stage prod|dev)")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"unparseable {path.relative_to(ROOT)}: {e}")


def short_type(t: str) -> str:
    for pat, rep in TYPE_SHORT:
        t = re.sub(pat, rep, t)
    return t


def as_list(v) -> list:
    return [] if v is None else v if isinstance(v, list) else [v]


def split_ref(ref: str) -> tuple[str, list[str]]:
    """'schema.table.col1+col2' → ('schema.table', ['col1', 'col2'])."""
    parts = ref.split(".")
    if len(parts) != 3:
        die(f"db-erd.yml: edge endpoint {ref!r} is not schema.table.columns")
    return f"{parts[0]}.{parts[1]}", parts[2].split("+")


def build() -> dict:
    try:
        ov = yaml.safe_load(OVERLAY.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        die(f"missing input {OVERLAY.relative_to(ROOT)}")
    except yaml.YAMLError as e:
        die(f"unparseable {OVERLAY.relative_to(ROOT)}: {e}")
    cats = {stage: load_json(p) for stage, p in CATALOGS.items()}
    rels = {stage: c.get("relations") or {} for stage, c in cats.items()}
    all_ids = sorted(set(rels["dev"]) | set(rels["prod"]))
    stale: list[str] = []          # overlay entries the catalog no longer backs

    # ---- what is deliberately left off
    hidden_ids: set[str] = set()
    hidden_notes = []
    for h in ov.get("hidden") or []:
        got = sorted(i for i in all_ids if any(fnmatch.fnmatchcase(i, p) for p in h["match"]))
        hidden_ids.update(got)
        if got:
            hidden_notes.append({"reason": h.get("reason", ""), "items": got})
        else:
            stale.append(f"hidden: nothing matches {h['match']}")
    shown = [i for i in all_ids if i not in hidden_ids]

    # ---- groups claim relations
    classes = ov.get("classes") or {}
    sources = ov.get("sources") or {}
    groups: dict[str, dict] = {}
    regions = []
    owner: dict[str, str] = {}
    for r in ov.get("regions") or []:
        if r.get("class") not in classes:
            die(f"db-erd.yml: region {r.get('id')!r} has unknown class {r.get('class')!r}")
        gids = []
        for g in r.get("groups") or []:
            gid = g["id"]
            if gid in groups:
                die(f"db-erd.yml: duplicate group id {gid!r}")
            cls = g.get("class") or r["class"]
            if cls not in classes:
                die(f"db-erd.yml: group {gid!r} has unknown class {cls!r}")
            w = g.get("writer") or {}
            page = w.get("page")
            if page and not (ROOT / page).exists():
                stale.append(f"group {gid}: writer.page {page} does not exist")
                page = None
            groups[gid] = {
                "id": gid, "label": g["label"], "cls": cls, "region": r["id"], "src": as_list(g.get("source")),
                "repo": w.get("repo"), "script": w.get("script"), "page": page, "cadence": g.get("cadence"),
                "note": g.get("note"), "collapsed": bool(g.get("collapsed")), "grain": g.get("grain") or [], "tables": [],
            }
            for pat in g.get("match") or []:
                got = [i for i in shown if fnmatch.fnmatchcase(i, pat)]
                if not got:
                    stale.append(f"group {gid}: nothing matches {pat}")
                for i in got:
                    if owner.setdefault(i, gid) != gid:      # first group in file order wins; say so
                        stale.append(f"group {gid}: {i} is already claimed by group {owner[i]}")
            gids.append(gid)
        regions.append({"id": r["id"], "number": r.get("number"), "row": int(r.get("row", 0)), "label": r["label"],
                        "cls": r["class"], "note": r.get("note"), "groups": gids})
    unclassified = [i for i in shown if i not in owner]
    if unclassified:
        classes.setdefault("ref", {"label": "Reference", "color": "#898781"})
        last_row = max((r["row"] for r in regions), default=0) + 1
        by_schema: dict[str, list[str]] = {}
        for i in unclassified:
            by_schema.setdefault(i.split(".")[0], []).append(i)
        gids = []
        for s, ids in sorted(by_schema.items()):
            gid = f"unclassified-{s}"
            groups[gid] = {"id": gid, "label": f"{s}.* — not yet placed", "cls": "ref", "region": "unclassified", "src": [],
                           "repo": None, "script": None, "page": None, "cadence": None, "collapsed": False, "grain": [],
                           "note": "No group in infrastructure/db-erd.yml claims these yet.", "tables": []}
            for i in ids:
                owner[i] = gid
            gids.append(gid)
        regions.append({"id": "unclassified", "number": None, "row": last_row, "label": "Unclassified", "cls": "ref",
                        "note": "Relations in the database that the curated overlay does not place yet.", "groups": gids})

    # ---- tables
    for src_list, where in [(g["src"], f"group {g['id']}") for g in groups.values()]:
        for s in src_list:
            if s not in sources:
                die(f"db-erd.yml: {where} names unknown source {s!r}")
    tov = ov.get("tables") or {}
    for tid in tov:
        if tid not in all_ids:
            stale.append(f"tables: {tid} is not in the catalog")
    tables: dict[str, dict] = {}
    for tid in shown:
        d, p = rels["dev"].get(tid), rels["prod"].get(tid)
        base = p or d                       # where a table is on both servers, prod is the one that counts
        o = tov.get(tid) or {}
        g = groups[owner[tid]]
        flags = {c[0]: (NOTNULL if c[2] else 0) for c in base["columns"]}
        for c in base["pk"]:
            flags[c] |= PK
        for u in base["unique"]:
            for c in u:
                if c in flags:
                    flags[c] |= UNIQUE
        own_key = o.get("key") or o.get("grain")
        conv_key = (own_key or g["grain"]) if base["kind"] == "table" and not base["pk"] else []
        missing = [c for c in conv_key if c not in flags]
        if missing:
            stale.append(f"tables: {tid} key names missing column(s) {missing}" if own_key else
                         f"group {g['id']}: grain column(s) {missing} are not on {tid} (give it its own key)")
        conv_key = [c for c in conv_key if c in flags]
        for c in conv_key:
            flags[c] |= CONV_KEY
        srcs = as_list(o.get("source")) or g["src"]
        for s in srcs:
            if s not in sources:
                die(f"db-erd.yml: tables.{tid} names unknown source {s!r}")
        drift = []
        if d and p:
            dc, pc = {c[0]: c[1] for c in d["columns"]}, {c[0]: c[1] for c in p["columns"]}
            for c in sorted(set(dc) | set(pc)):
                if dc.get(c) != pc.get(c):
                    drift.append([c, short_type(dc[c]) if c in dc else None, short_type(pc[c]) if c in pc else None])
        t = {
            "id": tid, "s": tid.split(".")[0], "n": tid.split(".", 1)[1], "k": KIND[base["kind"]], "g": g["id"],
            "st": {st: [x["rows"], x["bytes"]] for st, x in (("dev", d), ("prod", p)) if x},
            "cols": [[c[0], short_type(c[1]), flags[c[0]]] for c in base["columns"]],
            "src": srcs,
        }
        if base["pk"]:
            t["pk"] = base["pk"]
        if base["unique"]:
            t["uq"] = base["unique"]
        if conv_key:
            t["ck"] = conv_key
        for k_out, v in (("role", o.get("role")), ("note", o.get("note")), ("comment", base.get("comment")), ("drift", drift)):
            if v:
                t[k_out] = v
        tables[tid] = t
        g["tables"].append(tid)

    # ---- ghosts: named gaps
    edges: list[dict] = []
    for gh in ov.get("ghosts") or []:
        if gh["group"] not in groups:
            die(f"db-erd.yml: ghost {gh['id']!r} names unknown group {gh['group']!r}")
        g = groups[gh["group"]]
        tables[gh["id"]] = {"id": gh["id"], "s": "", "n": gh["label"], "k": "g", "g": g["id"], "st": {}, "cols": [],
                            "src": g["src"], "note": gh.get("note")}
        g["tables"].append(gh["id"])
        for e in gh.get("edges") or []:
            if e["to"] in tables:
                col = e.get("col")
                if col and not any(c[0] == col for c in tables[e["to"]]["cols"]):
                    stale.append(f"ghost {gh['id']}: {e['to']} has no column {col}")
                    col = None
                edges.append({"a": gh["id"], "ac": [], "b": e["to"], "bc": [col] if col else [], "k": "ghost", "label": e.get("label")})
                if col:
                    _flag(tables[e["to"]], col, JOIN)
            else:
                stale.append(f"ghost {gh['id']}: edge to {e['to']} (not on the map)")

    # ---- edges: declared foreign keys, then the overlay's join-by-convention, then view lineage
    seen: set[tuple] = set()
    n_fk_hidden = 0
    for stage in ("dev", "prod"):
        for tid, r in rels[stage].items():
            for fk in r["fks"]:
                key = (tid, tuple(fk["cols"]), fk["ref"], tuple(fk["ref_cols"]))
                if key in seen:
                    continue
                seen.add(key)
                if tid not in tables or fk["ref"] not in tables:
                    n_fk_hidden += 1
                    continue
                edges.append({"a": tid, "ac": fk["cols"], "b": fk["ref"], "bc": fk["ref_cols"], "k": "fk"})
                for c in fk["cols"]:
                    _flag(tables[tid], c, FK)
    hubs = set(ov.get("hubs") or [])
    for h in sorted(hubs):
        if h not in tables:
            stale.append(f"hubs: {h} is not on the map")
    for e in ov.get("edges") or []:
        (a, ac), (b, bc) = split_ref(e[0]), split_ref(e[1])
        label = e[2] if len(e) > 2 else None
        bad = [x for x in (a, b) if x not in tables]
        if bad:
            if any(x not in all_ids for x in bad):       # hidden endpoints are expected; unknown ones are stale
                stale.append(f"edge {e[0]} → {e[1]}: {', '.join(x for x in bad if x not in all_ids)} not in the catalog")
            continue
        acols, bcols = {c[0] for c in tables[a]["cols"]}, {c[0] for c in tables[b]["cols"]}
        miss = [f"{a}.{c}" for c in ac if c not in acols] + [f"{b}.{c}" for c in bc if c not in bcols]
        if miss:
            stale.append(f"edge {e[0]} → {e[1]}: missing column(s) {', '.join(miss)}")
            continue
        if (a, tuple(ac), b, tuple(bc)) in seen:
            continue                                     # the database now declares it
        seen.add((a, tuple(ac), b, tuple(bc)))
        ed = {"a": a, "ac": ac, "b": b, "bc": bc, "k": "conv"}
        if label:
            ed["label"] = label
        if b in hubs:
            ed["q"] = 1
        edges.append(ed)
        for c in ac:
            _flag(tables[a], c, JOIN)
        for c in bc:
            _flag(tables[b], c, JOIN)
    for stage in ("dev", "prod"):
        for vid, r in rels[stage].items():
            for src in r["reads"]:
                key = (vid, "reads", src)
                if key in seen or vid not in tables:
                    continue
                seen.add(key)
                if src not in tables:                    # reads something left off the map: say so in its drawer
                    tables[vid].setdefault("offmap", []).append(src)
                    continue
                edges.append({"a": vid, "ac": [], "b": src, "bc": [], "k": "view"})

    n = lambda kind: sum(1 for t in tables.values() if t["k"] == kind)  # noqa: E731
    notes = {
        "hidden": hidden_notes, "stale": stale, "unclassified": unclassified,
        "not_in_catalog": ov.get("not_in_catalog") or [], "fk_hidden": n_fk_hidden,
    }
    stats = {
        "tables": n("t"), "views": n("v") + n("m"),
        "fk": sum(1 for e in edges if e["k"] == "fk"), "conv": sum(1 for e in edges if e["k"] == "conv"),
        "dev": sum(1 for t in tables.values() if "dev" in t["st"]), "prod": sum(1 for t in tables.values() if "prod" in t["st"]),
        "drift": sum(1 for t in tables.values() if t.get("drift")),
    }
    return {
        "snapshot": {st: c.get("introspected") for st, c in cats.items()},
        "classes": classes, "sources": sources, "regions": regions, "groups": groups, "tables": tables, "edges": edges,
        "notes": notes, "stats": stats, "links": {"gh": GH, "kb": KB_BLOB},
    }


def _flag(table: dict, col: str, bit: int) -> None:
    for c in table["cols"]:
        if c[0] == col:
            c[2] |= bit
            return


def render(data: dict) -> str:
    if not TEMPLATE.exists():
        die(f"missing input {TEMPLATE.relative_to(ROOT)}")
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if tpl.count(MARK) != 1:
        die(f"{TEMPLATE.relative_to(ROOT)} must contain the data marker {MARK} exactly once")
    # No raw "<" inside the inline script, so no table comment can close it or open an HTML comment.
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return tpl.replace(MARK, blob)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args()
    data = build()
    for s in data["notes"]["stale"]:
        print(f"stale overlay entry — {s}", file=sys.stderr)
    for i in data["notes"]["unclassified"]:
        print(f"unclassified — {i} (add it to a group in infrastructure/db-erd.yml)", file=sys.stderr)
    if args.dump:
        print(json.dumps(data, indent=1, ensure_ascii=False))
        return
    html = render(data)
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != html:
            print(f"{OUT.name} is stale — run scripts/gen_db_erd.py", file=sys.stderr)
            sys.exit(2)
        return
    OUT.write_text(html, encoding="utf-8")
    s = data["stats"]
    print(f"Wrote {OUT.relative_to(ROOT)} — {s['tables']} tables, {s['views']} views, {s['fk']} declared FKs, "
          f"{s['conv']} joins by convention; {len(data['notes']['unclassified'])} unclassified, "
          f"{len(data['notes']['stale'])} stale overlay entries.")


if __name__ == "__main__":
    main()
