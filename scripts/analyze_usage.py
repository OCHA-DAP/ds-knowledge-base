#!/usr/bin/env python3
"""Analyse KB usage telemetry and produce an improvement digest.

The "Usage" axis of KB self-maintenance (see infrastructure/automation.md). Reads
`kb_usage.events` (written by the MCP, see mcp_server/usage.py) and surfaces the signals
that drive improvement — chiefly **searches that found nothing** (a missing or mis-titled
page) — then writes a markdown digest. The usage-review workflow turns the digest into a
`kb-usage` tracking issue (digest-first; auto-PR drafting via kb-ingest can be enabled
later).

Read-only: connects via ocha-stratus with the standard DSCI read creds. Never writes.

Usage:  python scripts/analyze_usage.py [--stage dev|prod] [--days 30] [--report usage-digest.md]
Needs:  ocha-stratus + sqlalchemy; DSCI_AZ_DB_* read env (+ PGSSLMODE=require).
Exit:   2 if there are actionable signals (zero-result searches or errors), else 0.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _rows(conn, sql, **params):
    from sqlalchemy import text
    return list(conn.execute(text(sql), params))


def _table(headers, rows, aligns=None):
    if not rows:
        return ["_none_", ""]
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    out.append("")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="dev", choices=["prod", "dev"],
                    help="which DB hosts kb_usage.events (default dev)")
    ap.add_argument("--days", type=int, default=30, help="lookback window")
    ap.add_argument("--report", help="write the markdown digest to this file")
    args = ap.parse_args()

    os.environ.setdefault("PGSSLMODE", "require")
    try:
        import ocha_stratus as stratus  # noqa
    except Exception:
        sys.exit("Needs ocha-stratus + sqlalchemy (pip install ocha-stratus).")

    from sqlalchemy.exc import ProgrammingError, OperationalError

    try:
        engine = stratus.get_engine(stage=args.stage)
        conn = engine.connect()
    except Exception as e:
        sys.exit(f"Could not connect to the {args.stage} DB: {e}\n"
                 "Check DSCI_AZ_DB_* env / secrets and PGSSLMODE=require.")

    window = f"ts >= now() - interval '{int(args.days)} days'"
    lines = [f"# KB usage digest — last {args.days} days", ""]
    actionable = False

    try:
        with conn:
            total = _rows(conn, f"SELECT count(*) n, count(*) FILTER (WHERE NOT ok) errs, "
                                f"count(DISTINCT tier) tiers, min(ts) since "
                                f"FROM kb_usage.events WHERE {window}")[0]
            n, errs = total.n or 0, total.errs or 0
            if n == 0:
                lines += ["No tool calls recorded in the window. Either telemetry was just "
                          "enabled, or the MCP hasn't been used yet.", ""]
                _emit(lines, args.report)
                sys.exit(0)

            lines.append(f"**{n}** tool calls · **{errs}** errors "
                         f"({round(100 * errs / n, 1)}%) · since `{total.since}`")
            lines.append("")

            # By tier + tool: volume, error %, p95 latency
            bytool = _rows(conn, f"""
                SELECT tier, tool, count(*) n,
                       round(100.0 * avg((NOT ok)::int), 1) err_pct,
                       percentile_disc(0.95) WITHIN GROUP (ORDER BY latency_ms) p95_ms,
                       round(100.0 * avg((empty IS TRUE)::int) FILTER (WHERE ok), 1) empty_pct
                FROM kb_usage.events WHERE {window}
                GROUP BY tier, tool ORDER BY n DESC""")
            lines += ["## Tool usage", ""]
            lines += _table(["tier", "tool", "calls", "err %", "p95 ms", "empty %"],
                            [(r.tier, r.tool, r.n, r.err_pct, r.p95_ms, r.empty_pct) for r in bytool])

            # THE signal: searches that found nothing.
            zero = _rows(conn, f"""
                SELECT arg_summary, count(*) n, count(DISTINCT tier) tiers
                FROM kb_usage.events
                WHERE {window} AND tool IN ('search_kb','grep')
                      AND empty IS TRUE AND coalesce(arg_summary,'') <> ''
                GROUP BY arg_summary ORDER BY n DESC LIMIT 25""")
            lines += ["## 🔍 Searches that found nothing", "",
                      "_The highest-value signal — what people look for and don't find. Each is a "
                      "candidate for a new/expanded page, a clearer title, or a search synonym._", ""]
            lines += _table(["query", "times", "tiers"],
                            [(f"`{r.arg_summary[:80]}`", r.n, r.tiers) for r in zero])
            if zero:
                actionable = True

            # Most-read pages (what's working / what to deepen)
            pages = _rows(conn, f"""
                SELECT arg_summary path, count(*) n FROM kb_usage.events
                WHERE {window} AND tool = 'read_kb_page' AND coalesce(arg_summary,'') <> ''
                GROUP BY arg_summary ORDER BY n DESC LIMIT 20""")
            lines += ["## 📄 Most-read pages", ""]
            lines += _table(["page", "reads"], [(f"`{r.path}`", r.n) for r in pages])

            # Top SQL shapes (internal) — candidates for a recipes page or a higher-level tool
            sqls = _rows(conn, f"""
                SELECT left(regexp_replace(arg_summary, '\\s+', ' ', 'g'), 140) q,
                       count(*) n, round(100.0 * avg((NOT ok)::int), 1) err_pct
                FROM kb_usage.events WHERE {window} AND tool = 'run_sql'
                      AND coalesce(arg_summary,'') <> ''
                GROUP BY q ORDER BY n DESC LIMIT 15""")
            if sqls:
                lines += ["## 🗃️ Top SQL queries (internal)", ""]
                lines += _table(["query", "times", "err %"],
                                [(f"`{r.q}`", r.n, r.err_pct) for r in sqls])

            # Errors worth fixing (MCP usability)
            errrows = _rows(conn, f"""
                SELECT tool, left(error, 140) error, count(*) n FROM kb_usage.events
                WHERE {window} AND NOT ok AND error IS NOT NULL
                GROUP BY tool, left(error, 140) ORDER BY n DESC LIMIT 15""")
            if errrows:
                actionable = True
                lines += ["## ⚠️ Errors", ""]
                lines += _table(["tool", "error", "times"],
                                [(r.tool, f"`{r.error}`", r.n) for r in errrows])

            lines += ["", "---",
                      "_How to act: zero-result searches & confusing reformulations → KB-organisation "
                      "fixes (new page, cross-links, search synonyms, clearer titles). Errors / "
                      "frequent identical SQL → MCP-behaviour fixes (tool description, a convenience "
                      "tool, a better default). File under `kb-usage`; route clean fixes through "
                      "`kb-ingest` when ready (see infrastructure/usage.md)._"]
    except (ProgrammingError, OperationalError) as e:
        msg = str(getattr(e, "orig", e))
        if "kb_usage" in msg or "does not exist" in msg:
            lines += ["⏳ **Telemetry not enabled yet** — `kb_usage.events` is not present in the "
                      f"`{args.stage}` DB (or not readable by this role). Apply "
                      "`mcp_server/deploy/usage_schema.sql` and set `KB_USAGE_DB_URL` / "
                      "`KB_USAGE_TIER` on the MCP app(s). See infrastructure/usage.md.", ""]
            _emit(lines, args.report)
            sys.exit(0)
        raise

    _emit(lines, args.report)
    sys.exit(2 if actionable else 0)


def _emit(lines, report_path):
    report = "\n".join(lines) + "\n"
    print(report)
    if report_path:
        Path(report_path).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
