#!/usr/bin/env python3
"""Mirror the Postgres DB schema into infrastructure/db-schema.md (read-only).

A point-in-time snapshot of the team's data assets: every schema → table →
columns + primary key, with a row-count estimate and on-disk size per table.
Connects read-only via ocha-stratus (never raw psycopg2). Also emits a small
machine-readable table list (`infrastructure/.db-tables.json`) that
`gen_dependency_graph.py` uses to wire DB tables into the dependency graph, and
the full catalog (`infrastructure/.db-catalog.json`: tables and views, column
types, declared primary / unique / foreign keys, view lineage) that
`gen_db_erd.py` draws the ER diagram from.

Refreshed daily by `.github/workflows/db-schema.yml`; safe to run locally if the
DSCI_AZ_DB_* env vars are set (+ PGSSLMODE=require).

Usage:  python scripts/gen_db_schema.py [--stage prod|dev]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "infrastructure" / "db-schema.md"
JSON_OUT = ROOT / "infrastructure" / ".db-tables.json"

TABLES_SQL = """
SELECT n.nspname AS schema, c.relname AS tbl,
       c.reltuples::bigint AS est_rows,
       pg_total_relation_size(c.oid) AS bytes
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND n.nspname NOT LIKE 'pg\\_%'
ORDER BY n.nspname, c.relname;
"""
COLS_SQL = """
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
  AND table_schema NOT LIKE 'pg\\_%'
ORDER BY table_schema, table_name, ordinal_position;
"""
PK_SQL = """
SELECT tc.table_schema AS s, tc.table_name AS t, kcu.column_name AS c
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
  AND tc.table_schema NOT LIKE 'pg\\_%';
"""


# ---- the full catalog (.db-catalog*.json) — what gen_db_erd.py draws the ER diagram from. Tables AND
# views, column types, declared keys, and view lineage; pg_catalog rather than information_schema
# because the latter hides constraints on tables the connecting role does not own.
NOT_SYS = "n.nspname NOT IN ('pg_catalog', 'information_schema') AND n.nspname NOT LIKE 'pg\\_%'"
CAT_RELS_SQL = f"""
SELECT n.nspname, c.relname, c.relkind::text, c.reltuples::bigint, pg_total_relation_size(c.oid),
       obj_description(c.oid, 'pg_class')
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'p', 'v', 'm', 'f') AND {NOT_SYS}
ORDER BY 1, 2;
"""
CAT_COLS_SQL = f"""
SELECT n.nspname, c.relname, a.attname, format_type(a.atttypid, a.atttypmod), a.attnotnull
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relkind IN ('r', 'p', 'v', 'm', 'f') AND {NOT_SYS}
ORDER BY 1, 2, a.attnum;
"""
CAT_CONS_SQL = f"""
SELECT n.nspname, c.relname, con.contype::text,
       (SELECT array_agg(att.attname ORDER BY k.ord)
          FROM unnest(con.conkey) WITH ORDINALITY k(attnum, ord)
          JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = k.attnum),
       fn.nspname, fc.relname,
       (SELECT array_agg(att.attname ORDER BY k.ord)
          FROM unnest(con.confkey) WITH ORDINALITY k(attnum, ord)
          JOIN pg_attribute att ON att.attrelid = con.confrelid AND att.attnum = k.attnum)
FROM pg_constraint con
JOIN pg_class c ON c.oid = con.conrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_class fc ON fc.oid = con.confrelid
LEFT JOIN pg_namespace fn ON fn.oid = fc.relnamespace
WHERE con.contype IN ('p', 'u', 'f') AND {NOT_SYS}
ORDER BY 1, 2, con.conname;
"""
# Unique indexes that are not backing a primary-key / unique constraint (the team's usual dedupe
# device). Partial indexes are left out: they make a subset of rows unique, not the table. An
# expression column has no attribute row, so it comes back as NULL and is written as "(expr)".
CAT_UIDX_SQL = f"""
SELECT n.nspname, c.relname,
       (SELECT array_agg(att.attname ORDER BY k.ord)
          FROM unnest(i.indkey::int2[]) WITH ORDINALITY k(attnum, ord)
          LEFT JOIN pg_attribute att ON att.attrelid = i.indrelid AND att.attnum = k.attnum
         WHERE k.ord <= i.indnkeyatts)
