#!/usr/bin/env python3
"""Flag framework pages whose published PDF may have a newer version.

The other drift axis: `check_drift.py` watches the *code* (source_sha); this
watches the authoritative *document*. AA frameworks are typically revised
annually, so an endorsed page whose `framework_doc_date` is aging is a prompt to
re-check the portfolio (this is how `lac-dry-corridor` silently went a version
stale). For each flagged framework it emits a one-click ReliefWeb search so the
check is trivial, and makes a best-effort ReliefWeb API probe for a newer doc
(degrades gracefully when the API is unreachable).

The authoritative fix — actually pulling the newest PDF — is a re-run of
`workflows/ingest-frameworks.mjs`, which resolves the latest published version.

Usage:  python scripts/check_pdf_freshness.py [--months 14] [--report f.md]
Exit:   0 = nothing due · 2 = at least one framework due for re-check
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ISO3 = {
    "AFG": "Afghanistan", "BFA": "Burkina Faso", "BGD": "Bangladesh", "COD": "DR Congo",
    "CUB": "Cuba", "MOZ": "Mozambique", "MRT": "Mauritania", "NER": "Niger", "NGA": "Nigeria",
    "NPL": "Nepal", "PHL": "Philippines", "TCD": "Chad", "HTI": "Haiti", "SLV": "El Salvador",
    "GTM": "Guatemala", "HND": "Honduras", "ETH": "Ethiopia", "SSD": "South Sudan",
    "FJI": "Fiji", "KEN": "Kenya", "MDG": "Madagascar", "MMR": "Myanmar",
    "VUT": "Vanuatu", "YEM": "Yemen",
}


def parse_fm(path: Path) -> dict | None:
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return None
    e = t.find("\n---", 3)
    try:
        return yaml.safe_load(t[3:e]) or {}
    except yaml.YAMLError:
        return None


def as_date(v) -> dt.date | None:
    s = str(v).strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def months_between(a: dt.date, b: dt.date) -> int:
    return (b.year - a.year) * 12 + (b.month - a.month)


def search_url(country: str, hazard: str) -> str:
    q = urllib.parse.quote_plus(f"anticipatory action framework {country} {hazard}")
    return f"https://reliefweb.int/updates?search={q}"


def reliefweb_latest(iso3: str, hazard: str) -> dict | None:
    """Best-effort: latest AA report date for a country. None if unreachable."""
    base = "https://api.reliefweb.int/v2/reports"
    params = {
        "appname": "ocha-ds-knowledge-base",
        "filter[field]": "primary_country.iso3",
        "filter[value]": iso3.lower(),
        "query[value]": f"anticipatory action framework {hazard}",
        "query[fields][]": "title",
        "sort[]": "date.original:desc",
        "limit": "3",
        "fields[include][]": "title",
    }
    url = base + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
    except Exception:
        return None
    for item in data.get("data", []):
        f = item.get("fields", {})
        title = (f.get("title") or "").lower()
        if "anticipatory action framework" in title or "action anticipatoire" in title or "cadre" in title:
            d = as_date((f.get("date") or {}).get("original", "")) if f.get("date") else None
            return {"title": f.get("title"), "date": d}
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=14, help="age (months) past which an endorsed doc is due for re-check")
    ap.add_argument("--report", help="write the markdown report to this file")
    ap.add_argument("--today", help="override today (YYYY-MM-DD) for testing")
    args = ap.parse_args()
    today = as_date(args.today) if args.today else dt.date.today()

    api_ok = None
    rows = []
    for path in sorted((ROOT / "frameworks").rglob("*.md")):
        if path.name in ("_TEMPLATE.md", "README.md"):
            continue
        fm = parse_fm(path)
        if not fm or fm.get("content_type") != "framework":
            continue
        status = fm.get("status", "")
        if status in ("superseded", "retired", "development", "pre-development"):
            continue
        doc_date = as_date(fm.get("framework_doc_date"))
        iso3s = fm.get("country_iso3")
        iso3s = iso3s if isinstance(iso3s, list) else [iso3s]
        iso3 = str(iso3s[0]) if iso3s and iso3s[0] else ""
        country = ISO3.get(iso3, iso3)
        hazard = fm.get("hazard", "")
        rel = path.relative_to(ROOT).as_posix()
        age = months_between(doc_date, today) if doc_date else None

        newer = None
        latest = reliefweb_latest(iso3, hazard) if iso3 else None
        if latest is not None:
            api_ok = True
            if latest.get("date") and doc_date and latest["date"] > doc_date:
                newer = latest
        elif api_ok is None:
            api_ok = False

        due = (age is not None and age >= args.months) or newer is not None
        rows.append({
            "page": rel, "doc_date": doc_date, "age": age, "due": due,
            "newer": newer, "url": search_url(country, hazard),
        })

    due_rows = [r for r in rows if r["due"]]
    due_rows.sort(key=lambda r: (-(r["age"] or 0)))

    lines = ["# KB framework-PDF freshness", ""]
    note = "ReliefWeb API probe: " + ("reachable ✅" if api_ok else "unreachable (age-based prompt only)")
    lines.append(f"_{note}. Re-check = open the search link; to adopt a newer version, re-run `workflows/ingest-frameworks.mjs` for that framework._")
    lines.append("")
    if due_rows:
        lines += [f"## Due for re-check (≥ {args.months} months old, or a newer doc was spotted)", "",
                  "| page | doc date | age (mo) | newer doc spotted | re-check |", "|---|---|--:|---|---|"]
        for r in due_rows:
            nd = f"**{r['newer']['title']}** ({r['newer']['date']})" if r["newer"] else "—"
            lines.append(f"| `{r['page']}` | {r['doc_date']} | {r['age']} | {nd} | [search]({r['url']}) |")
    else:
        lines.append("✅ No endorsed framework past the re-check age.")
    report = "\n".join(lines) + "\n"

    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    sys.exit(2 if due_rows else 0)


if __name__ == "__main__":
    main()
