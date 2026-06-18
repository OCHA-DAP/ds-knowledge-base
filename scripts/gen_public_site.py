#!/usr/bin/env python3
"""Generate the PUBLIC-FACING frameworks site → public-site/index.html.

A self-contained static page with two tables:
  1. **Active frameworks** — the current version of each framework (excludes
     superseded + retired), with trigger windows, validity/lead-time, funding,
     target people, and a link to the published framework doc.
  2. **All versions** — every version incl. superseded/retired.

PUBLIC-SAFE BY CONSTRUCTION: only fields that already appear in the published
framework PDF (or public CERF/AHF announcements) are emitted — trigger
thresholds, windows, funding, targets, the public doc link. It deliberately
DROPS every internal-only field: discrepancies, source_repo/branch, code_ref,
repo_completeness, dev-slot/operational notes, open questions, raw_extract,
operated_by, visibility, last_synced. Do not add those here.

This is what gets published to GitHub Pages (the gh-pages branch holds ONLY the
rendered index.html, never the internal markdown).

Usage:  python scripts/gen_public_site.py   (from repo root)
"""
from __future__ import annotations
import datetime
import html
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    import sys
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
FW = ROOT / "frameworks"
OUT = ROOT / "public-site" / "index.html"
MAXLEN = 200  # truncate long trigger cells; full detail is in the linked doc

STATUS_RANK = {"triggered": 0, "endorsed": 1, "pre-development": 2,
               "development": 3, "superseded": 4, "retired": 5}
ACTIVE_STATUSES = {"triggered", "endorsed", "pre-development", "development"}


def frontmatter(path: Path) -> dict | None:
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return None
    e = t.find("\n---", 3)
    if e == -1:
        return None
    try:
        return yaml.safe_load(t[3:e]) or {}
    except yaml.YAMLError:
        return None


def as_list(v) -> list:
    return [] if v is None else (v if isinstance(v, list) else [v])


def clean(s: str) -> str:
    """Strip markdown decoration → plain text, collapse whitespace.

    Also drops internal editorial asides that reference KB-only discrepancy
    notes (e.g. "(see discrepancy note)") — those don't belong on the public
    page and point at content that isn't published."""
    s = str(s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)   # [text](url) → text
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s*\([^()]*discrepanc[^()]*\)", "", s, flags=re.I)   # (… discrepancy …)
    s = re.sub(r"\s*[—-]+\s*see discrepanc\w*", "", s, flags=re.I)    # — see discrepancies
    s = re.sub(r"\s*\([^()]*\bin code\b[^()]*\)", "", s, flags=re.I)  # (… in code) — repo impl aside
    s = re.sub(r"\s+", " ", s).strip()
    return s