FROM pg_index i
JOIN pg_class ic ON ic.oid = i.indexrelid
JOIN pg_class c ON c.oid = i.indrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE i.indisunique AND NOT i.indisprimary AND i.indpred IS NULL AND {NOT_SYS}
  AND NOT EXISTS (SELECT 1 FROM pg_constraint con
                  WHERE con.conindid = i.indexrelid AND con.contype IN ('p', 'u', 'x'))
ORDER BY 1, 2, ic.relname;
"""
CAT_VIEWDEPS_SQL = f"""
SELECT DISTINCT n.nspname, v.relname, sn.nspname, s.relname
FROM pg_rewrite r
JOIN pg_class v ON v.oid = r.ev_class
JOIN pg_namespace n ON n.oid = v.relnamespace
JOIN pg_depend d ON d.objid = r.oid AND d.classid = 'pg_rewrite'::regclass
                AND d.refclassid = 'pg_class'::regclass
JOIN pg_class s ON s.oid = d.refobjid
JOIN pg_namespace sn ON sn.oid = s.relnamespace
WHERE v.relkind IN ('v', 'm') AND s.oid <> v.oid AND {NOT_SYS}
ORDER BY 1, 2, 3, 4;
"""
RELKIND = {"r": "table", "p": "table", "f": "table", "v": "view", "m": "matview"}


def build_catalog(conn, text, stage: str) -> dict:
    """Every relation with its columns, declared keys and (for views) the relations it reads."""
    rels: dict[str, dict] = {}
    for s, t, kind, rows, b, comment in conn.execute(text(CAT_RELS_SQL)).fetchall():
        rels[f"{s}.{t}"] = {"kind": RELKIND[kind], "rows": int(rows), "bytes": int(b), "columns": [],
                            "pk": [], "unique": [], "fks": [], "reads": []}
        if comment:
            rels[f"{s}.{t}"]["comment"] = comment
    for s, t, col, typ, notnull in conn.execute(text(CAT_COLS_SQL)).fetchall():
        if f"{s}.{t}" in rels:
            rels[f"{s}.{t}"]["columns"].append([col, typ, bool(notnull)])
    for s, t, contype, cols, rs, rt, rcols in conn.execute(text(CAT_CONS_SQL)).fetchall():
        r = rels.get(f"{s}.{t}")
        if r is None:
            continue
        if contype == "p":
            r["pk"] = list(cols)
        elif contype == "u":
            r["unique"].append(list(cols))
        else:
            r["fks"].append({"cols": list(cols), "ref": f"{rs}.{rt}", "ref_cols": list(rcols)})
    for s, t, cols in conn.execute(text(CAT_UIDX_SQL)).fetchall():
        if f"{s}.{t}" in rels:
            rels[f"{s}.{t}"]["unique"].append([c or "(expr)" for c in cols])
    for s, v, ss, st in conn.execute(text(CAT_VIEWDEPS_SQL)).fetchall():
        if f"{s}.{v}" in rels:
            rels[f"{s}.{v}"]["reads"].append(f"{ss}.{st}")
    return {"stage": stage, "introspected": date.today().isoformat(), "relations": rels}


def write_catalog(path: Path, cat: dict) -> None:
    """One relation per line, so a daily refresh diffs table by table."""
    lines = [f'{json.dumps(k)}: {json.dumps(v, separators=(",", ":"))}' for k, v in sorted(cat["relations"].items())]
    head = '{"stage": %s, "introspected": %s, "relations": {' % (json.dumps(cat["stage"]), json.dumps(cat["introspected"]))
    path.write_text(head + "\n" + ",\n".join(lines) + "\n}}\n", encoding="utf-8")


def human(n: int) -> str:
    f = float(n)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if f < 1024 or u == "TB":
            return f"{f:.0f} {u}" if u == "B" else f"{f:.1f} {u}"
        f /= 1024


def human_rows(n: int) -> str:
    if n < 0:
        return "?"          # never analyzed
    if n >= 1_000_000:
        return f"{n/1e6:.1f}M"
    if n >= 1_000:
        return f"{n/1e3:.1f}k"
    return str(n)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="prod", choices=["prod", "dev"])
    args = ap.parse_args()
    os.environ.setdefault("PGSSLMODE", "require")
    suffix = "" if args.stage == "prod" else f"-{args.stage}"
    out = ROOT / "infrastructure" / f"db-schema{suffix}.md"
    json_out = ROOT / "infrastructure" / f".db-tables{suffix}.json"
    catalog_out = ROOT / "infrastructure" / f".db-catalog{suffix}.json"

    try:
        import ocha_stratus as stratus
        from sqlalchemy import text
    except ImportError:
        sys.exit("Needs ocha-stratus + sqlalchemy (pip install ocha-stratus).")

    try:
        engine = stratus.get_engine(stage=args.stage)
        with engine.connect() as conn:
            tables = conn.execute(text(TABLES_SQL)).fetchall()
            cols = conn.execute(text(COLS_SQL)).fetchall()
            pks = conn.execute(text(PK_SQL)).fetchall()
            try:                # the catalog is an extra: its failure must not cost the snapshot below
                catalog = build_catalog(conn, text, args.stage)
            except Exception as e:
                catalog = None
                print(f"WARNING: catalog introspection failed ({type(e).__name__}: {e}) — "
                      f"{catalog_out.name} left as it was", file=sys.stderr)
    except Exception as e:
        sys.exit(f"DB introspection failed ({type(e).__name__}: {e}). "
                 "Check DSCI_AZ_DB_* env / secrets, PGSSLMODE=require, and network access to Azure PG.")

    cols_by = defaultdict(list)
    for s, t, c, dt in cols:
        cols_by[(s, t)].append((c, dt))
    pk_by = defaultdict(set)
    for s, t, c in pks:
        pk_by[(s, t)].add(c)

    by_schema = defaultdict(list)
    json_tables = {}
    for s, t, rows, b in tables:
        by_schema[s].append((t, rows, b))
        json_tables[f"{s}.{t}"] = {"rows": int(rows), "bytes": int(b),
                                   "columns": [c for c, _ in cols_by[(s, t)]]}

    n_tables = len(tables)
    total_bytes = sum(b for *_, b in tables)
    L = ["<!-- generated by scripts/gen_db_schema.py — a read-only snapshot of the live DB; do not edit -->",
         "", "# Database schema", "",
         f"Read-only snapshot of the Postgres **{args.stage}** database (via `ocha-stratus`), refreshed daily by "
         "`.github/workflows/db-schema.yml`. The team's data-asset map; row counts are planner estimates "
         "(`reltuples`), sizes include indexes + TOAST. These tables are nodes in "
         "`dependency-graph.md` (pipelines write them, apps read them).", "",
         f"**{len(by_schema)} schemas · {n_tables} tables · {human(total_bytes)} total.**", ""]
    for s in sorted(by_schema):
        rows = sorted(by_schema[s], key=lambda r: -r[2])
        sb = sum(b for *_, b in rows)
        L += [f"## `{s}` — {len(rows)} tables · {human(sb)}", "",
              "| table | rows (est) | size | columns |", "|---|--:|--:|---|"]
        for t, r, b in rows:
            cl = cols_by[(s, t)]
            pk = pk_by[(s, t)]
            colstr = ", ".join((f"**{c}**" if c in pk else c) + f" `{dt}`" for c, dt in cl)
            colcell = f"<details><summary>{len(cl)} cols</summary>{colstr}</details>" if cl else "—"
            L.append(f"| `{t}` | {human_rows(r)} | {human(b)} | {colcell} |")
        L.append("")
    L.append("_**bold** = primary key. Regenerate: `python scripts/gen_db_schema.py`._")

    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    json_out.write_text(json.dumps(json_tables, indent=0), encoding="utf-8")
    if catalog is not None:
        write_catalog(catalog_out, catalog)
    print(f"Wrote {out.relative_to(ROOT)} — {len(by_schema)} schemas, {n_tables} tables, {human(total_bytes)}.")


if __name__ == "__main__":
    main()
