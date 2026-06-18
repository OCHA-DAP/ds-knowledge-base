#!/usr/bin/env python3
"""Generate the PUBLIC-FACING frameworks site → public-site/index.html.

A self-contained static page with:
  * a status map (active / development / retired, with activations flagged);
  * an **Active frameworks** table (current version of each, multi-country
    frameworks split to one row per country);
  * an **All versions** table (every version incl. superseded/retired).

Each row: country (full name), hazard, AOI (admin areas), status, activations,
trigger windows, pre-arranged funding, target people, the published framework
doc, and a link to the source repo.

PUBLIC-SAFE BY CONSTRUCTION: only fields already in the published framework PDF
(or public CERF/AHF announcements) are emitted. It strips internal asides
(discrepancy notes, repo-implementation values) and NEVER emits discrepancies,
source_branch/sha, code_ref, repo_completeness, dev-slot notes, or visibility.
A private source repo is shown as "🔒 private" (name withheld), not linked.

Published from the gh-pages branch (only the rendered index.html + .nojekyll).

Usage:  python scripts/gen_public_site.py   (from repo root)
"""
from __future__ import annotations
import datetime
import html
import json
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
MAXLEN = 120

ACTIVE_STATUSES = {"triggered", "endorsed", "pre-development", "development"}
STATUS_RANK = {"triggered": 0, "endorsed": 1, "pre-development": 2,
               "development": 3, "superseded": 4, "retired": 5}

# iso3 → (display name, lat, lon centroid for the map)
COUNTRY = {
    "AFG": ("Afghanistan", 33.9, 67.7), "BFA": ("Burkina Faso", 12.2, -1.6),
    "BGD": ("Bangladesh", 23.7, 90.4), "COD": ("DR Congo", -2.9, 23.6),
    "CUB": ("Cuba", 21.7, -79.5), "ETH": ("Ethiopia", 9.1, 40.5),
    "FJI": ("Fiji", -17.7, 178.0), "GTM": ("Guatemala", 15.7, -90.2),
    "HND": ("Honduras", 15.0, -86.5), "HTI": ("Haiti", 19.0, -72.3),
    "KEN": ("Kenya", 0.2, 37.9), "MDG": ("Madagascar", -18.8, 46.9),
    "MMR": ("Myanmar", 21.0, 96.0), "MOZ": ("Mozambique", -18.0, 35.5),
    "MRT": ("Mauritania", 20.5, -10.9), "NER": ("Niger", 17.6, 9.4),
    "NGA": ("Nigeria", 9.1, 8.7), "NPL": ("Nepal", 28.2, 84.0),
    "PHL": ("Philippines", 12.9, 121.8), "PLW": ("Palau", 7.5, 134.6),
    "SLV": ("El Salvador", 13.8, -88.9), "TCD": ("Chad", 15.5, 18.7),
    "VUT": ("Vanuatu", -16.5, 168.0), "YEM": ("Yemen", 15.6, 48.0),
}

# per-country CERF envelope for multi-country frameworks (doc-stated; total = sum)
COUNTRY_FUNDING_SPLIT = {
    "lac-dry-corridor": {"GTM": 4_000_000, "HND": 4_000_000, "SLV": 2_500_000},
}

# Map legend, OCHA-portfolio style: shades of blue by maturity, grey = retired.
MAP_COLOR = {"activated": "#08306b", "endorsed": "#2171b5", "development": "#9ecae1", "retired": "#b6bcc4"}
MAP_LABEL = {"activated": "Activated", "endorsed": "Endorsed", "development": "In development", "retired": "Retired"}


