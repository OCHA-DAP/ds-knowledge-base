#!/usr/bin/env python3
"""Generate the PUBLIC cross-org AA page → ./aa_global.html (repo root).

The all-organisations counterpart of gen_public_site.py (D79, revised 2026-07-13):
its own TAB on the AA site — the OCHA map/stats pages and their generators are untouched;
this page only ADDS a view. One
self-contained Leaflet page: every AA framework across every org (OCHA/CERF from
frameworks/ latest versions + external-frameworks/), org-coloured markers, filterable
table. Reads ONLY common-core fields — public-safe by construction (doc links, funding,
people; never repo internals).

External pages vary in depth: `detail: stub` rows are inventory-level (Anticipation Hub
core facts, enrichment pending) and say so.

NO-CENTROID rule (the Nicaragua lesson): a country missing from the centroid table is
NEVER silently dropped — it still gets a table row, and the page + CI warn.

Served like index.html: committed at repo root, copied by site.yml to
site/anticipatory-action/global-map.html and framed by the "All organisations" tab
(gen_aa_site.py shell → global.html) on the AA site.

Usage:  python scripts/gen_global_site.py   (repo root; needs pyyaml)
"""
from __future__ import annotations

import datetime
import html
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from gen_public_site import COUNTRY as OCHA_COUNTRY  # noqa: E402 — (name, lat, lon) per ISO3

OUT = ROOT / "aa_global.html"

# Approximate country centroids for Hub countries outside the OCHA portfolio dict.
EXTRA_COUNTRY = {
    "AGO": ("Angola", -12.3, 17.5), "ARG": ("Argentina", -34.6, -64.2),
    "BDI": ("Burundi", -3.4, 29.9), "BOL": ("Bolivia", -16.7, -64.7),
    "COL": ("Colombia", 4.1, -73.1), "COM": ("Comoros", -11.9, 43.9),
    "CRI": ("Costa Rica", 9.9, -84.1), "DJI": ("Djibouti", 11.8, 42.6),
    "DOM": ("Dominican Republic", 18.9, -70.5), "ECU": ("Ecuador", -1.6, -78.4),
    "GRC": ("Greece", 39.3, 22.5), "IDN": ("Indonesia", -2.2, 117.9),
    "IRQ": ("Iraq", 33.0, 43.7), "KAZ": ("Kazakhstan", 48.0, 66.9),
    "KGZ": ("Kyrgyzstan", 41.5, 74.5), "KHM": ("Cambodia", 12.5, 104.9),
    "LAO": ("Laos", 18.5, 103.8), "LBN": ("Lebanon", 33.9, 35.9),
    "LSO": ("Lesotho", -29.6, 28.2), "MLI": ("Mali", 17.4, -3.5),
    "MNG": ("Mongolia", 46.9, 103.1), "PAK": ("Pakistan", 30.1, 69.4),
    "PER": ("Peru", -9.2, -75.0), "SDN": ("Sudan", 15.6, 30.2),
    "SEN": ("Senegal", 14.4, -14.5), "SWZ": ("Eswatini", -26.5, 31.5),
    "TJK": ("Tajikistan", 38.9, 71.3), "TLS": ("Timor-Leste", -8.8, 125.9),
    "UGA": ("Uganda", 1.4, 32.3), "VNM": ("Vietnam", 16.0, 106.3),
    "ZMB": ("Zambia", -13.5, 27.9), "ZWE": ("Zimbabwe", -19.0, 29.9),
}
CENTROIDS = {**EXTRA_COUNTRY, **OCHA_COUNTRY}

ORG_COLORS = {  # the big five get stable colours; everyone else shares a neutral
    "OCHA/CERF": "#1f77e0", "IFRC": "#d62728", "WFP": "#7a4de8",
    "FAO": "#2c9e4b", "START": "#e8871a",
}
OTHER_COLOR = "#6b7280"


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    try:
        return yaml.safe_load(text[3:end]) or {} if end != -1 else None
    except yaml.YAMLError:
        return None


