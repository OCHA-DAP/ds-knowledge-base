"""Generate activations.html — a self-contained, styled trigger-statistics page that matches the
public Leaflet map's look. Three in-page tabs:
  1. Historical activations — a year × framework matrix (one row per year, one column per framework)
  2. Summary statistics     — overall RP / probability / financing per framework
  3. By framework           — a per-framework block in the gsheet "Trigger Mechanism Statistics" style

Data: the dev `aa` schema (trigger stats) + KB frontmatter (country/hazard/funding/activation flag),
reusing scripts/gen_trigger_performance.py. Output is a static file (like index.html / the map),
embedded by triggers.md and served by Pages. Run: python scripts/gen_trigger_site.py
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_trigger_performance as tp   # fetch(), kb_meta(), ISO_NAME, HAZARD_LABEL, usd, pct

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "activations.html"

HAZ_COLOR = {"drought":"#b5872a", "flood":"#1f78b4", "tropical-cyclone":"#7b52ab",
             "cholera":"#0f8a8a", "infectious-disease":"#0f8a8a"}

CSS = """
:root { --ocha:#1a6bb5; --ink:#222; --muted:#777; --line:#e3e6ea; }
* { box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:var(--ink); margin:0; background:#fafbfc; line-height:1.4; }
.disclaimer { background:#fff4d6; border-bottom:1px solid #e6cf8f; color:#6b5310;
       font-size:13px; line-height:1.4; padding:9px 18px; text-align:center; }
.disclaimer b { color:#5a4408; }
header { background:var(--ocha); color:#fff; padding:24px; }
header h1 { margin:0 0 6px; font-size:24px; }
header p { margin:0; opacity:.92; font-size:14px; max-width:1000px; }
.tabbar { background:var(--ocha); padding:0 24px; display:flex; gap:2px; }
.tabbar button { border:none; background:rgba(255,255,255,.12); color:#fff; font-size:14px;
       padding:10px 18px; cursor:pointer; border-radius:7px 7px 0 0; font-weight:600; }
.tabbar button:hover { background:rgba(255,255,255,.22); }
.tabbar button.active { background:#fafbfc; color:var(--ocha); }
main { max-width:1560px; margin:0 auto; padding:22px 24px 60px; }
.sub { color:var(--muted); font-size:13px; margin:0 0 14px; max-width:1000px; }
.tw { overflow:auto; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.06); max-height:78vh; }
a { color:var(--ocha); }
/* --- summary table (map aesthetic) --- */
table.sum { border-collapse:collapse; width:100%; background:#fff; font-size:13px; }
table.sum th, table.sum td { text-align:left; padding:7px 12px; border-bottom:1px solid var(--line); white-space:nowrap; }
table.sum th { background:#f1f4f7; font-weight:600; position:sticky; top:0; z-index:2; }
table.sum td.num { text-align:right; }
table.sum tr:hover td { background:#f6f9fc; }
.flag { color:#e3322d; }
.badge { display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }
.b-endorsed { background:#e2f3e6; color:#1e7a37; }
.b-triggered { background:#fde2e1; color:#b3261e; }
/* --- activation matrix --- */
table.mtx { border-collapse:collapse; background:#fff; font-size:11px; }
table.mtx th, table.mtx td { border:1px solid #eef1f4; padding:0; text-align:center; }
table.mtx thead th { position:sticky; top:0; z-index:3; background:#f1f4f7; height:104px; vertical-align:bottom; }
table.mtx thead th .rot { writing-mode:vertical-rl; transform:rotate(180deg); white-space:nowrap;
       font-weight:600; font-size:11px; padding:6px 0; display:inline-block; }
table.mtx td.yr, table.mtx th.yrh { position:sticky; left:0; background:#f8fafc; z-index:2;
       font-weight:600; padding:3px 8px; text-align:right; white-space:nowrap; }
table.mtx th.yrh { z-index:4; }
table.mtx td.cell { width:22px; height:20px; }
table.mtx td.cell .d { display:inline-block; width:11px; height:11px; border-radius:3px; }
table.mtx td.tot { padding:3px 7px; font-weight:600; color:var(--muted); text-align:center; }
.legend { font-size:12px; color:var(--muted); margin:0 0 10px; display:flex; gap:16px; flex-wrap:wrap; }
.legend span .d { display:inline-block; width:11px; height:11px; border-radius:3px; vertical-align:-1px; margin-right:4px; }
/* --- gsheet-style per-framework block --- */
#fwpick { font-size:14px; padding:8px 10px; border:1px solid var(--line); border-radius:6px; margin:0 0 18px; min-width:320px; }
.gcard { background:#fff; border:1px solid var(--line); border-radius:10px; padding:22px 26px; box-shadow:0 1px 3px rgba(0,0,0,.06); max-width:920px; }
.gtitle { font-style:italic; font-weight:700; font-size:15px; margin:0 0 14px; border-bottom:none; }
.gsec { display:flex; justify-content:space-between; align-items:baseline; font-weight:700; font-size:13px;
        margin:18px 0 3px; border-bottom:2px solid #111; padding-bottom:2px; }
.gsec .ana { font-style:italic; font-weight:400; color:#555; font-size:12px; }
table.g { border-collapse:collapse; font-size:13px; margin:0; border-top:1px solid #111; border-bottom:1px solid #111; }
table.g th { font-style:italic; font-weight:400; text-align:center; padding:5px 16px; border-bottom:1px solid #111; background:none; white-space:nowrap; }
table.g td { text-align:center; padding:5px 16px; border:none; white-space:nowrap; }
table.g td.lbl { font-style:italic; text-align:left; }
table.g td.yrs { text-align:left; white-space:normal; max-width:430px; color:#333; }
table.gov td { padding:4px 16px 4px 0; border:none; font-size:13px; }
table.gov td.lbl { font-style:italic; }
.fin { font-size:13px; margin:10px 0 0; color:#333; }
.note { font-size:12px; color:var(--muted); margin-top:8px; }
footer { color:var(--muted); font-size:12px; padding:26px; text-align:center; }
"""

def e_attr(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def winlabel(w):
    """Prettify raw Excel window codes (ws / wt1 / wg1) that lack a gsheet trigger name."""
    import re as _re
    if w == "ws": return "Trigger"
    m = _re.match(r'^w[tg](\d+)$', w)
    return f"Window {m.group(1)}" if m else w

def build_entries():
    wins, acts, overall = tp.fetch()
    meta = tp.kb_meta()
    groups = defaultdict(list)
    for w in wins:
        if w.kb_status == "endorsed":
            groups[(w.kb_framework, w.kb_version, w.country_iso3)].append(w)
    entries = []
    for (fw, ver, ctry), ws in groups.items():
        fm = meta.get((fw, ver), {})
        act_years = sorted({y for w in ws for y in acts.get((fw, ver, ctry, w.window_name), [])})
        fin = fm.get("prearranged") or (sum(w.allocation_usd for w in ws if w.allocation_usd) or None)
        entries.append(dict(
            fw=fw, ver=ver, ctry=ctry, name=tp.ISO_NAME.get(ctry, ctry),
            hazard=fm.get("hazard",""), haz_label=tp.HAZARD_LABEL.get(fm.get("hazard",""), (fm.get("hazard","") or "").title()),
            windows=ws, acts=acts, overall=overall.get((fw, ver, ctry), {}),
            activated=bool(fm.get("n_activations", 0)), fin=fin, fund=fm.get("funding") or {},
            doc=fm.get("doc"), act_years=act_years,
            a0=ws[0].analysis_start, a1=ws[0].analysis_end, all_in=ws[0].all_in))
    entries.sort(key=lambda e: (e["hazard"], e["name"]))
    return entries

# ---------------- tab 1: activation matrix ----------------
def matrix_html(entries):
    yrs = sorted({y for e in entries for y in e["act_years"]}, reverse=True)
    if not yrs: return "<p>No activation data.</p>"
    cols = "".join(
        f'<th title="{e_attr(e["name"]+" — "+e["haz_label"])}"><span class="rot" '
        f'style="color:{HAZ_COLOR.get(e["hazard"],"#444")}">{e_attr(e["ctry"])} · {e_attr(e["haz_label"])}</span></th>'
        for e in entries)
    rows = []
    for y in yrs:
        cells = []
        n = 0
        for e in entries:
            if y in e["act_years"]:
                n += 1
                cells.append(f'<td class="cell" title="{e_attr(e["name"])} {y}">'
                             f'<span class="d" style="background:{HAZ_COLOR.get(e["hazard"],"#444")}"></span></td>')
            else:
                cells.append('<td class="cell"></td>')
        rows.append(f'<tr><td class="yr">{y}</td>{"".join(cells)}<td class="tot">{n}</td></tr>')
    legend = " ".join(f'<span><span class="d" style="background:{c}"></span>{h.replace("tropical-cyclone","cyclone").replace("infectious-disease","cholera").title()}</span>'
                      for h,c in HAZ_COLOR.items() if h != "infectious-disease")
    return (f'<p class="sub">Each filled cell marks a year the framework\'s trigger would have fired '
            f'in the historical (backtested) record. One row per year, one column per framework.</p>'
            f'<div class="legend">{legend}</div>'
            f'<div class="tw"><table class="mtx"><thead><tr><th class="yrh">Year</th>{cols}'
            f'<th class="yrh" style="left:auto">#</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

# ---------------- tab 2: summary ----------------
def summary_html(entries):
    rows = []
    for e in entries:
        ov = e["overall"]
        rp = f'{float(ov["rp"]):.1f} yr' if ov.get("rp") else "—"
        pr = tp.pct(ov.get("prob"))
        flag = '<span class="flag">● activated</span>' if e["activated"] else ""
        rows.append(
            f'<tr><td>{e_attr(e["name"])}</td><td>{e_attr(e["haz_label"])}</td>'
            f'<td class="num">{len(e["windows"])}</td><td class="num">{rp}</td>'
            f'<td class="num">{pr}</td><td class="num">{tp.usd(e["fin"])}</td>'
            f'<td>{"all-in" if e["all_in"] else "split"}</td><td>{flag}</td></tr>')
    return (f'<p class="sub">Overall return period = the chance <b>any</b> trigger in the framework fires. '
            f'Pre-arranged = committed financing released on activation.</p>'
            f'<div class="tw"><table class="sum"><thead><tr><th>Framework</th><th>Hazard</th>'
            f'<th class="num">Windows</th><th class="num">Overall RP</th><th class="num">Annual prob.</th>'
            f'<th class="num">Pre-arranged</th><th>Funding</th><th></th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')

# ---------------- tab 3: per-framework gsheet block ----------------
def gcard_html(e):
    ws = e["windows"]
    analysis = f"Analysis years: {e['a0']}–{e['a1']}" if e["a0"] and e["a1"] else ""
    trows = []
    for w in ws:
        yrs = ", ".join(str(y) for y in e["acts"].get((e["fw"], e["ver"], e["ctry"], w.window_name), [])) or "—"
        rp = f'{float(w.rp):.1f} years' if w.rp is not None else "—"
        trows.append(f'<tr><td class="lbl">{e_attr(winlabel(w.window_name))}</td><td>{rp}</td>'
                     f'<td>{tp.pct(w.prob)}</td><td class="yrs">{yrs}</td></tr>')
    ov = e["overall"]
    orp = f'{float(ov["rp"]):.1f} years' if ov.get("rp") else "—"
    oprob = tp.pct(ov.get("prob"))
    # estimated average annual spend = pre-arranged envelope × overall annual probability
    spend = "—"
    if e["fin"] and ov.get("prob"):
        spend = tp.usd(round(e["fin"] * float(ov["prob"])))
    fund = " (" + ", ".join(f"{k} {tp.usd(v)}" for k,v in e["fund"].items()) + ")" if e["fund"] else ""
    allin = " · all-in (whole envelope on any trigger)" if e["all_in"] else ""
    doc = f'<div class="note">Source: <a href="{e_attr(e["doc"])}" target="_blank" rel="noopener">framework document</a>.</div>' if e["doc"] else ""
    return (
        f'<div class="gcard" data-fw="{e_attr(e["fw"]+"|"+e["ctry"])}"'
        f'{"" if e["__first"] else " hidden"}>'
        f'<div class="gtitle">{e_attr(e["name"])} — {e_attr(e["haz_label"])} · Trigger Mechanism Statistics</div>'
        f'<div class="gsec"><span>Stats by trigger</span><span class="ana">{analysis}</span></div>'
        f'<table class="g"><thead><tr><th>Trigger</th><th>Return period</th>'
        f'<th>Activation probability</th><th>Years activated</th></tr></thead>'
        f'<tbody>{"".join(trows)}</tbody></table>'
        f'<div class="gsec"><span>Overall stats</span><span class="ana"></span></div>'
        f'<table class="gov"><tbody>'
        f'<tr><td class="lbl">Overall return period</td><td>{orp}</td></tr>'
        f'<tr><td class="lbl">Overall probability of activation</td><td>{oprob}</td></tr>'
        f'<tr><td class="lbl">Average total spending per year (est.)</td><td>{spend}</td></tr>'
        f'</tbody></table>'
        f'<div class="fin"><b>Pre-arranged financing:</b> {tp.usd(e["fin"])}{fund}{allin}</div>'
        f'{doc}</div>')

def byframework_html(entries):
    for i, e in enumerate(entries): e["__first"] = (i == 0)
    opts = "".join(f'<option value="{e_attr(e["fw"]+"|"+e["ctry"])}">{e_attr(e["name"])} — {e_attr(e["haz_label"])}</option>'
                   for e in entries)
    cards = "".join(gcard_html(e) for e in entries)
    return (f'<p class="sub">Per-framework trigger statistics in the format used in the framework documents.</p>'
            f'<select id="fwpick">{opts}</select><div id="fwdetail">{cards}</div>')

def main():
    entries = build_entries()
    html = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AA Trigger Statistics</title><style>{CSS}</style></head><body>
<div class="disclaimer" role="note">⚠️ <b>Work in progress.</b> Auto-generated from an internal knowledge base; figures are indicative, not authoritative.</div>
<header><h1>AA Trigger Statistics</h1>
<p>Published triggers, windows, return periods, and historical activations across the Centre for Humanitarian Data's Anticipatory Action portfolio. Activations are the historical (backtested) years each trigger would have fired.</p></header>
<div class="tabbar">
  <button data-tab="activations" class="active">Historical activations</button>
  <button data-tab="summary">Summary statistics</button>
  <button data-tab="byframework">By framework</button>
</div>
<main>
  <section id="tab-activations">{matrix_html(entries)}</section>
  <section id="tab-summary" hidden>{summary_html(entries)}</section>
  <section id="tab-byframework" hidden>{byframework_html(entries)}</section>
</main>
<footer>Generated from the <code>aa</code> trigger-performance schema · {len(entries)} endorsed framework-versions.</footer>
<script>
document.querySelectorAll('.tabbar button').forEach(function(b){{
  b.onclick=function(){{
    document.querySelectorAll('.tabbar button').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    ['activations','summary','byframework'].forEach(function(t){{
      document.getElementById('tab-'+t).hidden = (t !== b.dataset.tab);
    }});
  }};
}});
var pick=document.getElementById('fwpick');
if(pick){{ pick.onchange=function(){{
  document.querySelectorAll('#fwdetail .gcard').forEach(function(c){{
    c.hidden = (c.dataset.fw !== pick.value);
  }});
}}; }}
</script></body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(entries)} frameworks.")

if __name__ == "__main__":
    main()