def map_bucket(status: str, has_acts: bool) -> str:
    if has_acts or status == "triggered":
        return "activated"
    if status == "endorsed":
        return "endorsed"
    if status in ("development", "pre-development"):
        return "development"
    return "retired"


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
    s = str(s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s*\([^()]*discrepanc[^()]*\)", "", s, flags=re.I)
    s = re.sub(r"\s*[—-]+\s*see discrepanc\w*", "", s, flags=re.I)
    s = re.sub(r"\s*\([^()]*\bin code\b[^()]*\)", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def truncate(s: str, n: int = MAXLEN) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def load_private_repos() -> set[str]:
    """Slugs flagged private/internal in the spoke-repo registry (lowercase)."""
    out = set()
    reg = ROOT / "infrastructure" / "spoke-repos.md"
    if reg.exists():
        for line in reg.read_text(encoding="utf-8").splitlines():
            if "private" in line.lower() or "internal" in line.lower():
                m = re.search(r"ocha-dap/[A-Za-z0-9._-]+", line, re.I)
                if m:
                    out.add(m.group(0).lower())
    return out


PRIVATE_REPOS = load_private_repos()


def parse_windows(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower().startswith("## trigger window"))
    except StopIteration:
        return []
    # Collect ONLY the first contiguous pipe-table under the heading. Some pages
    # put a second table (e.g. per-province thresholds) right after the windows
    # table — stop at the blank line between them so it isn't merged in.
    tbl, started = [], False
    for l in lines[start + 1:]:
        if l.strip().startswith("## "):
            break
        if l.lstrip().startswith("|"):
            started = True
            tbl.append(l)
        elif started:
            break
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
    ci = {"window": col("window"), "indicator": col("indicator"), "threshold": col("threshold")}
    out = []
    for row in tbl[2:]:
        if set(row.strip()) <= {"|", "-", " ", ":"}:
            continue
        c = cells(row)
        def g(key):
            i = ci[key]
            return clean(c[i]) if i is not None and i < len(c) else ""
        if g("window"):
            out.append({"window": g("window"), "indicator": g("indicator"), "threshold": g("threshold")})
    return out


def fmt_funding(v) -> str:
    return f"${v/1e6:.1f}M" if isinstance(v, (int, float)) and v > 0 else "—"


def fmt_people(v) -> str:
    return f"{int(v):,}" if isinstance(v, (int, float)) and v > 0 else "—"


def fmt_aoi(v) -> str:
    items = as_list(v)
    return "; ".join(clean(str(x)) for x in items) if items else "—"


def display_aoi(scope, iso3: str) -> str:
    """AOI for a single-country row; a bare country code/name → 'National'."""
    items = [clean(str(x)) for x in as_list(scope)]
    if not items:
        return "—"
    national = {iso3.upper(), cname(iso3).upper(), "NATIONAL"}
    if len(items) == 1 and items[0].upper() in national:
        return "National"
    return "; ".join(items)


def cname(iso3: str) -> str:
    return COUNTRY.get(iso3, (iso3 or "—",))[0]


def aoi_for_country(scope: list, iso3: str) -> str:
    for s in scope:
        s = str(s)
        if s.upper().startswith(iso3.upper() + ":"):
            return clean(s.split(":", 1)[1])
    return "—"


def acts_for_country(acts: list, iso3: str) -> list:
    name = cname(iso3)
    keep = []
    for a in acts:
        blob = f"{a.get('note', '')} {a.get('window', '')}"
        if iso3 in blob or (name and name in blob):
            keep.append(a)
    return keep


def acts_dates(acts: list) -> list[str]:
    return [str(a.get("date"))[:7] for a in acts if isinstance(a, dict) and a.get("date")]


def acts_cell(acts: list) -> str:
    if not acts:
        return "—"
    parts = []
    for a in acts:
        if not (isinstance(a, dict) and a.get("date")):
            continue
        d = str(a.get("date"))[:7]
        url = a.get("url")
        if url and str(url).startswith("http"):
            parts.append(f'<a href="{html.escape(str(url))}" target="_blank" rel="noopener" title="trigger announcement">{d}↗</a>')
        else:
            parts.append(d)
    return ('<span class="act">⚡ ' + ", ".join(parts) + "</span>") if parts else "—"


def trigger_html(windows: list[dict]) -> str:
    if not windows:
        return '<span class="muted">see framework doc</span>'
    out = []
    for w in windows:
        body = truncate(": ".join(p for p in (w["indicator"], w["threshold"]) if p))
        out.append(f'<div class="win"><span class="wlabel">{html.escape(w["window"])}</span> {html.escape(body)}</div>')
    return "".join(out)


def doc_link(fm: dict) -> str:
    url = fm.get("framework_doc")
    if not url or not str(url).startswith("http"):
        return '<span class="muted">not public</span>'
    return f'<a href="{html.escape(str(url))}" target="_blank" rel="noopener">{html.escape(str(fm.get("framework_doc_date") or "doc"))} ↗</a>'


def repo_cell(fm: dict) -> str:
    m = re.search(r"ocha-dap/[A-Za-z0-9._-]+", str(fm.get("source_repo", "")), re.I)
    if not m:
        return "—"
    slug = m.group(0)
    if slug.lower() in PRIVATE_REPOS:
        return '<span class="muted">🔒 private</span>'
    short = slug.split("/", 1)[1]
    return f'<a href="https://github.com/{slug}" target="_blank" rel="noopener">{html.escape(short)} ↗</a>'


def badge(status: str) -> str:
    s = html.escape(status)
    return f'<span class="badge b-{s}">{s}</span>'


def entries(fm: dict) -> list[dict]:
    """One render-entry per row: split multi-country frameworks per country."""
    countries = [str(c) for c in as_list(fm.get("country_iso3"))]
    scope = as_list(fm.get("geographic_scope"))
    acts = [a for a in as_list(fm.get("activations")) if isinstance(a, dict)]
    if len(countries) > 1:
        split = COUNTRY_FUNDING_SPLIT.get(fm.get("framework"), {})
        return [{
            "iso3": iso3, "aoi": aoi_for_country(scope, iso3),
            "funding": split.get(iso3), "target": None,
            "acts": acts_for_country(acts, iso3),
        } for iso3 in sorted(countries)]
    iso3 = countries[0] if countries else ""
    return [{
        "iso3": iso3, "aoi": display_aoi(scope, iso3),
        "funding": fm.get("prearranged_funding_usd"), "target": fm.get("target_people"),
        "acts": acts,
    }]


def row_html(fm: dict, windows: list[dict], ent: dict, *, full: bool) -> str:
    cells = [
        f'<td class="ctry">{html.escape(cname(ent["iso3"]))}</td>',
        f'<td>{html.escape(str(fm.get("hazard", "—")))}</td>',
        f'<td class="aoi">{html.escape(ent["aoi"])}</td>',
        f'<td>{badge(str(fm.get("status", "—")))}</td>',
        f'<td class="num">{html.escape(str(fm.get("framework_doc_date") or "—"))}</td>',
    ]
    if full:
        cells.append(f'<td>{html.escape(str(fm.get("version", "—")))}</td>')
    cells += [
        f'<td class="actcol">{acts_cell(ent["acts"])}</td>',
        f'<td class="trig">{trigger_html(windows)}</td>',
        f'<td class="num">{fmt_funding(ent["funding"])}</td>',
        f'<td class="num">{fmt_people(ent["target"])}</td>',
        f'<td>{doc_link(fm)}</td>',
        f'<td class="repo">{repo_cell(fm)}</td>',
    ]
    if full:
        sup = fm.get("supersedes")
        cells.append(f'<td>{html.escape(str(sup)) if sup else "—"}</td>')
    return "<tr>" + "".join(cells) + "</tr>"


def table(rows: list[str], *, full: bool, tid: str) -> str:
    head = ["Country", "Hazard", "AOI", "Status", "Endorsed"]
    if full:
        head.append("Version")
    head += ["Activations", "Trigger (per window)", "Pre-arranged", "Target people", "Framework doc", "Repo"]
    if full:
        head.append("Supersedes")
    ths = "".join(f'<th title="click to sort">{h}</th>' for h in head)
    return (f'<div class="tw"><table id="{tid}" class="ftable"><thead><tr>{ths}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def main() -> None:
    pages = []
    for p in sorted(FW.rglob("*.md")):
        if p.name in ("_TEMPLATE.md", "README.md"):
            continue
        fm = frontmatter(p)
        if not fm or fm.get("content_type") != "framework":
            continue
        pages.append((p, fm, parse_windows(p)))

    by_fwk: dict[str, list] = {}
    for rec in pages:
        by_fwk.setdefault(rec[1].get("framework", rec[0].parent.name), []).append(rec)

    # current version per framework (latest non-superseded; else latest)
    current = []
    for versions in by_fwk.values():
        cands = [v for v in versions if v[1].get("status") != "superseded"]
        current.append(max(cands or versions, key=lambda v: str(v[1].get("version", ""))))

    # ---- map markers (current version per framework, one per country) ----
    markers = []
    for _, fm, windows in current:
        trig = ""
        if windows:
            trig = truncate(": ".join(x for x in (windows[0]["indicator"], windows[0]["threshold"]) if x), 110)
        for ent in entries(fm):
            iso3 = ent["iso3"]
            if iso3 not in COUNTRY:
                continue
            name, lat, lon = COUNTRY[iso3]
            markers.append({
                "fwk": fm.get("framework", ""), "country": name, "hazard": fm.get("hazard", ""),
                "status": fm.get("status", ""), "bucket": map_bucket(fm.get("status"), bool(ent["acts"])),
                "lat": lat, "lon": lon, "acts": acts_dates(ent["acts"]), "trig": trig,
                "doc": fm.get("framework_doc") if str(fm.get("framework_doc") or "").startswith("http") else None,
            })

    # ---- tables ----
    active = sorted((rec for rec in current if rec[1].get("status") in ACTIVE_STATUSES),
                    key=lambda r: (r[1].get("hazard", ""), r[1].get("framework", "")))
    active_rows = [row_html(fm, w, e, full=False) for _, fm, w in active for e in entries(fm)]

    all_sorted = sorted(pages, key=lambda r: (r[1].get("framework", ""),
                        STATUS_RANK.get(r[1].get("status"), 9), str(r[1].get("version", ""))))
    full_rows = [row_html(fm, w, e, full=True) for _, fm, w in all_sorted for e in entries(fm)]

    n_activated = sum(1 for m in markers if m["bucket"] == "activated")
    n_end = sum(1 for m in markers if m["bucket"] == "endorsed")
    n_dev = sum(1 for m in markers if m["bucket"] == "development")
    n_ret = sum(1 for m in markers if m["bucket"] == "retired")
    markers_json = json.dumps(markers).replace("<", "\\u003c")
    map_color_json = json.dumps(MAP_COLOR)
    today = datetime.date.today().isoformat()

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OCHA Anticipatory Action Frameworks</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  :root {{ --ocha:#1a6bb5; --ink:#222; --muted:#777; --line:#e3e6ea; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); margin:0; background:#fafbfc; line-height:1.4; }}
  header {{ background:var(--ocha); color:#fff; padding:28px 24px; }}
  header h1 {{ margin:0 0 6px; font-size:24px; }}
  header p {{ margin:0; opacity:.9; font-size:14px; }}
  main {{ max-width:1560px; margin:0 auto; padding:24px; }}
  h2 {{ font-size:19px; border-bottom:2px solid var(--ocha); padding-bottom:6px; margin:32px 0 4px; }}
  .sub {{ color:var(--muted); font-size:13px; margin:0 0 12px; }}
  #map {{ height:460px; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.08); z-index:0; background:#ffffff; }}
  .leaflet-container {{ background:#ffffff; }}
  .maplegend {{ font-size:12px; line-height:1.7; background:#fff; padding:8px 10px; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,.2); }}
  .dot {{ display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:5px; vertical-align:-1px; }}
  .pinwrap {{ background:none; border:none; }}
  .pin {{ display:block; width:13px; height:13px; border-radius:50% 50% 50% 0; transform:rotate(-45deg);
         border:2px solid #fff; box-shadow:0 1px 3px rgba(0,0,0,.45); }}
  .leaflet-tooltip.maplabel {{ background:transparent; border:none; box-shadow:none; padding:0;
         color:#16324f; font-size:10.5px; font-weight:600; white-space:nowrap; line-height:1.15;
         text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 3px #fff,0 0 3px #fff; }}
  .leaflet-tooltip.maplabel::before {{ display:none; }}
  input#q {{ width:100%; max-width:420px; padding:9px 12px; border:1px solid var(--line); border-radius:6px; font-size:14px; margin:8px 0 16px; }}
  .tw {{ overflow-x:auto; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  table {{ border-collapse:collapse; width:100%; background:#fff; font-size:12px; }}
  th, td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ background:#f1f4f7; font-weight:600; position:sticky; top:0; white-space:nowrap; }}
  td.ctry {{ font-weight:600; white-space:nowrap; }}
  td.num {{ text-align:right; white-space:nowrap; }}
  td.trig {{ min-width:180px; max-width:300px; font-size:11.5px; }}
  td.aoi {{ max-width:150px; font-size:11.5px; color:#444; word-break:break-word; }}
  td.repo {{ font-size:11.5px; white-space:nowrap; }}
  td.actcol {{ white-space:nowrap; }}
  tr.frow td {{ position:static; background:#f8fafc; padding:4px 6px; }}
  tr.frow input, tr.frow select {{ width:100%; box-sizing:border-box; font-size:11px; padding:3px 4px; border:1px solid var(--line); border-radius:4px; background:#fff; }}
  .act {{ color:#b3261e; font-weight:600; font-size:12px; }}
  .win {{ padding:2px 0; border-bottom:1px dotted #eee; }}
  .win:last-child {{ border-bottom:none; }}
  .wlabel {{ display:inline-block; font-weight:600; color:var(--ocha); margin-right:4px; }}
  .muted {{ color:var(--muted); font-style:italic; }}
  a {{ color:var(--ocha); }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; white-space:nowrap; }}
  .b-triggered {{ background:#fde2e1; color:#b3261e; }}
  .b-endorsed {{ background:#e2f3e6; color:#1e7a37; }}
  .b-development {{ background:#fdf0d5; color:#9a6d0a; }}
  .b-pre-development {{ background:#e5eefb; color:#15c; }}
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
  <p>Published triggers, windows, and pre-arranged financing across the Centre for Humanitarian Data's AA portfolio. ⚡ marks frameworks that have been activated.</p>
</header>
<main>
  <h2>Map</h2>
  <p class="sub">Current version of each framework, by status. ⚡ red ring = activated at least once. Click a marker for detail.</p>
  <div id="map"></div>

  <input id="q" type="search" placeholder="Filter the tables by country, hazard, AOI…" oninput="filterRows(this.value)">

  <h2>Active frameworks</h2>
  <p class="sub">Current version of each operational framework; multi-country frameworks are split to one row per country. Click a column header to sort; type in the per-column boxes to filter.</p>
  {table(active_rows, full=False, tid="t-active")}

  <h2>All versions</h2>
  <p class="sub">Every ingested version, including superseded and retired.</p>
  <details open>
    <summary>Show full version history</summary>
    <div style="margin-top:12px">{table(full_rows, full=True, tid="t-full")}</div>
  </details>
</main>
<footer>
  Auto-generated from the DS team knowledge base on {today}. Trigger details summarized; the linked framework document is authoritative.
</footer>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  var MARKERS = {markers_json};
  var COLOR = {map_color_json};
  var map = L.map('map', {{scrollWheelZoom:false, attributionControl:false}});
  // Boundaries on a pane BELOW the marker pane, so pins are never clipped by a
  // country edge (the async-loaded layer used to draw over them).
  map.createPane('boundaries'); map.getPane('boundaries').style.zIndex = 250;
  // No tile basemap: white "sea" (#map background); every country drawn flat grey.
  fetch('https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json')
    .then(function(r) {{ return r.json(); }})
    .then(function(geo) {{
      L.geoJSON(geo, {{ pane: 'boundaries', interactive: false,
        style: function() {{ return {{color: '#c8cdd4', weight: 0.6, fillColor: '#dfe3e8', fillOpacity: 1}}; }}
      }}).addTo(map);
    }}).catch(function() {{}});
  var group = L.featureGroup().addTo(map);
  MARKERS.forEach(function(m) {{
    var icon = L.divIcon({{
      className: 'pinwrap',
      html: '<span class="pin" style="background:' + COLOR[m.bucket] + '"></span>',
      iconSize: [16, 16], iconAnchor: [8, 16], popupAnchor: [0, -15], tooltipAnchor: [6, -8]
    }});
    var mk = L.marker([m.lat, m.lon], {{icon: icon}});
    var hz = (m.hazard || '').replace('tropical-cyclone', 'tropical cyclones').replace(/-/g, ' ');
    mk.bindTooltip('<b>' + m.country + '</b><br>' + hz, {{permanent: true, direction: 'right', className: 'maplabel'}});
    var html = '<b>' + m.fwk + '</b> &middot; ' + m.country + '<br>' + m.hazard + ' &middot; ' + m.status +
      (m.acts && m.acts.length ? '<br>⚡ activated: ' + m.acts.join(', ') : '') +
      (m.trig ? '<br><small>' + m.trig + '</small>' : '') +
      (m.doc ? '<br><a href="' + m.doc + '" target="_blank" rel="noopener">framework doc ↗</a>' : '');
    mk.bindPopup(html);
    mk.addTo(group);
  }});
  if (MARKERS.length) map.fitBounds(group.getBounds(), {{padding: [45, 45], maxZoom: 5}});
  else map.setView([12, 30], 2);
  var legend = L.control({{position:'bottomleft'}});
  legend.onAdd = function() {{
    var d = L.DomUtil.create('div', 'maplegend');
    d.innerHTML = '<b>Framework</b><br>' +
      '<span class="dot" style="background:' + COLOR.activated + '"></span>Activated ({n_activated})<br>' +
      '<span class="dot" style="background:' + COLOR.endorsed + '"></span>Endorsed ({n_end})<br>' +
      '<span class="dot" style="background:' + COLOR.development + '"></span>In development ({n_dev})<br>' +
      '<span class="dot" style="background:' + COLOR.retired + '"></span>Retired ({n_ret})';
    return d;
  }};
  legend.addTo(map);

  // ---- sortable + per-column filterable tables ----
  function numval(s) {{
    s = s.replace(/[,\\s]/g, '');
    var m = s.match(/-?\\d+\\.?\\d*/);
    if (!m) return null;
    var n = parseFloat(m[0]);
    if (/m/i.test(s)) n *= 1e6; else if (/k/i.test(s)) n *= 1e3;
    return n;
  }}
  function refilter() {{
    var g = (document.getElementById('q').value || '').trim().toLowerCase();
    document.querySelectorAll('table.ftable').forEach(function(table) {{
      var fs = [];
      table.querySelectorAll('.colf').forEach(function(c) {{
        var v = (c.value || '').trim().toLowerCase();
        if (v) fs.push({{col: +c.dataset.col, v: v, eq: c.dataset.type === 'eq'}});
      }});
      Array.prototype.forEach.call(table.tBodies[0].rows, function(tr) {{
        var show = !g || tr.textContent.toLowerCase().indexOf(g) >= 0;
        if (show) {{
          for (var k = 0; k < fs.length; k++) {{
            var cell = tr.cells[fs[k].col].textContent.trim().toLowerCase();
            if (fs[k].eq ? cell !== fs[k].v : cell.indexOf(fs[k].v) < 0) {{ show = false; break; }}
          }}
        }}
        tr.style.display = show ? '' : 'none';
      }});
    }});
  }}
  function distinctCol(table, idx) {{
    var set = {{}};
    Array.prototype.forEach.call(table.tBodies[0].rows, function(tr) {{
      var t = tr.cells[idx].textContent.trim();
      if (t && t !== '—') set[t] = 1;
    }});
    return Object.keys(set).sort();
  }}
  function sortTable(table, col, th) {{
    var tb = table.tBodies[0], rows = Array.prototype.slice.call(tb.rows);
    var dir = (table.getAttribute('data-sc') == col && table.getAttribute('data-sd') == '1') ? -1 : 1;
    var allnum = rows.every(function(r) {{ var t = r.cells[col].textContent.trim(); return t === '' || t === '—' || numval(t) !== null; }});
    rows.sort(function(a, b) {{
      var x = a.cells[col].textContent.trim(), y = b.cells[col].textContent.trim();
      if (allnum) {{ var nx = numval(x), ny = numval(y); nx = nx === null ? -Infinity : nx; ny = ny === null ? -Infinity : ny; return (nx - ny) * dir; }}
      return x.localeCompare(y) * dir;
    }});
    rows.forEach(function(r) {{ tb.appendChild(r); }});
    table.setAttribute('data-sc', col); table.setAttribute('data-sd', dir == 1 ? '1' : '0');
    table.querySelectorAll('thead tr:first-child th').forEach(function(h, i) {{
      h.textContent = h.textContent.replace(/ [▲▼]$/, '') + (i == col ? (dir == 1 ? ' ▲' : ' ▼') : '');
    }});
  }}
  document.querySelectorAll('table.ftable').forEach(function(table) {{
    var hrow = table.tHead.rows[0], n = hrow.cells.length;
    var frow = table.tHead.insertRow(); frow.className = 'frow';
    for (var i = 0; i < n; i++) {{
      (function(idx) {{
        var label = hrow.cells[idx].textContent.trim();
        hrow.cells[idx].style.cursor = 'pointer';
        hrow.cells[idx].addEventListener('click', function() {{ sortTable(table, idx, this); }});
        var fc = frow.insertCell(), ctrl;
        if (label === 'Hazard' || label === 'Status') {{
          ctrl = document.createElement('select');
          ctrl.innerHTML = '<option value="">all</option>';
          distinctCol(table, idx).forEach(function(v) {{
            var o = document.createElement('option'); o.value = v.toLowerCase(); o.textContent = v; ctrl.appendChild(o);
          }});
          ctrl.dataset.type = 'eq';
          ctrl.addEventListener('change', refilter);
        }} else if (label === 'Country') {{
          var dl = document.createElement('datalist'); dl.id = 'dl-' + table.id + '-' + idx;
          distinctCol(table, idx).forEach(function(v) {{ var o = document.createElement('option'); o.value = v; dl.appendChild(o); }});
          fc.appendChild(dl);
          ctrl = document.createElement('input');
          ctrl.setAttribute('list', dl.id); ctrl.placeholder = 'country…'; ctrl.dataset.type = 'contains';
          ctrl.addEventListener('input', refilter);
        }} else if (label === 'AOI') {{
          ctrl = document.createElement('input');
          ctrl.placeholder = 'filter…'; ctrl.dataset.type = 'contains';
          ctrl.addEventListener('input', refilter);
        }} else {{
          return;  // no filter control for other columns
        }}
        ctrl.className = 'colf'; ctrl.dataset.col = idx;
        fc.appendChild(ctrl);
      }})(i);
    }}
  }});
  function filterRows() {{ refilter(); }}
</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(active_rows)} active rows, {len(full_rows)} total rows, "
          f"{len(markers)} map markers ({n_activated} activated / {n_end} endorsed / {n_dev} dev / {n_ret} retired).")


if __name__ == "__main__":
    main()