def as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def collect() -> list[dict]:
    rows = []

    def add(org: str, fm: dict, detail: str) -> None:
        for iso in as_list(fm.get("country_iso3")):
            iso = str(iso)
            name = CENTROIDS.get(iso, (iso, None, None))[0]
            rows.append({
                "org": org, "iso3": iso, "country": name,
                "hazard": str(fm.get("hazard") or "—"),
                "status": str(fm.get("status") or "unknown"),
                "funding": fm.get("prearranged_funding_usd"),
                "people": fm.get("target_people"),
                "n_act": len(as_list(fm.get("activations"))),
                "doc": fm.get("framework_doc") or "",
                "detail": detail,
            })

    for fw_dir in sorted(p for p in (ROOT / "frameworks").iterdir() if p.is_dir()):
        pages = [p for p in fw_dir.glob("*.md") if p.name != "README.md"]
        dated = sorted(p for p in pages if p.stem[:4].isdigit())
        page = dated[-1] if dated else (sorted(pages)[-1] if pages else None)
        if page and (fm := parse_frontmatter(page)) and fm.get("content_type") == "framework":
            add("OCHA/CERF", fm, "full")
    for page in sorted((ROOT / "external-frameworks").glob("*/*.md")):
        fm = parse_frontmatter(page)
        if fm and fm.get("content_type") == "framework-external":
            detail = "stub" if not fm.get("trigger_summary") else "full"
            add(str(fm.get("org") or page.parent.name.upper()), fm, detail)
    return rows


