#!/usr/bin/env python3
"""Generate the PUBLIC cross-org AA page → ./aa_global.html (repo root).

The all-organisations counterpart of gen_public_site.py (D79): the "All organisations"
tab of the AA site. **Same map engine as the OCHA status map** — a static,
CSS-scaled Leaflet poster (no drag/zoom), shaded country polygons, one HTML callout
per country (name + one hazard icon-row per country-hazard combo) placed in open
space by the same eject/separate force layout, leader line to a dot on the country.
Clicking a hazard icon opens a popover listing which organisations cover that combo
(doc links; stubs marked). Six hazard chips above the map filter + act as legend.

Classification is the COUNTRY-HAZARD COMBO (framework identity, D62) — deflating
org-crowded counts (206 pages → 121 combos). Colors: HDX tokens validated with the
dataviz palette checker (blue=flood, amber=drought, red=heat, purple=cold,
teal=cyclone, recessive gray=other/multi); hazard glyphs (shared HAZARD_SVG) keep
identity non-color-alone.

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
# shared with the OCHA status map: centroids, callout seed directions, hazard glyphs
from gen_public_site import COUNTRY as OCHA_COUNTRY  # noqa: E402
from gen_public_site import DIRECTIONS as OCHA_DIRECTIONS  # noqa: E402
from gen_public_site import HAZARD_SVG  # noqa: E402

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

# Callout seed direction for countries the OCHA map doesn't place (ocean-/open-space-ward).
EXTRA_DIRECTIONS = {
    "AGO": (-1, 0.5), "ARG": (1, 0.5), "BDI": (-1, 0.8), "BOL": (-1, 0.8),
    "COL": (-1, -0.5), "COM": (1, 0.4), "CRI": (-1, 0.6), "DJI": (1, -0.5),
    "DOM": (1, -0.7), "ECU": (-1, 0.1), "GRC": (-0.5, -1), "IDN": (0.6, 1),
    "IRQ": (0.4, -0.9), "KAZ": (-0.4, -1), "KGZ": (1, -0.5), "KHM": (0.3, 1),
    "LAO": (0.2, -1), "LBN": (-1, -0.4), "LSO": (0.6, 1), "MLI": (0, -1),
    "MNG": (0.3, -1), "PAK": (0.5, -1), "PER": (-1, 0.3), "SDN": (0.4, -0.8),
    "SEN": (-1, -0.3), "SWZ": (1, 0.6), "TJK": (1, 0.2), "TLS": (1, 0.8),
    "UGA": (-0.5, -1), "VNM": (1, 0.4), "ZMB": (-0.8, 0.9), "ZWE": (0.5, 1),
}
# overrides applied LAST — problem placements observed at review (2026-07-13):
# aim rings at nearby ocean/uncovered land so the label reads as the country's
DIR_OVERRIDES = {
    "MMR": (-0.8, 0.9),   # Bay of Bengal (SW)
    "SSD": (-1, -0.3),    # CAR (uncovered, W)
    "PER": (-1, 0.4),     # Pacific (W)
    "BDI": (1, 0.7),      # Tanzania (uncovered, SE)
    "COD": (-1, 0.2),     # Congo/Gabon (uncovered, W)
    "PAK": (-0.3, 1),     # Arabian Sea (S)
    "NPL": (0.2, -1),     # Tibetan plateau (uncovered, N)
    "UGA": (0.9, -0.6),   # toward L. Turkana gap (NE)
    "TJK": (1, 0.5),      # toward W China (uncovered, E)
    "KGZ": (1, -0.4),
}
DIRECTIONS = {**EXTRA_DIRECTIONS, **OCHA_DIRECTIONS, **DIR_OVERRIDES}

# Fixed categorical order — hazard slots (see docstring). Other = recessive fold.
SLOTS = ["Drought", "Flood", "Tropical cyclone", "Heatwave", "Cold wave", "Other / multi"]
HAZARD_SLOT = {"drought": "Drought", "flood": "Flood", "tropical-cyclone": "Tropical cyclone",
               "heatwave": "Heatwave", "cold-wave": "Cold wave"}
SLOT_COLORS = {"Drought": "#aa7222", "Flood": "#1862d8", "Tropical cyclone": "#269777",
               "Heatwave": "#c44536", "Cold wave": "#8059c8", "Other / multi": "#7e8e8f"}


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
                "org": org,
                "slot": HAZARD_SLOT.get(str(fm.get("hazard")), "Other / multi"),
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

    # per-country markers: one item per country-hazard COMBO, orgs listed within
    countries: dict[str, dict] = {}
    for r in rows:
        if r["iso3"] not in CENTROIDS:
            continue
        name, lat, lon = CENTROIDS[r["iso3"]]
        c = countries.setdefault(r["iso3"], {
            "iso3": r["iso3"], "country": name, "lat": lat, "lon": lon,
            "dir": list(DIRECTIONS.get(r["iso3"], (1, -0.4))), "_combos": {}})
        it = c["_combos"].setdefault(r["hazard"], {
            "hazard": r["hazard"], "slot": r["slot"],
            "label": r["hazard"].replace("-", " "), "orgs": []})
        it["orgs"].append({"o": r["org"], "doc": r["doc"], "stub": r["detail"] == "stub",
                           "status": r["status"]})
    markers = []
    for c in countries.values():
        items = sorted(c.pop("_combos").values(), key=lambda i: SLOTS.index(i["slot"]))
        markers.append({**c, "items": items})

    combos = {(r["iso3"], r["hazard"]) for r in rows}
    slot_counts = {s: len({(i, h) for (i, h) in combos
                           if HAZARD_SLOT.get(h, "Other / multi") == s}) for s in SLOTS}
    today = datetime.date.today().isoformat()
    n_stub = sum(1 for r in rows if r["detail"] == "stub")
    warn_html = (f'<p class="warn">⚠ {len(unmapped)} countries lack map centroids: '
                 f'{html.escape(", ".join(unmapped))} (table only)</p>' if unmapped else "")

    page = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anticipatory action frameworks — all organisations</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
 body{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1c2b33;background:#fafbfc}
 header{padding:14px 20px 6px}
 h1{font-size:19px;margin:0 0 4px} .sub{color:#5b6b73;font-size:13px;max-width:1080px}
 .warn{color:#9a6700;font-size:12px;margin:6px 20px}
 .filters{padding:8px 20px 6px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
 .filters .hint{color:#8a98a0;font-size:12px;margin-left:4px}
 .chip{display:inline-flex;align-items:center;gap:7px;border:1.5px solid transparent;
  border-radius:15px;padding:4px 13px;cursor:pointer;font-size:13px;font-weight:600;
  background:#f1f4f5;color:#3c4a52;user-select:none}
 .chip .sw{width:10px;height:10px;border-radius:50%;flex:none}
 .chip .n{font-weight:400;color:#7c8a91;font-size:12px}
 .chip.off{opacity:.42;border-color:transparent}
 .chip:not(.off){border-color:currentColor}
 #mapwrap{position:relative;width:1360px;max-width:calc(100% - 24px);margin:2px auto 0}
 #map{position:absolute;top:0;left:0;width:1360px;height:620px;transform-origin:top left;
  border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08);z-index:0;background:#fff;cursor:default}
 .leaflet-container{cursor:default!important;background:#fff}
 .labelpane{position:absolute;inset:0;pointer-events:none;z-index:620}
 .leadersvg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
 .leader{stroke:#8a99a8;stroke-width:1}
 .callout{position:absolute;display:flex;flex-direction:column;align-items:flex-start}
 .callout{align-items:center;cursor:pointer}
 .cname{font-weight:600;font-size:10px;color:#16324f;white-space:nowrap;line-height:1.1;margin-top:1px;
  text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 3px #fff,0 0 3px #fff}
 .donut{filter:drop-shadow(0 1px 1.5px rgba(20,40,50,.3));display:block}
 .infopop{position:absolute;z-index:720;max-width:320px;background:#fff;border:1px solid #d4d8de;
  border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.22);padding:10px 26px 10px 12px;
  font-size:12px;line-height:1.5;color:#222;pointer-events:auto}
 .infopop b{font-size:13px} .infopop a{color:#0f6fbe}
 .infopop .stub{color:#8a98a0;font-size:10.5px;margin-left:3px}
 .infox{position:absolute;top:3px;right:7px;border:none;background:none;font-size:17px;
  line-height:1;cursor:pointer;color:#9aa3ad}
 .infox:hover{color:#555}
 table{border-collapse:collapse;width:100%;font-size:13px}
 th,td{padding:6px 10px;border-bottom:1px solid #eef1f2;text-align:left;white-space:nowrap}
 th{position:sticky;top:0;background:#f7f9fa}
 .wrap{padding:10px 20px 30px;overflow-x:auto}
 .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:baseline}
 .stub{color:#8a98a0;font-size:11.5px} a{color:#0f6fbe;text-decoration:none}
</style></head><body>
<header>
 <h1>Anticipatory action frameworks — all organisations <span style="font-weight:400;color:#8a98a0">(beta)</span></h1>
 <div class="sub">__N__ frameworks · __NCOMBO__ country-hazard combos · __NORGS__ organisations · __NC__ countries —
 covered countries are shaded; each callout lists the hazards with anticipatory-action coverage.
 Click a hazard icon to see which organisations run frameworks for it. Generated __TODAY__ from the
 <a href="https://github.com/OCHA-DAP/ds-knowledge-base">OCHA CHD-DS knowledge base</a>
 (external inventory seeded from the <a href="https://www.anticipation-hub.org/experience/global-map">Anticipation Hub</a>;
 __NSTUB__ entries are inventory-level stubs pending enrichment).</div>
</header>
__WARN__
<div class="filters" id="filters"><span class="hint">click to toggle a hazard</span></div>
<div id="mapwrap"><div id="map"></div></div>
<div class="wrap"><table id="tbl"><thead><tr>
 <th>organisation</th><th>country</th><th>hazard (combo)</th><th>status</th><th>pre-arr. funding</th>
 <th>people</th><th>activations</th><th>doc</th><th>detail</th>
</tr></thead><tbody></tbody></table></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/polygon-clipping@0.15.7/dist/polygon-clipping.umd.js"></script>
<script>
var MARKERS=__MARKERS__, ROWS=__ROWS__, COLORS=__COLORS__, SLOTS=__SLOTS__,
    COUNTS=__COUNTS__, HAZ=__HAZ__, COVERED=__COVERED__;
var active={}; SLOTS.forEach(function(s){active[s]=true;});
var map=L.map('map',{scrollWheelZoom:false,doubleClickZoom:false,touchZoom:false,
  boxZoom:false,zoomControl:false,dragging:false,keyboard:false,attributionControl:false,
  trackResize:false,zoomSnap:0});
// fixed 1360x600 render, CSS-scaled to the container (same static-poster engine as the OCHA map)
var mapwrap=document.getElementById('mapwrap'),mapEl=document.getElementById('map');
function scaleMap(){
  var s=Math.min(1,mapwrap.clientWidth/1360);
  mapEl.style.transform=s<1?'scale('+s+')':'none';
  mapwrap.style.height=Math.round(620*s)+'px';
}
window.addEventListener('resize',scaleMap);scaleMap();
map.createPane('boundaries');map.getPane('boundaries').style.zIndex=250;
var FWBBOX={};
function fwIso(f){
  if(f.id==='-99'&&f.properties&&f.properties.name==='Somaliland')return 'SOM';
  return f.id;
}
fetch('https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json')
 .then(function(r){return r.json();})
 .then(function(geo){
  try{
    var _som=null,_sl=null;
    geo.features.forEach(function(f){
      if(f.id==='SOM')_som=f;
      else if(f.id==='-99'&&f.properties&&f.properties.name==='Somaliland')_sl=f;
    });
    if(_som&&_sl&&window.polygonClipping){
      var _u=polygonClipping.union(_som.geometry.coordinates,_sl.geometry.coordinates);
      _som.geometry={type:'MultiPolygon',coordinates:_u};
      geo.features=geo.features.filter(function(f){return f!==_sl;});
    }
  }catch(e){}
  L.geoJSON(geo,{pane:'boundaries',interactive:false,
    style:function(f){
      return COVERED[fwIso(f)]
        ?{color:'#9cc0e3',weight:0.8,fillColor:'#cfe0f2',fillOpacity:1}
        :{color:'#d3d7dc',weight:0.5,fillColor:'#ebedf0',fillOpacity:1};
    }}).addTo(map);
  geo.features.forEach(function(f){
    if(!COVERED[fwIso(f)]||!f.geometry)return;
    var polys=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
    var b={minx:1e9,miny:1e9,maxx:-1e9,maxy:-1e9};
    polys.forEach(function(poly){poly[0].forEach(function(p){
      if(p[0]<b.minx)b.minx=p[0];if(p[0]>b.maxx)b.maxx=p[0];
      if(p[1]<b.miny)b.miny=p[1];if(p[1]>b.maxy)b.maxy=p[1];
    });});
    if(b.maxx-b.minx<=170&&b.maxy-b.miny<=130){
      var _k=fwIso(f),_pb=FWBBOX[_k];
      FWBBOX[_k]=_pb?{minx:Math.min(_pb.minx,b.minx),miny:Math.min(_pb.miny,b.miny),
                      maxx:Math.max(_pb.maxx,b.maxx),maxy:Math.max(_pb.maxy,b.maxy)}:b;
    }
  });
  runLayout();
 }).catch(function(){});
// callout: a compact donut ring (one segment per ACTIVE hazard combo, count in the
// centre) with the country name beneath — ring size grows gently with combo count
function calloutHTML(m){
  var items=m.items.filter(function(it){return active[it.slot];});
  var n=items.length; if(!n) return '';
  var R=6.5+1.7*Math.sqrt(n), r=R*0.52, S=2*R+4, cx=S/2;
  var a0=-Math.PI/2, segs='';
  items.forEach(function(it){
    var a1=a0+2*Math.PI/n, large=(a1-a0)>Math.PI?1:0;
    function pt(a,rad){return (cx+rad*Math.cos(a)).toFixed(2)+','+(cx+rad*Math.sin(a)).toFixed(2);}
    segs+= n===1
      ? '<circle cx="'+cx+'" cy="'+cx+'" r="'+((R+r)/2)+'" fill="none" stroke="'+COLORS[it.slot]+'" stroke-width="'+(R-r)+'"/>'
      : '<path d="M '+pt(a0,R)+' A '+R+' '+R+' 0 '+large+' 1 '+pt(a1,R)+' L '+pt(a1,r)+' A '+r+' '+r+' 0 '+large+' 0 '+pt(a0,r)+' Z" fill="'+COLORS[it.slot]+'" stroke="#fff" stroke-width="1.3" stroke-linejoin="round"/>';
    a0=a1;});
  return '<svg class="donut" width="'+S+'" height="'+S+'" viewBox="0 0 '+S+' '+S+'">'+
    '<circle cx="'+cx+'" cy="'+cx+'" r="'+(r-0.5)+'" fill="#fff"/>'+segs+'</svg>'+
    '<span class="cname">'+m.country+'</span>';
}
var NS='http://www.w3.org/2000/svg';
var dots=L.layerGroup().addTo(map);
var lpane=L.DomUtil.create('div','labelpane',map.getContainer());
var lsvg=document.createElementNS(NS,'svg');lsvg.setAttribute('class','leadersvg');lpane.appendChild(lsvg);
var info=L.DomUtil.create('div','infopop',map.getContainer());info.style.display='none';
L.DomEvent.disableClickPropagation(info);
map.on('click',function(){info.style.display='none';});
function infoHTML(m){
  var items=m.items.filter(function(it){return active[it.slot];});
  var rows=items.map(function(it){
    var orgs=it.orgs.map(function(o){
      return '<span style="white-space:nowrap">'+
        (o.doc?'<a href="'+o.doc+'" target="_blank" rel="noopener">'+o.o+'↗</a>':o.o)+
        (o.stub?'<span class="stub">stub</span>':'')+'</span>';
    }).join(', ');
    return '<div style="margin:3px 0"><span class="dot" style="background:'+COLORS[it.slot]+'"></span>'+
      '<b style="font-size:12px">'+it.label+'</b> &mdash; '+orgs+'</div>';
  }).join('');
  return '<button class="infox" aria-label="close">&times;</button>'+
    '<b>'+m.country+'</b> &mdash; '+items.length+' hazard'+(items.length>1?'s':'')+' covered'+rows;
}
function showInfo(m,pt){
  info.innerHTML=infoHTML(m);
  info.style.display='block';
  var sz=map.getSize(),w=info.offsetWidth,h=info.offsetHeight;
  var x=pt.x+12,y=pt.y+10;
  if(x+w>sz.x-4)x=pt.x-w-12;
  if(y+h>sz.y-4)y=sz.y-h-4;
  info.style.left=Math.max(4,x)+'px';info.style.top=Math.max(4,y)+'px';
  info.querySelector('.infox').onclick=function(){info.style.display='none';};
}
var bounds=[];
var labels=MARKERS.map(function(m){
  var dot=L.circleMarker([m.lat,m.lon],{radius:3.5,color:'#fff',weight:1.5,fillColor:'#39506b',fillOpacity:1}).addTo(dots);
  var el=document.createElement('div');el.className='callout';el.innerHTML=calloutHTML(m);
  el.style.pointerEvents='auto';el.style.visibility='hidden';
  lpane.appendChild(el);
  L.DomEvent.disableClickPropagation(el);
  wireIcons(m,el);
  var ln=document.createElementNS(NS,'line');ln.setAttribute('class','leader');lsvg.appendChild(ln);
  bounds.push([m.lat,m.lon]);
  return {lat:m.lat,lon:m.lon,dir:m.dir,iso3:m.iso3,m:m,el:el,ln:ln,dot:dot,on:true};
});
function wireIcons(m,el){
  el.onclick=function(e){
    e.stopPropagation();
    var r=el.getBoundingClientRect(),mr=map.getContainer().getBoundingClientRect(),
        sc=Math.min(1,mapwrap.clientWidth/1360);
    showInfo(m,{x:(r.left-mr.left+r.width/2)/sc,y:(r.top-mr.top+r.height/2)/sc});
  };
}
map.setView([9,10],Math.log2(1360/256));   // whole world: zoom fits all 360° of longitude
var LOCKZ=map.getZoom();map.setMinZoom(LOCKZ);map.setMaxZoom(LOCKZ);
// ---- the OCHA map's force layout: eject from country boxes, separate callouts ----
var PAD=4,GAP=3;
function ownRect(Lb){
  var b=FWBBOX[Lb.iso3];if(!b)return null;
  var p1=map.latLngToContainerPoint([b.maxy,b.minx]),p2=map.latLngToContainerPoint([b.miny,b.maxx]);
  return {x1:Math.min(p1.x,p2.x),y1:Math.min(p1.y,p2.y),x2:Math.max(p1.x,p2.x),y2:Math.max(p1.y,p2.y)};
}
function actives(){return labels.filter(function(Lb){return Lb.on;});}
function clampAll(W,H){
  actives().forEach(function(Lb){
    if(Lb.cx-Lb.w/2<3)Lb.cx=3+Lb.w/2;if(Lb.cx+Lb.w/2>W-3)Lb.cx=W-3-Lb.w/2;
    if(Lb.cy-Lb.h/2<3)Lb.cy=3+Lb.h/2;if(Lb.cy+Lb.h/2>H-3)Lb.cy=H-3-Lb.h/2;
  });
}
function ejectCountries(Lb){
  // unlike the OCHA map (31 dispersed countries), 59 covered countries shade most of
  // the tropics — avoiding EVERY country box leaves no legal space, so callouts only
  // avoid their OWN country (the white text-halo keeps them readable over neighbours)
  var best=Lb.rect;
  if(!best)return false;
  var bx1=Lb.cx-Lb.w/2-GAP,by1=Lb.cy-Lb.h/2-GAP,bx2=Lb.cx+Lb.w/2+GAP,by2=Lb.cy+Lb.h/2+GAP;
  var ox=Math.min(bx2,best.x2)-Math.max(bx1,best.x1),oy=Math.min(by2,best.y2)-Math.max(by1,best.y1);
  if(ox<=0||oy<=0)return false;
  var pushL=best.x1-bx2,pushR=best.x2-bx1,pushU=best.y1-by2,pushD=best.y2-by1;
  var cands=[[Math.abs(pushL),pushL,0],[Math.abs(pushR),pushR,0],[Math.abs(pushU),0,pushU],[Math.abs(pushD),0,pushD]];
  cands.sort(function(a,b){return a[0]-b[0];});
  var dirBias=cands.filter(function(c){return (c[1]*Lb.dir[0]+c[2]*Lb.dir[1])>=0;});
  var pick=(dirBias[0]&&dirBias[0][0]<=cands[0][0]*1.6)?dirBias[0]:cands[0];
  Lb.cx+=pick[1];Lb.cy+=pick[2];
  return true;
}
function separate(iters,W,H){
  var act=actives();
  for(var s=0;s<iters;s++){
    var clean=true;
    for(var i=0;i<act.length;i++)for(var j=i+1;j<act.length;j++){
      var a=act[i],b=act[j];
      var ax=a.cx-a.w/2,ay=a.cy-a.h/2,bx=b.cx-b.w/2,by=b.cy-b.h/2;
      if(ax<bx+b.w+PAD&&ax+a.w+PAD>bx&&ay<by+b.h+PAD&&ay+a.h+PAD>by){
        clean=false;
        var ox=Math.min(ax+a.w,bx+b.w)-Math.max(ax,bx)+PAD;
        var oy=Math.min(ay+a.h,by+b.h)-Math.max(ay,by)+PAD;
        if(ox<=oy){var hx=ox/2+0.5;if(a.cx<b.cx){a.cx-=hx;b.cx+=hx;}else{a.cx+=hx;b.cx-=hx;}}
        else{var hy=oy/2+0.5;if(a.cy<b.cy){a.cy-=hy;b.cy+=hy;}else{a.cy+=hy;b.cy-=hy;}}
      }
    }
    act.forEach(function(Lb){if(ejectCountries(Lb))clean=false;});
    clampAll(W,H);
    if(clean)return true;
  }
  return false;
}
function runLayout(){
  var sz=map.getSize(),W=sz.x,H=sz.y;
  actives().forEach(function(Lb){
    var p=map.latLngToContainerPoint([Lb.lat,Lb.lon]);Lb.px=p.x;Lb.py=p.y;
    Lb.w=Lb.el.offsetWidth;Lb.h=Lb.el.offsetHeight;
    Lb.rect=ownRect(Lb);
    var dl=Math.sqrt(Lb.dir[0]*Lb.dir[0]+Lb.dir[1]*Lb.dir[1])||1,ux=Lb.dir[0]/dl,uy=Lb.dir[1]/dl;
    var r=Lb.rect,cx0=r?(r.x1+r.x2)/2:Lb.px,cy0=r?(r.y1+r.y2)/2:Lb.py;
    var hx=r?(r.x2-r.x1)/2:0,hy=r?(r.y2-r.y1)/2:0;
    var reach=Math.abs(ux)*hx+Math.abs(uy)*hy+GAP+Math.abs(ux)*Lb.w/2+Math.abs(uy)*Lb.h/2+2;
    Lb.cx=cx0+ux*reach;Lb.cy=cy0+uy*reach;
  });
  for(var step=0;step<55;step++){
    actives().forEach(function(Lb){
      Lb.cx+=(Lb.px-Lb.cx)*0.11;Lb.cy+=(Lb.py-Lb.cy)*0.11;
      ejectCountries(Lb);
    });
    separate(10,W,H);
  }
  separate(1600,W,H);
  actives().forEach(function(Lb){Lb.ll=map.containerPointToLatLng([Lb.cx,Lb.cy]);});
  render();
}
function render(){
  labels.forEach(function(Lb){
    if(!Lb.on||!Lb.ll){Lb.el.style.visibility='hidden';Lb.ln.style.display='none';return;}
    var c=map.latLngToContainerPoint(Lb.ll),p=map.latLngToContainerPoint([Lb.lat,Lb.lon]);
    Lb.cx=c.x;Lb.cy=c.y;Lb.px=p.x;Lb.py=p.y;
    Lb.el.style.visibility='visible';Lb.ln.style.display='';
    Lb.el.style.left=(Lb.cx-Lb.w/2)+'px';Lb.el.style.top=(Lb.cy-Lb.h/2)+'px';
    // leader attaches wherever the label box is closest to the country dot
    var x1=Lb.cx-Lb.w/2,y1=Lb.cy-Lb.h/2,x2=x1+Lb.w,y2=y1+Lb.h;
    var ax=Math.max(x1,Math.min(Lb.px,x2)),ay=Math.max(y1,Math.min(Lb.py,y2));
    if(ax===Lb.px&&ay===Lb.py){Lb.ln.style.display='none';}   // dot under the label: no line
    else{Lb.ln.setAttribute('x1',Lb.px);Lb.ln.setAttribute('y1',Lb.py);
         Lb.ln.setAttribute('x2',ax);Lb.ln.setAttribute('y2',ay);}
  });
}
map.on('move zoom viewreset resize',render);
setTimeout(function(){if(!labels[0]||!labels[0].ll)runLayout();},1500);
// ---- hazard chips: filter callout rows + table, then re-run the layout ----
function applyFilter(){
  info.style.display='none';
  labels.forEach(function(Lb){
    var h=calloutHTML(Lb.m);
    Lb.el.innerHTML=h;
    Lb.on=!!h;
    if(Lb.on){if(!dots.hasLayer(Lb.dot))dots.addLayer(Lb.dot);}
    else{dots.removeLayer(Lb.dot);}
  });
  renderTable();
  runLayout();
}
var fmtUsd=function(v){return v?(v>=1e6?'$'+(v/1e6).toFixed(1)+'M':'$'+Math.round(v/1e3)+'k'):'—';};
var fmtN=function(v){return v?v.toLocaleString():'—';};
function renderTable(){
  var tb=document.querySelector('#tbl tbody');tb.innerHTML='';
  ROWS.filter(function(r){return active[r.slot];})
      .sort(function(a,b){return a.country.localeCompare(b.country)||a.hazard.localeCompare(b.hazard)||a.org.localeCompare(b.org);})
      .forEach(function(r){
    tb.insertAdjacentHTML('beforeend',
     '<tr><td>'+r.org+'</td>'+
     '<td>'+r.country+'</td><td><span class="dot" style="background:'+COLORS[r.slot]+'"></span>'+r.hazard+'</td>'+
     '<td>'+r.status+'</td><td>'+fmtUsd(r.funding)+'</td>'+
     '<td>'+fmtN(r.people)+'</td><td>'+(r.n_act||'—')+'</td>'+
     '<td>'+(r.doc?'<a href="'+r.doc+'" target="_blank">doc</a>':'—')+'</td>'+
     '<td>'+(r.detail==='stub'?'<span class="stub">stub</span>':'full')+'</td></tr>');});
}
var fl=document.getElementById('filters');
SLOTS.forEach(function(s){
  var b=document.createElement('button');b.className='chip';b.style.color=COLORS[s];
  b.innerHTML='<span class="sw" style="background:'+COLORS[s]+'"></span>'+
    '<span style="color:#2b3a42">'+s+' <span class="n">('+COUNTS[s]+')</span></span>';
  b.onclick=function(){active[s]=!active[s];b.classList.toggle('off');applyFilter();};
  fl.insertBefore(b,fl.querySelector('.hint'));});
renderTable();
</script></body></html>"""
    covered = {c["iso3"]: 1 for c in markers}
    page = (page
            .replace("__MARKERS__", json.dumps(markers, ensure_ascii=False).replace("<", "\\u003c"))
            .replace("__ROWS__", json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c"))
            .replace("__COLORS__", json.dumps(SLOT_COLORS))
            .replace("__SLOTS__", json.dumps(SLOTS))
            .replace("__COUNTS__", json.dumps(slot_counts))
            .replace("__HAZ__", json.dumps(HAZARD_SVG).replace("<", "\\u003c"))
            .replace("__COVERED__", json.dumps(covered))
            .replace("__NCOMBO__", str(len(combos)))
            .replace("__N__", str(len(rows)))
            .replace("__NORGS__", str(len({r['org'] for r in rows})))
            .replace("__NC__", str(len(markers)))
            .replace("__NSTUB__", str(n_stub)).replace("__TODAY__", today)
            .replace("__WARN__", warn_html))
    OUT.write_text(page, encoding="utf-8")
    print(f"aa_global.html: {len(rows)} frameworks, {len(combos)} combos, "
          f"{len(markers)} countries, {len({r['org'] for r in rows})} orgs, {n_stub} stubs"
          + (f", {len(unmapped)} UNMAPPED" if unmapped else ""))


if __name__ == "__main__":
    main()