def truncate(s: str, n: int = MAXLEN) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def parse_windows(path: Path) -> list[dict]:
    """Pull the '## Trigger windows' markdown table into row dicts."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower().startswith("## trigger window"))
    except StopIteration:
        return []
    tbl = []
    for l in lines[start + 1:]:
        if l.strip().startswith("## "):
            break
        if l.lstrip().startswith("|"):
            tbl.append(l)
    if len(tbl) < 2:
        return []
    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]
    header = [h.lower() for h in cells(tbl[0])]

    def col(*keys):
        for i, h in enumerate(header):
            if any(k in h for k in keys):
                return i
        return None
    ci = {"window": col("window"), "indicator": col("indicator"),
          "threshold": col("threshold"), "lead": col("lead")}
    out = []
    for row in tbl[2:]:                      # skip header + separator
        if set(row.strip()) <= {"|", "-", " ", ":"}:
            continue
        c = cells(row)
        def g(key):
            i = ci[key]
            return clean(c[i]) if i is not None and i < len(c) else ""
        w = g("window")
        if not w:
            continue
        out.append({"window": w, "indicator": g("indicator"),
                    "threshold": g("threshold"), "lead": g("lead")})
    return out


def fmt_country(v) -> str:
    return "/".join(str(x) for x in as_list(v)) or "—"


def fmt_funding(v) -> str:
    return f"${v/1e6:.1f}M" if isinstance(v, (int, float)) and v > 0 else "—"


def fmt_people(v) -> str:
    if isinstance(v, (int, float)) and v > 0:
        return f"{int(v):,}"
    return "—"


def fmt_aoi(v) -> str:
    items = as_list(v)
    return "; ".join(clean(str(x)) for x in items) if items else "—"


def trigger_html(windows: list[dict]) -> str:
    if not windows:
        return '<span class="muted">see framework doc</span>'
    parts = []
    for w in windows:
        ind = w["indicator"]
        thr = w["threshold"]
        body = truncate(": ".join(p for p in (ind, thr) if p))
        parts.append(f'<div class="win"><span class="wlabel">{html.escape(w["window"])}</span> '
                     f'{html.escape(body)}</div>')
    return "".join(parts)


def doc_link(fm: dict) -> str:
    url = fm.get("framework_doc")
    if not url or not str(url).startswith("http"):
        return '<span class="muted">not public</span>'
    date = fm.get("framework_doc_date") or "doc"
    return f'<a href="{html.escape(str(url))}" target="_blank" rel="noopener">{html.escape(str(date))} ↗</a>'


def badge(status: str) -> str:
    s = html.escape(status)
    return f'<span class="badge b-{s}">{s}</span>'


def row_html(fm: dict, windows: list[dict], *, full: bool) -> str:
    fwk = fm.get("framework", "—")
    cells = [
        f'<td>{html.escape(fmt_country(fm.get("country_iso3")))}</td>',
        f'<td class="fwk">{html.escape(str(fwk))}</td>',
        f'<td>{html.escape(str(fm.get("hazard", "—")))}</td>',
        f'<td class="aoi">{html.escape(fmt_aoi(fm.get("geographic_scope")))}</td>',
    ]
    if full:
        cells.append(f'<td>{html.escape(str(fm.get("version", "—")))}</td>')
    cells += [
        f'<td>{badge(str(fm.get("status", "—")))}</td>',
        f'<td class="trig">{trigger_html(windows)}</td>',
        f'<td class="num">{fmt_funding(fm.get("prearranged_funding_usd"))}</td>',
        f'<td class="num">{fmt_people(fm.get("target_people"))}</td>',
        f'<td>{doc_link(fm)}</td>',
    ]
    if full:
        sup = fm.get("supersedes")
        cells.append(f'<td>{html.escape(str(sup)) if sup else "—"}</td>')
    return "<tr>" + "".join(cells) + "</tr>"


def table(rows_html: list[str], *, full: bool) -> str:
    head = ["Country", "Framework", "Hazard", "AOI"]
    if full:
        head.append("Version")
    head += ["Status", "Trigger (per window)",
             "Pre-arranged", "Target people", "Framework doc"]
    if full:
        head.append("Supersedes")
    ths = "".join(f"<th>{h}</th>" for h in head)
    return (f'<table><thead><tr>{ths}</tr></thead><tbody>'
            + "".join(rows_html) + "</tbody></table>")


def main() -> None:
    pages = []
    for p in sorted(FW.rglob("*.md")):
        if p.name in ("_TEMPLATE.md", "README.md"):
            continue
        fm = frontmatter(p)
        if not fm or fm.get("content_type") != "framework":
            continue
        pages.append((p, fm, parse_windows(p)))

    # current version per framework folder: prefer an active status, else latest version
    by_fwk: dict[str, list] = {}
    for p, fm, w in pages:
        by_fwk.setdefault(fm.get("framework", p.parent.name), []).append((p, fm, w))
    active = []
    for fwk, versions in by_fwk.items():
        cands = [v for v in versions if v[1].get("status") in ACTIVE_STATUSES]
        if not cands:
            continue  # framework is entirely superseded/retired → full table only
        cands.sort(key=lambda v: str(v[1].get("version", "")), reverse=True)
        active.append(cands[0])

    active.sort(key=lambda v: (v[1].get("hazard", ""), str(v[1].get("country_iso3", "")), v[1].get("framework", "")))
    all_versions = sorted(
        pages,
        key=lambda v: (v[1].get("framework", ""), STATUS_RANK.get(v[1].get("status"), 9), str(v[1].get("version", ""))),
    )

    active_rows = [row_html(fm, w, full=False) for _, fm, w in active]
    full_rows = [row_html(fm, w, full=True) for _, fm, w in all_versions]
    today = datetime.date.today().isoformat()

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OCHA Anticipatory Action Frameworks</title>
<style>
  :root {{ --ocha:#1a6bb5; --ink:#222; --muted:#777; --line:#e3e6ea; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); margin:0; background:#fafbfc; line-height:1.4; }}
  header {{ background:var(--ocha); color:#fff; padding:28px 24px; }}
  header h1 {{ margin:0 0 6px; font-size:24px; }}
  header p {{ margin:0; opacity:.9; font-size:14px; }}
  main {{ max-width:1500px; margin:0 auto; padding:24px; }}
  h2 {{ font-size:19px; border-bottom:2px solid var(--ocha); padding-bottom:6px; margin:32px 0 4px; }}
  .sub {{ color:var(--muted); font-size:13px; margin:0 0 12px; }}
  input#q {{ width:100%; max-width:420px; padding:9px 12px; border:1px solid var(--line);
            border-radius:6px; font-size:14px; margin:8px 0 16px; }}
  table {{ border-collapse:collapse; width:100%; background:#fff; font-size:13px;
          box-shadow:0 1px 3px rgba(0,0,0,.06); border-radius:8px; overflow:hidden; }}
  th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ background:#f1f4f7; font-weight:600; position:sticky; top:0; white-space:nowrap; }}
  td.fwk {{ font-weight:600; white-space:nowrap; }}
  td.num {{ text-align:right; white-space:nowrap; }}
  td.trig {{ min-width:230px; max-width:440px; }}
  td.aoi {{ max-width:260px; font-size:12px; color:#444; }}
  .win {{ padding:2px 0; border-bottom:1px dotted #eee; }}
  .win:last-child {{ border-bottom:none; }}
  .wlabel {{ display:inline-block; font-weight:600; color:var(--ocha); margin-right:4px; }}
  .muted {{ color:var(--muted); font-style:italic; }}
  a {{ color:var(--ocha); }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; white-space:nowrap; }}
  .b-triggered {{ background:#fde2e1; color:#b3261e; }}
  .b-endorsed {{ background:#e2f3e6; color:#1e7a37; }}
  .b-development {{ background:#eceff3; color:#555; }}
  .b-pre-development {{ background:#e5eefb; color:#1a5; }}
  .b-superseded {{ background:#f3f0e2; color:#8a6d1e; }}
  .b-retired {{ background:#e8e8e8; color:#666; }}
  details {{ margin-top:4px; }}
  summary {{ cursor:pointer; font-weight:600; color:var(--ocha); }}
  footer {{ color:var(--muted); font-size:12px; padding:24px; text-align:center; }}
</style>
</head>
<body>
<header>
  <h1>OCHA Anticipatory Action Frameworks</h1>
  <p>Published triggers, windows, and pre-arranged financing across the Centre for Humanitarian Data's AA portfolio. Click a date to open the framework document.</p>
</header>
<main>
  <input id="q" type="search" placeholder="Filter by country, hazard, framework…" oninput="filterRows(this.value)">

  <h2>Active frameworks</h2>
  <p class="sub">The current version of each framework ({len(active_rows)} frameworks). Excludes superseded and retired versions.</p>
  {table(active_rows, full=False)}

  <h2>All versions</h2>
  <p class="sub">Every ingested version, including superseded and retired ({len(full_rows)} versions).</p>
  <details open>
    <summary>Show full version history</summary>
    <div style="margin-top:12px">{table(full_rows, full=True)}</div>
  </details>
</main>
<footer>
  Auto-generated from the DS team knowledge base on {today}. Trigger details summarized; the linked framework document is authoritative.
</footer>
<script>
  function filterRows(q) {{
    q = q.trim().toLowerCase();
    document.querySelectorAll('table tbody tr').forEach(function(tr) {{
      tr.style.display = !q || tr.textContent.toLowerCase().includes(q) ? '' : 'none';
    }});
  }}
</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(active_rows)} active, {len(full_rows)} total versions.")


if __name__ == "__main__":
    main()