def main() -> None:
    rows = collect()
    unmapped = sorted({r["iso3"] for r in rows if r["iso3"] not in CENTROIDS})
    if unmapped:
        print(f"::warning::NO-CENTROID for {', '.join(unmapped)} — shown in table, not on map")

    markers = []
    for r in rows:
        if r["iso3"] in CENTROIDS:
            _, lat, lon = CENTROIDS[r["iso3"]]
            markers.append({**r, "lat": lat, "lon": lon,
                            "color": ORG_COLORS.get(r["org"], OTHER_COLOR)})
    orgs = sorted({r["org"] for r in rows},
                  key=lambda o: (o not in ORG_COLORS, o))
    today = datetime.date.today().isoformat()
    n_stub = sum(1 for r in rows if r["detail"] == "stub")

    data_json = json.dumps(markers, ensure_ascii=False)
    org_json = json.dumps({o: ORG_COLORS.get(o, OTHER_COLOR) for o in orgs}, ensure_ascii=False)
    warn_html = (f'<p class="warn">⚠ {len(unmapped)} countries lack map centroids: '
                 f'{html.escape(", ".join(unmapped))} (table only)</p>' if unmapped else "")

    OUT.write_text("""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anticipatory action frameworks — all organisations</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
 body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1c2b33}
 header{padding:14px 20px;border-bottom:1px solid #e3e8ea}
 h1{font-size:19px;margin:0 0 4px} .sub{color:#5b6b73;font-size:13px}
 #map{height:52vh;min-height:340px} .warn{color:#9a6700;font-size:12px;margin:6px 20px}
 .filters{padding:8px 20px;display:flex;gap:6px;flex-wrap:wrap}
 .filters button{border:1px solid #cfd8dc;background:#fff;border-radius:14px;padding:3px 11px;cursor:pointer;font-size:12.5px}
 .filters button.on{color:#fff;border-color:transparent}
 table{border-collapse:collapse;width:100%;font-size:13px}
 th,td{padding:6px 10px;border-bottom:1px solid #eef1f2;text-align:left;white-space:nowrap}
 th{position:sticky;top:0;background:#f7f9fa;cursor:pointer}
 .wrap{padding:0 20px 30px;overflow-x:auto}
 .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}
 .stub{color:#8a98a0;font-size:11.5px} a{color:#0f6fbe;text-decoration:none}
 .leaflet-container{background:#fff}
</style></head><body>
<header>
 <h1>Anticipatory action frameworks — all organisations <span style="font-weight:400;color:#8a98a0">(beta)</span></h1>
 <div class="sub">__N__ frameworks · __NORGS__ organisations · generated __TODAY__ from the
 <a href="https://github.com/OCHA-DAP/ds-knowledge-base">OCHA CHD-DS knowledge base</a>
 (external inventory seeded from the <a href="https://www.anticipation-hub.org/experience/global-map">Anticipation Hub</a>;
 __NSTUB__ entries are inventory-level stubs pending enrichment).</div>
</header>
__WARN__
<div class="filters" id="filters"></div>
<div id="map"></div>
<div class="wrap"><table id="tbl"><thead><tr>
 <th>org</th><th>country</th><th>hazard</th><th>status</th><th>pre-arr. funding</th>
 <th>people</th><th>activations</th><th>doc</th><th>detail</th>
</tr></thead><tbody></tbody></table></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const DATA=__DATA__, ORGS=__ORGS__;
const map=L.map('map',{scrollWheelZoom:false}).setView([12,15],2);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
 {attribution:'&copy; OpenStreetMap &copy; CARTO',maxZoom:8}).addTo(map);
let active=new Set(Object.keys(ORGS)); let layer=L.layerGroup().addTo(map);
const fmtUsd=v=>v?(v>=1e6?'$'+(v/1e6).toFixed(1)+'M':'$'+Math.round(v/1e3)+'k'):'—';
const fmtN=v=>v?v.toLocaleString():'—';
function jitter(rows){const seen={};return rows.map(r=>{const k=r.iso3;const i=(seen[k]=(seen[k]||0)+1)-1;
 const a=i*2.4, d=i?0.55+0.13*i:0;return {...r,jlat:r.lat+d*Math.sin(a),jlon:r.lon+d*Math.cos(a)};});}
function render(){
 layer.clearLayers();
 jitter(DATA.filter(r=>active.has(r.org))).forEach(r=>{
  L.circleMarker([r.jlat,r.jlon],{radius:6,color:r.color,fillColor:r.color,fillOpacity:.75,weight:1})
   .bindPopup(`<b>${r.org}</b> — ${r.country} ${r.hazard}<br>status: ${r.status} · activations: ${r.n_act}`+
    `<br>funding: ${fmtUsd(r.funding)} · people: ${fmtN(r.people)}`+
    (r.doc?`<br><a href="${r.doc}" target="_blank">framework document</a>`:'')+
    (r.detail==='stub'?'<br><i>inventory-level stub</i>':''))
   .addTo(layer);});
 const tb=document.querySelector('#tbl tbody');tb.innerHTML='';
 DATA.filter(r=>active.has(r.org)).forEach(r=>{
  tb.insertAdjacentHTML('beforeend',`<tr><td><span class="dot" style="background:${r.color}"></span>${r.org}</td>`+
   `<td>${r.country}</td><td>${r.hazard}</td><td>${r.status}</td><td>${fmtUsd(r.funding)}</td>`+
   `<td>${fmtN(r.people)}</td><td>${r.n_act||'—'}</td>`+
   `<td>${r.doc?`<a href="${r.doc}" target="_blank">doc</a>`:'—'}</td>`+
   `<td>${r.detail==='stub'?'<span class="stub">stub</span>':'full'}</td></tr>`);});
}
const fl=document.getElementById('filters');
Object.entries(ORGS).forEach(([o,c])=>{const b=document.createElement('button');
 b.textContent=o;b.className='on';b.style.background=c;b.style.color='#fff';
 b.onclick=()=>{active.has(o)?active.delete(o):active.add(o);
  b.classList.toggle('on');b.style.background=b.classList.contains('on')?c:'#fff';
  b.style.color=b.classList.contains('on')?'#fff':'#444';render();};fl.appendChild(b);});
render();
</script></body></html>"""
        .replace("__DATA__", data_json).replace("__ORGS__", org_json)
        .replace("__N__", str(len(rows))).replace("__NORGS__", str(len(orgs)))
        .replace("__NSTUB__", str(n_stub)).replace("__TODAY__", today)
        .replace("__WARN__", warn_html), encoding="utf-8")
    print(f"aa_global.html: {len(rows)} rows, {len(orgs)} orgs, {n_stub} stubs"
          + (f", {len(unmapped)} UNMAPPED" if unmapped else ""))


if __name__ == "__main__":
    main()
