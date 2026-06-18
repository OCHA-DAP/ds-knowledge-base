#!/usr/bin/env python3
"""Regenerate catalog.md from frameworks/**/*.md frontmatter.

The catalog is the generated, filterable index of every framework-version.
Source of truth is each page's YAML frontmatter — never edit catalog.md by hand.

Usage:  python scripts/gen_catalog.py   (run from repo root)
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml  (or pip install pyyaml)")

ROOT = Path(__file__).resolve().parent.parent
FW_DIR = ROOT / "frameworks"
OUT = ROOT / "catalog.md"


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return None


def as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def fmt_country(v) -> str:
    return "/".join(str(x) for x in as_list(v)) or "—"


def fmt_completeness(v) -> str:
    if isinstance(v, dict):
        return "/".join(f"{k}:{val}" for k, val in v.items())
    return str(v) if v else "—"


MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_months(months) -> str:
    """Compact a month-int list into season spans: [11,12,1,2,3,4] -> 'Nov–Apr'."""
    ms = sorted({int(m) for m in as_list(months) if isinstance(m, (int, float))})
    if not ms:
        return "—"
    if len(ms) == 12:
        return "year-round"
    runs, start, prev = [], ms[0], ms[0]
    for m in ms[1:]:
        if m == prev + 1:
            prev = m
        else:
            runs.append((start, prev))
            start = prev = m
    runs.append((start, prev))
    if len(runs) >= 2 and runs[0][0] == 1 and runs[-1][1] == 12:  # wrap Dec->Jan
        first, last = runs.pop(0), runs.pop(-1)
        runs.insert(0, (last[0], first[1]))
    fmt = lambda a, b: MONTH_ABBR[a] if a == b else f"{MONTH_ABBR[a]}–{MONTH_ABBR[b]}"
    return ", ".join(fmt(a, b) for a, b in runs)


def fmt_funding(v) -> str:
    if not isinstance(v, (int, float)) or v <= 0:
        return "—"
    return f"${v / 1e6:.1f}M"


def fmt_activated(activations) -> str:
    acts = as_list(activations)
    if not acts:
        return "—"
    dates = [str(a.get("date", "")) for a in acts if isinstance(a, dict)]
    return "✅ " + ", ".join(d for d in dates if d) if dates else "✅"


def main() -> None:
    rows = []
    for path in sorted(FW_DIR.rglob("*.md")):
        if path.name in ("_TEMPLATE.md", "README.md"):
            continue
        fm = parse_frontmatter(path)
        if not fm or fm.get("content_type") != "framework":
            continue
        facets = fm.get("trigger_facets") or {}
        rel = path.relative_to(ROOT).as_posix()
        rows.append({
            "framework": fm.get("framework", path.parent.name),
            "version": str(fm.get("version", "")),
            "country": fmt_country(fm.get("country_iso3")),
            "hazard": fm.get("hazard", "—"),
            "status": fm.get("status", "—"),
            "funding": fmt_funding(fm.get("prearranged_funding_usd")),
            "basis": facets.get("basis", "—"),
            "nwin": facets.get("n_windows", ""),
            "axes": ", ".join(as_list(facets.get("window_axes"))) or "—",
            "monitoring": fmt_months((fm.get("monitoring_period") or {}).get("months")),
            "sources": ", ".join(str(s) for s in as_list(fm.get("data_sources"))) or "—",
            "completeness": fmt_completeness(fm.get("repo_completeness")),
            "activated": fmt_activated(fm.get("activations")),
            "path": rel,
        })

    rows.sort(key=lambda r: (r["framework"], r["version"]))

    lines = [
        "# Catalog — all framework-versions",
        "",
        f"Generated from `frameworks/**/*.md` frontmatter by `scripts/gen_catalog.py`. "
        f"{len(rows)} version(s). Filter by hazard / data source / basis / #windows / "
        f"window axes / monitoring period / status / completeness / activation.",
        "",
        "| framework | version | country | hazard | monitoring | status | $ pre-arr. | basis | #win | axes | data sources | repo | activated? |",
        "|---|---|---|---|---|---|--:|---|--:|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| [{r['framework']}]({r['path']}) | {r['version']} | {r['country']} | "
            f"{r['hazard']} | {r['monitoring']} | {r['status']} | {r['funding']} | {r['basis']} | {r['nwin']} | "
            f"{r['axes']} | {r['sources']} | {r['completeness']} | {r['activated']} |"
        )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(rows)} framework-versions.")


if __name__ == "__main__":
    main()
