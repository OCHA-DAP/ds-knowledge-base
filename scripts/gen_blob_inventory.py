#!/usr/bin/env python3
"""Inventory blobs under a given prefix in an Azure storage container.

Connects read-only via ocha-stratus. Enumerates blobs under --prefix, groups
them by virtual directory, and emits a size/count/date-range summary. With
--coverage, also parses GloFAS filenames and shows attribute coverage
(gauges/locations, years, leadtimes, member types, gaps).

With --write, saves a markdown asset page to assets/<project>/<datasource>.md
instead of printing to stdout.

Usage:
    # print directory tree
    python scripts/gen_blob_inventory.py --stage dev

    # drill into GloFAS, show coverage, write the asset page
    python scripts/gen_blob_inventory.py --stage dev --filter glofas --coverage --write

Auth: set DSCI_AZ_BLOB_PROD_SAS (or DSCI_AZ_BLOB_DEV_SAS for --stage dev).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# GloFAS filename patterns
# ---------------------------------------------------------------------------
# reanalysis:          glofas_raw_reanalysis_{location}_{year}.grib
# reforecast:          glofas_raw_reforecast_{location}_{member}_{year}_lt{a}-{b}.grib
# reforecast_country:  glofas_raw_reforecast_country_{member}_{year}_lt{a}-{b}.grib
# monitoring (plain):  glofas_{type}_{YYYY-MM-DD}.grib
# monitoring (located):glofas_{location}_{type}_{YYYY-MM-DD}.grib

_REANALYSIS = re.compile(
    r"glofas_raw_reanalysis_(?P<location>.+?)_(?P<year>\d{4})\.grib"
)
_REFORECAST_COUNTRY = re.compile(
    r"glofas_raw_reforecast_country_(?P<member>ensemble|control)_(?P<year>\d{4})_lt(?P<lt_start>\d+)-(?P<lt_end>\d+)\.grib"
)
_REFORECAST = re.compile(
    r"glofas_raw_reforecast_(?P<location>[^_]+)_(?P<member>ensemble|control)_(?P<year>\d{4})_lt(?P<lt_start>\d+)-(?P<lt_end>\d+)\.grib"
)
_MONITORING = re.compile(
    r"glofas_(?:(?P<location>[^_]+)_)?(?P<type>forecast|reanalysis)_(?P<date>\d{4}-\d{2}-\d{2})\.grib"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def human_size(n: int) -> str:
    f = float(n)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if f < 1024 or u == "TB":
            return f"{f:.0f} {u}" if u == "B" else f"{f:.1f} {u}"
        f /= 1024


def fmt_date(ts) -> str:
    return ts.strftime("%Y-%m-%d") if ts else "—"


def year_ranges(years: list[int]) -> str:
    """Compact representation, e.g. '2003–2010, 2015, 2018–2020'."""
    if not years:
        return "—"
    years = sorted(set(years))
    ranges, start, prev = [], years[0], years[0]
    for y in years[1:]:
        if y != prev + 1:
            ranges.append(f"{start}–{prev}" if start != prev else str(start))
            start = y
        prev = y
    ranges.append(f"{start}–{prev}" if start != prev else str(start))
    return ", ".join(ranges)


def gap_years(years: list[int]) -> list[int]:
    ys = sorted(set(years))
    if not ys:
        return []
    expected = set(range(ys[0], ys[-1] + 1))
    return sorted(expected - set(ys))


def lt_label(lt_start: str, lt_end: str) -> str:
    return f"lt{lt_start}–{lt_end}h"


def lt_sort_key(label: str) -> int:
    return int(label[2:].split("–")[0])


# ---------------------------------------------------------------------------
# Directory tree
# ---------------------------------------------------------------------------

def make_tree(blobs: list, prefix: str, group_depth: int) -> dict:
    """Group blobs by virtual directory up to group_depth levels below prefix.

    Only creates groups for true virtual directories — never for the filename
    segment itself, so flat files don't appear as fake subdirectories.
    """
    dirs: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "size": 0, "earliest": None, "latest": None}
    )
    for blob in blobs:
        rel = blob.name[len(prefix):]
        parts = [p for p in rel.split("/") if p]
        for d in range(1, min(group_depth + 1, len(parts))):
            key = prefix + "/".join(parts[:d]) + "/"
            dirs[key]["count"] += 1
            dirs[key]["size"] += blob.size or 0
            ts = blob.last_modified
            if ts:
                if dirs[key]["earliest"] is None or ts < dirs[key]["earliest"]:
                    dirs[key]["earliest"] = ts
                if dirs[key]["latest"] is None or ts > dirs[key]["latest"]:
                    dirs[key]["latest"] = ts
    return dirs


def render_tree_md(dirs: dict, prefix: str) -> list[str]:
    """Render the directory tree as markdown table rows."""
    prefix_depth = prefix.rstrip("/").count("/") + 1
    lines = [
        "| path | files | size | earliest | latest |",
        "|---|--:|--:|---|---|",
    ]
    for path in sorted(dirs):
        d = dirs[path]
        depth = path.count("/") - prefix_depth
        indent = "  " * depth  # non-breaking spaces for indent
        display = path[len(prefix):]
        lines.append(
            f"| {indent}`{display}` | {d['count']} | {human_size(d['size'])} "
            f"| {fmt_date(d['earliest'])} | {fmt_date(d['latest'])} |"
        )
    return lines


# ---------------------------------------------------------------------------
# GloFAS coverage analysis
# ---------------------------------------------------------------------------

def parse_glofas(blobs: list) -> dict:
    """Parse GloFAS filenames into structured coverage data."""
    reanalysis: dict[str, list[int]] = defaultdict(list)
    reforecast: dict[tuple, dict] = defaultdict(lambda: {"years": [], "lt_ranges": set()})
    reforecast_country: dict[str, dict] = defaultdict(lambda: {"years": [], "lt_ranges": set()})
    monitoring: dict[tuple, list] = defaultdict(list)

    for b in blobs:
        if b.name.endswith("/"):
            continue
        fname = b.name.split("/")[-1]

        m = _REANALYSIS.match(fname)
        if m:
            reanalysis[m["location"]].append(int(m["year"]))
            continue

        m = _REFORECAST_COUNTRY.match(fname)
        if m:
            d = reforecast_country[m["member"]]
            d["years"].append(int(m["year"]))
            d["lt_ranges"].add(lt_label(m["lt_start"], m["lt_end"]))
            continue

        m = _REFORECAST.match(fname)
        if m:
            d = reforecast[(m["location"], m["member"])]
            d["years"].append(int(m["year"]))
            d["lt_ranges"].add(lt_label(m["lt_start"], m["lt_end"]))
            continue

        m = _MONITORING.match(fname)
        if m:
            loc = m["location"] or "(global)"
            monitoring[(loc, m["type"])].append(m["date"])

    return {
        "reanalysis": reanalysis,
        "reforecast": reforecast,
        "reforecast_country": reforecast_country,
        "monitoring": monitoring,
    }


def render_raw_glofas_md(parsed: dict) -> list[str]:
    """Render the Raw data section: format description + coverage tables by subdir."""
    lines = [
        "## Raw data (`raw/glofas/`)",
        "",
        "Format: **GRIB** (`.grib`), readable via `cfgrib` / `xarray`. "
        "All files expose a single variable:",
        "",
        "| variable | long name | units |",
        "|---|---|---|",
        "| `dis24` | Mean discharge in the last 24 hours | m³ s⁻¹ |",
        "",
        "Dimensions vary by subdir:",
        "",
        "| subdir | dimensions | notes |",
        "|---|---|---|",
        "| `reanalysis/` | `time` | daily analysis at a single gauge point (lat/lon) |",
        "| `reforecast/` | `number`, `time`, `step` | 10 ensemble members; `time` = issue date; `step` = lead days within the batch |",
        "| `reforecast_country/` | `number`, `time`, `step` | same as reforecast, country-wide spatial extent |",
        "| `monitoring/` | `step` | 5-day forecast issued on the file date |",
        "",
    ]

    ra = parsed["reanalysis"]
    rf = parsed["reforecast"]
    rfc = parsed["reforecast_country"]
    mon = parsed["monitoring"]

    if ra:
        lines += ["### Reanalysis coverage", ""]
        lines += [
            "| location | years | files | gaps |",
            "|---|---|--:|---|",
        ]
        for loc, years in sorted(ra.items()):
            ys = sorted(set(years))
            missing = gap_years(ys)
            lines.append(
                f"| {loc} | {year_ranges(ys)} | {len(ys)} | "
                f"{year_ranges(missing) if missing else 'none'} |"
            )
        lines.append("")

    if rf:
        lines += ["### Reforecast coverage — by location and member type", ""]
        lines += [
            "| location | member | years | leadtime ranges | gaps |",
            "|---|---|---|---|---|",
        ]
        for (loc, member), d in sorted(rf.items()):
            ys = sorted(set(d["years"]))
            missing = gap_years(ys)
            lt = ", ".join(sorted(d["lt_ranges"], key=lt_sort_key))
            lines.append(
                f"| {loc} | {member} | {year_ranges(ys)} | {lt} | "
                f"{year_ranges(missing) if missing else 'none'} |"
            )
        lines.append("")

    if rfc:
        lines += ["### Reforecast coverage — country-wide", ""]
        lines += [
            "| member | years | leadtime ranges | gaps |",
            "|---|---|---|---|",
        ]
        for member, d in sorted(rfc.items()):
            ys = sorted(set(d["years"]))
            missing = gap_years(ys)
            lt = ", ".join(sorted(d["lt_ranges"], key=lt_sort_key))
            lines.append(
                f"| {member} | {year_ranges(ys)} | {lt} | "
                f"{year_ranges(missing) if missing else 'none'} |"
            )
        lines.append("")

    if mon:
        lines += ["### Monitoring coverage", ""]
        lines += [
            "| location | type | date range | files |",
            "|---|---|---|--:|",
        ]
        for (loc, typ), dates in sorted(mon.items()):
            dates_s = sorted(dates)
            lines.append(
                f"| {loc} | {typ} | {dates_s[0]} → {dates_s[-1]} | {len(dates)} |"
            )
        lines.append("")

    return lines


def inspect_processed_parquets(client, prefix: str, datasource: str, stratus, stage: str) -> list[dict]:
    """Load each processed parquet under prefix/processed/<datasource>/ and return schema info."""
    processed_prefix = f"{prefix}processed/{datasource}/"
    blobs = [
        b for b in client.list_blobs(name_starts_with=processed_prefix)
        if not b.name.endswith("/") and b.name.endswith(".parquet")
    ]
    results = []
    for b in sorted(blobs, key=lambda x: x.name):
        fname = b.name.split("/")[-1]
        try:
            df = stratus.load_parquet_from_blob(b.name, stage=stage)
            cols = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]
            results.append({
                "filename": fname,
                "rows": len(df),
                "size": b.size,
                "columns": cols,
            })
        except Exception as e:
            results.append({"filename": fname, "rows": None, "size": b.size, "error": str(e)})
    return results


def render_processed_md(processed_info: list[dict]) -> list[str]:
    """Render the Processed data section: file inventory + per-file schema."""
    lines = [
        "## Processed data (`processed/glofas/`)",
        "",
        "Format: **Parquet** (`.parquet`), readable via `ocha-stratus` / `pandas`. "
        "Extracted and flattened from the raw GRIBs.",
        "",
        "| file | rows | size | columns |",
        "|---|--:|--:|---|",
    ]
    for f in processed_info:
        if "error" in f:
            lines.append(f"| `{f['filename']}` | — | {human_size(f['size'])} | _(read error: {f['error']})_ |")
        else:
            col_str = ", ".join(f"`{c['name']}` ({c['dtype']})" for c in f["columns"])
            lines.append(
                f"| `{f['filename']}` | {f['rows']:,} | {human_size(f['size'])} | {col_str} |"
            )
    lines.append("")

    # group files by schema signature for schema tables
    seen_schemas: dict[str, list[str]] = {}
    for f in processed_info:
        if "error" in f or not f.get("columns"):
            continue
        sig = tuple((c["name"], c["dtype"]) for c in f["columns"])
        seen_schemas.setdefault(sig, []).append(f["filename"])

    if seen_schemas:
        lines += ["### Schemas", ""]
        for sig, fnames in seen_schemas.items():
            lines.append(f"**`{'`, `'.join(fnames)}`**")
            lines.append("")
            lines += [
                "| column | dtype | description |",
                "|---|---|---|",
            ]
            _DESCRIPTIONS = {
                "time":       "forecast issue date (or analysis date for reanalysis)",
                "valid_time": "validity date of the forecast",
                "dis24":      "mean river discharge in the last 24 hours (m³/s)",
                "number":     "ensemble member index",
                "leadtime":   "lead time in days",
                "product_type": "GloFAS product type (e.g. ensemble)",
                "year":       "year of the reforecast",
                "lt_start":   "leadtime window start (hours)",
                "lt_end":     "leadtime window end (hours)",
                "downloaded_at": "ISO timestamp when this batch was downloaded",
            }
            for col_name, dtype in sig:
                desc = _DESCRIPTIONS.get(col_name, "")
                lines.append(f"| `{col_name}` | `{dtype}` | {desc} |")
            lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def build_page(
    prefix: str,
    datasource: str,
    stage: str,
    container: str,
    blobs: list,
    dirs: dict,
    raw_coverage: dict | None,
    processed_info: list[dict] | None,
    generated_on: str,
) -> str:
    total_files = sum(b.size is not None for b in blobs)
    total_size = sum(b.size or 0 for b in blobs)

    L = [
        "---",
        "content_type: asset",
        f"project_prefix: {prefix.rstrip('/')}",
        f"datasource: {datasource}",
        f"container: {container}",
        f"stage: {stage}",
        "visibility: internal",
        f"last_synced: {generated_on}",
        "---",
        "",
        f"# {prefix.rstrip('/')} — {datasource}",
        "",
        "<!-- generated by scripts/gen_blob_inventory.py — do not edit; re-run to refresh -->",
        "",
        f"**{total_files} files · {human_size(total_size)}** "
        f"in `{container}` ({stage}), prefix `{prefix}`.",
        "",
        "## Directory overview",
        "",
    ]
    L += render_tree_md(dirs, prefix)
    L.append("")

    if raw_coverage:
        L += render_raw_glofas_md(raw_coverage)

    if processed_info:
        L += render_processed_md(processed_info)

    L.append(
        f"_Regenerate: `python scripts/gen_blob_inventory.py "
        f"--stage {stage} --filter {datasource} --coverage --write`_"
    )
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--prefix",
        default="ds-aa-nga-flooding",
        help="Blob prefix to enumerate (default: ds-aa-nga-flooding)",
    )
    ap.add_argument("--stage", default="prod", choices=["prod", "dev"])
    ap.add_argument("--container", default="projects")
    ap.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Path segments after prefix to group by (default: 2)",
    )
    ap.add_argument(
        "--filter",
        default=None,
        metavar="SUBSTR",
        help="Only show directory groups whose path contains SUBSTR (e.g. glofas)",
    )
    ap.add_argument(
        "--coverage",
        action="store_true",
        help="Parse GloFAS filenames and show attribute coverage",
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Write markdown asset page to assets/<prefix>/<datasource>.md",
    )
    args = ap.parse_args()

    try:
        import ocha_stratus as stratus
    except ImportError:
        sys.exit("Needs ocha-stratus: pip install ocha-stratus")

    prefix = args.prefix.rstrip("/") + "/"
    print(f"Listing blobs: container={args.container!r}, stage={args.stage!r}, prefix={prefix!r}")

    try:
        client = stratus.get_container_client(args.container, stage=args.stage, write=False)
        blobs = list(client.list_blobs(name_starts_with=prefix))
    except Exception as e:
        sys.exit(
            f"Blob listing failed ({type(e).__name__}: {e}).\n"
            f"Check DSCI_AZ_BLOB_{args.stage.upper()}_SAS env var."
        )

    if not blobs:
        print(f"No blobs found under {prefix!r} in {args.container!r} ({args.stage}).")
        return

    total_size = sum(b.size or 0 for b in blobs)
    print(f"Found {len(blobs)} blobs — {human_size(total_size)} total.")

    dirs = make_tree(blobs, prefix, args.depth)
    if args.filter:
        dirs = {k: v for k, v in dirs.items() if args.filter.lower() in k.lower()}

    datasource = args.filter or args.prefix.split("-")[-1]
    generated_on = date.today().isoformat()

    raw_coverage = None
    processed_info = None
    if args.coverage:
        glofas_blobs = [b for b in blobs if datasource.lower() in b.name.lower()]
        raw_coverage = parse_glofas(glofas_blobs)
        print("Inspecting processed parquets...")
        try:
            processed_info = inspect_processed_parquets(client, prefix, datasource, stratus, args.stage)
        except Exception as e:
            print(f"  warning: could not inspect processed files: {e}")

    if args.write:
        page = build_page(prefix, datasource, args.stage, args.container,
                          blobs, dirs, raw_coverage, processed_info, generated_on)
        out = ROOT / "assets" / args.prefix / f"{datasource}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"Wrote {out.relative_to(ROOT)}")
    else:
        # print to stdout
        from io import StringIO
        buf = StringIO()

        def p(*a, **kw):
            print(*a, **kw, file=buf)

        p(f"\n{'path':<72} {'files':>6} {'size':>10} {'earliest':>12} {'latest':>12}")
        p("-" * 116)
        prefix_depth = prefix.rstrip("/").count("/") + 1
        for path in sorted(dirs):
            d = dirs[path]
            depth = path.count("/") - prefix_depth
            indent = "  " * depth
            display = path[len(prefix):]
            label = f"{indent}{display}"
            p(
                f"{label:<72} {d['count']:>6} {human_size(d['size']):>10}"
                f" {fmt_date(d['earliest']):>12} {fmt_date(d['latest']):>12}"
            )

        if raw_coverage:
            p("\n" + "=" * 72)
            p("GloFAS coverage")
            p("=" * 72)
            ra, rf, rfc, mon = (
                coverage["reanalysis"], coverage["reforecast"],
                coverage["reforecast_country"], coverage["monitoring"],
            )
            if ra:
                p("\n### Reanalysis")
                p(f"  {'location':<20} {'years':<30} files  gaps")
                p("  " + "-" * 65)
                for loc, years in sorted(ra.items()):
                    ys = sorted(set(years))
                    missing = gap_years(ys)
                    p(f"  {loc:<20} {year_ranges(ys):<30} {len(ys):>5}  {year_ranges(missing) if missing else 'none'}")
            if rf:
                p("\n### Reforecast (location × member type)")
                p(f"  {'location':<12} {'member':<10} {'years':<30} {'leadtime ranges':<40} gaps")
                p("  " + "-" * 105)
                for (loc, member), d in sorted(rf.items()):
                    ys = sorted(set(d["years"]))
                    missing = gap_years(ys)
                    lt = ", ".join(sorted(d["lt_ranges"], key=lt_sort_key))
                    p(f"  {loc:<12} {member:<10} {year_ranges(ys):<30} {lt:<40} {year_ranges(missing) if missing else 'none'}")
            if rfc:
                p("\n### Reforecast — country-wide")
                p(f"  {'member':<10} {'years':<30} {'leadtime ranges':<40} gaps")
                p("  " + "-" * 85)
                for member, d in sorted(rfc.items()):
                    ys = sorted(set(d["years"]))
                    missing = gap_years(ys)
                    lt = ", ".join(sorted(d["lt_ranges"], key=lt_sort_key))
                    p(f"  {member:<10} {year_ranges(ys):<30} {lt:<40} {year_ranges(missing) if missing else 'none'}")
            if mon:
                p("\n### Monitoring")
                p(f"  {'location':<14} {'type':<12} {'date range':<24} files")
                p("  " + "-" * 60)
                for (loc, typ), dates in sorted(mon.items()):
                    dates_s = sorted(dates)
                    p(f"  {loc:<14} {typ:<12} {dates_s[0]} → {dates_s[-1]}  {len(dates)}")

        print(buf.getvalue())
        print(f"Showing up to {args.depth} path level(s) below prefix. Use --depth N to go deeper.")


if __name__ == "__main__":
    main()
