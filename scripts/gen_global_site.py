#!/usr/bin/env python3
"""Generate the PUBLIC cross-org AA page → ./aa_global.html (repo root).

The all-organisations counterpart of gen_public_site.py (D79): the "All organisations"
tab of the AA site. One self-contained Leaflet page — **one donut marker per country**
(segments = org share, centre = framework count) + six org filter chips + a full table.
Reads ONLY common-core fields from frameworks/ (latest versions) + external-frameworks/
— public-safe by construction.

DESIGN (dataviz method + HDX tokens, 2026-07-13 redesign):
  * form: per-country aggregation (donut + count), NOT per-framework jittered dots —
    the data's job is org identity + count, and overlapping dots encoded neither.
  * categorical slots are FIXED order: OCHA/CERF · IFRC · WFP · FAO · START · Other —
    the 20-org long tail folds into "Other" (never generated hues); full org names
    stay in popups and the table.
  * colors are HDX tokens (primary-5, error-5, brand-5, warning-6, neutral-6), except
    WFP purple — HDX has no purple family; value chosen inside the token lightness
    band. The 5 chromatic slots pass the dataviz skill's validate_palette.js:
    lightness band, chroma floor, CVD ΔE ≥ 38, contrast ≥ 3:1. "Other" is
    deliberately recessive gray (an aggregate, not a series); identity is never
    color-alone (white segment gaps, chip labels, popups, table).
  * map: no world wrap, no basemap place-labels (light_nolabels — the donuts are the
    content), bounded panning.

NO-CENTROID rule (the Nicaragua lesson): a country missing from the centroid table is
NEVER silently dropped — table row + on-page warning + CI ::warning.

Served like index.html: committed at repo root; site.yml copies it to
site/anticipatory-action/global-map.html, framed by the tab shell (gen_aa_site.py).

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

# Fixed categorical order; HDX tokens (see docstring). Other = recessive aggregate.
SLOTS = ["OCHA/CERF", "IFRC", "WFP", "FAO", "START", "Other"]
SLOT_COLORS = {"OCHA/CERF": "#1862d8", "IFRC": "#c44536", "WFP": "#8059c8",
               "FAO": "#269777", "START": "#aa7222", "Other": "#7e8e8f"}


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
            rows.append({
                "org": org, "slot": org if org in SLOT_COLORS else "Other",
                "iso3": iso, "country": CENTROIDS.get(iso, (iso,))[0],
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
            add(str(fm.get("org") or page.parent.name.upper()), fm,
                "stub" if not fm.get("trigger_summary") else "full")
    return rows


def main() -> None:
    rows = collect()
    unmapped = sorted({r["iso3"] for r in rows if r["iso3"] not in CENTROIDS})
    if unmapped:
        print(f"::warning::NO-CENTROID for {', '.join(unmapped)} — shown in table, not on map")

    countries: dict[str, dict] = {}
    for r in rows:
        if r["iso3"] not in CENTROIDS:
            continue
        name, lat, lon = CENTROIDS[r["iso3"]]
        c = countries.setdefault(r["iso3"], {"iso3": r["iso3"], "country": name,
                                             "lat": lat, "lon": lon, "fw": []})
        c["fw"].append({k: r[k] for k in ("org", "slot", "hazard", "status", "doc", "detail")})

    slot_counts = {s: sum(1 for r in rows if r["slot"] == s) for s in SLOTS}
    n_other_orgs = len({r["org"] for r in rows if r["slot"] == "Other"})
    today = datetime.date.today().isoformat()
    n_stub = sum(1 for r in rows if r["detail"] == "stub")

    warn_html = (f'<p class="warn">⚠ {len(unmapped)} countries lack map centroids: '
                 f'{html.escape(", ".join(unmapped))} (table only)</p>' if unmapped else "")

    page = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anticipatory action frameworks — all organisations</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
 body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1c2b33}
 header{padding:14px 20px;border-bottom:1px solid #e3e8ea}
 h1{font-size:19px;margin:0 0 4px} .sub{color:#5b6b73;font-size:13px;max-width:980px}
 #map{height:56vh;min-height:380px} .warn{color:#9a6700;font-size:12px;margin:6px 20px}
 .filters{padding:10px 20px 8px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
 .filters .hint{color:#8a98a0;font-size:12px;margin-left:4px}
 .chip{display:inline-flex;align-items:center;gap:7px;border:1.5px solid transparent;
  border-radius:15px;padding:4px 13px;cursor:pointer;font-size:13px;font-weight:600;
  background:#f1f4f5;color:#3c4a52;user-select:none}
 .chip .sw{width:10px;height:10px;border-radius:50%;flex:none}
 .chip .n{font-weight:400;color:#7c8a91;font-size:12px}
 .chip.off{opacity:.42;border-color:transparent}
 .chip:not(.off){border-color:currentColor}
 table{border-collapse:collapse;width:100%;font-size:13px}
 th,td{padding:6px 10px;border-bottom:1px solid #eef1f2;text-align:left;white-space:nowrap}
 th{position:sticky;top:0;background:#f7f9fa}
 .wrap{padding:0 20px 30px;overflow-x:auto}
 .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:baseline}
 .stub{color:#8a98a0;font-size:11.5px} a{color:#0f6fbe;text-decoration:none}
 .leaflet-container{background:#eef3f5}
 .donut{filter:drop-shadow(0 1px 1.5px rgba(20,40,50,.25))}
 .pop b{font-size:13.5px} .pop ul{margin:6px 0 0;padding:0 0 0 2px;list-style:none;max-height:210px;overflow-y:auto}
 .pop li{margin:2px 0;white-space:nowrap} .pop .stub{margin-left:4px}
</style></head><body>
<header>
 <h1>Anticipatory action frameworks — all organisations <span style="font-weight:400;color:#8a98a0">(beta)</span></h1>
 <div class="sub">__N__ frameworks · __NORGS__ organisations · __NC__ countries — each ring is a country:
 segments show which organisations run frameworks there, the number is how many. Generated __TODAY__ from the
 <a href="https://github.com/OCHA-DAP/ds-knowledge-base">OCHA CHD-DS knowledge base</a>
 (external inventory seeded from the <a href="https://www.anticipation-hub.org/experience/global-map">Anticipation Hub</a>;
 __NSTUB__ entries are inventory-level stubs pending enrichment).</div>
</header>
__WARN__
<div class="filters" id="filters"><span class="hint">click to toggle an organisation</span></div>
<div id="map"></div>
<div class="wrap"><table id="tbl"><thead><tr>
 <th>organisation</th><th>country</th><th>hazard</th><th>status</th><th>pre-arr. funding</th>
 <th>people</th><th>activations</th><th>doc</th><th>detail</th>
</tr></thead><tbody></tbody></table></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const COUNTRIES=__COUNTRIES__, ROWS=__ROWS__, COLORS=__COLORS__,
      SLOTS=__SLOTS__, COUNTS=__COUNTS__, OTHER_ORGS=__NOTHER__;
const map=L.map('map',{scrollWheelZoom:false,zoomSnap:.25,maxBounds:[[-62,-185],[78,200]],maxBoundsViscosity:.8});
map.fitBounds([[-42,-95],[52,150]]);   // frame the data belt, fill the container width
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
 {attribution:'&copy; OpenStreetMap &copy; CARTO',maxZoom:8,minZoom:2,noWrap:true}).addTo(map);
let active=new Set(SLOTS); let layer=L.layerGroup().addTo(map);
const fmtUsd=v=>v?(v>=1e6?'$'+(v/1e6).toFixed(1)+'M':'$'+Math.round(v/1e3)+'k'):'—';
const fmtN=v=>v?v.toLocaleString():'—';

// donut divIcon: segments per active slot with 2px white gaps, count in the centre
function donut(c){
  const fw=c.fw.filter(f=>active.has(f.slot)); if(!fw.length) return null;
  const by={}; SLOTS.forEach(s=>by[s]=0); fw.forEach(f=>by[f.slot]++);
  const n=fw.length, R=8+3.9*Math.sqrt(n), r=R*0.62, S=2*R+6, cx=S/2;
  let a0=-Math.PI/2, segs='';
  SLOTS.forEach(s=>{ if(!by[s]) return;
    const a1=a0+2*Math.PI*by[s]/n;
    const large=(a1-a0)>Math.PI?1:0;
    const p=(a,rad)=>(cx+rad*Math.cos(a))+','+(cx+rad*Math.sin(a));
    segs+=(n===by[s])
      ? `<circle cx="${cx}" cy="${cx}" r="${(R+r)/2}" fill="none" stroke="${COLORS[s]}" stroke-width="${R-r}"/>`
      : `<path d="M ${p(a0,R)} A ${R} ${R} 0 ${large} 1 ${p(a1,R)} L ${p(a1,r)} A ${r} ${r} 0 ${large} 0 ${p(a0,r)} Z" fill="${COLORS[s]}" stroke="#fff" stroke-width="2" stroke-linejoin="round"/>`;
    a0=a1;});
  const htmlS=`<svg class="donut" width="${S}" height="${S}" viewBox="0 0 ${S} ${S}">`+
    `<circle cx="${cx}" cy="${cx}" r="${r-1}" fill="#fff"/>${segs}`+
    `<text x="${cx}" y="${cx}" text-anchor="middle" dominant-baseline="central" font-size="${n>9?11:12}" font-weight="700" fill="#2b3a42">${n}</text></svg>`;
  return L.divIcon({html:htmlS,className:'',iconSize:[S,S],iconAnchor:[S/2,S/2]});
}
function popup(c){
  const fw=c.fw.filter(f=>active.has(f.slot));
  const items=fw.map(f=>`<li><span class="dot" style="background:${COLORS[f.slot]}"></span>`+
    `${f.org} — ${f.hazard} <span style="color:#7c8a91">(${f.status})</span>`+
    (f.doc?` <a href="${f.doc}" target="_blank">doc</a>`:'')+
    (f.detail==='stub'?'<span class="stub">stub</span>':'')+`</li>`).join('');
  return `<div class="pop"><b>${c.country}</b> — ${fw.length} framework${fw.length>1?'s':''}<ul>${items}</ul></div>`;
}
function render(){
  layer.clearLayers();
  COUNTRIES.forEach(c=>{
    const ic=donut(c); if(!ic) return;
    L.marker([c.lat,c.lon],{icon:ic}).addTo(layer)
     .bindTooltip(`${c.country}: ${c.fw.filter(f=>active.has(f.slot)).length}`,{direction:'top',offset:[0,-10]})
     .bindPopup(popup(c),{maxWidth:340});
  });
  const tb=document.querySelector('#tbl tbody');tb.innerHTML='';
  ROWS.filter(r=>active.has(r.slot)).forEach(r=>{
    tb.insertAdjacentHTML('beforeend',
     `<tr><td><span class="dot" style="background:${COLORS[r.slot]}"></span>${r.org}</td>`+
     `<td>${r.country}</td><td>${r.hazard}</td><td>${r.status}</td><td>${fmtUsd(r.funding)}</td>`+
     `<td>${fmtN(r.people)}</td><td>${r.n_act||'—'}</td>`+
     `<td>${r.doc?`<a href="${r.doc}" target="_blank">doc</a>`:'—'}</td>`+
     `<td>${r.detail==='stub'?'<span class="stub">stub</span>':'full'}</td></tr>`);});
}
const fl=document.getElementById('filters');
SLOTS.forEach(s=>{
  const b=document.createElement('button'); b.className='chip'; b.style.color=COLORS[s];
  const label=s==='Other'?`Other <span class="n">(${OTHER_ORGS} orgs · ${COUNTS[s]})</span>`
                         :`${s} <span class="n">(${COUNTS[s]})</span>`;
  b.innerHTML=`<span class="sw" style="background:${COLORS[s]}"></span><span style="color:#2b3a42">${label}</span>`;
  b.onclick=()=>{active.has(s)?active.delete(s):active.add(s);b.classList.toggle('off');render();};
  fl.insertBefore(b,fl.querySelector('.hint'));});
render();
</script></body></html>"""
    page = (page
            .replace("__COUNTRIES__", json.dumps(list(countries.values()), ensure_ascii=False))
            .replace("__ROWS__", json.dumps(rows, ensure_ascii=False))
            .replace("__COLORS__", json.dumps(SLOT_COLORS))
            .replace("__SLOTS__", json.dumps(SLOTS))
            .replace("__COUNTS__", json.dumps(slot_counts))
            .replace("__NOTHER__", str(n_other_orgs))
            .replace("__N__", str(len(rows)))
            .replace("__NORGS__", str(len({r['org'] for r in rows})))
            .replace("__NC__", str(len(countries)))
            .replace("__NSTUB__", str(n_stub)).replace("__TODAY__", today)
            .replace("__WARN__", warn_html))
    OUT.write_text(page, encoding="utf-8")
    print(f"aa_global.html: {len(rows)} frameworks, {len(countries)} countries, "
          f"{len({r['org'] for r in rows})} orgs, {n_stub} stubs"
          + (f", {len(unmapped)} UNMAPPED" if unmapped else ""))


if __name__ == "__main__":
    main()
